from __future__ import annotations

import base64
import json
import os
import re
import socket
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Callable, Mapping

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[1] / "config" / "llm_providers.json"
_DATA_URL_RE = re.compile(r"^data:([^;,]+);base64,(.*)$", re.DOTALL)


class LlmConfigurationError(RuntimeError):
    """Raised when no usable LLM provider can be selected."""


class LlmRequestError(RuntimeError):
    """Raised when a provider request fails or returns no text."""


def _optional_text(value: Any) -> str | None:
    text = str(value or "").strip()
    return text or None


def _normalize_prompt_text(value: Any, *, key: str) -> str:
    if isinstance(value, str):
        text = value
    elif isinstance(value, list) and all(isinstance(line, str) for line in value):
        text = "\n".join(value)
    else:
        raise LlmConfigurationError(
            f"prompt_text {key!r} must be a string or an array of strings"
        )
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return "\n".join(line.rstrip() for line in text.split("\n")).strip("\n")


def _prompt_names(value: Any, *, provider_id: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise LlmConfigurationError(
            f"Provider {provider_id!r} prompt_text must be an array of section names"
        )
    names = tuple(item.strip() for item in value if item.strip())
    if len(names) != len(set(names)):
        raise LlmConfigurationError(
            f"Provider {provider_id!r} prompt_text contains duplicate section names"
        )
    return names


def _metadata_value(value: Any, depth: int = 0) -> Any:
    if depth > 5:
        return repr(value)
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Mapping):
        return {
            str(key): _metadata_value(item, depth + 1)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [_metadata_value(item, depth + 1) for item in value]
    for method_name in ("model_dump", "dict"):
        method = getattr(value, method_name, None)
        if callable(method):
            try:
                return _metadata_value(method(), depth + 1)
            except Exception:
                pass
    if hasattr(value, "__dict__"):
        public = {
            key: item
            for key, item in vars(value).items()
            if not key.startswith("_")
        }
        if public:
            return _metadata_value(public, depth + 1)
    return repr(value)


@dataclass(frozen=True)
class ProviderSpec:
    provider_id: str
    label: str
    adapter: str
    model: str
    enabled: bool | str = "auto"
    model_env: str | None = None
    api_key_env: str | None = None
    api_key_optional: bool = False
    base_url: str | None = None
    base_url_env: str | None = None
    health_url: str | None = None
    health_url_env: str | None = None
    supports_reasoning: bool = False
    timeout_seconds: float = 600.0
    anthropic_version: str = "2023-06-01"
    prompt_text: tuple[str, ...] = ()

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "ProviderSpec":
        provider_id = str(raw.get("id") or "").strip()
        if not provider_id:
            raise LlmConfigurationError("Every LLM provider requires a nonempty id")
        adapter = str(raw.get("adapter") or "").strip()
        if adapter not in {"openai_responses", "anthropic_messages"}:
            raise LlmConfigurationError(
                f"Provider {provider_id!r} has unsupported adapter {adapter!r}"
            )
        enabled = raw.get("enabled", "auto")
        if enabled not in {True, False, "auto"}:
            raise LlmConfigurationError(
                f"Provider {provider_id!r} enabled must be true, false, or 'auto'"
            )
        return cls(
            provider_id=provider_id,
            label=str(raw.get("label") or provider_id),
            adapter=adapter,
            model=str(raw.get("model") or "").strip(),
            enabled=enabled,
            model_env=_optional_text(raw.get("model_env")),
            api_key_env=_optional_text(raw.get("api_key_env")),
            api_key_optional=bool(raw.get("api_key_optional", False)),
            base_url=_optional_text(raw.get("base_url")),
            base_url_env=_optional_text(raw.get("base_url_env")),
            health_url=_optional_text(raw.get("health_url")),
            health_url_env=_optional_text(raw.get("health_url_env")),
            supports_reasoning=bool(raw.get("supports_reasoning", False)),
            timeout_seconds=float(raw.get("timeout_seconds", 600.0)),
            anthropic_version=str(raw.get("anthropic_version") or "2023-06-01"),
            prompt_text=_prompt_names(raw.get("prompt_text"), provider_id=provider_id),
        )

    def resolved_model(self) -> str:
        value = os.environ.get(self.model_env, "").strip() if self.model_env else ""
        return value or self.model

    def resolved_api_key(self) -> str | None:
        if not self.api_key_env:
            return None
        return os.environ.get(self.api_key_env) or None

    def resolved_base_url(self) -> str | None:
        value = os.environ.get(self.base_url_env, "").strip() if self.base_url_env else ""
        return (value or self.base_url or "").rstrip("/") or None

    def resolved_health_url(self) -> str | None:
        value = os.environ.get(self.health_url_env, "").strip() if self.health_url_env else ""
        return (value or self.health_url or "").strip() or None

    def configuration_state(self) -> tuple[bool, str]:
        if self.enabled is False:
            return False, "disabled"
        if not self.resolved_model():
            return False, "missing model"
        key = self.resolved_api_key()
        if self.api_key_env and not self.api_key_optional and not key:
            return False, f"missing {self.api_key_env}"
        return True, "configured"


@dataclass(frozen=True)
class ProviderStatus:
    provider_id: str
    label: str
    model: str
    configured: bool
    state: str
    active: bool
    base_url: str | None


class _ResponsesFacade:
    def __init__(self, router: "LlmProviderRouter") -> None:
        self._router = router

    def create(self, **kwargs: Any) -> Any:
        return self._router.create_response(**kwargs)


class LlmProviderRouter:
    """OpenAI-Responses-shaped router over cloud and local LLM providers.

    Provider definitions and reusable prompt sections share one JSON config.
    Each provider selects an ordered list of ``prompt_text`` section names, so
    expensive or irrelevant sections such as ``transitions`` can be omitted
    without copying or editing one monolithic combined prompt.
    """

    def __init__(
        self,
        config_path: str | Path | None = None,
        *,
        openai_client_factory: Callable[..., Any] | None = None,
        urlopen: Callable[..., Any] | None = None,
    ) -> None:
        selected_path = Path(
            os.environ.get("ARC3_LLM_CONFIG") or config_path or DEFAULT_CONFIG_PATH
        ).expanduser().resolve()
        self.config_path = selected_path
        raw = json.loads(selected_path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise LlmConfigurationError(f"LLM config must be one JSON object: {selected_path}")

        raw_prompt_text = raw.get("prompt_text")
        if not isinstance(raw_prompt_text, Mapping) or not raw_prompt_text:
            raise LlmConfigurationError(
                f"LLM config must contain a nonempty prompt_text object: {selected_path}"
            )
        self.prompt_text = {
            str(key): _normalize_prompt_text(value, key=str(key))
            for key, value in raw_prompt_text.items()
        }
        self.default_prompt_text = _prompt_names(
            raw.get("default_prompt_text"),
            provider_id="default_prompt_text",
        )

        providers = raw.get("llm_providers")
        if providers is None:
            providers = raw.get("providers")  # compatibility with earlier configs
        if not isinstance(providers, list) or not providers:
            raise LlmConfigurationError(
                f"LLM config must contain a nonempty llm_providers list: {selected_path}"
            )
        self.specs = tuple(ProviderSpec.from_mapping(item) for item in providers)
        ids = [spec.provider_id for spec in self.specs]
        if len(ids) != len(set(ids)):
            raise LlmConfigurationError("LLM provider ids must be unique")
        for spec in self.specs:
            names = spec.prompt_text or self.default_prompt_text
            if not names:
                raise LlmConfigurationError(
                    f"Provider {spec.provider_id!r} must select at least one prompt_text section"
                )
            missing = [name for name in names if name not in self.prompt_text]
            if missing:
                raise LlmConfigurationError(
                    f"Provider {spec.provider_id!r} references unknown prompt_text sections: "
                    + ", ".join(missing)
                )

        self.default_provider = str(raw.get("default_provider") or "").strip() or None
        env_default = os.environ.get("ARC3_LLM_PROVIDER", "").strip()
        if env_default:
            self.default_provider = env_default
        self._active_id: str | None = None
        self._openai_clients: dict[tuple[str, str | None, str], Any] = {}
        self._openai_client_factory = openai_client_factory
        self._urlopen = urlopen or urllib.request.urlopen
        self.responses = _ResponsesFacade(self)

    def configured_specs(self) -> tuple[ProviderSpec, ...]:
        return tuple(spec for spec in self.specs if spec.configuration_state()[0])

    def current_spec(self) -> ProviderSpec:
        configured = self.configured_specs()
        if not configured:
            reasons = ", ".join(
                f"{spec.provider_id}: {spec.configuration_state()[1]}"
                for spec in self.specs
            )
            raise LlmConfigurationError(f"No configured LLM providers ({reasons})")
        if self._active_id:
            match = next(
                (spec for spec in configured if spec.provider_id == self._active_id),
                None,
            )
            if match is not None:
                return match
        preferred = next(
            (spec for spec in configured if spec.provider_id == self.default_provider),
            None,
        )
        chosen = preferred or configured[0]
        self._active_id = chosen.provider_id
        return chosen

    def prompt_section_names(self, spec: ProviderSpec | None = None) -> tuple[str, ...]:
        selected = spec or self.current_spec()
        return selected.prompt_text or self.default_prompt_text

    def prompt_sections(
        self,
        spec: ProviderSpec | None = None,
    ) -> tuple[tuple[str, str], ...]:
        names = self.prompt_section_names(spec)
        return tuple((name, self.prompt_text[name]) for name in names)

    def compose_prompt(self, spec: ProviderSpec | None = None) -> str:
        return "\n\n".join(text for _, text in self.prompt_sections(spec)).strip()

    def cycle(self) -> ProviderSpec:
        configured = self.configured_specs()
        if not configured:
            return self.current_spec()
        if self._active_id is None:
            return self.current_spec()
        current_index = next(
            (
                index
                for index, spec in enumerate(configured)
                if spec.provider_id == self._active_id
            ),
            -1,
        )
        chosen = configured[(current_index + 1) % len(configured)]
        self._active_id = chosen.provider_id
        return chosen

    def select(self, provider_id: str) -> ProviderSpec:
        configured = self.configured_specs()
        match = next((spec for spec in configured if spec.provider_id == provider_id), None)
        if match is None:
            known = ", ".join(spec.provider_id for spec in configured) or "none"
            raise LlmConfigurationError(
                f"LLM provider {provider_id!r} is not configured; available: {known}"
            )
        self._active_id = match.provider_id
        return match

    def statuses(self, *, probe: bool = False) -> tuple[ProviderStatus, ...]:
        result: list[ProviderStatus] = []
        for spec in self.specs:
            configured, state = spec.configuration_state()
            if configured and probe and spec.resolved_health_url():
                ok, detail = self._probe(spec.resolved_health_url() or "")
                state = "ready" if ok else f"offline: {detail}"
            result.append(
                ProviderStatus(
                    provider_id=spec.provider_id,
                    label=spec.label,
                    model=spec.resolved_model(),
                    configured=configured,
                    state=state,
                    active=spec.provider_id == self._active_id,
                    base_url=spec.resolved_base_url(),
                )
            )
        return tuple(result)

    def _probe(self, url: str) -> tuple[bool, str]:
        request = urllib.request.Request(url, headers={"Accept": "application/json"})
        try:
            with self._urlopen(request, timeout=0.4) as response:
                status = int(getattr(response, "status", 200))
                return 200 <= status < 300, f"HTTP {status}"
        except Exception as exc:
            if isinstance(exc, urllib.error.URLError):
                return False, str(exc.reason)
            if isinstance(exc, socket.timeout):
                return False, "timeout"
            return False, str(exc)

    def describe_current(self) -> str:
        spec = self.current_spec()
        endpoint = f" @ {spec.resolved_base_url()}" if spec.resolved_base_url() else ""
        prompt_names = ",".join(self.prompt_section_names(spec))
        return (
            f"{spec.label} [{spec.provider_id}] model={spec.resolved_model()}{endpoint} "
            f"prompt_text=[{prompt_names}]"
        )

    def create_response(self, **kwargs: Any) -> Any:
        spec = self.current_spec()
        model = spec.resolved_model() or str(kwargs.get("model") or "")
        if not model:
            raise LlmConfigurationError(f"Provider {spec.provider_id} has no model")
        if spec.adapter == "openai_responses":
            output, metadata = self._openai_response(spec, model=model, request=kwargs)
        elif spec.adapter == "anthropic_messages":
            output, metadata = self._anthropic_response(spec, model=model, request=kwargs)
        else:
            raise LlmConfigurationError(f"Unsupported adapter: {spec.adapter}")
        if not output.strip():
            raise LlmRequestError(
                f"Provider {spec.provider_id} returned no textual response"
            )
        metadata.update(
            {
                "provider_id": spec.provider_id,
                "adapter": spec.adapter,
                "requested_model": model,
                "prompt_text": list(self.prompt_section_names(spec)),
            }
        )
        return SimpleNamespace(output_text=output, provider_metadata=metadata)

    def _openai_response(
        self,
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
        cache_key = (spec.provider_id, base_url, api_key or "local-no-key")
        client = self._openai_clients.get(cache_key)
        if client is None:
            factory = self._openai_client_factory
            if factory is None:
                from openai import OpenAI

                factory = OpenAI
            client = factory(api_key=api_key or "local-no-key", base_url=base_url)
            self._openai_clients[cache_key] = client

        payload: dict[str, Any] = {
            "model": model,
            "input": request.get("input"),
            "max_output_tokens": request.get("max_output_tokens"),
        }
        if spec.supports_reasoning and request.get("reasoning"):
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
        }
        return str(output or ""), metadata

    def _anthropic_response(
        self,
        spec: ProviderSpec,
        *,
        model: str,
        request: Mapping[str, Any],
    ) -> tuple[str, dict[str, Any]]:
        api_key = spec.resolved_api_key()
        if not api_key:
            raise LlmConfigurationError(
                f"Provider {spec.provider_id} requires {spec.api_key_env or 'ANTHROPIC_API_KEY'}"
            )
        base_url = spec.resolved_base_url() or "https://api.anthropic.com/v1"
        endpoint = base_url if base_url.endswith("/messages") else base_url + "/messages"
        system_parts: list[str] = []
        messages: list[dict[str, Any]] = []
        for message in request.get("input") or []:
            if not isinstance(message, Mapping):
                continue
            role = str(message.get("role") or "user")
            blocks = _anthropic_blocks(message.get("content"))
            if role in {"system", "developer"}:
                system_parts.extend(
                    block["text"] for block in blocks if block.get("type") == "text"
                )
                continue
            messages.append(
                {
                    "role": "assistant" if role == "assistant" else "user",
                    "content": blocks,
                }
            )
        payload: dict[str, Any] = {
            "model": model,
            "max_tokens": int(request.get("max_output_tokens") or 8192),
            "messages": messages,
        }
        if system_parts:
            payload["system"] = "\n\n".join(system_parts)
        body = json.dumps(payload).encode("utf-8")
        http_request = urllib.request.Request(
            endpoint,
            data=body,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "x-api-key": api_key,
                "anthropic-version": spec.anthropic_version,
            },
        )
        try:
            with self._urlopen(http_request, timeout=spec.timeout_seconds) as response:
                result = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise LlmRequestError(
                f"{spec.label} request failed with HTTP {exc.code}: {detail}"
            ) from exc
        except Exception as exc:
            raise LlmRequestError(f"{spec.label} request failed: {exc}") from exc
        content = result.get("content") if isinstance(result, dict) else None
        if not isinstance(content, list):
            raise LlmRequestError(f"{spec.label} response had no content list")
        output = "".join(
            str(block.get("text") or "")
            for block in content
            if isinstance(block, Mapping) and block.get("type") == "text"
        )
        metadata = {
            "response_id": result.get("id"),
            "response_model": result.get("model"),
            "stop_reason": result.get("stop_reason"),
            "stop_sequence": result.get("stop_sequence"),
            "usage": _metadata_value(result.get("usage")),
            "base_url": base_url,
        }
        return output, metadata


def _anthropic_blocks(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, str):
        return [{"type": "text", "text": value}]
    result: list[dict[str, Any]] = []
    for item in value or []:
        if not isinstance(item, Mapping):
            continue
        item_type = item.get("type")
        if item_type in {"input_text", "text"}:
            result.append({"type": "text", "text": str(item.get("text") or "")})
            continue
        if item_type in {"input_image", "image_url"}:
            image_value = item.get("image_url")
            if isinstance(image_value, Mapping):
                image_value = image_value.get("url")
            match = _DATA_URL_RE.match(str(image_value or ""))
            if not match:
                raise LlmRequestError(
                    "Claude adapter currently requires base64 data-URL images"
                )
            media_type, encoded = match.groups()
            base64.b64decode(encoded, validate=True)
            result.append(
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": media_type,
                        "data": encoded,
                    },
                }
            )
    return result


def _extract_openai_output_text(response: Any) -> str:
    output = getattr(response, "output", None)
    if output is None and isinstance(response, Mapping):
        output = response.get("output")
    texts: list[str] = []
    for item in output or []:
        content = getattr(item, "content", None)
        if content is None and isinstance(item, Mapping):
            content = item.get("content")
        for block in content or []:
            block_type = getattr(block, "type", None)
            text = getattr(block, "text", None)
            if isinstance(block, Mapping):
                block_type = block.get("type", block_type)
                text = block.get("text", text)
            if block_type in {"output_text", "text"} and text:
                texts.append(str(text))
    return "".join(texts)
