from __future__ import annotations

import csv
import os
import re
import socket
import subprocess
import urllib.request
from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, Request

from resource_store import get_filesystem_provider
from system_control_api import _is_loopback


router = APIRouter()
ROOT = Path(__file__).resolve().parents[2]
LOG_ROOT = ROOT / "runtime" / "logs"


@dataclass(frozen=True)
class ServiceDefinition:
    id: str
    label: str
    description: str
    port: int
    health_path: str
    launcher: Path | None = None
    controllable: bool = False


MANAGED_SERVICES = (
    ServiceDefinition(
        "clawrouter", "ClawRouter", "Keyless local model-routing gateway.", 3456, "/health",
        ROOT / "workbench" / "scripts" / "run_clawrouter.bat", True,
    ),
    ServiceDefinition(
        "omniroute", "OmniRoute", "Local multi-provider routing gateway.", 20128, "/",
        ROOT / "workbench" / "scripts" / "run_omniroute.bat", True,
    ),
    ServiceDefinition(
        "freerouter", "FreeRouter", "Local gateway pinned to OpenRouter's free route.", 18800, "/health",
        ROOT / "workbench" / "scripts" / "run_freerouter.bat", True,
    ),
)

_SECRET_PATTERNS = (
    re.compile(r"(?i)(authorization\s*[:=]\s*bearer\s+)[^\s\"']+"),
    re.compile(r"(?i)((?:api[_-]?key|token|secret)\s*[:=]\s*)[^\s,;\"']+"),
    re.compile(r"\b(?:sk|or-v1)-[A-Za-z0-9_-]{12,}\b"),
)
_ANSI_ESCAPE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")


def _redact(value: str) -> str:
    value = _ANSI_ESCAPE.sub("", value)
    for pattern in _SECRET_PATTERNS:
        value = pattern.sub(lambda match: (match.group(1) if match.lastindex else "") + "[REDACTED]", value)
    return value


def _listener_pids() -> dict[int, int]:
    if os.name != "nt":
        return {}
    completed = subprocess.run(
        ["netstat", "-ano", "-p", "tcp"], capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=5, check=False,
    )
    listeners: dict[int, int] = {}
    for line in completed.stdout.splitlines():
        parts = line.split()
        if len(parts) < 5 or parts[0].upper() != "TCP" or parts[3].upper() != "LISTENING":
            continue
        try:
            port = int(parts[1].rsplit(":", 1)[1])
            listeners.setdefault(port, int(parts[4]))
        except (IndexError, ValueError):
            continue
    return listeners


def _process_name(pid: int | None) -> str | None:
    if not pid or os.name != "nt":
        return None
    completed = subprocess.run(
        ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=5, check=False,
    )
    rows = list(csv.reader(StringIO(completed.stdout)))
    if not rows or not rows[0] or rows[0][0].startswith("INFO:"):
        return None
    return rows[0][0]


def _port_open(port: int) -> bool:
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=0.3):
            return True
    except OSError:
        return False


def _health(port: int, path: str) -> str:
    try:
        request = urllib.request.Request(f"http://127.0.0.1:{port}{path}", method="GET")
        with urllib.request.urlopen(request, timeout=0.8) as response:
            return "healthy" if response.status < 500 else "degraded"
    except Exception:
        return "listening" if _port_open(port) else "stopped"


def _tail(path: Path, line_count: int = 60) -> str:
    resources = get_filesystem_provider()
    if not resources.is_file(path):
        return ""
    try:
        lines = resources.read_text(path, encoding="utf-8").splitlines()
    except (OSError, UnicodeError):
        return ""
    return _redact("\n".join(lines[-line_count:]))


def _service_payload(definition: ServiceDefinition, listeners: dict[int, int]) -> dict[str, Any]:
    pid = listeners.get(definition.port)
    status = _health(definition.port, definition.health_path) if pid or _port_open(definition.port) else "stopped"
    return {
        "id": definition.id,
        "label": definition.label,
        "description": definition.description,
        "port": definition.port,
        "status": status,
        "running": status != "stopped",
        "pid": pid,
        "processName": _process_name(pid),
        "controllable": definition.controllable,
        "launcher": str(definition.launcher.relative_to(ROOT)) if definition.launcher else None,
        "stdout": _tail(LOG_ROOT / f"{definition.id}.stdout.log"),
        "stderr": _tail(LOG_ROOT / f"{definition.id}.stderr.log"),
    }


def _definitions(api_port: int) -> tuple[ServiceDefinition, ...]:
    return (
        ServiceDefinition("workbench-api", "Workbench API", "Active FastAPI development server.", api_port, "/api/health"),
        ServiceDefinition("workbench-web", "Workbench Web", "Active Vite development frontend.", int(os.getenv("WORKBENCH_WEB_PORT", "5173")), "/"),
        *MANAGED_SERVICES,
    )


@router.get("/system/services")
def list_services(request: Request) -> dict[str, Any]:
    api_port = request.url.port or 8000
    listeners = _listener_pids()
    services = [_service_payload(item, listeners) for item in _definitions(api_port)]
    return {"services": services, "running": sum(1 for item in services if item["running"])}


def _managed(service_id: str) -> ServiceDefinition:
    definition = next((item for item in MANAGED_SERVICES if item.id == service_id), None)
    if definition is None:
        raise HTTPException(status_code=404, detail="Unknown controllable workbench service")
    return definition


def _require_local(request: Request) -> None:
    if not _is_loopback(request.client.host if request.client else None):
        raise HTTPException(status_code=403, detail="Workbench service controls are available only locally")


def _start(definition: ServiceDefinition) -> None:
    if _port_open(definition.port):
        return
    assert definition.launcher is not None
    resources = get_filesystem_provider()
    resources.make_directory(LOG_ROOT)
    stdout_handle = resources.open_append_text(LOG_ROOT / f"{definition.id}.stdout.log")
    stderr_handle = resources.open_append_text(LOG_ROOT / f"{definition.id}.stderr.log")
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0) | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
    try:
        subprocess.Popen(
            [os.environ.get("COMSPEC", "cmd.exe"), "/d", "/c", str(definition.launcher)],
            cwd=ROOT, stdin=subprocess.DEVNULL, stdout=stdout_handle, stderr=stderr_handle,
            creationflags=flags, close_fds=False,
        )
    finally:
        stdout_handle.close()
        stderr_handle.close()


def _stop(definition: ServiceDefinition) -> None:
    pid = _listener_pids().get(definition.port)
    if not pid:
        return
    if os.name != "nt":
        raise HTTPException(status_code=501, detail="Service stopping is currently implemented for Windows")
    completed = subprocess.run(
        ["taskkill", "/PID", str(pid), "/T", "/F"], capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=15, check=False,
    )
    if completed.returncode != 0 and _port_open(definition.port):
        raise HTTPException(status_code=500, detail=_redact(completed.stderr.strip() or "Unable to stop service"))


@router.post("/system/services/{service_id}/{action}")
def control_service(service_id: str, action: str, request: Request) -> dict[str, str]:
    _require_local(request)
    definition = _managed(service_id)
    if action == "start":
        _start(definition)
    elif action == "stop":
        _stop(definition)
    elif action == "restart":
        _stop(definition)
        _start(definition)
    else:
        raise HTTPException(status_code=400, detail="Action must be start, stop, or restart")
    return {"status": action, "serviceId": service_id}
