"""HTTP surface over the shared mailbox_channels client.

The workbench Chat page and its floatable mini-dock talk to the same append-only
JSONL mailbox that the CLI agents use (``mailbox_channel/mailbox/messages.jsonl``).
Core endpoints:

* ``GET  /mailbox/status``   - resolved mailbox directory + availability.
* ``GET  /mailbox/messages`` - the conversation thread between two participants
  (tail-read so it stays cheap as the shared log grows).
* ``POST /mailbox/send``     - append a message from the workbench user.
* ``GET  /mailbox/resolve``  - typed resolver (users/workspaces/channels by UUID
  plus an alias table mapping any spelling to typed refs).
* ``POST /mailbox/worker``   - run or enqueue a worker op (identifier_lookup,
  groom_channels, sync_subscriptions); enqueued commands are durable
  ``worker_task`` records on the ``server_worker_queue`` channel.

Converted record scheme (post-groom): bridged channels use one canonical id
``mm-<host-dashed>-<platform-key>`` (workspace slugs omitted); every channel
keeps its platform UUID as ``key`` with all legacy spellings as ``aliases``;
each record belonging to a channel carries ``entry_key`` (``entry_<n>`` in
arrival order). Entry keys are never reused — the next key is max+1, so
settled entries stay safe to delete later (compaction comes separately).
Agents carry a ``subscriptions`` map (channel -> subscribed|unsubscribed,
opt-outs sticky) distinct from their byte+entry ``cursors``.

First-class service agents: ``mattermost-bridge-agent`` handles all mattermost
driver jobs for every configured Mattermost server (the legacy ``mattermost``/
``local-mattermost-server``/``mattermost-bridge`` identities merge into it, and
most registry entries are entered by it); ``mailbox-server-agent`` is the local
server itself (``local-agent``/``mailbox-server``/``channel-relay`` merge into
it); ``worker_pool_loader_agent`` drains ``server_worker_queue`` WITHOUT
removing entries — it layers ``worker_task_status`` (blocked/submitted) and
``worker_task_result`` records over the leftover ``entry_<n>``. A task may
declare ``depends_on: ["entry_4", …]``; unsettled dependencies block it, and a
dependency whose entry no longer exists counts as satisfied.

Reading the thread goes straight to the JSONL file (filtered by the participant
pair) rather than the cursor-based ``receive``/``peek`` helpers, because the chat
view needs both directions of the conversation and must not consume cursors.
"""

from __future__ import annotations

import bisect
import json
import os
import re
import shutil
import threading
import time
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
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
# addressed to this well-known registry channel; the latest record per channel
# wins. It is the identifier blackboard: identifier_entry records, resolver
# indexes and relay snapshots all live here.
REGISTRY_CHANNEL = "server_identifiers_registry"

# Edited agent/channel JSONs live on their own blackboard channels: every
# ``agent_entry`` record goes to server_agents_registry and every
# ``channel_entry`` record to server_channels_registry; the latest record per
# id wins.
AGENTS_CHANNEL = "server_agents_registry"
CHANNELS_CHANNEL = "server_channels_registry"

# Background work requests (e.g. identifier lookups inspired by opaque ids found
# in registry metadata) are enqueued as durable ``worker_task`` records on this
# channel. ``worker_pool_loader_agent`` takes items off the queue WITHOUT
# removing them: it layers ``worker_task_status`` records (submitted/blocked)
# and a final ``worker_task_result`` over the original entry, referencing it by
# its ``entry_key``. Settled entries are DESIGNED to be safe to delete
# (compaction comes later, only once settlement is provably safe): entry keys
# are never reused and a dependency whose entry no longer exists counts as
# satisfied.
WORKER_QUEUE_CHANNEL = "server_worker_queue"
WORKER_LOADER_AGENT = "worker_pool_loader_agent"

# The outbound drop-boxes for posting to the outside world. A sender does NOT
# need to know how delivery works: it drops its text plus whatever address
# hints it has (channel_type, endpoint_address, channel_id, root_id, …) and
# the resolver agent below monitors both queues and owns the know-how —
# resolving human names (e.g. channel "test" on a chat workspace) to endpoint
# addresses and handing each item to the bridge that can deliver it.
#   server_outbound_relay_agent_to_channel — agent -> platform-channel
#     messages (e.g. posts destined for a Mattermost channel).
#   server_outbound_relay_agent_to_agent   — agent -> agent messages.
# The legacy single queue (outbound_delivery / server_outbound_delivery) and
# the old agent_to_channel / agent_to_agent audit channels fold into these:
# bare ids fold via the alias table, whole records split by content (endpoint
# evidence means a platform-channel delivery).
OUTBOUND_TO_CHANNEL_QUEUE = "server_outbound_relay_agent_to_channel"
OUTBOUND_TO_AGENT_QUEUE = "server_outbound_relay_agent_to_agent"
OUTBOUND_LEGACY_IDS = frozenset({"outbound_delivery", "server_outbound_delivery"})
OUTBOUND_DELIVERY_RESOLVER_AGENT = "outbound_delivery_resolver_agent"

# Server lifecycle / adapter event stream (posted by the mailbox server side
# as ``server_events``; displayed and groomed under the canonical log name).
EVENTS_CHANNEL = "server_events_log"

# Service channels are ``server_``-prefixed and registries say ``_registry``.
# These seeds fold legacy spellings into the canonical ids at view time, and a
# ``groom_channels`` apply rewrites history as if they always existed.
CHANNEL_ALIAS_CANONICAL = {
    "server_registry": REGISTRY_CHANNEL,
    "server_agents": AGENTS_CHANNEL,
    "server_channels": CHANNELS_CHANNEL,
    "outbound_delivery": OUTBOUND_TO_CHANNEL_QUEUE,
    "server_outbound_delivery": OUTBOUND_TO_CHANNEL_QUEUE,
    "agent_to_channel": OUTBOUND_TO_CHANNEL_QUEUE,
    "agent_to_agent": OUTBOUND_TO_AGENT_QUEUE,
    "server_events": EVENTS_CHANNEL,
}

# The grooming registry holds the remap knowledge itself as data: one
# ``remap_entry`` record per legacy spelling ({id, canonical, kind}; the
# latest record wins and an empty canonical retires the remap), plus
# cumulative ``remap_usage`` records counting how often each fold fired per
# preposition set (to / from / channel_id combinations).
GROOMING_CHANNEL = "server_grooming_registry"

# ``server_adapters_relays_registry`` catalogs the delivery plumbing as data:
#   adapter_type_entry — one per adapter TYPE the code ships (mirrors
#                        mailbox_channels.channel_relay.ADAPTER_CAPABILITIES).
#   relay_entry        — the presences. These matter most: each relay is a
#                        distinct bot presence with its OWN bot token, and
#                        says things as it is puppeted by our codex agents.
#                        A presence declaration carries ALL the config its
#                        adapter might use (server, identity, token env,
#                        channels, ...) — there is no separate per-connection
#                        config tier.
# Stored entries extend/override the seeds, and the connectors + relays
# arrays in the sibling config/relays.json are merged in read-only.
ADAPTERS_RELAYS_CHANNEL = "server_adapters_relays_registry"

# Reflects mailbox_channels.channel_relay.ADAPTER_CAPABILITIES (kept local so
# the workbench never has to import the relay's adapter stack).
ADAPTER_TYPE_SEEDS = {
    "mattermost": {"presence": "single", "threads": True, "attachments": True},
    "irc": {"presence": "single", "threads": False, "attachments": False},
    "discord": {"presence": "single", "threads": True, "attachments": True},
    "matrix": {"presence": "single", "threads": True, "attachments": True},
    "discourse": {"presence": "single", "threads": True, "attachments": True,
                  "interaction": "forum"},
    "slack": {"presence": "multiple", "threads": True, "attachments": True},
    "telegram": {"presence": "single", "threads": True, "attachments": True},
    "whatsapp": {"presence": "single", "threads": False, "attachments": True,
                 "interaction": "business"},
    "whatsapp_personal": {"presence": "single", "threads": True, "attachments": True,
                          "interaction": "unofficial-web-companion", "official": False},
    "facebook_messenger": {"presence": "single", "threads": False, "attachments": True,
                           "interaction": "page"},
    "viber": {"presence": "single", "threads": False, "attachments": True,
              "interaction": "bot"},
    "line": {"presence": "single", "threads": True, "attachments": True,
             "interaction": "user-group-room"},
}

# Known relays: puppet bot presences that an adapter logs onto a server
# (e.g. the irc adapter puts jllykifsh into irc.quakenet ##logicmoo).
# Each relay uses its own bot token/identity and says things as it is
# puppeted by our codex agents. A presence declaration carries all the
# config its adapter might use; how presences map to connections (one
# socket each, pooled, shared) is up to the adapter. When the adapter gets
# a presence logged in it merges tracking fields into that relay's stored
# JSON here, and tries to note logouts the same way.
RELAY_SEEDS = {
    # The mm presences relay-chat the agent -> platform-channel drop-box:
    # they speak queued outbound items into mattermost. The mm channel is
    # decided per item from its address hints.
    "mm_relay_presence_min_botnick": {
        "adapter": "mattermost",
        "server": "chat.singularitynet.io",
        "identity": "min.botnick",
        "own_token": True,
        "token_env": "MM_BOT_TOKEN",
        "puppeted_by": "codex agents",
        "relay-chat": [OUTBOUND_TO_CHANNEL_QUEUE],
    },
    "mm_relay_presence_atom_ant": {
        "adapter": "mattermost",
        "server": "chat.singularitynet.io",
        "identity": "atom_ant",
        "own_token": True,
        "puppeted_by": "codex agents",
        "relay-chat": [OUTBOUND_TO_CHANNEL_QUEUE],
    },
    "mm_relay_presence_metta_bot": {
        "adapter": "mattermost",
        "server": "chat.singularitynet.io",
        "identity": "metta_bot",
        "own_token": True,
        "puppeted_by": "codex agents",
        "relay-chat": [OUTBOUND_TO_CHANNEL_QUEUE],
    },
    "irc_relay_presence_jllykifsh": {
        "adapter": "irc",
        "server": "irc.quakenet.org",
        "identity": "jllykifsh",
        "channels": ["##logicmoo"],
        "own_token": True,
        "puppeted_by": "codex agents",
        # Prospective job (software configured later): relay all chat from
        # these mattermost channels into ##logicmoo, one line each, e.g.
        # "snet|test|douglas.miles: hi irc". Named example-of- until real.
        "example-of-relay-chat": ["test", "image", "arc3"],
    },
}


def _fold_channel(cid: Any) -> Any:
    """Canonical spelling for a channel id (legacy service names fold)."""

    return _REMAPS_CACHE["channels"].get(cid, cid) if isinstance(cid, str) else cid


def _fold_agent(aid: Any) -> Any:
    """Canonical spelling for an agent id (aliases + stored remaps fold)."""

    return _REMAPS_CACHE["agents"].get(aid, aid) if isinstance(aid, str) else aid


def _fold_id(value: Any) -> Any:
    """Fold a to/from-style id through both the channel and agent remaps."""

    return _fold_agent(_fold_channel(value))


# Blackboard/service channels are never agents: stored entries or cursors
# bearing these ids (canonical or legacy) must not leak into the agents
# directory.
WELL_KNOWN_CHANNELS = {
    REGISTRY_CHANNEL, AGENTS_CHANNEL, CHANNELS_CHANNEL, WORKER_QUEUE_CHANNEL,
    OUTBOUND_TO_CHANNEL_QUEUE, OUTBOUND_TO_AGENT_QUEUE, EVENTS_CHANNEL,
    GROOMING_CHANNEL, ADAPTERS_RELAYS_CHANNEL, *CHANNEL_ALIAS_CANONICAL,
}

# Every Mattermost bridge identity is one agent whose job is to handle ALL
# mattermost driver jobs for every configured Mattermost server (inbound
# fan-out, outbound posts, channel IO — one agent, many hosts). Legacy
# spellings are merged by the groom (history, cursors, registry docs) and
# folded at view time so stray new traffic still displays under the canonical id.
MATTERMOST_BRIDGE_AGENT = "mattermost-bridge-agent"
# Likewise the local mailbox server's own identities (the log daemon, the
# channel relay and the generic local agent) are one first-class agent.
MAILBOX_SERVER_AGENT = "mailbox-server-agent"
AGENT_ALIAS_CANONICAL = {
    "mattermost": MATTERMOST_BRIDGE_AGENT,
    "local-mattermost-server": MATTERMOST_BRIDGE_AGENT,
    "mattermost-bridge": MATTERMOST_BRIDGE_AGENT,
    "local-agent": MAILBOX_SERVER_AGENT,
    "mailbox-server": MAILBOX_SERVER_AGENT,
    "channel-relay": MAILBOX_SERVER_AGENT,
}

# legacy -> canonical fold maps merged from the built-in seeds above and the
# ``remap_entry`` records stored on the grooming registry. Refreshed whenever
# the log grows, the root changes, or the TTL lapses.
_REMAPS_CACHE: dict[str, Any] = {
    "root": "",
    "size": -1,
    "at": 0.0,
    "channels": dict(CHANNEL_ALIAS_CANONICAL),
    "agents": dict(AGENT_ALIAS_CANONICAL),
}
REMAPS_CACHE_TTL_SECS = 30.0

# Fold telemetry accumulated since the last flush: (kind, legacy) ->
# {"canonical": id, "sets": {"to+channel_id": count, ...}}. Not every fold is
# persisted individually — counts are folded into cumulative ``remap_usage``
# records on the grooming registry, one per remap, keyed by preposition set.
_REMAP_USAGE: dict[tuple[str, str], dict[str, Any]] = {}
_REMAP_USAGE_FLUSHED_AT = [0.0]
REMAP_USAGE_FLUSH_SECS = 60.0


def _note_fold(kind: str, legacy: str, canonical: str, fields: tuple[str, ...]) -> None:
    """Count one fold application under its preposition set (e.g. to+channel_id)."""

    if not fields:
        return
    usage = _REMAP_USAGE.setdefault((kind, legacy), {"canonical": canonical, "sets": {}})
    usage["canonical"] = canonical
    label = "+".join(fields)
    usage["sets"][label] = int(usage["sets"].get(label) or 0) + 1


def _split_outbound(record: dict[str, Any]) -> str:
    """Pick the outbound queue a legacy outbound_delivery record belongs to.

    Endpoint evidence (an ``endpoint_address`` / ``endpoint`` block or a
    ``channel_type`` hint) marks an agent -> platform-channel delivery;
    anything else was an agent -> agent message.
    """

    if (
        record.get("endpoint_address")
        or isinstance(record.get("endpoint"), dict)
        or record.get("channel_type")
    ):
        return OUTBOUND_TO_CHANNEL_QUEUE
    return OUTBOUND_TO_AGENT_QUEUE


def _fold_record_addresses(record: dict[str, Any]) -> tuple[Any, Any, Any]:
    """Fold a message's to/from/channel_id, logging which prepositions folded."""

    raw = (record.get("to"), record.get("from"), record.get("channel_id"))
    folded = tuple(
        _split_outbound(record)
        if field in ("to", "channel_id") and value in OUTBOUND_LEGACY_IDS
        else _fold_id(value)
        for field, value in zip(("to", "from", "channel_id"), raw)
    )
    hits: dict[tuple[str, str], list[str]] = {}
    for field, old, new in zip(("to", "from", "channel_id"), raw, folded):
        if isinstance(old, str) and new != old:
            hits.setdefault((old, str(new)), []).append(field)
    for (legacy, canonical), fields in hits.items():
        kind = "channel" if legacy in _REMAPS_CACHE["channels"] else "agent"
        _note_fold(kind, legacy, canonical, tuple(fields))
    return folded  # type: ignore[return-value]


def _raw_grooming_entries(root: Path, record_type: str) -> dict[str, dict[str, Any]]:
    """Latest grooming-registry entries by id, WITHOUT folding (no recursion)."""

    entries: dict[str, dict[str, Any]] = {}
    for record in read_tail_records(root / "messages.jsonl", REGISTRY_TAIL_BYTES):
        if record.get("audit_of"):
            continue
        if GROOMING_CHANNEL not in (record.get("to"), record.get("channel_id")):
            continue
        if record.get("type") != record_type:
            continue
        entry = record.get("entry")
        if isinstance(entry, dict) and isinstance(entry.get("id"), str) and entry["id"]:
            entries[entry["id"]] = entry
    return entries


def _refresh_remaps(root: Path, *, force: bool = False) -> None:
    """Merge stored remap_entry records into the fold maps (and flush usage)."""

    now = time.time()
    size = _messages_size(root)
    same_root = _REMAPS_CACHE["root"] == str(root)
    if (not force and same_root and _REMAPS_CACHE["size"] == size
            and now - _REMAPS_CACHE["at"] < REMAPS_CACHE_TTL_SECS):
        return
    channels = dict(CHANNEL_ALIAS_CANONICAL)
    agents = dict(AGENT_ALIAS_CANONICAL)
    for legacy, entry in _raw_grooming_entries(root, "remap_entry").items():
        canonical = str(entry.get("canonical") or "").strip()
        kind = str(entry.get("kind") or "channel").strip().lower()
        table = agents if kind == "agent" else channels
        if not canonical or canonical == legacy:
            table.pop(legacy, None)  # retired remap (built-in seeds included)
        else:
            table[legacy] = canonical
    if not same_root:
        _REMAP_USAGE.clear()  # usage never crosses mailbox roots
    _REMAPS_CACHE.update(root=str(root), size=size, at=now, channels=channels, agents=agents)
    _flush_remap_usage(root)


def _flush_remap_usage(root: Path, *, force: bool = False) -> None:
    """Fold accumulated counts into cumulative remap_usage records."""

    now = time.time()
    if not _REMAP_USAGE or _mailbox_client is None:
        return
    if not force and now - _REMAP_USAGE_FLUSHED_AT[0] < REMAP_USAGE_FLUSH_SECS:
        return
    _REMAP_USAGE_FLUSHED_AT[0] = now
    stored = _raw_grooming_entries(root, "remap_usage")
    pending = dict(_REMAP_USAGE)
    _REMAP_USAGE.clear()
    try:
        for (kind, legacy), usage in pending.items():
            key = f"usage:{kind}:{legacy}"
            sets = dict((stored.get(key) or {}).get("sets") or {})
            for label, count in usage["sets"].items():
                sets[label] = int(sets.get(label) or 0) + int(count)
            entry = {
                "id": key,
                "kind": kind,
                "legacy": legacy,
                "canonical": usage["canonical"],
                "sets": sets,
                "total": sum(sets.values()),
            }
            _mailbox_client.send(
                GROOMING_CHANNEL, "", sender=DEFAULT_USER_AGENT, root=root,
                message_type="remap_usage", extra_fields={"entry": entry},
                channel_id=GROOMING_CHANNEL,
            )
    except Exception:
        # Sending failed: put the pending deltas back for the next flush.
        for key2, usage2 in pending.items():
            back = _REMAP_USAGE.setdefault(key2, {"canonical": usage2["canonical"], "sets": {}})
            for label, count in usage2["sets"].items():
                back["sets"][label] = int(back["sets"].get(label) or 0) + int(count)

# Role descriptions seeded onto server_agents_registry for the service identities.
AGENT_ROLES = {
    MATTERMOST_BRIDGE_AGENT: (
        "Handles all mattermost driver jobs for every configured Mattermost "
        "server: inbound fan-out, outbound posts and channel IO. Delivers the "
        "outbound-relay items the resolver routes to it (adapters, "
        "duplicate suppression)."
    ),
    OUTBOUND_DELIVERY_RESOLVER_AGENT: (
        "Monitors the server_outbound_relay_agent_to_channel and "
        "server_outbound_relay_agent_to_agent queues: resolves each drop's "
        "address hints (channel_type, endpoint_address, human channel names) "
        "and subscribes/hands off to the right bridge agent for delivery."
    ),
    MAILBOX_SERVER_AGENT: (
        "The local mailbox server itself: owns messages.jsonl, relays channel "
        "traffic and runs the local delivery jobs."
    ),
    WORKER_LOADER_AGENT: (
        "Takes work items off server_worker_queue (leaving the entries in "
        "place) and layers submitted/blocked/result statuses over them."
    ),
}

# Known channel_type -> bridge routing the resolver applies when it hands an
# outbound-delivery item to a delivery-capable bridge (an email-bridge-agent
# would register here once it exists).
DELIVERY_BRIDGE_AGENTS = {
    "mattermost": MATTERMOST_BRIDGE_AGENT,
}

# Service queues are monitored by the agents expected to hold a cursor there
# and settle entries. Designated, not exclusive: anyone may also subscribe
# (e.g. a user watching the delivery queue for debugging) — but these agents
# are the ones responsible for it.
CHANNEL_MONITORS = {
    WORKER_QUEUE_CHANNEL: (WORKER_LOADER_AGENT,),
    OUTBOUND_TO_CHANNEL_QUEUE: (OUTBOUND_DELIVERY_RESOLVER_AGENT,),
    OUTBOUND_TO_AGENT_QUEUE: (OUTBOUND_DELIVERY_RESOLVER_AGENT,),
}

# Only read the tail of the shared log for the thread view; the file accumulates
# every agent's traffic and can be several megabytes.
MESSAGES_TAIL_BYTES = 512 * 1024

# Registry snapshots (messaging_registry / identifier_entry / channel_config
# records on the identifiers-registry channel) get a deeper tail so they stay
# discoverable as ordinary chat traffic accumulates.
REGISTRY_TAIL_BYTES = 4 * 1024 * 1024


def resolve_mailbox_root() -> Path:
    """Return the mailbox directory, honouring the AGENT_MAILBOX_DIR override.

    Falls back to the sibling ``mailbox_channel/mailbox`` directory next to the
    repository root (matching run_channel_relay.bat and mailbox.system.metta).
    """

    configured = os.environ.get("AGENT_MAILBOX_DIR")
    if configured:
        root = Path(configured).expanduser().resolve()
    else:
        repo_root = Path(__file__).resolve().parents[2]
        root = (repo_root.parent / "mailbox_channel" / "mailbox").resolve()
    try:
        # Keep the legacy->canonical fold maps in sync with the grooming
        # registry; cheap thanks to the size+TTL guard.
        _refresh_remaps(root)
    except Exception:
        pass
    return root


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
        "entryKey": record.get("entry_key"),
        # A relayed/forwarded entry names its original as ``mailbox-id/entry_n``
        # (e.g. an agent forwarding a queue message into the right mailbox).
        "copyOf": record.get("copy_of"),
        "raw": record,
    }


def read_tail_records(messages_path: Path, max_bytes: int | None = None) -> list[dict[str, Any]]:
    """Parse a JSONL mailbox file into records.

    Always starts at byte 0 (the whole file) unless a caller deliberately
    limits itself by passing ``max_bytes``, in which case only the file's
    tail is parsed (the partial line at the seek boundary is discarded).
    """

    try:
        size = messages_path.stat().st_size
    except FileNotFoundError:
        return []
    with messages_path.open("rb") as stream:
        if max_bytes is not None and size > max_bytes:
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
    max_bytes: int | None = None,
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


# (The legacy agent_to_channel / agent_to_agent audit pseudo-recipients fold
# into the outbound relay queues via CHANNEL_ALIAS_CANONICAL; audit copies —
# records bearing ``audit_of`` — stay hidden everywhere regardless.)


def channel_messages(
    root: Path,
    channel: str,
    *,
    limit: int = 200,
    max_bytes: int | None = None,
    names: dict[str, str] | None = None,
) -> list[dict[str, Any]]:
    """Return every message that involves ``channel`` (as sender or recipient)."""

    wanted = _fold_id(channel)
    thread = [
        _project_record(record, names)
        for record in read_tail_records(root / "messages.jsonl", max_bytes)
        if not record.get("audit_of")
        and wanted in _fold_record_addresses(record)
    ]
    if limit and len(thread) > limit:
        thread = thread[-limit:]
    return thread


def filtered_messages(
    root: Path,
    *,
    to: str | None = None,
    sender: str | None = None,
    channel: str | None = None,
    channel_id: str | None = None,
    text: str | None = None,
    limit: int = 200,
    names: dict[str, str] | None = None,
) -> list[dict[str, Any]]:
    """Search the WHOLE log; every given constraint must match (logical AND).

    Constraints mirror the UI's require-match bar: ``to``/``sender`` exact
    record fields, ``channel`` involvement (from, to or channel_id),
    ``channel_id`` the routed send channel only, and ``text`` a
    case-insensitive substring — or a regular expression when written
    ``/like-this/``. No constraints means everything, everywhere (audit
    copies stay hidden).
    """

    matcher = None
    if text:
        if len(text) > 1 and text.startswith("/") and text.endswith("/"):
            try:
                matcher = re.compile(text[1:-1], re.IGNORECASE).search
            except re.error:
                matcher = None  # broken regex falls back to a plain substring
        if matcher is None:
            needle = text.lower()
            matcher = lambda value: needle in value.lower()  # noqa: E731
    picked = []
    to = _fold_id(to)
    sender = _fold_id(sender)
    channel = _fold_id(channel)
    channel_id = _fold_channel(channel_id)
    for record in read_tail_records(root / "messages.jsonl"):
        if record.get("audit_of"):
            continue
        folded_to, folded_from, folded_cid = _fold_record_addresses(record)
        if to and folded_to != to:
            continue
        if sender and folded_from != sender:
            continue
        if channel and channel not in (folded_to, folded_from, folded_cid):
            continue
        if channel_id and folded_cid != channel_id:
            continue
        if matcher and not matcher(str(record.get("text") or "")):
            continue
        picked.append(_project_record(record, names))
    if limit and len(picked) > limit:
        picked = picked[-limit:]
    return picked


def stored_messaging_registry(root: Path, *, max_bytes: int | None = None) -> dict[str, Any]:
    """Return the latest relay-registry snapshot stored on the registry channel."""

    stored: dict[str, Any] = {}
    for record in read_tail_records(root / "messages.jsonl", max_bytes):
        if record.get("audit_of"):
            continue
        if REGISTRY_CHANNEL not in (
            _fold_channel(record.get("to")), _fold_channel(record.get("channel_id"))
        ):
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
    """The registry (agents/connectors/channels/relays) read from the blackboard.

    The ``server_identifiers_registry`` channel is the single source of truth:
    the latest ``messaging_registry`` record wins. The live relay is consulted
    only by the bootstrap endpoint, which syncs relay state onto the channel.
    """

    return stored_messaging_registry(root)


def _cursor_map(root: Path) -> dict[str, list[str]]:
    """agent -> channels with a cursor, from cursor_subscriptions.json."""

    try:
        document = json.loads((root / "cursor_subscriptions.json").read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    cursors = document.get("cursors") or {}
    result: dict[str, list[str]] = {}
    for agent, channel_ids in cursors.items():
        if isinstance(channel_ids, list):
            result[str(agent)] = list(dict.fromkeys(str(c) for c in channel_ids))
    return result


def _cursor_brief(root: Path, channel: str, agent: str, size: int) -> dict[str, Any]:
    """Compact cursor position for embedding in agent/channel records."""

    path = _mailbox_client._cursor_path(root, f"{channel}:{agent}")
    initialized = path.exists()
    offset = _mailbox_client._read_cursor(path)
    return {
        "offset": offset,
        "behind": max(0, size - offset) if initialized else size,
        "initialized": initialized,
    }


def _messages_size(root: Path) -> int:
    try:
        return (root / "messages.jsonl").stat().st_size
    except FileNotFoundError:
        return 0


# Lifetime per-id traffic stats, maintained incrementally: whenever a message
# lands on the log, the next reader picks up only the appended bytes, so the
# message counts and last-message timestamps stay live without rescanning the
# whole (multi-megabyte) file on every poll.
_TRAFFIC_LOCK = threading.Lock()
_TRAFFIC_STATE: dict[str, Any] = {"path": "", "offset": 0, "checkpoint": b"", "stats": {}}
_TRAFFIC_CHECKPOINT_BYTES = 64


def _traffic_stats(root: Path) -> dict[str, dict[str, Any]]:
    """id -> lifetime traffic stats over the WHOLE messages.jsonl.

    Each entry carries ``messages`` (count of records mentioning the id as
    to/from/channel_id), ``entries`` (count of records BELONGING to the id as a
    channel — also the next ``entry_<n>`` key), ``lastMessageAt`` (timestamp of
    the newest such record), ``channelName`` (newest bridged channel_name seen
    for the id) and ``isChannel`` (True once the id has appeared as a record's
    channel_id — such ids are channels, never agent mailboxes).

    Incremental: only bytes appended since the previous call are parsed. A
    truncated or rewritten file (checkpoint mismatch) triggers a full rescan.
    """

    path = root / "messages.jsonl"
    key = str(path)
    with _TRAFFIC_LOCK:
        state = _TRAFFIC_STATE
        if state["path"] != key:
            state.update(path=key, offset=0, checkpoint=b"", stats={})
        try:
            size = path.stat().st_size
        except FileNotFoundError:
            state.update(offset=0, checkpoint=b"", stats={})
            return {}
        offset = int(state["offset"])
        checkpoint = state["checkpoint"]
        with path.open("rb") as stream:
            if size < offset:
                offset = 0
            elif offset and checkpoint:
                stream.seek(max(0, offset - len(checkpoint)))
                if stream.read(len(checkpoint)) != checkpoint:
                    offset = 0  # file was rewritten underneath us: rescan
            if offset == 0:
                state.update(offset=0, checkpoint=b"", stats={})
            if size == offset:
                return dict(state["stats"])
            stream.seek(offset)
            data = stream.read(size - offset)
        end = data.rfind(b"\n")
        if end < 0:
            return dict(state["stats"])  # no complete appended line yet
        complete = data[: end + 1]
        stats: dict[str, dict[str, Any]] = state["stats"]
        for line in complete.split(b"\n"):
            if not line.strip():
                continue
            try:
                record = json.loads(line.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                continue
            if not isinstance(record, dict) or record.get("audit_of"):
                continue
            timestamp = record.get("timestamp")
            folded_to, folded_from, folded_cid = _fold_record_addresses(record)
            affiliation = folded_cid or folded_to
            seen: set[str] = set()
            for value in (folded_to, folded_from, folded_cid):
                if isinstance(value, str) and value:
                    seen.add(value)
            for value in seen:
                entry = stats.setdefault(
                    value,
                    {
                        "messages": 0,
                        "entries": 0,
                        "nextEntry": 0,
                        "lastMessageAt": None,
                        "channelName": None,
                        "isChannel": False,
                    },
                )
                entry["messages"] += 1
                if value == affiliation:
                    # This record BELONGS to the channel: its key is entry_<n>.
                    # nextEntry is max+1 (never a recycled key), so deleting
                    # settled entries later can never reissue an old key.
                    entry["entries"] += 1
                    stamped = record.get("entry_key")
                    index = None
                    if isinstance(stamped, str) and stamped.startswith("entry_"):
                        try:
                            index = int(stamped[6:])
                        except ValueError:
                            index = None
                    if index is None:
                        index = entry["nextEntry"]
                    entry["nextEntry"] = max(entry["nextEntry"], index + 1)
                if isinstance(timestamp, str) and timestamp:
                    entry["lastMessageAt"] = timestamp
                if value == folded_cid:
                    entry["isChannel"] = True
                    if record.get("channel_name"):
                        entry["channelName"] = str(record["channel_name"])
        state["offset"] = offset + end + 1
        state["checkpoint"] = complete[-_TRAFFIC_CHECKPOINT_BYTES:]
        return dict(stats)


def list_channels(root: Path) -> list[dict[str, Any]]:
    """List every mailbox/channel worth showing in the pickers.

    Merges the relay registry (authoritative: agent mailboxes + retained
    channels, each keeping its FULL record — metadata included) with the
    participants seen in traffic. Message counts and last-message timestamps
    are lifetime stats maintained incrementally as records land on the log.
    """

    stats = _traffic_stats(root)
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

    def add(cid: Any, kind: str, source: dict[str, Any] | None = None) -> None:
        if not isinstance(cid, str) or not cid:
            return
        cid = _fold_channel(cid)
        traffic = stats.get(cid) or {}
        if cid not in channels:
            channels[cid] = {
                "id": cid,
                "kind": kind,
                "messages": int(traffic.get("messages") or 0),
                "name": readable(cid) or traffic.get("channelName"),
            }
            if traffic.get("lastMessageAt"):
                channels[cid]["lastMessageAt"] = traffic["lastMessageAt"]
        if isinstance(source, dict):
            # Registry records merge in whole (metadata, aliases, …) by default;
            # containers are copied so later mutation never aliases the registry.
            for key, value in source.items():
                if isinstance(value, list):
                    value = list(value)
                elif isinstance(value, dict):
                    value = dict(value)
                channels[cid].setdefault(key, value)
        # Every bridged channel keeps its platform UUID as ``key``.
        metadata = channels[cid].get("metadata")
        address = metadata.get("external_address") if isinstance(metadata, dict) else None
        match = _MM_SLASH_RE.match(str(address or "")) or _MM_DASH_RE.match(cid)
        if match:
            channels[cid].setdefault("key", match.group("key"))
        elif _looks_opaque_id(cid):
            channels[cid].setdefault("key", cid)

    registry = messaging_registry(root)
    # Registry entries are entered by the first-class bridge agent — it owns
    # the relay registry — so stamp provenance unless a record says otherwise.
    for agent in registry.get("agents", []) or []:
        mailbox = agent.get("mailbox") or agent.get("agent_id")
        if isinstance(mailbox, str):
            mailbox = _fold_agent(mailbox)
        record = dict(agent)
        if mailbox != MATTERMOST_BRIDGE_AGENT:
            record.setdefault("entered_by", MATTERMOST_BRIDGE_AGENT)
        add(mailbox, "mailbox", record)
    for channel in registry.get("channels", []) or []:
        record = dict(channel)
        record.setdefault("entered_by", MATTERMOST_BRIDGE_AGENT)
        add(channel.get("id"), str(channel.get("channel_type") or "channel"), record)
        _inspire_metadata_lookups(channel, names)

    for cid in sorted(WELL_KNOWN_CHANNELS):
        add(cid, "registry")
    for cid, monitors in CHANNEL_MONITORS.items():
        if cid in channels:
            channels[cid].setdefault("monitors", list(monitors))
    for participant, traffic in stats.items():
        # An id seen as a record's channel_id is a channel, never a mailbox.
        add(participant, "channel" if traffic.get("isChannel") else "mailbox")
    for default_id in (DEFAULT_PEER_AGENT, DEFAULT_USER_AGENT):
        add(default_id, "mailbox")

    for channel_id, entry in stored_entity_entries(root, "channel_entry", CHANNELS_CHANNEL).items():
        record = channels.get(channel_id)
        if record is None:
            continue  # entries for unlisted channels appear once traffic exists
        cleaned = {
            k: v
            for k, v in entry.items()
            if k not in ("cursors", "messages", "subscribers", "lastMessageAt")
        }
        authority = str(cleaned.get("authority") or CHANNELS_CHANNEL)
        copy_from = str(cleaned.get("authority_copy_from") or "always").lower()
        # authority decides who wins at start: the blackboard entry when it names
        # the entity channel, the computed/source record when it names a file —
        # unless the copy already happened once (authority_copy_from: once).
        entry_wins = authority == CHANNELS_CHANNEL or copy_from == "once"
        merged = {**record, **cleaned} if entry_wins else {**cleaned, **record}
        merged["id"] = channel_id
        merged["authority"] = authority
        channels[channel_id] = merged
    for record in channels.values():
        record.setdefault("authority", "messages.jsonl")
    if _mailbox_client is not None:
        # Channels keep a plain subscriber list; per-cursor detail (offset/behind)
        # lives on the agent JSON instead.
        for agent_id, channel_ids in _cursor_map(root).items():
            for cid in channel_ids:
                record = channels.get(cid)
                if record is not None:
                    subscribers = record.setdefault("subscribers", [])
                    if agent_id not in subscribers:
                        subscribers.append(agent_id)
    # Declared registry membership counts too: the list is the live union of
    # cursor holders and the registry's channel subscribers, never a saved copy.
    for channel_rec in registry.get("channels", []) or []:
        record = channels.get(channel_rec.get("id"))
        if record is None or not isinstance(channel_rec.get("subscribers"), list):
            continue
        subscribers = record.setdefault("subscribers", [])
        for name in channel_rec["subscribers"]:
            if isinstance(name, str) and name and name not in subscribers:
                subscribers.append(name)
    for record in channels.values():
        if isinstance(record.get("subscribers"), list):
            record["subscribers"] = sorted(record["subscribers"])
    result = list(channels.values())
    result.sort(key=lambda item: (item["kind"] != "mailbox", -int(item["messages"]), item["id"]))
    return result


def list_agents(root: Path) -> list[dict[str, Any]]:
    """List registered agents (for the YOU/TO pickers).

    Merges the relay registry agents with the mailbox participants seen in recent
    traffic, so the YOU/TO combos are populated with every possibility. Each entry
    keeps the full registry record (plus traffic stats) so the UI can display the
    agent's JSON. The two default identities are always present.
    """

    registry = messaging_registry(root)
    by_id: dict[str, dict[str, Any]] = {}
    order: list[str] = []

    def add(agent_id: Any, record: dict[str, Any] | None = None) -> None:
        if not isinstance(agent_id, str) or not agent_id:
            return
        # Aliased bridge identities fold into their canonical agent, and
        # blackboard channels never masquerade as agents.
        agent_id = _fold_agent(agent_id)
        if agent_id in WELL_KNOWN_CHANNELS:
            return
        if agent_id not in by_id:
            by_id[agent_id] = {"id": agent_id}
            order.append(agent_id)
        if isinstance(record, dict):
            for key, value in record.items():
                by_id[agent_id].setdefault(key, value)

    for agent in registry.get("agents", []) or []:
        record = dict(agent)
        # Registry agents are entered by the first-class bridge agent: it owns
        # the relay registry and registers the bridged identities it drives.
        if _fold_agent(str(agent.get("agent_id"))) != MATTERMOST_BRIDGE_AGENT:
            record.setdefault("entered_by", MATTERMOST_BRIDGE_AGENT)
        add(agent.get("agent_id"), record)
    for channel in list_channels(root):
        if channel.get("kind") == "mailbox":
            add(channel["id"], channel)
    add(DEFAULT_USER_AGENT)
    add(DEFAULT_PEER_AGENT)
    for service_agent, role in AGENT_ROLES.items():
        add(service_agent, {"role": role})
    for agent_id, entry in stored_entity_entries(root, "agent_entry", AGENTS_CHANNEL).items():
        agent_id = _fold_agent(agent_id)
        if agent_id in WELL_KNOWN_CHANNELS:
            continue
        add(agent_id)
        cleaned = {k: v for k, v in entry.items() if k not in ("cursors", "messages", "lastMessageAt")}
        authority = str(cleaned.get("authority") or AGENTS_CHANNEL)
        copy_from = str(cleaned.get("authority_copy_from") or "always").lower()
        if authority == AGENTS_CHANNEL or copy_from == "once":
            by_id[agent_id].update(cleaned)  # entry is authoritative: edits win
        else:
            for key, value in cleaned.items():  # file authority: source fields win
                by_id[agent_id].setdefault(key, value)
        by_id[agent_id]["id"] = agent_id
        by_id[agent_id]["authority"] = authority
    for record in by_id.values():
        record.setdefault("authority", "messages.jsonl")
    if _mailbox_client is not None:
        size = _messages_size(root)
        for agent_id, channel_ids in _cursor_map(root).items():
            agent_id = _fold_agent(agent_id)
            if agent_id in WELL_KNOWN_CHANNELS:
                continue  # a blackboard channel's cursor is not an agent
            add(agent_id)
            by_id[agent_id]["cursors"] = {
                cid: _cursor_brief(root, cid, agent_id, size) for cid in channel_ids
            }
    return [by_id[agent_id] for agent_id in order]


def _agent_channel_subscriptions(agent: str) -> set[str]:
    """Channels ``agent`` holds a cursor on, read straight from the blackboard root."""

    if _mailbox_client is None:
        return set()
    return set(_cursor_map(resolve_mailbox_root()).get(agent, []))


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


def stored_channel_config(root: Path, channel: str, *, max_bytes: int | None = None) -> dict[str, Any]:
    """Return the latest edited config stored on the registry channel."""

    stored: dict[str, Any] = {}
    for record in read_tail_records(root / "messages.jsonl", max_bytes):
        if record.get("audit_of"):
            continue
        if REGISTRY_CHANNEL not in (
            _fold_channel(record.get("to")), _fold_channel(record.get("channel_id"))
        ):
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


def stored_entity_entries(
    root: Path, record_type: str, channel: str, *, max_bytes: int | None = None
) -> dict[str, dict[str, Any]]:
    """Latest edited agent/channel entries stored on ``channel``, by id.

    Each ``agent_entry``/``channel_entry`` record carries one full JSON object in
    its ``entry`` field; the latest record per id wins.
    """

    entries: dict[str, dict[str, Any]] = {}
    for record in read_tail_records(root / "messages.jsonl", max_bytes):
        if record.get("audit_of"):
            continue
        if channel not in (
            _fold_channel(record.get("to")), _fold_channel(record.get("channel_id"))
        ):
            continue
        if record.get("type") != record_type:
            continue
        entry = record.get("entry")
        if isinstance(entry, dict) and isinstance(entry.get("id"), str) and entry["id"]:
            entries[entry["id"]] = entry
    return entries


def _relays_config(root: Path) -> dict[str, Any]:
    """Best-effort read of the sibling relay's config/relays.json (read-only)."""

    candidates: list[Path] = []
    env_dir = os.environ.get("MAILBOX_RELAY_CONFIG_DIR")
    if env_dir:
        candidates.append(Path(env_dir) / "relays.json")
    candidates.append(root.parent / "config" / "relays.json")
    for path in candidates:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if isinstance(payload, dict):
            return payload
    return {}


def adapters_relays_registry(root: Path, *, max_bytes: int | None = None) -> dict[str, Any]:
    """Adapter types + relay presences: seeds ∪ config ∪ stored entries.

    Relays are the interesting part: puppet bot presences (own token, spoken
    through by our codex agents) whose declarations carry all the config an
    adapter might use. Sources are tagged: ``code`` seeds, the sibling
    config/relays.json connectors + relays arrays (``config``, read-only) and
    ``adapter_type_entry``/``relay_entry`` records stored on the registry
    channel (``stored``, latest per id wins). Adapters merge tracking fields
    into the stored relay JSONs at runtime — on login, and best-effort on
    logout too — so stored overlays seed fields rather than replacing the
    declaration.
    """

    adapter_types = {
        type_id: {"id": type_id, "source": "code", **caps}
        for type_id, caps in ADAPTER_TYPE_SEEDS.items()
    }
    relays = {
        relay_id: {"id": relay_id, "source": "code", **spec}
        for relay_id, spec in RELAY_SEEDS.items()
    }

    config = _relays_config(root)
    for stanza in list(config.get("connectors") or []) + list(config.get("relays") or []):
        if not isinstance(stanza, dict) or not stanza.get("id"):
            continue
        relay_id = str(stanza["id"])
        entry = dict(relays.get(relay_id) or {"id": relay_id})
        entry["source"] = "config"
        for key, value in stanza.items():
            if key in ("id", "kind"):
                continue
            # connectors call the server "instance"; presences say "server"
            entry["server" if key == "instance" else key] = value
        relays[relay_id] = entry

    for type_id, entry in stored_entity_entries(
        root, "adapter_type_entry", ADAPTERS_RELAYS_CHANNEL, max_bytes=max_bytes
    ).items():
        adapter_types[type_id] = {
            **(adapter_types.get(type_id) or {}), "id": type_id, **entry, "source": "stored",
        }
    for relay_id, entry in stored_entity_entries(
        root, "relay_entry", ADAPTERS_RELAYS_CHANNEL, max_bytes=max_bytes
    ).items():
        relays[relay_id] = {
            **(relays.get(relay_id) or {}), "id": relay_id, **entry, "source": "stored",
        }

    return {
        "channel": ADAPTERS_RELAYS_CHANNEL,
        "adapter_types": [adapter_types[key] for key in sorted(adapter_types)],
        "relays": [relays[key] for key in sorted(relays)],
    }


def _identifier_display(entry: dict[str, Any]) -> str | None:
    """Readable name for an identifier-directory entry (display name over text)."""

    display = entry.get("display") or (entry.get("metadata") or {}).get("display_name")
    name = display or entry.get("text")
    return str(name) if name else None


def stored_identifier_directory(root: Path, *, max_bytes: int | None = None) -> list[dict[str, Any]]:
    """Return the identifier entries stored on the registry channel, one per bubble.

    Each ``identifier_entry`` record carries one full (uncondensed) directory
    entry in its ``entry`` field; the latest record per identifier wins.
    """

    entries: dict[str, dict[str, Any]] = {}
    for record in read_tail_records(root / "messages.jsonl", max_bytes):
        if record.get("audit_of"):
            continue
        if REGISTRY_CHANNEL not in (
            _fold_channel(record.get("to")), _fold_channel(record.get("channel_id"))
        ):
            continue
        if record.get("type") != "identifier_entry":
            continue
        entry = record.get("entry")
        if isinstance(entry, dict) and entry.get("identifier"):
            entries[str(entry["identifier"])] = entry
    return list(entries.values())


# identifier -> human name cache; the directory rarely changes, so resolve it at
# most once per TTL and after an explicit bootstrap.
_NAMES_CACHE: dict[str, Any] = {"at": 0.0, "names": {}}
NAMES_CACHE_TTL_SECS = 60.0

# ids we already asked the relay about and got nothing back:
# id -> {"at": asked-at time, "message": the incoming message that made us ask}.
# Keeps repeated lookups of the same unknown id from hammering the relay.
_LOOKUP_MISSES: dict[str, dict[str, Any]] = {}
LOOKUP_MISS_TTL_SECS = 300.0


def identifier_names(root: Path, *, refresh: bool = False) -> dict[str, str]:
    """Map opaque platform identifiers (e.g. Mattermost ids) to readable names.

    Reads only the ``identifier_entry`` records on the
    ``server_identifiers_registry`` blackboard (populated by the bootstrap
    endpoint); the live relay is never consulted here.
    """

    now = time.time()
    if not refresh and _NAMES_CACHE["names"] and now - _NAMES_CACHE["at"] < NAMES_CACHE_TTL_SECS:
        return dict(_NAMES_CACHE["names"])
    names: dict[str, str] = {}
    for entry in stored_identifier_directory(root):
        identifier = entry.get("identifier")
        display = _identifier_display(entry)
        if identifier and display:
            names[str(identifier)] = display
    _NAMES_CACHE["at"] = now
    _NAMES_CACHE["names"] = dict(names)
    return names


@router.post("/mailbox/registry/bootstrap")
def mailbox_registry_bootstrap(limit: int = Query(2000, ge=1, le=10000)) -> dict[str, Any]:
    """Bootstrap the identifiers-registry channel from the live relay.

    Persists relay state as records on the ``server_identifiers_registry``
    channel, which
    acts as the registry's blackboard: the relay's ``/v1/registry``
    (agents/connectors/channels/relays) as one ``messaging_registry`` record,
    and every ``/v1/identifiers`` directory entry as its own uncondensed
    ``identifier_entry`` record (one JSON bubble per entry; the latest record
    per identifier wins, and unchanged entries are not re-posted). Readers fall
    back to these records, so the registry and readable names survive relay
    restarts and ride the same mailbox log as everything else.
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
        entry
        for entry in (data.get("identifiers", []) or [])
        if isinstance(entry, dict) and entry.get("identifier")
    ]
    already = {
        str(entry.get("identifier")): entry for entry in stored_identifier_directory(root)
    }
    posted = 0
    for entry in entries:
        if already.get(str(entry["identifier"])) == entry:
            continue  # blackboard already holds this exact entry
        try:
            _mailbox_client.send(
                REGISTRY_CHANNEL,
                "",
                sender=DEFAULT_USER_AGENT,
                root=root,
                message_type="identifier_entry",
                extra_fields={"entry": entry},
                channel_id=REGISTRY_CHANNEL,
            )
            posted += 1
        except Exception as error:
            raise HTTPException(status_code=500, detail=f"Storing identifier failed: {error}") from error
    _NAMES_CACHE["at"] = 0.0
    _NAMES_CACHE["names"] = {}
    return {
        "channel": REGISTRY_CHANNEL,
        "registryStored": registry_stored,
        "registryCounts": registry_counts,
        "identifierCount": len(entries),
        "identifiersPosted": posted,
        "identifiersUnchanged": len(entries) - posted,
    }


def _identifier_lookup(
    identifier: str, *, force: bool = False, message: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Resolve one strange identifier: blackboard first, then the live relay.

    When an id is not on the ``server_identifiers_registry`` blackboard yet, the relay's
    ``/v1/identifiers`` directory is asked for an exact match. A hit is
    persisted back to the blackboard as a new ``identifier_entry`` bubble so
    every agent learns it. A full miss reports ``found: false``, is remembered
    for ``LOOKUP_MISS_TTL_SECS`` so the relay is not asked about the same
    unknown id again until then (``force`` re-asks immediately), and is posted
    to the blackboard as an ``identifier_lookup_request`` bubble carrying the
    original incoming ``message`` as the reason the id got requested.
    """

    root = resolve_mailbox_root()
    for entry in stored_identifier_directory(root):
        if str(entry.get("identifier")) == identifier:
            _LOOKUP_MISSES.pop(identifier, None)
            return {
                "id": identifier,
                "found": True,
                "source": "blackboard",
                "entry": entry,
                "name": _identifier_display(entry),
                "stored": False,
            }

    now = time.time()
    cached = _LOOKUP_MISSES.get(identifier)
    if not force and cached and now - cached["at"] < LOOKUP_MISS_TTL_SECS:
        # We already asked the relay about this id recently; don't ask again.
        return {
            "id": identifier,
            "found": False,
            "source": "miss-cache",
            "entry": None,
            "name": None,
            "stored": False,
            "requestedAt": cached["at"],
            "requestedBecause": cached.get("message"),
            "retryAfterSecs": round(LOOKUP_MISS_TTL_SECS - (now - cached["at"])),
        }

    miss: dict[str, Any] = {"id": identifier, "found": False, "source": None,
                            "entry": None, "name": None, "stored": False}
    if _mailbox_client is None:
        return miss
    query = urllib.parse.urlencode({"identifier": identifier, "limit": 5})
    try:
        data = _mailbox_client._rest_request("GET", f"/v1/identifiers?{query}")
    except Exception:
        data = {}
    candidates = [
        entry
        for entry in ((data.get("identifiers") if isinstance(data, dict) else None) or [])
        if isinstance(entry, dict) and entry.get("identifier")
    ]
    # Prefer the exact id; fall back to the relay's first (normalized) match.
    entry = next(
        (candidate for candidate in candidates if str(candidate["identifier"]) == identifier),
        candidates[0] if candidates else None,
    )
    if entry is None:
        _LOOKUP_MISSES[identifier] = {"at": now, "message": message}
        try:
            # Durable "why": the unresolved request lands on the blackboard so
            # any agent that can resolve the id sees what triggered the ask.
            _mailbox_client.send(
                REGISTRY_CHANNEL,
                "",
                sender=DEFAULT_USER_AGENT,
                root=root,
                message_type="identifier_lookup_request",
                extra_fields={
                    "identifier": identifier,
                    "requested_at": now,
                    "requested_because": message,
                },
                channel_id=REGISTRY_CHANNEL,
            )
        except Exception:
            pass  # the miss is still reported even if persisting the ask fails
        miss["requestedAt"] = now
        miss["requestedBecause"] = message
        return miss
    _LOOKUP_MISSES.pop(identifier, None)
    stored = False
    try:
        _mailbox_client.send(
            REGISTRY_CHANNEL,
            "",
            sender=DEFAULT_USER_AGENT,
            root=root,
            message_type="identifier_entry",
            extra_fields={"entry": entry},
            channel_id=REGISTRY_CHANNEL,
        )
        stored = True
        _NAMES_CACHE["at"] = 0.0
        _NAMES_CACHE["names"] = {}
    except Exception:
        pass  # the lookup still succeeds even if persisting the discovery fails
    return {
        "id": identifier,
        "found": True,
        "source": "relay",
        "entry": entry,
        "name": _identifier_display(entry),
        "stored": stored,
    }


@router.get("/mailbox/identifier")
def mailbox_identifier_lookup(id: str = Query(...), force: bool = Query(False)) -> dict[str, Any]:
    identifier = id.strip() if isinstance(id, str) else ""
    if not identifier:
        raise HTTPException(status_code=400, detail="Identifier must not be empty")
    return _identifier_lookup(identifier, force=force is True)


@router.post("/mailbox/identifier")
def mailbox_identifier_lookup_post(
    id: str = Body(..., embed=True),
    force: bool = Body(False, embed=True),
    message: Any = Body(None, embed=True),
    queue: str = Body("immediate", embed=True),
) -> dict[str, Any]:
    """Lookup with context: ``message`` is the original incoming message (JSON)
    whose strange id triggered the request; it is remembered as the reason.

    ``queue`` follows the worker-queue contract: ``immediate`` (default for
    every REST command) resolves now; ``enqueue`` posts a durable
    ``worker_task`` on ``server_worker_queue`` and lets the pool resolve it.
    """

    identifier = id.strip() if isinstance(id, str) else ""
    if not identifier:
        raise HTTPException(status_code=400, detail="Identifier must not be empty")
    reason = message if isinstance(message, dict) else None
    command = {"op": "identifier_lookup", "id": identifier, "force": force is True}
    if reason is not None:
        command["message"] = reason
    if str(queue).strip().lower() == "enqueue":
        return run_worker_command(command, queue_mode="enqueue", reason=reason)
    return _identifier_lookup(identifier, force=force is True, message=reason)


# ── server_worker_queue ──────────────────────────────────────────────────────
# Durable command queue: each ``worker_task`` record carries the command a REST
# call would have been, plus ``queue_mode``. REST commands execute immediately
# unless the client requested ``enqueue``; a task picked up from the queue
# requests immediate execution (never re-enqueues). ``worker_pool_loader_agent``
# drains the queue WITHOUT removing entries: it layers ``worker_task_status``
# (submitted / blocked) and ``worker_task_result`` records over the original
# entry_<n>, so the leftover task entry plus its overlay tells the full story.
# A task may declare ``depends_on: ["entry_4", "entry_20"]``; the loader holds
# it (blocked) until those queue entries are settled — a result record exists,
# or the entry itself no longer exists (compacted away = satisfied).

_WORKER_POOL: ThreadPoolExecutor | None = None
_WORKER_LOCK = threading.Lock()
_WORKER_SEEN: set[str] = set()  # task keys enqueued during this process run

WORKER_QUEUE_MODES = {"immediate", "enqueue"}
WORKER_DEP_WAIT_SECS = 60.0  # max time the loader holds a blocked task
WORKER_DEP_POLL_SECS = 0.25


def _worker_pool() -> ThreadPoolExecutor:
    global _WORKER_POOL
    if _WORKER_POOL is None:
        _WORKER_POOL = ThreadPoolExecutor(max_workers=2, thread_name_prefix="mailbox-worker")
    return _WORKER_POOL


def _command_key(command: dict[str, Any]) -> str:
    return json.dumps(command, sort_keys=True, ensure_ascii=False)


def _next_entry_key(root: Path, channel: str) -> str:
    """Next never-reused entry_<n> for ``channel`` (max existing + 1)."""

    stats_entry = _traffic_stats(root).get(channel) or {}
    return f"entry_{int(stats_entry.get('nextEntry') or 0)}"


def _queue_entry_states(root: Path) -> dict[str, str]:
    """Fold the queue channel into entry_key -> latest lifecycle status.

    A ``worker_task`` starts ``queued``; ``worker_task_status`` overlays
    (submitted/blocked/…); ``worker_task_result`` settles it (done/error). The
    original entries stay in the log — the overlay is the source of truth.
    """

    states: dict[str, str] = {}
    for record in read_tail_records(root / "messages.jsonl"):
        if record.get("audit_of"):
            continue
        if WORKER_QUEUE_CHANNEL not in (record.get("to"), record.get("channel_id")):
            continue
        kind = record.get("type")
        if kind == "worker_task":
            key = record.get("entry_key")
            if isinstance(key, str) and key:
                states.setdefault(key, str(record.get("status") or "queued"))
        elif kind in ("worker_task_status", "worker_task_result"):
            key = record.get("task_entry")
            if isinstance(key, str) and key and record.get("status"):
                states[key] = str(record["status"])
    return states


def _dependencies_settled(root: Path, depends_on: list[str]) -> bool:
    """True when every dependency entry is settled or no longer exists."""

    if not depends_on:
        return True
    states = _queue_entry_states(root)
    for dep in depends_on:
        status = states.get(dep)
        # Unknown entry = deleted/compacted away = satisfied by design.
        if status is not None and status not in ("done", "error"):
            return False
    return True


def execute_worker_command(command: dict[str, Any]) -> dict[str, Any]:
    """Run one REST-equivalent command right now (immediate mode)."""

    op = str(command.get("op") or "")
    if op == "identifier_lookup":
        identifier = str(command.get("id") or command.get("identifier") or "").strip()
        if not identifier:
            return {"error": "identifier must not be empty"}
        message = command.get("message")
        return _identifier_lookup(
            identifier,
            force=bool(command.get("force")),
            message=message if isinstance(message, dict) else None,
        )
    if op == "groom_channels":
        return _groom_channels(apply=bool(command.get("apply")))
    if op == "sync_subscriptions":
        return _sync_subscriptions()
    if op == "set_subscription":
        return _set_subscription(
            str(command.get("agent") or ""),
            str(command.get("channel") or ""),
            str(command.get("state") or ""),
        )
    if op == "set_remap":
        return _set_remap(
            str(command.get("legacy") or ""),
            str(command.get("canonical") or ""),
            str(command.get("kind") or "channel"),
        )
    return {"error": f"unknown op {op!r}"}


def run_worker_command(
    command: dict[str, Any],
    *,
    queue_mode: str = "immediate",
    reason: dict[str, Any] | None = None,
    dedup: bool = True,
) -> dict[str, Any]:
    """Execute or enqueue a REST-equivalent command.

    ``immediate`` runs the command now and returns its result. ``enqueue``
    posts a durable ``worker_task`` record on ``server_worker_queue`` and hands
    the command to the thread pool; dedup skips task keys already enqueued
    during this process run.
    """

    mode = str(queue_mode).strip().lower()
    if mode not in WORKER_QUEUE_MODES:
        mode = "immediate"
    if mode == "immediate":
        return {"queued": False, "result": execute_worker_command(command)}
    key = _command_key(command)
    if dedup:
        with _WORKER_LOCK:
            if key in _WORKER_SEEN:
                return {"queued": False, "duplicate": True, "taskKey": key}
            _WORKER_SEEN.add(key)
    depends_on = [d for d in (command.get("depends_on") or []) if isinstance(d, str) and d]
    task_entry = None
    if _mailbox_client is not None:
        try:
            root = resolve_mailbox_root()
            task_entry = _next_entry_key(root, WORKER_QUEUE_CHANNEL)
            fields: dict[str, Any] = {
                "command": command,
                "queue_mode": "enqueue",
                "task_key": key,
                "entry_key": task_entry,
                "status": "queued",
                "requested_at": time.time(),
                "requested_because": reason,
            }
            if depends_on:
                fields["depends_on"] = depends_on
            _mailbox_client.send(
                WORKER_QUEUE_CHANNEL,
                "",
                sender=DEFAULT_USER_AGENT,
                root=root,
                message_type="worker_task",
                extra_fields=fields,
                channel_id=WORKER_QUEUE_CHANNEL,
            )
        except Exception:
            pass  # the pool still runs the task; only the durable record is lost
    try:
        _worker_pool().submit(_run_queued_command, dict(command), key, task_entry, depends_on)
    except Exception:
        pass
    return {"queued": True, "taskKey": key, "taskEntry": task_entry}


def _post_task_status(task_entry: str | None, key: str, status: str, **fields: Any) -> None:
    """Loader-agent overlay: layer a status record over the leftover task entry."""

    if _mailbox_client is None:
        return
    try:
        root = resolve_mailbox_root()
        _mailbox_client.send(
            WORKER_QUEUE_CHANNEL,
            "",
            sender=WORKER_LOADER_AGENT,
            root=root,
            message_type="worker_task_status",
            extra_fields={
                # Overlay records are queue entries in their own right.
                "entry_key": _next_entry_key(root, WORKER_QUEUE_CHANNEL),
                "task_key": key,
                "task_entry": task_entry,
                "status": status,
                "at": time.time(),
                **fields,
            },
            channel_id=WORKER_QUEUE_CHANNEL,
        )
    except Exception:
        pass  # best effort: the overlay must never kill the worker


def _run_queued_command(
    command: dict[str, Any],
    key: str,
    task_entry: str | None = None,
    depends_on: list[str] | None = None,
) -> None:
    """The worker_pool_loader_agent takes one item off the queue.

    The ``worker_task`` entry stays in the log; the loader layers status
    records over it: ``submitted`` when it hands the command to the pool
    thread, ``blocked`` while declared ``depends_on`` entries are unsettled,
    and finally a ``worker_task_result``.
    """

    deps = list(depends_on or [])
    if task_entry in deps:
        deps.remove(task_entry)  # a task can never depend on its own entry
    if deps:
        try:
            root = resolve_mailbox_root()
            if not _dependencies_settled(root, deps):
                _post_task_status(task_entry, key, "blocked", depends_on=deps)
                deadline = time.monotonic() + WORKER_DEP_WAIT_SECS
                while time.monotonic() < deadline:
                    time.sleep(WORKER_DEP_POLL_SECS)
                    if _dependencies_settled(root, deps):
                        break
        except Exception:
            pass
    _post_task_status(task_entry, key, "submitted", depends_on=deps or None)
    try:
        result = execute_worker_command(command)
    except Exception as error:  # noqa: BLE001 - worker threads must never raise
        result = {"error": str(error)}
    if _mailbox_client is None:
        return
    summary = {k: result[k] for k in ("found", "name", "source", "error") if k in result}
    try:
        root = resolve_mailbox_root()
        _mailbox_client.send(
            WORKER_QUEUE_CHANNEL,
            "",
            sender=WORKER_LOADER_AGENT,
            root=root,
            message_type="worker_task_result",
            extra_fields={
                "entry_key": _next_entry_key(root, WORKER_QUEUE_CHANNEL),
                "command": command,
                "task_key": key,
                "task_entry": task_entry,
                "queue_mode": "immediate",
                "status": "error" if result.get("error") else "done",
                "completed_at": time.time(),
                "result": summary,
            },
            channel_id=WORKER_QUEUE_CHANNEL,
        )
    except Exception:
        pass  # best effort: losing the result record must not kill the worker


@router.post("/mailbox/worker")
def mailbox_worker_command(
    command: dict[str, Any] = Body(..., embed=True),
    queue: str = Body("immediate", embed=True),
) -> dict[str, Any]:
    """REST parity for the worker queue: run ``command`` now (default) or
    enqueue it on ``server_worker_queue`` when the client asks for it."""

    if not isinstance(command, dict) or not command.get("op"):
        raise HTTPException(status_code=400, detail="command.op must not be empty")
    return run_worker_command(command, queue_mode=queue)


_OPAQUE_ID_MIN_LEN = 20


def _looks_opaque_id(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) >= _OPAQUE_ID_MIN_LEN
        and value.isalnum()
        and value == value.lower()
    )


def _inspire_metadata_lookups(channel_record: dict[str, Any], names: dict[str, str]) -> None:
    """Opaque ids in registry channel metadata inspire identifier lookups.

    Ids like a bridged workspace_id that the identifier directory (``names``)
    cannot name yet are enqueued (at least) as durable lookup tasks on
    ``server_worker_queue``; the pool resolves them against the relay.
    """

    metadata = channel_record.get("metadata")
    if not isinstance(metadata, dict):
        return
    cid = channel_record.get("id")
    aliases = channel_record.get("aliases") or []
    candidates = [
        (key, value)
        for key, value in metadata.items()
        if key.endswith("_id") and _looks_opaque_id(value) and value != cid and value not in aliases
    ]
    for key, value in candidates:
        if value in names:
            continue
        run_worker_command(
            {"op": "identifier_lookup", "id": value},
            queue_mode="enqueue",
            reason={"channel": cid, "metadata_key": key},
        )


# ── channel grooming: canonical keys, aliases, entry_N message keys ──────────
# Bridged Mattermost channels accumulated several spellings of the same place:
#   dash form            mm-chat-singularitynet-io-81u5jjbjttng8fejorr11xns9h
#   workspace dash form  mm-chat-singularitynet-io-chat-81u5jjbjttng8fejorr11xns9h
#   slash form           mm/chat.singularitynet.io/81u5jjbjttng8fejorr11xns9h
#   bare platform key    81u5jjbjttng8fejorr11xns9h
# The groom rewrites messages.jsonl as if only the canonical dash form (host +
# platform key, workspace name omitted) ever existed, merging the duplicates.
# Every channel keeps its platform UUID as ``key``; every record in a channel
# is keyed ``entry_<n>`` in arrival order, so a channel's ``messages`` count is
# always the next entry key. The resolver keeps typed maps (users / workspaces
# / channels, each keyed by their own UUID) plus an alias table mapping any
# spelling or friendly name to typed refs.

_MM_SLASH_RE = re.compile(r"^mm/(?P<host>[^/]+)/(?P<key>[a-z0-9]{20,})$")
_MM_DASH_RE = re.compile(r"^mm-(?P<body>.+)-(?P<key>[a-z0-9]{20,})$")


def _channel_alias_plan(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Group every seen channel spelling by platform key -> canonical identity.

    Metadata (``external_address``/``endpoint``/``workspace_name``) is
    authoritative for the canonical host; without it the shortest dash form
    seen for a key wins (dropping the extra workspace segment).
    """

    groups: dict[str, dict[str, Any]] = {}

    def group(key: str) -> dict[str, Any]:
        return groups.setdefault(
            key, {"key": key, "host": None, "workspace": None, "names": [], "seen": set()}
        )

    def note_name(info: dict[str, Any], name: Any) -> None:
        if isinstance(name, str) and name and name not in info["names"]:
            info["names"].append(name)

    def note_id(value: Any) -> None:
        if not isinstance(value, str) or not value:
            return
        slash = _MM_SLASH_RE.match(value)
        if slash:
            info = group(slash.group("key"))
            info["host"] = info["host"] or slash.group("host")
            info["seen"].add(value)
            return
        dash = _MM_DASH_RE.match(value)
        if dash:
            group(dash.group("key"))["seen"].add(value)
            return
        if _looks_opaque_id(value) and value in groups:
            groups[value]["seen"].add(value)

    def note_channel_record(channel: dict[str, Any]) -> None:
        metadata = channel.get("metadata") if isinstance(channel.get("metadata"), dict) else {}
        address = str(metadata.get("external_address") or "")
        slash = _MM_SLASH_RE.match(address)
        key = None
        if slash:
            key = slash.group("key")
            info = group(key)
            info["host"] = slash.group("host")
        else:
            dash = _MM_DASH_RE.match(str(channel.get("id") or ""))
            if dash:
                key = dash.group("key")
                info = group(key)
        if key is None:
            return
        info = groups[key]
        endpoint = metadata.get("endpoint")
        if isinstance(endpoint, str) and endpoint:
            info["host"] = info["host"] or endpoint
        workspace = metadata.get("workspace_name")
        if isinstance(workspace, str) and workspace:
            info["workspace"] = workspace
        note_name(info, metadata.get("channel_name"))
        for alias in channel.get("aliases") or []:
            note_name(info, alias)
        note_id(channel.get("id"))
        note_id(address)

    # Pass 1: registry snapshots declare hosts/workspaces; bare keys become
    # known so pass 2 can claim bare-id traffic for them.
    for record in records:
        if record.get("type") == "messaging_registry":
            try:
                snapshot = json.loads(record.get("text") or "{}")
            except json.JSONDecodeError:
                continue
            for channel in (snapshot.get("channels") or []) if isinstance(snapshot, dict) else []:
                if isinstance(channel, dict):
                    note_channel_record(channel)
    for record in records:
        for field in ("to", "from", "channel_id"):
            note_id(record.get(field))
        if record.get("channel_id") and record.get("channel_name"):
            dash = _MM_DASH_RE.match(str(record["channel_id"]))
            slash = _MM_SLASH_RE.match(str(record["channel_id"]))
            match = dash or slash
            if match and match.group("key") in groups:
                note_name(groups[match.group("key")], record.get("channel_name"))

    plan: dict[str, dict[str, Any]] = {}
    for key, info in groups.items():
        host = info["host"]
        if host:
            canonical = f"mm-{host.replace('.', '-')}-{key}"
        else:
            dash_forms = sorted(
                (form for form in info["seen"] if form.startswith("mm-")), key=len
            )
            canonical = dash_forms[0] if dash_forms else key
        aliases = sorted({form for form in info["seen"] if form != canonical} | {key} - {canonical})
        workspace = info["workspace"]
        if host and workspace:
            aliases.append(f"mm-{host.replace('.', '-')}-{workspace}-{key}")
        if host:
            aliases.append(f"mm/{host}/{key}")
        mapping_sources = sorted(set(aliases) | info["seen"] - {canonical})
        plan[key] = {
            "key": key,
            "canonical": canonical,
            "aliases": sorted(set(aliases) - {canonical}),
            "merges": mapping_sources,
            "names": info["names"],
            "host": host,
            "workspace": workspace,
        }
    return plan


def _read_all_lines(path: Path) -> tuple[list[bytes], list[int]]:
    """All newline-terminated lines plus each line's cumulative end offset."""

    lines: list[bytes] = []
    ends: list[int] = []
    offset = 0
    try:
        raw = path.read_bytes()
    except FileNotFoundError:
        return lines, ends
    for line in raw.splitlines(keepends=True):
        offset += len(line)
        lines.append(line)
        ends.append(offset)
    return lines, ends


def _remap_id(value: Any, mapping: dict[str, str]) -> Any:
    return mapping.get(value, value) if isinstance(value, str) else value


def _remap_registry_snapshot(snapshot: dict[str, Any], plan: dict[str, dict[str, Any]],
                             mapping: dict[str, str]) -> dict[str, Any]:
    """Convert a registry doc to the canonical scheme: keyed channels, merged aliases."""

    snapshot = dict(snapshot)
    agents = snapshot.get("agents")
    if isinstance(agents, list):
        merged_agents: dict[str, dict[str, Any]] = {}
        for agent in agents:
            if not isinstance(agent, dict):
                continue
            agent_id = _remap_id(agent.get("agent_id"), mapping)
            mailbox = _remap_id(agent.get("mailbox"), mapping)
            target = merged_agents.setdefault(str(mailbox or agent_id), {})
            for field, value in agent.items():
                target.setdefault(field, value)
            if agent_id:
                target["agent_id"] = agent_id
            if mailbox:
                target["mailbox"] = mailbox
        snapshot["agents"] = list(merged_agents.values())
    channels = snapshot.get("channels")
    if not isinstance(channels, list):
        return snapshot
    merged: dict[str, dict[str, Any]] = {}
    for channel in channels:
        if not isinstance(channel, dict):
            continue
        cid = _remap_id(channel.get("id"), mapping)
        target = merged.setdefault(str(cid), {})
        for field, value in channel.items():
            if field == "aliases":
                continue
            target.setdefault(field, value)
        target["id"] = cid
        aliases = {a for a in (target.get("aliases") or []) if isinstance(a, str)}
        aliases.update(a for a in (channel.get("aliases") or []) if isinstance(a, str))
        dash = _MM_DASH_RE.match(str(cid))
        if dash and dash.group("key") in plan:
            info = plan[dash.group("key")]
            target["key"] = info["key"]
            aliases.update(info["aliases"])
        target["aliases"] = sorted(aliases - {cid})
        subscribers = {
            _remap_id(s, mapping) for s in (target.get("subscribers") or []) if isinstance(s, str)
        }
        subscribers.update(
            _remap_id(s, mapping) for s in (channel.get("subscribers") or []) if isinstance(s, str)
        )
        target["subscribers"] = sorted(subscribers)
    snapshot["channels"] = list(merged.values())
    return snapshot


def _resolver_index(root: Path) -> dict[str, Any]:
    """Typed resolver maps: users / workspaces / channels by UUID + alias table.

    ``aliases`` maps every known spelling or friendly name to typed refs, e.g.
    ``"test": [{"type": "channel", "key": "<CHANNEL-UUID>"}]`` so one name can
    resolve to a user, a workspace and a channel at the same time.
    """

    users: dict[str, dict[str, Any]] = {}
    workspaces: dict[str, dict[str, Any]] = {}
    channels: dict[str, dict[str, Any]] = {}
    aliases: dict[str, list[dict[str, str]]] = {}

    def alias(name: Any, ref_type: str, key: str) -> None:
        if not isinstance(name, str) or not name or name == key:
            return
        refs = aliases.setdefault(name, [])
        ref = {"type": ref_type, "key": key}
        if ref not in refs:
            refs.append(ref)

    for entry in stored_identifier_directory(root):
        key = str(entry.get("identifier"))
        kind = str(entry.get("kind") or "")
        display = _identifier_display(entry)
        record = {"key": key, "name": display, "kind": kind or None}
        if kind == "user":
            users[key] = record
            alias(display, "user", key)
        elif kind in {"workspace", "team"}:
            workspaces[key] = record
            alias(display, "workspace", key)
        elif kind == "channel":
            channels.setdefault(key, {}).update(record)
            alias(display, "channel", key)
    registry = messaging_registry(root)
    for channel in registry.get("channels", []) or []:
        if not isinstance(channel, dict):
            continue
        metadata = channel.get("metadata") if isinstance(channel.get("metadata"), dict) else {}
        cid = str(channel.get("id") or "")
        dash = _MM_DASH_RE.match(cid)
        key = str(channel.get("key") or (dash.group("key") if dash else "") or cid)
        record = channels.setdefault(key, {"key": key})
        record.update({"id": cid, "name": metadata.get("channel_name") or record.get("name")})
        alias(cid, "channel", key)
        alias(metadata.get("channel_name"), "channel", key)
        for name in channel.get("aliases") or []:
            alias(name, "channel", key)
        workspace_id = metadata.get("workspace_id")
        if isinstance(workspace_id, str) and workspace_id:
            workspaces.setdefault(workspace_id, {"key": workspace_id}).setdefault(
                "name", metadata.get("workspace_name")
            )
            alias(metadata.get("workspace_name"), "workspace", workspace_id)
            record["workspace"] = workspace_id
    return {"users": users, "workspaces": workspaces, "channels": channels, "aliases": aliases}


def _groom_channels(*, apply: bool = False) -> dict[str, Any]:
    """Merge duplicate channel spellings in messages.jsonl (dry-run by default).

    Applying rewrites the log in place (after a timestamped backup) as if the
    canonical ids always existed: every record's to/from/channel_id is
    remapped, registry snapshots and entity/config records are converted, each
    channel record gains ``entry_key`` (``entry_<n>`` in arrival order), and
    cursors are re-pointed at their equivalent position in the new file.
    """

    root = resolve_mailbox_root()
    path = root / "messages.jsonl"
    lines, old_ends = _read_all_lines(path)
    records: list[dict[str, Any] | None] = []
    for line in lines:
        try:
            parsed = json.loads(line.decode("utf-8"))
            records.append(parsed if isinstance(parsed, dict) else None)
        except (UnicodeDecodeError, json.JSONDecodeError):
            records.append(None)
    plan = _channel_alias_plan([r for r in records if r])
    mapping: dict[str, str] = {}
    for info in plan.values():
        for source in info["merges"]:
            if source != info["canonical"]:
                mapping[source] = info["canonical"]
    # Duplicate bridge/agent identities merge the same way channels do, and
    # legacy registry spellings fold into their canonical ``_registry`` ids —
    # including any remap_entry knowledge stored on the grooming registry.
    _refresh_remaps(root, force=True)
    mapping.update(_REMAPS_CACHE["agents"])
    mapping.update(_REMAPS_CACHE["channels"])
    touched = sum(
        1
        for record in records
        if record
        and any(record.get(field) in mapping for field in ("to", "from", "channel_id"))
    )
    summary = {
        "records": len([r for r in records if r]),
        "recordsToRemap": touched,
        "channels": {info["canonical"]: {
            "key": info["key"],
            "aliases": info["aliases"],
            "names": info["names"],
        } for info in plan.values()},
        "agents": {
            canonical: sorted(a for a, c in _REMAPS_CACHE["agents"].items() if c == canonical)
            for canonical in set(_REMAPS_CACHE["agents"].values())
        },
        "applied": False,
    }
    if not apply:
        return summary

    stamp = time.strftime("%Y%m%d-%H%M%S")
    if path.exists():
        shutil.copy2(path, path.with_name(f"messages.jsonl.groomed-{stamp}.bak"))
    subscriptions_path = root / "cursor_subscriptions.json"
    if subscriptions_path.exists():
        shutil.copy2(subscriptions_path, subscriptions_path.with_name(
            f"cursor_subscriptions.groomed-{stamp}.bak.json"))

    entry_counts: dict[str, int] = {}
    new_lines: list[bytes] = []
    new_ends: list[int] = []
    offset = 0
    for line, record in zip(lines, records):
        if record is None:
            new_lines.append(line)
            offset += len(line)
            new_ends.append(offset)
            continue
        # Legacy outbound_delivery drops split by content: endpoint evidence
        # means agent -> platform-channel, otherwise agent -> agent.
        for field in ("to", "channel_id"):
            if record.get(field) in OUTBOUND_LEGACY_IDS:
                record[field] = _split_outbound(record)
        for field in ("to", "from", "channel_id"):
            if record.get(field) in mapping:
                record[field] = mapping[record[field]]
        if record.get("type") == "messaging_registry":
            try:
                snapshot = json.loads(record.get("text") or "{}")
                if isinstance(snapshot, dict):
                    record["text"] = json.dumps(
                        _remap_registry_snapshot(snapshot, plan, mapping), ensure_ascii=False
                    )
            except json.JSONDecodeError:
                pass
        if record.get("config_for") in mapping:
            record["config_for"] = mapping[record["config_for"]]
        entry = record.get("entry")
        if (
            isinstance(entry, dict) and entry.get("id") in mapping
            # remap_entry/remap_usage ids ARE the legacy spellings — never
            # rewrite the remap knowledge itself.
            and record.get("type") not in ("remap_entry", "remap_usage")
        ):
            entry["id"] = mapping[entry["id"]]
        if not record.get("audit_of"):
            channel = record.get("channel_id") or record.get("to")
            if isinstance(channel, str) and channel:
                index = entry_counts.get(channel, 0)
                record["entry_key"] = f"entry_{index}"
                entry_counts[channel] = index + 1
        encoded = (json.dumps(record, ensure_ascii=False) + "\n").encode("utf-8")
        new_lines.append(encoded)
        offset += len(encoded)
        new_ends.append(offset)

    temporary = path.with_name(f"messages.jsonl.groomed-{stamp}.tmp")
    with temporary.open("wb") as stream:
        stream.writelines(new_lines)
    os.replace(temporary, path)
    with _TRAFFIC_LOCK:
        _TRAFFIC_STATE.update(path="", offset=0, checkpoint=b"", stats={})

    cursor_pairs = 0
    if _mailbox_client is not None:
        cursor_map = _cursor_map(root)
        # Fold aliased agents (and channels) together, keeping the furthest
        # consumed position per merged pair.
        consumed_by_agent: dict[str, dict[str, int]] = {}
        for agent, channel_ids in cursor_map.items():
            target = consumed_by_agent.setdefault(mapping.get(agent, agent), {})
            for cid in channel_ids:
                canonical = mapping.get(cid, cid)
                old_offset = _mailbox_client._read_cursor(
                    _mailbox_client._cursor_path(root, f"{cid}:{agent}")
                )
                count = bisect.bisect_right(old_ends, old_offset)
                target[canonical] = max(target.get(canonical, 0), count)
        remapped: dict[str, list[str]] = {}
        for agent, consumed in consumed_by_agent.items():
            for canonical, count in consumed.items():
                new_offset = new_ends[count - 1] if count else 0
                _mailbox_client._write_cursor(
                    _mailbox_client._cursor_path(root, f"{canonical}:{agent}"), new_offset
                )
                cursor_pairs += 1
            remapped[agent] = list(consumed)
        document = {"version": 1, "cursors": remapped}
        subscriptions_path.write_text(
            json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        # The registry doc itself converts to the canonical keyed scheme.
        groomed = _remap_registry_snapshot(messaging_registry(root), plan, mapping)
        try:
            _mailbox_client.send(
                REGISTRY_CHANNEL, "", sender=DEFAULT_USER_AGENT, root=root,
                message_type="messaging_registry",
                extra_fields={"text": json.dumps(groomed, ensure_ascii=False)},
                channel_id=REGISTRY_CHANNEL,
            )
            _mailbox_client.send(
                REGISTRY_CHANNEL, "", sender=DEFAULT_USER_AGENT, root=root,
                message_type="resolver_index",
                extra_fields={"index": _resolver_index(root)},
                channel_id=REGISTRY_CHANNEL,
            )
        except Exception:
            pass  # the rewrite already succeeded; refreshed docs are best effort
    summary.update(applied=True, cursorsRewritten=cursor_pairs,
                   entryCounts=entry_counts, backup=f"messages.jsonl.groomed-{stamp}.bak")
    return summary


def _channel_entry_ends(root: Path) -> dict[str, list[int]]:
    """channel -> byte end offset of each of its entries, in entry_N order.

    Uses the same affiliation rule as entry_key stamping (non-audit records,
    channel = channel_id or to), so ``bisect(ends, cursor_offset)`` converts a
    byte cursor into "entries consumed" and back.
    """

    ends: dict[str, list[int]] = {}
    offset = 0
    lines, _ = _read_all_lines(root / "messages.jsonl")
    for line in lines:
        offset += len(line)
        try:
            record = json.loads(line.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
        if not isinstance(record, dict) or record.get("audit_of"):
            continue
        channel = _fold_channel(record.get("channel_id") or record.get("to"))
        if channel in OUTBOUND_LEGACY_IDS or record.get("channel_id") in OUTBOUND_LEGACY_IDS \
                or record.get("to") in OUTBOUND_LEGACY_IDS:
            channel = _split_outbound(record)
        if isinstance(channel, str) and channel:
            ends.setdefault(channel, []).append(offset)
    return ends


def _sync_subscriptions() -> dict[str, Any]:
    """Project the subscription relation onto the durable registries.

    Subscription is explicit intent, cursors are just read positions — so each
    agent's ``agent_entry`` on ``server_agents_registry`` carries BOTH: a
    ``subscriptions`` map (channel -> "subscribed" | "unsubscribed", where
    "unsubscribed" is a sticky opt-out that subscribe-missing sweeps must
    honor) and the ``cursors`` map (offset + entry_N per channel). Channels an
    agent has a cursor on default to "subscribed" unless already opted out.
    Each channel's ``channel_entry`` on ``server_channels_registry`` carries the
    mirrored ``subscribers`` list (subscribed agents only). A subscription
    without a cursor is materialized: an offset-0 cursor (entry_0, nothing
    consumed yet) is auto-created and registered in cursor_subscriptions.json.
    """

    if _mailbox_client is None:
        return {"error": "mailbox_channels client is not installed"}
    root = resolve_mailbox_root()
    # Aliased bridge identities fold into their canonical agent, and blackboard
    # channels themselves never count as subscribing agents.
    cursor_map: dict[str, list[str]] = {}
    for raw_agent, channel_ids in _cursor_map(root).items():
        agent = _fold_agent(raw_agent)
        if agent in WELL_KNOWN_CHANNELS:
            continue
        merged = set(cursor_map.get(agent) or [])
        merged.update(channel_ids)
        cursor_map[agent] = sorted(merged)
    channel_subscribers: dict[str, set[str]] = {}
    for channel in messaging_registry(root).get("channels", []) or []:
        if isinstance(channel, dict) and isinstance(channel.get("id"), str):
            declared = channel_subscribers.setdefault(_fold_channel(channel["id"]), set())
            declared.update(
                _fold_agent(s)
                for s in (channel.get("subscribers") or [])
                if isinstance(s, str) and s and s not in WELL_KNOWN_CHANNELS
            )
    size = _messages_size(root)
    entry_ends = _channel_entry_ends(root)
    agents_written = 0
    autocursored = 0
    stored_agents: dict[str, dict[str, Any]] = {}
    for raw_agent, entry in stored_entity_entries(root, "agent_entry", AGENTS_CHANNEL).items():
        agent = _fold_agent(raw_agent)
        if agent in WELL_KNOWN_CHANNELS:
            continue
        target = stored_agents.setdefault(agent, {})
        merge_subs = target.get("subscriptions")
        for key, value in entry.items():
            target.setdefault(key, value)
        extra_subs = entry.get("subscriptions")
        if (isinstance(merge_subs, dict) and isinstance(extra_subs, dict)
                and merge_subs is not extra_subs):
            for cid, status in extra_subs.items():
                # Union alias subscriptions; a sticky opt-out wins on conflict.
                if str(status) == "unsubscribed" or cid not in merge_subs:
                    merge_subs[cid] = status
    agent_names = set(cursor_map)
    agent_names.update(m for ms in CHANNEL_MONITORS.values() for m in ms)
    for agent, entry in stored_agents.items():
        if isinstance(entry.get("subscriptions"), (list, dict)):
            agent_names.add(agent)
    for agent in sorted(agent_names):
        stored = dict(stored_agents.get(agent) or {})
        declared_subs = stored.get("subscriptions")
        subscriptions: dict[str, str] = {}
        if isinstance(declared_subs, dict):
            for cid, status in declared_subs.items():
                if isinstance(cid, str) and cid:
                    subscriptions[_fold_channel(cid)] = (
                        "unsubscribed" if str(status) == "unsubscribed" else "subscribed"
                    )
        elif isinstance(declared_subs, list):  # legacy list form -> all subscribed
            subscriptions = {
                _fold_channel(cid): "subscribed"
                for cid in declared_subs if isinstance(cid, str) and cid
            }
        cursor_channels = set(cursor_map.get(agent) or [])
        for cid, monitors in CHANNEL_MONITORS.items():
            # Designated monitors are subscribed to their service queue unless
            # they explicitly opted out (sticky "unsubscribed" wins).
            if agent in monitors:
                subscriptions.setdefault(cid, "subscribed")
        for cid in cursor_channels:
            subscriptions.setdefault(cid, "subscribed")
        for cid, status in subscriptions.items():
            if status == "subscribed":
                channel_subscribers.setdefault(cid, set()).add(agent)
                if cid not in cursor_channels:
                    # Autocursor: a subscription without a cursor gets one at
                    # offset 0 (entry_0 — nothing consumed yet).
                    _mailbox_client._write_cursor(
                        _mailbox_client._cursor_path(root, f"{cid}:{agent}"), 0
                    )
                    cursor_channels.add(cid)
                    autocursored += 1
            else:
                # Sticky opt-out: an old cursor never re-subscribes the agent.
                channel_subscribers.setdefault(cid, set()).discard(agent)
        cursor_map[agent] = sorted(cursor_channels)
        cursors: dict[str, dict[str, Any]] = {}
        for cid in sorted(cursor_channels):
            brief = _cursor_brief(root, cid, agent, size)
            # The byte offset is the fast path; the entry_N position survives
            # any future rewrite of the log, so cursors can be reconstructed.
            consumed = bisect.bisect_right(entry_ends.get(cid, []), brief["offset"])
            brief["entries_consumed"] = consumed
            brief["entry_next"] = f"entry_{consumed}"
            cursors[cid] = brief
        entry = stored
        entry["id"] = agent
        entry["subscriptions"] = dict(sorted(subscriptions.items()))
        entry["cursors"] = cursors
        _mailbox_client.send(
            AGENTS_CHANNEL, "", sender=DEFAULT_USER_AGENT, root=root,
            message_type="agent_entry", extra_fields={"entry": entry},
            channel_id=AGENTS_CHANNEL,
        )
        agents_written += 1
    channels_written = 0
    stored_channels = stored_entity_entries(root, "channel_entry", CHANNELS_CHANNEL)
    for cid, subscribers in sorted(channel_subscribers.items()):
        if not subscribers:
            continue
        entry = dict(stored_channels.get(cid) or {})
        entry["id"] = cid
        entry["subscribers"] = sorted(subscribers)
        _mailbox_client.send(
            CHANNELS_CHANNEL, "", sender=DEFAULT_USER_AGENT, root=root,
            message_type="channel_entry", extra_fields={"entry": entry},
            channel_id=CHANNELS_CHANNEL,
        )
        channels_written += 1
    if autocursored:
        document = {"version": 1, "cursors": {a: sorted(c) for a, c in sorted(cursor_map.items())}}
        (root / "cursor_subscriptions.json").write_text(
            json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    return {
        "agents": agents_written,
        "channels": channels_written,
        "autocursored": autocursored,
    }


def _set_subscription(agent: str, channel: str, state: str) -> dict[str, Any]:
    """Edit one explicit subscription setting, then re-project the registries.

    ``subscribed`` / ``unsubscribed`` write the sticky intent onto the agent's
    stored ``agent_entry``; ``remove`` clears the explicit setting so the
    default inference (cursor holders count as subscribed) takes over again.
    """

    if _mailbox_client is None:
        return {"error": "mailbox_channels client is not installed"}
    agent = _fold_agent(agent)
    channel = _fold_channel(channel)
    if not agent or not channel:
        return {"error": "agent and channel must not be empty"}
    if agent in WELL_KNOWN_CHANNELS:
        return {"error": f"{agent!r} is a well-known channel, not an agent"}
    if state not in ("subscribed", "unsubscribed", "remove"):
        return {"error": "state must be subscribed, unsubscribed or remove"}
    root = resolve_mailbox_root()
    entry = dict(stored_entity_entries(root, "agent_entry", AGENTS_CHANNEL).get(agent) or {})
    subscriptions = dict(entry.get("subscriptions") or {})
    if state == "remove":
        subscriptions.pop(channel, None)
    else:
        subscriptions[channel] = state
    entry["id"] = agent
    entry["subscriptions"] = subscriptions
    _mailbox_client.send(
        AGENTS_CHANNEL, "", sender=DEFAULT_USER_AGENT, root=root,
        message_type="agent_entry", extra_fields={"entry": entry},
        channel_id=AGENTS_CHANNEL,
    )
    sync = _sync_subscriptions()
    return {
        "agent": agent,
        "channel": channel,
        "state": state,
        "subscriptions": subscriptions,
        "sync": sync,
    }


def _set_remap(legacy: str, canonical: str, kind: str) -> dict[str, Any]:
    """Store one legacy->canonical remap on the grooming registry.

    The remap becomes data: a ``remap_entry`` record whose id IS the legacy
    spelling. The latest record per id wins; an empty (or self) canonical
    retires the remap — including the built-in seeds.
    """

    if _mailbox_client is None:
        return {"error": "mailbox_channels client is not installed"}
    legacy = legacy.strip()
    canonical = canonical.strip()
    kind = kind.strip().lower() or "channel"
    if not legacy:
        return {"error": "legacy spelling must not be empty"}
    if kind not in ("channel", "agent"):
        return {"error": "kind must be channel or agent"}
    service_ids = {
        REGISTRY_CHANNEL, AGENTS_CHANNEL, CHANNELS_CHANNEL, WORKER_QUEUE_CHANNEL,
        OUTBOUND_TO_CHANNEL_QUEUE, OUTBOUND_TO_AGENT_QUEUE, EVENTS_CHANNEL,
        GROOMING_CHANNEL,
    }
    if legacy in service_ids:
        return {"error": f"{legacy!r} is a canonical service channel; it cannot be remapped"}
    root = resolve_mailbox_root()
    retired = not canonical or canonical == legacy
    entry = {"id": legacy, "canonical": "" if retired else canonical, "kind": kind}
    _mailbox_client.send(
        GROOMING_CHANNEL, "", sender=DEFAULT_USER_AGENT, root=root,
        message_type="remap_entry", extra_fields={"entry": entry},
        channel_id=GROOMING_CHANNEL,
    )
    _refresh_remaps(root, force=True)
    return {
        "legacy": legacy,
        "canonical": entry["canonical"],
        "kind": kind,
        "action": "retired" if retired else "set",
        "channels": dict(_REMAPS_CACHE["channels"]),
        "agents": dict(_REMAPS_CACHE["agents"]),
    }


@router.get("/mailbox/resolve")
def mailbox_resolve(name: str = Query("")) -> dict[str, Any]:
    """The typed resolver: users / workspaces / channels maps keyed by UUID.

    With ``name`` returns just that alias's typed refs, e.g.
    ``test -> [{"type": "channel", "key": "<CHANNEL-UUID>"}]``.
    """

    index = _resolver_index(resolve_mailbox_root())
    wanted = name.strip()
    if wanted:
        return {"name": wanted, "refs": index["aliases"].get(wanted, [])}
    return index


def channel_config(root: Path, channel: str) -> dict[str, Any]:
    """Describe one channel: relay registry record enriched with traffic details.

    Registry channels contribute kind/channel_type/aliases/subscribers/metadata;
    agent mailboxes contribute agent_id/presences. Recent traffic supplies the
    human-readable ``channelName`` (e.g. Mattermost's channel_name), a message
    count, and the last-message timestamp. Configs edited in the UI are stored on
    the ``server_identifiers_registry`` channel and overlay everything else.
    """

    config: dict[str, Any] = {
        "id": channel,
        "kind": "mailbox",
        # Everyone gets to know about everything and can choose to ignore it:
        # every channel auto-subscribes by default; a stored config can opt out.
        "dont-autosubscribe": False,
    }
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

    traffic = _traffic_stats(root).get(channel) or {}
    traffic_name = traffic.get("channelName")
    messages = int(traffic.get("messages") or 0)
    last_timestamp = traffic.get("lastMessageAt")
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
    stored = stored_channel_config(root, channel)
    for key, value in stored.items():
        if key not in {"id", "messages", "lastMessageAt"}:
            config[key] = value
    return config


def channel_allows_autosubscribe(root: Path, channel: str) -> bool:
    """Whether addressing an agent on ``channel`` may auto-subscribe it.

    Everyone gets to know about everything and can choose to ignore it, so
    every channel defaults to ``dont-autosubscribe: false``. A stored
    channel_config edit can opt any channel out.
    """

    stored = stored_channel_config(root, channel)
    if "dont-autosubscribe" in stored:
        return not stored["dont-autosubscribe"]
    return True


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
    ``server_identifiers_registry`` channel, where the latest record per
    channel wins.
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


@router.post("/mailbox/entity")
def mailbox_entity_save(
    kind: str = Body(..., embed=True),
    id: str = Body(..., embed=True),
    entry: dict[str, Any] = Body(..., embed=True),
) -> dict[str, Any]:
    """Persist an edited entity JSON as a durable blackboard record.

    Agent entries go to ``server_agents_registry``, channel entries to
    ``server_channels_registry``, and relay/adapter_type entries to
    ``server_adapters_relays_registry``; the latest record per id wins.
    Computed fields (``cursors``/``messages``) are stripped before storing.
    """

    if _mailbox_client is None:
        raise HTTPException(status_code=503, detail="mailbox_channels client is not installed")
    kinds = {
        "agent": (AGENTS_CHANNEL, "agent_entry"),
        "channel": (CHANNELS_CHANNEL, "channel_entry"),
        "relay": (ADAPTERS_RELAYS_CHANNEL, "relay_entry"),
        "adapter_type": (ADAPTERS_RELAYS_CHANNEL, "adapter_type_entry"),
    }
    kind_id = kind.strip().lower() if isinstance(kind, str) else ""
    entity_id = id.strip() if isinstance(id, str) else ""
    if kind_id not in kinds:
        raise HTTPException(
            status_code=400,
            detail="kind must be 'agent', 'channel', 'relay' or 'adapter_type'",
        )
    if not entity_id:
        raise HTTPException(status_code=400, detail="id must not be empty")
    if not isinstance(entry, dict):
        raise HTTPException(status_code=400, detail="entry must be a JSON object")
    root = resolve_mailbox_root()
    target, message_type = kinds[kind_id]
    payload = {
        k: v
        for k, v in entry.items()
        if k not in ("cursors", "messages", "subscribers", "lastMessageAt")
    }
    payload["id"] = entity_id
    if kind_id in ("agent", "channel"):
        # authority: filename | channelname — decides whether source data
        # overwrites this entry at start; authority_copy_from: always | once —
        # with a filename authority, "once" stops re-copying after the first
        # materialization.
        payload.setdefault("authority", target)
        payload.setdefault("authority_copy_from", "always")
    try:
        _mailbox_client.send(
            target,
            "",
            sender=DEFAULT_USER_AGENT,
            root=root,
            message_type=message_type,
            extra_fields={"entry": payload},
            channel_id=target,
        )
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Storing entry failed: {error}") from error
    if kind_id == "agent":
        records = list_agents(root)
    elif kind_id == "channel":
        records = list_channels(root)
    else:
        registry = adapters_relays_registry(root)
        records = registry["relays" if kind_id == "relay" else "adapter_types"]
    fresh = next((item for item in records if item.get("id") == entity_id), payload)
    return {"kind": kind_id, "id": entity_id, "stored": True, "channel": target, "entry": fresh}


def _cursor_status(root: Path, channel: str, agent: str) -> dict[str, Any]:
    """Report where ``agent``'s cursor sits on ``channel`` (bytes + entry_N)."""

    channel = _fold_channel(channel)
    agent = _fold_agent(agent)
    size = _messages_size(root)
    brief = _cursor_brief(root, channel, agent, size)
    # The rewrite-proof position: how many of the channel's entries are behind
    # the byte offset, i.e. the next unread entry key.
    ends = _channel_entry_ends(root).get(channel, [])
    consumed = bisect.bisect_right(ends, brief["offset"])
    return {
        "channel": channel,
        "agent": agent,
        "size": size,
        **brief,
        "entries_consumed": consumed,
        "entry_next": f"entry_{consumed}",
        "entries_total": len(ends),
    }


@router.get("/mailbox/cursor")
def mailbox_cursor_status(channel: str = Query(...), agent: str = Query(...)) -> dict[str, Any]:
    if _mailbox_client is None:
        raise HTTPException(status_code=503, detail="mailbox_channels client is not installed")
    channel_id = channel.strip() if isinstance(channel, str) else ""
    agent_id = agent.strip() if isinstance(agent, str) else ""
    if not channel_id or not agent_id:
        raise HTTPException(status_code=400, detail="channel and agent are required")
    return _cursor_status(resolve_mailbox_root(), channel_id, agent_id)


@router.post("/mailbox/cursor")
def mailbox_cursor_set(
    channel: str = Body(..., embed=True),
    agent: str = Body(..., embed=True),
    start: str = Body("now", embed=True),
) -> dict[str, Any]:
    """Move ``agent``'s cursor on ``channel`` to the beginning or to now.

    An existing cursor file is repositioned in place; a missing one is
    initialized (which also registers the subscription).
    """

    if _mailbox_client is None:
        raise HTTPException(status_code=503, detail="mailbox_channels client is not installed")
    channel_id = channel.strip() if isinstance(channel, str) else ""
    agent_id = agent.strip() if isinstance(agent, str) else ""
    normalized = start.strip().lower() if isinstance(start, str) else "now"
    if not channel_id or not agent_id:
        raise HTTPException(status_code=400, detail="channel and agent are required")
    channel_id = _fold_channel(channel_id)
    agent_id = _fold_agent(agent_id)
    if normalized not in {"beginning", "start", "now"}:
        raise HTTPException(status_code=400, detail="start must be 'beginning' or 'now'")
    root = resolve_mailbox_root()
    path = _mailbox_client._cursor_path(root, f"{channel_id}:{agent_id}")
    try:
        if path.exists():
            offset = 0 if normalized in {"beginning", "start"} else _messages_size(root)
            _mailbox_client._write_cursor(path, offset)
            # Back-fill the subscriptions map so both the agent JSON and the
            # channel JSON list this cursor in their computed cursor maps.
            _mailbox_client._remember_cursor_subscription(root, agent_id, channel_id)
            action = "repositioned"
        else:
            _mailbox_client.initialize_cursor(
                channel_id, cursor=agent_id, start=normalized, root=root
            )
            action = "initialized"
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Cursor update failed: {error}") from error
    try:
        # Setting a cursor makes you a subscriber: mirror it into the relay's
        # registry subscriber list (the inverse of what remove does).
        _mailbox_client._rest_request(
            "POST",
            "/v1/subscriptions",
            {"channel": channel_id, "identity": agent_id, "subscribed": True},
        )
    except Exception:
        pass  # relay subscriber list is advisory here
    status = _cursor_status(root, channel_id, agent_id)
    status["action"] = action
    status["start"] = normalized
    return status


def _forget_cursor_subscription(root: Path, agent: str, channel: str) -> bool:
    """Drop ``channel`` from ``agent``'s cursor list in cursor_subscriptions.json."""

    path = root / "cursor_subscriptions.json"
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return False
    cursors = document.get("cursors") or {}
    entries = [str(item) for item in cursors.get(agent, [])]
    if channel not in entries:
        return False
    remaining = [item for item in entries if item != channel]
    if remaining:
        cursors[agent] = remaining
    else:
        cursors.pop(agent, None)
    document["cursors"] = cursors
    path.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return True


@router.delete("/mailbox/cursor")
def mailbox_cursor_remove(channel: str = Query(...), agent: str = Query(...)) -> dict[str, Any]:
    """Remove ``agent``'s cursor on ``channel`` entirely (no cursor set).

    Deletes the cursor file, forgets the cursor subscription, and best-effort
    clears the registry subscriber entry on the relay.
    """

    if _mailbox_client is None:
        raise HTTPException(status_code=503, detail="mailbox_channels client is not installed")
    channel_id = channel.strip() if isinstance(channel, str) else ""
    agent_id = agent.strip() if isinstance(agent, str) else ""
    if not channel_id or not agent_id:
        raise HTTPException(status_code=400, detail="channel and agent are required")
    channel_id = _fold_channel(channel_id)
    agent_id = _fold_agent(agent_id)
    root = resolve_mailbox_root()
    path = _mailbox_client._cursor_path(root, f"{channel_id}:{agent_id}")
    existed = path.exists()
    try:
        path.unlink(missing_ok=True)
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Cursor remove failed: {error}") from error
    forgotten = _forget_cursor_subscription(root, agent_id, channel_id)
    try:
        _mailbox_client._rest_request(
            "POST",
            "/v1/subscriptions",
            {"channel": channel_id, "identity": agent_id, "subscribed": False},
        )
    except Exception:
        pass  # relay subscriber list is advisory here
    status = _cursor_status(root, channel_id, agent_id)
    status["action"] = "removed" if (existed or forgotten) else "absent"
    return status


@router.post("/mailbox/subscription")
def mailbox_subscription(
    agent: str = Body(..., embed=True),
    channel: str = Body(..., embed=True),
    state: str = Body(..., embed=True),
) -> dict[str, Any]:
    """Set or clear one explicit subscription (also worker op set_subscription)."""

    result = _set_subscription(
        agent.strip() if isinstance(agent, str) else "",
        channel.strip() if isinstance(channel, str) else "",
        state.strip().lower() if isinstance(state, str) else "",
    )
    if "error" in result:
        code = 503 if "not installed" in result["error"] else 400
        raise HTTPException(status_code=code, detail=result["error"])
    return result


@router.post("/mailbox/remap")
def mailbox_remap(
    legacy: str = Body(..., embed=True),
    canonical: str = Body("", embed=True),
    kind: str = Body("channel", embed=True),
) -> dict[str, Any]:
    """Store one legacy->canonical remap (empty canonical retires it)."""

    result = _set_remap(
        legacy if isinstance(legacy, str) else "",
        canonical if isinstance(canonical, str) else "",
        kind if isinstance(kind, str) else "channel",
    )
    if "error" in result:
        code = 503 if "not installed" in result["error"] else 400
        raise HTTPException(status_code=code, detail=result["error"])
    return result


@router.get("/mailbox/remaps")
def mailbox_remaps() -> dict[str, Any]:
    """The merged fold maps plus the cumulative fold-usage counters."""

    root = resolve_mailbox_root()
    _refresh_remaps(root, force=True)
    _flush_remap_usage(root, force=True)
    usage = sorted(
        _raw_grooming_entries(root, "remap_usage").values(),
        key=lambda item: str(item.get("id") or ""),
    )
    return {
        "channels": dict(_REMAPS_CACHE["channels"]),
        "agents": dict(_REMAPS_CACHE["agents"]),
        "usage": usage,
    }


@router.get("/mailbox/adapters-relays")
def mailbox_adapters_relays() -> dict[str, Any]:
    """The adapters/relays registry: adapter types + relay presences."""

    return adapters_relays_registry(resolve_mailbox_root())


@router.get("/mailbox/messages")
def mailbox_messages(
    user: str = Query(DEFAULT_USER_AGENT),
    peer: str = Query(DEFAULT_PEER_AGENT),
    channel: str | None = None,
    to: str | None = Query(None),
    sender: str | None = Query(None, alias="from"),
    channel_id: str | None = Query(None),
    text: str | None = Query(None),
    require: bool = Query(False, alias="filter"),
    limit: int = Query(200, ge=1, le=2000),
) -> dict[str, Any]:
    root = resolve_mailbox_root()
    names = identifier_names(root)

    # Direct (non-HTTP) callers leave FastAPI's Query sentinels in place;
    # treat anything that is not a real value as unset.
    def _opt(value: Any) -> str | None:
        return value if isinstance(value, str) and value else None

    to, sender, channel_id, text = _opt(to), _opt(sender), _opt(channel_id), _opt(text)
    require = require is True
    if require or to or sender or channel_id or text:
        # Require-match mode: look everywhere, then AND the given constraints.
        messages = filtered_messages(
            root, to=to, sender=sender, channel=channel,
            channel_id=channel_id, text=text, limit=limit, names=names,
        )
    elif channel:
        messages = channel_messages(root, channel, limit=limit, names=names)
    else:
        messages = thread_messages(root, user, peer, limit=limit, names=names)
    return {
        "messages": messages,
        "user": user,
        "peer": peer,
        "channel": channel,
        "filters": {
            "to": to, "from": sender, "channel": channel,
            "channelId": channel_id, "text": text,
        } if (require or to or sender or channel_id or text) else None,
        "mailboxDir": str(root),
    }


@router.post("/mailbox/send")
def mailbox_send(
    text: str = Body(..., embed=True),
    to: str = Body(DEFAULT_PEER_AGENT, embed=True),
    sender: str = Body(DEFAULT_USER_AGENT, embed=True),
    channel_id: str | None = Body(None, embed=True),
    copy_of: str | None = Body(None, embed=True),
) -> dict[str, Any]:
    if _mailbox_client is None:
        raise HTTPException(status_code=503, detail="mailbox_channels client is not installed")
    if not text.strip():
        raise HTTPException(status_code=400, detail="Message text must not be empty")
    reference = copy_of.strip() if isinstance(copy_of, str) else ""
    if reference and not re.fullmatch(r".+/entry_\d+", reference):
        raise HTTPException(
            status_code=400, detail="copy_of must look like 'mailbox-id/entry_n'"
        )
    # Agent aliases fold on send; channel spellings are kept raw so legacy
    # readers (e.g. the sibling relay watching outbound_delivery) still match.
    to = _fold_agent(to)
    channel = (channel_id.strip() or None) if isinstance(channel_id, str) else None
    root = resolve_mailbox_root()
    # Addressing an agent on a channel auto-subscribes it unless the stored
    # channel config opts that channel out.
    subscribed = (
        subscribe_agent_to_channel(to, channel)
        if channel and channel_allows_autosubscribe(root, channel)
        else False
    )
    extra = {"channel_id": channel} if channel else {}
    # Secret per-channel message key: the record BELONGS to channel (or the
    # ``to`` mailbox) and gets the next ``entry_<n>`` — always max+1, so keys
    # stay unique even after settled entries are deleted.
    affiliation = channel or to
    stats_entry = _traffic_stats(root).get(affiliation) or {}
    next_index = int(stats_entry.get("nextEntry") or stats_entry.get("entries") or 0)
    extra["extra_fields"] = {"entry_key": f"entry_{next_index}"}
    if reference:
        # A forwarded/relayed copy keeps a pointer to its original entry, so
        # readers can trace it back (and dedupe) across sequences.
        extra["extra_fields"]["copy_of"] = reference
    try:
        record = _mailbox_client.send(to, text, sender=sender, root=root, **extra)
    except Exception as error:  # surface send failures as a 500 with detail
        raise HTTPException(status_code=500, detail=f"Mailbox send failed: {error}") from error
    return {"message": _project_record(record), "subscribed": subscribed}
