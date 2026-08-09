from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path
from threading import RLock
from typing import Any
from urllib.parse import urlparse

from resource_store import get_filesystem_provider


_NAME = re.compile(r"^[A-Z][A-Z0-9_]{1,127}$")
_LOCK = RLock()
_RELATIVE_PATH = "runtime/.credentials"


def _validate_name(name: str) -> str:
    value = str(name or "").strip()
    if not _NAME.fullmatch(value):
        raise ValueError("credential name must be an uppercase environment-variable name")
    return value


def _path(workspace_root: Path) -> Path:
    return get_filesystem_provider().resolve(Path(workspace_root), _RELATIVE_PATH)


def read_workspace_credentials(workspace_root: Path) -> dict[str, str]:
    resources = get_filesystem_provider()
    path = _path(workspace_root)
    if not resources.is_file(path):
        return {}
    try:
        payload = json.loads(resources.read_text(path))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError("workspace credential store is invalid") from error
    if not isinstance(payload, dict):
        raise ValueError("workspace credential store must contain an object")
    return {str(name): str(value) for name, value in payload.items() if isinstance(value, str) and value}


def write_workspace_credential(workspace_root: Path, name: str, value: str | None) -> None:
    name = _validate_name(name)
    with _LOCK:
        values = read_workspace_credentials(workspace_root)
        if value:
            values[name] = str(value)
        else:
            values.pop(name, None)
        resources = get_filesystem_provider()
        path = _path(workspace_root)
        if values:
            resources.write_text(path, json.dumps(values, indent=2, sort_keys=True) + "\n")
        else:
            resources.delete(path)


def resolve_workspace_credential(workspace_root: Path | str | None, name: str) -> str:
    name = _validate_name(name)
    if workspace_root:
        value = read_workspace_credentials(Path(workspace_root)).get(name, "")
        if value:
            return value
    return os.environ.get(name, "")


def credential_statuses(workspace_root: Path, backends: list[dict[str, Any]]) -> list[dict[str, Any]]:
    local = read_workspace_credentials(workspace_root)
    entries: dict[str, dict[str, Any]] = {}
    for record in backends:
        backend = record.get("document") if isinstance(record.get("document"), dict) else record
        configuration = backend.get("configuration") or {}
        name = str(configuration.get("apiKeyEnvironmentVariable") or configuration.get("apiKeyEnvironment") or "")
        if not name:
            continue
        _validate_name(name)
        entry = entries.setdefault(name, {"environmentVariable": name, "backendIds": [], "backendLabels": []})
        entry["backendIds"].append(str(backend.get("id") or ""))
        entry["backendLabels"].append(str(backend.get("label") or backend.get("id") or name))
        bootstrap = configuration.get("credentialBootstrap")
        if isinstance(bootstrap, dict):
            entry["bootstrap"] = {
                "backendId": str(backend.get("id") or ""),
                "label": str(bootstrap.get("label") or f"Set up {backend.get('label') or backend.get('id')} automatically"),
            }
    for name, entry in entries.items():
        source = "workspace" if local.get(name) else "environment" if os.environ.get(name) else "missing"
        entry.update({"configured": source != "missing", "source": source})
    return sorted(entries.values(), key=lambda item: item["environmentVariable"])


def bootstrap_backend_credential(workspace_root: Path, backend: dict[str, Any]) -> str:
    configuration = backend.get("configuration") or {}
    name = _validate_name(
        str(configuration.get("apiKeyEnvironmentVariable") or configuration.get("apiKeyEnvironment") or "")
    )
    bootstrap = configuration.get("credentialBootstrap")
    if not isinstance(bootstrap, dict):
        raise ValueError("backend does not declare automatic credential setup")
    url = str(bootstrap.get("url") or "")
    parsed = urlparse(url)
    if parsed.scheme != "http" or parsed.hostname not in {"localhost", "127.0.0.1", "::1"}:
        raise ValueError("automatic credential setup is restricted to a local HTTP service")
    body = bootstrap.get("request") if isinstance(bootstrap.get("request"), dict) else {}
    request = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method=str(bootstrap.get("method") or "POST").upper(),
    )
    try:
        with urllib.request.urlopen(request, timeout=float(bootstrap.get("timeoutSeconds") or 10)) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")[:500]
        raise ValueError(f"{backend.get('label') or backend.get('id')} rejected automatic key setup (HTTP {error.code}): {detail}") from error
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        raise ValueError(f"cannot reach {backend.get('label') or backend.get('id')} at {url}: {error}") from error
    field = str(bootstrap.get("responseField") or "key")
    value = payload.get(field) if isinstance(payload, dict) else None
    if not isinstance(value, str) or not value:
        raise ValueError(f"automatic credential setup returned no {field}")
    write_workspace_credential(workspace_root, name, value)
    return name
