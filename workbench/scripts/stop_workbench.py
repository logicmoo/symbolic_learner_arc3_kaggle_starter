from __future__ import annotations

import argparse
import json
import os
import subprocess
from dataclasses import dataclass

import psutil


ROOT = __import__("pathlib").Path(__file__).resolve().parents[2]
PROCESS_LEDGER = ROOT / "runtime" / "run_workbench_processes.json"


@dataclass(frozen=True)
class Target:
    label: str
    port: int
    command_patterns: tuple[str, ...]


def _listener_pids() -> dict[int, int]:
    completed = subprocess.run(
        ["netstat", "-ano", "-p", "tcp"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=10,
        check=False,
    )
    listeners: dict[int, int] = {}
    for line in completed.stdout.splitlines():
        parts = line.split()
        if len(parts) < 5 or parts[0].upper() != "TCP" or parts[3].upper() != "LISTENING":
            continue
        try:
            listeners.setdefault(int(parts[1].rsplit(":", 1)[1]), int(parts[4]))
        except (IndexError, ValueError):
            continue
    return listeners


def _process_evidence(pid: int) -> str:
    evidence: list[str] = []
    try:
        process = psutil.Process(pid)
        for _ in range(6):
            try:
                evidence.extend((process.name(), process.cwd(), " ".join(process.cmdline())))
                parent = process.parent()
            except (psutil.AccessDenied, psutil.NoSuchProcess, OSError):
                break
            if parent is None:
                break
            process = parent
    except (psutil.AccessDenied, psutil.NoSuchProcess, OSError):
        return ""
    return " ".join(evidence).lower()


def _matches(target: Target, pid: int) -> bool:
    evidence = _process_evidence(pid)
    return bool(evidence) and any(pattern.lower() in evidence for pattern in target.command_patterns)


def _kill_tree(pid: int) -> tuple[bool, str]:
    completed = subprocess.run(
        ["taskkill", "/PID", str(pid), "/T", "/F"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=20,
        check=False,
    )
    message = (completed.stdout or completed.stderr).strip()
    return completed.returncode == 0 or not psutil.pid_exists(pid), message


def stop_targets(web_port: int, api_port: int) -> int:
    targets = (
        Target("ClawRouter", 3456, ("clawrouter", "run_clawrouter.bat")),
        Target("OmniRoute", 20128, ("omniroute", "omni-route", "run_omniroute.bat")),
        Target("FreeRouter", 18800, ("freerouter", "run_freerouter.bat")),
        Target("Workbench API", api_port, ("run_api_server", "uvicorn", "workbench.server")),
        Target("Workbench Web", web_port, ("vite", "run_vite_server.bat")),
        Target("Mailbox Channel Relay", 46667, ("mailbox-server", "mailbox_channel")),
    )
    try:
        ledger = json.loads(PROCESS_LEDGER.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        ledger = []
    owned = {
        str(entry.get("service")): int(entry.get("pid"))
        for entry in ledger if isinstance(entry, dict) and str(entry.get("pid") or "").isdigit()
    }
    service_ids = {
        "ClawRouter": "clawrouter", "OmniRoute": "omniroute", "FreeRouter": "freerouter",
        "Workbench API": "workbench-api", "Workbench Web": "workbench-web",
        "Mailbox Channel Relay": "channel-relay",
    }
    failures = 0
    for target in targets:
        pid = owned.get(service_ids[target.label])
        if pid is None:
            print(f"{target.label}: not recorded as started by run_workbench")
            continue
        if not psutil.pid_exists(pid):
            print(f"{target.label}: recorded PID {pid} is no longer running")
            continue
        if not _matches(target, pid):
            print(f"{target.label}: REFUSED recorded PID {pid}; process identity no longer matches")
            failures += 1
            continue
        stopped, message = _kill_tree(pid)
        if stopped:
            print(f"{target.label}: stopped PID {pid} on port {target.port}")
        else:
            print(f"{target.label}: FAILED to stop PID {pid} on port {target.port}: {message}")
            failures += 1
    if failures == 0 and PROCESS_LEDGER.exists():
        PROCESS_LEDGER.unlink()
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Stop process trees started by run_workbench.bat.")
    parser.add_argument("--web-port", type=int, default=5173)
    parser.add_argument("--api-port", type=int, default=8000)
    args = parser.parse_args()
    if os.name != "nt":
        parser.error("this launcher shutdown helper currently supports Windows only")
    for label, port in (("web", args.web_port), ("API", args.api_port)):
        if not 1 <= port <= 65535:
            parser.error(f"{label} port must be from 1 through 65535")
    return stop_targets(args.web_port, args.api_port)


if __name__ == "__main__":
    raise SystemExit(main())
