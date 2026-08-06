from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from backend_library import MODEL_CATALOG_DIRECTORY, load_workspace_backend_records
from task_library import DEFAULT_WORKSPACES_ROOT

SHARED_WORKSPACE_ID = "shared"


def read_model_file(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Invalid model definition {path}: {error}") from error
    if not isinstance(value, dict):
        raise ValueError(f"Model definition must be a JSON object: {path}")
    if value.get("kind") != "model":
        raise ValueError(f"Model definition must declare kind='model': {path}")
    if not str(value.get("id") or "").strip():
        raise ValueError(f"Model definition requires id: {path}")
    if not str(value.get("backend") or "").strip():
        raise ValueError(f"Model definition requires backend: {path}")
    if not str(value.get("model") or "").strip():
        raise ValueError(f"Model definition requires model: {path}")
    defaults = value.get("defaults")
    if defaults is not None and not isinstance(defaults, dict):
        raise ValueError(f"Model defaults must be a JSON object: {path}")
    return value


def _model_records(workspace_root: Path, source: str, workspace_id: str) -> list[dict[str, Any]]:
    """Read kind=model files from the unified models/ catalog."""
    directory = workspace_root / MODEL_CATALOG_DIRECTORY
    if not directory.is_dir():
        return []
    records: list[dict[str, Any]] = []
    for path in sorted(directory.glob("*.json"), key=lambda item: item.name.lower()):
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(raw, dict) or raw.get("kind") != "model":
            continue
        record: dict[str, Any] = {
            "path": path.relative_to(workspace_root).as_posix(),
            "source": source,
            "workspaceId": workspace_id,
        }
        try:
            record["document"] = read_model_file(path)
        except ValueError as error:
            record["error"] = str(error)
        records.append(record)
    return records


def load_shared_model_records(workspaces_root: Path = DEFAULT_WORKSPACES_ROOT) -> list[dict[str, Any]]:
    return _model_records(workspaces_root / SHARED_WORKSPACE_ID, "shared", SHARED_WORKSPACE_ID)


def load_workspace_local_model_records(workspace_root: Path) -> list[dict[str, Any]]:
    workspace_id = workspace_root.name
    if workspace_id == SHARED_WORKSPACE_ID:
        return []
    return _model_records(workspace_root, "workspace", workspace_id)


def _sort_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(records, key=lambda item: str((item.get("document") or {}).get("label") or item["path"]).lower())


def load_workspace_model_records(workspace_root: Path, *, workspaces_root: Path = DEFAULT_WORKSPACES_ROOT) -> list[dict[str, Any]]:
    combined: dict[str, dict[str, Any]] = {}
    for record in load_shared_model_records(workspaces_root):
        document = record.get("document") or {}
        combined[str(document.get("id") or record["path"])] = record
    for record in load_workspace_local_model_records(workspace_root):
        document = record.get("document") or {}
        combined[str(document.get("id") or record["path"])] = record
    return _sort_records(list(combined.values()))


def resolve_model_records(workspace_root: Path, model_records: list[dict[str, Any]] | None = None, *, workspaces_root: Path = DEFAULT_WORKSPACES_ROOT) -> list[dict[str, Any]]:
    records = model_records or load_workspace_model_records(workspace_root, workspaces_root=workspaces_root)
    backend_records = load_workspace_backend_records(workspace_root, workspaces_root=workspaces_root)
    backends = {str((record.get("document") or {}).get("id")): record for record in backend_records if (record.get("document") or {}).get("id")}
    resolved: list[dict[str, Any]] = []
    for source_record in records:
        record = dict(source_record)
        model = record.get("document") or {}
        backend_id = str(model.get("backend") or "")
        backend_record = backends.get(backend_id)
        backend = (backend_record or {}).get("document") or {}
        inherited_configuration = dict(backend.get("configuration") or {})
        inherited_defaults = dict(backend.get("modelDefaults") or {})
        model_defaults = dict(model.get("defaults") or {})
        record["resolved"] = {
            "backendId": backend_id,
            "backendSource": (backend_record or {}).get("source"),
            "backendPath": (backend_record or {}).get("path"),
            "backend": backend if backend else None,
            "configuration": inherited_configuration,
            "defaults": {**inherited_defaults, **model_defaults},
            "enabled": bool(backend) and backend.get("enabled", True) is not False and model.get("enabled", True) is not False,
        }
        if not backend and not record.get("error"):
            record["error"] = f"Model references unavailable backend: {backend_id}"
        resolved.append(record)
    return _sort_records(resolved)


def load_model_library_records(workspace_root: Path, *, workspaces_root: Path = DEFAULT_WORKSPACES_ROOT) -> dict[str, list[dict[str, Any]]]:
    shared = load_shared_model_records(workspaces_root)
    local = load_workspace_local_model_records(workspace_root)
    effective = load_workspace_model_records(workspace_root, workspaces_root=workspaces_root)
    return {"shared": shared, "workspace": local, "effective": resolve_model_records(workspace_root, effective, workspaces_root=workspaces_root)}


def load_effective_model_documents(workspace_root: Path) -> list[dict[str, Any]]:
    return [record["document"] for record in load_workspace_model_records(workspace_root) if "document" in record]
