"""HTTP tests for the rebuilt mailbox admin backend (mailbox_api_lib).

Exercises the endpoints the chat UI (ChatConversation.tsx) calls, over the new
per-mailbox JSON store, through a FastAPI TestClient so query params resolve the
same way they do in production.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

import mailbox_api_lib


@pytest.fixture()
def client(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> TestClient:
    monkeypatch.setenv("AGENT_MAILBOX_DIR", str(tmp_path))
    app = FastAPI()
    app.include_router(mailbox_api_lib.router, prefix="/api")
    return TestClient(app)


def test_send_then_read_two_way(client: TestClient) -> None:
    client.post("/api/mailbox/send", json={"text": "hi there", "to": "peer-agent", "sender": "user-agent"})
    client.post("/api/mailbox/send", json={"text": "reply back", "to": "user-agent", "sender": "peer-agent"})
    payload = client.get("/api/mailbox/messages",
                         params={"from": "user-agent", "to": "peer-agent", "filter": "1"}).json()
    texts = sorted(m["text"] for m in payload["messages"])
    assert texts == ["hi there", "reply back"]
    assert payload["user"] == "user-agent" and payload["peer"] == "peer-agent"


def test_mailboxes_add_list_delete(client: TestClient) -> None:
    # Listing mailboxes is always allowed.
    assert client.get("/api/mailbox/mailboxes").status_code == 200
    # Add, list, then delete the mailbox .json doc.
    assert client.post("/api/mailbox/mailboxes", json={"id": "team-updates"}).json()["created"] is True
    ids = [c["id"] for c in client.get("/api/mailbox/mailboxes").json()["mailboxes"]]
    assert "team-updates" in ids
    assert client.request("DELETE", "/api/mailbox/mailboxes", params={"id": "team-updates"}).json()["deleted"] is True


def test_agents_create_and_list(client: TestClient) -> None:
    assert client.post("/api/mailbox/agents", json={"id": "review-agent"}).json()["created"] is True
    ids = [a["id"] for a in client.get("/api/mailbox/agents").json()["agents"]]
    assert "review-agent" in ids


def test_entity_edit_writes_registry_object(client: TestClient) -> None:
    payload = client.post("/api/mailbox/entity",
                          json={"kind": "agent", "id": "review-agent",
                                "entry": {"id": "review-agent", "note": "hello"}}).json()
    assert payload["mailbox"] == "server_registry_agents"
    assert payload["entry"]["note"] == "hello"


def test_mailbox_config_roundtrip_and_subscribe(client: TestClient) -> None:
    saved = client.post("/api/mailbox/mailbox-config",
                        json={"mailbox": "team", "config": {"title": "Team", "subscribers": ["user-agent"]}}).json()
    assert saved["subscribed"] == ["user-agent"]
    got = client.get("/api/mailbox/mailbox-config", params={"mailbox": "team"}).json()
    assert got["config"]["title"] == "Team"


def test_cursor_shape_and_move(client: TestClient) -> None:
    client.post("/api/mailbox/send", json={"text": "a", "to": "peer-agent", "sender": "user-agent"})
    mailbox = mailbox_api_lib._mailbox_doc_for(mailbox_api_lib._root(), "peer-agent")
    info = client.get("/api/mailbox/cursor", params={"mailbox": mailbox, "agent": "user-agent"}).json()
    for key in ("mailbox", "agent", "initialized", "offset", "size", "behind",
                "entries_consumed", "entry_next", "entries_total"):
        assert key in info
    moved = client.post("/api/mailbox/cursor", json={"mailbox": mailbox, "agent": "user-agent", "start": "now"}).json()
    assert moved["initialized"] is True


def test_record_edit_in_place_and_at_end(client: TestClient) -> None:
    sent = client.post("/api/mailbox/send",
                       json={"text": "original", "to": "peer-agent", "sender": "user-agent"}).json()
    rid = sent["message"]["id"]
    at_end = client.post("/api/mailbox/record",
                         json={"id": rid, "record": {**sent["message"], "text": "edited"}, "mode": "at-end"}).json()
    assert at_end["entryKey"].startswith("entry_")
