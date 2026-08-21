from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest


SERVER_ROOT = Path(__file__).resolve().parents[1] / "workbench" / "server"
sys.path.insert(0, str(SERVER_ROOT))

import mailbox_api  # noqa: E402


def _write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as stream:
        for record in records:
            stream.write(json.dumps(record) + "\n")


def test_resolve_mailbox_root_honours_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("AGENT_MAILBOX_DIR", str(tmp_path / "mb"))
    assert mailbox_api.resolve_mailbox_root() == (tmp_path / "mb").resolve()


def test_resolve_mailbox_root_defaults_to_sibling(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("AGENT_MAILBOX_DIR", raising=False)
    resolved = mailbox_api.resolve_mailbox_root()
    assert resolved.name == "mailbox"
    assert resolved.parent.name == "mailbox_channel"


def test_read_tail_records_skips_blank_and_invalid_lines(tmp_path: Path) -> None:
    messages = tmp_path / "messages.jsonl"
    with messages.open("w", encoding="utf-8") as stream:
        stream.write(json.dumps({"id": "1", "text": "ok"}) + "\n")
        stream.write("\n")
        stream.write("not json\n")
        stream.write(json.dumps({"id": "2", "text": "second"}) + "\n")
    records = mailbox_api.read_tail_records(messages)
    assert [record["id"] for record in records] == ["1", "2"]


def test_read_tail_records_returns_empty_when_missing(tmp_path: Path) -> None:
    assert mailbox_api.read_tail_records(tmp_path / "nope.jsonl") == []


def test_thread_messages_filters_to_participant_pair(tmp_path: Path) -> None:
    _write_jsonl(
        tmp_path / "messages.jsonl",
        [
            {"id": "1", "from": "user", "to": "codex", "text": "hi", "type": "message"},
            {"id": "2", "from": "codex", "to": "user", "text": "hello", "type": "message"},
            {"id": "3", "from": "user", "to": "someone-else", "text": "nope", "type": "message"},
            {"id": "4", "from": "codex", "to": "user", "text": "audit copy", "audit_of": "2"},
        ],
    )
    thread = mailbox_api.thread_messages(tmp_path, "user", "codex")
    assert [message["id"] for message in thread] == ["1", "2"]
    assert all("audit_of" not in message for message in thread)


def test_thread_messages_respects_limit(tmp_path: Path) -> None:
    _write_jsonl(
        tmp_path / "messages.jsonl",
        [
            {"id": str(index), "from": "user", "to": "codex", "text": f"m{index}"}
            for index in range(10)
        ],
    )
    thread = mailbox_api.thread_messages(tmp_path, "user", "codex", limit=3)
    assert [message["id"] for message in thread] == ["7", "8", "9"]


def test_mailbox_messages_endpoint_reads_from_env_root(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("AGENT_MAILBOX_DIR", str(tmp_path))
    _write_jsonl(
        tmp_path / "messages.jsonl",
        [{"id": "1", "from": "u", "to": "p", "text": "hey", "type": "message"}],
    )
    payload = mailbox_api.mailbox_messages(user="u", peer="p", limit=200)
    assert payload["messages"][0]["text"] == "hey"
    assert payload["user"] == "u"
    assert payload["peer"] == "p"


def test_send_then_read_roundtrip(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    if mailbox_api._mailbox_client is None:  # pragma: no cover - client absent in some envs
        pytest.skip("mailbox_channels client not installed")
    monkeypatch.setenv("AGENT_MAILBOX_DIR", str(tmp_path))
    sent = mailbox_api.mailbox_send(text="**hello** world", to="peer-agent", sender="user-agent")
    assert sent["message"]["from"] == "user-agent"
    assert sent["message"]["to"] == "peer-agent"
    payload = mailbox_api.mailbox_messages(user="user-agent", peer="peer-agent", limit=200)
    texts = [message["text"] for message in payload["messages"]]
    assert "**hello** world" in texts


def test_mailbox_status_reports_directory(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("AGENT_MAILBOX_DIR", str(tmp_path))
    _write_jsonl(tmp_path / "messages.jsonl", [{"id": "1", "from": "u", "to": "p", "text": "x"}])
    status = mailbox_api.mailbox_status()
    assert status["mailboxDir"] == str(tmp_path.resolve())
    assert status["exists"] is True
    assert status["messagesBytes"] > 0


def test_channel_messages_returns_to_or_from(tmp_path: Path) -> None:
    _write_jsonl(
        tmp_path / "messages.jsonl",
        [
            {"id": "1", "from": "user", "to": "agent", "text": "hi"},
            {"id": "2", "from": "agent", "to": "user", "text": "hello"},
            {"id": "3", "from": "other", "to": "someone", "text": "unrelated"},
            {"id": "4", "from": "agent", "to": "user", "text": "audit", "audit_of": "2"},
        ],
    )
    thread = mailbox_api.channel_messages(tmp_path, "agent")
    assert [message["id"] for message in thread] == ["1", "2"]


def test_list_channels_includes_participants_and_defaults(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # Avoid a real relay call for retained channels during the test.
    monkeypatch.setattr(mailbox_api, "_mailbox_client", None)
    _write_jsonl(
        tmp_path / "messages.jsonl",
        [
            {"id": "1", "from": "symbolic-workbench-user", "to": "github-copilot-facilitator-agent", "text": "a"},
            {"id": "2", "from": "github-copilot-facilitator-agent", "to": "symbolic-workbench-user", "text": "b"},
            {"id": "3", "from": "x", "to": "agent_to_agent", "text": "audit-channel", "audit_of": "1"},
        ],
    )
    channels = mailbox_api.list_channels(tmp_path)
    ids = [channel["id"] for channel in channels]
    assert "github-copilot-facilitator-agent" in ids
    assert "symbolic-workbench-user" in ids
    # Audit fan-out channels are hidden.
    assert "agent_to_agent" not in ids


def test_mailbox_messages_channel_mode(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("AGENT_MAILBOX_DIR", str(tmp_path))
    _write_jsonl(
        tmp_path / "messages.jsonl",
        [
            {"id": "1", "from": "user", "to": "agent", "text": "to-agent"},
            {"id": "2", "from": "agent", "to": "elsewhere", "text": "from-agent"},
            {"id": "3", "from": "n", "to": "m", "text": "unrelated"},
        ],
    )
    payload = mailbox_api.mailbox_messages(channel="agent", limit=200)
    assert [message["id"] for message in payload["messages"]] == ["1", "2"]
    assert payload["channel"] == "agent"


def test_channel_messages_matches_channel_id(tmp_path: Path) -> None:
    _write_jsonl(
        tmp_path / "messages.jsonl",
        [
            {"id": "1", "from": "mattermost", "to": "bridge", "text": "hi", "channel_id": "room-1"},
            {"id": "2", "from": "x", "to": "y", "text": "nope"},
        ],
    )
    thread = mailbox_api.channel_messages(tmp_path, "room-1")
    assert [message["id"] for message in thread] == ["1"]


def test_list_agents_merges_participants_and_defaults(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(mailbox_api, "_mailbox_client", None)
    _write_jsonl(
        tmp_path / "messages.jsonl",
        [{"id": "1", "from": "alice", "to": "bob", "text": "hi"}],
    )
    agent_ids = [agent["id"] for agent in mailbox_api.list_agents(tmp_path)]
    assert "alice" in agent_ids and "bob" in agent_ids
    assert mailbox_api.DEFAULT_USER_AGENT in agent_ids
    assert mailbox_api.DEFAULT_PEER_AGENT in agent_ids


@pytest.fixture(autouse=True)
def _reset_names_cache() -> None:
    """Keep the identifier-name cache from leaking between tests."""

    mailbox_api._NAMES_CACHE["at"] = 0.0
    mailbox_api._NAMES_CACHE["names"] = {}


class _FakeRelay:
    def __init__(self, registry: dict | None = None, identifiers: list[dict] | None = None) -> None:
        self.sent: list[dict] = []
        self.cursors: list[tuple[str, str]] = []
        self.registry = registry or {}
        self.identifiers = identifiers or []

    def _rest_request(self, method: str, path: str, payload=None, base_url=None):  # noqa: ANN001
        if path == "/v1/registry":
            return self.registry
        if path.startswith("/v1/identifiers"):
            return {"identifiers": self.identifiers}
        return {"recipients": [], "positions": []}

    def initialize_cursor_rest(self, recipient: str, *, cursor: str, start: str = "now", base_url=None):  # noqa: ANN001
        self.cursors.append((recipient, cursor))
        return {"recipient": recipient, "cursor": cursor}

    def register_agent_rest(self, agent_id: str, *, presence_id: str = "", base_url=None):  # noqa: ANN001
        self.registered = getattr(self, "registered", [])
        self.registered.append((agent_id, presence_id))
        return {"agent_id": agent_id, "presence_id": presence_id}

    def send(  # noqa: ANN001 - mirrors the real client's keyword surface
        self,
        to: str,
        text: str,
        *,
        sender: str,
        root=None,
        message_type: str = "message",
        metadata=None,
        extra_fields=None,
        channel_id=None,
        **extra,
    ):
        record = {
            "id": f"s{len(self.sent) + 1}",
            "from": sender,
            "to": to,
            "text": text,
            "type": message_type,
        }
        if extra_fields:
            record.update(extra_fields)
        if channel_id:
            record["channel_id"] = channel_id
        record.update(extra)
        self.sent.append(record)
        return record


def test_mailbox_send_with_channel_id_auto_subscribes(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("AGENT_MAILBOX_DIR", str(tmp_path))
    fake = _FakeRelay()
    monkeypatch.setattr(mailbox_api, "_mailbox_client", fake)
    result = mailbox_api.mailbox_send(text="hi", to="some-agent", sender="me", channel_id="room-9")
    assert result["subscribed"] is True
    assert ("room-9", "some-agent") in fake.cursors
    assert fake.sent and fake.sent[0].get("channel_id") == "room-9"


def test_mailbox_create_agent(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = _FakeRelay()
    monkeypatch.setattr(mailbox_api, "_mailbox_client", fake)
    result = mailbox_api.mailbox_create_agent(id="new-agent", presence=None)
    assert result["id"] == "new-agent"
    assert ("new-agent", "new-agent-app") in fake.registered


def test_mailbox_create_channel(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = _FakeRelay()
    monkeypatch.setattr(mailbox_api, "_mailbox_client", fake)
    result = mailbox_api.mailbox_create_channel(id="new-room")
    assert result["id"] == "new-room"
    assert ("new-room", mailbox_api.DEFAULT_PEER_AGENT) in fake.cursors


def test_project_record_resolves_names() -> None:
    record = {
        "id": "1",
        "from": "mattermost",
        "author": "mmid-abc",
        "channel_id": "mmchan-1",
        "text": "hi",
    }
    projected = mailbox_api._project_record(record, {"mmid-abc": "alice", "mmchan-1": "General"})
    assert projected["authorName"] == "alice"
    assert projected["channelName"] == "General"


def test_list_channels_annotates_readable_names(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(mailbox_api, "_mailbox_client", None)
    directory = [
        {"identifier": "c83yabc", "text": "arc3-room", "kind": "channel", "display": "ARC3 Room"},
    ]
    _write_jsonl(
        tmp_path / "messages.jsonl",
        [
            {
                "id": "1",
                "from": "app",
                "to": mailbox_api.REGISTRY_CHANNEL,
                "type": "identifier_directory",
                "text": json.dumps(directory),
            },
            {"id": "2", "from": "mm-chat-host-c83yabc", "to": "someone", "text": "traffic"},
        ],
    )
    channels = {channel["id"]: channel for channel in mailbox_api.list_channels(tmp_path)}
    # The bridged id's trailing segment resolves through the stored directory.
    assert channels["mm-chat-host-c83yabc"]["name"] == "ARC3 Room"


def test_messaging_registry_falls_back_to_stored(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(mailbox_api, "_mailbox_client", None)
    snapshot = {"version": 1, "agents": [{"agent_id": "stored-agent"}], "channels": []}
    _write_jsonl(
        tmp_path / "messages.jsonl",
        [
            {
                "id": "1",
                "from": "app",
                "to": mailbox_api.REGISTRY_CHANNEL,
                "type": "messaging_registry",
                "text": json.dumps(snapshot),
            },
        ],
    )
    assert mailbox_api.messaging_registry(tmp_path) == snapshot
    agent_ids = [agent["id"] for agent in mailbox_api.list_agents(tmp_path)]
    assert "stored-agent" in agent_ids


def test_channel_config_merges_registry_traffic_and_stored(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    fake = _FakeRelay(
        registry={
            "channels": [
                {"id": "room-1", "channel_type": "mattermost", "aliases": [], "subscribers": ["a"]},
            ],
            "agents": [],
        }
    )
    monkeypatch.setattr(mailbox_api, "_mailbox_client", fake)
    stored = {"purpose": "testing", "channelName": "Renamed Room"}
    _write_jsonl(
        tmp_path / "messages.jsonl",
        [
            {"id": "1", "from": "mattermost", "to": "bridge", "channel_id": "room-1",
             "channel_name": "room-one", "text": "hi", "timestamp": "2026-01-01T00:00:00Z"},
            {"id": "2", "from": "app", "to": mailbox_api.REGISTRY_CHANNEL,
             "type": "channel_config", "config_for": "room-1", "text": json.dumps(stored)},
        ],
    )
    config = mailbox_api.channel_config(tmp_path, "room-1")
    assert config["kind"] == "mattermost"
    assert config["messages"] == 1
    assert config["purpose"] == "testing"
    # The stored edit overlays the traffic-derived name.
    assert config["channelName"] == "Renamed Room"


def test_update_channel_config_subscribes_and_stores(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("AGENT_MAILBOX_DIR", str(tmp_path))
    fake = _FakeRelay(registry={"channels": [], "agents": []})
    monkeypatch.setattr(mailbox_api, "_mailbox_client", fake)
    result = mailbox_api.mailbox_update_channel_config(
        channel="room-2", config={"channelName": "Room Two", "subscribers": ["bob"]}
    )
    assert result["stored"] is True
    assert result["subscribed"] == ["bob"]
    assert ("room-2", "bob") in fake.cursors
    stored = [record for record in fake.sent if record["type"] == "channel_config"]
    assert stored and stored[0]["to"] == mailbox_api.REGISTRY_CHANNEL
    assert stored[0]["config_for"] == "room-2"
    assert json.loads(stored[0]["text"])["channelName"] == "Room Two"


def test_registry_bootstrap_stores_both_snapshots(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("AGENT_MAILBOX_DIR", str(tmp_path))
    fake = _FakeRelay(
        registry={"version": 1, "agents": [{"agent_id": "a1"}], "connectors": [], "channels": [], "relays": []},
        identifiers=[
            {"identifier": "u1", "text": "alice", "kind": "user", "metadata": {}},
            {"identifier": "c1", "text": "room", "kind": "channel",
             "metadata": {"display_name": "The Room"}},
            {"identifier": "", "text": "dropped", "kind": "user"},
        ],
    )
    monkeypatch.setattr(mailbox_api, "_mailbox_client", fake)
    result = mailbox_api.mailbox_registry_bootstrap(limit=100)
    assert result["registryStored"] is True
    assert result["identifiersStored"] is True
    assert result["identifierCount"] == 2
    types = [record["type"] for record in fake.sent]
    assert "messaging_registry" in types and "identifier_directory" in types
    directory = json.loads(
        next(record for record in fake.sent if record["type"] == "identifier_directory")["text"]
    )
    assert {"identifier": "c1", "text": "room", "kind": "channel",
            "display": "The Room", "system": None} in directory


def test_identifier_names_merges_stored_and_relay(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    fake = _FakeRelay(identifiers=[{"identifier": "live-1", "text": "livename", "kind": "user"}])
    monkeypatch.setattr(mailbox_api, "_mailbox_client", fake)
    _write_jsonl(
        tmp_path / "messages.jsonl",
        [
            {"id": "1", "from": "app", "to": mailbox_api.REGISTRY_CHANNEL,
             "type": "identifier_directory",
             "text": json.dumps([{"identifier": "stored-1", "text": "storedname"}])},
        ],
    )
    names = mailbox_api.identifier_names(tmp_path, refresh=True)
    assert names["stored-1"] == "storedname"
    assert names["live-1"] == "livename"


