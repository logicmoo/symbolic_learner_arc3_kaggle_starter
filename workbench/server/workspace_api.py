from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Body, HTTPException, Query

router = APIRouter(prefix="/workspaces", tags=["workspaces"])

MANIFEST_NAMES = ("workbench.workspace.json", ".workbench/workspace.json")
DEFAULT_ROOT = Path(__file__).resolve().parents[2]
TEXT_SUFFIXES = {".json", ".md", ".txt", ".py", ".pl", ".metta", ".yaml", ".yml", ".toml"}


def _configured_roots() -> list[Path]:
    raw = os.getenv("WORKBENCH_WORKSPACE_ROOTS", "")
    roots = [Path(part).expanduser().resolve() for part in raw.split(os.pathsep) if part.strip()]
    if DEFAULT_ROOT not in roots:
        roots.insert(0, DEFAULT_ROOT)
    return roots


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Invalid JSON file {path}: {error}") from error
    if not isinstance(value, dict):
        raise ValueError(f"JSON file must contain an object: {path}")
    return value


def _workspace_from_manifest(manifest_path: Path) -> dict[str, Any]:
    manifest = _read_json(manifest_path)
    root = manifest_path.parent.parent if manifest_path.parent.name == ".workbench" else manifest_path.parent
    workflow_relative = str(manifest.get("workflowDirectory") or "workflows").replace("\\", "/").strip("/")
    prompt_relative = str(manifest.get("promptDirectory") or "prompts").replace("\\", "/").strip("/")
    config_relative = str(manifest.get("configDirectory") or "config").replace("\\", "/").strip("/")
    workflow_dir = root / workflow_relative
    prompt_dir = root / prompt_relative
    config_dir = root / config_relative
    return {
        "id": str(manifest.get("id") or root.name),
        "label": str(manifest.get("label") or root.name),
        "description": str(manifest.get("description") or ""),
        "root": str(root.resolve()),
        "manifest": str(manifest_path.resolve()),
        "workflowDirectory": str(workflow_dir.resolve()),
        "workflowDirectoryRelative": workflow_relative,
        "promptDirectory": str(prompt_dir.resolve()),
        "promptDirectoryRelative": prompt_relative,
        "configDirectory": str(config_dir.resolve()),
        "configDirectoryRelative": config_relative,
        "metadata": manifest.get("metadata") or {},
        "workflowFileCount": len(list(workflow_dir.glob("*.json"))) if workflow_dir.exists() else 0,
    }


def discover_workspaces() -> list[dict[str, Any]]:
    found: dict[str, dict[str, Any]] = {}
    for base in _configured_roots():
        if not base.exists():
            continue
        candidates: list[Path] = []
        for name in MANIFEST_NAMES:
            direct = base / name
            if direct.is_file():
                candidates.append(direct)
        try:
            children = list(base.iterdir())
        except OSError:
            children = []
        for child in children:
            if not child.is_dir() or child.name.startswith("."):
                continue
            for name in MANIFEST_NAMES:
                candidate = child / name
                if candidate.is_file():
                    candidates.append(candidate)
        for manifest_path in candidates:
            try:
                workspace = _workspace_from_manifest(manifest_path)
                found[workspace["root"]] = workspace
            except ValueError:
                continue
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


def _load_workflows(workspace: dict[str, Any]) -> list[dict[str, Any]]:
    root = Path(workspace["root"])
    directory = Path(workspace["workflowDirectory"])
    result: list[dict[str, Any]] = []
    if not directory.exists():
        return result
    for path in sorted(directory.glob("*.json")):
        try:
            document = _read_json(path)
            result.append({"path": path.relative_to(root).as_posix(), "document": document})
        except ValueError as error:
            result.append({"path": path.relative_to(root).as_posix(), "error": str(error)})
    return result


@router.get("")
def list_workspaces() -> dict[str, Any]:
    return {"workspaces": discover_workspaces()}


@router.get("/{workspace_id}")
def get_workspace(workspace_id: str) -> dict[str, Any]:
    try:
        workspace = _resolve_workspace(workspace_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return {"workspace": workspace}


@router.get("/{workspace_id}/snapshot")
def workspace_snapshot(workspace_id: str) -> dict[str, Any]:
    try:
        workspace = _resolve_workspace(workspace_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    root = Path(workspace["root"])
    files: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*")):
        if any(part in {".git", "node_modules", ".venv", "__pycache__"} for part in path.parts):
            continue
        if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
            files.append(_file_record(root, path))
        if len(files) >= 2000:
            break
    return {
        "workspace": workspace,
        "workflows": _load_workflows(workspace),
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
