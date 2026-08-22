"""HTTP surface for the mailbox-admin chat UI, on the per-mailbox JSON store.

This module is intentionally small: it exposes only what ``ChatConversation.tsx``
consumes — viewing and editing the remote mailboxes and the ``server_registry_*``
objects. Every mailbox is an object in the ``mailbox_channels`` per-mailbox JSON
store; there is no legacy ``messages.jsonl`` here.

Endpoints (mounted under ``/api``):

* ``GET  /mailbox/agents``            -> {"agents":  [{"id", ...}]}
* ``POST /mailbox/agents``  {id}      -> register an agent
* ``GET  /mailbox/mailboxes``         -> {"mailboxes":[{"id","kind","messages","name"}]}
* ``POST /mailbox/mailboxes`` {id}    -> add a mailbox (its .json document)
* ``DELETE /mailbox/mailboxes`` {id}  -> delete a mailbox (its .json document)
* ``GET  /mailbox/messages``          -> {"messages":[...], "user", "peer"} (both directions)
* ``POST /mailbox/send``              -> append a message
* ``POST /mailbox/record``            -> edit one record in place or at-end
* ``GET/POST /mailbox/mailbox-config``-> read/store a mailbox config object
* ``GET/POST/DELETE /mailbox/cursor`` -> inspect/move/clear an agent's cursor
* ``POST /mailbox/subscription``      -> set/clear subscription intent
* ``POST /mailbox/entity``            -> edit an agent/mailbox registry object
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter, Body, HTTPException, Query

try:  # The client ships as an installed package (mailbox_channel/src/mailbox_channels).
    from mailbox_channels import agent_mailbox as _mailbox_client
    from mailbox_channels import channel_store
    from mailbox_channels import connector_registry
    from mailbox_channels import subscriptions as _subscriptions
except Exception:  # pragma: no cover - client absent in some envs
    _mailbox_client = None
    channel_store = None
    connector_registry = None
    _subscriptions = None

router = APIRouter()


# ── roots and helpers ────────────────────────────────────────────────────────

def _root() -> Path:
    if _mailbox_client is None:
        raise HTTPException(status_code=503, detail="mailbox_channels client is not installed")
    return _mailbox_client.mailbox_dir()


def _require_client() -> None:
    if _mailbox_client is None or channel_store is None:
        raise HTTPException(status_code=503, detail="mailbox_channels client is not installed")


def _agent_ids(root: Path) -> set[str]:
    try:
        return {str(item.get("agent_id") or item.get("id") or "")
                for item in connector_registry.public_registry(root).get("agents", [])}
    except Exception:
        return set()


def _mailbox_doc_for(root: Path, agent_id: str) -> str:
    """The mailbox document that holds an agent's direct messages."""
    try:
        return connector_registry.agent_mailbox_address(agent_id, root)
    except Exception:
        return agent_id.replace("-", "_")


def _mailbox_docs_for(root: Path, identity: str) -> list[str]:
    """Docs that can hold an identity's direct messages.

    ``send`` stores a record in the doc named by its ``to`` field: the literal
    identity for unregistered names, or the registry mailbox address (underscored
    twin) for registered agents. Try both so either case renders.
    """
    docs = [identity]
    resolved = _mailbox_doc_for(root, identity)
    if resolved and resolved not in docs:
        docs.append(resolved)
    return docs


def _mailbox_message_count(root: Path, mailbox_id: str) -> int:
    try:
        document = channel_store.load_channel(root, mailbox_id)
    except Exception:
        return 0
    return len(document.get("messages") or {})


def _record_to_message(record: dict[str, Any]) -> dict[str, Any]:
    """Map a stored record to the ChatMessage shape the UI reads."""
    return {
        "id": record.get("id") or record.get("entry_number") or "",
        "timestamp": record.get("timestamp"),
        "from": record.get("from"),
        "to": record.get("to"),
        "text": record.get("text") or "",
        "type": record.get("type"),
        "mailboxId": record.get("channel_id"),
        "author": record.get("author") or record.get("from"),
        "authorName": record.get("author_name"),
        "mailboxName": record.get("channel_name"),
        "raw": record,
    }


def _iter_mailbox_records(root: Path, mailbox_id: str) -> list[dict[str, Any]]:
    try:
        document = channel_store.load_channel(root, mailbox_id)
    except Exception:
        return []
    return [record for _key, record in channel_store.ordered_messages(document)]


# ── directory: agents and mailboxes ──────────────────────────────────────────

@router.get("/mailbox/agents")
def mailbox_agents() -> dict[str, Any]:
    _require_client()
    root = _root()
    agents = []
    for item in connector_registry.public_registry(root).get("agents", []):
        agent_id = str(item.get("agent_id") or item.get("id") or "")
        if not agent_id:
            continue
        agents.append({**item, "id": agent_id})
    return {"agents": agents}


@router.post("/mailbox/agents")
def mailbox_add_agent(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    _require_client()
    agent_id = str(payload.get("id") or "").strip()
    if not agent_id:
        raise HTTPException(status_code=400, detail="id is required")
    root = _root()
    try:
        connector_registry.register_agent(agent_id, path=root)
    except Exception as error:  # already registered or validation error
        raise HTTPException(status_code=400, detail=str(error))
    return {"id": agent_id, "created": True}


@router.get("/mailbox/mailboxes")
def mailbox_list() -> dict[str, Any]:
    """List mailboxes — every per-mailbox ``.json`` document in the store.

    Registry documents (``sub_kind == "ordered_id_channel"``) are not mailboxes
    and are excluded.
    """
    _require_client()
    root = _root()
    mailboxes = []
    for mid in channel_store.channel_ids(root):
        document = channel_store.load_channel(root, mid)
        if document.get("sub_kind") == "ordered_id_channel":
            continue
        mailboxes.append({
            "id": mid,
            "kind": document.get("sub_kind") or "mailbox",
            "messages": len(document.get("messages") or {}),
            "name": document.get("name"),
        })
    return {"mailboxes": mailboxes}


@router.post("/mailbox/mailboxes")
def mailbox_add(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """Add a mailbox: create its per-mailbox ``.json`` document if absent."""
    _require_client()
    mailbox_id = str(payload.get("id") or "").strip()
    if not mailbox_id:
        raise HTTPException(status_code=400, detail="id is required")
    root = _root()
    path = channel_store.channel_path(root, mailbox_id)
    if not path.exists():
        channel_store.save_channel(root, channel_store.load_channel(root, mailbox_id))
    return {"id": mailbox_id, "created": True}


@router.delete("/mailbox/mailboxes")
def mailbox_delete(id: str = Query(...)) -> dict[str, Any]:  # noqa: A002 - matches UI param
    """Delete a mailbox: remove its per-mailbox ``.json`` document."""
    _require_client()
    mailbox_id = str(id or "").strip()
    if not mailbox_id:
        raise HTTPException(status_code=400, detail="id is required")
    root = _root()
    path = channel_store.channel_path(root, mailbox_id)
    existed = path.exists()
    if existed:
        path.unlink()
    return {"id": mailbox_id, "deleted": existed}


# ── messages (two-way, non-consuming) ────────────────────────────────────────

@router.get("/mailbox/messages")
def mailbox_messages(
    to: str | None = Query(None),
    sender: str | None = Query(None, alias="from"),
    mailbox: str | None = Query(None),
    send_to: str | None = Query(None),
    text: str | None = Query(None),
    limit: int = Query(300),
    filter: bool = Query(False),  # noqa: A002 - matches the UI query param
) -> dict[str, Any]:
    _require_client()
    root = _root()

    # Which documents hold the conversation: an explicit mailbox, or the two
    # participants' mailboxes for a direct thread.
    doc_ids: list[str] = []
    if send_to:
        doc_ids.append(send_to)
    if mailbox and mailbox not in doc_ids:
        doc_ids.append(mailbox)
    if not doc_ids:
        for identity in (to, sender):
            if identity:
                for doc in _mailbox_docs_for(root, identity):
                    if doc not in doc_ids:
                        doc_ids.append(doc)

    records: list[dict[str, Any]] = []
    seen: set[str] = set()
    for mid in doc_ids:
        for record in _iter_mailbox_records(root, mid):
            rid = str(record.get("id") or "")
            if rid and rid in seen:
                continue
            if rid:
                seen.add(rid)
            records.append(record)

    def keep(record: dict[str, Any]) -> bool:
        if filter and to and record.get("to") != to and record.get("from") != to:
            return False
        if filter and sender and record.get("from") != sender and record.get("to") != sender:
            return False
        if filter and text and text not in (record.get("text") or ""):
            return False
        return True

    filtered = [r for r in records if keep(r)]
    filtered.sort(key=lambda r: str(r.get("timestamp") or ""))
    messages = [_record_to_message(r) for r in filtered[-max(1, limit):]]
    return {"messages": messages, "user": sender or "", "peer": to or ""}


@router.post("/mailbox/send")
def mailbox_send(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    _require_client()
    text = str(payload.get("text") or "")
    to = str(payload.get("to") or "").strip()
    if not to:
        raise HTTPException(status_code=400, detail="to is required")
    sender = str(payload.get("sender") or _mailbox_client.DEFAULT_SENDER)
    send_to = payload.get("send_to") or None
    root = _root()
    record = _mailbox_client.send(to, text, sender=sender, channel_id=send_to, root=root)
    return {"message": record}


# ── per-record edit (in place / at end) ──────────────────────────────────────

def _find_record(root: Path, record_id: str) -> tuple[str, str, dict[str, Any]] | None:
    """Return (mailbox_id, entry_key, record) for the newest match by id."""
    for mid in channel_store.channel_ids(root):
        document = channel_store.load_channel(root, mid)
        for key, record in (document.get("messages") or {}).items():
            if isinstance(record, dict) and str(record.get("id") or "") == record_id:
                return mid, key, record
    return None


@router.post("/mailbox/record")
def mailbox_record(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    _require_client()
    record_id = str(payload.get("id") or "").strip()
    new_record = payload.get("record")
    mode = str(payload.get("mode") or "in-place")
    if not record_id or not isinstance(new_record, dict):
        raise HTTPException(status_code=400, detail="id and record object are required")
    root = _root()
    found = _find_record(root, record_id)
    if found is None:
        raise HTTPException(status_code=404, detail=f"no record with id {record_id!r}")
    mailbox_id, entry_key, old_record = found
    document = channel_store.load_channel(root, mailbox_id)
    if mode == "at-end":
        count = int(document.get("count") or 0)
        new_key = f"entry_{count}"
        stored = {**new_record, "entry_number": new_key}
        document.setdefault("messages", {})[new_key] = stored
        document["count"] = count + 1
        old = document["messages"].get(entry_key)
        if isinstance(old, dict):
            old["replaced-by"] = new_key
        channel_store.save_channel(root, document)
        return {"entryKey": new_key, "mailbox": mailbox_id, "record": stored}
    # in-place: keep the entry key, replace its contents.
    stored = {**new_record, "entry_number": entry_key}
    document.setdefault("messages", {})[entry_key] = stored
    channel_store.save_channel(root, document)
    return {"entryKey": entry_key, "mailbox": mailbox_id, "record": stored}


# ── mailbox config object ────────────────────────────────────────────────────

def _config_id(mailbox: str) -> str:
    return f"channel_config:{mailbox}"


@router.get("/mailbox/mailbox-config")
def mailbox_get_config(mailbox: str = Query(...)) -> dict[str, Any]:
    _require_client()
    root = _root()
    entry = channel_store.get_entry(root, channel_store.IDENTIFIERS_REGISTRY, _config_id(mailbox))
    config = (entry or {}).get("payload") if isinstance(entry, dict) else None
    return {"mailbox": mailbox, "config": config or {}}


@router.post("/mailbox/mailbox-config")
def mailbox_set_config(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    _require_client()
    mailbox = str(payload.get("mailbox") or "").strip()
    config = payload.get("config")
    if not mailbox or not isinstance(config, dict):
        raise HTTPException(status_code=400, detail="mailbox and config object are required")
    root = _root()
    subscribed: list[str] = []
    for name in config.get("subscribers") or []:
        name = str(name).strip()
        if not name:
            continue
        try:
            _subscriptions.set_subscription(mailbox, name, enabled=True, path=root)
            subscribed.append(name)
        except Exception:
            pass
    channel_store.put_entry(root, channel_store.IDENTIFIERS_REGISTRY, _config_id(mailbox), config)
    return {"mailbox": mailbox, "config": config, "subscribed": subscribed}


# ── cursor inspect / move / clear ────────────────────────────────────────────

def _cursor_info(root: Path, mailbox: str, agent: str) -> dict[str, Any]:
    total = _mailbox_message_count(root, mailbox)
    state = channel_store.get_cursor(root, agent, mailbox)
    consumed = int((state or {}).get("consumed") or 0)
    return {
        "mailbox": mailbox,
        "agent": agent,
        "initialized": state is not None,
        "offset": consumed,
        "size": total,
        "behind": max(0, total - consumed),
        "entries_consumed": consumed,
        "entry_next": (state or {}).get("next"),
        "entries_total": total,
    }


@router.get("/mailbox/cursor")
def mailbox_cursor(mailbox: str = Query(...), agent: str = Query(...)) -> dict[str, Any]:
    _require_client()
    return _cursor_info(_root(), mailbox, agent)


@router.post("/mailbox/cursor")
def mailbox_move_cursor(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    _require_client()
    mailbox = str(payload.get("mailbox") or "").strip()
    agent = str(payload.get("agent") or "").strip()
    start = str(payload.get("start") or "now")
    if not mailbox or not agent:
        raise HTTPException(status_code=400, detail="mailbox and agent are required")
    root = _root()
    total = _mailbox_message_count(root, mailbox)
    next_index = 0 if start == "beginning" else total
    channel_store.set_cursor(root, agent, mailbox, next_index)
    return _cursor_info(root, mailbox, agent)


@router.delete("/mailbox/cursor")
def mailbox_clear_cursor(mailbox: str = Query(...), agent: str = Query(...)) -> dict[str, Any]:
    _require_client()
    root = _root()
    try:
        channel_store.delete_cursors(root, owners={agent}, channels={mailbox})
    except Exception:
        pass
    return _cursor_info(root, mailbox, agent)


# ── subscription intent ──────────────────────────────────────────────────────

@router.post("/mailbox/subscription")
def mailbox_subscription(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    _require_client()
    agent = str(payload.get("agent") or "").strip()
    mailbox = str(payload.get("mailbox") or "").strip()
    state = str(payload.get("state") or "").strip()
    if not agent or not mailbox or state not in {"subscribed", "unsubscribed", "remove"}:
        raise HTTPException(status_code=400, detail="agent, mailbox and a valid state are required")
    root = _root()
    # There is no tri-state subscription; "remove" reverts to the default
    # inference by clearing the explicit subscribed entry (i.e. unsubscribe).
    enabled = state == "subscribed"
    _subscriptions.set_subscription(mailbox, agent, enabled=enabled, path=root)
    return {"agent": agent, "mailbox": mailbox, "state": state}


# ── registry object edit (agent / mailbox) ───────────────────────────────────

@router.post("/mailbox/entity")
def mailbox_entity(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    _require_client()
    kind = str(payload.get("kind") or "").strip()
    entity_id = str(payload.get("id") or "").strip()
    entry = payload.get("entry")
    if kind not in {"agent", "mailbox"} or not entity_id or not isinstance(entry, dict):
        raise HTTPException(status_code=400, detail="kind (agent|mailbox), id and entry object are required")
    root = _root()
    registry = channel_store.AGENTS_REGISTRY if kind == "agent" else channel_store.CHANNELS_REGISTRY
    stored = channel_store.put_entry(root, registry, entity_id, entry)
    saved = stored.get("payload") if isinstance(stored, dict) and "payload" in stored else entry
    return {"kind": kind, "id": entity_id, "entry": saved, "mailbox": registry}
