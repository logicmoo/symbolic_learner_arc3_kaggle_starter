"""Minimal append-only JSONL mailbox shared by local agents."""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import os
import re
import shlex
import shutil
import socket
import sys
import threading
import time
import uuid
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from .attachment_storage import copy_file
except ImportError:  # Standalone copy downloaded from /agent_mailbox.py.
    def copy_file(root: Path, source: Path, destination: Path) -> None:
        maximum_file = int(os.environ.get("MAILBOX_RELAY_MAX_ATTACHMENT_BYTES", 1024 * 1024 * 1024))
        maximum_total = int(os.environ.get(
            "MAILBOX_RELAY_MAX_ATTACHMENT_STORAGE_BYTES", 25 * 1024 * 1024 * 1024,
        ))
        size = source.stat().st_size
        if size > maximum_file:
            raise ValueError(f"attachment is {size} bytes; maximum is {maximum_file} bytes")
        attachment_root = root / "attachments"
        used = sum(path.stat().st_size for path in attachment_root.rglob("*") if path.is_file())
        if used + size > maximum_total:
            raise ValueError(
                f"attachment storage quota exceeded: {used} + {size} bytes is greater than {maximum_total} bytes"
            )
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)


DEFAULT_SENDER = "local-agent"
PEERS = ("omegaclaw-core", "omegaclaw-min", "channel-relay")
MAILBOX_ENV = "AGENT_MAILBOX_DIR"
MAILBOX_URL_ENV = "AGENT_MAILBOX_URL"
MAILBOX_TOKEN_ENV = "AGENT_MAILBOX_TOKEN"
DEFAULT_MAILBOX_URL = "http://127.0.0.1:46667"
VERSION = "0.2.0"
REST_TIMEOUT = 15.0
REST_RETRIES = 0
REST_RETRY_DELAY = 1.0
REST_TOKEN: str | None = None
MAX_JSONL_ENV = "MAILBOX_RELAY_MAX_JSONL_BYTES"
DEFAULT_MAX_JSONL_BYTES = 5 * 1024 * 1024 * 1024
_MESSAGE_WRITE_LOCK = threading.Lock()
UNSAFE_FILENAME = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
GLOBAL_RUN_FIELDS = (
    "dir", "url", "mailbox", "config", "from", "format", "output", "timeout", "token",
    "curl", "input", "retry", "retry_delay", "quiet", "verbose", "nobuffer",
)
COMMAND_POSITIONALS = {
    "send": ("recipient", "text"),
    "receive": ("recipient",),
    "peek": ("recipient",),
    "poll": ("recipient",),
    "follow": ("recipient",),
    "unread-count": ("recipient",),
    "ack": ("recipient", "message_id"),
    "status": (),
    "check": (),
}


def default_mailbox_dir() -> Path:
    return Path.cwd() / "mailbox"


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
    try:
        for source in paths:
            resolved = source.expanduser().resolve(strict=True)
            if not resolved.is_file():
                raise ValueError(f"attachment is not a file: {source}")
            name = _safe_attachment_name(resolved, used_names)
            destination = destination_dir / name
            copy_file(target, resolved, destination)
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
    except Exception:
        shutil.rmtree(destination_dir, ignore_errors=True)
        raise
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
    messages_path = target / "messages.jsonl"
    maximum = int(os.environ.get(MAX_JSONL_ENV, DEFAULT_MAX_JSONL_BYTES))
    if maximum < 1:
        raise ValueError("JSONL mailbox size limit must be positive")
    with _MESSAGE_WRITE_LOCK:
        current = messages_path.stat().st_size if messages_path.exists() else 0
        if current + len(payload) > maximum:
            if copied_attachments:
                shutil.rmtree(target / "attachments" / message_id, ignore_errors=True)
            raise ValueError(
                f"JSONL mailbox quota exceeded: {current} + {len(payload)} bytes is greater than {maximum} bytes"
            )
        fd = os.open(messages_path, os.O_APPEND | os.O_CREAT | os.O_WRONLY, 0o600)
        try:
            os.write(fd, payload)
        finally:
            os.close(fd)
    return record


def receive(
    recipient: str,
    *,
    root: Path | None = None,
    advance: bool = True,
    cursor: str | None = None,
) -> list[dict[str, Any]]:
    target = root or mailbox_dir()
    messages_path = target / "messages.jsonl"
    cursor_path = _cursor_path(target, f"{recipient}:{cursor}" if cursor else recipient)
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

    if advance and (committed_offset != start or not cursor_path.exists()):
        _write_cursor(cursor_path, committed_offset)
    return found


def peek(recipient: str, *, root: Path | None = None, cursor: str | None = None) -> list[dict[str, Any]]:
    """Return unread messages without advancing the recipient cursor."""
    return receive(recipient, root=root, advance=False, cursor=cursor)


def acknowledge(recipient: str, message_id: str, *, root: Path | None = None,
                cursor: str | None = None) -> bool:
    target = root or mailbox_dir()
    messages_path = target / "messages.jsonl"
    try:
        with messages_path.open("rb") as stream:
            while line := stream.readline():
                try:
                    record = json.loads(line.decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError):
                    continue
                if record.get("to") == recipient and record.get("id") == message_id:
                    key = f"{recipient}:{cursor}" if cursor else recipient
                    _write_cursor(_cursor_path(target, key), stream.tell())
                    return True
    except FileNotFoundError:
        pass
    return False


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
    advance: bool = True,
    cursor: str | None = None,
    sleep: Any = time.sleep,
    port_probe: Any = _port_is_listening,
) -> tuple[list[dict[str, Any]], list[int]]:
    if interval_seconds < 0:
        raise ValueError("interval_seconds must be non-negative")
    if max_checks < 1:
        raise ValueError("max_checks must be at least 1")
    for check in range(max_checks):
        if check:
            sleep(interval_seconds)
        found = receive(recipient, root=root, advance=advance, cursor=cursor)
        if found:
            return found, []
        missing = [port for port in required_ports if not port_probe(port)]
        if missing:
            return [], missing
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
    token = REST_TOKEN or os.environ.get(MAILBOX_TOKEN_ENV)
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    if encoded is not None:
        request.add_header("Content-Type", "application/json")
    for attempt in range(REST_RETRIES + 1):
        try:
            with urllib.request.urlopen(request, timeout=REST_TIMEOUT) as response:
                return json.loads(response.read().decode("utf-8"))
        except (OSError, urllib.error.URLError):
            if attempt >= REST_RETRIES:
                raise
            time.sleep(REST_RETRY_DELAY)
    raise RuntimeError("REST request exhausted retries")


def send_rest(recipient: str, text: str, *, sender: str = DEFAULT_SENDER, message_type: str = "message",
              attachments: list[Path] | None = None, channel_id: str | None = None,
              channel_type: str | None = None, source_id: str | None = None,
              thread_id: str | None = None, root_id: str | None = None,
              base_url: str | None = None) -> dict[str, Any]:
    payload = {"to": recipient, "text": text, "from": sender, "type": message_type,
               "attachments": [str(path.expanduser().resolve()) for path in (attachments or [])],
               "channel_id": channel_id, "channel_type": channel_type, "source_id": source_id,
               "thread_id": thread_id, "root_id": root_id}
    return dict(_rest_request("POST", "/v1/messages", payload, base_url=base_url)["message"])


def receive_rest(
    recipient: str,
    *,
    base_url: str | None = None,
    advance: bool = True,
    cursor: str | None = None,
) -> list[dict[str, Any]]:
    query = urllib.parse.urlencode({"recipient": recipient, "advance": str(advance).lower(),
                                    "cursor": cursor or ""})
    return list(_rest_request("GET", f"/v1/messages?{query}", base_url=base_url)["messages"])


def peek_rest(recipient: str, *, base_url: str | None = None,
              cursor: str | None = None) -> list[dict[str, Any]]:
    return receive_rest(recipient, base_url=base_url, advance=False, cursor=cursor)


def acknowledge_rest(recipient: str, message_id: str, *, base_url: str | None = None,
                     cursor: str | None = None) -> bool:
    result = _rest_request("POST", "/v1/ack", {"recipient": recipient, "message_id": message_id,
                                                "cursor": cursor}, base_url=base_url)
    return bool(result.get("acknowledged"))


def status_rest(*, base_url: str | None = None) -> dict[str, Any]:
    return dict(_rest_request("GET", "/v1/status", base_url=base_url))


def default_config_path() -> Path:
    return Path.cwd() / "config" / "mailboxes.json"


def named_mailbox(name: str, path: Path | None = None) -> tuple[Path | None, str | None]:
    config_path = (path or default_config_path()).expanduser().resolve()
    try:
        document = json.loads(config_path.read_text(encoding="utf-8"))
        entry = document["mailboxes"][name]
    except FileNotFoundError as error:
        raise ValueError(f"mailbox config not found: {config_path}") from error
    except (KeyError, TypeError, json.JSONDecodeError) as error:
        raise ValueError(f"named mailbox not found or invalid: {name}") from error
    if isinstance(entry, str):
        entry = {"url": entry} if entry.startswith(("http://", "https://")) else {"dir": entry}
    if not isinstance(entry, dict) or bool(entry.get("dir")) == bool(entry.get("url")):
        raise ValueError(f"mailbox {name!r} must define exactly one of 'dir' or 'url'")
    if entry.get("url"):
        return None, str(entry["url"])
    directory = Path(str(entry["dir"])).expanduser()
    if not directory.is_absolute():
        directory = config_path.parent / directory
    return directory.resolve(), None


def _where_filters(values: list[str]) -> dict[str, str]:
    filters: dict[str, str] = {}
    for value in values:
        key, separator, expected = value.partition("=")
        if not separator or not key.strip():
            raise ValueError(f"invalid --where filter: {value!r}; expected FIELD=VALUE")
        filters[key.strip()] = expected
    return filters


def _select_records(records: list[dict[str, Any]], *, since: str | None = None,
                    limit: int | None = None, where: list[str] | None = None) -> list[dict[str, Any]]:
    filters = _where_filters(where or [])
    selected: list[dict[str, Any]] = []
    after_id = since is None
    for record in records:
        if since and not after_id:
            if record.get("id") == since:
                after_id = True
                continue
            if str(record.get("timestamp", "")) <= since:
                continue
            after_id = True
        if all(str(record.get(key, "")) == expected for key, expected in filters.items()):
            selected.append(record)
            if limit is not None and len(selected) >= limit:
                break
    return selected


def _render_text_record(item: dict[str, Any]) -> str:
    line = f"[{item.get('timestamp', '')}] {item.get('from', '')}: {item.get('text', '')}"
    if item.get("type") != "chat_server_status":
        return line
    context = item.get("service_context") if isinstance(item.get("service_context"), dict) else {}
    diagnostic = item.get("diagnostic") if isinstance(item.get("diagnostic"), dict) else {}
    details = [
        f"adapter={item.get('adapter') or context.get('adapter') or item.get('channel_type', '')}",
        f"state={item.get('connection_state', '')}",
    ]
    if context.get("listener_ids"):
        details.append(f"listeners={','.join(map(str, context['listener_ids']))}")
    if context.get("channel_ids"):
        details.append(f"channels={','.join(map(str, context['channel_ids']))}")
    if diagnostic:
        details.append(f"operation={diagnostic.get('operation', '')}")
        details.append(f"error={diagnostic.get('error_type', '')}: {diagnostic.get('error_message', '')}")
        details.append(f"will_retry={str(bool(diagnostic.get('will_retry'))).lower()}")
    return f"{line}\n  {'; '.join(details)}"


def _render_records(records: list[dict[str, Any]], output_format: str) -> str:
    if output_format == "json":
        return json.dumps(records, ensure_ascii=False, indent=2)
    if output_format == "text":
        return "\n".join(_render_text_record(item) for item in records)
    return "\n".join(json.dumps(item, ensure_ascii=False) for item in records)


def _emit(text: str, *, output: Path | None, quiet: bool, append: bool = False) -> None:
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("a" if append else "w", encoding="utf-8") as stream:
            if text:
                stream.write(text + "\n")
    if text and not quiet:
        print(text, flush=True)


def _add_read_options(parser: argparse.ArgumentParser, *, waiting: bool = True) -> None:
    parser.add_argument("--cursor", help="independent cursor name")
    parser.add_argument("--since", help="only return records after a timestamp or message ID")
    parser.add_argument("--limit", type=int, help="maximum records to return")
    parser.add_argument("--where", action="append", default=[], metavar="FIELD=VALUE",
                        help="filter by an envelope field; repeatable")
    parser.add_argument("--no-advance", action="store_true", help="do not advance the cursor")
    if waiting:
        parser.add_argument("--wait", type=float, default=0.0, help="wait up to this many seconds for mail")


def curl_command(args: argparse.Namespace, base_url: str, *, token: bool) -> str:
    base = base_url.rstrip("/")
    method = "GET"
    payload: dict[str, Any] | None = None
    if args.command in {"status", "check"}:
        url = f"{base}/v1/status"
    elif args.command == "send":
        url = f"{base}/v1/messages"
        method = "POST"
        payload = {
            "to": args.recipient, "text": args.text,
            "from": args.sender or args.global_sender or DEFAULT_SENDER,
            "type": args.message_type, "attachments": [str(path.resolve()) for path in args.attach],
            "channel_id": args.channel_id, "channel_type": args.channel_type,
            "source_id": args.source_id, "thread_id": args.thread_id, "root_id": args.root_id,
        }
    elif args.command == "ack" or (args.command == "receive" and args.ack):
        url = f"{base}/v1/ack"
        method = "POST"
        payload = {"recipient": args.recipient,
                   "message_id": args.message_id if args.command == "ack" else args.ack,
                   "cursor": args.cursor}
    else:
        advance = args.command not in {"peek", "unread-count"} and not getattr(args, "no_advance", False)
        query = urllib.parse.urlencode({"recipient": args.recipient, "advance": str(advance).lower(),
                                        "cursor": getattr(args, "cursor", None) or ""})
        url = f"{base}/v1/messages?{query}"
    parts = ["curl", "-sS", "-X", method]
    if token:
        parts.extend(["-H", "Authorization: Bearer <REDACTED_TOKEN>"])
    if payload is not None:
        parts.extend(["-H", "Content-Type: application/json", "--data", json.dumps(payload, ensure_ascii=False)])
    parts.append(url)
    return " ".join(shlex.quote(part) for part in parts)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agent-mailbox",
        description=__doc__,
        epilog="Use 'agent-mailbox COMMAND --help' for command-specific options. Global options may appear before or after COMMAND; -- stops option processing.",
    )
    parser.add_argument("--run", type=Path, metavar="COMMAND.json",
                        help="execute the entire command from a JSON document")
    transport = parser.add_mutually_exclusive_group()
    transport.add_argument("--dir", type=Path, help="use this JSONL mailbox directory")
    transport.add_argument("--url", help=f"use REST instead of JSONL (default service: {DEFAULT_MAILBOX_URL})")
    transport.add_argument("--mailbox", help="use a named mailbox from the mailbox config")
    parser.add_argument("--config", type=Path, help="mailbox configuration file")
    parser.add_argument("--from", dest="global_sender", help="default sender identity")
    parser.add_argument("--to", dest="global_recipient", help="send destination identity")
    parser.add_argument("--format", choices=("jsonl", "json", "text"), default="jsonl",
                        help="output rendering format (default: jsonl)")
    parser.add_argument("--output", type=Path, help="write rendered output to this file instead of stdout")
    parser.add_argument("--timeout", type=float, default=15.0, help="REST request timeout in seconds")
    parser.add_argument("--token", help=f"REST Bearer token (or {MAILBOX_TOKEN_ENV})")
    parser.add_argument("--curl", action="store_true",
                        help="print the equivalent REST curl command without executing it")
    parser.add_argument(
        "--input", dest="input_file", type=Path,
        help="read send message text from a UTF-8 file",
    )
    parser.add_argument("--retry", type=int, default=0, help="number of REST retries")
    parser.add_argument("--retry-delay", type=float, default=1.0, help="delay between REST retries")
    parser.add_argument("--quiet", action="store_true", help="suppress normal rendered output")
    parser.add_argument("--verbose", action="store_true", help="report selected transport and target")
    parser.add_argument("--nobuffer", action="store_true",
                        help="write stdout and stderr immediately without block buffering")
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    commands = parser.add_subparsers(dest="command", required=True, metavar="COMMAND")
    send_parser = commands.add_parser(
        "send", help="append a message", description="Append one durable mailbox message.",
        epilog="Example: agent-mailbox send agent-beta 'Task complete' --type result",
    )
    send_parser.add_argument("recipient", nargs="?", help="destination identity; alternatively use --to")
    send_parser.add_argument("text", nargs="?", help="message text; alternatively use global --input PATH")
    send_parser.add_argument("--sender", help="sender identity overriding global --from")
    send_parser.add_argument("--type", dest="message_type", default="message",
                             help="mailbox message type (default: message)")
    send_parser.add_argument("--channel-id", help="external channel or conversation identifier")
    send_parser.add_argument("--channel-type", help="external adapter type, such as telegram or slack")
    send_parser.add_argument("--source-id", help="source platform message/event identifier")
    send_parser.add_argument("--thread-id", help="source or destination thread identifier")
    send_parser.add_argument("--root-id", help="root message identifier for threaded transports")
    send_parser.add_argument(
        "--attach",
        action="append",
        default=[],
        type=Path,
        help="copy a file into this message (repeatable)",
    )
    receive_parser = commands.add_parser(
        "receive", help="consume unread messages",
        description="Read unread messages and advance the selected durable cursor.",
        epilog="Example: agent-mailbox receive worker-1 --limit 10 --where type=result",
    )
    receive_parser.add_argument("recipient", help="mailbox identity whose unread messages are consumed")
    _add_read_options(receive_parser)
    receive_parser.add_argument("--ack", metavar="MESSAGE_ID", help="acknowledge through this message ID")
    peek_parser = commands.add_parser(
        "peek", help="show unread messages without advancing the cursor",
        description="Inspect unread messages without changing any cursor.",
        epilog="Example: agent-mailbox peek worker-1 --cursor audit --limit 20",
    )
    peek_parser.add_argument("recipient", help="mailbox identity to inspect")
    _add_read_options(peek_parser, waiting=False)
    poll_parser = commands.add_parser(
        "poll", help="poll for unread messages",
        description="Check repeatedly until mail arrives or the bounded check count is exhausted.",
        epilog="Example: agent-mailbox poll worker-1 --interval 5 --checks 12 --nobuffer",
    )
    poll_parser.add_argument("recipient", help="mailbox identity to poll")
    poll_parser.add_argument("--interval", type=float, default=30.0,
                             help="seconds between checks (default: 30)")
    poll_parser.add_argument("--checks", type=int, default=10,
                             help="maximum checks before exiting (default: 10)")
    poll_parser.add_argument("--require-port", action="append", default=[], type=int,
                             help="fail when this local TCP port stops listening; repeatable")
    _add_read_options(poll_parser, waiting=False)
    follow_parser = commands.add_parser(
        "follow", help="continuously stream incoming messages",
        description="Continuously read new messages, advancing the selected cursor as they arrive.",
        epilog="Example: agent-mailbox follow worker-1 --interval 1 --nobuffer",
    )
    follow_parser.add_argument("recipient", help="mailbox identity to follow")
    follow_parser.add_argument("--interval", type=float, default=1.0,
                               help="seconds between checks (default: 1)")
    follow_parser.add_argument("--require-port", action="append", default=[], type=int,
                               help="exit when this local TCP port stops listening; repeatable")
    _add_read_options(follow_parser, waiting=False)
    unread_parser = commands.add_parser(
        "unread-count", help="count unread messages without consuming them",
        description="Count unread messages without advancing the selected cursor.",
        epilog="Example: agent-mailbox unread-count worker-1 --cursor monitor",
    )
    unread_parser.add_argument("recipient", help="mailbox identity whose unread messages are counted")
    unread_parser.add_argument("--cursor", help="independent cursor name")
    ack_parser = commands.add_parser(
        "ack", help="advance a cursor through a specific message",
        description="Explicitly acknowledge through a message ID on a durable cursor.",
        epilog="Example: agent-mailbox ack worker-1 MESSAGE_ID --cursor audit",
    )
    ack_parser.add_argument("recipient", help="mailbox identity owning the cursor")
    ack_parser.add_argument("message_id", help="message ID through which the cursor advances")
    ack_parser.add_argument("--cursor", help="independent cursor name")
    commands.add_parser(
        "status", help="show mailbox configuration",
        description="Show the selected mailbox or REST service status without consuming messages.",
        epilog="Example: agent-mailbox --url http://127.0.0.1:46667 status",
    )
    commands.add_parser(
        "check", help="validate mailbox access without consuming messages",
        description="Validate mailbox access and report a nonzero exit status on failure.",
        epilog="Example: agent-mailbox --url http://127.0.0.1:46667 check",
    )
    return parser


def _option_arguments(name: str, value: Any) -> list[str]:
    option = f"--{name.replace('_', '-')}"
    if isinstance(value, bool):
        return [option] if value else []
    if isinstance(value, list):
        result: list[str] = []
        for item in value:
            result.extend([option, str(item)])
        return result
    if value is None:
        return []
    return [option, str(value)]


def _command_document_argv(document: Any) -> list[str]:
    if isinstance(document, list):
        if not all(isinstance(item, str) for item in document):
            raise ValueError("command JSON array must contain only strings")
        return list(document)
    if not isinstance(document, dict):
        raise ValueError("command JSON must be an object, string array, or object containing args")
    if "args" in document:
        if set(document) != {"args"}:
            raise ValueError("a command document containing args cannot contain other fields")
        return _command_document_argv(document["args"])
    command = str(document.get("command") or "").strip()
    if command not in COMMAND_POSITIONALS:
        raise ValueError(f"unknown or missing command: {command or '<empty>'}")
    known_positionals = COMMAND_POSITIONALS[command]
    known_fields = {"command", "to", *GLOBAL_RUN_FIELDS, *known_positionals}
    command_fields = set(document) - known_fields
    command_options = {
        "sender", "type", "channel_id", "channel_type", "source_id", "thread_id", "root_id",
        "attach", "cursor", "ack", "interval", "checks", "require_port", "wait", "limit",
        "contains", "message_type", "no_advance",
    }
    unknown = command_fields - command_options
    if unknown:
        raise ValueError(f"unknown command document fields: {', '.join(sorted(unknown))}")
    arguments: list[str] = []
    for name in GLOBAL_RUN_FIELDS:
        if name in document:
            arguments.extend(_option_arguments(name, document[name]))
    arguments.append(command)
    for name in known_positionals:
        if name == "text":
            continue
        if command == "send" and name == "recipient" and "to" in document:
            if "recipient" in document:
                raise ValueError("send command document accepts either to or recipient, not both")
            arguments.extend(["--to", str(document["to"])])
            continue
        if name not in document:
            raise ValueError(f"{command} command document requires {name}")
        arguments.append(str(document[name]))
    for name in sorted(command_fields):
        arguments.extend(_option_arguments(name, document[name]))
    if "text" in known_positionals and document.get("text") is not None:
        arguments.extend(["--", str(document["text"])])
    return arguments


def _expand_run_document(argv: list[str]) -> list[str]:
    boundary = argv.index("--") if "--" in argv else len(argv)
    active = argv[:boundary]
    matches = [index for index, value in enumerate(active) if value == "--run" or value.startswith("--run=")]
    if not matches:
        return argv
    if len(matches) != 1:
        raise ValueError("--run may be specified only once")
    index = matches[0]
    if active[index] == "--run":
        if index + 1 >= len(active):
            raise ValueError("--run requires a JSON file")
        path_text = active[index + 1]
        consumed = {index, index + 1}
    else:
        path_text = active[index].partition("=")[2]
        consumed = {index}
    if any(position not in consumed for position in range(len(active))) or boundary != len(argv):
        raise ValueError("--run defines the entire command and cannot be combined with other arguments")
    path = Path(path_text).expanduser()
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot load --run command document: {error}") from error
    return _command_document_argv(document)


def _normalize_anywhere_flags(argv: list[str]) -> list[str]:
    """Move position-independent global options ahead of the subcommand."""
    boundary = argv.index("--") if "--" in argv else len(argv)
    options, literal_arguments = argv[:boundary], argv[boundary:]
    curl_requested = "--curl" in options
    nobuffer_requested = "--nobuffer" in options
    normalized: list[str] = []
    input_option: list[str] = []
    to_option: list[str] = []
    index = 0
    while index < len(options):
        argument = options[index]
        if argument in {"--curl", "--nobuffer"}:
            index += 1
            continue
        if argument == "--input":
            if index + 1 >= len(options):
                normalized.append(argument)
                index += 1
                continue
            input_option = [argument, options[index + 1]]
            index += 2
            continue
        if argument == "--to":
            if index + 1 >= len(options):
                normalized.append(argument)
                index += 1
                continue
            to_option = [argument, options[index + 1]]
            index += 2
            continue
        if argument.startswith("--to="):
            to_option = [argument]
            index += 1
            continue
        if argument.startswith("--input="):
            input_option = [argument]
            index += 1
            continue
        normalized.append(argument)
        index += 1
    leading = (["--curl"] if curl_requested else []) + (["--nobuffer"] if nobuffer_requested else [])
    return leading + input_option + to_option + normalized + literal_arguments


def _enable_unbuffered_output() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(line_buffering=True, write_through=True)


def main(argv: list[str] | None = None) -> int:
    global REST_TIMEOUT, REST_RETRIES, REST_RETRY_DELAY, REST_TOKEN
    supplied = list(sys.argv[1:] if argv is None else argv)
    try:
        supplied = _expand_run_document(supplied)
    except ValueError as error:
        build_parser().error(str(error))
    args = build_parser().parse_args(_normalize_anywhere_flags(supplied))
    if args.nobuffer:
        _enable_unbuffered_output()
    if args.command != "send" and args.input_file:
        build_parser().error("--input is only valid with send")
    if args.command == "send":
        if args.global_recipient and args.recipient:
            if args.text is not None:
                build_parser().error("send accepts either positional recipient or --to, not both")
            args.text, args.recipient = args.recipient, None
        args.recipient = args.global_recipient or args.recipient
        if not args.recipient:
            build_parser().error("send requires positional recipient or --to RECIPIENT")
        if args.input_file and args.text is not None:
            build_parser().error("send accepts either inline text or --input, not both")
        if args.input_file:
            try:
                args.text = args.input_file.expanduser().read_text(encoding="utf-8")
            except OSError as error:
                build_parser().error(f"cannot read --input: {error}")
        if args.text is None:
            build_parser().error("send requires inline text or --input PATH")
    elif args.global_recipient:
        build_parser().error("--to is only valid with send")
    if args.timeout <= 0 or args.retry < 0 or args.retry_delay < 0:
        build_parser().error("--timeout must be positive; retry values must be non-negative")
    REST_TIMEOUT, REST_RETRIES, REST_RETRY_DELAY = args.timeout, args.retry, args.retry_delay
    REST_TOKEN = args.token or os.environ.get(MAILBOX_TOKEN_ENV)
    configured_dir = os.environ.get(MAILBOX_ENV)
    if args.mailbox:
        try:
            mailbox_root, rest_url = named_mailbox(args.mailbox, args.config)
        except ValueError as error:
            build_parser().error(str(error))
    else:
        mailbox_root = args.dir.expanduser().resolve() if args.dir else (
            Path(configured_dir).expanduser().resolve() if configured_dir else None
        )
        rest_url = args.url or (None if mailbox_root else os.environ.get(MAILBOX_URL_ENV))
    use_rest = bool(rest_url)
    if args.curl:
        if not use_rest:
            build_parser().error("--curl requires a REST transport selected by --url, --mailbox, or AGENT_MAILBOX_URL")
        print(curl_command(args, str(rest_url), token=bool(REST_TOKEN)))
        return 0
    if args.verbose:
        target = rest_url if use_rest else str(mailbox_root or mailbox_dir())
        print(f"agent_mailbox transport={'REST' if use_rest else 'JSONL'} target={target}", file=sys.stderr)
    if args.command == "send":
        record = (
                (send_rest if use_rest else send)(
                    args.recipient,
                    args.text,
                    sender=args.sender or args.global_sender or DEFAULT_SENDER,
                    message_type=args.message_type,
                    attachments=args.attach,
                    channel_id=args.channel_id,
                    channel_type=args.channel_type,
                    source_id=args.source_id,
                    thread_id=args.thread_id,
                    root_id=args.root_id,
                    **({"base_url": rest_url} if use_rest else {"root": mailbox_root}),
                )
        )
        _emit(_render_records([record], args.format), output=args.output, quiet=args.quiet)
    elif args.command in {"receive", "peek"}:
        if args.command == "receive" and args.ack:
            acknowledged = (acknowledge_rest(args.recipient, args.ack, base_url=rest_url, cursor=args.cursor)
                            if use_rest else acknowledge(args.recipient, args.ack, root=mailbox_root,
                                                         cursor=args.cursor))
            _emit(json.dumps({"acknowledged": acknowledged}), output=args.output, quiet=args.quiet)
            return 0 if acknowledged else 1
        advance = args.command == "receive" and not args.no_advance
        deadline = time.monotonic() + max(0.0, getattr(args, "wait", 0.0))
        while True:
            records = (receive_rest(args.recipient, base_url=rest_url, advance=advance, cursor=args.cursor)
                       if use_rest else receive(args.recipient, root=mailbox_root, advance=advance,
                                                cursor=args.cursor))
            if records or time.monotonic() >= deadline:
                break
            time.sleep(min(0.25, max(0.0, deadline - time.monotonic())))
        records = _select_records(records, since=args.since, limit=args.limit, where=args.where)
        _emit(_render_records(records, args.format), output=args.output, quiet=args.quiet)
    elif args.command == "poll":
        if use_rest:
            records, missing_ports = [], []
            for check in range(args.checks):
                if check:
                    time.sleep(args.interval)
                records = receive_rest(args.recipient, base_url=rest_url,
                                       advance=not args.no_advance, cursor=args.cursor)
                if records:
                    break
                missing_ports = [port for port in args.require_port if not _port_is_listening(port)]
                if missing_ports:
                    break
        else:
            records, missing_ports = poll(args.recipient, interval_seconds=args.interval,
                                          max_checks=args.checks, required_ports=tuple(args.require_port),
                                          root=mailbox_root, advance=not args.no_advance,
                                          cursor=args.cursor)
        records = _select_records(records, since=args.since, limit=args.limit, where=args.where)
        _emit(_render_records(records, args.format), output=args.output, quiet=args.quiet)
        if missing_ports:
            print(json.dumps({"error": "monitored_process_failure", "missing_ports": missing_ports}), file=sys.stderr)
            return 2
    elif args.command == "follow":
        if args.interval < 0:
            raise ValueError("interval must be non-negative")
        seen_without_advance: set[str] = set()
        try:
            while True:
                records = (receive_rest(args.recipient, base_url=rest_url,
                                        advance=not args.no_advance, cursor=args.cursor) if use_rest
                           else receive(args.recipient, root=mailbox_root,
                                        advance=not args.no_advance, cursor=args.cursor))
                records = _select_records(records, since=args.since, limit=args.limit, where=args.where)
                if args.no_advance:
                    records = [record for record in records if str(record.get("id")) not in seen_without_advance]
                    seen_without_advance.update(str(record.get("id")) for record in records)
                _emit(_render_records(records, args.format), output=args.output, quiet=args.quiet, append=True)
                missing_ports = [port for port in args.require_port if not _port_is_listening(port)]
                if missing_ports:
                    print(json.dumps({"error": "monitored_process_failure", "missing_ports": missing_ports}),
                          file=sys.stderr)
                    return 2
                time.sleep(args.interval)
        except KeyboardInterrupt:
            return 0
    elif args.command == "unread-count":
        records = (peek_rest(args.recipient, base_url=rest_url, cursor=args.cursor) if use_rest
                   else peek(args.recipient, root=mailbox_root, cursor=args.cursor))
        _emit(str(len(records)), output=args.output, quiet=args.quiet)
    elif args.command == "ack":
        acknowledged = (acknowledge_rest(args.recipient, args.message_id, base_url=rest_url,
                                         cursor=args.cursor) if use_rest
                        else acknowledge(args.recipient, args.message_id, root=mailbox_root,
                                         cursor=args.cursor))
        _emit(json.dumps({"acknowledged": acknowledged}), output=args.output, quiet=args.quiet)
        return 0 if acknowledged else 1
    else:
        result = status_rest(base_url=rest_url) if use_rest else status(root=mailbox_root)
        if args.command == "check":
            result = {"ok": True, "transport": "rest" if use_rest else "jsonl", **result}
        _emit(json.dumps(result, ensure_ascii=False, indent=2), output=args.output, quiet=args.quiet)
    return 0


if __name__ == "__main__":
    sys.exit(main())
