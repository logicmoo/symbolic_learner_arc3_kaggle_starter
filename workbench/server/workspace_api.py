from __future__ import annotations

import json
import os
import re
import shutil
import time
import base64
import binascii
from concurrent.futures import ThreadPoolExecutor
from collections import Counter
from threading import RLock
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Body, HTTPException, Query
from fastapi.responses import FileResponse

from artifact_category_library import apply_artifact_categories, load_workspace_artifact_categories
from backend_library import MODEL_CATALOG_DIRECTORY, backend_matches, load_backend_library_records, load_workspace_backend_records
from goal_plan_library import load_workspace_symbolic_records, symbolic_hierarchy
from datatype_library import (
    DATATYPE_DIRECTORY,
    REPRESENTATION_DIRECTORY,
    CONCRETE_DIRECTORY,
    load_workspace_concrete_datatype_records,
    load_workspace_datatype_records,
    load_workspace_representation_records,
)
from model_library import load_model_library_records, resolve_model_records
from prompt_library import load_prompt_library_records, load_workspace_prompt_records
from policy_library import load_workspace_policy_records, policy_hierarchy
from resource_convention import canonical_resource_path, infer_resource_kind
from resource_relationships import relationship_ids, synchronize_parent_backlinks
from operation_library import DEFAULT_WORKSPACES_ROOT, load_workspace_operation_implementation_records, load_workspace_operation_records
from workspace_inheritance import (
    SHARED_WORKSPACE_ID,
    declared_include_specs,
    effective_workspace_layers,
    layer_source,
    read_workspace_metadata,
    workspace_metadata_path,
)
from resource_store import get_filesystem_provider
from workspace_credentials import bootstrap_backend_credential, credential_statuses, write_workspace_credential

router = APIRouter(prefix="/workspaces", tags=["workspaces"])

TEXT_SUFFIXES = {".json", ".md", ".txt", ".py", ".pl", ".metta", ".yaml", ".yml", ".toml"}
# Suffixes that may be written verbatim through PUT /{workspace_id}/data-file. This
# superset of TEXT_SUFFIXES adds the setup-panel file-group extensions (.eng/.prompt)
# so the [edit]/[new] editors can round-trip their bytes without JSON/resource mangling.
DATA_FILE_SUFFIXES = TEXT_SUFFIXES | {".eng", ".prompt"}
IGNORED_DIRECTORIES = {".git", ".venv", "node_modules", "__pycache__"}
WORKSPACE_DISCOVERY_CACHE_SECONDS = 60.0
_workspace_cache_lock = RLock()
_workspace_cache: tuple[tuple[str, ...], float, list[dict[str, Any]]] | None = None


def _workspace_roots() -> list[Path]:
    raw = os.getenv("WORKBENCH_WORKSPACE_ROOTS", "")
    roots = [Path(part).expanduser().resolve() for part in raw.split(os.pathsep) if part.strip()]
    default = DEFAULT_WORKSPACES_ROOT.resolve()
    if default not in roots:
        roots.insert(0, default)
    return roots


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = get_filesystem_provider().read_json(path)
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Invalid JSON file {path}: {error}") from error
    if not isinstance(value, dict):
        raise ValueError(f"JSON file must contain an object: {path}")
    return value


def _optional_metadata(root: Path) -> dict[str, Any]:
    value = read_workspace_metadata(root)
    if value:
        value.setdefault("kind", "workspace")
    return value


def _humanize(name: str) -> str:
    return name.replace("-", " ").replace("_", " ").strip().title()


def _workspace_disk_summary(root: Path) -> tuple[int, int]:
    resources = get_filesystem_provider()
    files = [path for path in resources.rglob(root, "*") if resources.is_file(path)]
    total_bytes = 0
    for path in files:
        try:
            total_bytes += resources.stat(path).st_size
        except OSError:
            continue
    return len(files), total_bytes


def _local_resource_counts(root: Path) -> dict[str, int]:
    resources = get_filesystem_provider()
    counts: Counter[str] = Counter()
    kind_labels = {
        "workflow": "workflows", "operation": "operations", "operation_implementation": "implementations",
        "semantic_datatype": "datatypes", "representation_datatype": "representations",
        "concrete_datatype": "concreteDatatypes", "backend": "systems", "system": "systems",
        "model": "models", "prompt": "prompts", "prompt_implementation": "prompts",
        "prompt_profile": "prompts", "goal": "goals", "plan": "plans",
        "planning_strategy": "plans", "context": "atomspaces", "atomspace": "atomspaces",
    }
    paths = resources.rglob(root, "*.metta") + resources.rglob(root, "*.json")
    for path in sorted(set(paths)):
        try:
            documents = resources.read_json_documents(path)
        except (OSError, ValueError):
            continue
        for document in documents:
            if isinstance(document, dict):
                label = kind_labels.get(str(document.get("kind") or ""))
                if label:
                    counts[label] += 1
    return dict(counts)


def _resource_ids_for_layer(
    layer: Path,
    directories: tuple[str, ...],
    *,
    accepted_kinds: set[str],
    default_kind: str | None = None,
    require_parents: bool | None = None,
) -> set[str]:
    resources = get_filesystem_provider()
    ids: set[str] = set()
    for path in resources.glob(layer, directories):
        try:
            documents = resources.read_json_documents(path)
        except (OSError, ValueError, json.JSONDecodeError):
            continue
        for document in documents:
            if not isinstance(document, dict):
                continue
            normalized_kind = str(document.get("kind") or default_kind or "").replace("-", "_")
            if accepted_kinds and normalized_kind not in accepted_kinds:
                continue
            parent_ids = relationship_ids(document.get("parents"))
            if require_parents is True and not parent_ids:
                continue
            if require_parents is False and parent_ids:
                continue
            resource_id = str(document.get("id") or "").strip()
            if not resource_id:
                continue
            ids.add(resource_id)
    return ids


def _resource_count_breakdown(
    root: Path,
    directories: tuple[str, ...],
    *,
    accepted_kinds: set[str],
    default_kind: str | None = None,
    require_parents: bool | None = None,
) -> dict[str, int]:
    layers = effective_workspace_layers(root, root.parent)
    local_layer_index = next(
        (
            index
            for index, layer in enumerate(layers)
            if layer.resolve() == root.resolve()
        ),
        len(layers) - 1,
    )
    layer_resource_ids = [
        _resource_ids_for_layer(
            layer,
            directories,
            accepted_kinds=accepted_kinds,
            default_kind=default_kind,
            require_parents=require_parents,
        )
        for layer in layers
    ]
    winner_index_by_id: dict[str, int] = {}
    for layer_index, identifiers in enumerate(layer_resource_ids):
        for identifier in identifiers:
            winner_index_by_id[identifier] = layer_index
    local_ids = {
        identifier
        for identifier, winner_index in winner_index_by_id.items()
        if winner_index == local_layer_index
    }
    overridden_count = sum(
        1
        for identifier in local_ids
        if any(identifier in layer_resource_ids[index] for index in range(local_layer_index))
    )
    total = len(winner_index_by_id)
    local = len(local_ids)
    return {
        "total": total,
        "local": local,
        "inherited": total - local,
        "overridden": overridden_count,
    }


def _workspace_from_directory(root: Path, *, include_counts: bool = True) -> dict[str, Any]:
    resources = get_filesystem_provider()
    metadata = _optional_metadata(root)
    workflow_dir = root / "design" / "workflows"
    prompt_dir = root / "design" / "prompts"
    config_dir = root / "config"
    operation_dir = root / "design" / "operations"
    datatype_dir = root / DATATYPE_DIRECTORY
    representation_dir = root / REPRESENTATION_DIRECTORY
    concrete_dir = root / CONCRETE_DIRECTORY
    model_dir = root / "design" / MODEL_CATALOG_DIRECTORY
    goal_dir = root / "design" / "goals"
    plan_dir = root / "design" / "plans"
    context_dir = root / "design" / "atomspaces"
    backend_count = len(load_workspace_backend_records(root)) if include_counts else 0
    model_count = len(resolve_model_records(root)) if include_counts else 0
    prompt_count = len(load_workspace_prompt_records(root)) if include_counts else 0
    operation_count = len(load_workspace_operation_records(root)) if include_counts else 0
    operation_implementation_count = len(load_workspace_operation_implementation_records(root)) if include_counts else 0
    datatype_count = len(load_workspace_datatype_records(root)) if include_counts else 0
    representation_count = len(load_workspace_representation_records(root)) if include_counts else 0
    concrete_count = len(load_workspace_concrete_datatype_records(root)) if include_counts else 0
    goal_count = len(load_workspace_symbolic_records(root, "goal")) if include_counts else 0
    plan_count = len(load_workspace_symbolic_records(root, "plan")) if include_counts else 0
    context_count = len(load_workspace_symbolic_records(root, "context")) if include_counts else 0
    file_count, disk_usage_bytes = _workspace_disk_summary(root) if include_counts else (0, 0)
    local_resource_counts = _local_resource_counts(root) if include_counts else {}
    resource_count_breakdowns = (
        {
            "workflows": _resource_count_breakdown(
                root,
                ("design/workflows", "workflows"),
                accepted_kinds={"workflow"},
                default_kind="workflow",
            ),
            "operations": _resource_count_breakdown(
                root,
                (
                    "design/operations",
                    "design/operation_implementations",
                    "operations",
                    "operation_implementations",
                ),
                accepted_kinds={"operation", "operation_implementation"},
                default_kind="operation",
                require_parents=False,
            ),
            "datatypes": _resource_count_breakdown(
                root,
                (DATATYPE_DIRECTORY, "semantic_datatypes", "datatypes"),
                accepted_kinds={"semantic_datatype"},
                default_kind="semantic_datatype",
            ),
            "representations": _resource_count_breakdown(
                root,
                (REPRESENTATION_DIRECTORY, "representation_datatypes", "representations"),
                accepted_kinds={"representation_datatype"},
                default_kind="representation_datatype",
            ),
            "models": _resource_count_breakdown(
                root,
                ("design/models", "design/profiles", "models", "profiles"),
                accepted_kinds={"model", "profile"},
            ),
            "prompts": _resource_count_breakdown(
                root,
                (
                    "design/prompts",
                    "design/prompt_implementations",
                    "prompts",
                    "prompt_implementations",
                ),
                accepted_kinds={"prompt"},
                default_kind="prompt",
                require_parents=False,
            ),
        }
        if include_counts
        else {}
    )
    layers = effective_workspace_layers(root, root.parent)
    include_specs = declared_include_specs(root)
    return {
        "id": root.name,
        "label": str(metadata.get("label") or _humanize(root.name)),
        "description": str(metadata.get("description") or "Filesystem workspace"),
        "workspaceType": str(metadata.get("workspaceType") or ("library" if root.name == SHARED_WORKSPACE_ID else "project")),
        "hidden": metadata.get("hidden") is True,
        "root": str(root.resolve()),
        "manifest": None,
        "discovery": "directory-enumeration",
        "workflowDirectory": str(workflow_dir.resolve()),
        "workflowDirectoryRelative": "design/workflows",
        "promptDirectory": str(prompt_dir.resolve()),
        "promptDirectoryRelative": "design/prompts",
        "configDirectory": str(config_dir.resolve()),
        "configDirectoryRelative": "config",
        "operationDirectory": str(operation_dir.resolve()),
        "operationDirectoryRelative": "design/operations",
        "datatypeDirectory": str(datatype_dir.resolve()),
        "datatypeDirectoryRelative": DATATYPE_DIRECTORY,
        "representationDirectory": str(representation_dir.resolve()),
        "representationDirectoryRelative": REPRESENTATION_DIRECTORY,
        "concreteDatatypeDirectory": str(concrete_dir.resolve()),
        "concreteDatatypeDirectoryRelative": CONCRETE_DIRECTORY,
        "backendDirectory": str(model_dir.resolve()),
        "backendDirectoryRelative": "design/backends",
        "modelDirectory": str(model_dir.resolve()),
        "modelDirectoryRelative": "design/models",
        "goalDirectory": str(goal_dir.resolve()),
        "goalDirectoryRelative": "design/goals",
        "planDirectory": str(plan_dir.resolve()),
        "planDirectoryRelative": "design/plans",
        "metadata": metadata.get("metadata") or {},
        "includes": include_specs,
        "effectiveIncludes": [layer.name for layer in layers if layer.resolve() != root.resolve()],
        "countsAvailable": include_counts,
        "fileCount": file_count,
        "diskUsageBytes": disk_usage_bytes,
        "resourceCounts": local_resource_counts,
        "resourceCountScope": "local",
        "resourceCountBreakdowns": resource_count_breakdowns,
        "workflowFileCount": len(resources.glob(root, ("design/workflows",))) if include_counts and resources.is_dir(workflow_dir) else 0,
        "operationFileCount": operation_count,
        "operationImplementationFileCount": operation_implementation_count,
        "datatypeFileCount": datatype_count,
        "representationFileCount": representation_count,
        "concreteDatatypeFileCount": concrete_count,
        "backendFileCount": backend_count,
        "modelFileCount": model_count,
        "promptFileCount": prompt_count,
        "goalFileCount": goal_count,
        "planFileCount": plan_count,
        "contextFileCount": context_count,
        "catalogFileCount": len(resources.glob(root, ("design/models",))) if include_counts and resources.is_dir(model_dir) else 0,
    }


def invalidate_workspace_discovery() -> None:
    global _workspace_cache
    with _workspace_cache_lock:
        _workspace_cache = None


def discover_workspaces(*, force: bool = False, include_counts: bool = True) -> list[dict[str, Any]]:
    global _workspace_cache
    resources = get_filesystem_provider()
    roots = _workspace_roots()
    cache_key = (f"counts={include_counts}", *(str(root) for root in roots))
    with _workspace_cache_lock:
        if (
            not force
            and _workspace_cache
            and _workspace_cache[0] == cache_key
            and time.monotonic() - _workspace_cache[1] < WORKSPACE_DISCOVERY_CACHE_SECONDS
        ):
            return [dict(item) for item in _workspace_cache[2]]

    candidates: list[Path] = []
    for container in roots:
        if not resources.is_dir(container):
            continue
        try:
            children = resources.iterdir(container)
        except OSError:
            continue
        for child in children:
            if not resources.is_dir(child) or child.name.startswith(".") or child.name in IGNORED_DIRECTORIES:
                continue
            candidates.append(child)

    found: dict[str, dict[str, Any]] = {}

    def load_workspace(child: Path) -> dict[str, Any]:
        return _workspace_from_directory(child, include_counts=include_counts)

    if candidates:
        max_workers = min(8, len(candidates))
        with ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="workspace-discovery") as pool:
            for workspace in pool.map(load_workspace, candidates):
                found[workspace["root"]] = workspace

    discovered = sorted(found.values(), key=lambda item: (item["label"].lower(), item["root"].lower()))
    projects = [item for item in discovered if item.get("workspaceType") == "project"]
    project_ids = {item["id"] for item in projects}
    for item in discovered:
        used_by = sorted(project["id"] for project in projects if item["id"] in project.get("effectiveIncludes", []))
        consumed_projects = sorted(project_id for project_id in item.get("effectiveIncludes", []) if project_id in project_ids)
        item["usedByProjectCount"] = len(used_by)
        item["usedByProjects"] = used_by
        item["consumedProjectCount"] = len(consumed_projects)
        item["consumedProjects"] = consumed_projects

    with _workspace_cache_lock:
        _workspace_cache = (cache_key, time.monotonic(), discovered)
    return [dict(item) for item in discovered]


def _resolve_workspace(workspace_id: str) -> dict[str, Any]:
    with _workspace_cache_lock:
        if _workspace_cache and _workspace_cache[0][0] == "counts=True" and time.monotonic() - _workspace_cache[1] < WORKSPACE_DISCOVERY_CACHE_SECONDS:
            cached = next((item for item in _workspace_cache[2] if item["id"] == workspace_id or item["root"] == workspace_id), None)
            if cached:
                return dict(cached)
    if re.fullmatch(r"[A-Za-z0-9_.-]+", workspace_id):
        resources = get_filesystem_provider()
        for container in _workspace_roots():
            candidate = container / workspace_id
            if resources.is_dir(candidate):
                return _workspace_from_directory(candidate)
    for workspace in discover_workspaces():
        if workspace["id"] == workspace_id or workspace["root"] == workspace_id:
            return workspace
    raise KeyError("workspace not found")


def _resolve_workspace_without_counts(workspace_id: str) -> dict[str, Any]:
    """Resolve a workspace for direct file access without catalog enumeration.

    Reading one Markdown or source file must not parse every model, prompt,
    operation, datatype, and runtime record merely to recover the workspace
    root. Detailed discovery remains available to endpoints that display those
    counts.
    """
    if re.fullmatch(r"[A-Za-z0-9_.-]+", workspace_id):
        resources = get_filesystem_provider()
        for container in _workspace_roots():
            candidate = container / workspace_id
            if resources.is_dir(candidate):
                return _workspace_from_directory(candidate, include_counts=False)
    for workspace in discover_workspaces(include_counts=False):
        if workspace["id"] == workspace_id or workspace["root"] == workspace_id:
            return workspace
    raise KeyError("workspace not found")


def _normalize_include_specs(workspace: dict[str, Any], raw: Any) -> list[dict[str, Any]]:
    if workspace["id"] == SHARED_WORKSPACE_ID:
        return []
    if not isinstance(raw, list):
        raise ValueError("includes must be an ordered array")
    available = {item["id"]: Path(item["root"]) for item in discover_workspaces()}
    result: list[dict[str, Any]] = []
    for value in raw:
        if not isinstance(value, dict):
            raise ValueError("Each include must contain workspaceId and includeInherited")
        included_id = str(value.get("workspaceId") or "").strip()
        if not included_id or included_id == workspace["id"]:
            raise ValueError("A workspace cannot include itself")
        if included_id not in available:
            raise ValueError(f"Included workspace does not exist: {included_id}")
        if any(item["workspaceId"] == included_id for item in result):
            raise ValueError(f"Workspace is included more than once: {included_id}")
        result.append({"workspaceId": included_id, "includeInherited": value.get("includeInherited", True) is not False})

    proposed = {workspace["id"]: result}
    visiting: list[str] = []

    def validate(workspace_id: str, include_inherited: bool = True) -> None:
        if workspace_id in visiting:
            raise ValueError(f"Workspace inclusion cycle: {' -> '.join((*visiting, workspace_id))}")
        visiting.append(workspace_id)
        specs = proposed.get(workspace_id, declared_include_specs(available[workspace_id]))
        if include_inherited:
            for spec in specs:
                child_id = spec["workspaceId"]
                if child_id not in available:
                    raise ValueError(f"Included workspace does not exist: {child_id}")
                validate(child_id, spec["includeInherited"])
        visiting.pop()

    validate(workspace["id"])
    return result


def _safe_child(root: Path, relative: str) -> Path:
    resolved_root = root.resolve()
    resolved = (resolved_root / relative).resolve()
    if resolved != resolved_root and resolved_root not in resolved.parents:
        raise ValueError("path escapes workspace root")
    return resolved


def _file_record(root: Path, path: Path) -> dict[str, Any]:
    resources = get_filesystem_provider()
    stat = resources.stat(path)
    return {
        "path": path.relative_to(root).as_posix(),
        "name": path.name,
        "suffix": path.suffix.lower(),
        "size": stat.st_size,
        "modified": stat.st_mtime,
        "kind": "directory" if resources.is_dir(path) else "file",
    }


def _load_documents(root: Path, directory: Path, source: str, expected_kind: str | None = None) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    resources = get_filesystem_provider()
    if not resources.is_dir(directory):
        return result
    relative_directory = directory.relative_to(root).as_posix()
    for path in resources.glob(root, (relative_directory,)):
        try:
            documents = resources.read_json_documents(path)
        except ValueError as error:
            result.append({"path": path.relative_to(root).as_posix(), "source": source, "workspaceId": root.name, "error": str(error)})
            continue
        for resource_index, document in enumerate(documents):
            if not isinstance(document, dict):
                continue
            if expected_kind and document.get("kind") not in (None, expected_kind):
                continue
            record: dict[str, Any] = {"path": path.relative_to(root).as_posix(), "source": source, "workspaceId": root.name, "resourceIndex": resource_index}
            if expected_kind:
                document.setdefault("kind", expected_kind)
                record["convention"] = "canonical" if path.name.endswith(f".{expected_kind}.json") else "legacy-filename"
            record["document"] = document
            result.append(record)
    return result


def _load_workflows(workspace: dict[str, Any]) -> list[dict[str, Any]]:
    root = Path(workspace["root"])
    combined: dict[str, dict[str, Any]] = {}
    for layer in effective_workspace_layers(root, root.parent):
        directories = (layer / "design" / "workflows", layer / "workflows")
        for directory in directories:
            for record in _load_documents(layer, directory, layer_source(layer, root), "workflow"):
                document = record.get("document") or {}
                combined[str(document.get("id") or record["path"])] = record
    records = sorted(combined.values(), key=lambda record: str((record.get("document") or {}).get("label") or record["path"]).lower())
    return _with_artifact_categories(workspace, records, "workflows")


def _load_workflow_pages(workspace: dict[str, Any]) -> list[dict[str, Any]]:
    """Load effective, filesystem-backed workflow page definitions.

    Page definitions are deliberately separate from executable Workflows. They
    describe which rich workbench surface presents a Workflow and how its
    three accordion columns are named and populated.
    """
    root = Path(workspace["root"])
    combined: dict[str, dict[str, Any]] = {}
    for layer in effective_workspace_layers(root, root.parent):
        directory = layer / "design" / "workflow_pages"
        for record in _load_documents(layer, directory, layer_source(layer, root), "workflow_page"):
            document = record.get("document") or {}
            combined[str(document.get("id") or record["path"])] = record
    return sorted(
        combined.values(),
        key=lambda record: (
            {"first": 0, "middle": 1, "last": 2}.get(
                str((record.get("document") or {}).get("menuPlacement") or "middle").lower(),
                1,
            ),
            int((record.get("document") or {}).get("order") or 1000),
            str((record.get("document") or {}).get("label") or record["path"]).lower(),
        ),
    )


def _effective_text_documents(workspace: dict[str, Any]) -> list[dict[str, Any]]:
    """List editable text documents across the effective workspace layers."""
    root = Path(workspace["root"])
    combined: dict[str, dict[str, Any]] = {}
    resources = get_filesystem_provider()
    for layer in effective_workspace_layers(root, root.parent):
        for path in resources.rglob(layer, "*", ignored_names=IGNORED_DIRECTORIES):
            if any(part in IGNORED_DIRECTORIES for part in path.parts):
                continue
            if not resources.is_file(path) or path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            record = _file_record(layer, path)
            record.update({
                "source": layer_source(layer, root),
                "workspaceId": layer.name,
            })
            combined[record["path"]] = record
    return sorted(combined.values(), key=lambda record: str(record["path"]).lower())


def _validate_workflow_page_definition(document: Any, expected_id: str) -> dict[str, Any]:
    if not isinstance(document, dict):
        raise ValueError("workflow page source must contain one JSON object")
    if document.get("kind") != "workflow_page":
        raise ValueError("workflow page kind must be workflow_page")
    if str(document.get("id") or "") != expected_id:
        raise ValueError(f"workflow page id must remain {expected_id}")
    if not str(document.get("label") or "").strip():
        raise ValueError("workflow page label is required")
    if not str(document.get("routeView") or "").strip():
        raise ValueError("workflow page routeView is required")
    if not str(document.get("renderer") or "").strip():
        raise ValueError("workflow page renderer is required")
    menu_placement = str(document.get("menuPlacement") or "middle").lower()
    if menu_placement not in {"first", "middle", "last"}:
        raise ValueError("workflow page menuPlacement must be first, middle, or last")
    layout = document.get("layout")
    if not isinstance(layout, dict) or layout.get("kind") != "three_column_accordion":
        raise ValueError("workflow page layout must be three_column_accordion")
    columns = layout.get("columns")
    if not isinstance(columns, list):
        raise ValueError("workflow page layout.columns must be an array")
    by_id = {
        str(column.get("id") or ""): column
        for column in columns
        if isinstance(column, dict)
    }
    for column_id in ("left", "center", "right"):
        column = by_id.get(column_id)
        if not column:
            raise ValueError(f"workflow page must declare the {column_id} column")
        if not isinstance(column.get("members"), list):
            raise ValueError(f"workflow page {column_id} column members must be an array")
    members = [
        member
        for column in by_id.values()
        for member in column.get("members", [])
        if isinstance(member, dict)
    ]
    has_source_editor = any(
        member.get("component") == "ResourceSourceEditor"
        and (member.get("resource") or {}).get("kind") == "workflow_page"
        and (member.get("resource") or {}).get("id") == expected_id
        for member in members
    )
    if not has_source_editor:
        raise ValueError(
            "three-column workflow page must expose its own workflow_page JSON through a ResourceSourceEditor member"
        )
    return document


def _load_artifact_categories(workspace: dict[str, Any]) -> list[dict[str, Any]]:
    return load_workspace_artifact_categories(Path(workspace["root"]))


def _with_artifact_categories(workspace: dict[str, Any], records: list[dict[str, Any]], tree: str) -> list[dict[str, Any]]:
    return apply_artifact_categories(records, _load_artifact_categories(workspace), tree)


def _load_operations(workspace: dict[str, Any]) -> list[dict[str, Any]]:
    return _with_artifact_categories(workspace, load_workspace_operation_records(Path(workspace["root"])), "operations")


def _load_operation_implementations(workspace: dict[str, Any]) -> list[dict[str, Any]]:
    return _with_artifact_categories(workspace, load_workspace_operation_implementation_records(Path(workspace["root"])), "operations")


def _load_datatypes(workspace: dict[str, Any]) -> list[dict[str, Any]]:
    return _with_artifact_categories(workspace, load_workspace_datatype_records(Path(workspace["root"])), "datatypes")


def _load_representations(workspace: dict[str, Any]) -> list[dict[str, Any]]:
    return _with_artifact_categories(workspace, load_workspace_representation_records(Path(workspace["root"])), "datatypes")


def _load_concrete_datatypes(workspace: dict[str, Any]) -> list[dict[str, Any]]:
    return _with_artifact_categories(workspace, load_workspace_concrete_datatype_records(Path(workspace["root"])), "datatypes")


def _load_backends(workspace: dict[str, Any]) -> list[dict[str, Any]]:
    return _with_artifact_categories(workspace, load_workspace_backend_records(Path(workspace["root"])), "models")


def _load_systems(workspace: dict[str, Any]) -> list[dict[str, Any]]:
    root = Path(workspace["root"])
    combined: dict[str, dict[str, Any]] = {}
    for layer in effective_workspace_layers(root, root.parent):
        for directory in (layer / "design" / "systems", layer / "systems"):
            for record in _load_documents(layer, directory, layer_source(layer, root), "system"):
                document = record.get("document") or {}
                combined[str(document.get("id") or record["path"])] = record
    ordered = sorted(combined.values(), key=lambda record: str((record.get("document") or {}).get("label") or record["path"]).lower())
    return _with_artifact_categories(workspace, ordered, "models")


def _load_models(workspace: dict[str, Any]) -> list[dict[str, Any]]:
    return _with_artifact_categories(workspace, resolve_model_records(Path(workspace["root"])), "models")


def _load_prompts(workspace: dict[str, Any]) -> list[dict[str, Any]]:
    return _with_artifact_categories(workspace, load_workspace_prompt_records(Path(workspace["root"])), "prompts")


def _load_symbolic_family(workspace: dict[str, Any], family: str) -> list[dict[str, Any]]:
    tree = {"goal": "goals", "plan": "plans", "context": "atomspaces"}[family]
    return _with_artifact_categories(workspace, load_workspace_symbolic_records(Path(workspace["root"]), family), tree)


def _load_backend_library(workspace: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    return load_backend_library_records(Path(workspace["root"]))


def _load_model_library(workspace: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    return load_model_library_records(Path(workspace["root"]))


def _load_prompt_library(workspace: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    library = load_prompt_library_records(Path(workspace["root"]))
    hierarchy = library["hierarchy"]
    prompts = _with_artifact_categories(workspace, hierarchy["prompts"], "prompts")
    implementations = _with_artifact_categories(workspace, hierarchy["promptImplementations"], "prompts")
    profiles = _with_artifact_categories(workspace, hierarchy["promptProfiles"], "prompts")
    by_prompt: dict[str, list[dict[str, Any]]] = {}
    for record in implementations:
        for parent in relationship_ids((record.get("document") or {}).get("parents")):
            by_prompt.setdefault(parent, []).append(record)
    library["hierarchy"] = {"prompts": prompts, "promptImplementations": implementations, "promptProfiles": profiles, "implementationsByPrompt": by_prompt}
    return library


@router.get("")
def list_workspaces(refresh: bool = Query(default=False), detailed: bool = Query(default=False)) -> dict[str, Any]:
    workspaces = discover_workspaces(force=refresh, include_counts=detailed)
    if not detailed:
        workspaces = [workspace for workspace in workspaces if not workspace.get("hidden")]
    return {"workspaceRoots": [str(path) for path in _workspace_roots()], "workspaces": workspaces}


@router.post("", status_code=201)
def create_workspace(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    resources = get_filesystem_provider()
    label = str(body.get("label") or "").strip()
    requested_id = str(body.get("id") or label).strip().lower()
    workspace_id = re.sub(r"[^a-z0-9]+", "_", requested_id).strip("_")
    if not label or not workspace_id:
        raise HTTPException(status_code=400, detail="A workspace label is required")
    if workspace_id in {"shared", "default"}:
        raise HTTPException(status_code=400, detail="That workspace id is reserved")
    template_id = str(body.get("templateWorkspaceId") or "default").strip()
    try:
        template_workspace = _resolve_workspace(template_id)
    except KeyError as error:
        raise HTTPException(status_code=400, detail=f"Template workspace not found: {template_id}") from error
    container = _workspace_roots()[0]
    template = Path(template_workspace["root"])
    target = container / workspace_id
    if resources.exists(target):
        raise HTTPException(status_code=409, detail=f"Workspace already exists: {workspace_id}")
    if not resources.is_dir(template):
        raise HTTPException(status_code=500, detail="Workspace template is missing")
    try:
        resources.copy_tree(template, target, ignored_names=IGNORED_DIRECTORIES)
        metadata = {
            "kind": "workspace",
            "id": workspace_id,
            "label": label,
            "description": str(body.get("description") or f"Workspace created from {template_workspace['label']}."),
            "includes": declared_include_specs(template),
        }
        resources.write_json(target / "workspace.json", metadata)
        invalidate_workspace_discovery()
        return {"workspace": _workspace_from_directory(target), "templateWorkspaceId": template_workspace["id"]}
    except OSError as error:
        if resources.exists(target):
            resources.delete_tree(target)
        raise HTTPException(status_code=500, detail=str(error)) from error


@router.get("/{workspace_id}")
def get_workspace(workspace_id: str) -> dict[str, Any]:
    try:
        return {"workspace": _resolve_workspace(workspace_id)}
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.get("/{workspace_id}/settings")
def get_workspace_settings(workspace_id: str) -> dict[str, Any]:
    try:
        workspace = _resolve_workspace(workspace_id)
        root = Path(workspace["root"])
        return {"workspace": workspace, "document": read_workspace_metadata(root), "path": str(workspace_metadata_path(root))}
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except (OSError, ValueError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.put("/{workspace_id}/settings")
def update_workspace_settings(workspace_id: str, body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    try:
        workspace = _resolve_workspace(workspace_id)
        incoming_document = body.get("document")
        if incoming_document is not None and not isinstance(incoming_document, dict):
            raise ValueError("document must be an object")
        changes = incoming_document if isinstance(incoming_document, dict) else body
        includes = _normalize_include_specs(workspace, changes.get("includes")) if "includes" in changes else declared_include_specs(Path(workspace["root"]))
        workspace_type = str(changes.get("workspaceType") or workspace.get("workspaceType") or "project")
        if workspace_type not in {"project", "library"}:
            raise ValueError("workspaceType must be 'project' or 'library'")
        root = Path(workspace["root"])
        path = workspace_metadata_path(root)
        metadata = read_workspace_metadata(root)
        if incoming_document is not None:
            metadata = dict(incoming_document)
            incoming_id = str(metadata.get("id") or workspace["id"])
            if incoming_id != workspace["id"]:
                raise ValueError("workspace id cannot be changed from the registry editor")
        metadata.update({
            "kind": "workspace",
            "id": workspace["id"],
            "label": str(metadata.get("label") or workspace["label"]),
            "description": str(metadata.get("description") or workspace["description"]),
            "includes": includes,
            "workspaceType": workspace_type,
            "hidden": changes.get("hidden") is True if "hidden" in changes else metadata.get("hidden") is True,
        })
        get_filesystem_provider().write_json(path, metadata)
        invalidate_workspace_discovery()
        return {"workspace": _workspace_from_directory(root), "document": metadata, "path": str(path)}
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except (OSError, ValueError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.delete("/{workspace_id}")
def delete_workspace(workspace_id: str) -> dict[str, Any]:
    if workspace_id in {SHARED_WORKSPACE_ID, "default", "shared_library_system"}:
        raise HTTPException(status_code=400, detail="This protected workspace cannot be deleted")
    try:
        workspace = _resolve_workspace(workspace_id)
        dependents = [item["id"] for item in discover_workspaces(force=True) if item["id"] != workspace_id and any(spec["workspaceId"] == workspace_id for spec in item.get("includes", []))]
        if dependents:
            raise ValueError(f"Workspace is still included by: {', '.join(sorted(dependents))}")
        root = Path(workspace["root"])
        trash = root.parent / ".workspace-trash"
        target = trash / f"{root.name}-{int(time.time())}"
        resources = get_filesystem_provider()
        resources.make_directory(trash)
        resources.replace(root, target)
        invalidate_workspace_discovery()
        return {"deleted": workspace_id, "recoverable": True, "recoveryPath": str(target)}
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except (OSError, ValueError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


def _workspace_credential_statuses(workspace: dict[str, Any]) -> list[dict[str, Any]]:
    root = Path(workspace["root"])
    return credential_statuses(root, load_workspace_backend_records(root))


@router.get("/{workspace_id}/credentials")
def workspace_credentials(workspace_id: str) -> dict[str, Any]:
    try:
        workspace = _resolve_workspace(workspace_id)
        return {"credentials": _workspace_credential_statuses(workspace)}
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except (OSError, ValueError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.put("/{workspace_id}/credentials/{environment_name}")
def update_workspace_credential(workspace_id: str, environment_name: str, body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    try:
        workspace = _resolve_workspace(workspace_id)
        allowed = {item["environmentVariable"] for item in _workspace_credential_statuses(workspace)}
        if environment_name not in allowed:
            raise ValueError("credential is not declared by a backend visible to this workspace")
        value = body.get("value")
        if not isinstance(value, str) or not value.strip():
            raise ValueError("credential value is required")
        if len(value) > 8192:
            raise ValueError("credential value is too long")
        write_workspace_credential(Path(workspace["root"]), environment_name, value)
        return {"credentials": _workspace_credential_statuses(workspace)}
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except (OSError, ValueError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.delete("/{workspace_id}/credentials/{environment_name}")
def delete_workspace_credential(workspace_id: str, environment_name: str) -> dict[str, Any]:
    try:
        workspace = _resolve_workspace(workspace_id)
        allowed = {item["environmentVariable"] for item in _workspace_credential_statuses(workspace)}
        if environment_name not in allowed:
            raise ValueError("credential is not declared by a backend visible to this workspace")
        write_workspace_credential(Path(workspace["root"]), environment_name, None)
        return {"credentials": _workspace_credential_statuses(workspace)}
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except (OSError, ValueError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.post("/{workspace_id}/credentials/{environment_name}/bootstrap")
def bootstrap_workspace_credential(workspace_id: str, environment_name: str, body: dict[str, Any] = Body(default={})) -> dict[str, Any]:
    try:
        workspace = _resolve_workspace(workspace_id)
        records = load_workspace_backend_records(Path(workspace["root"]))
        backend_id = str(body.get("backendId") or "")
        backend = next(
            (
                record.get("document")
                for record in records
                if backend_matches(record.get("document") or {}, backend_id)
            ),
            None,
        )
        if not backend:
            raise ValueError("automatic credential backend is not visible to this workspace")
        configuration = backend.get("configuration") or {}
        declared_name = str(configuration.get("apiKeyEnvironmentVariable") or configuration.get("apiKeyEnvironment") or "")
        if declared_name != environment_name:
            raise ValueError("backend does not declare the requested credential")
        bootstrap_backend_credential(Path(workspace["root"]), backend)
        return {"credentials": _workspace_credential_statuses(workspace)}
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except (OSError, ValueError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.get("/{workspace_id}/operations")
def workspace_operations(workspace_id: str) -> dict[str, Any]:
    try:
        workspace = _resolve_workspace(workspace_id)
        return {"workspace": workspace, "operations": _load_operations(workspace), "operationImplementations": _load_operation_implementations(workspace)}
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.get("/{workspace_id}/artifact-categories")
def workspace_artifact_categories(workspace_id: str) -> dict[str, Any]:
    try:
        workspace = _resolve_workspace(workspace_id)
        return {"workspace": workspace, "artifactCategories": _load_artifact_categories(workspace)}
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.get("/{workspace_id}/datatypes")
def workspace_datatypes(workspace_id: str) -> dict[str, Any]:
    try:
        workspace = _resolve_workspace(workspace_id)
        return {"workspace": workspace, "datatypes": _load_datatypes(workspace)}
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.get("/{workspace_id}/representations")
def workspace_representations(workspace_id: str) -> dict[str, Any]:
    try:
        workspace = _resolve_workspace(workspace_id)
        return {"workspace": workspace, "representations": _load_representations(workspace)}
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.get("/{workspace_id}/backends")
def workspace_backends(workspace_id: str) -> dict[str, Any]:
    try:
        workspace = _resolve_workspace(workspace_id)
        return {"workspace": workspace, "backends": _load_backends(workspace), "backendLibrary": _load_backend_library(workspace)}
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.get("/{workspace_id}/systems")
def workspace_systems(workspace_id: str) -> dict[str, Any]:
    try:
        workspace = _resolve_workspace(workspace_id)
        return {"workspace": workspace, "systems": _load_systems(workspace)}
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.get("/{workspace_id}/models")
def workspace_models(workspace_id: str) -> dict[str, Any]:
    try:
        workspace = _resolve_workspace(workspace_id)
        return {"workspace": workspace, "models": _load_models(workspace), "modelLibrary": _load_model_library(workspace)}
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.get("/{workspace_id}/prompts")
def workspace_prompts(workspace_id: str) -> dict[str, Any]:
    try:
        workspace = _resolve_workspace(workspace_id)
        return {"workspace": workspace, "prompts": _load_prompts(workspace), "promptLibrary": _load_prompt_library(workspace)}
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.get("/{workspace_id}/goals")
def workspace_goals(workspace_id: str) -> dict[str, Any]:
    try:
        workspace = _resolve_workspace(workspace_id)
        records = _load_symbolic_family(workspace, "goal")
        return {"workspace": workspace, "resources": records, "hierarchy": symbolic_hierarchy(records, "goal")}
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.get("/{workspace_id}/policies")
def workspace_policies(workspace_id: str) -> dict[str, Any]:
    try:
        workspace = _resolve_workspace(workspace_id)
        records = load_workspace_policy_records(Path(workspace["root"]))
        return {"workspace": workspace, "resources": records, "hierarchy": policy_hierarchy(records)}
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.get("/{workspace_id}/plans")
def workspace_plans(workspace_id: str) -> dict[str, Any]:
    try:
        workspace = _resolve_workspace(workspace_id)
        records = _load_symbolic_family(workspace, "plan")
        return {"workspace": workspace, "resources": records, "hierarchy": symbolic_hierarchy(records, "plan")}
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.get("/{workspace_id}/contexts")
def workspace_contexts(workspace_id: str) -> dict[str, Any]:
    try:
        workspace = _resolve_workspace(workspace_id)
        records = _load_symbolic_family(workspace, "context")
        return {"workspace": workspace, "resources": records, "hierarchy": symbolic_hierarchy(records, "context")}
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.get("/{workspace_id}/text-documents")
def workspace_text_documents(workspace_id: str) -> dict[str, Any]:
    try:
        workspace = _resolve_workspace_without_counts(workspace_id)
        return {"documents": _effective_text_documents(workspace)}
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except (OSError, ValueError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.get("/{workspace_id}/text-document")
def read_effective_text_document(
    workspace_id: str,
    path: str = Query(...),
    source_workspace_id: str = Query(default="", alias="sourceWorkspaceId"),
) -> dict[str, Any]:
    try:
        workspace = _resolve_workspace_without_counts(workspace_id)
        root = Path(workspace["root"])
        layers = effective_workspace_layers(root, root.parent)
        if source_workspace_id:
            layer = next((candidate for candidate in layers if candidate.name == source_workspace_id), None)
            if layer is None:
                raise ValueError("text document source is not visible to this workspace")
        else:
            layer = next(
                (
                    candidate
                    for candidate in reversed(layers)
                    if get_filesystem_provider().is_file(_safe_child(candidate, path))
                ),
                root,
            )
        target = _safe_child(layer, path)
        resources = get_filesystem_provider()
        if not resources.is_file(target):
            raise ValueError("text document not found")
        if target.suffix.lower() not in TEXT_SUFFIXES:
            raise ValueError("file type is not editable text")
        record = _file_record(layer, target)
        record.update({"source": layer_source(layer, root), "workspaceId": layer.name})
        return {"document": {**record, "content": resources.read_text(target)}}
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except (OSError, ValueError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.get("/{workspace_id}/workflow-pages/{page_id}/source")
def read_workflow_page_source(workspace_id: str, page_id: str) -> dict[str, Any]:
    try:
        workspace = _resolve_workspace_without_counts(workspace_id)
        root = Path(workspace["root"])
        record = next(
            (
                item
                for item in _load_workflow_pages(workspace)
                if str((item.get("document") or {}).get("id") or "") == page_id
            ),
            None,
        )
        if record is None:
            raise ValueError("workflow page definition not found")
        modified: float | None = None
        relative_path = str(record.get("path") or "")
        if relative_path:
            layer = next(
                (candidate for candidate in effective_workspace_layers(root, root.parent) if candidate.name == str(record.get("workspaceId") or "")),
                root,
            )
            target = _safe_child(layer, relative_path)
            resources = get_filesystem_provider()
            if resources.is_file(target):
                modified = resources.stat(target).st_mtime
        return {
            "workflowPage": record,
            "content": json.dumps(record["document"], indent=2, ensure_ascii=False) + "\n",
            "modified": modified,
        }
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except (OSError, ValueError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.put("/{workspace_id}/workflow-pages/{page_id}/source")
def write_workflow_page_source(
    workspace_id: str,
    page_id: str,
    body: dict[str, Any] = Body(...),
) -> dict[str, Any]:
    try:
        workspace = _resolve_workspace(workspace_id)
        root = Path(workspace["root"])
        content = str(body.get("content") or "")
        document = _validate_workflow_page_definition(json.loads(content), page_id)
        workspace_record = next(
            (
                item
                for item in _load_workflow_pages(workspace)
                if item.get("source") == "workspace"
                and str((item.get("document") or {}).get("id") or "") == page_id
            ),
            None,
        )
        filename = f"{re.sub(r'[^A-Za-z0-9_-]+', '_', page_id).strip('_')}.workflow_page.json"
        target = _safe_child(
            root,
            str(workspace_record.get("path")) if workspace_record else f"design/workflow_pages/{filename}",
        )
        resources = get_filesystem_provider()
        resources.make_directory(target.parent)
        normalized = json.dumps(document, indent=2, ensure_ascii=False) + "\n"
        resources.write_text(target, normalized)
        invalidate_workspace_discovery()
        refreshed = next(
            item
            for item in _load_workflow_pages(workspace)
            if str((item.get("document") or {}).get("id") or "") == page_id
        )
        return {
            "workflowPage": refreshed,
            "content": normalized,
            "createdOverride": workspace_record is None,
            "modified": resources.stat(target).st_mtime if resources.is_file(target) else None,
        }
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except (OSError, ValueError, json.JSONDecodeError, StopIteration) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.get("/{workspace_id}/snapshot")
def workspace_snapshot(workspace_id: str, scope: str = Query(default="full", pattern="^(full|shell)$")) -> dict[str, Any]:
    try:
        workspace = _resolve_workspace(workspace_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    root = Path(workspace["root"])
    files: list[dict[str, Any]] = []
    resources = get_filesystem_provider()
    for path in resources.rglob(root, "*", ignored_names=IGNORED_DIRECTORIES):
        if any(part in IGNORED_DIRECTORIES for part in path.parts):
            continue
        if resources.is_file(path) and path.suffix.lower() in TEXT_SUFFIXES:
            files.append(_file_record(root, path))
        if len(files) >= 2000:
            break
    shell = {
        "workspace": workspace,
        "workflows": _load_workflows(workspace),
        "workflowPages": _load_workflow_pages(workspace),
        "goals": _load_symbolic_family(workspace, "goal"),
        "plans": _load_symbolic_family(workspace, "plan"),
        "contexts": _load_symbolic_family(workspace, "context"),
        "files": files,
    }
    if scope == "shell":
        return shell
    return {
        **shell,
        "operations": _load_operations(workspace),
        "operationImplementations": _load_operation_implementations(workspace),
        "datatypes": _load_datatypes(workspace),
        "representations": _load_representations(workspace),
        "concreteDatatypes": _load_concrete_datatypes(workspace),
        "backends": _load_backends(workspace),
        "systems": _load_systems(workspace),
        "backendLibrary": _load_backend_library(workspace),
        "models": _load_models(workspace),
        "modelLibrary": _load_model_library(workspace),
        "prompts": _load_prompts(workspace),
        "promptLibrary": _load_prompt_library(workspace),
        "policies": load_workspace_policy_records(root),
        "artifactCategories": _load_artifact_categories(workspace),
    }


@router.get("/{workspace_id}/data/files")
def workspace_data_files(workspace_id: str) -> dict[str, Any]:
    try:
        workspace = _resolve_workspace(workspace_id)
        root = Path(workspace["root"])
        resources = get_filesystem_provider()
        files: list[dict[str, Any]] = []
        for path in resources.rglob(root, "*", ignored_names=IGNORED_DIRECTORIES):
            if any(part in IGNORED_DIRECTORIES for part in path.parts):
                continue
            if not resources.is_file(path):
                continue
            relative = path.relative_to(root).as_posix().lower()
            if relative.startswith("data/") or relative.startswith("knowledge/data/"):
                files.append(_file_record(root, path))
            if len(files) >= 5000:
                break
        return {"workspace": workspace, "files": files}
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except OSError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.get("/{workspace_id}/file")
def read_workspace_file(workspace_id: str, path: str = Query(...)) -> dict[str, Any]:
    try:
        workspace = _resolve_workspace_without_counts(workspace_id)
        root = Path(workspace["root"])
        target = _safe_child(root, path)
        resources = get_filesystem_provider()
        if not resources.is_file(target):
            raise ValueError("file not found")
        if target.suffix.lower() not in TEXT_SUFFIXES:
            raise ValueError("file type is not editable text")
        return {"file": {**_file_record(root, target), "content": resources.read_text(target)}}
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except (OSError, ValueError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.get("/{workspace_id}/asset")
def read_workspace_asset(workspace_id: str, path: str = Query(...)) -> FileResponse:
    try:
        workspace = _resolve_workspace(workspace_id)
        root = Path(workspace["root"]).resolve()
        requested = Path(path)
        target = requested.resolve() if requested.is_absolute() else _safe_child(root, path).resolve()
        if target != root and root not in target.parents:
            raise ValueError("asset path escapes workspace")
        if not target.is_file():
            raise ValueError("asset not found")
        return FileResponse(target)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except (OSError, ValueError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.post("/{workspace_id}/data/import")
def import_workspace_data(workspace_id: str, body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """Import binary knowledge values without bypassing the filesystem provider."""
    try:
        workspace = _resolve_workspace(workspace_id)
        root = Path(workspace["root"])
        directory = str(body.get("directory") or "knowledge/data/imports").strip().replace("\\", "/").strip("/")
        if not directory or directory.startswith(("design/", "runtime/")):
            raise ValueError("data directory must be under workspace knowledge storage")
        items = body.get("files")
        if not isinstance(items, list) or not items:
            raise ValueError("files must contain at least one upload")
        if len(items) > 100:
            raise ValueError("at most 100 files may be imported at once")
        resources = get_filesystem_provider()
        overwrite = body.get("overwrite") is True
        imported: list[dict[str, Any]] = []
        for item in items:
            if not isinstance(item, dict):
                raise ValueError("each upload must be an object")
            name = Path(str(item.get("name") or "")).name
            if not name or name in {".", ".."}:
                raise ValueError("each upload requires a safe filename")
            encoded = str(item.get("base64") or "")
            try:
                content = base64.b64decode(encoded, validate=True)
            except (ValueError, binascii.Error) as error:
                raise ValueError(f"invalid base64 for {name}") from error
            if len(content) > 25 * 1024 * 1024:
                raise ValueError(f"{name} exceeds the 25 MiB import limit")
            target = _safe_child(root, f"{directory}/{name}")
            if resources.exists(target) and not overwrite:
                raise ValueError(f"{name} already exists; enable overwrite to replace it")
            resources.write_bytes(target, content)
            imported.append(_file_record(root, target))
        invalidate_workspace_discovery()
        return {"files": imported, "directory": directory}
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except (OSError, ValueError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.put("/{workspace_id}/file")
def write_workspace_file(workspace_id: str, body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    try:
        workspace = _resolve_workspace(workspace_id)
        root = Path(workspace["root"])
        relative = str(body.get("path") or "")
        if not relative:
            raise ValueError("path is required")
        requested = _safe_child(root, relative)
        if requested.suffix.lower() not in TEXT_SUFFIXES:
            raise ValueError("file type is not editable text")
        content = str(body.get("content") or "")
        target = requested
        previous_document: dict[str, Any] | None = None
        relationship_sync = {"updated": [], "unresolved": []}
        if requested.suffix.lower() == ".json":
            resources = get_filesystem_provider()
            if resources.is_file(requested):
                previous_value = resources.read_json(requested)
                incoming_id = str(json.loads(content).get("id") or "")
                previous_documents = previous_value if isinstance(previous_value, list) else [previous_value]
                previous_document = next(
                    (item for item in previous_documents if isinstance(item, dict) and str(item.get("id") or "") == incoming_id),
                    None,
                )
            document = json.loads(content)
            if not isinstance(document, dict):
                raise ValueError("JSON resource must contain an object")
            kind = infer_resource_kind(requested, document)
            document["kind"] = kind
            target = canonical_resource_path(requested, document)
            content = json.dumps(document, indent=2, ensure_ascii=False) + "\n"
        resources = get_filesystem_provider()
        resources.make_directory(target.parent)
        if target != requested and resources.exists(target) and resources.exists(requested):
            raise ValueError(f"canonical target already exists: {target.relative_to(root).as_posix()}")
        resources.write_text(target, content)
        if requested.suffix.lower() == ".json":
            relationship_sync = synchronize_parent_backlinks(root, document, previous_document, resources)
        if target != requested and resources.is_file(requested):
            resources.delete(requested)
        invalidate_workspace_discovery()
        return {"file": {**_file_record(root, target), "content": content}, "relationshipSync": relationship_sync}
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except (OSError, ValueError, json.JSONDecodeError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.delete("/{workspace_id}/file")
def delete_workspace_file(workspace_id: str, path: str = Query(...)) -> dict[str, Any]:
    try:
        workspace = _resolve_workspace(workspace_id)
        root = Path(workspace["root"])
        requested = _safe_child(root, path)
        if requested.suffix.lower() not in TEXT_SUFFIXES:
            raise ValueError("file type is not editable text")
        resources = get_filesystem_provider()
        if not resources.is_file(requested):
            raise KeyError(f"file not found: {path}")
        resources.delete(requested)
        invalidate_workspace_discovery()
        return {"deleted": requested.relative_to(root).as_posix()}
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except (OSError, ValueError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.put("/{workspace_id}/data-file")
def write_workspace_data_file(workspace_id: str, body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """Write a text file verbatim, bypassing all resource/JSON handling.

    Unlike ``PUT /{workspace_id}/file`` this endpoint never injects a ``kind`` field,
    never relocates the target to a canonical resource path, and never synchronizes
    parent backlinks. The setup panel's [scan]/state-editor save and the file-group
    [edit]/[new] editors rely on the on-disk bytes round-tripping exactly (e.g. a plain
    ``state.json`` must not gain a ``kind``). Writable suffixes are limited to
    ``DATA_FILE_SUFFIXES``; other types fall back to a client-side download.
    """
    try:
        workspace = _resolve_workspace(workspace_id)
        root = Path(workspace["root"])
        relative = str(body.get("path") or "")
        if not relative:
            raise ValueError("path is required")
        target = _safe_child(root, relative)
        if target.suffix.lower() not in DATA_FILE_SUFFIXES:
            raise ValueError("file type is not writable as raw text")
        content = body.get("content")
        if not isinstance(content, str):
            raise ValueError("content must be a string")
        resources = get_filesystem_provider()
        # write_bytes writes the exact bytes to the literal path. Do NOT use write_text:
        # for .json paths the provider remaps to a .metta physical file and re-serializes
        # a JSON mirror, which would mangle a plain state.json rather than store it verbatim.
        resources.write_bytes(target, content.encode("utf-8"))
        invalidate_workspace_discovery()
        return {"file": {**_file_record(root, target), "content": content}}
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except (OSError, ValueError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.post("/{workspace_id}/data/line-counts")
def data_file_line_counts(workspace_id: str, body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """Return the non-blank line count for many files in a single request.

    The setup panel shows a per-file "~N lines" and a per-folder total; batching avoids
    one asset request per file. Reads the literal bytes of each path (no resource/JSON
    remapping) and counts lines that contain non-whitespace.
    """
    try:
        workspace = _resolve_workspace(workspace_id)
        root = Path(workspace["root"])
        paths = body.get("paths")
        if not isinstance(paths, list):
            raise ValueError("paths must be a list")
        if len(paths) > 2000:
            raise ValueError("at most 2000 paths may be counted at once")
        resources = get_filesystem_provider()
        counts: dict[str, int] = {}
        for raw in paths:
            if not isinstance(raw, str) or not raw:
                continue
            relative = raw.replace("\\", "/").lstrip("/")
            try:
                target = _safe_child(root, relative)
            except (OSError, ValueError):
                continue
            if not resources.is_file(target):
                continue
            try:
                data = resources.read_bytes(target)
            except (OSError, ValueError):
                continue
            text = data.decode("utf-8", errors="replace")
            counts[relative] = sum(1 for line in text.splitlines() if line.strip())
        return {"counts": counts}
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except (OSError, ValueError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
