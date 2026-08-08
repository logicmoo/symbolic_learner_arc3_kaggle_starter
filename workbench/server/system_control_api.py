from __future__ import annotations

import ipaddress
import time
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request

router = APIRouter()
INSTANCE_ID = uuid4().hex
SERVER_DIR = Path(__file__).resolve().parent
VITE_CONFIG = SERVER_DIR.parent / "frontend" / "vite.config.ts"


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
