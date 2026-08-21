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
import urllib.parse
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
        "channelId": record.get("channel_id"),
        "author": record.get("author"),
        "channelName": record.get("channel_name"),
        "raw": record,
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
        and (
            record.get("to") == channel
            or record.get("from") == channel
            or record.get("channel_id") == channel
        )
    ]
    if limit and len(thread) > limit:
        thread = thread[-limit:]
    return thread


def list_channels(root: Path, *, max_bytes: int = MESSAGES_TAIL_BYTES) -> list[dict[str, Any]]:
    """List every mailbox/channel worth showing in the pickers.

    Merges the relay registry (authoritative: agent mailboxes + retained
    channels) with participants seen in recent traffic, so the combos are
    populated with every possibility. Message counts come from recent traffic.
    """

    participants: dict[str, int] = {}
    for record in read_tail_records(root / "messages.jsonl", max_bytes):
        if record.get("audit_of"):
            continue
        for key in ("to", "from"):
            value = record.get(key)
            if isinstance(value, str) and value and value not in AUDIT_CHANNEL_NAMES:
                participants[value] = participants.get(value, 0) + 1

    channels: dict[str, dict[str, Any]] = {}

    def add(cid: Any, kind: str) -> None:
        if not isinstance(cid, str) or not cid or cid in AUDIT_CHANNEL_NAMES or cid in channels:
            return
        channels[cid] = {"id": cid, "kind": kind, "messages": participants.get(cid, 0)}

    if _mailbox_client is not None:
        try:
            registry = _mailbox_client._rest_request("GET", "/v1/registry")
            for agent in registry.get("agents", []):
                add(agent.get("mailbox") or agent.get("agent_id"), "mailbox")
            for channel in registry.get("channels", []):
                add(channel.get("id"), str(channel.get("channel_type") or "channel"))
        except Exception:
            pass

    for participant in participants:
        add(participant, "mailbox")
    for default_id in (DEFAULT_PEER_AGENT, DEFAULT_USER_AGENT):
        add(default_id, "mailbox")

    result = list(channels.values())
    result.sort(key=lambda item: (item["kind"] != "mailbox", -int(item["messages"]), item["id"]))
    return result


def list_agents(root: Path) -> list[dict[str, Any]]:
    """List registered agents (for the YOU/TO pickers).

    Merges the relay registry agents with the mailbox participants seen in recent
    traffic, so the YOU/TO combos are populated with every possibility. The two
    default identities are always present.
    """

    agents: list[str] = []
    if _mailbox_client is not None:
        try:
            registry = _mailbox_client._rest_request("GET", "/v1/registry")
            agents = [str(a.get("agent_id")) for a in registry.get("agents", []) if a.get("agent_id")]
        except Exception:
            agents = []
    agents.extend(channel["id"] for channel in list_channels(root) if channel.get("kind") == "mailbox")
    agents.extend((DEFAULT_USER_AGENT, DEFAULT_PEER_AGENT))
    seen: set[str] = set()
    ordered: list[dict[str, Any]] = []
    for agent_id in agents:
        if agent_id and agent_id not in seen:
            seen.add(agent_id)
            ordered.append({"id": agent_id})
    return ordered


def _agent_channel_subscriptions(agent: str) -> set[str]:
    if _mailbox_client is None:
        return set()
    try:
        data = _mailbox_client._rest_request(
            "GET", "/v1/cursors?" + urllib.parse.urlencode({"cursor": agent})
        )
    except Exception:
        return set()
    recipients: set[str] = set(data.get("recipients", []) or [])
    for position in data.get("positions", []) or []:
        recipient = position.get("recipient")
        if recipient:
            recipients.add(str(recipient))
    return recipients


def subscribe_agent_to_channel(agent: str, channel: str) -> bool:
    """Give ``agent`` a cursor on ``channel`` so addressing it there subscribes it.

    Best effort and idempotent: skips when the agent already subscribes, and
    subscribes with ``start=now`` (called before the message is sent so the agent
    still sees it).
    """

    if _mailbox_client is None or not agent or not channel or agent == channel:
        return False
    if channel in _agent_channel_subscriptions(agent):
        return False
    try:
        _mailbox_client.initialize_cursor_rest(channel, cursor=agent, start="now")
        return True
    except Exception:
        return False


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


@router.get("/mailbox/agents")
def mailbox_agents() -> dict[str, Any]:
    root = resolve_mailbox_root()
    return {"agents": list_agents(root), "defaultUser": DEFAULT_USER_AGENT, "defaultAgent": DEFAULT_PEER_AGENT}


@router.post("/mailbox/agents")
def mailbox_create_agent(
    id: str = Body(..., embed=True),
    presence: str | None = Body(None, embed=True),
) -> dict[str, Any]:
    if _mailbox_client is None:
        raise HTTPException(status_code=503, detail="mailbox_channels client is not installed")
    agent_id = id.strip() if isinstance(id, str) else ""
    if not agent_id:
        raise HTTPException(status_code=400, detail="Agent id must not be empty")
    presence_id = presence.strip() if isinstance(presence, str) and presence.strip() else f"{agent_id}-app"
    try:
        registration = _mailbox_client.register_agent_rest(agent_id, presence_id=presence_id)
    except Exception as error:
        registration = {"skipped": True, "reason": str(error)}
    return {"id": agent_id, "presence": presence_id, "registration": registration}


@router.post("/mailbox/channels")
def mailbox_create_channel(id: str = Body(..., embed=True)) -> dict[str, Any]:
    if _mailbox_client is None:
        raise HTTPException(status_code=503, detail="mailbox_channels client is not installed")
    channel_id = id.strip() if isinstance(id, str) else ""
    if not channel_id:
        raise HTTPException(status_code=400, detail="Channel id must not be empty")
    # Creating a channel = subscribing the default agent to it so the relay retains it.
    created = subscribe_agent_to_channel(DEFAULT_PEER_AGENT, channel_id)
    return {"id": channel_id, "created": created}


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
    channel_id: str | None = Body(None, embed=True),
) -> dict[str, Any]:
    if _mailbox_client is None:
        raise HTTPException(status_code=503, detail="mailbox_channels client is not installed")
    if not text.strip():
        raise HTTPException(status_code=400, detail="Message text must not be empty")
    channel = (channel_id.strip() or None) if isinstance(channel_id, str) else None
    # Addressing an agent on a channel auto-subscribes that agent to the channel.
    subscribed = subscribe_agent_to_channel(to, channel) if channel else False
    root = resolve_mailbox_root()
    extra = {"channel_id": channel} if channel else {}
    try:
        record = _mailbox_client.send(to, text, sender=sender, root=root, **extra)
    except Exception as error:  # surface send failures as a 500 with detail
        raise HTTPException(status_code=500, detail=f"Mailbox send failed: {error}") from error
    return {"message": _project_record(record), "subscribed": subscribed}
