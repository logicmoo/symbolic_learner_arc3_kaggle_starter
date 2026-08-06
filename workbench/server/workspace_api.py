from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Body, HTTPException, Query

from backend_library import MODEL_CATALOG_DIRECTORY, load_backend_library_records, load_workspace_backend_records
from model_library import load_model_library_records, resolve_model_records
from prompt_library import load_prompt_library_records, load_workspace_prompt_records
from task_library import DEFAULT_WORKSPACES_ROOT, load_workspace_task_records

router = APIRouter(prefix="/workspaces", tags=["workspaces"])

TEXT_SUFFIXES = {".json", ".md", ".txt", ".py", ".pl", ".metta", ".yaml", ".yml", ".toml"}
IGNORED_DIRECTORIES = {".git", ".venv", "node_modules", "__pycache__"}


def _workspace_roots() -> list[Path]:
    raw = os.getenv("WORKBENCH_WORKSPACE_ROOTS", "")
    roots = [Path(part).expanduser().resolve() for part in raw.split(os.pathsep) if part.strip()]
    default = DEFAULT_WORKSPACES_ROOT.resolve()
    if default not in roots:
        roots.insert(0, default)
    return roots


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Invalid JSON file {path}: {error}") from error
    if not isinstance(value, dict):
        raise ValueError(f"JSON file must contain an object: {path}")
    return value


def _optional_metadata(root: Path) -> dict[str, Any]:
    path = root / "workspace.json"
    if not path.is_file():
        return {}
    try:
        return _read_json(path)
    except ValueError:
        return {}


def _humanize(name: str) -> str:
    return name.replace("-", " ").replace("_", " ").strip().title()


def _workspace_from_directory(root: Path) -> dict[str, Any]:
    metadata = _optional_metadata(root)
    workflow_dir = root / "workflows"
    prompt_dir = root / "prompts"
    config_dir = root / "config"
    task_dir = root / "tasks"
    model_dir = root / MODEL_CATALOG_DIRECTORY
    backend_count = len(load_workspace_backend_records(root))
    model_count = len(resolve_model_records(root))
    prompt_count = len(load_workspace_prompt_records(root))
    return {
        "id": root.name,
        "label": str(metadata.get("label") or _humanize(root.name)),
        "description": str(metadata.get("description") or "Filesystem workspace"),
        "root": str(root.resolve()),
        "manifest": None,
        "discovery": "directory-enumeration",
        "workflowDirectory": str(workflow_dir.resolve()),
        "workflowDirectoryRelative": "workflows",
        "promptDirectory": str(prompt_dir.resolve()),
        "promptDirectoryRelative": "prompts",
        "configDirectory": str(config_dir.resolve()),
        "configDirectoryRelative": "config",
        "taskDirectory": str(task_dir.resolve()),
        "taskDirectoryRelative": "tasks",
        "backendDirectory": str(model_dir.resolve()),
        "backendDirectoryRelative": MODEL_CATALOG_DIRECTORY,
        "modelDirectory": str(model_dir.resolve()),
        "modelDirectoryRelative": MODEL_CATALOG_DIRECTORY,
        "metadata": metadata.get("metadata") or {},
        "workflowFileCount": len(list(workflow_dir.glob("*.json"))) if workflow_dir.exists() else 0,
        "taskFileCount": len(list(task_dir.glob("*.json"))) if task_dir.exists() else 0,
        "backendFileCount": backend_count,
        "modelFileCount": model_count,
        "promptFileCount": prompt_count,
        "catalogFileCount": len(list(model_dir.glob("*.json"))) if model_dir.exists() else 0,
    }


def discover_workspaces() -> list[dict[str, Any]]:
    found: dict[str, dict[str, Any]] = {}
    for container in _workspace_roots():
        if not container.is_dir():
            continue
        try:
            children = sorted(container.iterdir(), key=lambda path: path.name.lower())
        except OSError:
            continue
        for child in children:
            if not child.is_dir() or child.name.startswith(".") or child.name in IGNORED_DIRECTORIES:
                continue
            workspace = _workspace_from_directory(child)
            found[workspace["root"]] = workspace
    return sorted(found.values(), key=lambda item: (item["label"].lower(), item["root"].lower()))


def _resolve_workspace(workspace_id: str) -> dict[str, Any]:
    for workspace in discover_workspaces():
        if workspace["id"] == workspace_id or workspace["root"] == workspace_id:
            return workspace
    raise KeyError("workspace not found")


def _safe_child(root: Path, relative: str) -> Path:
    resolved_root = root.resolve()
    resolved = (resolved_root / relative).resolve()
    if resolved != resolved_root and resolved_root not in resolved.parents:
        raise ValueError("path escapes workspace root")
    return resolved


def _file_record(root: Path, path: Path) -> dict[str, Any]:
    stat = path.stat()
    return {
        "path": path.relative_to(root).as_posix(),
        "name": path.name,
        "suffix": path.suffix.lower(),
        "size": stat.st_size,
        "modified": stat.st_mtime,
        "kind": "directory" if path.is_dir() else "file",
    }


def _load_documents(root: Path, directory: Path, source: str) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    if not directory.exists():
        return result
    for path in sorted(directory.glob("*.json"), key=lambda item: item.name.lower()):
        record: dict[str, Any] = {"path": path.relative_to(root).as_posix(), "source": source}
        try:
            record["document"] = _read_json(path)
        except ValueError as error:
            record["error"] = str(error)
        result.append(record)
    return result


def _load_workflows(workspace: dict[str, Any]) -> list[dict[str, Any]]:
    root = Path(workspace["root"])
    return _load_documents(root, Path(workspace["workflowDirectory"]), "workspace")


def _load_tasks(workspace: dict[str, Any]) -> list[dict[str, Any]]:
    return load_workspace_task_records(Path(workspace["root"]))


def _load_backends(workspace: dict[str, Any]) -> list[dict[str, Any]]:
    return load_workspace_backend_records(Path(workspace["root"]))


def _load_models(workspace: dict[str, Any]) -> list[dict[str, Any]]:
    return resolve_model_records(Path(workspace["root"]))


def _load_prompts(workspace: dict[str, Any]) -> list[dict[str, Any]]:
    return load_workspace_prompt_records(Path(workspace["root"]))


def _load_backend_library(workspace: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    return load_backend_library_records(Path(workspace["root"]))


def _load_model_library(workspace: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    return load_model_library_records(Path(workspace["root"]))


def _load_prompt_library(workspace: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    return load_prompt_library_records(Path(workspace["root"]))


@router.get("")
def list_workspaces() -> dict[str, Any]:
    return {"workspaceRoots": [str(path) for path in _workspace_roots()], "workspaces": discover_workspaces()}


@router.get("/{workspace_id}")
def get_workspace(workspace_id: str) -> dict[str, Any]:
    try:
        return {"workspace": _resolve_workspace(workspace_id)}
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.get("/{workspace_id}/tasks")
def workspace_tasks(workspace_id: str) -> dict[str, Any]:
    try:
        workspace = _resolve_workspace(workspace_id)
        return {"workspace": workspace, "tasks": _load_tasks(workspace)}
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


@router.get("/{workspace_id}/snapshot")
def workspace_snapshot(workspace_id: str) -> dict[str, Any]:
    try:
        workspace = _resolve_workspace(workspace_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    root = Path(workspace["root"])
    files: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*")):
        if any(part in IGNORED_DIRECTORIES for part in path.parts):
            continue
        if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
            files.append(_file_record(root, path))
        if len(files) >= 2000:
            break
    return {
        "workspace": workspace,
        "workflows": _load_workflows(workspace),
        "tasks": _load_tasks(workspace),
        "backends": _load_backends(workspace),
        "backendLibrary": _load_backend_library(workspace),
        "models": _load_models(workspace),
        "modelLibrary": _load_model_library(workspace),
        "prompts": _load_prompts(workspace),
        "promptLibrary": _load_prompt_library(workspace),
        "files": files,
    }


@router.get("/{workspace_id}/file")
def read_workspace_file(workspace_id: str, path: str = Query(...)) -> dict[str, Any]:
    try:
        workspace = _resolve_workspace(workspace_id)
        root = Path(workspace["root"])
        target = _safe_child(root, path)
        if not target.is_file():
            raise ValueError("file not found")
        if target.suffix.lower() not in TEXT_SUFFIXES:
            raise ValueError("file type is not editable text")
        return {"file": {**_file_record(root, target), "content": target.read_text(encoding="utf-8")}}
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
        target = _safe_child(root, relative)
        if target.suffix.lower() not in TEXT_SUFFIXES:
            raise ValueError("file type is not editable text")
        target.parent.mkdir(parents=True, exist_ok=True)
        content = str(body.get("content") or "")
        target.write_text(content, encoding="utf-8")
        return {"file": {**_file_record(root, target), "content": content}}
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except (OSError, ValueError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
