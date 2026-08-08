from __future__ import annotations

import json
import os
import re
import urllib.request
from pathlib import Path
from typing import Any, Callable


def _headers(backend: dict[str, Any]) -> dict[str, str]:
    configuration = backend.get("configuration") or {}
    headers = {"Accept": "application/json", "User-Agent": "MeTTaSymbolicLearnerWorkbench/0.6"}
    environment_name = str(configuration.get("apiKeyEnvironmentVariable") or configuration.get("apiKeyEnvironment") or "")
    api_key = os.environ.get(environment_name, "") if environment_name else ""
    if api_key:
        if configuration.get("adapter") == "anthropic_messages":
            headers.update({"x-api-key": api_key, "anthropic-version": "2023-06-01"})
        else:
            headers["Authorization"] = f"Bearer {api_key}"
    return headers


def _capabilities(row: dict[str, Any], backend: dict[str, Any], model_id: str) -> dict[str, bool]:
    architecture = row.get("architecture") if isinstance(row.get("architecture"), dict) else {}
    inputs = {str(value).lower() for value in architecture.get("input_modalities") or row.get("input_modalities") or []}
    outputs = {str(value).lower() for value in architecture.get("output_modalities") or row.get("output_modalities") or []}
    parameters = {str(value).lower() for value in row.get("supported_parameters") or []}
    name = model_id.lower()
    base_url = str((backend.get("configuration") or {}).get("baseUrl") or "")
    vision = "image" in inputs or "vision" in name
    audio = "audio" in inputs | outputs or any(token in name for token in ("audio", "realtime", "transcribe", "tts", "whisper"))
    tools = bool(parameters & {"tools", "tool_choice"})
    json_mode = bool(parameters & {"response_format", "structured_outputs"})
    return {
        "audio": audio,
        "code": any(token in name for token in ("code", "coder", "codex")),
        "functionCalling": tools,
        "json": json_mode,
        "jsonMode": json_mode,
        "local": base_url.startswith(("http://127.0.0.1", "http://localhost")),
        "multimodal": len(inputs | outputs) > 1 or vision or audio,
        "reasoning": bool(parameters & {"reasoning", "include_reasoning"}) or any(token in name for token in ("reason", "thinking", "deep-research", "o1", "o3", "o4")),
        "text": not inputs or "text" in inputs,
        "tools": tools,
        "vision": vision,
    }


def discover_backend_models(backend: dict[str, Any], *, timeout_seconds: float = 20,
                            opener: Callable[..., Any] = urllib.request.urlopen) -> list[dict[str, Any]]:
    configuration = backend.get("configuration") or {}
    base_url = str(configuration.get("baseUrl") or "").rstrip("/")
    if not base_url:
        raise ValueError("backend has no configuration.baseUrl")
    request = urllib.request.Request(f"{base_url}/models", headers=_headers(backend), method="GET")
    with opener(request, timeout=timeout_seconds) as response:
        payload = json.loads(response.read().decode("utf-8"))
    rows = payload.get("data") if isinstance(payload, dict) else payload
    if not isinstance(rows, list) and isinstance(payload, dict):
        rows = payload.get("models")
    if not isinstance(rows, list):
        raise ValueError("backend /models response has no data or models list")
    discovered: dict[str, dict[str, Any]] = {}
    for row in rows:
        if isinstance(row, str):
            model_id, label, metadata = row, row, {"id": row}
        elif isinstance(row, dict):
            model_id = str(row.get("id") or row.get("name") or row.get("model") or "")
            label = str(row.get("display_name") or row.get("displayName") or row.get("name") or model_id)
            metadata = row
        else:
            continue
        if model_id:
            top_provider = metadata.get("top_provider") if isinstance(metadata.get("top_provider"), dict) else {}
            discovered[model_id] = {
                "id": model_id, "label": label,
                "capabilities": _capabilities(metadata, backend, model_id),
                "limits": {"contextWindow": metadata.get("context_length"), "maxOutputTokens": top_provider.get("max_completion_tokens")},
                "pricing": metadata.get("pricing") if isinstance(metadata.get("pricing"), dict) else {},
                "properties": {**metadata, "ownedBy": metadata.get("owned_by") or metadata.get("ownedBy")},
                "providerMetadata": metadata,
            }
    return sorted(discovered.values(), key=lambda row: row["id"].lower())


def import_discovered_models(root: Path, backend: dict[str, Any], models: list[dict[str, Any]]) -> list[dict[str, Any]]:
    directory = root / "models"
    directory.mkdir(parents=True, exist_ok=True)
    imported: list[dict[str, Any]] = []
    for row in models:
        remote_id = str(row.get("id") or "").strip()
        if not remote_id:
            continue
        resource_id = re.sub(r"[^a-zA-Z0-9._-]+", "_", f"{backend['id']}-{remote_id}").strip("._").lower()
        document = {"kind": "model", "id": resource_id, "label": str(row.get("label") or remote_id),
                    "description": f"Discovered from {backend.get('label') or backend['id']}.",
                    "inherits": backend["id"], "model": remote_id, "enabled": True,
                    "capabilities": row.get("capabilities") or {}, "limits": row.get("limits") or {},
                    "pricing": row.get("pricing") or {}, "properties": row.get("properties") or {},
                    "providerMetadata": row.get("providerMetadata") or {}}
        target = directory / f"{resource_id}.model.json"
        temporary = target.with_suffix(target.suffix + ".tmp")
        temporary.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
        temporary.replace(target)
        imported.append(document)
    return imported
