from __future__ import annotations

import os
import re
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Callable, Mapping

from llm_json import LlmJsonError, parse_or_repair_json_object, strict_json_text
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


def _response_directory() -> Path:
    try:
        from multillm_runner import last_runner

        runner = last_runner()
        node = getattr(runner, "current_node", None) if runner is not None else None
        path = getattr(node, "path", None)
        if path is not None:
            return Path(path)
    except Exception:
        pass

    configured = os.environ.get("ARC3_LLM_RESPONSE_DIR", "").strip()
    root = Path(configured or ".llm_responses").expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    return root


def _write_response(name: str, text: str) -> Path | None:
    if not _env_bool("ARC3_LLM_SAVE_RAW_RESPONSE", True):
        return None
    directory = _response_directory()
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / name
    path.write_text(text + ("" if text.endswith("\n") else "\n"), encoding="utf-8")
    return path


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


def _resilient_create_response(
    original_create_response: Callable[..., Any],
    router: StudioAwareLlmProviderRouter,
    **kwargs: Any,
) -> Any:
    response = original_create_response(router, **kwargs)
    raw = getattr(response, "output_text", None)
    if not raw:
        return response

    required_keys = _required_keys(kwargs.get("input"))
    raw_path = _write_response("llm_response.raw.txt", str(raw))
    used_provider_retry = False

    try:
        bundle, repaired = parse_or_repair_json_object(
            str(raw),
            required_keys=required_keys,
        )
    except LlmJsonError as first_error:
        if not _env_bool("ARC3_LLM_JSON_RETRY", True):
            location = f" Raw response: {raw_path}" if raw_path else ""
            raise RuntimeError(f"{first_error}.{location}") from first_error

        print(
            "LLM response was not recoverable locally; requesting one "
            "text-only JSON repair pass..."
        )
        used_provider_retry = True
        repair_response = original_create_response(
            router,
            model=kwargs.get("model"),
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": _repair_prompt(str(raw), required_keys),
                        }
                    ],
                }
            ],
            reasoning={"effort": "low"},
            max_output_tokens=kwargs.get("max_output_tokens"),
        )
        retry_raw = getattr(repair_response, "output_text", None)
        if not retry_raw:
            raise RuntimeError(
                f"LLM JSON repair pass returned no output. Original error: {first_error}"
            ) from first_error
        retry_path = _write_response("llm_response.retry.raw.txt", str(retry_raw))
        try:
            bundle, repaired = parse_or_repair_json_object(
                str(retry_raw),
                required_keys=required_keys,
            )
        except LlmJsonError as retry_error:
            locations = [path for path in (raw_path, retry_path) if path is not None]
            suffix = (
                " Saved responses: " + ", ".join(str(path) for path in locations)
                if locations
                else ""
            )
            raise RuntimeError(
                f"LLM JSON remained invalid after repair pass: {retry_error}.{suffix}"
            ) from retry_error
        repaired = True

    strict = strict_json_text(bundle)
    if repaired:
        repaired_path = _write_response("llm_response.repaired.json", strict)
        location = f" Saved: {repaired_path}" if repaired_path else ""
        method = (
            "with a text-only provider repair pass"
            if used_provider_retry
            else "locally"
        )
        print(f"Recovered malformed LLM JSON {method}.{location}")

    return SimpleNamespace(output_text=strict)


def install_llm_json_resilience() -> None:
    """Wrap provider responses with strict parse, local repair, and one retry."""
    global _INSTALLED
    if _INSTALLED:
        return
    _INSTALLED = True

    original_create_response = StudioAwareLlmProviderRouter.create_response

    def resilient_create_response(
        self: StudioAwareLlmProviderRouter,
        **kwargs: Any,
    ) -> Any:
        return _resilient_create_response(original_create_response, self, **kwargs)

    StudioAwareLlmProviderRouter.create_response = resilient_create_response
