from __future__ import annotations

import json
import os
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Iterator, Mapping

from llm_providers import (
    LlmConfigurationError,
    LlmProviderRouter,
    LlmRequestError,
    ProviderSpec,
    _ResponsesFacade,
    _extract_openai_output_text,
    _metadata_value,
)
from llm_readme_patch import transcript_is_restorable
from llm_transcripts import list_transcripts, restore_transcript, transcript_metadata

DEFAULT_BATCH_CONFIG = Path(__file__).resolve().parents[1] / "config" / "llm_batch_profiles.json"


@dataclass
class BatchProfile:
    profile_id: str
    label: str
    provider_id: str
    model: str
    enabled: bool
    analysis_level: int
    max_output_tokens: int
    temperature: float | None
    top_p: float | None
    reasoning_effort: str
    current_image_detail: str
    parent_image_detail: str
    timeout_seconds: float
    seed: int | None = None

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "BatchProfile":
        level = int(raw.get("analysis_level", 2))
        if level not in {2, 3, 4}:
            raise ValueError("analysis_level must be 2, 3, or 4")
        return cls(
            profile_id=str(raw.get("id") or "").strip(),
            label=str(raw.get("label") or raw.get("id") or "Unnamed profile"),
            provider_id=str(raw.get("provider_id") or "").strip(),
            model=str(raw.get("model") or "").strip(),
            enabled=bool(raw.get("enabled", False)),
            analysis_level=level,
            max_output_tokens=int(raw.get("max_output_tokens", 12000)),
            temperature=(
                None if raw.get("temperature") is None else float(raw["temperature"])
            ),
            top_p=None if raw.get("top_p") is None else float(raw["top_p"]),
            reasoning_effort=str(raw.get("reasoning_effort") or "low"),
            current_image_detail=str(raw.get("current_image_detail") or "low"),
            parent_image_detail=str(raw.get("parent_image_detail") or "low"),
            timeout_seconds=float(raw.get("timeout_seconds", 600)),
            seed=None if raw.get("seed") is None else int(raw["seed"]),
        )

    def to_mapping(self) -> dict[str, Any]:
        return {
            "id": self.profile_id,
            "label": self.label,
            "provider_id": self.provider_id,
            "model": self.model,
            "enabled": self.enabled,
            "analysis_level": self.analysis_level,
            "max_output_tokens": self.max_output_tokens,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "reasoning_effort": self.reasoning_effort,
            "current_image_detail": self.current_image_detail,
            "parent_image_detail": self.parent_image_detail,
            "timeout_seconds": self.timeout_seconds,
            "seed": self.seed,
        }


def load_profiles(path: str | Path | None = None) -> list[BatchProfile]:
    selected = Path(
        path or os.environ.get("ARC3_LLM_BATCH_CONFIG") or DEFAULT_BATCH_CONFIG
    ).expanduser().resolve()
    raw = json.loads(selected.read_text(encoding="utf-8"))
    items = raw.get("profiles") if isinstance(raw, dict) else None
    if not isinstance(items, list):
        raise ValueError(f"Batch profile config must contain a profiles list: {selected}")
    profiles = [BatchProfile.from_mapping(item) for item in items]
    if any(not profile.profile_id for profile in profiles):
        raise ValueError("Every batch profile requires a nonempty id")
    ids = [profile.profile_id for profile in profiles]
    if len(ids) != len(set(ids)):
        raise ValueError("Batch profile ids must be unique")
    return profiles


def save_profiles(profiles: list[BatchProfile], path: str | Path | None = None) -> Path:
    selected = Path(
        path or os.environ.get("ARC3_LLM_BATCH_CONFIG") or DEFAULT_BATCH_CONFIG
    ).expanduser().resolve()
    selected.write_text(
        json.dumps(
            {"profiles": [profile.to_mapping() for profile in profiles]},
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    return selected


@contextmanager
def _temporary_environment(values: Mapping[str, Any]) -> Iterator[None]:
    previous: dict[str, str | None] = {}
    try:
        for name, value in values.items():
            previous[name] = os.environ.get(name)
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = str(value)
        yield
    finally:
        for name, value in previous.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value


def _profile_environment(profile: BatchProfile, spec: ProviderSpec) -> dict[str, Any]:
    prefix = f"ARC3_GPT_{profile.analysis_level}_"
    values: dict[str, Any] = {
        prefix + "MAX_OUTPUT_TOKENS": profile.max_output_tokens,
        prefix + "REASONING_EFFORT": profile.reasoning_effort,
        prefix + "IMAGE_DETAIL": profile.current_image_detail,
        prefix + "PARENT_IMAGE_DETAIL": profile.parent_image_detail,
        "ARC3_LLM_TEMPERATURE": profile.temperature,
        "ARC3_LLM_TOP_P": profile.top_p,
        "ARC3_LLM_SEED": profile.seed,
        "ARC3_LLM_TIMEOUT_SECONDS": profile.timeout_seconds,
    }
    if spec.model_env:
        values[spec.model_env] = profile.model
    return values


def _number(prompt: str, current: Any, cast: Any, *, allow_blank: bool = True) -> Any:
    value = input(f"{prompt} [{current}]: ").strip()
    if not value and allow_blank:
        return current
    return cast(value)


def _edit_profile(profile: BatchProfile) -> None:
    print(f"\nEditing {profile.profile_id}. Blank keeps the current value.")
    profile.label = input(f"Label [{profile.label}]: ").strip() or profile.label
    profile.model = input(f"Model [{profile.model}]: ").strip() or profile.model
    profile.analysis_level = _number("Analysis level 2/3/4", profile.analysis_level, int)
    if profile.analysis_level not in {2, 3, 4}:
        raise ValueError("Analysis level must be 2, 3, or 4")
    profile.max_output_tokens = _number(
        "Maximum output tokens", profile.max_output_tokens, int
    )
    profile.temperature = _number("Temperature", profile.temperature, float)
    profile.top_p = _number("Top-p", profile.top_p, float)
    profile.reasoning_effort = (
        input(f"Reasoning effort [{profile.reasoning_effort}]: ").strip()
        or profile.reasoning_effort
    )
    profile.current_image_detail = (
        input(f"Current image detail [{profile.current_image_detail}]: ").strip()
        or profile.current_image_detail
    )
    profile.parent_image_detail = (
        input(f"Parent image detail [{profile.parent_image_detail}]: ").strip()
        or profile.parent_image_detail
    )
    profile.timeout_seconds = _number(
        "Request timeout seconds", profile.timeout_seconds, float
    )
    seed = input(f"Seed [{profile.seed if profile.seed is not None else 'none'}]: ").strip()
    if seed:
        profile.seed = None if seed.lower() in {"none", "off", "null"} else int(seed)


def _profile_state(profile: BatchProfile, router: LlmProviderRouter) -> tuple[bool, str]:
    spec = next(
        (candidate for candidate in router.specs if candidate.provider_id == profile.provider_id),
        None,
    )
    if spec is None:
        return False, "unknown provider"
    configured, detail = spec.configuration_state()
    return configured, detail


def _print_profiles(profiles: list[BatchProfile], router: LlmProviderRouter) -> None:
    print("\nMULTI-LLM BATCH PROFILES")
    print("Toggle a row by number. Each row has its own model and parameters.")
    for index, profile in enumerate(profiles, start=1):
        configured, state = _profile_state(profile, router)
        check = "x" if profile.enabled else " "
        usable = "ready" if configured else state
        print(
            f" {index:>2}. [{check}] {profile.label}\n"
            f"      provider={profile.provider_id}  model={profile.model}\n"
            f"      L{profile.analysis_level} tokens={profile.max_output_tokens} "
            f"temp={profile.temperature} top_p={profile.top_p} "
            f"reasoning={profile.reasoning_effort} "
            f"images={profile.current_image_detail}/{profile.parent_image_detail} "
            f"timeout={profile.timeout_seconds:g}s  {usable}"
        )
    print("Commands: number=toggle  e NUMBER=edit  a=all ready  n=none")
    print("          s=save choices/edits  r=run checked  Enter=cancel")


def _new_transcripts(node: Any, before: set[str]) -> list[Path]:
    return [path for path in list_transcripts(node) if path.name not in before]


def _restore_selected_provider(
    runner: Any,
    selected_provider_id: str,
    before_active: Path | None,
    fresh: list[Path],
) -> Path | None:
    store, node = runner._require_node()
    candidates = [
        path
        for path in fresh
        if transcript_is_restorable(path)
        and transcript_metadata(path).get("provider_id") == selected_provider_id
    ]
    target = candidates[0] if candidates else before_active
    if target is None or not target.exists() or not transcript_is_restorable(target):
        return None
    restore_transcript(store, node, target)
    return target


def run_batch_menu(runner: Any) -> None:
    router = runner.llm_router()
    profiles = load_profiles()
    while True:
        _print_profiles(profiles, router)
        command = input("Batch selection: ").strip()
        if not command:
            print("Batch cancelled.")
            return
        lower = command.lower()
        if lower == "a":
            for profile in profiles:
                profile.enabled = _profile_state(profile, router)[0]
            continue
        if lower == "n":
            for profile in profiles:
                profile.enabled = False
            continue
        if lower == "s":
            print(f"Saved batch profiles: {save_profiles(profiles)}")
            continue
        if lower.startswith("e "):
            index = int(lower.split(None, 1)[1]) - 1
            if not 0 <= index < len(profiles):
                raise ValueError("Profile number is out of range")
            _edit_profile(profiles[index])
            continue
        if lower == "r":
            break
        index = int(command) - 1
        if not 0 <= index < len(profiles):
            raise ValueError("Profile number is out of range")
        profiles[index].enabled = not profiles[index].enabled

    selected_provider = router.current_spec().provider_id
    store, node = runner._require_node()
    before = {path.name for path in list_transcripts(node)}
    before_active = next(
        (path for path in list_transcripts(node) if transcript_is_restorable(path)),
        None,
    )
    successes: list[str] = []
    failures: list[str] = []

    for profile in profiles:
        if not profile.enabled:
            continue
        configured, state = _profile_state(profile, router)
        if not configured:
            print(f"Skipping {profile.label}: {state}")
            failures.append(f"{profile.label}: {state}")
            continue
        spec = router.select(profile.provider_id)
        print(
            f"\nRunning {profile.label}\n"
            f"  model={profile.model} level={profile.analysis_level} "
            f"tokens={profile.max_output_tokens} timeout={profile.timeout_seconds:g}s"
        )
        try:
            with _temporary_environment(_profile_environment(profile, spec)):
                runner._run_gpt_analysis_level(profile.analysis_level)
            successes.append(profile.label)
        except Exception as exc:
            print(f"Batch profile failed and will be skipped: {exc}")
            failures.append(f"{profile.label}: {exc}")

    fresh = _new_transcripts(node, before)
    restored = _restore_selected_provider(
        runner, selected_provider, before_active, fresh
    )
    try:
        router.select(selected_provider)
    except Exception:
        pass

    print("\nLLM batch complete.")
    print(f"  successful profiles: {len(successes)}")
    print(f"  failed/skipped profiles: {len(failures)}")
    print(f"  new comparison transcripts: {len(fresh)}")
    if restored is not None:
        print(
            "  active README/artifacts restored to the lowercase-g selected "
            f"provider via: {restored.name}"
        )
    elif fresh:
        print("  no completed transcript for the selected provider was available to restore")


def _install_sampling_parameters() -> None:
    if getattr(_ResponsesFacade.create, "_arc3_batch_sampling", False):
        return

    original_facade_create = _ResponsesFacade.create

    def facade_create(self: _ResponsesFacade, **kwargs: Any) -> Any:
        for env_name, request_name, cast in (
            ("ARC3_LLM_TEMPERATURE", "temperature", float),
            ("ARC3_LLM_TOP_P", "top_p", float),
            ("ARC3_LLM_SEED", "seed", int),
        ):
            value = os.environ.get(env_name, "").strip()
            if value and request_name not in kwargs:
                kwargs[request_name] = cast(value)
        return original_facade_create(self, **kwargs)

    setattr(facade_create, "_arc3_batch_sampling", True)
    _ResponsesFacade.create = facade_create

    original_openai_response = LlmProviderRouter._openai_response

    def openai_response(
        self: LlmProviderRouter,
        spec: ProviderSpec,
        *,
        model: str,
        request: Mapping[str, Any],
    ) -> tuple[str, dict[str, Any]]:
        api_key = spec.resolved_api_key()
        if not api_key and not spec.api_key_optional:
            raise LlmConfigurationError(
                f"Provider {spec.provider_id} requires {spec.api_key_env or 'an API key'}"
            )
        base_url = spec.resolved_base_url()
        timeout = float(
            os.environ.get("ARC3_LLM_TIMEOUT_SECONDS", "").strip()
            or spec.timeout_seconds
        )
        cache_key = (
            spec.provider_id,
            base_url,
            (api_key or "local-no-key") + f"|timeout={timeout:g}",
        )
        client = self._openai_clients.get(cache_key)
        if client is None:
            factory = self._openai_client_factory
            if factory is None:
                from openai import OpenAI

                factory = OpenAI
            try:
                client = factory(
                    api_key=api_key or "local-no-key",
                    base_url=base_url,
                    timeout=timeout,
                )
            except TypeError:
                client = factory(api_key=api_key or "local-no-key", base_url=base_url)
            self._openai_clients[cache_key] = client

        payload: dict[str, Any] = {
            "model": model,
            "input": request.get("input"),
            "max_output_tokens": request.get("max_output_tokens"),
            "temperature": request.get("temperature"),
            "top_p": request.get("top_p"),
            "seed": request.get("seed"),
        }
        if request.get("reasoning") and (
            spec.supports_reasoning or "openrouter.ai" in (base_url or "")
        ):
            payload["reasoning"] = request["reasoning"]
        payload = {key: value for key, value in payload.items() if value is not None}
        try:
            response = client.responses.create(**payload)
        except Exception as exc:
            endpoint = f" at {base_url}" if base_url else ""
            raise LlmRequestError(
                f"{spec.label} request failed{endpoint}: {exc}"
            ) from exc
        output = getattr(response, "output_text", None)
        if not output:
            output = _extract_openai_output_text(response)
        metadata = {
            "response_id": getattr(response, "id", None),
            "response_model": getattr(response, "model", None),
            "status": getattr(response, "status", None),
            "usage": _metadata_value(getattr(response, "usage", None)),
            "base_url": base_url,
            "timeout_seconds": timeout,
            "temperature": payload.get("temperature"),
            "top_p": payload.get("top_p"),
            "seed": payload.get("seed"),
        }
        return str(output or ""), metadata

    openai_response._arc3_original = original_openai_response  # type: ignore[attr-defined]
    LlmProviderRouter._openai_response = openai_response


def install_batch_ui(ui_module: Any) -> None:
    _install_sampling_parameters()
    if getattr(ui_module.read_key, "_arc3_batch_ui", False):
        return
    original_read_key = ui_module.read_key
    original_print_controls = ui_module.print_controls

    def read_key() -> str:
        key = original_read_key()
        if key != "G":
            return key
        from multillm_runner import last_runner

        runner = last_runner()
        if runner is None:
            print("No active ARC3 runner is available for LLM batch mode.")
        else:
            try:
                run_batch_menu(runner)
            except Exception as exc:
                print(f"LLM batch menu error: {exc}")
        return "\r"

    def print_controls(runner: Any, rows: list[dict[str, Any]]) -> None:
        original_print_controls(runner, rows)
        print("LLM batch: (G) choose provider-specific model/parameter profiles")

    setattr(read_key, "_arc3_batch_ui", True)
    ui_module.read_key = read_key
    ui_module.print_controls = print_controls
