from __future__ import annotations

import os
import re
import time
from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any, Callable, Mapping

from llm_json import LlmJsonError, parse_or_repair_json_object, strict_json_text
from llm_readme_patch import install_llm_readme_patch
from llm_transcripts import (
    begin_transcript,
    record_initial_response,
    record_repair_response,
    save_transcript,
)
from unsloth_studio import StudioAwareLlmProviderRouter

_REQUIRED_KEYS_RE = re.compile(
    r"RETURN ONLY THESE ARTIFACT KEYS:\s*(.+?)\.\s*Omit unrequested",
    flags=re.I | re.S,
)
_INSTALLED = False


def _env_bool(name: str, default: bool) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on", "y"}:
        return True
    if normalized in {"0", "false", "no", "off", "n"}:
        return False
    raise RuntimeError(f"{name} must be a boolean value, not {value!r}")


def _required_keys(request_input: Any) -> tuple[str, ...]:
    texts: list[str] = []
    for message in request_input or []:
        if not isinstance(message, Mapping):
            continue
        content = message.get("content")
        if isinstance(content, str):
            texts.append(content)
            continue
        for block in content or []:
            if not isinstance(block, Mapping):
                continue
            if block.get("type") in {"input_text", "text"}:
                texts.append(str(block.get("text") or ""))
    match = _REQUIRED_KEYS_RE.search("\n".join(texts))
    if not match:
        return ()
    return tuple(
        key.strip()
        for key in match.group(1).split(",")
        if key.strip()
    )


def _repair_prompt(raw: str, required_keys: tuple[str, ...]) -> str:
    return (
        "Repair the malformed JSON below. Return exactly one strict JSON object "
        "and nothing else. Preserve every semantic fact and preserve each Prolog "
        "string exactly except for JSON escaping needed to make it valid. Do not "
        "summarize, omit, rename, or invent facts. Required top-level keys: "
        + ", ".join(required_keys)
        + ".\n\nMALFORMED JSON:\n"
        + raw
    )


def _save_failed_transcript(run: Any, error: BaseException) -> None:
    if run is None:
        return
    run.error = str(error)
    run.status = "failed"
    run.repair_method = "failed"
    run.metadata["completed_at"] = datetime.now(timezone.utc).isoformat()
    save_transcript(run)


def _resilient_create_response(
    original_create_response: Callable[..., Any],
    router: StudioAwareLlmProviderRouter,
    **kwargs: Any,
) -> Any:
    run = begin_transcript(router, kwargs)
    started = time.perf_counter()
    try:
        response = original_create_response(router, **kwargs)
    except Exception as error:
        if run is not None:
            run.elapsed_seconds = time.perf_counter() - started
        _save_failed_transcript(run, error)
        raise

    elapsed = time.perf_counter() - started
    record_initial_response(run, response, elapsed_seconds=elapsed)
    raw = getattr(response, "output_text", None)
    if not raw:
        error = RuntimeError("LLM response contained no output_text")
        _save_failed_transcript(run, error)
        raise error

    required_keys = _required_keys(kwargs.get("input"))
    if run is not None:
        run.required_keys = required_keys
    used_provider_retry = False

    try:
        bundle, repaired = parse_or_repair_json_object(
            str(raw),
            required_keys=required_keys,
        )
    except LlmJsonError as first_error:
        if not _env_bool("ARC3_LLM_JSON_RETRY", True):
            _save_failed_transcript(run, first_error)
            location = f" Transcript: {run.path}" if run is not None else ""
            raise RuntimeError(f"{first_error}.{location}") from first_error

        print(
            "LLM response was not recoverable locally; requesting one "
            "text-only JSON repair pass..."
        )
        used_provider_retry = True
        repair_prompt = _repair_prompt(str(raw), required_keys)
        repair_started = time.perf_counter()
        try:
            repair_response = original_create_response(
                router,
                model=kwargs.get("model"),
                input=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_text",
                                "text": repair_prompt,
                            }
                        ],
                    }
                ],
                reasoning={"effort": "low"},
                max_output_tokens=kwargs.get("max_output_tokens"),
            )
        except Exception as error:
            if run is not None:
                run.repair_prompt = repair_prompt
                run.repair_elapsed_seconds = time.perf_counter() - repair_started
            _save_failed_transcript(run, error)
            raise
        repair_elapsed = time.perf_counter() - repair_started
        record_repair_response(
            run,
            prompt=repair_prompt,
            response=repair_response,
            elapsed_seconds=repair_elapsed,
        )
        retry_raw = getattr(repair_response, "output_text", None)
        if not retry_raw:
            error = RuntimeError(
                f"LLM JSON repair pass returned no output. Original error: {first_error}"
            )
            _save_failed_transcript(run, error)
            raise error from first_error
        try:
            bundle, repaired = parse_or_repair_json_object(
                str(retry_raw),
                required_keys=required_keys,
            )
        except LlmJsonError as retry_error:
            _save_failed_transcript(run, retry_error)
            suffix = f" Transcript: {run.path}" if run is not None else ""
            raise RuntimeError(
                f"LLM JSON remained invalid after repair pass: {retry_error}.{suffix}"
            ) from retry_error
        repaired = True

    strict = strict_json_text(bundle)
    if run is not None:
        run.normalized_response = strict
        run.repair_method = (
            "provider_text_retry"
            if used_provider_retry
            else ("local_json_repair" if repaired else "strict_json")
        )
        run.status = "normalized"
        run.metadata["completed_at"] = datetime.now(timezone.utc).isoformat()
        transcript_path = save_transcript(run)
    else:
        transcript_path = None

    if repaired:
        method = (
            "with a text-only provider repair pass"
            if used_provider_retry
            else "locally"
        )
        location = f" Transcript: {transcript_path}" if transcript_path else ""
        print(f"Recovered malformed LLM JSON {method}.{location}")
    elif transcript_path is not None:
        print(f"LLM transcript: {transcript_path}")

    return SimpleNamespace(
        output_text=strict,
        provider_metadata=getattr(response, "provider_metadata", {}),
    )


def install_llm_json_resilience() -> None:
    """Wrap provider responses with transcripts, local repair, and one retry."""
    global _INSTALLED
    if _INSTALLED:
        return
    _INSTALLED = True
    install_llm_readme_patch()

    original_create_response = StudioAwareLlmProviderRouter.create_response

    def resilient_create_response(
        self: StudioAwareLlmProviderRouter,
        **kwargs: Any,
    ) -> Any:
        return _resilient_create_response(original_create_response, self, **kwargs)

    StudioAwareLlmProviderRouter.create_response = resilient_create_response
