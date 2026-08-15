from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
POLICY_PATH = (
    ROOT / "workbench" / "workspaces" / "shared_library_system" / "policies"
    / "workbench_startup.workbench_startup_policy.metta"
)
LEGACY_POLICY_PATH = ROOT / "config" / "workbench_startup.json"
SERVICE_DIRECTORY = ROOT / "workbench" / "workspaces" / "shared_library_system" / "design" / "services"


def _policy_document() -> dict:
    if POLICY_PATH.is_file():
        sys.path.insert(0, str(ROOT / "workbench" / "server"))
        from metta_resource_codec import metta_document_to_json
        return metta_document_to_json(POLICY_PATH.read_text(encoding="utf-8"))
    try:
        return json.loads(LEGACY_POLICY_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def policy_for(service_id: str) -> dict[str, bool]:
    defaults = {"start": True, "hiddenWindow": False}
    for candidate in SERVICE_DIRECTORY.glob("*.managed_service.metta"):
        try:
            sys.path.insert(0, str(ROOT / "workbench" / "server"))
            from metta_resource_codec import metta_document_to_json
            service = metta_document_to_json(candidate.read_text(encoding="utf-8"))
            if service.get("id") == service_id:
                configured_default = service.get("defaultStartup") or {}
                defaults = {"start": configured_default.get("start", True) is True, "hiddenWindow": configured_default.get("hiddenWindow", configured_default.get("hidden")) is True}
                break
        except (OSError, ValueError, AttributeError):
            continue
    try:
        document = _policy_document()
        value = document.get("services", {}).get(service_id)
    except (OSError, ValueError, AttributeError):
        value = None
    if not isinstance(value, dict):
        return defaults
    return {"start": value.get("start", defaults["start"]) is True, "hiddenWindow": value.get("hiddenWindow", value.get("hidden", defaults["hiddenWindow"])) is True}


def main() -> int:
    parser = argparse.ArgumentParser(description="Start one run_workbench child according to the persisted system policy.")
    parser.add_argument("--service", required=True)
    parser.add_argument("--cwd", type=Path, default=ROOT / "workbench")
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    policy = policy_for(args.service)
    if not policy["start"]:
        print(f"{args.service}: disabled by the shared Workbench startup policy resource")
        return 3
    if not args.command:
        parser.error("a child command is required")
    flags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
    stdout = stderr = None
    if os.name == "nt":
        flags |= getattr(subprocess, "CREATE_NO_WINDOW" if policy["hiddenWindow"] else "CREATE_NEW_CONSOLE", 0)
    if policy["hiddenWindow"]:
        log_root = ROOT / "runtime" / "logs"
        log_root.mkdir(parents=True, exist_ok=True)
        stdout = (log_root / f"{args.service}.stdout.log").open("a", encoding="utf-8")
        stderr = (log_root / f"{args.service}.stderr.log").open("a", encoding="utf-8")
    try:
        subprocess.Popen(args.command, cwd=args.cwd, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr, creationflags=flags, close_fds=False)
    finally:
        if stdout:
            stdout.close()
        if stderr:
            stderr.close()
    print(f"{args.service}: started ({'hidden window' if policy['hiddenWindow'] else 'visible window'})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
