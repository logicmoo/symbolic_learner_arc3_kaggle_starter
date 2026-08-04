from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any, Mapping

from llm_providers import (
    LlmConfigurationError,
    LlmProviderRouter,
    LlmRequestError,
    ProviderSpec,
    _ResponsesFacade,
    _anthropic_blocks,
    _extract_openai_output_text,
    _metadata_value,
)


def _install_request_parameter_injection() -> None:
    current = _ResponsesFacade.create
    if getattr(current, "_arc3_catalog_sampling", False):
        return
    original = current

    def create(self: _ResponsesFacade, **kwargs: Any) -> Any:
        for env_name, request_name, cast in (
            ("ARC3_LLM_TEMPERATURE", "temperature", float),
            ("ARC3_LLM_TOP_P", "top_p", float),
            ("ARC3_LLM_SEED", "seed", int),
        ):
            value = os.environ.get(env_name, "").strip()
            if value and request_name not in kwargs:
                kwargs[request_name] = cast(value)
        return original(self, **kwargs)

    create._arc3_catalog_sampling = True  # type: ignore[attr-defined]
    _ResponsesFacade.create = create


def _install_openai_profile_sampling() -> None:
    current = LlmProviderRouter._openai_response
    if getattr(current, "_arc3_catalog_sampling", False):
        return

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
                f"Provider {spec.provider_id} requires "
                f"{spec.api_key_env or 'an API key'}"
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
                client = factory(
                    api_key=api_key or "local-no-key",
                    base_url=base_url,
                )
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

    openai_response._arc3_catalog_sampling = True  # type: ignore[attr-defined]
    LlmProviderRouter._openai_response = openai_response


def _install_anthropic_profile_sampling() -> None:
    current = LlmProviderRouter._anthropic_response
    if getattr(current, "_arc3_catalog_sampling", False):
        return

    def anthropic_response(
        self: LlmProviderRouter,
        spec: ProviderSpec,
        *,
        model: str,
        request: Mapping[str, Any],
    ) -> tuple[str, dict[str, Any]]:
        api_key = spec.resolved_api_key()
        if not api_key:
            raise LlmConfigurationError(
                f"Provider {spec.provider_id} requires "
                f"{spec.api_key_env or 'ANTHROPIC_API_KEY'}"
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
            "temperature": request.get("temperature"),
            "top_p": request.get("top_p"),
        }
        if system_parts:
            payload["system"] = "\n\n".join(system_parts)
        payload = {key: value for key, value in payload.items() if value is not None}
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
        timeout = float(
            os.environ.get("ARC3_LLM_TIMEOUT_SECONDS", "").strip()
            or spec.timeout_seconds
        )
        try:
            with self._urlopen(http_request, timeout=timeout) as response:
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
            "timeout_seconds": timeout,
            "temperature": payload.get("temperature"),
            "top_p": payload.get("top_p"),
        }
        return output, metadata

    anthropic_response._arc3_catalog_sampling = True  # type: ignore[attr-defined]
    LlmProviderRouter._anthropic_response = anthropic_response


def install_profile_sampling() -> None:
    _install_request_parameter_injection()
    _install_openai_profile_sampling()
    _install_anthropic_profile_sampling()
