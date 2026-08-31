from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from threading import RLock
import time
from typing import Any

from backend_library import BACKEND_DIRECTORIES, MODEL_CATALOG_DIRECTORY, backend_record_index, load_workspace_backend_records
from operation_library import DEFAULT_WORKSPACES_ROOT
from workspace_inheritance import effective_workspace_layers, layer_source
from resource_store import get_filesystem_provider
from resource_relationships import (
    relationship_ids,
    resolve_dependency_enablement,
    resolve_inherited_document,
)

SHARED_WORKSPACE_ID = "shared_library_system"
# ``profile`` and the old profile directories remain read-only compatibility
# inputs. Validation normalizes every loaded resource to ``kind=model``; the
# parent relationship determines whether the UI presents it as a model preset.
MODEL_KINDS = {"model", "profile"}
MODEL_DIRECTORIES = ("design/models", "design/profiles", "models", "profiles")
MODEL_OVERRIDE_PATH = "design/models/model_overridden_properties.json"
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
        raise ValueError(f"Invalid model/preset definition {path}: {error}") from error
    return _validate_model(value, path)


def _validate_model(value: Any, path: Path) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"Model/preset definition must be a JSON object: {path}")
    if value.get("kind") not in MODEL_KINDS:
        raise ValueError(f"Model/preset definition must declare kind='model' (legacy kind='profile' is accepted): {path}")
    if not str(value.get("id") or "").strip():
        raise ValueError(f"Model/preset definition requires id: {path}")
    implemented_ids = relationship_ids(value.get("implements"))
    if not implemented_ids:
        raise ValueError(f"Model definition requires implements: {path}")
    value["kind"] = "model"
    defaults = value.get("defaults")
    if defaults is not None and not isinstance(defaults, dict):
        raise ValueError(f"Model/preset defaults must be a JSON object: {path}")
    if "prompt_text" in value or "prompts" in value:
        raise ValueError(f"Prompt lists belong on operations, not model/preset definitions: {path}")
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


def _deep_merge(base: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in patch.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(dict(merged.get(key) or {}), value)
        else:
            merged[key] = value
    return merged


def _model_override_rows(
    workspace_root: Path,
    *,
    workspaces_root: Path = DEFAULT_WORKSPACES_ROOT,
) -> dict[str, dict[str, Any]]:
    resources = get_filesystem_provider()
    merged: dict[str, dict[str, Any]] = {}
    for layer in effective_workspace_layers(workspace_root, workspaces_root):
        target = layer / MODEL_OVERRIDE_PATH
        if not resources.is_file(target):
            continue
        try:
            document = resources.read_json(target)
        except (OSError, json.JSONDecodeError, ValueError):
            continue
        if not isinstance(document, dict):
            continue
        model_rows = document.get("models")
        if not isinstance(model_rows, dict):
            continue
        for model_id, patch in model_rows.items():
            if not str(model_id).strip() or not isinstance(patch, dict):
                continue
            merged[str(model_id)] = _deep_merge(merged.get(str(model_id), {}), patch)
    return merged


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
    """Resolve model and Model Preset inheritance chains to a backend.

    Backends, models, and presets share one catalog. A model inherits a backend;
    a Model Preset remains ``kind=model`` but inherits a model or another preset
    and changes only generation/runtime defaults. Prompt composition is not part
    of this graph; Prompt Profiles are separate resources.

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
    backends = backend_record_index(backend_records)
    nodes = {
        str((record.get("document") or {}).get("id")): record
        for record in records
        if (record.get("document") or {}).get("id")
    }

    documents_by_id = {
        str((record.get("document") or {}).get("id")): record["document"]
        for record in [*backend_records, *records]
        if (record.get("document") or {}).get("id")
    }
    for identifier, record in backends.items():
        if record.get("document"):
            documents_by_id.setdefault(identifier, record["document"])

    def ancestor_ids(node_id: str, trail: tuple[str, ...] = ()) -> list[str]:
        if node_id in trail:
            raise ValueError(f"Model/preset inheritance cycle: {' -> '.join((*trail, node_id))}")
        document = documents_by_id.get(node_id)
        if not document:
            raise ValueError(f"Model/preset inherits unavailable item: {node_id}")
        result: list[str] = []
        for implemented_id in relationship_ids(document.get("implements")):
            result.extend(ancestor_ids(implemented_id, (*trail, node_id)))
            result.append(implemented_id)
        return list(dict.fromkeys(result))

    def resolve(node_id: str) -> dict[str, Any]:
        if not node_id or node_id not in nodes:
            raise ValueError(f"Model/preset has no resolvable id: {node_id!r}")
        record = nodes[node_id]
        node = record.get("document") or {}
        implemented_ids = relationship_ids(node.get("implements"))
        if not implemented_ids:
            raise ValueError(f"Model/preset {node_id} has no implemented resource")
        inheritance_resolution = resolve_inherited_document(node, documents_by_id)
        blockers = [
            *inheritance_resolution["conflicts"],
            *inheritance_resolution["missingResources"],
            *inheritance_resolution["missingBacklinks"],
        ]
        if blockers:
            raise ValueError(f"Model/preset inheritance is unresolved for {node_id}: {'; '.join(blockers)}")
        effective = inheritance_resolution["document"]
        ancestors = ancestor_ids(node_id)
        backend_candidates: dict[str, dict[str, Any]] = {}
        for ancestor_id in ancestors:
            backend_record = backends.get(ancestor_id)
            if not backend_record:
                continue
            backend = backend_record.get("document") or {}
            canonical_id = str(backend.get("id") or ancestor_id)
            backend_candidates[canonical_id] = backend_record
        if len(backend_candidates) != 1:
            raise ValueError(
                f"Model/preset {node_id} must resolve exactly one backend; found {sorted(backend_candidates)}"
            )
        canonical_backend_id, backend_record = next(iter(backend_candidates.items()))
        backend = backend_record.get("document") or {}
        configuration = dict(effective.get("configuration") or {})
        defaults = {
            **dict(effective.get("modelDefaults") or {}),
            **dict(effective.get("defaults") or {}),
        }
        dependency_resolution = resolve_dependency_enablement(node, documents_by_id)
        parent_id = implemented_ids[0]
        parent_document = documents_by_id.get(parent_id) or {}
        normalized_ancestors = [
            str((backends[resource_id].get("document") or {}).get("id") or resource_id)
            if resource_id in backends else resource_id
            for resource_id in ancestors
        ]
        normalized_ancestors = list(dict.fromkeys(normalized_ancestors))
        return {
            "parentId": parent_id,
            "parentKind": str(parent_document.get("kind") or "model"),
            "backendId": canonical_backend_id,
            "backendSource": backend_record.get("source"),
            "backendPath": backend_record.get("path"),
            "backend": backend,
            "implementationPath": [*normalized_ancestors, node_id],
            "propertyInheritanceResolution": inheritance_resolution,
            "dependencyResolution": dependency_resolution,
            "dependencies": dependency_resolution["dependencies"],
            "blockingDependencies": dependency_resolution["blockingDependencies"],
            "configuration": configuration,
            "model": effective.get("model") or configuration.get("defaultModel"),
            "defaults": defaults,
            "enabled": dependency_resolution["enabled"],
        }

    resolved: list[dict[str, Any]] = []
    override_rows = _model_override_rows(workspace_root, workspaces_root=workspaces_root)
    for source_record in records:
        record = dict(source_record)
        node = record.get("document") or {}
        node_id = str(node.get("id") or "")
        if not node_id:
            raw = record.get("raw") or {}
            raw_id = str(raw.get("id") or "")
            record["resolved"] = {
                "enabled": False,
                "implementationPath": [raw_id] if raw_id else [],
            }
            if not record.get("error"):
                record["error"] = "Model/preset definition has no valid id"
            resolved.append(record)
            continue
        try:
            record["resolved"] = resolve(node_id)
        except (KeyError, ValueError) as error:
            record["resolved"] = {"enabled": False, "implementationPath": [node_id]}
            if not record.get("error"):
                record["error"] = str(error)
        override = override_rows.get(node_id)
        if override:
            document_patch = (
                override.get("document")
                if isinstance(override.get("document"), dict)
                else override
            )
            resolved_patch = (
                override.get("resolved")
                if isinstance(override.get("resolved"), dict)
                else {}
            )
            document = record.get("document")
            if isinstance(document, dict) and isinstance(document_patch, dict):
                record["document"] = _deep_merge(document, document_patch)
            resolved_state = record.get("resolved")
            if isinstance(resolved_state, dict):
                merged_resolved = dict(resolved_state)
                if isinstance(document_patch, dict):
                    if isinstance(document_patch.get("defaults"), dict):
                        merged_resolved["defaults"] = _deep_merge(
                            dict(merged_resolved.get("defaults") or {}),
                            dict(document_patch.get("defaults") or {}),
                        )
                    if "model" in document_patch and document_patch.get("model"):
                        merged_resolved["model"] = document_patch.get("model")
                    if "enabled" in document_patch:
                        merged_resolved["enabled"] = document_patch.get("enabled")
                if isinstance(resolved_patch, dict):
                    merged_resolved = _deep_merge(merged_resolved, resolved_patch)
                record["resolved"] = merged_resolved
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
