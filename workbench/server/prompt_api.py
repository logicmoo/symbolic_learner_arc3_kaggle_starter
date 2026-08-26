from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter, Body, HTTPException, Query

from prompt_library import (
    _validate_prompt,
    load_workspace_prompt_implementation_records,
    load_workspace_prompt_profile_records,
    load_workspace_prompt_records,
    prompt_hierarchy,
    resolve_prompt_implementation,
    resolve_prompt_profile,
)
from resource_relationships import synchronize_implementation_backlinks
from resource_store import get_filesystem_provider
from workspace_api import _resolve_workspace, _safe_child, invalidate_workspace_discovery

router = APIRouter(prefix="/workspaces", tags=["prompts"])


def _root(workspace_id: str) -> tuple[dict[str, Any], Path]:
    try:
        workspace = _resolve_workspace(workspace_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return workspace, Path(workspace["root"])


@router.get("/{workspace_id}/prompt-hierarchy")
def workspace_prompt_hierarchy(workspace_id: str) -> dict[str, Any]:
    workspace, root = _root(workspace_id)
    return {"workspace": workspace, **prompt_hierarchy(root)}


@router.get("/{workspace_id}/prompt-implementations")
def workspace_prompt_implementations(workspace_id: str) -> dict[str, Any]:
    workspace, root = _root(workspace_id)
    return {
        "workspace": workspace,
        "prompts": load_workspace_prompt_records(root),
        "promptImplementations": load_workspace_prompt_implementation_records(root),
        "promptProfiles": load_workspace_prompt_profile_records(root),
    }


@router.put("/{workspace_id}/prompts/{prompt_id}")
def update_prompt_resource(
    workspace_id: str,
    prompt_id: str,
    body: dict[str, Any] = Body(...),
) -> dict[str, Any]:
    """Replace one Prompt resource without overwriting siblings in its file."""
    workspace, root = _root(workspace_id)
    relative = str(body.get("path") or "").strip()
    document = body.get("document")
    if not relative:
        raise HTTPException(status_code=400, detail="path is required")
    if not isinstance(document, dict):
        raise HTTPException(status_code=400, detail="document must be an object")
    try:
        path = _safe_child(root, relative)
        if "prompts" not in path.relative_to(root).parts:
            raise ValueError("Prompt resources must remain in a prompts directory")
        resources = get_filesystem_provider()
        if not resources.is_file(path):
            raise ValueError("Prompt resource file not found")
        previous = next(
            (
                value
                for value in resources.read_json_documents(path)
                if isinstance(value, dict) and str(value.get("id") or "") == prompt_id
            ),
            None,
        )
        if previous is None:
            raise ValueError(f"Prompt resource not found in file: {prompt_id}")
        updated = _validate_prompt(dict(document), path)
        if str(updated.get("id") or "") != prompt_id:
            raise ValueError("Prompt id cannot be changed by this editor")
        resources.write_json_resource(path, updated)
        relationship_sync = synchronize_implementation_backlinks(root, updated, previous, resources)
        invalidate_workspace_discovery()
        return {
            "workspace": workspace,
            "path": relative,
            "document": updated,
            "relationshipSync": relationship_sync,
        }
    except (OSError, ValueError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.get("/{workspace_id}/prompt-profiles/{profile_id}/resolve")
def resolve_profile(workspace_id: str, profile_id: str) -> dict[str, Any]:
    workspace, root = _root(workspace_id)
    try:
        resolved = resolve_prompt_profile(root, profile_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return {"workspace": workspace, **resolved}


@router.get("/{workspace_id}/prompts/{prompt_id}/resolve")
def resolve_prompt(
    workspace_id: str,
    prompt_id: str,
    implementation: str | None = Query(default=None),
) -> dict[str, Any]:
    workspace, root = _root(workspace_id)
    try:
        resolved = resolve_prompt_implementation(root, prompt_id, implementation)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return {"workspace": workspace, **resolved}
