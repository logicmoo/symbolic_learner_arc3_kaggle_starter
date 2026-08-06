from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, Query

from datatype_library import (
    load_workspace_datatype_records,
    load_workspace_representation_records,
    representation_graph,
    resolve_datatype_representation,
)
from workspace_api import _resolve_workspace

router = APIRouter(prefix="/workspaces", tags=["datatypes"])


def _root(workspace_id: str) -> tuple[dict[str, Any], Path]:
    try:
        workspace = _resolve_workspace(workspace_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return workspace, Path(workspace["root"])


@router.get("/{workspace_id}/datatypes")
def workspace_datatypes(workspace_id: str) -> dict[str, Any]:
    workspace, root = _root(workspace_id)
    return {"workspace": workspace, "datatypes": load_workspace_datatype_records(root)}


@router.get("/{workspace_id}/representations")
def workspace_representations(workspace_id: str) -> dict[str, Any]:
    workspace, root = _root(workspace_id)
    return {"workspace": workspace, "representations": load_workspace_representation_records(root)}


@router.get("/{workspace_id}/representation-graph")
def workspace_representation_graph(workspace_id: str) -> dict[str, Any]:
    workspace, root = _root(workspace_id)
    return {"workspace": workspace, **representation_graph(root)}


@router.get("/{workspace_id}/datatypes/{datatype_id}/resolve")
def resolve_representation(workspace_id: str, datatype_id: str, representation: str | None = Query(default=None)) -> dict[str, Any]:
    workspace, root = _root(workspace_id)
    try:
        resolved = resolve_datatype_representation(root, datatype_id, representation)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return {"workspace": workspace, **resolved}
