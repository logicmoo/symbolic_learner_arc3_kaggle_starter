"""Minimal append-only JSONL mailbox shared by local agents."""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import os
import re
import runpy
import shutil
import socket
import sys
import time
import uuid
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_SENDER = "symbolic-workbench-codex"
PEERS = ("omegaclaw-core-codex", "omegaclaw-min", "channel-relay")
MAILBOX_ENV = "AGENT_MAILBOX_DIR"
MAILBOX_URL_ENV = "AGENT_MAILBOX_URL"
DEFAULT_MAILBOX_URL = "http://127.0.0.1:46667"
UNSAFE_FILENAME = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def default_mailbox_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "mailbox_channel" / "mailbox"


def mailbox_dir() -> Path:
    configured = os.environ.get(MAILBOX_ENV)
    return Path(configured).expanduser().resolve() if configured else default_mailbox_dir()


def _cursor_path(root: Path, recipient: str) -> Path:
    digest = hashlib.sha256(recipient.encode("utf-8")).hexdigest()[:16]
    return root / "cursors" / f"{digest}.cursor"


def _read_cursor(path: Path) -> int:
    try:
        return max(0, int(path.read_text(encoding="ascii").strip()))
    except (FileNotFoundError, ValueError):
        return 0


def _write_cursor(path: Path, offset: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(f".{os.getpid()}.{uuid.uuid4().hex}.tmp")
    temporary.write_text(str(offset), encoding="ascii")
    os.replace(temporary, path)


def _safe_attachment_name(path: Path, used_names: set[str]) -> str:
    name = UNSAFE_FILENAME.sub("_", path.name).strip(" .") or "attachment"
    candidate = name
    suffix = 2
    while candidate.casefold() in used_names:
        candidate = f"{Path(name).stem}-{suffix}{Path(name).suffix}"
        suffix += 1
    used_names.add(candidate.casefold())
    return candidate


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _copy_attachments(target: Path, message_id: str, paths: list[Path]) -> list[dict[str, Any]]:
    if not paths:
        return []
    destination_dir = target / "attachments" / message_id
    destination_dir.mkdir(parents=True, exist_ok=False)
    attachments: list[dict[str, Any]] = []
    used_names: set[str] = set()
    for source in paths:
        resolved = source.expanduser().resolve(strict=True)
        if not resolved.is_file():
            raise ValueError(f"attachment is not a file: {source}")
        name = _safe_attachment_name(resolved, used_names)
        destination = destination_dir / name
        shutil.copyfile(resolved, destination)
        mime_type = mimetypes.guess_type(name)[0] or "application/octet-stream"
        attachments.append(
            {
                "path": str(destination),
                "name": name,
                "mime_type": mime_type,
                "size": destination.stat().st_size,
                "sha256": _sha256(destination),
            }
        )
    return attachments


def send(
    recipient: str,
    text: str,
    *,
    sender: str = DEFAULT_SENDER,
    message_type: str = "message",
    metadata: dict[str, Any] | None = None,
    extra_fields: dict[str, Any] | None = None,
    attachments: list[Path] | None = None,
    channel_id: str | None = None,
    channel_type: str | None = None,
    source_id: str | None = None,
    thread_id: str | None = None,
    root_id: str | None = None,
    root: Path | None = None,
) -> dict[str, Any]:
    target = root or mailbox_dir()
    target.mkdir(parents=True, exist_ok=True)
    message_id = str(uuid.uuid4())
    record: dict[str, Any] = {
        "id": message_id,
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "from": sender,
        "to": recipient,
        "type": message_type,
        "text": text,
    }
    if metadata is not None:
        record["metadata"] = metadata
    if extra_fields:
        record.update(extra_fields)
    routing_context = {
        "channel_id": channel_id,
        "channel_type": channel_type,
        "source_id": source_id,
        "thread_id": thread_id,
        "root_id": root_id,
    }
    record.update({key: value for key, value in routing_context.items() if value})
    copied_attachments = _copy_attachments(target, message_id, attachments or [])
    if copied_attachments:
        record["attachments"] = copied_attachments
    payload = (json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")
    fd = os.open(target / "messages.jsonl", os.O_APPEND | os.O_CREAT | os.O_WRONLY, 0o600)
    try:
        os.write(fd, payload)
    finally:
        os.close(fd)
    return record


def receive(recipient: str, *, root: Path | None = None) -> list[dict[str, Any]]:
    target = root or mailbox_dir()
    messages_path = target / "messages.jsonl"
    cursor_path = _cursor_path(target, recipient)
    start = _read_cursor(cursor_path)
    try:
        file_size = messages_path.stat().st_size
    except FileNotFoundError:
        return []
    if start > file_size:
        start = 0

    found: list[dict[str, Any]] = []
    committed_offset = start
    with messages_path.open("rb") as stream:
        stream.seek(start)
        while True:
            line_start = stream.tell()
            line = stream.readline()
            if not line:
                break
            if not line.endswith(b"\n"):
                committed_offset = line_start
                break
            committed_offset = stream.tell()
            try:
                record = json.loads(line.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                continue
            if isinstance(record, dict) and record.get("to") == recipient:
                found.append(record)

    if committed_offset != start or not cursor_path.exists():
        _write_cursor(cursor_path, committed_offset)
    return found


def _port_is_listening(port: int) -> bool:
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=0.25):
            return True
    except OSError:
        return False


def poll(
    recipient: str,
    *,
    interval_seconds: float = 30.0,
    max_checks: int = 10,
    required_ports: tuple[int, ...] = (),
    root: Path | None = None,
    sleep: Any = time.sleep,
    port_probe: Any = _port_is_listening,
) -> tuple[list[dict[str, Any]], list[int]]:
    """Poll until mail or a monitored listener failure ends the session."""
    if interval_seconds < 0:
        raise ValueError("interval_seconds must be non-negative")
    if max_checks < 1:
        raise ValueError("max_checks must be at least 1")

    for check in range(max_checks):
        if check:
            sleep(interval_seconds)
        found = receive(recipient, root=root)
        if found:
            return found, []
        missing_ports = [port for port in required_ports if not port_probe(port)]
        if missing_ports:
            return [], missing_ports
    return [], []


def status(*, root: Path | None = None) -> dict[str, Any]:
    target = root or mailbox_dir()
    path = target / "messages.jsonl"
    return {
        "directory": str(target),
        "messages_file": str(path),
        "size_bytes": path.stat().st_size if path.exists() else 0,
        "default_sender": DEFAULT_SENDER,
        "peers": list(PEERS),
    }


def _rest_request(method: str, path: str, payload: dict[str, Any] | None = None, *, base_url: str | None = None) -> Any:
    url = (base_url or os.environ.get(MAILBOX_URL_ENV) or DEFAULT_MAILBOX_URL).rstrip("/") + path
    encoded = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = urllib.request.Request(url, data=encoded, method=method)
    if encoded is not None:
        request.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(request, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))


def send_rest(
    recipient: str,
    text: str,
    *,
    sender: str = DEFAULT_SENDER,
    message_type: str = "message",
    attachments: list[Path] | None = None,
    channel_id: str | None = None,
    channel_type: str | None = None,
    source_id: str | None = None,
    thread_id: str | None = None,
    root_id: str | None = None,
    base_url: str | None = None,
) -> dict[str, Any]:
    payload = {
        "to": recipient,
        "text": text,
        "from": sender,
        "type": message_type,
        "attachments": [str(path.expanduser().resolve()) for path in (attachments or [])],
        "channel_id": channel_id,
        "channel_type": channel_type,
        "source_id": source_id,
        "thread_id": thread_id,
        "root_id": root_id,
    }
    return dict(_rest_request("POST", "/v1/messages", payload, base_url=base_url)["message"])


def receive_rest(recipient: str, *, base_url: str | None = None) -> list[dict[str, Any]]:
    query = urllib.parse.urlencode({"recipient": recipient})
    return list(_rest_request("GET", f"/v1/messages?{query}", base_url=base_url)["messages"])


def status_rest(*, base_url: str | None = None) -> dict[str, Any]:
    return dict(_rest_request("GET", "/v1/status", base_url=base_url))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    transport = parser.add_mutually_exclusive_group()
    transport.add_argument("--dir", type=Path, help="use this JSONL mailbox directory")
    transport.add_argument("--url", help=f"use REST instead of JSONL (default service: {DEFAULT_MAILBOX_URL})")
    commands = parser.add_subparsers(dest="command", required=True)
    send_parser = commands.add_parser("send", help="append a message")
    send_parser.add_argument("recipient")
    send_parser.add_argument("text")
    send_parser.add_argument("--sender", default=DEFAULT_SENDER)
    send_parser.add_argument("--type", dest="message_type", default="message")
    send_parser.add_argument("--channel-id")
    send_parser.add_argument("--channel-type")
    send_parser.add_argument("--source-id")
    send_parser.add_argument("--thread-id")
    send_parser.add_argument("--root-id")
    send_parser.add_argument(
        "--attach",
        action="append",
        default=[],
        type=Path,
        help="copy a file into this message (repeatable)",
    )
    receive_parser = commands.add_parser("receive", help="consume unread messages")
    receive_parser.add_argument("recipient")
    poll_parser = commands.add_parser("poll", help="poll for unread messages")
    poll_parser.add_argument("recipient")
    poll_parser.add_argument("--interval", type=float, default=30.0)
    poll_parser.add_argument("--checks", type=int, default=10)
    poll_parser.add_argument("--require-port", action="append", default=[], type=int)
    commands.add_parser("status", help="show mailbox configuration")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    configured_dir = os.environ.get(MAILBOX_ENV)
    mailbox_root = args.dir.expanduser().resolve() if args.dir else (
        Path(configured_dir).expanduser().resolve() if configured_dir else None
    )
    rest_url = args.url or (None if mailbox_root else os.environ.get(MAILBOX_URL_ENV))
    use_rest = bool(rest_url)
    if args.command == "send":
        print(
            json.dumps(
                (send_rest if use_rest else send)(
                    args.recipient,
                    args.text,
                    sender=args.sender,
                    message_type=args.message_type,
                    attachments=args.attach,
                    channel_id=args.channel_id,
                    channel_type=args.channel_type,
                    source_id=args.source_id,
                    thread_id=args.thread_id,
                    root_id=args.root_id,
                    **({"base_url": rest_url} if use_rest else {"root": mailbox_root}),
                ),
                ensure_ascii=False,
            )
        )
    elif args.command == "receive":
        records = receive_rest(args.recipient, base_url=rest_url) if use_rest else receive(args.recipient, root=mailbox_root)
        for record in records:
            print(json.dumps(record, ensure_ascii=False))
    elif args.command == "poll":
        if use_rest:
            records = []
            missing_ports = []
            for check in range(args.checks):
                if check:
                    time.sleep(args.interval)
                records = receive_rest(args.recipient, base_url=rest_url)
                if records:
                    break
                missing_ports = [port for port in args.require_port if not _port_is_listening(port)]
                if missing_ports:
                    break
        else:
            records, missing_ports = poll(
                args.recipient,
                interval_seconds=args.interval,
                max_checks=args.checks,
                required_ports=tuple(args.require_port),
                root=mailbox_root,
            )
        for record in records:
            print(json.dumps(record, ensure_ascii=False))
        if missing_ports:
            print(
                json.dumps({"error": "monitored_process_failure", "missing_ports": missing_ports}),
                file=sys.stderr,
            )
            return 2
    else:
        print(json.dumps(status_rest(base_url=rest_url) if use_rest else status(root=mailbox_root),
                         ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    canonical_client = (
        Path(__file__).resolve().parents[2]
        / "mailbox_channel"
        / "src"
        / "mailbox_channels"
        / "agent_mailbox.py"
    )
    if canonical_client.is_file() and canonical_client.resolve() != Path(__file__).resolve():
        runpy.run_path(str(canonical_client), run_name="__main__")
    else:
        sys.exit(main())
