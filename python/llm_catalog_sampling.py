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
    _anthropic_blocks,
    _metadata_value,
)


def install_anthropic_profile_sampling() -> None:
    """Honor profile sampling and timeout fields for Anthropic messages."""
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
