from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys
import time

import uvicorn


WORKBENCH_ROOT = Path(__file__).resolve().parents[1]
SERVER_ROOT = WORKBENCH_ROOT / "server"
RESTART_EXIT_CODE = 75
SUPERVISED_WORKER_ENV = "WORKBENCH_API_SUPERVISED_WORKER"


def _stop_worker(worker: subprocess.Popen[bytes]) -> None:
    if worker.poll() is not None:
        return
    worker.terminate()
    try:
        worker.wait(timeout=5)
    except subprocess.TimeoutExpired:
        worker.kill()
        worker.wait(timeout=5)


def _run_explicit_restart_supervisor(host: str, port: int) -> None:
    command = [sys.executable, str(Path(__file__).resolve()), "--host", host, "--port", str(port)]
    environment = {**os.environ, SUPERVISED_WORKER_ENV: "1"}
    worker = subprocess.Popen(command, cwd=WORKBENCH_ROOT, env=environment)
    try:
        while True:
            return_code = worker.wait()
            if return_code != RESTART_EXIT_CODE:
                raise SystemExit(return_code)
            print("Explicit API restart requested; starting fresh worker...", flush=True)
            time.sleep(0.2)
            worker = subprocess.Popen(command, cwd=WORKBENCH_ROOT, env=environment)
    except KeyboardInterrupt:
        pass
    finally:
        _stop_worker(worker)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Workbench API development server.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8000, type=int)
    args = parser.parse_args()

    os.chdir(SERVER_ROOT)
    sys.path.insert(0, str(SERVER_ROOT))
    if os.environ.get(SUPERVISED_WORKER_ENV) != "1":
        _run_explicit_restart_supervisor(args.host, args.port)
        return
    uvicorn.run(
        "app:app",
        host=args.host,
        port=args.port,
        reload=False,
        timeout_graceful_shutdown=5,
    )


if __name__ == "__main__":
    main()
