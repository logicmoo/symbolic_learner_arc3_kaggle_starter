from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import replace
from typing import Any, Callable, Mapping

from llm_providers import (
    LlmConfigurationError,
    LlmProviderRouter,
    LlmRequestError,
    ProviderSpec,
    ProviderStatus,
)


def _env_bool(name: str, default: bool) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on", "y"}:
        return True
    if normalized in {"0", "false", "no", "off", "n"}:
        return False
    raise LlmConfigurationError(f"{name} must be a boolean value, not {value!r}")


def _env_int(name: str, default: int, *, minimum: int = 1) -> int:
    value = os.environ.get(name)
    try:
        result = int(value) if value is not None else default
    except ValueError as error:
        raise LlmConfigurationError(f"{name} must be an integer, not {value!r}") from error
    if result < minimum:
        raise LlmConfigurationError(f"{name} must be at least {minimum}")
    return result


def _text(value: Any) -> str:
    return str(value or "").strip()


class StudioAwareLlmProviderRouter(LlmProviderRouter):
    """LLM router that manages the resident model in Unsloth Studio.

    Unsloth Studio can be healthy and authenticated while its llama-server has
    no model loaded. Before an Unsloth `/v1/responses` request, this router uses
    the authenticated management API to inspect `/api/inference/status`, load
    the configured GGUF through `/api/inference/load` when necessary, and wait
    until the requested model is resident.
    """

    def __init__(
        self,
        *args: Any,
        sleep: Callable[[float], None] | None = None,
        clock: Callable[[], float] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._sleep = sleep or time.sleep
        self._clock = clock or time.monotonic

    @staticmethod
    def _is_unsloth(spec: ProviderSpec) -> bool:
        return spec.provider_id.lower() == "unsloth"

    @staticmethod
    def _studio_root(spec: ProviderSpec) -> str:
        base_url = spec.resolved_base_url()
        if not base_url:
            raise LlmConfigurationError("Unsloth provider requires a base URL")
        return base_url[:-3] if base_url.endswith("/v1") else base_url

    def _status_url(self, spec: ProviderSpec) -> str:
        return os.environ.get("ARC3_UNSLOTH_STATUS_URL", "").strip() or (
            self._studio_root(spec) + "/api/inference/status"
        )

    def _load_url(self, spec: ProviderSpec) -> str:
        return os.environ.get("ARC3_UNSLOTH_LOAD_URL", "").strip() or (
            self._studio_root(spec) + "/api/inference/load"
        )

    @staticmethod
    def _api_key(spec: ProviderSpec) -> str:
        key = spec.resolved_api_key()
        if not key:
            raise LlmConfigurationError(
                "Unsloth Studio requires ARC3_UNSLOTH_API_KEY for its external API"
            )
        if not key.startswith("sk-unsloth-"):
            raise LlmConfigurationError(
                "ARC3_UNSLOTH_API_KEY must be an Unsloth Studio key beginning "
                "with 'sk-unsloth-'"
            )
        return key

    def _request_json(
        self,
        url: str,
        *,
        api_key: str,
        method: str = "GET",
        body: Mapping[str, Any] | None = None,
        timeout: float = 30.0,
    ) -> dict[str, Any]:
        data = json.dumps(dict(body)).encode("utf-8") if body is not None else None
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
        if data is not None:
            headers["Content-Type"] = "application/json"
        request = urllib.request.Request(
            url,
            data=data,
            method=method,
            headers=headers,
        )
        try:
            with self._urlopen(request, timeout=timeout) as response:
                raw = response.read().decode("utf-8", errors="replace").strip()
        except urllib.error.HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace").strip()
            try:
                parsed = json.loads(detail)
                detail = _text(parsed.get("detail")) or detail
            except (json.JSONDecodeError, AttributeError):
                pass
            raise LlmRequestError(
                f"Unsloth Studio management request failed with HTTP "
                f"{error.code} at {url}: {detail}"
            ) from error
        except Exception as error:
            raise LlmRequestError(
                f"Unable to reach Unsloth Studio management API at {url}: {error}"
            ) from error

        if not raw:
            return {}
        try:
            result = json.loads(raw)
        except json.JSONDecodeError as error:
            raise LlmRequestError(
                f"Unsloth Studio returned invalid JSON from {url}: {raw[:240]}"
            ) from error
        if not isinstance(result, dict):
            raise LlmRequestError(
                f"Unsloth Studio returned a non-object response from {url}"
            )
        deferred = result.get("_deferred_error")
        if isinstance(deferred, Mapping):
            raise LlmRequestError(
                "Unsloth Studio model load failed: "
                + _text(deferred.get("detail") or deferred)
            )
        return result

    def _inference_status(self, spec: ProviderSpec) -> dict[str, Any]:
        return self._request_json(
            self._status_url(spec),
            api_key=self._api_key(spec),
            timeout=5.0,
        )

    @staticmethod
    def _candidate_models(status: Mapping[str, Any]) -> tuple[str, ...]:
        values: list[str] = []
        for key in ("model_identifier", "active_model"):
            value = _text(status.get(key))
            if value:
                values.append(value)
        loaded = status.get("loaded")
        if isinstance(loaded, list):
            values.extend(_text(value) for value in loaded if _text(value))
        return tuple(values)

    @staticmethod
    def _model_matches(
        status: Mapping[str, Any],
        model: str,
        variant: str | None,
    ) -> bool:
        wanted = model.casefold()
        model_matches = any(
            candidate.casefold() == wanted
            or candidate.casefold().startswith(wanted + ":")
            for candidate in StudioAwareLlmProviderRouter._candidate_models(status)
        )
        if not model_matches:
            return False
        active_variant = _text(status.get("gguf_variant"))
        return not variant or not active_variant or active_variant.casefold() == variant.casefold()

    @staticmethod
    def _loading_models(status: Mapping[str, Any]) -> tuple[str, ...]:
        loading = status.get("loading")
        if not isinstance(loading, list):
            return ()
        return tuple(_text(value) for value in loading if _text(value))

    def _load_payload(self, spec: ProviderSpec) -> dict[str, Any]:
        variant = os.environ.get(
            "ARC3_UNSLOTH_GGUF_VARIANT", "UD-Q4_K_XL"
        ).strip() or None
        cache_type = os.environ.get("ARC3_UNSLOTH_CACHE_TYPE_KV", "").strip() or None
        speculative = os.environ.get(
            "ARC3_UNSLOTH_SPECULATIVE_TYPE", ""
        ).strip() or None
        payload: dict[str, Any] = {
            "model_path": spec.resolved_model(),
            "hf_token": (
                os.environ.get("HF_TOKEN")
                or os.environ.get("HUGGING_FACE_HUB_TOKEN")
                or None
            ),
            "max_seq_length": _env_int(
                "ARC3_UNSLOTH_MAX_SEQ_LENGTH", 131072
            ),
            "load_in_4bit": False,
            "is_lora": False,
            "gguf_variant": variant,
            "trust_remote_code": _env_bool(
                "ARC3_UNSLOTH_TRUST_REMOTE_CODE", False
            ),
            "cache_type_kv": cache_type,
            "speculative_type": speculative,
            "n_parallel": _env_int("ARC3_UNSLOTH_N_PARALLEL", 1),
            "gpu_memory_mode": os.environ.get(
                "ARC3_UNSLOTH_GPU_MEMORY_MODE", "auto"
            ).strip()
            or "auto",
            "force_cancel_active": _env_bool(
                "ARC3_UNSLOTH_FORCE_CANCEL_ACTIVE", False
            ),
        }
        return {key: value for key, value in payload.items() if value is not None}

    def _wait_until_loaded(
        self,
        spec: ProviderSpec,
        *,
        model: str,
        variant: str | None,
        deadline: float,
    ) -> dict[str, Any]:
        last_status: dict[str, Any] = {}
        while self._clock() < deadline:
            last_status = self._inference_status(spec)
            if self._model_matches(last_status, model, variant):
                return last_status
            self._sleep(1.0)
        active = ", ".join(self._candidate_models(last_status)) or "none"
        loading = ", ".join(self._loading_models(last_status)) or "none"
        raise LlmRequestError(
            f"Timed out waiting for Unsloth Studio to load {model}; "
            f"active={active}, loading={loading}"
        )

    def ensure_unsloth_model_loaded(
        self,
        spec: ProviderSpec,
        *,
        force: bool = False,
    ) -> dict[str, Any]:
        if not self._is_unsloth(spec):
            return {}
        model = spec.resolved_model()
        if not model:
            raise LlmConfigurationError("Unsloth provider has no configured model")
        variant = os.environ.get(
            "ARC3_UNSLOTH_GGUF_VARIANT", "UD-Q4_K_XL"
        ).strip() or None
        timeout = float(os.environ.get("ARC3_UNSLOTH_LOAD_TIMEOUT", "900"))
        if timeout <= 0:
            raise LlmConfigurationError("ARC3_UNSLOTH_LOAD_TIMEOUT must be positive")
        deadline = self._clock() + timeout

        status = self._inference_status(spec)
        if not force and self._model_matches(status, model, variant):
            return status

        if self._loading_models(status):
            print(
                "Unsloth Studio is already loading a model; waiting for the "
                "inference service to become ready..."
            )
            status = self._wait_until_loaded(
                spec,
                model=model,
                variant=variant,
                deadline=deadline,
            )
            if self._model_matches(status, model, variant):
                return status

        if not _env_bool("ARC3_UNSLOTH_AUTO_LOAD", True):
            raise LlmRequestError(
                f"Unsloth Studio has no matching loaded model. Load {model} in "
                "Studio or set ARC3_UNSLOTH_AUTO_LOAD=1."
            )

        payload = self._load_payload(spec)
        variant_note = f" ({variant})" if variant else ""
        print(
            f"Unsloth Studio: loading {model}{variant_note} with "
            f"context={payload['max_seq_length']}..."
        )
        self._request_json(
            self._load_url(spec),
            api_key=self._api_key(spec),
            method="POST",
            body=payload,
            timeout=timeout,
        )
        status = self._wait_until_loaded(
            spec,
            model=model,
            variant=variant,
            deadline=deadline,
        )
        print(f"Unsloth Studio model ready: {model}{variant_note}")
        return status

    def statuses(self, *, probe: bool = False) -> tuple[ProviderStatus, ...]:
        base_statuses = super().statuses(probe=False)
        if not probe:
            return base_statuses
        specs = {spec.provider_id: spec for spec in self.specs}
        result: list[ProviderStatus] = []
        for status in base_statuses:
            spec = specs[status.provider_id]
            if not status.configured or not self._is_unsloth(spec):
                result.append(status)
                continue
            try:
                inference = self._inference_status(spec)
                active = self._candidate_models(inference)
                loading = self._loading_models(inference)
                variant = os.environ.get(
                    "ARC3_UNSLOTH_GGUF_VARIANT", "UD-Q4_K_XL"
                ).strip() or None
                if self._model_matches(inference, spec.resolved_model(), variant):
                    state = "ready: " + (active[0] if active else spec.resolved_model())
                elif loading:
                    state = "loading: " + ", ".join(loading)
                elif active:
                    state = (
                        "ready with different model: "
                        + active[0]
                        + "; will auto-load selected model"
                    )
                else:
                    state = "server ready; no model loaded; will auto-load"
                result.append(replace(status, state=state))
            except Exception as error:
                result.append(replace(status, state=f"unavailable: {error}"))
        return tuple(result)

    def create_response(self, **kwargs: Any) -> Any:
        spec = self.current_spec()
        if not self._is_unsloth(spec):
            return super().create_response(**kwargs)

        self.ensure_unsloth_model_loaded(spec)
        try:
            return super().create_response(**kwargs)
        except LlmRequestError as error:
            message = str(error).casefold()
            if "no model loaded" not in message:
                raise
            # Studio can unload an idle model between the status check and the
            # request. Reload exactly once and retry the original analysis call.
            self.ensure_unsloth_model_loaded(spec, force=True)
            return super().create_response(**kwargs)
