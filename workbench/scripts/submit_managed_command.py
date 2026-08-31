from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Ask the Workbench API to launch one expanded managed command.")
    parser.add_argument("--api", default="http://127.0.0.1:8000")
    parser.add_argument("--service", required=True)
    parser.add_argument("--cwd", type=Path, required=True)
    parser.add_argument("--env", action="append", default=[])
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = list(args.command)
    if command[:1] == ["--"]:
        command = command[1:]
    if not command:
        parser.error("an expanded command is required after --")
    environment = {name: os.environ[name] for name in args.env if name in os.environ}
    payload = json.dumps({"cwd": str(args.cwd.resolve()), "command": command, "environment": environment}).encode("utf-8")
    request = urllib.request.Request(
        f"{args.api.rstrip('/')}/workbench/system/services/{args.service}/launch-command",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            result = json.loads(response.read().decode("utf-8"))
        print(f"{args.service}: Workbench API returned {result['status']} for PID {result.get('pid')}")
        return 0
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError, ValueError) as error:
        print("WARNING: Workbench API is unavailable; running this command in LEGACY MODE.", file=sys.stderr)
        print(f"WARNING: This fallback process is not API-owned: {error}", file=sys.stderr)
        return subprocess.call(command, cwd=args.cwd)


if __name__ == "__main__":
    raise SystemExit(main())
