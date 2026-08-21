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
import time
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

# Channel configs edited in the UI are persisted as ``channel_config`` records
# addressed to this well-known registry channel; the latest record per channel wins.
REGISTRY_CHANNEL = "server_registry"

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


def _project_record(record: dict[str, Any], names: dict[str, str] | None = None) -> dict[str, Any]:
    author = record.get("author")
    channel_id = record.get("channel_id")
    return {
        "id": record.get("id"),
        "timestamp": record.get("timestamp"),
        "from": record.get("from"),
        "to": record.get("to"),
        "text": record.get("text", ""),
        "type": record.get("type", "message"),
        "channelId": channel_id,
        "author": author,
        "authorName": (names or {}).get(str(author)) if author else None,
        "channelName": record.get("channel_name")
        or ((names or {}).get(str(channel_id)) if channel_id else None),
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
    names: dict[str, str] | None = None,
) -> list[dict[str, Any]]:
    """Return the direct conversation between ``user`` and ``peer``.

    Audit copies (records with an ``audit_of`` marker, written to the server's
    fan-out channels) are skipped so the thread shows each message once.
    """

    pair = {user, peer}
    thread = [
        _project_record(record, names)
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
    names: dict[str, str] | None = None,
) -> list[dict[str, Any]]:
    """Return every message that involves ``channel`` (as sender or recipient)."""

    thread = [
        _project_record(record, names)
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


def stored_messaging_registry(root: Path, *, max_bytes: int = MESSAGES_TAIL_BYTES) -> dict[str, Any]:
    """Return the latest relay-registry snapshot stored on server_registry."""

    stored: dict[str, Any] = {}
    for record in read_tail_records(root / "messages.jsonl", max_bytes):
        if record.get("audit_of"):
            continue
        if REGISTRY_CHANNEL not in (record.get("to"), record.get("channel_id")):
            continue
        if record.get("type") != "messaging_registry":
            continue
        try:
            payload = json.loads(record.get("text") or "{}")
        except Exception:
            continue
        if isinstance(payload, dict):
            stored = payload  # chronological tail read: the last record wins
    return stored


def messaging_registry(root: Path) -> dict[str, Any]:
    """The relay's ``/v1/registry`` (agents/connectors/channels/relays).

    Live relay first; falls back to the snapshot persisted on the
    ``server_registry`` channel so the registry survives relay restarts.
    """

    if _mailbox_client is not None:
        try:
            registry = _mailbox_client._rest_request("GET", "/v1/registry")
            if isinstance(registry, dict) and registry:
                return registry
        except Exception:
            pass
    return stored_messaging_registry(root)


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
    names = identifier_names(root)

    def readable(cid: str) -> str | None:
        """Resolve a channel id to a human name via the identifier directory.

        Mailbox channel ids for bridged platforms embed the opaque platform id as
        their trailing dash segment (e.g. mm-…-c83yjes…), so fall back to that.
        """

        if cid in names:
            return names[cid]
        tail = cid.rsplit("-", 1)[-1]
        if tail != cid and tail in names:
            return names[tail]
        return None

    def add(cid: Any, kind: str) -> None:
        if not isinstance(cid, str) or not cid or cid in AUDIT_CHANNEL_NAMES or cid in channels:
            return
        channels[cid] = {
            "id": cid,
            "kind": kind,
            "messages": participants.get(cid, 0),
            "name": readable(cid),
        }

    registry = messaging_registry(root)
    for agent in registry.get("agents", []) or []:
        add(agent.get("mailbox") or agent.get("agent_id"), "mailbox")
    for channel in registry.get("channels", []) or []:
        add(channel.get("id"), str(channel.get("channel_type") or "channel"))

    for participant in participants:
        add(participant, "mailbox")
    add(REGISTRY_CHANNEL, "registry")
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

    registry = messaging_registry(root)
    agents = [str(a.get("agent_id")) for a in registry.get("agents", []) or [] if a.get("agent_id")]
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


def stored_channel_config(root: Path, channel: str, *, max_bytes: int = MESSAGES_TAIL_BYTES) -> dict[str, Any]:
    """Return the latest edited config stored on the server_registry channel."""

    stored: dict[str, Any] = {}
    for record in read_tail_records(root / "messages.jsonl", max_bytes):
        if record.get("audit_of"):
            continue
        if REGISTRY_CHANNEL not in (record.get("to"), record.get("channel_id")):
            continue
        if record.get("type") != "channel_config" or record.get("config_for") != channel:
            continue
        try:
            payload = json.loads(record.get("text") or "{}")
        except Exception:
            continue
        if isinstance(payload, dict):
            stored = payload  # chronological tail read: the last record wins
    return stored


def _condense_identifier(entry: dict[str, Any]) -> dict[str, Any] | None:
    """Reduce a relay identifier-directory entry to its essential mapping."""

    identifier = entry.get("identifier")
    text = entry.get("text")
    if not identifier or not text:
        return None
    condensed: dict[str, Any] = {
        "system": entry.get("system"),
        "identifier": identifier,
        "text": text,
        "kind": entry.get("kind"),
    }
    display = (entry.get("metadata") or {}).get("display_name")
    if display and display != text:
        condensed["display"] = display
    return condensed


def stored_identifier_directory(root: Path, *, max_bytes: int = MESSAGES_TAIL_BYTES) -> list[dict[str, Any]]:
    """Return the latest identifier-directory bootstrap stored on server_registry."""

    stored: list[dict[str, Any]] = []
    for record in read_tail_records(root / "messages.jsonl", max_bytes):
        if record.get("audit_of"):
            continue
        if REGISTRY_CHANNEL not in (record.get("to"), record.get("channel_id")):
            continue
        if record.get("type") != "identifier_directory":
            continue
        try:
            payload = json.loads(record.get("text") or "[]")
        except Exception:
            continue
        if isinstance(payload, list):
            stored = [entry for entry in payload if isinstance(entry, dict)]
    return stored


# identifier -> human name cache; the directory rarely changes, so resolve it at
# most once per TTL and after an explicit bootstrap.
_NAMES_CACHE: dict[str, Any] = {"at": 0.0, "names": {}}
NAMES_CACHE_TTL_SECS = 60.0


def identifier_names(root: Path, *, refresh: bool = False) -> dict[str, str]:
    """Map opaque platform identifiers (e.g. Mattermost ids) to readable names.

    Sources, later ones winning: the identifier-directory bootstrap stored on the
    ``server_registry`` channel, then the relay's live ``/v1/identifiers``.
    """

    now = time.time()
    if not refresh and _NAMES_CACHE["names"] and now - _NAMES_CACHE["at"] < NAMES_CACHE_TTL_SECS:
        return dict(_NAMES_CACHE["names"])
    names: dict[str, str] = {}
    for entry in stored_identifier_directory(root):
        identifier = entry.get("identifier")
        if identifier:
            names[str(identifier)] = str(entry.get("display") or entry.get("text") or identifier)
    if _mailbox_client is not None:
        try:
            data = _mailbox_client._rest_request("GET", "/v1/identifiers?limit=2000")
            for entry in data.get("identifiers", []) or []:
                condensed = _condense_identifier(entry)
                if condensed:
                    names[str(condensed["identifier"])] = str(
                        condensed.get("display") or condensed["text"]
                    )
        except Exception:
            pass
    _NAMES_CACHE["at"] = now
    _NAMES_CACHE["names"] = dict(names)
    return names


@router.post("/mailbox/registry/bootstrap")
def mailbox_registry_bootstrap(limit: int = Query(2000, ge=1, le=10000)) -> dict[str, Any]:
    """Bootstrap the server_registry channel from the live relay.

    Persists two snapshots as records on the ``server_registry`` channel: the
    relay's ``/v1/registry`` (agents/connectors/channels/relays, stored as a
    ``messaging_registry`` record) and its ``/v1/identifiers`` directory
    (condensed to system/identifier/text/kind/display, stored as an
    ``identifier_directory`` record). Readers fall back to these snapshots, so
    the registry and readable names survive relay restarts and ride the same
    mailbox log as everything else.
    """

    if _mailbox_client is None:
        raise HTTPException(status_code=503, detail="mailbox_channels client is not installed")
    root = resolve_mailbox_root()
    subscribe_agent_to_channel(DEFAULT_PEER_AGENT, REGISTRY_CHANNEL)

    registry_stored = False
    registry_counts: dict[str, int] = {}
    try:
        registry = _mailbox_client._rest_request("GET", "/v1/registry")
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"Relay registry fetch failed: {error}") from error
    if isinstance(registry, dict) and registry:
        registry_counts = {
            key: len(registry.get(key) or [])
            for key in ("agents", "connectors", "channels", "relays")
        }
        try:
            _mailbox_client.send(
                REGISTRY_CHANNEL,
                json.dumps(registry, ensure_ascii=False, sort_keys=True),
                sender=DEFAULT_USER_AGENT,
                root=root,
                message_type="messaging_registry",
                extra_fields={"entry_counts": registry_counts},
                channel_id=REGISTRY_CHANNEL,
            )
            registry_stored = True
        except Exception as error:
            raise HTTPException(status_code=500, detail=f"Storing registry failed: {error}") from error

    query = urllib.parse.urlencode({"limit": limit})
    try:
        data = _mailbox_client._rest_request("GET", f"/v1/identifiers?{query}")
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"Relay identifier fetch failed: {error}") from error
    entries = [
        condensed
        for condensed in (_condense_identifier(entry) for entry in data.get("identifiers", []) or [])
        if condensed
    ]
    identifiers_stored = False
    if entries:
        try:
            _mailbox_client.send(
                REGISTRY_CHANNEL,
                json.dumps(entries, ensure_ascii=False, sort_keys=True),
                sender=DEFAULT_USER_AGENT,
                root=root,
                message_type="identifier_directory",
                extra_fields={"entry_count": len(entries)},
                channel_id=REGISTRY_CHANNEL,
            )
            identifiers_stored = True
        except Exception as error:
            raise HTTPException(status_code=500, detail=f"Storing directory failed: {error}") from error
    _NAMES_CACHE["at"] = 0.0
    _NAMES_CACHE["names"] = {}
    return {
        "channel": REGISTRY_CHANNEL,
        "registryStored": registry_stored,
        "registryCounts": registry_counts,
        "identifiersStored": identifiers_stored,
        "identifierCount": len(entries),
    }


def channel_config(root: Path, channel: str, *, max_bytes: int = MESSAGES_TAIL_BYTES) -> dict[str, Any]:
    """Describe one channel: relay registry record enriched with traffic details.

    Registry channels contribute kind/channel_type/aliases/subscribers/metadata;
    agent mailboxes contribute agent_id/presences. Recent traffic supplies the
    human-readable ``channelName`` (e.g. Mattermost's channel_name), a message
    count, and the last-message timestamp. Configs edited in the UI are stored on
    the ``server_registry`` channel and overlay everything else.
    """

    config: dict[str, Any] = {"id": channel, "kind": "mailbox"}
    registry = messaging_registry(root)
    matched = False
    for entry in registry.get("channels", []) or []:
        if entry.get("id") == channel or channel in (entry.get("aliases") or []):
            config.update(entry)
            config["kind"] = str(entry.get("channel_type") or "channel")
            matched = True
            break
    if not matched:
        for agent in registry.get("agents", []) or []:
            if channel in (agent.get("agent_id"), agent.get("mailbox")):
                config["agent_id"] = agent.get("agent_id")
                config["mailbox"] = agent.get("mailbox")
                config["presences"] = agent.get("presences", [])
                break

    traffic_name: str | None = None
    messages = 0
    last_timestamp: str | None = None
    for record in read_tail_records(root / "messages.jsonl", max_bytes):
        if record.get("audit_of"):
            continue
        if channel not in (record.get("to"), record.get("from"), record.get("channel_id")):
            continue
        messages += 1
        last_timestamp = record.get("timestamp") or last_timestamp
        if not traffic_name and record.get("channel_name"):
            traffic_name = str(record.get("channel_name"))
    config["channelName"] = (
        traffic_name
        or config.get("channelName")
        or identifier_names(root).get(channel)
        or channel
    )
    config.setdefault("subscribers", [])
    config["messages"] = messages
    if last_timestamp:
        config["lastMessageAt"] = last_timestamp
    stored = stored_channel_config(root, channel, max_bytes=max_bytes)
    for key, value in stored.items():
        if key not in {"id", "messages", "lastMessageAt"}:
            config[key] = value
    return config


@router.get("/mailbox/channel-config")
def mailbox_channel_config(channel: str = Query(...)) -> dict[str, Any]:
    root = resolve_mailbox_root()
    channel_id = channel.strip() if isinstance(channel, str) else ""
    if not channel_id:
        raise HTTPException(status_code=400, detail="Channel must not be empty")
    return {"channel": channel_id, "config": channel_config(root, channel_id)}


@router.post("/mailbox/channel-config")
def mailbox_update_channel_config(
    channel: str = Body(..., embed=True),
    config: dict[str, Any] = Body(..., embed=True),
) -> dict[str, Any]:
    """Apply an edited channel config.

    Names added to ``subscribers`` get a relay cursor on the channel; the whole
    edited config is then persisted as a ``channel_config`` record on the
    ``server_registry`` channel, where the latest record per channel wins.
    """

    root = resolve_mailbox_root()
    channel_id = channel.strip() if isinstance(channel, str) else ""
    if not channel_id:
        raise HTTPException(status_code=400, detail="Channel must not be empty")
    if not isinstance(config, dict):
        raise HTTPException(status_code=400, detail="Config must be a JSON object")
    current = channel_config(root, channel_id)
    subscribed: list[str] = []
    wanted = config.get("subscribers")
    if isinstance(wanted, list):
        existing = {str(name) for name in (current.get("subscribers") or [])}
        for name in wanted:
            if isinstance(name, str) and name.strip() and name.strip() not in existing:
                if subscribe_agent_to_channel(name.strip(), channel_id):
                    subscribed.append(name.strip())
    stored = False
    if _mailbox_client is not None:
        try:
            _mailbox_client.send(
                REGISTRY_CHANNEL,
                json.dumps(config, indent=2, sort_keys=True),
                sender=DEFAULT_USER_AGENT,
                root=root,
                message_type="channel_config",
                extra_fields={"config_for": channel_id},
                channel_id=REGISTRY_CHANNEL,
            )
            stored = True
        except Exception as error:
            raise HTTPException(status_code=500, detail=f"Storing config failed: {error}") from error
    return {
        "channel": channel_id,
        "subscribed": subscribed,
        "stored": stored,
        "config": channel_config(root, channel_id),
    }


@router.get("/mailbox/messages")
def mailbox_messages(
    user: str = Query(DEFAULT_USER_AGENT),
    peer: str = Query(DEFAULT_PEER_AGENT),
    channel: str | None = None,
    limit: int = Query(200, ge=1, le=2000),
) -> dict[str, Any]:
    root = resolve_mailbox_root()
    names = identifier_names(root)
    if channel:
        messages = channel_messages(root, channel, limit=limit, names=names)
    else:
        messages = thread_messages(root, user, peer, limit=limit, names=names)
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
