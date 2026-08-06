from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, Query

from prompt_library import (
    load_workspace_prompt_implementation_records,
    load_workspace_prompt_records,
    prompt_hierarchy,
    resolve_prompt_implementation,
)
from workspace_api import _resolve_workspace

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
    }


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
