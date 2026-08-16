from __future__ import annotations

import ipaddress
import time
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Body, HTTPException, Request
from model_library import resolve_model_records
from model_selection_settings import (
    SYSTEM_POLICY_PATH,
    WORKSPACES_ROOT,
    effective_model_selection,
    system_model_selection,
    workspace_model_selection,
    workspace_policy_path,
    write_system_model_selection,
    write_workspace_model_selection,
)
from resource_store import get_filesystem_provider

router = APIRouter()
INSTANCE_ID = uuid4().hex
SERVER_DIR = Path(__file__).resolve().parent
VITE_CONFIG = SERVER_DIR.parent / "frontend" / "vite.config.ts"


@router.get("/system/resource-provider")
def resource_provider_status() -> dict[str, object]:
    provider = get_filesystem_provider()
    return {"provider": type(provider).__name__, "metrics": provider.metrics()}


def _model_choices(workspace_root: Path) -> list[dict[str, object]]:
    choices: list[dict[str, object]] = []
    for record in resolve_model_records(workspace_root):
        document = record.get("document") or {}
        resolved = record.get("resolved") or {}
        model_id = str(document.get("id") or "")
        if not model_id or record.get("error") or resolved.get("enabled") is False:
            continue
        choices.append({
            "id": model_id,
            "label": str(document.get("label") or model_id),
            "backendId": str(resolved.get("backendId") or ""),
            "remoteModel": str(resolved.get("model") or model_id),
        })
    return sorted(choices, key=lambda item: (str(item["label"]).lower(), str(item["id"])))


def _require_known_model(workspace_root: Path, model_id: str) -> None:
    if model_id and model_id not in {str(item["id"]) for item in _model_choices(workspace_root)}:
        raise HTTPException(status_code=400, detail=f"Unknown or disabled model: {model_id}")


@router.get("/system/model-selection")
def get_system_model_selection() -> dict[str, object]:
    shared_root = WORKSPACES_ROOT / "shared_library_system"
    return {
        "document": system_model_selection(),
        "models": _model_choices(shared_root),
        "path": str(SYSTEM_POLICY_PATH),
    }


@router.put("/system/model-selection")
def update_system_model_selection(
    request: Request,
    body: dict[str, object] = Body(...),
) -> dict[str, object]:
    if not _is_loopback(request.client.host if request.client else None):
        raise HTTPException(status_code=403, detail="System model settings are available only locally")
    incoming = body.get("document") if isinstance(body.get("document"), dict) else body
    document = dict(incoming)
    model_id = str(document.get("fallbackModelId") or "").strip()
    shared_root = WORKSPACES_ROOT / "shared_library_system"
    _require_known_model(shared_root, model_id)
    saved = write_system_model_selection(document)
    return {"document": saved, "models": _model_choices(shared_root), "path": str(SYSTEM_POLICY_PATH)}


@router.get("/workspaces/{workspace_id}/model-selection")
def get_workspace_model_selection(workspace_id: str) -> dict[str, object]:
    workspace_root = WORKSPACES_ROOT / workspace_id
    if not get_filesystem_provider().is_dir(workspace_root):
        raise HTTPException(status_code=404, detail=f"workspace not found: {workspace_id}")
    document = workspace_model_selection(workspace_root)
    effective, source = effective_model_selection(workspace_root, {})
    return {
        "document": document,
        "system": system_model_selection(),
        "effective": effective,
        "source": source,
        "models": _model_choices(workspace_root),
        "path": str(workspace_policy_path(workspace_root)),
    }


@router.put("/workspaces/{workspace_id}/model-selection")
def update_workspace_model_selection(
    workspace_id: str,
    request: Request,
    body: dict[str, object] = Body(...),
) -> dict[str, object]:
    if not _is_loopback(request.client.host if request.client else None):
        raise HTTPException(status_code=403, detail="Workspace model settings are available only locally")
    workspace_root = WORKSPACES_ROOT / workspace_id
    if not get_filesystem_provider().is_dir(workspace_root):
        raise HTTPException(status_code=404, detail=f"workspace not found: {workspace_id}")
    incoming = body.get("document") if isinstance(body.get("document"), dict) else body
    document = dict(incoming)
    model_id = str(document.get("overrideModelId") or "").strip()
    _require_known_model(workspace_root, model_id)
    saved = write_workspace_model_selection(workspace_root, document)
    effective, source = effective_model_selection(workspace_root, {})
    return {
        "document": saved,
        "system": system_model_selection(),
        "effective": effective,
        "source": source,
        "models": _model_choices(workspace_root),
        "path": str(workspace_policy_path(workspace_root)),
    }


def trigger_development_restart(
    api_marker: Path = Path(__file__).resolve(),
    web_marker: Path = VITE_CONFIG,
) -> None:
    """Touch files watched by the Uvicorn and Vite development servers."""
    time.sleep(0.25)
    web_marker.touch()
    api_marker.touch()


def _is_loopback(host: str | None) -> bool:
    if not host:
        return False
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return host.lower() == "localhost"


@router.post("/system/restart", status_code=202)
def restart_development_servers(
    request: Request,
    background_tasks: BackgroundTasks,
) -> dict[str, str]:
    if not _is_loopback(request.client.host if request.client else None):
        raise HTTPException(status_code=403, detail="Server restart is available only locally")
    background_tasks.add_task(trigger_development_restart)
    return {"status": "restarting", "instanceId": INSTANCE_ID}
