from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys

import uvicorn


WORKBENCH_ROOT = Path(__file__).resolve().parents[1]
SERVER_ROOT = WORKBENCH_ROOT / "server"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Workbench API development server.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8000, type=int)
    args = parser.parse_args()

    os.chdir(SERVER_ROOT)
    sys.path.insert(0, str(SERVER_ROOT))
    uvicorn.run(
        "app:app",
        host=args.host,
        port=args.port,
        reload=True,
        reload_dirs=[str(SERVER_ROOT)],
        reload_includes=["*.py"],
        reload_excludes=[
            "environment_files/*",
            "runtime/*",
            "__pycache__/*",
            "test_*.py",
        ],
    )


if __name__ == "__main__":
    main()
