from __future__ import annotations

import json
import os
import re
import shutil
import time
from threading import RLock
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Body, HTTPException, Query

from artifact_category_library import apply_artifact_categories, load_workspace_artifact_categories
from backend_library import MODEL_CATALOG_DIRECTORY, load_backend_library_records, load_workspace_backend_records
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
    layers = effective_workspace_layers(root, root.parent)
    include_specs = declared_include_specs(root)
    return {
        "id": root.name,
        "label": str(metadata.get("label") or _humanize(root.name)),
        "description": str(metadata.get("description") or "Filesystem workspace"),
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
        if not force and _workspace_cache and _workspace_cache[0] == cache_key and time.monotonic() - _workspace_cache[1] < WORKSPACE_DISCOVERY_CACHE_SECONDS:
            return [dict(item) for item in _workspace_cache[2]]
        found: dict[str, dict[str, Any]] = {}
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
                workspace = _workspace_from_directory(child, include_counts=include_counts)
                found[workspace["root"]] = workspace
        discovered = sorted(found.values(), key=lambda item: (item["label"].lower(), item["root"].lower()))
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
    return sorted(combined.values(), key=lambda record: str((record.get("document") or {}).get("label") or record["path"]).lower())


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
    return {"workspaceRoots": [str(path) for path in _workspace_roots()], "workspaces": discover_workspaces(force=refresh, include_counts=detailed)}


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


@router.put("/{workspace_id}/settings")
def update_workspace_settings(workspace_id: str, body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    try:
        workspace = _resolve_workspace(workspace_id)
        includes = _normalize_include_specs(workspace, body.get("includes"))
        root = Path(workspace["root"])
        path = workspace_metadata_path(root)
        metadata = read_workspace_metadata(root)
        metadata.update({
            "kind": "workspace",
            "id": workspace["id"],
            "label": metadata.get("label") or workspace["label"],
            "description": metadata.get("description") or workspace["description"],
            "includes": includes,
        })
        get_filesystem_provider().write_json(path, metadata)
        invalidate_workspace_discovery()
        return {"workspace": _workspace_from_directory(root)}
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
                if (record.get("document") or {}).get("id") == backend_id
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


@router.get("/{workspace_id}/file")
def read_workspace_file(workspace_id: str, path: str = Query(...)) -> dict[str, Any]:
    try:
        workspace = _resolve_workspace(workspace_id)
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
