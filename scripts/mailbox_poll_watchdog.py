"""Keep one agent's existing mailbox poll healthy and preserve its output.

Each invocation owns exactly one agent identity.  Run four invocations for four
agents; there is deliberately no central multi-agent supervisor.
"""

from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import IO, Any, Sequence

try:
    from _runtime import configure_runtime_home
except ModuleNotFoundError:  # Loaded as scripts.mailbox_poll_watchdog in tests/tools.
    from scripts._runtime import configure_runtime_home


ROOT = configure_runtime_home(__file__)
DEFAULT_CLIENT = ROOT / ".codex" / "mailbox" / "agent_mailbox.py"
DEFAULT_RUNTIME_ROOT = ROOT / ".codex" / "mailbox" / "runtime"
DEFAULT_URL = "http://127.0.0.1:46667"


def safe_identity(identity: str) -> str:
    value = "".join(character if character.isalnum() or character in "-_" else "-"
                    for character in identity.strip())
    if not value:
        raise ValueError("agent identity must not be empty")
    return value


def runtime_dir(identity: str, root: Path = DEFAULT_RUNTIME_ROOT) -> Path:
    return root / safe_identity(identity)


def poll_command(
    identity: str,
    *,
    client: Path = DEFAULT_CLIENT,
    url: str = DEFAULT_URL,
    poll_interval: int = 5,
    poll_checks: int = 61,
) -> list[str]:
    return [
        sys.executable,
        str(client),
        "--url",
        url,
        "--as",
        identity,
        "--format",
        "jsonl",
        "--nobuffer",
        "poll",
        "--subscriptions",
        "--cursor",
        identity,
        "--interval",
        str(poll_interval),
        "--checks",
        str(poll_checks),
        "--require-port",
        "46667",
    ]


def process_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    if os.name == "nt":
        import ctypes

        process_query_limited_information = 0x1000
        handle = ctypes.windll.kernel32.OpenProcess(
            process_query_limited_information,
            False,
            pid,
        )
        if not handle:
            return False
        ctypes.windll.kernel32.CloseHandle(handle)
        return True
    try:
        os.kill(pid, 0)
    except (OSError, ProcessLookupError):
        return False
    return True


def _lock(lock_file: IO[bytes]) -> None:
    lock_file.seek(0)
    lock_file.write(b"1")
    lock_file.flush()
    lock_file.seek(0)
    if os.name == "nt":
        import msvcrt

        msvcrt.locking(lock_file.fileno(), msvcrt.LK_NBLCK, 1)
    else:
        import fcntl

        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}
    return payload if isinstance(payload, dict) else {}


def launch_poll(
    command: Sequence[str], spool: IO[bytes], errors: IO[bytes],
) -> subprocess.Popen[bytes]:
    creation_flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    return subprocess.Popen(
        list(command),
        cwd=ROOT,
        stdin=subprocess.DEVNULL,
        stdout=spool,
        stderr=errors,
        creationflags=creation_flags,
    )


def run_supervisor(
    identity: str,
    *,
    url: str = DEFAULT_URL,
    client: Path = DEFAULT_CLIENT,
    runtime_root: Path = DEFAULT_RUNTIME_ROOT,
    watchdog_interval: int = 10,
    poll_interval: int = 5,
    poll_checks: int = 61,
    sleep: Any = time.sleep,
    launcher: Any = launch_poll,
) -> int:
    target = runtime_dir(identity, runtime_root)
    target.mkdir(parents=True, exist_ok=True)
    lock_path = target / "supervisor.lock"
    status_path = target / "status.json"
    spool_path = target / "deliveries.jsonl"
    error_path = target / "poller.log"
    stop_requested = False
    child: subprocess.Popen[bytes] | None = None

    def request_stop(_signum: int, _frame: Any) -> None:
        nonlocal stop_requested
        stop_requested = True

    signal.signal(signal.SIGINT, request_stop)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, request_stop)

    with lock_path.open("a+b") as lock_file:
        try:
            _lock(lock_file)
        except OSError:
            return 2
        command = poll_command(
            identity,
            client=client,
            url=url,
            poll_interval=poll_interval,
            poll_checks=poll_checks,
        )
        with spool_path.open("ab", buffering=0) as spool, error_path.open("ab", buffering=0) as errors:
            while not stop_requested:
                if child is None:
                    child = launcher(command, spool, errors)
                    write_json(status_path, {
                        "agent": identity,
                        "supervisor_pid": os.getpid(),
                        "poll_pid": child.pid,
                        "state": "polling",
                        "watchdog_interval": watchdog_interval,
                        "poll_interval": poll_interval,
                        "poll_checks": poll_checks,
                        "started_at": time.time(),
                    })
                sleep(watchdog_interval)
                return_code = child.poll()
                if return_code is None:
                    continue
                write_json(status_path, {
                    "agent": identity,
                    "supervisor_pid": os.getpid(),
                    "poll_pid": child.pid,
                    "state": "restarting",
                    "last_exit_code": return_code,
                    "restart_at": time.time() + watchdog_interval,
                })
                child = None
            if child is not None and child.poll() is None:
                child.terminate()
                try:
                    child.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    child.kill()
            write_json(status_path, {
                "agent": identity,
                "supervisor_pid": os.getpid(),
                "state": "stopped",
                "stopped_at": time.time(),
            })
    return 0


def spool_offset(target: Path) -> int:
    payload = read_json(target / "spool_cursor.json")
    try:
        return max(0, int(payload.get("offset", 0)))
    except (TypeError, ValueError):
        return 0


def peek_spool(identity: str, runtime_root: Path = DEFAULT_RUNTIME_ROOT) -> tuple[int, bytes]:
    target = runtime_dir(identity, runtime_root)
    path = target / "deliveries.jsonl"
    offset = spool_offset(target)
    if not path.exists():
        return offset, b""
    size = path.stat().st_size
    if offset > size:
        offset = 0
    with path.open("rb") as stream:
        stream.seek(offset)
        return offset, stream.read()


def acknowledge_spool(
    identity: str,
    runtime_root: Path = DEFAULT_RUNTIME_ROOT,
    *,
    offset: int | None = None,
) -> int:
    target = runtime_dir(identity, runtime_root)
    path = target / "deliveries.jsonl"
    size = path.stat().st_size if path.exists() else 0
    current = spool_offset(target)
    acknowledged = size if offset is None else offset
    if acknowledged < current or acknowledged > size:
        raise ValueError(
            f"ack offset must be between current offset {current} and spool size {size}"
        )
    target.mkdir(parents=True, exist_ok=True)
    write_json(
        target / "spool_cursor.json",
        {"offset": acknowledged, "updated_at": time.time()},
    )
    return acknowledged


def status(identity: str, runtime_root: Path = DEFAULT_RUNTIME_ROOT) -> dict[str, Any]:
    payload = read_json(runtime_dir(identity, runtime_root) / "status.json")
    supervisor_pid = int(payload.get("supervisor_pid", 0) or 0)
    poll_pid = int(payload.get("poll_pid", 0) or 0)
    payload["supervisor_alive"] = process_alive(supervisor_pid)
    payload["poll_alive"] = process_alive(poll_pid)
    return payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Supervise one agent mailbox poll")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name in ("run", "status", "peek", "ack"):
        subparser = subparsers.add_parser(name)
        subparser.add_argument("--agent", required=True)
        subparser.add_argument("--runtime-root", type=Path, default=DEFAULT_RUNTIME_ROOT)
        if name == "run":
            subparser.add_argument("--url", default=DEFAULT_URL)
            subparser.add_argument("--client", type=Path, default=DEFAULT_CLIENT)
            subparser.add_argument("--watchdog-interval", type=int, default=10)
            subparser.add_argument("--poll-interval", type=int, default=5)
            subparser.add_argument("--poll-checks", type=int, default=61)
        if name == "peek":
            subparser.add_argument("--envelope", action="store_true")
        if name == "ack":
            subparser.add_argument("--offset", type=int)
    return parser


def main(arguments: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(arguments)
    if args.command == "run":
        return run_supervisor(
            args.agent,
            url=args.url,
            client=args.client,
            runtime_root=args.runtime_root,
            watchdog_interval=args.watchdog_interval,
            poll_interval=args.poll_interval,
            poll_checks=args.poll_checks,
        )
    if args.command == "status":
        print(json.dumps(status(args.agent, args.runtime_root), indent=2))
        return 0
    if args.command == "peek":
        offset, content = peek_spool(args.agent, args.runtime_root)
        if args.envelope:
            records = []
            for line in content.splitlines():
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    records.append({"raw": line.decode("utf-8", errors="replace")})
            print(json.dumps({
                "agent": args.agent,
                "start_offset": offset,
                "end_offset": offset + len(content),
                "records": records,
            }))
        else:
            sys.stdout.buffer.write(content)
        return 0
    if args.command == "ack":
        print(json.dumps({
            "agent": args.agent,
            "offset": acknowledge_spool(
                args.agent,
                args.runtime_root,
                offset=args.offset,
            ),
        }))
        return 0
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
