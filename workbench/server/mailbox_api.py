"""HTTP surface over the shared mailbox_channels client.

The workbench Chat page and its floatable mini-dock talk to the same append-only
JSONL mailbox that the CLI agents use (``mailbox_channel/mailbox/messages.jsonl``).
This router exposes three endpoints:

* ``GET  /mailbox/status``   - resolved mailbox directory + availability.
* ``GET  /mailbox/messages`` - the conversation thread between two participants
  (tail-read so it stays cheap as the shared log grows).
* ``POST /mailbox/send``     - append a message from the workbench user.

Reading the thread goes straight to the JSONL file (filtered by the participant
pair) rather than the cursor-based ``receive``/``peek`` helpers, because the chat
view needs both directions of the conversation and must not consume cursors.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Body, HTTPException, Query

try:  # The client ships as an installed package (mailbox_channel/src/mailbox_channels).
    from mailbox_channels import agent_mailbox as _mailbox_client
except Exception:  # pragma: no cover - exercised only when the package is absent.
    _mailbox_client = None

router = APIRouter()

# The workbench user and the agent they chat with. Both are overridable per request
# so the same UI can address other agents on the shared bus.
DEFAULT_USER_AGENT = "symbolic-workbench-user"
DEFAULT_PEER_AGENT = "github-copilot-facilitator-agent"

# Only read the tail of the shared log for the thread view; the file accumulates
# every agent's traffic and can be several megabytes.
MESSAGES_TAIL_BYTES = 512 * 1024


def resolve_mailbox_root() -> Path:
    """Return the mailbox directory, honouring the AGENT_MAILBOX_DIR override.

    Falls back to the sibling ``mailbox_channel/mailbox`` directory next to the
    repository root (matching run_channel_relay.bat and mailbox.system.metta).
    """

    configured = os.environ.get("AGENT_MAILBOX_DIR")
    if configured:
        return Path(configured).expanduser().resolve()
    repo_root = Path(__file__).resolve().parents[2]
    return (repo_root.parent / "mailbox_channel" / "mailbox").resolve()


def _project_record(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": record.get("id"),
        "timestamp": record.get("timestamp"),
        "from": record.get("from"),
        "to": record.get("to"),
        "text": record.get("text", ""),
        "type": record.get("type", "message"),
    }


def read_tail_records(messages_path: Path, max_bytes: int = MESSAGES_TAIL_BYTES) -> list[dict[str, Any]]:
    """Parse the last ``max_bytes`` of a JSONL mailbox file into records."""

    try:
        size = messages_path.stat().st_size
    except FileNotFoundError:
        return []
    with messages_path.open("rb") as stream:
        if size > max_bytes:
            stream.seek(size - max_bytes)
            stream.readline()  # discard the partial line at the seek boundary
        raw = stream.read()
    records: list[dict[str, Any]] = []
    for line in raw.split(b"\n"):
        if not line.strip():
            continue
        try:
            records.append(json.loads(line.decode("utf-8")))
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
    return records


def thread_messages(
    root: Path,
    user: str,
    peer: str,
    *,
    limit: int = 200,
    max_bytes: int = MESSAGES_TAIL_BYTES,
) -> list[dict[str, Any]]:
    """Return the direct conversation between ``user`` and ``peer``.

    Audit copies (records with an ``audit_of`` marker, written to the server's
    fan-out channels) are skipped so the thread shows each message once.
    """

    pair = {user, peer}
    thread = [
        _project_record(record)
        for record in read_tail_records(root / "messages.jsonl", max_bytes)
        if not record.get("audit_of")
        and record.get("from") in pair
        and record.get("to") in pair
    ]
    if limit and len(thread) > limit:
        thread = thread[-limit:]
    return thread


# The server's fan-out audit copies go to these pseudo-recipients; hide them from
# the channel picker and channel views.
AUDIT_CHANNEL_NAMES = {"agent_to_channel", "agent_to_agent"}


def channel_messages(
    root: Path,
    channel: str,
    *,
    limit: int = 200,
    max_bytes: int = MESSAGES_TAIL_BYTES,
) -> list[dict[str, Any]]:
    """Return every message that involves ``channel`` (as sender or recipient)."""

    thread = [
        _project_record(record)
        for record in read_tail_records(root / "messages.jsonl", max_bytes)
        if not record.get("audit_of")
        and (record.get("to") == channel or record.get("from") == channel)
    ]
    if limit and len(thread) > limit:
        thread = thread[-limit:]
    return thread


def list_channels(root: Path, *, max_bytes: int = MESSAGES_TAIL_BYTES) -> list[dict[str, Any]]:
    """List every mailbox/channel worth showing in the picker.

    Mailboxes are derived from the participants seen in recent traffic; retained
    relay channels are added from the relay status (best effort over REST). The
    two default identities are always present so the chat works on a fresh store.
    """

    participants: dict[str, int] = {}
    for record in read_tail_records(root / "messages.jsonl", max_bytes):
        if record.get("audit_of"):
            continue
        for key in ("to", "from"):
            value = record.get(key)
            if isinstance(value, str) and value and value not in AUDIT_CHANNEL_NAMES:
                participants[value] = participants.get(value, 0) + 1

    channels = [{"id": cid, "kind": "mailbox", "messages": count} for cid, count in participants.items()]
    known_ids = set(participants)

    if _mailbox_client is not None:
        try:
            status = _mailbox_client.status_rest()
            for cid in status.get("channels") or []:
                if isinstance(cid, str) and cid not in known_ids:
                    channels.append({"id": cid, "kind": "channel", "messages": 0})
                    known_ids.add(cid)
        except Exception:
            pass

    for default_id in (DEFAULT_PEER_AGENT, DEFAULT_USER_AGENT):
        if default_id not in known_ids:
            channels.append({"id": default_id, "kind": "mailbox", "messages": 0})
            known_ids.add(default_id)

    channels.sort(key=lambda item: (item["kind"] != "mailbox", -int(item["messages"]), item["id"]))
    return channels


@router.get("/mailbox/status")
def mailbox_status() -> dict[str, Any]:
    root = resolve_mailbox_root()
    messages_path = root / "messages.jsonl"
    return {
        "mailboxDir": str(root),
        "exists": root.exists(),
        "messagesFile": str(messages_path),
        "messagesBytes": messages_path.stat().st_size if messages_path.exists() else 0,
        "clientAvailable": _mailbox_client is not None,
        "defaultUser": DEFAULT_USER_AGENT,
        "defaultPeer": DEFAULT_PEER_AGENT,
    }


@router.get("/mailbox/channels")
def mailbox_channels() -> dict[str, Any]:
    root = resolve_mailbox_root()
    return {"channels": list_channels(root), "default": DEFAULT_PEER_AGENT}


@router.get("/mailbox/messages")
def mailbox_messages(
    user: str = Query(DEFAULT_USER_AGENT),
    peer: str = Query(DEFAULT_PEER_AGENT),
    channel: str | None = None,
    limit: int = Query(200, ge=1, le=2000),
) -> dict[str, Any]:
    root = resolve_mailbox_root()
    if channel:
        messages = channel_messages(root, channel, limit=limit)
    else:
        messages = thread_messages(root, user, peer, limit=limit)
    return {
        "messages": messages,
        "user": user,
        "peer": peer,
        "channel": channel,
        "mailboxDir": str(root),
    }


@router.post("/mailbox/send")
def mailbox_send(
    text: str = Body(..., embed=True),
    to: str = Body(DEFAULT_PEER_AGENT, embed=True),
    sender: str = Body(DEFAULT_USER_AGENT, embed=True),
) -> dict[str, Any]:
    if _mailbox_client is None:
        raise HTTPException(status_code=503, detail="mailbox_channels client is not installed")
    if not text.strip():
        raise HTTPException(status_code=400, detail="Message text must not be empty")
    root = resolve_mailbox_root()
    try:
        record = _mailbox_client.send(to, text, sender=sender, root=root)
    except Exception as error:  # surface send failures as a 500 with detail
        raise HTTPException(status_code=500, detail=f"Mailbox send failed: {error}") from error
    return {"message": _project_record(record)}
