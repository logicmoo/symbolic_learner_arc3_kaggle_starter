from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request
from pathlib import Path

import psutil


ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "runtime" / "run_workbench_processes.json"


def _owned_pid(service_id: str) -> int | None:
    try:
        entries = json.loads(LEDGER.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    for entry in reversed(entries if isinstance(entries, list) else []):
        if isinstance(entry, dict) and entry.get("service") == service_id:
            try:
                return int(entry["pid"])
            except (KeyError, TypeError, ValueError):
                return None
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--service", required=True)
    parser.add_argument("--url", required=True)
    parser.add_argument("--timeout", type=float, required=True)
    args = parser.parse_args()
    deadline = time.monotonic() + args.timeout
    grace_deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(args.url, timeout=2) as response:
                if 200 <= response.status < 500:
                    return 0
        except (urllib.error.URLError, TimeoutError, OSError):
            pass
        pid = _owned_pid(args.service)
        if time.monotonic() >= grace_deadline and pid is not None and not psutil.pid_exists(pid):
            print(f"ERROR: {args.service} exited before becoming healthy (owned PID {pid}).")
            return 2
        time.sleep(0.5)
    print(f"ERROR: {args.service} did not become healthy within {args.timeout:g} seconds.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
