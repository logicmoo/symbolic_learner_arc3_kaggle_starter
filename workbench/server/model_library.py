from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from threading import RLock
import time
from typing import Any

from backend_library import BACKEND_DIRECTORIES, MODEL_CATALOG_DIRECTORY, load_workspace_backend_records
from operation_library import DEFAULT_WORKSPACES_ROOT
from workspace_inheritance import effective_workspace_layers, layer_source
from resource_store import get_filesystem_provider

SHARED_WORKSPACE_ID = "shared"
MODEL_KINDS = {"model", "profile"}
MODEL_DIRECTORIES = ("design/models", "design/profiles", "models", "profiles")
_resolved_cache_lock = RLock()
_resolved_cache: dict[tuple[str, str], tuple[int, float, tuple[tuple[str, int, int], ...], list[dict[str, Any]]]] = {}
MODEL_REVISION_CHECK_SECONDS = 1.0


def _catalog_revision(workspace_root: Path, workspaces_root: Path) -> tuple[tuple[str, int, int], ...]:
    resources = get_filesystem_provider()
    entries: list[tuple[str, int, int]] = []
    for layer in effective_workspace_layers(workspace_root, workspaces_root):
        for path in resources.glob(layer, (*BACKEND_DIRECTORIES, *MODEL_DIRECTORIES)):
            try:
                metadata = resources.stat(path)
            except OSError:
                continue
            entries.append((str(path), metadata.st_mtime_ns, metadata.st_size))
    return tuple(sorted(set(entries)))


def read_model_file(path: Path) -> dict[str, Any]:
    try:
        value = get_filesystem_provider().read_json_documents(path)[0]
    except (OSError, json.JSONDecodeError, ValueError) as error:
        raise ValueError(f"Invalid model/profile definition {path}: {error}") from error
    return _validate_model(value, path)


def _validate_model(value: Any, path: Path) -> dict[str, Any]:
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
        raise ValueError(f"Prompt lists belong on operations, not model/profile definitions: {path}")
    return value


def _model_records(workspace_root: Path, source: str, workspace_id: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    resources = get_filesystem_provider()
    paths = resources.glob(workspace_root, MODEL_DIRECTORIES)
    for path in sorted(paths, key=lambda item: item.name.lower()):
        try:
            documents = resources.read_json_documents(path)
        except (OSError, json.JSONDecodeError, ValueError):
            continue
        for resource_index, raw in enumerate(documents):
            if not isinstance(raw, dict) or raw.get("kind") not in MODEL_KINDS:
                continue
            record: dict[str, Any] = {"path": path.relative_to(workspace_root).as_posix(), "source": source, "workspaceId": workspace_id, "resourceIndex": resource_index}
            try:
                record["document"] = _validate_model(raw, path)
            except ValueError as error:
                record["error"] = str(error)
                record["raw"] = raw
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
    return sorted(
        records,
        key=lambda item: str(
            (item.get("document") or item.get("raw") or {}).get("label")
            or item.get("path")
            or ""
        ).lower(),
    )


def _record_key(record: dict[str, Any]) -> str:
    document = record.get("document") or record.get("raw") or {}
    return str(document.get("id") or record.get("path") or "")


def load_workspace_model_records(
    workspace_root: Path,
    *,
    workspaces_root: Path = DEFAULT_WORKSPACES_ROOT,
) -> list[dict[str, Any]]:
    combined: dict[str, dict[str, Any]] = {}
    for layer in effective_workspace_layers(workspace_root, workspaces_root):
        for record in _model_records(layer, layer_source(layer, workspace_root), layer.name):
            combined[_record_key(record)] = record
    return _sort_records(list(combined.values()))


def resolve_model_records(
    workspace_root: Path,
    model_records: list[dict[str, Any]] | None = None,
    *,
    workspaces_root: Path = DEFAULT_WORKSPACES_ROOT,
) -> list[dict[str, Any]]:
    """Resolve model/profile inheritance chains until they terminate at a backend.

    Backends, models, and profiles share one catalog. A model can inherit a
    backend or model. A profile normally inherits a model/profile and changes
    only generation/runtime defaults. Prompt composition is deliberately not
    part of this graph; prompt lists belong to operation definitions.

    Invalid catalog files are returned with an error and disabled resolution;
    they never abort workspace discovery.
    """
    cache_key = (str(workspace_root.resolve()), str(workspaces_root.resolve()))
    revision: tuple[tuple[str, int, int], ...] | None = None
    if model_records is None:
        provider_revision = get_filesystem_provider().revision()
        with _resolved_cache_lock:
            cached = _resolved_cache.get(cache_key)
            if cached and cached[0] == provider_revision and time.monotonic() - cached[1] < MODEL_REVISION_CHECK_SECONDS:
                return deepcopy(cached[3])
        revision = _catalog_revision(workspace_root, workspaces_root)
        with _resolved_cache_lock:
            cached = _resolved_cache.get(cache_key)
            if cached and cached[2] == revision:
                _resolved_cache[cache_key] = (provider_revision, time.monotonic(), cached[2], cached[3])
                return deepcopy(cached[3])
    records = model_records or load_workspace_model_records(workspace_root, workspaces_root=workspaces_root)
    backend_records = load_workspace_backend_records(
        workspace_root, workspaces_root=workspaces_root
    )
    backends = {
        str((record.get("document") or {}).get("id")): record
        for record in backend_records
        if (record.get("document") or {}).get("id")
    }
    nodes = {
        str((record.get("document") or {}).get("id")): record
        for record in records
        if (record.get("document") or {}).get("id")
    }

    def resolve(node_id: str, trail: tuple[str, ...] = ()) -> dict[str, Any]:
        if not node_id or node_id not in nodes:
            raise ValueError(f"Model/profile has no resolvable id: {node_id!r}")
        if node_id in trail:
            raise ValueError(
                f"Model/profile inheritance cycle: {' -> '.join((*trail, node_id))}"
            )
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
                "enabled": backend.get("enabled", True) is not False
                and node.get("enabled", True) is not False,
            }

        parent_record = nodes.get(parent_id)
        if parent_record:
            parent = resolve(parent_id, (*trail, node_id))
            parent_kind = str(
                (parent_record.get("document") or {}).get("kind") or "model"
            )
            return {
                **parent,
                "parentId": parent_id,
                "parentKind": parent_kind,
                "inheritance": [*parent.get("inheritance", []), node_id],
                "model": own_model or parent.get("model"),
                "defaults": {**dict(parent.get("defaults") or {}), **own_defaults},
                "enabled": bool(parent.get("enabled", False))
                and node.get("enabled", True) is not False,
            }

        raise ValueError(
            f"Model/profile {node_id} inherits unavailable item: {parent_id}"
        )

    resolved: list[dict[str, Any]] = []
    for source_record in records:
        record = dict(source_record)
        node = record.get("document") or {}
        node_id = str(node.get("id") or "")
        if not node_id:
            raw = record.get("raw") or {}
            raw_id = str(raw.get("id") or "")
            record["resolved"] = {
                "enabled": False,
                "inheritance": [raw_id] if raw_id else [],
            }
            if not record.get("error"):
                record["error"] = "Model/profile definition has no valid id"
            resolved.append(record)
            continue
        try:
            record["resolved"] = resolve(node_id)
        except (KeyError, ValueError) as error:
            record["resolved"] = {"enabled": False, "inheritance": [node_id]}
            if not record.get("error"):
                record["error"] = str(error)
        resolved.append(record)
    result = _sort_records(resolved)
    if revision is not None:
        with _resolved_cache_lock:
            _resolved_cache[cache_key] = (get_filesystem_provider().revision(), time.monotonic(), revision, deepcopy(result))
    return result


def load_model_library_records(
    workspace_root: Path,
    *,
    workspaces_root: Path = DEFAULT_WORKSPACES_ROOT,
) -> dict[str, list[dict[str, Any]]]:
    shared = load_shared_model_records(workspaces_root)
    local = load_workspace_local_model_records(workspace_root)
    effective = load_workspace_model_records(
        workspace_root, workspaces_root=workspaces_root
    )
    return {
        "shared": shared,
        "workspace": local,
        "effective": resolve_model_records(
            workspace_root, effective, workspaces_root=workspaces_root
        ),
    }


def load_effective_model_documents(workspace_root: Path) -> list[dict[str, Any]]:
    return [
        record["document"]
        for record in load_workspace_model_records(workspace_root)
        if "document" in record
    ]
