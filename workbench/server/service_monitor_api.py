from __future__ import annotations

import csv
import os
import re
import socket
import subprocess
import urllib.request
import json
import psutil
import time
from threading import RLock, Thread, get_ident
from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Body, HTTPException, Request

from resource_store import get_filesystem_provider
from system_control_api import _is_loopback


router = APIRouter()
ROOT = Path(__file__).resolve().parents[2]
LOG_ROOT = ROOT / "runtime" / "logs"
STARTUP_POLICY_PATH = (
    ROOT / "workbench" / "workspaces" / "shared_library_system" / "policies"
    / "workbench_startup.workbench_startup_policy.json"
)
LEGACY_STARTUP_POLICY_PATH = ROOT / "config" / "workbench_startup.json"
MANAGED_SERVICE_DIRECTORY = ROOT / "workbench" / "workspaces" / "shared_library_system" / "design" / "services"
PROCESS_LEDGER = ROOT / "runtime" / "run_workbench_processes.json"
_LAUNCH_LOCK = RLock()
_PENDING_LAUNCHES: dict[str, tuple[int, float]] = {}


@dataclass(frozen=True)
class ServiceDefinition:
    id: str
    label: str
    description: str
    port: int
    health_path: str
    launcher: Path | None = None
    controllable: bool = False
    command_patterns: tuple[str, ...] = ()
    working_directory: Path = ROOT
    allow_kill: bool = True
    allow_relaunch: bool = True
    default_start: bool = True
    default_hidden: bool = False
    singleton: bool = False


MANAGED_SERVICES = (
    ServiceDefinition(
        "mailbox_server", "Mailbox Channel Relay Proxy", "Standalone mailbox and chat-platform bridging proxy daemon.", 46667, "/health",
        ROOT.parent / "mailbox_channel" / "mailbox-server.cmd", True,
        ("mailbox-server", "mailbox_channel"),
    ),
    ServiceDefinition(
        "clawrouter", "ClawRouter", "Keyless local model-routing gateway.", 3456, "/health",
        ROOT / "workbench" / "scripts" / "run_clawrouter.bat", True,
        ("clawrouter",),
    ),
    ServiceDefinition(
        "omniroute", "OmniRoute", "Local multi-provider routing gateway.", 20128, "/",
        ROOT / "workbench" / "scripts" / "run_omniroute.bat", True,
        ("omniroute", "omni-route"),
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


def _system_processes() -> list[dict[str, Any]]:
    """Return enough OS process metadata to recognize equivalent external launches."""
    if os.name != "nt":
        return []
    script = (
        "Get-CimInstance Win32_Process | Select-Object ProcessId,ParentProcessId,Name,CommandLine | "
        "ConvertTo-Json -Compress"
    )
    completed = subprocess.run(
        ["powershell", "-NoProfile", "-Command", script], capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=10, check=False,
    )
    if completed.returncode != 0 or not completed.stdout.strip():
        return []
    try:
        document = json.loads(completed.stdout)
    except json.JSONDecodeError:
        return []
    rows = document if isinstance(document, list) else [document]
    return [row for row in rows if isinstance(row, dict)]


def _matching_processes(
    definition: ServiceDefinition,
    processes: list[dict[str, Any]],
    listener_pid: int | None,
) -> list[dict[str, Any]]:
    matches: dict[int, dict[str, Any]] = {}
    processes_by_pid = {
        int(process["ProcessId"]): process
        for process in processes if str(process.get("ProcessId") or "").isdigit()
    }
    process_names = {
        int(process["ProcessId"]): str(process.get("Name") or "") or None
        for process in processes if str(process.get("ProcessId") or "").isdigit()
    }
    patterns = tuple(pattern.lower() for pattern in definition.command_patterns)
    for process in processes:
        try:
            pid = int(process.get("ProcessId"))
        except (TypeError, ValueError):
            continue
        command = str(process.get("CommandLine") or "")
        if pid != listener_pid and not any(pattern in command.lower() for pattern in patterns):
            continue
        try:
            parent_pid = int(process.get("ParentProcessId"))
        except (TypeError, ValueError):
            parent_pid = None
        parent_process = processes_by_pid.get(parent_pid) if parent_pid else None
        matches[pid] = {
            "pid": pid,
            "processName": str(process.get("Name") or "") or None,
            "commandLine": _redact(command),
            "listener": pid == listener_pid,
            "workingDirectory": _working_directory(pid),
            "parentPid": parent_pid,
            "parentProcessName": process_names.get(parent_pid) if parent_pid else None,
            "parentWorkingDirectory": _working_directory(parent_pid) if parent_pid else None,
            "parentCommandLine": _redact(str(parent_process.get("CommandLine") or "")) if parent_process else None,
        }
    if listener_pid and listener_pid not in matches:
        parent_pid, parent_name, parent_working_directory, parent_command_line = _parent_process(listener_pid)
        matches[listener_pid] = {
            "pid": listener_pid, "processName": _process_name(listener_pid),
            "commandLine": None, "listener": True,
            "workingDirectory": _working_directory(listener_pid),
            "parentPid": parent_pid, "parentProcessName": parent_name,
            "parentWorkingDirectory": parent_working_directory,
            "parentCommandLine": parent_command_line,
        }
    return sorted(matches.values(), key=lambda item: (not item["listener"], item["pid"]))


def _working_directory(pid: int) -> str | None:
    try:
        return psutil.Process(pid).cwd()
    except (psutil.Error, OSError):
        return None


def _parent_process(pid: int) -> tuple[int | None, str | None, str | None, str | None]:
    try:
        parent = psutil.Process(pid).parent()
        if not parent:
            return None, None, None, None
        try:
            working_directory = parent.cwd()
        except (psutil.Error, OSError):
            working_directory = None
        try:
            command_line = _redact(" ".join(parent.cmdline()))
        except (psutil.Error, OSError):
            command_line = None
        return parent.pid, parent.name(), working_directory, command_line
    except (psutil.Error, OSError):
        return None, None, None, None


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


def _service_payload(
    definition: ServiceDefinition,
    listeners: dict[int, int],
    processes: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    pid = listeners.get(definition.port)
    matches = _matching_processes(definition, processes or [], pid)
    status = _health(definition.port, definition.health_path) if pid or _port_open(definition.port) else "stopped"
    detected = status != "stopped" or bool(matches)
    if status == "stopped" and matches:
        status = "process detected"
    return {
        "id": definition.id,
        "label": definition.label,
        "description": definition.description,
        "port": definition.port,
        "status": status,
        "running": detected,
        "listening": pid is not None,
        "pid": pid,
        "processName": _process_name(pid),
        "processes": matches,
        "matchingProcessCount": len(matches),
        "controllable": definition.controllable,
        "launcher": (
            str(definition.launcher.relative_to(ROOT))
            if definition.launcher and definition.launcher.is_relative_to(ROOT)
            else str(definition.launcher) if definition.launcher else None
        ),
        "workingDirectory": str(definition.working_directory),
        "commandPatterns": list(definition.command_patterns),
        "allowKill": definition.allow_kill,
        "allowRelaunch": definition.allow_relaunch,
        "singleton": definition.singleton,
        "stdout": _tail(LOG_ROOT / f"{definition.id}.stdout.log"),
        "stderr": _tail(LOG_ROOT / f"{definition.id}.stderr.log"),
    }


def _builtin_definitions(api_port: int) -> tuple[ServiceDefinition, ...]:
    return (
        ServiceDefinition(
            "workbench-api", "Workbench API", "Active Python API development server.", api_port, "/api/health",
            command_patterns=("run_api_server.py", "uvicorn", "flask"),
        ),
        ServiceDefinition(
            "workbench-web", "Workbench Web", "Active Vite development frontend.",
            int(os.getenv("WORKBENCH_WEB_PORT", "5173")), "/", command_patterns=("vite",),
        ),
        *MANAGED_SERVICES,
    )


def _read_policy_resource() -> dict[str, Any]:
    resources = get_filesystem_provider()
    source_path = STARTUP_POLICY_PATH if resources.is_file(STARTUP_POLICY_PATH) else LEGACY_STARTUP_POLICY_PATH
    if not resources.is_file(source_path):
        return {}
    try:
        document = resources.read_json(source_path)
        return document if isinstance(document, dict) else {}
    except (OSError, ValueError):
        return {}


def _read_managed_service_resources() -> dict[str, dict[str, Any]]:
    resources = get_filesystem_provider()
    configured: dict[str, dict[str, Any]] = {}
    if not resources.is_dir(MANAGED_SERVICE_DIRECTORY):
        return configured
    for path in resources.glob(MANAGED_SERVICE_DIRECTORY.parent.parent, ("design/services",), "*.managed_service.json"):
        try:
            documents = resources.read_json_documents(path)
        except (OSError, ValueError):
            continue
        for document in documents:
            if isinstance(document, dict) and document.get("kind") == "managed_service" and document.get("id"):
                configured[str(document["id"])] = document
    return configured


def _configured_definition(service_id: str, value: dict[str, Any], fallback: ServiceDefinition | None) -> ServiceDefinition | None:
    launcher_value = value.get("launcher")
    launcher = Path(str(launcher_value)) if launcher_value else fallback.launcher if fallback else None
    if launcher and not launcher.is_absolute():
        launcher = ROOT / launcher
    if launcher:
        launcher = launcher.resolve()
    working_value = value.get("workingDirectory")
    working_directory = Path(str(working_value)) if working_value else fallback.working_directory if fallback else ROOT
    if not working_directory.is_absolute():
        working_directory = ROOT / working_directory
    working_directory = working_directory.resolve()
    try:
        port = int(value.get("port", fallback.port if fallback else 0))
    except (TypeError, ValueError):
        return None
    patterns_value = value.get("commandPatterns", fallback.command_patterns if fallback else ())
    patterns = tuple(str(item) for item in patterns_value) if isinstance(patterns_value, (list, tuple)) else ()
    if not port and not patterns:
        return None
    return ServiceDefinition(
        service_id, str(value.get("label") or (fallback.label if fallback else service_id)),
        str(value.get("description") or (fallback.description if fallback else "Configured managed process.")),
        port, str(value.get("healthPath") or (fallback.health_path if fallback else "/")), launcher,
        value.get("controllable", fallback.controllable if fallback else bool(launcher)) is True,
        patterns, working_directory,
        value.get("allowKill", fallback.allow_kill if fallback else True) is True,
        value.get("allowRelaunch", fallback.allow_relaunch if fallback else True) is True,
        (value.get("defaultStartup") or {}).get("start", fallback.default_start if fallback else True) is True,
        (value.get("defaultStartup") or {}).get("hidden", fallback.default_hidden if fallback else False) is True,
        value.get("singleton", fallback.singleton if fallback else False) is True,
    )


def _definitions(api_port: int) -> tuple[ServiceDefinition, ...]:
    builtins = {item.id: item for item in _builtin_definitions(api_port)}
    configured = _read_managed_service_resources()
    if not configured:
        return tuple(builtins.values())
    definitions: dict[str, ServiceDefinition] = dict(builtins)
    for service_id, value in configured.items():
        if isinstance(value, dict):
            definition = _configured_definition(str(service_id), value, builtins.get(str(service_id)))
            if definition:
                definitions[str(service_id)] = definition
    return tuple(definitions.values())


def _startup_policy() -> dict[str, dict[str, bool]]:
    defaults = {item.id: {"start": item.default_start, "hiddenWindow": item.default_hidden, "hideFromProcessViewer": False} for item in _definitions(8000)}
    document = _read_policy_resource()
    configured = document.get("services") if isinstance(document, dict) else None
    if not isinstance(configured, dict):
        return defaults
    for service_id, value in configured.items():
        if service_id in defaults and isinstance(value, dict):
            defaults[service_id] = {"start": value.get("start") is True, "hiddenWindow": value.get("hiddenWindow", value.get("hidden")) is True, "hideFromProcessViewer": value.get("hideFromProcessViewer") is True}
    return defaults


def _startup_policy_document() -> dict[str, Any]:
    document = _read_policy_resource()
    configured = document.get("services") if isinstance(document.get("services"), dict) else {}
    services: dict[str, Any] = {}
    for definition in _definitions(8000):
        existing = configured.get(definition.id) if isinstance(configured.get(definition.id), dict) else {}
        services[definition.id] = {
            "start": existing.get("start", definition.default_start) is True,
            "hiddenWindow": existing.get("hiddenWindow", existing.get("hidden", definition.default_hidden)) is True,
            "hideFromProcessViewer": existing.get("hideFromProcessViewer") is True,
        }
    return {
        **document,
        "kind": "workbench_startup_policy", "id": "workbench_startup",
        "label": "Managed Process Startup Policy", "services": services,
    }


@router.get("/system/startup")
def get_startup_policy() -> dict[str, Any]:
    document = _startup_policy_document()
    return {"services": document["services"], "document": document, "path": str(STARTUP_POLICY_PATH)}


@router.put("/system/startup")
def update_startup_policy(request: Request, body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    _require_local(request)
    incoming_document = body.get("document")
    if incoming_document is not None and not isinstance(incoming_document, dict):
        raise HTTPException(status_code=400, detail="document must be an object")
    incoming = (incoming_document or body).get("services")
    if not isinstance(incoming, dict):
        raise HTTPException(status_code=400, detail="services must be an object")
    normalized: dict[str, Any] = {}
    for service_id, value in incoming.items():
        if not isinstance(value, dict):
            raise HTTPException(status_code=400, detail=f"Invalid service policy: {service_id}")
        if service_id not in {item.id for item in _definitions(8000)}:
            raise HTTPException(status_code=400, detail=f"Unknown managed service: {service_id}")
        normalized[str(service_id)] = {"start": value.get("start") is True, "hiddenWindow": value.get("hiddenWindow", value.get("hidden")) is True, "hideFromProcessViewer": value.get("hideFromProcessViewer") is True}
    resources = get_filesystem_provider()
    resources.make_directory(STARTUP_POLICY_PATH.parent)
    document = {
        **(incoming_document or {}), "kind": "workbench_startup_policy",
        "id": "workbench_startup", "services": normalized,
    }
    resources.write_json(STARTUP_POLICY_PATH, document)
    return {"services": _startup_policy(), "document": document, "path": str(STARTUP_POLICY_PATH)}


@router.get("/system/services")
def list_services(request: Request, include_hidden: bool = False) -> dict[str, Any]:
    api_port = request.url.port or 8000
    listeners = _listener_pids()
    processes = _system_processes()
    services = [_service_payload(item, listeners, processes) for item in _definitions(api_port)]
    if not include_hidden:
        policy = _startup_policy()
        services = [item for item in services if not policy.get(item["id"], {}).get("hideFromProcessViewer")]
    return {"services": services, "running": sum(1 for item in services if item["running"])}


def _managed(service_id: str) -> ServiceDefinition:
    definition = next((item for item in _definitions(8000) if item.id == service_id), None)
    if definition is None or not definition.controllable or not definition.launcher:
        raise HTTPException(status_code=404, detail="Unknown controllable workbench service")
    return definition


def _require_local(request: Request) -> None:
    if not _is_loopback(request.client.host if request.client else None):
        raise HTTPException(status_code=403, detail="Workbench service controls are available only locally")


def _validate_submitted_command(service_id: str, cwd: Path, command: list[str]) -> None:
    text = " ".join(command).lower()
    cwd_text = str(cwd.resolve()).lower()
    allowed = {
        "clawrouter": "@blockrun/clawrouter" in text,
        "omniroute": "omniroute" in text,
        "workbench-web": cwd.name.lower() == "frontend" and "npm" in text and "dev" in text and "vite" in text,
        "mailbox_server": "mailbox_channel" in cwd_text and "mailbox_channels.server" in text,
    }
    if not allowed.get(service_id, False):
        raise HTTPException(status_code=400, detail="Submitted command does not match the managed service contract")


def _validated_environment(service_id: str, value: Any) -> dict[str, str]:
    if value is None:
        return {}
    if not isinstance(value, dict) or not all(isinstance(key, str) and isinstance(item, str) for key, item in value.items()):
        raise HTTPException(status_code=400, detail="environment must be a string map")
    allowed = {
        "clawrouter": {"CLAWROUTER_PORT"},
        "omniroute": {"PORT", "DASHBOARD_PORT"},
        "workbench-web": {"WORKBENCH_WEB_HOST", "WORKBENCH_WEB_PORT", "WORKBENCH_API_TARGET"},
        "mailbox_server": {"PYTHONPATH"},
    }.get(service_id, set())
    unexpected = set(value) - allowed
    if unexpected:
        raise HTTPException(status_code=400, detail=f"Unsupported environment overrides: {', '.join(sorted(unexpected))}")
    return dict(value)


def _record_api_launch(service_id: str, process: subprocess.Popen, cwd: Path, command: list[str]) -> None:
    resources = get_filesystem_provider()
    try:
        entries = json.loads(resources.read_text(PROCESS_LEDGER, encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        entries = []
    if not isinstance(entries, list):
        entries = []
    entries = [entry for entry in entries if isinstance(entry, dict) and entry.get("service") != service_id]
    entries.append({"service": service_id, "pid": process.pid, "startedAtEpoch": time.time(), "cwd": str(cwd.resolve()), "rawCommand": command, "terminationScope": "process-tree", "launchedBy": "workbench-api"})
    resources.make_directory(PROCESS_LEDGER.parent, parents=True, exist_ok=True)
    temporary = PROCESS_LEDGER.with_name(
        f".{PROCESS_LEDGER.name}.{os.getpid()}.{get_ident()}.tmp"
    )
    resources.write_text(temporary, json.dumps(entries, indent=2) + "\n", encoding="utf-8")
    resources.replace(temporary, PROCESS_LEDGER)


@router.post("/system/services/{service_id}/launch-command")
def launch_submitted_command(service_id: str, request: Request, body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    _require_local(request)
    command = body.get("command")
    if not isinstance(command, list) or not command or not all(isinstance(value, str) and value for value in command):
        raise HTTPException(status_code=400, detail="command must be a non-empty string array")
    cwd = Path(str(body.get("cwd") or ""))
    if not cwd.is_dir():
        raise HTTPException(status_code=400, detail="cwd must be an existing directory")
    _validate_submitted_command(service_id, cwd, command)
    environment = _validated_environment(service_id, body.get("environment"))
    definition = next((item for item in _definitions(request.url.port or 8000) if item.id == service_id), None)
    with _LAUNCH_LOCK:
        if definition and definition.port and _port_open(definition.port):
            return {"status": "already-running", "serviceId": service_id, "pid": _listener_pids().get(definition.port), "terminationScope": "external-or-existing"}
        pending = _PENDING_LAUNCHES.get(service_id)
        if pending and psutil.pid_exists(pending[0]) and time.monotonic() - pending[1] < 120:
            return {"status": "launch-pending", "serviceId": service_id, "pid": pending[0], "terminationScope": "process-tree"}
        _PENDING_LAUNCHES.pop(service_id, None)
        flags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0) | getattr(subprocess, "CREATE_NEW_CONSOLE", 0)
        executable_command = command
        if Path(command[0]).suffix.lower() in {".bat", ".cmd"}:
            executable_command = [os.environ.get("COMSPEC", "cmd.exe"), "/d", "/c", *command]
        process = subprocess.Popen(executable_command, cwd=cwd, env={**os.environ, **environment}, stdin=subprocess.DEVNULL, creationflags=flags, close_fds=False)
        _PENDING_LAUNCHES[service_id] = (process.pid, time.monotonic())
        _record_api_launch(service_id, process, cwd, command)
        return {"status": "started", "serviceId": service_id, "pid": process.pid, "rawCommand": command, "terminationScope": "process-tree"}


def _start(definition: ServiceDefinition) -> None:
    if _port_open(definition.port):
        return
    if definition.singleton and _matching_processes(definition, _system_processes(), None):
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
            cwd=definition.working_directory, stdin=subprocess.DEVNULL, stdout=stdout_handle, stderr=stderr_handle,
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


def reconcile_startup_services(api_port: int = 8000) -> list[dict[str, Any]]:
    """Restore enabled daemons after an API restart without claiming outsiders."""
    policy = _startup_policy()
    results: list[dict[str, Any]] = []
    for definition in _definitions(api_port):
        if definition.id in {"workbench-api", "workbench-web"}:
            continue
        if not policy.get(definition.id, {}).get("start"):
            results.append({"serviceId": definition.id, "status": "disabled"})
            continue
        if _port_open(definition.port):
            results.append({"serviceId": definition.id, "status": "already-running", "owned": False})
            continue
        try:
            _start(definition)
            results.append({"serviceId": definition.id, "status": "launch-requested"})
        except Exception as error:
            results.append({"serviceId": definition.id, "status": "error", "error": _redact(str(error))})
    return results


def schedule_startup_reconciliation(api_port: int = 8000, delay_seconds: float = 2.0) -> None:
    def run() -> None:
        time.sleep(delay_seconds)
        results = reconcile_startup_services(api_port)
        get_filesystem_provider().make_directory(LOG_ROOT)
        get_filesystem_provider().write_text(
            LOG_ROOT / "startup-reconciliation.json",
            json.dumps({"reconciledAtEpoch": time.time(), "results": results}, indent=2) + "\n",
        )
    Thread(target=run, name="workbench-startup-reconciler", daemon=True).start()


def _kill_pid(pid: int) -> None:
    """Terminate only the selected PID; service-level controls own tree termination."""
    if os.name != "nt":
        raise HTTPException(status_code=501, detail="Process killing is currently implemented for Windows")
    completed = subprocess.run(
        ["taskkill", "/PID", str(pid), "/F"], capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=15, check=False,
    )
    if completed.returncode != 0 and psutil.pid_exists(pid):
        raise HTTPException(status_code=500, detail=_redact(completed.stderr.strip() or "Unable to kill process"))


def _require_matching_pid(definition: ServiceDefinition, pid: int) -> None:
    listener_pid = _listener_pids().get(definition.port)
    matches = _matching_processes(definition, _system_processes(), listener_pid)
    if pid not in {item["pid"] for item in matches}:
        raise HTTPException(status_code=409, detail="PID no longer matches this service; refresh Processes")


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


@router.post("/system/services/{service_id}/processes/{pid}/{action}")
def control_matching_process(service_id: str, pid: int, action: str, request: Request) -> dict[str, Any]:
    _require_local(request)
    definition = _managed(service_id)
    _require_matching_pid(definition, pid)
    if action not in {"kill", "relaunch"}:
        raise HTTPException(status_code=400, detail="Action must be kill or relaunch")
    if action == "kill" and not definition.allow_kill:
        raise HTTPException(status_code=403, detail="Killing is disabled by the managed process policy")
    if action == "relaunch" and not definition.allow_relaunch:
        raise HTTPException(status_code=403, detail="Relaunching is disabled by the managed process policy")
    _kill_pid(pid)
    if action == "relaunch":
        _start(definition)
    return {"status": action, "serviceId": service_id, "pid": pid, "terminationScope": "selected-pid-only"}
