from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from operation_library import DEFAULT_WORKSPACES_ROOT
from workspace_inheritance import effective_workspace_layers, layer_source
from resource_store import get_filesystem_provider

SHARED_WORKSPACE_ID = "shared"
MODEL_CATALOG_DIRECTORY = "models"
BACKEND_DIRECTORIES = ("design/backends", "backends", "models")


def read_backend_file(path: Path) -> dict[str, Any]:
    try:
        value = get_filesystem_provider().read_json_documents(path)[0]
    except (OSError, json.JSONDecodeError, ValueError) as error:
        raise ValueError(f"Invalid backend definition {path}: {error}") from error
    return _validate_backend(value, path)


def _validate_backend(value: Any, path: Path) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"Backend definition must be a JSON object: {path}")
    if value.get("kind") != "backend":
        raise ValueError(f"Backend definition must declare kind='backend': {path}")
    if not str(value.get("id") or "").strip():
        raise ValueError(f"Backend definition requires id: {path}")
    if not str(value.get("provider") or "").strip():
        raise ValueError(f"Backend definition requires provider: {path}")
    return value


def _backend_records(workspace_root: Path, source: str, workspace_id: str) -> list[dict[str, Any]]:
    """Read kind=backend files from kind-specific or legacy catalogs."""
    records: list[dict[str, Any]] = []
    resources = get_filesystem_provider()
    paths = resources.glob(workspace_root, BACKEND_DIRECTORIES)
    for path in sorted(paths, key=lambda item: item.name.lower()):
        try:
            documents = resources.read_json_documents(path)
        except (OSError, json.JSONDecodeError, ValueError):
            continue
        for resource_index, raw in enumerate(documents):
            if not isinstance(raw, dict) or raw.get("kind") != "backend":
                continue
            record: dict[str, Any] = {"path": path.relative_to(workspace_root).as_posix(), "source": source, "workspaceId": workspace_id, "resourceIndex": resource_index}
            try:
                record["document"] = _validate_backend(raw, path)
            except ValueError as error:
                record["error"] = str(error)
            records.append(record)
    return records


def load_shared_backend_records(workspaces_root: Path = DEFAULT_WORKSPACES_ROOT) -> list[dict[str, Any]]:
    return _backend_records(workspaces_root / SHARED_WORKSPACE_ID, "shared", SHARED_WORKSPACE_ID)


def load_workspace_local_backend_records(workspace_root: Path) -> list[dict[str, Any]]:
    workspace_id = workspace_root.name
    if workspace_id == SHARED_WORKSPACE_ID:
        return []
    return _backend_records(workspace_root, "workspace", workspace_id)


def load_workspace_backend_records(
    workspace_root: Path,
    *,
    workspaces_root: Path = DEFAULT_WORKSPACES_ROOT,
) -> list[dict[str, Any]]:
    combined: dict[str, dict[str, Any]] = {}
    for layer in effective_workspace_layers(workspace_root, workspaces_root):
        for record in _backend_records(layer, layer_source(layer, workspace_root), layer.name):
            document = record.get("document") or {}
            combined[str(document.get("id") or record["path"])] = record
    return sorted(
        combined.values(),
        key=lambda item: str((item.get("document") or {}).get("label") or item["path"]).lower(),
    )


def load_backend_library_records(
    workspace_root: Path,
    *,
    workspaces_root: Path = DEFAULT_WORKSPACES_ROOT,
) -> dict[str, list[dict[str, Any]]]:
    return {
        "shared": load_shared_backend_records(workspaces_root),
        "workspace": load_workspace_local_backend_records(workspace_root),
        "effective": load_workspace_backend_records(workspace_root, workspaces_root=workspaces_root),
    }


def load_effective_backend_documents(workspace_root: Path) -> list[dict[str, Any]]:
    return [record["document"] for record in load_workspace_backend_records(workspace_root) if "document" in record]
