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


def discover_backend_models(backend: dict[str, Any], *, timeout_seconds: float = 20,
                            opener: Callable[..., Any] = urllib.request.urlopen) -> list[dict[str, str]]:
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
    discovered: dict[str, dict[str, str]] = {}
    for row in rows:
        if isinstance(row, str):
            model_id, label = row, row
        elif isinstance(row, dict):
            model_id = str(row.get("id") or row.get("name") or row.get("model") or "")
            label = str(row.get("display_name") or row.get("displayName") or row.get("name") or model_id)
        else:
            continue
        if model_id:
            discovered[model_id] = {"id": model_id, "label": label}
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
                    "inherits": backend["id"], "model": remote_id, "enabled": True}
        target = directory / f"{resource_id}.model.json"
        temporary = target.with_suffix(target.suffix + ".tmp")
        temporary.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
        temporary.replace(target)
        imported.append(document)
    return imported
