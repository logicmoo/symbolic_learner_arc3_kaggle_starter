from __future__ import annotations

import json
import os
import tempfile
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator, Mapping

from llm_providers import LlmConfigurationError, ProviderSpec
from unsloth_studio import StudioAwareLlmProviderRouter


def _text(value: Any) -> str:
    return str(value or "").strip()


def _optional_text(value: Any) -> str | None:
    text = _text(value)
    return text or None


@dataclass(frozen=True)
class ProviderBackend:
    backend_id: str
    label: str
    adapter: str
    enabled: bool | str
    api_key_env: str | None
    api_key_optional: bool
    base_url: str | None
    base_url_env: str | None
    health_url: str | None
    health_url_env: str | None
    supports_reasoning: bool
    timeout_seconds: float
    anthropic_version: str
    default_model: str | None

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "ProviderBackend":
        backend_id = _text(raw.get("id"))
        if not backend_id:
            raise LlmConfigurationError("Every LLM provider backend requires an id")
        adapter = _text(raw.get("adapter"))
        if adapter not in {"openai_responses", "anthropic_messages"}:
            raise LlmConfigurationError(
                f"Provider backend {backend_id!r} has unsupported adapter {adapter!r}"
            )
        enabled = raw.get("enabled", "auto")
        if enabled not in {True, False, "auto"}:
            raise LlmConfigurationError(
                f"Provider backend {backend_id!r} enabled must be true, false, or 'auto'"
            )
        return cls(
            backend_id=backend_id,
            label=_text(raw.get("label")) or backend_id,
            adapter=adapter,
            enabled=enabled,
            api_key_env=_optional_text(raw.get("api_key_env")),
            api_key_optional=bool(raw.get("api_key_optional", False)),
            base_url=_optional_text(raw.get("base_url")),
            base_url_env=_optional_text(raw.get("base_url_env")),
            health_url=_optional_text(raw.get("health_url")),
            health_url_env=_optional_text(raw.get("health_url_env")),
            supports_reasoning=bool(raw.get("supports_reasoning", False)),
            timeout_seconds=float(raw.get("timeout_seconds", 600.0)),
            anthropic_version=_text(raw.get("anthropic_version")) or "2023-06-01",
            default_model=_optional_text(raw.get("default_model")),
        )


@dataclass(frozen=True)
class ModelDefinition:
    model_id: str
    provider_id: str
    label: str
    model: str
    model_env: str | None
    supports_reasoning: bool | None
    vision: bool
    default_level: int

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "ModelDefinition":
        model_id = _text(raw.get("id"))
        provider_id = _text(raw.get("provider"))
        model = _text(raw.get("model"))
        if not model_id or not provider_id or not model:
            raise LlmConfigurationError(
                "Every llm_models entry requires id, provider, and model"
            )
        level = int(raw.get("default_level", 3))
        if level not in {2, 3, 4}:
            raise LlmConfigurationError(
                f"Model {model_id!r} default_level must be 2, 3, or 4"
            )
        reasoning = raw.get("supports_reasoning")
        if reasoning is not None:
            reasoning = bool(reasoning)
        return cls(
            model_id=model_id,
            provider_id=provider_id,
            label=_text(raw.get("label")) or model_id,
            model=model,
            model_env=_optional_text(raw.get("model_env")),
            supports_reasoning=reasoning,
            vision=bool(raw.get("vision", True)),
            default_level=level,
        )

    def resolved_model(self) -> str:
        value = os.environ.get(self.model_env, "").strip() if self.model_env else ""
        return value or self.model


@dataclass(frozen=True)
class ProfileDefinition:
    profile_id: str
    model_id: str
    label: str
    analysis_level: int
    single_enabled: bool
    batch_enabled: bool
    max_output_tokens: int
    temperature: float | None
    top_p: float | None
    reasoning_effort: str
    current_image_detail: str
    parent_image_detail: str
    timeout_seconds: float
    seed: int | None
    prompt_text: tuple[str, ...]

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "ProfileDefinition":
        profile_id = _text(raw.get("id"))
        model_id = _text(raw.get("model"))
        if not profile_id or not model_id:
            raise LlmConfigurationError(
                "Every llm_profiles entry requires id and model"
            )
        level = int(raw.get("analysis_level", 3))
        if level not in {2, 3, 4}:
            raise LlmConfigurationError(
                f"Profile {profile_id!r} analysis_level must be 2, 3, or 4"
            )
        names = raw.get("prompt_text")
        if not isinstance(names, list) or not names or not all(
            isinstance(name, str) and name.strip() for name in names
        ):
            raise LlmConfigurationError(
                f"Profile {profile_id!r} requires a nonempty prompt_text list"
            )
        normalized_names = tuple(name.strip() for name in names)
        if len(normalized_names) != len(set(normalized_names)):
            raise LlmConfigurationError(
                f"Profile {profile_id!r} prompt_text contains duplicates"
            )
        return cls(
            profile_id=profile_id,
            model_id=model_id,
            label=_text(raw.get("label")) or profile_id,
            analysis_level=level,
            single_enabled=bool(raw.get("single_enabled", False)),
            batch_enabled=bool(raw.get("batch_enabled", False)),
            max_output_tokens=int(raw.get("max_output_tokens", 12000)),
            temperature=(
                None if raw.get("temperature") is None else float(raw["temperature"])
            ),
            top_p=None if raw.get("top_p") is None else float(raw["top_p"]),
            reasoning_effort=_text(raw.get("reasoning_effort")) or "low",
            current_image_detail=_text(raw.get("current_image_detail")) or "low",
            parent_image_detail=_text(raw.get("parent_image_detail")) or "low",
            timeout_seconds=float(raw.get("timeout_seconds", 600.0)),
            seed=None if raw.get("seed") is None else int(raw["seed"]),
            prompt_text=normalized_names,
        )


class CatalogAwareLlmProviderRouter(StudioAwareLlmProviderRouter):
    """Router over provider backends, models, and level-specific profiles.

    The existing low-level adapters continue to receive a flat ProviderSpec.
    This class expands each profile into that compatibility shape at startup,
    while retaining the normalized three-layer catalog for the UI and runner.
    """

    def __init__(self, config_path: str | Path, **kwargs: Any) -> None:
        self.catalog_path = Path(config_path).expanduser().resolve()
        raw = json.loads(self.catalog_path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise LlmConfigurationError(
                f"LLM catalog must be one JSON object: {self.catalog_path}"
            )
        prompt_text = raw.get("prompt_text")
        if not isinstance(prompt_text, Mapping) or not prompt_text:
            raise LlmConfigurationError("LLM catalog requires prompt_text")

        provider_items = raw.get("llm_providers")
        model_items = raw.get("llm_models")
        profile_items = raw.get("llm_profiles")
        if not isinstance(provider_items, list) or not provider_items:
            raise LlmConfigurationError("LLM catalog requires llm_providers")
        if not isinstance(model_items, list) or not model_items:
            raise LlmConfigurationError("LLM catalog requires llm_models")
        if not isinstance(profile_items, list) or not profile_items:
            raise LlmConfigurationError("LLM catalog requires llm_profiles")

        self.backends = tuple(
            ProviderBackend.from_mapping(item)
            for item in provider_items
            if isinstance(item, Mapping)
        )
        self.models = tuple(
            ModelDefinition.from_mapping(item)
            for item in model_items
            if isinstance(item, Mapping)
        )
        self.profiles = tuple(
            ProfileDefinition.from_mapping(item)
            for item in profile_items
            if isinstance(item, Mapping)
        )
        self.backend_by_id = {item.backend_id: item for item in self.backends}
        self.model_by_id = {item.model_id: item for item in self.models}
        self.profile_by_id = {item.profile_id: item for item in self.profiles}
        for name, values, expected in (
            ("provider backend", self.backend_by_id, len(self.backends)),
            ("model", self.model_by_id, len(self.models)),
            ("profile", self.profile_by_id, len(self.profiles)),
        ):
            if len(values) != expected:
                raise LlmConfigurationError(f"Duplicate {name} ids are not allowed")

        for model in self.models:
            if model.provider_id not in self.backend_by_id:
                raise LlmConfigurationError(
                    f"Model {model.model_id!r} references unknown provider "
                    f"{model.provider_id!r}"
                )
        for profile in self.profiles:
            if profile.model_id not in self.model_by_id:
                raise LlmConfigurationError(
                    f"Profile {profile.profile_id!r} references unknown model "
                    f"{profile.model_id!r}"
                )
            missing = [name for name in profile.prompt_text if name not in prompt_text]
            if missing:
                raise LlmConfigurationError(
                    f"Profile {profile.profile_id!r} references unknown prompt sections: "
                    + ", ".join(missing)
                )
            if profile.max_output_tokens <= 0 or profile.timeout_seconds <= 0:
                raise LlmConfigurationError(
                    f"Profile {profile.profile_id!r} token and timeout values must be positive"
                )

        self.default_model_id = self._resolve_default_model(raw)
        self.default_profile_id = self._resolve_default_profile(raw)
        expanded = self._expanded_config(raw)
        handle, temporary_name = tempfile.mkstemp(
            prefix="arc3_llm_catalog_", suffix=".json"
        )
        os.close(handle)
        self._expanded_config_path = Path(temporary_name)
        self._expanded_config_path.write_text(
            json.dumps(expanded, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        original_env = os.environ.get("ARC3_LLM_PROVIDER")
        translated = self._translate_selection(original_env) if original_env else None
        try:
            if translated:
                os.environ["ARC3_LLM_PROVIDER"] = translated
            elif original_env:
                os.environ.pop("ARC3_LLM_PROVIDER", None)
            super().__init__(self._expanded_config_path, **kwargs)
        finally:
            if original_env is None:
                os.environ.pop("ARC3_LLM_PROVIDER", None)
            else:
                os.environ["ARC3_LLM_PROVIDER"] = original_env

        self.config_path = self.catalog_path
        self._active_model_id = self.model_for_profile(
            getattr(self, "_active_id", None) or self.default_profile_id
        ).model_id

    def __del__(self) -> None:
        try:
            self._expanded_config_path.unlink(missing_ok=True)
        except Exception:
            pass

    def _resolve_default_model(self, raw: Mapping[str, Any]) -> str:
        candidate = _text(raw.get("default_model"))
        if candidate in self.model_by_id:
            return candidate
        legacy = _text(raw.get("default_provider"))
        if legacy in self.model_by_id:
            return legacy
        if legacy in self.backend_by_id:
            default = self.backend_by_id[legacy].default_model
            if default in self.model_by_id:
                return str(default)
        return self.models[0].model_id

    def _resolve_default_profile(self, raw: Mapping[str, Any]) -> str:
        candidate = _text(raw.get("default_profile"))
        if candidate in self.profile_by_id:
            return candidate
        return self.default_profile_for_model(self.default_model_id).profile_id

    def _translate_selection(self, value: str | None) -> str | None:
        wanted = _text(value)
        if not wanted:
            return None
        if wanted in self.profile_by_id:
            return wanted
        if wanted in self.model_by_id:
            return self.default_profile_for_model(wanted).profile_id
        backend = self.backend_by_id.get(wanted)
        if backend and backend.default_model in self.model_by_id:
            return self.default_profile_for_model(str(backend.default_model)).profile_id
        return None

    def _expanded_config(self, raw: Mapping[str, Any]) -> dict[str, Any]:
        rows: list[dict[str, Any]] = []
        for profile in self.profiles:
            model = self.model_by_id[profile.model_id]
            backend = self.backend_by_id[model.provider_id]
            supports_reasoning = (
                backend.supports_reasoning
                if model.supports_reasoning is None
                else model.supports_reasoning
            )
            rows.append(
                {
                    "id": profile.profile_id,
                    "label": profile.label,
                    "adapter": backend.adapter,
                    "model": model.resolved_model(),
                    "model_env": model.model_env,
                    "api_key_env": backend.api_key_env,
                    "api_key_optional": backend.api_key_optional,
                    "base_url": backend.base_url,
                    "base_url_env": backend.base_url_env,
                    "health_url": backend.health_url,
                    "health_url_env": backend.health_url_env,
                    "enabled": backend.enabled,
                    "supports_reasoning": supports_reasoning,
                    "timeout_seconds": profile.timeout_seconds,
                    "anthropic_version": backend.anthropic_version,
                    "prompt_text": list(profile.prompt_text),
                }
            )
        return {
            "default_provider": self.default_profile_id,
            "prompt_text": raw["prompt_text"],
            "llm_providers": rows,
        }

    @staticmethod
    def _is_unsloth(spec: ProviderSpec) -> bool:
        return spec.api_key_env == "ARC3_UNSLOTH_API_KEY"

    def profile_for_spec(self, spec: ProviderSpec | None = None) -> ProfileDefinition:
        selected = spec or self.current_spec()
        return self.profile_by_id[selected.provider_id]

    def model_for_profile(
        self, profile: str | ProfileDefinition | ProviderSpec
    ) -> ModelDefinition:
        if isinstance(profile, ProviderSpec):
            profile_id = profile.provider_id
        elif isinstance(profile, ProfileDefinition):
            profile_id = profile.profile_id
        else:
            profile_id = profile
        return self.model_by_id[self.profile_by_id[profile_id].model_id]

    def backend_for_profile(
        self, profile: str | ProfileDefinition | ProviderSpec
    ) -> ProviderBackend:
        model = self.model_for_profile(profile)
        return self.backend_by_id[model.provider_id]

    def profiles_for_model(self, model_id: str) -> tuple[ProfileDefinition, ...]:
        return tuple(
            profile for profile in self.profiles if profile.model_id == model_id
        )

    def default_profile_for_model(self, model_id: str) -> ProfileDefinition:
        model = self.model_by_id[model_id]
        profiles = self.profiles_for_model(model_id)
        exact = next(
            (
                profile
                for profile in profiles
                if profile.analysis_level == model.default_level
                and profile.single_enabled
            ),
            None,
        )
        return exact or next(
            (profile for profile in profiles if profile.single_enabled),
            profiles[0],
        )

    def configured_profile_specs(
        self, *, single: bool | None = None, batch: bool | None = None
    ) -> tuple[ProviderSpec, ...]:
        result: list[ProviderSpec] = []
        by_id = {spec.provider_id: spec for spec in self.specs}
        for profile in self.profiles:
            if single is not None and profile.single_enabled is not single:
                continue
            if batch is not None and profile.batch_enabled is not batch:
                continue
            spec = by_id[profile.profile_id]
            if spec.configuration_state()[0]:
                result.append(spec)
        return tuple(result)

    def configured_model_ids(self) -> tuple[str, ...]:
        configured = {
            self.profile_by_id[spec.provider_id].model_id
            for spec in self.configured_profile_specs(single=True)
        }
        return tuple(
            model.model_id for model in self.models if model.model_id in configured
        )

    def select_model(self, model_id: str) -> ProviderSpec:
        if model_id not in self.model_by_id:
            raise LlmConfigurationError(f"Unknown LLM model {model_id!r}")
        profiles = [
            profile
            for profile in self.profiles_for_model(model_id)
            if profile.single_enabled
        ]
        if not profiles:
            raise LlmConfigurationError(
                f"Model {model_id!r} has no single_enabled profile"
            )
        preferred = self.default_profile_for_model(model_id)
        candidates = [preferred, *[p for p in profiles if p != preferred]]
        for profile in candidates:
            spec = next(s for s in self.specs if s.provider_id == profile.profile_id)
            if spec.configuration_state()[0]:
                self._active_model_id = model_id
                return super().select(profile.profile_id)
        raise LlmConfigurationError(
            f"Model {model_id!r} has no configured single profile"
        )

    def cycle_model(self) -> ProviderSpec:
        model_ids = self.configured_model_ids()
        if not model_ids:
            raise LlmConfigurationError("No configured single-run LLM models")
        current = getattr(self, "_active_model_id", None)
        index = model_ids.index(current) if current in model_ids else -1
        return self.select_model(model_ids[(index + 1) % len(model_ids)])

    def activate_level(self, level: int, *, mode: str = "single") -> ProviderSpec:
        model_id = getattr(self, "_active_model_id", self.default_model_id)
        flag = "single_enabled" if mode == "single" else "batch_enabled"
        profile = next(
            (
                item
                for item in self.profiles_for_model(model_id)
                if item.analysis_level == level and getattr(item, flag)
            ),
            None,
        )
        if profile is None:
            raise LlmConfigurationError(
                f"Model {model_id!r} has no {mode}-enabled level {level} profile"
            )
        return self.select_profile(profile.profile_id, mode=mode)

    def select_profile(self, profile_id: str, *, mode: str | None = None) -> ProviderSpec:
        profile = self.profile_by_id.get(profile_id)
        if profile is None:
            raise LlmConfigurationError(f"Unknown LLM profile {profile_id!r}")
        if mode == "single" and not profile.single_enabled:
            raise LlmConfigurationError(
                f"Profile {profile_id!r} is not enabled for single runs"
            )
        if mode == "batch" and not profile.batch_enabled:
            raise LlmConfigurationError(
                f"Profile {profile_id!r} is not enabled for batch runs"
            )
        self._active_model_id = profile.model_id
        return super().select(profile_id)

    def select(self, provider_id: str) -> ProviderSpec:
        return self.select_profile(provider_id)

    def batch_profiles(self) -> tuple[ProfileDefinition, ...]:
        return tuple(profile for profile in self.profiles if profile.batch_enabled)

    def active_model(self) -> ModelDefinition:
        return self.model_by_id[
            getattr(self, "_active_model_id", self.default_model_id)
        ]

    def describe_current(self) -> str:
        spec = self.current_spec()
        profile = self.profile_for_spec(spec)
        model = self.model_for_profile(profile)
        backend = self.backend_for_profile(profile)
        prompt_names = ",".join(profile.prompt_text)
        endpoint = f" @ {spec.resolved_base_url()}" if spec.resolved_base_url() else ""
        return (
            f"{model.label} [{model.model_id}] via {backend.label} "
            f"profile={profile.profile_id} L{profile.analysis_level} "
            f"model={spec.resolved_model()}{endpoint} prompt_text=[{prompt_names}]"
        )

    @contextmanager
    def profile_environment(
        self, profile: ProfileDefinition | str | None = None
    ) -> Iterator[None]:
        selected = (
            self.profile_by_id[profile]
            if isinstance(profile, str)
            else profile or self.profile_for_spec()
        )
        model = self.model_by_id[selected.model_id]
        prefix = f"ARC3_GPT_{selected.analysis_level}_"
        values: dict[str, Any] = {
            prefix + "MAX_OUTPUT_TOKENS": selected.max_output_tokens,
            prefix + "REASONING_EFFORT": selected.reasoning_effort,
            prefix + "IMAGE_DETAIL": selected.current_image_detail,
            prefix + "PARENT_IMAGE_DETAIL": selected.parent_image_detail,
            "ARC3_LLM_TEMPERATURE": selected.temperature,
            "ARC3_LLM_TOP_P": selected.top_p,
            "ARC3_LLM_SEED": selected.seed,
            "ARC3_LLM_TIMEOUT_SECONDS": selected.timeout_seconds,
        }
        if model.model_env:
            values[model.model_env] = model.model
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
