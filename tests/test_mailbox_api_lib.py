"""HTTP tests for the rebuilt mailbox admin backend (mailbox_api_lib).

Exercises the endpoints the chat UI (ChatConversation.tsx) calls, over the new
per-mailbox JSON store, through a FastAPI TestClient so query params resolve the
same way they do in production.
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

import mailbox_api_lib


@pytest.fixture()
def client(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> TestClient:
    monkeypatch.setenv("AGENT_MAILBOX_DIR", str(tmp_path))
    app = FastAPI()
    app.include_router(mailbox_api_lib.router, prefix="/workbench")
    return TestClient(app)


def test_send_then_read_two_way(client: TestClient) -> None:
    client.post("/workbench/mailbox/send", json={"text": "hi there", "to": "peer-agent", "sender": "user-agent"})
    client.post("/workbench/mailbox/send", json={"text": "reply back", "to": "user-agent", "sender": "peer-agent"})
    payload = client.get("/workbench/mailbox/messages",
                         params={"from": "user-agent", "to": "peer-agent", "filter": "1"}).json()
    texts = sorted(m["text"] for m in payload["messages"])
    assert texts == ["hi there", "reply back"]
    assert payload["user"] == "user-agent" and payload["peer"] == "peer-agent"


def test_mailboxes_add_list_delete(client: TestClient) -> None:
    # Listing mailboxes is always allowed.
    assert client.get("/workbench/mailbox/mailboxes").status_code == 200
    # Add, list, then delete the mailbox .json doc.
    assert client.post("/workbench/mailbox/mailboxes", json={"id": "team-updates"}).json()["created"] is True
    ids = [c["id"] for c in client.get("/workbench/mailbox/mailboxes").json()["mailboxes"]]
    assert "team-updates" in ids
    assert client.request("DELETE", "/workbench/mailbox/mailboxes", params={"id": "team-updates"}).json()["deleted"] is True


def test_agents_create_and_list(client: TestClient) -> None:
    assert client.post("/workbench/mailbox/agents", json={"id": "review-agent"}).json()["created"] is True
    ids = [a["id"] for a in client.get("/workbench/mailbox/agents").json()["agents"]]
    assert "review-agent" in ids


def test_entity_edit_writes_registry_object(client: TestClient) -> None:
    payload = client.post("/workbench/mailbox/entity",
                          json={"kind": "agent", "id": "review-agent",
                                "entry": {"id": "review-agent", "note": "hello"}}).json()
    assert payload["mailbox"] == "server_registry_agents"
    assert payload["entry"]["note"] == "hello"


def test_mailbox_config_roundtrip_and_subscribe(client: TestClient) -> None:
    saved = client.post("/workbench/mailbox/mailbox-config",
                        json={"mailbox": "team", "config": {"title": "Team", "subscribers": ["user-agent"]}}).json()
    assert saved["subscribed"] == ["user-agent"]
    got = client.get("/workbench/mailbox/mailbox-config", params={"mailbox": "team"}).json()
    assert got["config"]["title"] == "Team"


def test_cursor_shape_and_move(client: TestClient) -> None:
    client.post("/workbench/mailbox/send", json={"text": "a", "to": "peer-agent", "sender": "user-agent"})
    mailbox = mailbox_api_lib._mailbox_doc_for(mailbox_api_lib._root(), "peer-agent")
    info = client.get("/workbench/mailbox/cursor", params={"mailbox": mailbox, "agent": "user-agent"}).json()
    for key in ("mailbox", "agent", "initialized", "offset", "size", "behind",
                "entries_consumed", "entry_next", "entries_total", "last_read_id",
                "next_unread_id"):
        assert key in info
    moved = client.post("/workbench/mailbox/cursor", json={"mailbox": mailbox, "agent": "user-agent", "start": "now"}).json()
    assert moved["initialized"] is True


def test_mailbox_directory_reports_activity_and_messages_past_personal_cursor(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    records = [
        {"id": "first", "timestamp": "2999-01-01T00:00:00+00:00", "text": "first"},
        {"id": "second", "timestamp": "2999-01-01T00:00:01+00:00", "text": "second"},
    ]
    document = {"messages": {"entry_1": records[0], "entry_2": records[1]}, "server": "relay-a"}
    store = SimpleNamespace(
        channel_ids=lambda _root: ["team"],
        load_channel=lambda _root, _mailbox: document,
        ordered_messages=lambda _document: [(f"entry_{index}", record) for index, record in enumerate(records, 1)],
        get_cursor=lambda _root, _agent, _mailbox: {"consumed": 1, "next": "entry_2"},
    )
    monkeypatch.setattr(mailbox_api_lib, "_mailbox_client", SimpleNamespace(mailbox_dir=lambda: tmp_path))
    monkeypatch.setattr(mailbox_api_lib, "channel_store", store)

    row = mailbox_api_lib.mailbox_list(agent="user-agent")["mailboxes"][0]
    assert row["unread"] == 1
    assert row["activityPerMinute"] >= 2
    assert row["activityPerHour"] >= 2
    assert row["cursorOffset"] == 1
    assert row["lastReadMessageId"] == "first"
    assert row["nextUnreadMessageId"] == "second"
    assert row["server"] == "relay-a"


def test_record_edit_in_place_and_at_end(client: TestClient) -> None:
    sent = client.post("/workbench/mailbox/send",
                       json={"text": "original", "to": "peer-agent", "sender": "user-agent"}).json()
    rid = sent["message"]["id"]
    at_end = client.post("/workbench/mailbox/record",
                         json={"id": rid, "record": {**sent["message"], "text": "edited"}, "mode": "at-end"}).json()
    assert at_end["entryKey"].startswith("entry_")
