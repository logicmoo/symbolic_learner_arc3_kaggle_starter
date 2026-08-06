from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from backend_library import MODEL_CATALOG_DIRECTORY, load_workspace_backend_records
from task_library import DEFAULT_WORKSPACES_ROOT

SHARED_WORKSPACE_ID = "shared"
MODEL_KINDS = {"model", "profile"}


def read_model_file(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Invalid model/profile definition {path}: {error}") from error
    if not isinstance(value, dict):
        raise ValueError(f"Model/profile definition must be a JSON object: {path}")
    if value.get("kind") not in MODEL_KINDS:
        raise ValueError(f"Model/profile definition must declare kind='model' or kind='profile': {path}")
    if not str(value.get("id") or "").strip():
        raise ValueError(f"Model/profile definition requires id: {path}")
    if not str(value.get("inherits") or "").strip():
        raise ValueError(f"Model/profile definition requires inherits: {path}")
    defaults = value.get("defaults")
    if defaults is not None and not isinstance(defaults, dict):
        raise ValueError(f"Model/profile defaults must be a JSON object: {path}")
    if "prompt_text" in value or "prompts" in value:
        raise ValueError(
            f"Prompt lists belong on tasks, not model/profile definitions: {path}"
        )
    return value


def _model_records(workspace_root: Path, source: str, workspace_id: str) -> list[dict[str, Any]]:
    directory = workspace_root / MODEL_CATALOG_DIRECTORY
    if not directory.is_dir():
        return []
    records: list[dict[str, Any]] = []
    for path in sorted(directory.glob("*.json"), key=lambda item: item.name.lower()):
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(raw, dict) or raw.get("kind") not in MODEL_KINDS:
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
    """Resolve model/profile inheritance chains until they terminate at a backend.

    Backends, models, and profiles share one catalog. A model can inherit a
    backend or model. A profile normally inherits a model/profile and changes
    only generation/runtime defaults. Prompt composition is deliberately not
    part of this graph; prompt lists belong to task definitions.
    """
    records = model_records or load_workspace_model_records(workspace_root, workspaces_root=workspaces_root)
    backend_records = load_workspace_backend_records(workspace_root, workspaces_root=workspaces_root)
    backends = {str((record.get("document") or {}).get("id")): record for record in backend_records if (record.get("document") or {}).get("id")}
    nodes = {str((record.get("document") or {}).get("id")): record for record in records if (record.get("document") or {}).get("id")}

    def resolve(node_id: str, trail: tuple[str, ...] = ()) -> dict[str, Any]:
        if node_id in trail:
            raise ValueError(f"Model/profile inheritance cycle: {' -> '.join((*trail, node_id))}")
        record = nodes[node_id]
        node = record.get("document") or {}
        parent_id = str(node.get("inherits") or "")
        own_defaults = dict(node.get("defaults") or {})
        own_model = node.get("model")

        backend_record = backends.get(parent_id)
        if backend_record:
            backend = backend_record.get("document") or {}
            configuration = dict(backend.get("configuration") or {})
            inherited_defaults = dict(backend.get("modelDefaults") or {})
            return {
                "parentId": parent_id,
                "parentKind": "backend",
                "backendId": parent_id,
                "backendSource": backend_record.get("source"),
                "backendPath": backend_record.get("path"),
                "backend": backend,
                "inheritance": [parent_id, node_id],
                "configuration": configuration,
                "model": own_model or configuration.get("defaultModel"),
                "defaults": {**inherited_defaults, **own_defaults},
                "enabled": backend.get("enabled", True) is not False and node.get("enabled", True) is not False,
            }

        parent_record = nodes.get(parent_id)
        if parent_record:
            parent = resolve(parent_id, (*trail, node_id))
            parent_kind = str((parent_record.get("document") or {}).get("kind") or "model")
            return {
                **parent,
                "parentId": parent_id,
                "parentKind": parent_kind,
                "inheritance": [*parent.get("inheritance", []), node_id],
                "model": own_model or parent.get("model"),
                "defaults": {**dict(parent.get("defaults") or {}), **own_defaults},
                "enabled": bool(parent.get("enabled", False)) and node.get("enabled", True) is not False,
            }

        raise ValueError(f"Model/profile {node_id} inherits unavailable item: {parent_id}")

    resolved: list[dict[str, Any]] = []
    for source_record in records:
        record = dict(source_record)
        node = record.get("document") or {}
        node_id = str(node.get("id") or "")
        try:
            record["resolved"] = resolve(node_id)
        except ValueError as error:
            record["resolved"] = {"enabled": False, "inheritance": [node_id]}
            if not record.get("error"):
                record["error"] = str(error)
        resolved.append(record)
    return _sort_records(resolved)


def load_model_library_records(workspace_root: Path, *, workspaces_root: Path = DEFAULT_WORKSPACES_ROOT) -> dict[str, list[dict[str, Any]]]:
    shared = load_shared_model_records(workspaces_root)
    local = load_workspace_local_model_records(workspace_root)
    effective = load_workspace_model_records(workspace_root, workspaces_root=workspaces_root)
    return {"shared": shared, "workspace": local, "effective": resolve_model_records(workspace_root, effective, workspaces_root=workspaces_root)}


def load_effective_model_documents(workspace_root: Path) -> list[dict[str, Any]]:
    return [record["document"] for record in load_workspace_model_records(workspace_root) if "document" in record]
