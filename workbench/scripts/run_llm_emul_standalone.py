"""Run llm_emul (the simulated LLM backend relay) standalone, on its own
port -- the same router that's normally mounted inside the main
workbench server (see workbench/server/app.py, which serves it on port
8000 alongside everything else), for when you want it reachable
independently (e.g. a separate machine/process, or just to keep it out
of the main server's restart cycle).

Usage:
    python workbench/scripts/run_llm_emul_standalone.py               # 127.0.0.1:8801
    python workbench/scripts/run_llm_emul_standalone.py --port 9001
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys

import uvicorn

WORKBENCH_ROOT = Path(__file__).resolve().parents[1]
SERVER_ROOT = WORKBENCH_ROOT / "server"
DEFAULT_PORT = 8801  # distinct from the main workbench server's 8000


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=DEFAULT_PORT, type=int)
    parser.add_argument("--no-reload", action="store_true", help="disable autoreload (e.g. for a longer-lived background run)")
    args = parser.parse_args()

    os.chdir(SERVER_ROOT)
    sys.path.insert(0, str(SERVER_ROOT))
    uvicorn.run(
        "llm_emul.standalone_app:app",
        host=args.host,
        port=args.port,
        reload=not args.no_reload,
        reload_dirs=[str(SERVER_ROOT)] if not args.no_reload else None,
        reload_includes=["llm_emul/*.py"] if not args.no_reload else None,
        reload_excludes=["runtime/*", "__pycache__/*", "test_*.py"] if not args.no_reload else None,
    )


if __name__ == "__main__":
    main()
