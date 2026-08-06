from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Body, HTTPException, Query

router = APIRouter(prefix="/workspaces", tags=["workspaces"])

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_WORKSPACES_ROOT = REPOSITORY_ROOT / "workbench" / "workspaces"
DEFAULT_WORKSPACE_ID = "default"
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
        "metadata": metadata.get("metadata") or {},
        "workflowFileCount": len(list(workflow_dir.glob("*.json"))) if workflow_dir.exists() else 0,
        "taskFileCount": len(list(task_dir.glob("*.json"))) if task_dir.exists() else 0,
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


def _default_workspace() -> dict[str, Any] | None:
    try:
        return _resolve_workspace(DEFAULT_WORKSPACE_ID)
    except KeyError:
        return None


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
    for path in sorted(directory.glob("*.json")):
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
    """Merge disk-backed default tasks with workspace-specific tasks.

    Workspace task IDs override shared default task IDs while both remain visibly
    attributed to their source directory in the task editor.
    """
    combined: dict[str, dict[str, Any]] = {}
    default = _default_workspace()
    if default:
        default_root = Path(default["root"])
        for record in _load_documents(default_root, Path(default["taskDirectory"]), "shared"):
            document = record.get("document") or {}
            key = str(document.get("id") or record["path"])
            record["workspaceId"] = default["id"]
            combined[key] = record
    root = Path(workspace["root"])
    for record in _load_documents(root, Path(workspace["taskDirectory"]), "workspace"):
        document = record.get("document") or {}
        key = str(document.get("id") or record["path"])
        record["workspaceId"] = workspace["id"]
        combined[key] = record
    return sorted(combined.values(), key=lambda item: str((item.get("document") or {}).get("label") or item["path"]).lower())


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
