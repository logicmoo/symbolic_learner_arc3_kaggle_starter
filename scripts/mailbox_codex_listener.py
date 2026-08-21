"""Codex mailbox worker glue (REST against the relay at :46667).

Implements the first cut of ``mailbox_channel/docs/WORKBENCH_CODEX_WORKER.md``:
register ``workbench-codex-worker`` (+ presence), give it a cursor on its own
mailbox and ``server_events``, and poll those together over REST. SNET Mattermost
channel subscriptions are a later addition.

The Codex-listener automation calls this on each tick. The agent *is* the
responder: a tick runs ``poll`` (usually in the background, bounded by a timer)
and either

* returns immediately with new messages so the agent starts reacting, or
* times out with ``status=idle`` so the agent resumes its previous work.

Everything goes through the relay REST API (default ``http://127.0.0.1:46667``);
no filesystem access. The relay owns delivery and per-cursor read state.

Commands: ``register`` · ``poll`` · ``send`` · ``ack`` · ``ensure`` · ``status``.
"""

from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Callable, Sequence

try:
    from mailbox_channels import agent_mailbox as _mailbox
except Exception:  # pragma: no cover - only when the client package is absent
    _mailbox = None

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_AGENT = "github-copilot-facilitator-agent"
DEFAULT_PRESENCE = "github-copilot-facilitator-agent-app"
DEFAULT_PEER = "symbolic-workbench-user"
# The shared channel both the workbench user and the agent post to; it is also the
# Chat page's default display channel.
SHARED_USER_CHANNEL = "symbolic-workbench-user"
EVENT_CHANNEL = "server_events"
RELAY_URL = os.environ.get("AGENT_MAILBOX_URL") or "http://127.0.0.1:46667"
API_BASE = os.environ.get("WORKBENCH_API_BASE", "http://127.0.0.1:8000")
RELAY_HOST = "127.0.0.1"
RELAY_PORT = 46667

# poll exit codes: the automation branches on these.
EXIT_MESSAGE = 0
EXIT_IDLE = 20
EXIT_ERROR = 2


def _require_client() -> Any:
    if _mailbox is None:
        raise RuntimeError("mailbox_channels client is not installed")
    return _mailbox


def default_sources(agent: str) -> list[str]:
    """The poll set for the chat loop.

    Includes the shared user channel, the agent's own mailbox, and
    ``server_events`` - lifecycle events are surfaced too so the agent can read
    them and decide whether to react. Only the agent's own posts are filtered out
    (to avoid reacting to itself); that decision lives in the poll, not here.
    """
    ordered = [SHARED_USER_CHANNEL, agent, EVENT_CHANNEL]
    seen: set[str] = set()
    result: list[str] = []
    for source in ordered:
        if source and source not in seen:
            seen.add(source)
            result.append(source)
    return result


def _project(record: dict[str, Any], *, source: str | None = None) -> dict[str, Any]:
    projected = {
        "id": record.get("id"),
        "timestamp": record.get("timestamp"),
        "from": record.get("from"),
        "to": record.get("to"),
        "text": record.get("text", ""),
        "type": record.get("type", "message"),
    }
    if source is not None:
        projected["source"] = source
    return projected


def register_worker(
    agent: str,
    *,
    presence: str,
    sources: Sequence[str],
    base_url: str = RELAY_URL,
    start: str = "now",
) -> dict[str, Any]:
    """Register the worker + presence and initialise its cursor on each source.

    Idempotent: an already-registered agent (the relay answers 400) is tolerated
    so re-runs still (re)initialise cursors, which is the part that matters when
    adding a new source to the poll set.
    """
    client = _require_client()
    try:
        registration: dict[str, Any] = client.register_agent_rest(agent, presence_id=presence, base_url=base_url)
    except Exception as error:
        registration = {"skipped": True, "reason": str(error)}
    cursors: list[dict[str, Any]] = []
    for source in sources:
        try:
            cursors.append(client.initialize_cursor_rest(source, cursor=agent, start=start, base_url=base_url))
        except Exception as error:
            cursors.append({"recipient": source, "error": str(error)})
    return {"agent": agent, "presence": presence, "registration": registration, "cursors": cursors}


def unread_across_sources(
    *,
    sources: Sequence[str],
    cursor: str,
    base_url: str = RELAY_URL,
    exclude_from: str | None = None,
    only_messages: bool = False,
) -> list[dict[str, Any]]:
    """Peek unread messages across every polled source without advancing cursors.

    ``exclude_from`` drops the agent's own posts (so a shared channel does not make
    it react to itself); ``only_messages`` keeps chat messages and drops relay
    lifecycle events so the chat interrupt is not tripped by them.
    """
    client = _require_client()
    messages: list[dict[str, Any]] = []
    for source in sources:
        for record in client.peek_rest(source, base_url=base_url, cursor=cursor):
            if record.get("audit_of"):
                continue
            if only_messages and record.get("type", "message") != "message":
                continue
            if exclude_from and record.get("from") == exclude_from:
                continue
            messages.append(_project(record, source=source))
    return messages


def poll_until(
    *,
    timeout: float,
    interval: float,
    peek: Callable[[], list[dict[str, Any]]],
    now: Callable[[], float] = time.monotonic,
    sleep: Callable[[float], None] = time.sleep,
) -> tuple[str, list[dict[str, Any]]]:
    """Block up to ``timeout`` seconds, returning on the first unread batch.

    Returns ("message", messages) as soon as anything is waiting, otherwise
    ("idle", []) when the timer expires. The first check happens immediately so a
    zero timeout behaves like a single instant check.
    """
    deadline = now() + max(0.0, timeout)
    while True:
        messages = peek()
        if messages:
            return "message", messages
        remaining = deadline - now()
        if remaining <= 0:
            return "idle", []
        sleep(min(max(0.1, interval), remaining))


def send_message(text: str, *, sender: str, recipient: str, base_url: str = RELAY_URL) -> dict[str, Any]:
    client = _require_client()
    if not text.strip():
        raise ValueError("message text must not be empty")
    return _project(client.send_rest(recipient, text, sender=sender, base_url=base_url))


def ack_messages(source: str, message_ids: Sequence[str], *, cursor: str, base_url: str = RELAY_URL) -> int:
    """Acknowledge handled message ids on a source so they stop being redelivered."""
    client = _require_client()
    acknowledged = 0
    for message_id in message_ids:
        if message_id and client.acknowledge_rest(source, message_id, base_url=base_url, cursor=cursor):
            acknowledged += 1
    return acknowledged


def port_open(host: str = RELAY_HOST, port: int = RELAY_PORT, timeout: float = 0.5) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _spawn_detached(command: Sequence[str], *, cwd: Path) -> int:
    flags = 0
    if os.name == "nt":
        flags = getattr(subprocess, "CREATE_NO_WINDOW", 0) | getattr(subprocess, "DETACHED_PROCESS", 0)
    process = subprocess.Popen(
        list(command),
        cwd=str(cwd),
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=flags,
    )
    return process.pid


def _relay_launcher() -> Path:
    return ROOT.parent / "mailbox_channel" / "mailbox-server.cmd"


def ensure_relay(
    *,
    check: Callable[[], bool] = port_open,
    spawn: Callable[[Sequence[str], Path], int] = lambda command, cwd: _spawn_detached(command, cwd=cwd),
) -> dict[str, Any]:
    """Make sure the mailbox relay (mailbox_server) is listening on :46667."""
    if check():
        return {"service": "channel-relay", "state": "running", "action": "none"}
    # Prefer the workbench service supervisor so the relay is tracked/reconciled.
    try:
        import urllib.request

        request = urllib.request.Request(
            f"{API_BASE}/api/system/services/channel-relay/start", method="POST"
        )
        with urllib.request.urlopen(request, timeout=5):
            return {"service": "channel-relay", "state": "starting", "action": "service-monitor"}
    except Exception:
        pass
    launcher = _relay_launcher()
    if not launcher.exists():
        return {"service": "channel-relay", "state": "down", "action": "missing-launcher", "launcher": str(launcher)}
    pid = spawn([str(launcher)], launcher.parent)
    return {"service": "channel-relay", "state": "starting", "action": "launched", "pid": pid}


def status_snapshot(agent: str, *, sources: Sequence[str], cursor: str, base_url: str = RELAY_URL) -> dict[str, Any]:
    relay_up = port_open()
    relay: dict[str, Any] = {}
    unread: list[dict[str, Any]] = []
    if relay_up and _mailbox is not None:
        try:
            relay = _mailbox.status_rest(base_url=base_url)
        except Exception:
            relay = {}
        try:
            unread = unread_across_sources(
                sources=sources, cursor=cursor, base_url=base_url, exclude_from=agent
            )
        except Exception:
            unread = []
    return {
        "agent": agent,
        "cursor": cursor,
        "sources": list(sources),
        "relayUrl": base_url,
        "relayUp": relay_up,
        "clientAvailable": _mailbox is not None,
        "unread": len(unread),
        "agents": relay.get("agents") if isinstance(relay, dict) else None,
    }


def _print(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False))


def _resolve_sources(args: argparse.Namespace) -> list[str]:
    if getattr(args, "sources", None):
        return [value.strip() for value in args.sources.split(",") if value.strip()]
    return default_sources(args.agent)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Codex mailbox worker glue (REST)")
    sub = parser.add_subparsers(dest="command", required=True)

    register = sub.add_parser("register", help="register the worker + presence and init cursors")
    register.add_argument("--agent", default=DEFAULT_AGENT)
    register.add_argument("--presence", default=DEFAULT_PRESENCE)
    register.add_argument("--sources", help="comma-separated poll sources (default: agent,server_events)")
    register.add_argument("--start", default="now", help="cursor start: now | beginning | 7d | UTC timestamp")
    register.add_argument("--base-url", default=RELAY_URL)

    poll = sub.add_parser("poll", help="bounded poll; returns on first message or timeout")
    poll.add_argument("--agent", default=DEFAULT_AGENT)
    poll.add_argument("--cursor", help="cursor name (default: agent)")
    poll.add_argument("--sources", help="comma-separated poll sources (default: agent,server_events)")
    poll.add_argument("--timeout", type=float, default=50.0)
    poll.add_argument("--interval", type=float, default=3.0)
    poll.add_argument("--base-url", default=RELAY_URL)
    poll.add_argument("--ensure", action="store_true", help="ensure the relay is up first")

    ensure = sub.add_parser("ensure", help="ensure the relay (mailbox_server) is running")

    send = sub.add_parser("send", help="send a reply from the worker to the user")
    send.add_argument("--text", help="reply text (reads stdin when omitted)")
    send.add_argument("--to", dest="recipient", default=DEFAULT_PEER)
    send.add_argument("--from", dest="sender", default=DEFAULT_AGENT)
    send.add_argument("--base-url", default=RELAY_URL)

    ack = sub.add_parser("ack", help="acknowledge handled message ids on a source")
    ack.add_argument("--agent", default=DEFAULT_AGENT)
    ack.add_argument("--cursor", help="cursor name (default: agent)")
    ack.add_argument("--source", help="source the ids came from (default: agent)")
    ack.add_argument("--ids", required=True, help="comma-separated message ids to acknowledge")
    ack.add_argument("--base-url", default=RELAY_URL)

    snapshot = sub.add_parser("status", help="relay + unread snapshot")
    snapshot.add_argument("--agent", default=DEFAULT_AGENT)
    snapshot.add_argument("--cursor", help="cursor name (default: agent)")
    snapshot.add_argument("--sources", help="comma-separated poll sources (default: agent,server_events)")
    snapshot.add_argument("--base-url", default=RELAY_URL)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "ensure":
        _print({"relay": ensure_relay()})
        return 0

    if args.command == "register":
        try:
            result = register_worker(
                args.agent,
                presence=args.presence,
                sources=_resolve_sources(args),
                base_url=args.base_url,
                start=args.start,
            )
        except Exception as error:
            _print({"status": "error", "error": str(error)})
            return EXIT_ERROR
        _print({"status": "registered", **result})
        return 0

    if args.command == "poll":
        cursor = args.cursor or args.agent
        sources = _resolve_sources(args)
        ensured = ensure_relay() if args.ensure else None
        try:
            state, messages = poll_until(
                timeout=args.timeout,
                interval=args.interval,
                peek=lambda: unread_across_sources(
                    sources=sources,
                    cursor=cursor,
                    base_url=args.base_url,
                    exclude_from=args.agent,
                ),
            )
        except Exception as error:
            _print({"status": "error", "error": str(error)})
            return EXIT_ERROR
        _print({
            "status": "message" if state == "message" else "idle",
            "resume": state == "idle",
            "count": len(messages),
            "messages": messages,
            "agent": args.agent,
            "cursor": cursor,
            "sources": sources,
            "relayUrl": args.base_url,
            **({"ensured": ensured} if ensured else {}),
        })
        return EXIT_MESSAGE if state == "message" else EXIT_IDLE

    if args.command == "send":
        text = args.text if args.text is not None else sys.stdin.read()
        try:
            record = send_message(text, sender=args.sender, recipient=args.recipient, base_url=args.base_url)
        except Exception as error:
            _print({"status": "error", "error": str(error)})
            return EXIT_ERROR
        _print({"status": "sent", "message": record})
        return 0

    if args.command == "ack":
        cursor = args.cursor or args.agent
        source = args.source or args.agent
        ids = [value.strip() for value in args.ids.split(",") if value.strip()]
        try:
            handled = ack_messages(source, ids, cursor=cursor, base_url=args.base_url)
        except Exception as error:
            _print({"status": "error", "error": str(error)})
            return EXIT_ERROR
        _print({"status": "acked", "handled": handled, "requested": len(ids), "source": source})
        return 0

    if args.command == "status":
        cursor = args.cursor or args.agent
        _print(status_snapshot(args.agent, sources=_resolve_sources(args), cursor=cursor, base_url=args.base_url))
        return 0

    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
