from __future__ import annotations

import ipaddress
import json
import os
import time
from pathlib import Path
from threading import Lock
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Body, HTTPException, Request
from starlette.concurrency import run_in_threadpool
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
from plugin_api import run_workbench_shutdown
from resource_store import get_filesystem_provider

router = APIRouter()
INSTANCE_ID = uuid4().hex
SERVER_DIR = Path(__file__).resolve().parent
API_RESTART_MARKER = SERVER_DIR.parent / "runtime" / "api_restart.request"
RESTART_PENDING_PATH = SERVER_DIR.parent / "runtime" / "restart_pending.json"
_api_restart_request_lock = Lock()
_API_RESTART_DEBOUNCE_SECONDS = 10.0
_workbench_presence: dict[str, dict[str, object]] = {}
_workbench_presence_lock = Lock()
_PRESENCE_TTL_SECONDS = 60.0


def _load_restart_pending() -> dict[str, object] | None:
    try:
        value = json.loads(RESTART_PENDING_PATH.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def restart_pending_active() -> bool:
    return _load_restart_pending() is not None


def _persist_restart_pending(value: dict[str, object] | None) -> None:
    if value is None:
        RESTART_PENDING_PATH.unlink(missing_ok=True)
        return
    RESTART_PENDING_PATH.parent.mkdir(parents=True, exist_ok=True)
    temporary = RESTART_PENDING_PATH.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, RESTART_PENDING_PATH)


_restart_pending: dict[str, object] | None = _load_restart_pending()


def _prune_workbench_presence() -> list[dict[str, object]]:
    cutoff = time.time() - _PRESENCE_TTL_SECONDS
    with _workbench_presence_lock:
        expired = [tab_id for tab_id, presence in _workbench_presence.items() if float(presence.get("serverSeenAt") or 0) < cutoff]
        for tab_id in expired:
            _workbench_presence.pop(tab_id, None)
        return sorted(_workbench_presence.values(), key=lambda presence: (str(presence.get("workspaceId") or ""), str(presence.get("pageId") or ""), str(presence.get("tabId") or "")))


@router.post("/system/presence")
async def report_workbench_presence(body: dict[str, object] = Body(...)) -> dict[str, object]:
    tab_id = str(body.get("tabId") or "").strip()
    if not tab_id or len(tab_id) > 100:
        raise HTTPException(status_code=400, detail="tabId is required and must be at most 100 characters")
    active = body.get("active") is not False
    with _workbench_presence_lock:
        if active:
            _workbench_presence[tab_id] = {
                "tabId": tab_id,
                "workspaceId": str(body.get("workspaceId") or "workspace-chooser")[:160],
                "pageId": str(body.get("pageId") or "workspace-chooser")[:160],
                "href": str(body.get("href") or "")[:2000],
                "active": True,
                "seenAt": int(body.get("seenAt") or 0),
                "serverSeenAt": time.time(),
            }
        else:
            _workbench_presence.pop(tab_id, None)
    return {"accepted": True, "active": active, "workbenches": _prune_workbench_presence()}


@router.get("/system/presence")
async def list_workbench_presence() -> dict[str, object]:
    return {"workbenches": _prune_workbench_presence(), "ttlSeconds": _PRESENCE_TTL_SECONDS, "restartPending": _restart_pending}


@router.post("/system/restart-pending")
async def report_restart_pending(body: dict[str, object] = Body(...)) -> dict[str, object]:
    global _restart_pending
    if body.get("active") is False:
        _restart_pending = None
    else:
        changes = body.get("changes")
        change_list = changes if isinstance(changes, list) else []
        _restart_pending = {
            "reason": str(body.get("reason") or "Restart requested.")[:1000],
            "changes": [str(change)[:1000] for change in change_list if str(change).strip()][:20],
            "requestedAt": time.time(),
        }
    await run_in_threadpool(_persist_restart_pending, _restart_pending)
    return {"accepted": True, "restartPending": _restart_pending}


@router.get("/system/resource-provider")
def resource_provider_status() -> dict[str, object]:
    provider = get_filesystem_provider()
    return {"provider": type(provider).__name__, "metrics": provider.metrics()}


def _model_choices(
    workspace_root: Path,
    *,
    include_disabled: bool = False,
) -> list[dict[str, object]]:
    choices: list[dict[str, object]] = []
    for record in resolve_model_records(workspace_root):
        document = record.get("document") or {}
        resolved = record.get("resolved") or {}
        model_id = str(document.get("id") or "")
        enabled = resolved.get("enabled") is not False
        if not model_id or record.get("error") or (not enabled and not include_disabled):
            continue
        choices.append({
            "id": model_id,
            "label": str(document.get("label") or model_id),
            "backendId": str(resolved.get("backendId") or ""),
            "remoteModel": str(resolved.get("model") or model_id),
            "source": str(record.get("source") or ""),
            "workspaceId": str(record.get("workspaceId") or workspace_root.name),
            "inherited": str(record.get("source") or "") != "workspace",
            "enabled": enabled,
            "capabilities": document.get("capabilities") if isinstance(document.get("capabilities"), dict) else {},
        })
    source_order = {"workspace": 0, "included": 1, "shared": 2}
    return sorted(
        choices,
        key=lambda item: (
            source_order.get(str(item["source"]), 3),
            str(item["label"]).lower(),
            str(item["id"]),
        ),
    )


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
async def get_workspace_model_selection(
    workspace_id: str,
    include_models: bool = True,
    include_disabled_models: bool = False,
) -> dict[str, object]:
    workspace_root = WORKSPACES_ROOT / workspace_id
    if not get_filesystem_provider().is_dir(workspace_root):
        raise HTTPException(status_code=404, detail=f"workspace not found: {workspace_id}")
    document = workspace_model_selection(workspace_root)
    effective, source = effective_model_selection(workspace_root, {})
    models = await run_in_threadpool(
        _model_choices,
        workspace_root,
        include_disabled=include_disabled_models,
    ) if include_models else []
    return {
        "document": document,
        "system": system_model_selection(),
        "effective": effective,
        "source": source,
        "models": models,
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


def trigger_api_restart(api_marker: Path = API_RESTART_MARKER) -> None:
    """Restart only the API; the browser owns its controlled UI reload lifecycle.

    A self-restart runs exactly one lifecycle phase -- ``workbenchShutdown``,
    then ``workbenchShutdownAfter`` -- and nothing else (no install,
    uninstall, or workspace-* phase). This is a notification, not a command:
    a plugin running in standalone mode (its own separate process) must not
    treat it as "restart yourself too", since only the embedded API process
    is restarting here, not the plugin's own process.
    """
    run_workbench_shutdown(reason="restart")
    time.sleep(0.25)
    api_marker.touch()
    if os.environ.get("WORKBENCH_API_SUPERVISED_WORKER") == "1":
        os._exit(75)


def _claim_api_restart(api_marker: Path = API_RESTART_MARKER) -> bool:
    with _api_restart_request_lock:
        api_marker.parent.mkdir(parents=True, exist_ok=True)
        if api_marker.is_file():
            age = time.time() - api_marker.stat().st_mtime
            if 0 <= age < _API_RESTART_DEBOUNCE_SECONDS:
                return False
        api_marker.touch()
        return True


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
    if not _claim_api_restart():
        return {"status": "already-restarting", "instanceId": INSTANCE_ID}
    background_tasks.add_task(trigger_api_restart, API_RESTART_MARKER)
    return {"status": "restarting", "instanceId": INSTANCE_ID}
