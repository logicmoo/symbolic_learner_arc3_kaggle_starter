from __future__ import annotations

import hashlib
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


def test_list_agents_keeps_full_registry_records(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(mailbox_api, "_mailbox_client", None)
    snapshot = {
        "version": 1,
        "agents": [{"agent_id": "alice", "display_name": "Alice", "host": "box-1"}],
        "channels": [],
    }
    _write_jsonl(
        tmp_path / "messages.jsonl",
        [
            {
                "id": "1",
                "from": "registry-bootstrap",
                "to": mailbox_api.REGISTRY_CHANNEL,
                "type": "messaging_registry",
                "text": json.dumps(snapshot),
            },
            {"id": "2", "from": "alice", "to": "bob", "text": "hi"},
        ],
    )
    agents = {agent["id"]: agent for agent in mailbox_api.list_agents(tmp_path)}
    # The registry record's fields survive, merged with traffic stats.
    assert agents["alice"]["display_name"] == "Alice"
    assert agents["alice"]["host"] == "box-1"
    assert agents["alice"]["messages"] >= 1
    assert agents["bob"]["id"] == "bob"


def _registry_snapshot_record(snapshot: dict) -> dict:
    return {
        "id": "r1",
        "from": "registry-bootstrap",
        "to": mailbox_api.REGISTRY_CHANNEL,
        "type": "messaging_registry",
        "text": json.dumps(snapshot),
    }


def test_agent_entry_overlay_respects_authority(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(mailbox_api, "_mailbox_client", None)
    snapshot = {"version": 1, "agents": [{"agent_id": "alice", "display_name": "Alice"}], "channels": []}

    def write(entry: dict) -> None:
        _write_jsonl(
            tmp_path / "messages.jsonl",
            [
                _registry_snapshot_record(snapshot),
                {
                    "id": "e1",
                    "from": "editor",
                    "to": mailbox_api.AGENTS_CHANNEL,
                    "type": "agent_entry",
                    "text": "",
                    "entry": entry,
                },
            ],
        )

    # Default authority (the entity channel): the edit wins.
    write({"id": "alice", "display_name": "Alice Prime", "team": "blue"})
    agents = {a["id"]: a for a in mailbox_api.list_agents(tmp_path)}
    assert agents["alice"]["display_name"] == "Alice Prime"
    assert agents["alice"]["team"] == "blue"
    assert agents["alice"]["authority"] == mailbox_api.AGENTS_CHANNEL

    # File authority + copy always: the source overwrites, entry only fills gaps.
    write({"id": "alice", "display_name": "Alice Prime", "team": "blue", "authority": "messages.jsonl"})
    agents = {a["id"]: a for a in mailbox_api.list_agents(tmp_path)}
    assert agents["alice"]["display_name"] == "Alice"
    assert agents["alice"]["team"] == "blue"
    assert agents["alice"]["authority"] == "messages.jsonl"

    # File authority + copy once: the copied entry keeps its own values.
    write(
        {
            "id": "alice",
            "display_name": "Alice Prime",
            "authority": "messages.jsonl",
            "authority_copy_from": "once",
        }
    )
    agents = {a["id"]: a for a in mailbox_api.list_agents(tmp_path)}
    assert agents["alice"]["display_name"] == "Alice Prime"

    # Untouched records report the file as their authority.
    assert agents[mailbox_api.DEFAULT_USER_AGENT]["authority"] == "messages.jsonl"


def test_channel_entry_overlay_and_cursor_maps(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    fake = _FakeRelay()
    monkeypatch.setattr(mailbox_api, "_mailbox_client", fake)
    snapshot = {
        "version": 1,
        "agents": [],
        "channels": [{"id": "room-1", "channel_type": "topic", "subscribers": ["carol"]}],
    }
    _write_jsonl(
        tmp_path / "messages.jsonl",
        [
            _registry_snapshot_record(snapshot),
            {"id": "1", "from": "alice", "to": "room-1", "text": "hi"},
            {
                "id": "e1",
                "from": "editor",
                "to": mailbox_api.CHANNELS_CHANNEL,
                "type": "channel_entry",
                "text": "",
                "entry": {
                    "id": "room-1",
                    "name": "War Room",
                    "messages": 999,
                    "subscribers": ["stale"],
                },
            },
        ],
    )
    (tmp_path / "cursor_subscriptions.json").write_text(
        json.dumps({"cursors": {"bob": ["room-1"]}}), encoding="utf-8"
    )
    fake._write_cursor(fake._cursor_path(tmp_path, "room-1:bob"), 0)

    channels = {c["id"]: c for c in mailbox_api.list_channels(tmp_path)}
    room = channels["room-1"]
    assert room["name"] == "War Room"  # saved edit wins
    assert room["messages"] == 1  # counts stay computed, not the saved 999
    # Live union of cursor holders + declared registry subscribers; stale saved
    # copies never survive.
    assert room["subscribers"] == ["bob", "carol"]
    assert "cursors" not in room  # cursor detail lives on the agent JSON

    agents = {a["id"]: a for a in mailbox_api.list_agents(tmp_path)}
    assert agents["bob"]["cursors"]["room-1"]["initialized"] is True


def test_entity_save_posts_to_entity_channel(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("AGENT_MAILBOX_DIR", str(tmp_path))
    fake = _FakeRelay()
    monkeypatch.setattr(mailbox_api, "_mailbox_client", fake)
    result = mailbox_api.mailbox_entity_save(
        kind="agent", id="alice", entry={"display_name": "Alice Prime", "cursors": {"x": {}}}
    )
    assert result["stored"] is True
    assert result["channel"] == mailbox_api.AGENTS_CHANNEL
    record = fake.sent[-1]
    assert record["to"] == mailbox_api.AGENTS_CHANNEL
    assert record["type"] == "agent_entry"
    # Flat config entry: the blob IS the record top level, keyed by entity id.
    assert "entry" not in record
    assert record["id"] == "alice"
    assert record["kind"] == "agent_entry"
    assert record["display_name"] == "Alice Prime"
    assert "cursors" not in record  # computed fields stripped before storing
    assert record["authority"] == mailbox_api.AGENTS_CHANNEL
    assert record["authority_copy_from"] == "always"

    channel_result = mailbox_api.mailbox_entity_save(
        kind="channel", id="room-1", entry={"name": "War Room", "subscribers": ["stale"]}
    )
    assert channel_result["channel"] == mailbox_api.CHANNELS_CHANNEL
    assert fake.sent[-1]["to"] == mailbox_api.CHANNELS_CHANNEL
    assert fake.sent[-1]["type"] == "channel_entry"
    assert fake.sent[-1]["id"] == "room-1"
    assert "subscribers" not in fake.sent[-1]  # computed list never stored


def test_entity_save_merge_posts_changed_keys(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """merge=True stores a <kind>_changed_keys patch without injecting defaults."""

    monkeypatch.setenv("AGENT_MAILBOX_DIR", str(tmp_path))
    fake = _FakeRelay()
    monkeypatch.setattr(mailbox_api, "_mailbox_client", fake)
    result = mailbox_api.mailbox_entity_save(
        kind="agent", id="alice", entry={"status": "logged-in"}, merge=True
    )
    assert result["stored"] is True
    record = fake.sent[-1]
    assert record["type"] == "agent_entry_changed_keys"
    assert record["kind"] == "agent_entry_changed_keys"
    assert record["id"] == "alice"
    assert record["status"] == "logged-in"
    assert "authority" not in record  # partial patch never injects defaults


@pytest.fixture(autouse=True)
def _reset_names_cache() -> None:
    """Keep the identifier-name cache from leaking between tests."""

    mailbox_api._NAMES_CACHE["at"] = 0.0
    mailbox_api._NAMES_CACHE["names"] = {}
    mailbox_api._LOOKUP_MISSES.clear()


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

    # Cursor-file helpers mirroring the real client's local implementations.
    def _cursor_path(self, root: Path, recipient: str) -> Path:
        digest = hashlib.sha256(recipient.encode("utf-8")).hexdigest()[:16]
        return root / "cursors" / f"{digest}.cursor"

    def _read_cursor(self, path: Path) -> int:
        try:
            return max(0, int(path.read_text(encoding="ascii").strip()))
        except (FileNotFoundError, ValueError):
            return 0

    def _write_cursor(self, path: Path, offset: int) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(str(offset), encoding="ascii")

    def _remember_cursor_subscription(self, root: Path, cursor: str, recipient: str) -> None:
        target = root / "cursor_subscriptions.json"
        try:
            document = json.loads(target.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError):
            document = {"version": 1, "cursors": {}}
        members = document.setdefault("cursors", {}).setdefault(cursor, [])
        if recipient not in members:
            members.append(recipient)
        target.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def initialize_cursor(self, recipient: str, *, cursor: str, start: str = "now", root=None):  # noqa: ANN001
        path = self._cursor_path(root, f"{recipient}:{cursor}")
        if path.exists():
            raise ValueError(f"cursor {cursor!r} is already initialized for {recipient!r}")
        if start in {"beginning", "start"}:
            offset = 0
        else:
            try:
                offset = (root / "messages.jsonl").stat().st_size
            except FileNotFoundError:
                offset = 0
        self._write_cursor(path, offset)
        self._remember_cursor_subscription(root, cursor, recipient)
        self.cursors.append((recipient, cursor))
        return {"recipient": recipient, "cursor": cursor, "start": start, "offset": offset}

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


def test_mailbox_send_on_registry_channel_also_auto_subscribes(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("AGENT_MAILBOX_DIR", str(tmp_path))
    fake = _FakeRelay()
    monkeypatch.setattr(mailbox_api, "_mailbox_client", fake)
    result = mailbox_api.mailbox_send(
        text="hi", to="some-agent", sender="me", channel_id=mailbox_api.REGISTRY_CHANNEL
    )
    assert result["subscribed"] is True
    assert (mailbox_api.REGISTRY_CHANNEL, "some-agent") in fake.cursors


def test_stored_dont_autosubscribe_overrides_default(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("AGENT_MAILBOX_DIR", str(tmp_path))
    fake = _FakeRelay()
    monkeypatch.setattr(mailbox_api, "_mailbox_client", fake)
    _write_jsonl(
        tmp_path / "messages.jsonl",
        [
            {"id": "1", "from": "app", "to": mailbox_api.REGISTRY_CHANNEL,
             "type": "channel_config", "config_for": "room-9",
             "text": json.dumps({"dont-autosubscribe": True})},
        ],
    )
    result = mailbox_api.mailbox_send(text="hi", to="some-agent", sender="me", channel_id="room-9")
    assert result["subscribed"] is False
    assert fake.cursors == []


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
    _write_jsonl(
        tmp_path / "messages.jsonl",
        [
            {
                "id": "1",
                "from": "app",
                "to": mailbox_api.REGISTRY_CHANNEL,
                "type": "identifier_entry",
                "text": "",
                "entry": {
                    "identifier": "c83yabc",
                    "text": "arc3-room",
                    "kind": "channel",
                    "metadata": {"display_name": "ARC3 Room"},
                },
            },
            {"id": "2", "from": "mm-chat-host-c83yabc", "to": "someone", "text": "traffic"},
        ],
    )
    channels = {channel["id"]: channel for channel in mailbox_api.list_channels(tmp_path)}
    # The bridged id's trailing segment resolves through the stored directory.
    assert channels["mm-chat-host-c83yabc"]["name"] == "ARC3 Room"


def test_messaging_registry_reads_only_the_blackboard(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # Even with a live relay available, the stored record is the source of truth.
    fake = _FakeRelay(registry={"version": 1, "agents": [{"agent_id": "live-only"}]})
    monkeypatch.setattr(mailbox_api, "_mailbox_client", fake)
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
    assert "live-only" not in agent_ids


def test_channel_config_merges_registry_traffic_and_stored(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(mailbox_api, "_mailbox_client", None)
    registry = {
        "channels": [
            {"id": "room-1", "channel_type": "mattermost", "aliases": [], "subscribers": ["a"]},
        ],
        "agents": [],
    }
    stored = {"purpose": "testing", "channelName": "Renamed Room"}
    _write_jsonl(
        tmp_path / "messages.jsonl",
        [
            {"id": "0", "from": "app", "to": mailbox_api.REGISTRY_CHANNEL,
             "type": "messaging_registry", "text": json.dumps(registry)},
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
    # Every channel (registry included) auto-subscribes unless a stored
    # config opts it out.
    assert config["dont-autosubscribe"] is False
    registry_config = mailbox_api.channel_config(tmp_path, mailbox_api.REGISTRY_CHANNEL)
    assert registry_config["dont-autosubscribe"] is False


def test_update_channel_config_subscribes_and_stores(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("AGENT_MAILBOX_DIR", str(tmp_path))
    fake = _FakeRelay()
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


def test_registry_bootstrap_posts_entry_bubbles(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("AGENT_MAILBOX_DIR", str(tmp_path))
    fake = _FakeRelay(
        registry={"version": 1, "agents": [{"agent_id": "a1"}], "connectors": [], "channels": [], "relays": []},
        identifiers=[
            {"identifier": "u1", "text": "alice", "kind": "user", "metadata": {"email": "a@x"}},
            {"identifier": "c1", "text": "room", "kind": "channel",
             "metadata": {"display_name": "The Room"}},
            {"identifier": "", "text": "dropped", "kind": "user"},
        ],
    )
    monkeypatch.setattr(mailbox_api, "_mailbox_client", fake)
    result = mailbox_api.mailbox_registry_bootstrap(limit=100)
    assert result["registryStored"] is True
    assert result["identifierCount"] == 2
    assert result["identifiersPosted"] == 2
    types = [record["type"] for record in fake.sent]
    assert "messaging_registry" in types
    bubbles = [record for record in fake.sent if record["type"] == "identifier_entry"]
    # One bubble per entry, carrying the full uncondensed entry with empty text.
    assert len(bubbles) == 2
    assert all(record["text"] == "" for record in bubbles)
    assert bubbles[0]["entry"] == fake.identifiers[0]
    assert bubbles[1]["entry"]["metadata"]["display_name"] == "The Room"


def test_registry_bootstrap_skips_unchanged_entries(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("AGENT_MAILBOX_DIR", str(tmp_path))
    entry = {"identifier": "u1", "text": "alice", "kind": "user", "metadata": {}}
    _write_jsonl(
        tmp_path / "messages.jsonl",
        [
            {"id": "1", "from": "app", "to": mailbox_api.REGISTRY_CHANNEL,
             "type": "identifier_entry", "text": "", "entry": entry},
        ],
    )
    fake = _FakeRelay(
        registry={"version": 1, "agents": [], "connectors": [], "channels": [], "relays": []},
        identifiers=[
            dict(entry),
            {"identifier": "u2", "text": "bob", "kind": "user", "metadata": {}},
        ],
    )
    monkeypatch.setattr(mailbox_api, "_mailbox_client", fake)
    result = mailbox_api.mailbox_registry_bootstrap(limit=100)
    assert result["identifierCount"] == 2
    assert result["identifiersPosted"] == 1
    assert result["identifiersUnchanged"] == 1
    bubbles = [record for record in fake.sent if record["type"] == "identifier_entry"]
    assert [record["entry"]["identifier"] for record in bubbles] == ["u2"]


def test_identifier_names_reads_only_the_blackboard(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # A live relay with extra identifiers must not leak into name resolution.
    fake = _FakeRelay(identifiers=[{"identifier": "live-1", "text": "livename", "kind": "user"}])
    monkeypatch.setattr(mailbox_api, "_mailbox_client", fake)
    _write_jsonl(
        tmp_path / "messages.jsonl",
        [
            {"id": "1", "from": "app", "to": mailbox_api.REGISTRY_CHANNEL,
             "type": "identifier_entry", "text": "",
             "entry": {"identifier": "stored-1", "text": "storedname"}},
            {"id": "2", "from": "app", "to": mailbox_api.REGISTRY_CHANNEL,
             "type": "identifier_entry", "text": "",
             "entry": {"identifier": "stored-2", "text": "plain",
                       "metadata": {"display_name": "Pretty Name"}}},
        ],
    )
    names = mailbox_api.identifier_names(tmp_path, refresh=True)
    assert names["stored-1"] == "storedname"
    # metadata display_name is preferred over text.
    assert names["stored-2"] == "Pretty Name"
    assert "live-1" not in names


def test_identifier_lookup_prefers_the_blackboard(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("AGENT_MAILBOX_DIR", str(tmp_path))
    fake = _FakeRelay(identifiers=[{"identifier": "u1", "text": "relay-copy"}])
    monkeypatch.setattr(mailbox_api, "_mailbox_client", fake)
    _write_jsonl(
        tmp_path / "messages.jsonl",
        [
            {"id": "1", "from": "app", "to": mailbox_api.REGISTRY_CHANNEL,
             "type": "identifier_entry", "text": "",
             "entry": {"identifier": "u1", "text": "stored-copy"}},
        ],
    )
    result = mailbox_api.mailbox_identifier_lookup(id="u1")
    assert result["found"] is True
    assert result["source"] == "blackboard"
    assert result["name"] == "stored-copy"
    assert fake.sent == []  # nothing re-posted for a known id


def test_identifier_lookup_asks_relay_and_persists_discovery(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("AGENT_MAILBOX_DIR", str(tmp_path))
    entry = {"identifier": "strange-id", "text": "mystery", "kind": "user",
             "metadata": {"display_name": "Mystery Guest"}}
    fake = _FakeRelay(identifiers=[entry])
    monkeypatch.setattr(mailbox_api, "_mailbox_client", fake)
    result = mailbox_api.mailbox_identifier_lookup(id="strange-id")
    assert result["found"] is True
    assert result["source"] == "relay"
    assert result["name"] == "Mystery Guest"
    assert result["stored"] is True
    bubbles = [record for record in fake.sent if record["type"] == "identifier_entry"]
    # The discovery lands on the blackboard so every agent learns it.
    assert len(bubbles) == 1
    assert bubbles[0]["to"] == mailbox_api.REGISTRY_CHANNEL
    assert bubbles[0]["text"] == ""
    assert bubbles[0]["entry"] == entry


def test_identifier_lookup_reports_a_full_miss(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("AGENT_MAILBOX_DIR", str(tmp_path))
    fake = _FakeRelay(identifiers=[])
    monkeypatch.setattr(mailbox_api, "_mailbox_client", fake)
    result = mailbox_api.mailbox_identifier_lookup(id="nobody-knows")
    assert result["found"] is False
    assert result["entry"] is None
    # The unresolved ask itself lands on the blackboard.
    requests = [r for r in fake.sent if r["type"] == "identifier_lookup_request"]
    assert len(requests) == 1
    assert requests[0]["to"] == mailbox_api.REGISTRY_CHANNEL
    assert requests[0]["identifier"] == "nobody-knows"
    assert requests[0]["requested_because"] is None


def test_identifier_lookup_stores_why_it_was_requested(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("AGENT_MAILBOX_DIR", str(tmp_path))
    fake = _FakeRelay(identifiers=[])
    monkeypatch.setattr(mailbox_api, "_mailbox_client", fake)
    incoming = {"id": "m1", "from": "xj29fkq", "text": "who am i?", "channel_id": "room-1"}
    result = mailbox_api.mailbox_identifier_lookup_post(id="xj29fkq", message=incoming)
    assert result["found"] is False
    assert result["requestedBecause"] == incoming
    requests = [r for r in fake.sent if r["type"] == "identifier_lookup_request"]
    assert requests[0]["requested_because"] == incoming
    # The cached miss keeps the original message as the reason too.
    again = mailbox_api.mailbox_identifier_lookup(id="xj29fkq")
    assert again["source"] == "miss-cache"
    assert again["requestedBecause"] == incoming


def test_list_channels_counts_channel_id_traffic(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(mailbox_api, "_mailbox_client", None)
    _write_jsonl(
        tmp_path / "messages.jsonl",
        [
            {"id": "1", "from": "mattermost", "to": "bridge", "channel_id": "room-x", "text": "a"},
            {"id": "2", "from": "mattermost", "to": "bridge", "channel_id": "room-x", "text": "b"},
        ],
    )
    channels = {c["id"]: c for c in mailbox_api.list_channels(tmp_path)}
    # Bridged traffic counts under the channel id, not just to/from parties.
    assert channels["room-x"]["messages"] == 2


def test_cursor_status_and_reposition(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("AGENT_MAILBOX_DIR", str(tmp_path))
    fake = _FakeRelay()
    monkeypatch.setattr(mailbox_api, "_mailbox_client", fake)
    _write_jsonl(tmp_path / "messages.jsonl", [{"id": "1", "from": "a", "to": "room-1", "text": "hi"}])
    size = (tmp_path / "messages.jsonl").stat().st_size

    status = mailbox_api.mailbox_cursor_status(channel="room-1", agent="bob")
    assert status["initialized"] is False
    assert status["behind"] == size

    made = mailbox_api.mailbox_cursor_set(channel="room-1", agent="bob", start="now")
    assert made["action"] == "initialized"
    assert made["offset"] == size
    assert made["behind"] == 0
    assert ("room-1", "bob") in fake.cursors

    back = mailbox_api.mailbox_cursor_set(channel="room-1", agent="bob", start="beginning")
    assert back["action"] == "repositioned"
    assert back["offset"] == 0
    assert back["behind"] == size

    forward = mailbox_api.mailbox_cursor_set(channel="room-1", agent="bob", start="now")
    assert forward["action"] == "repositioned"
    assert forward["behind"] == 0


def test_cursor_set_rejects_bad_start(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    from fastapi import HTTPException

    monkeypatch.setenv("AGENT_MAILBOX_DIR", str(tmp_path))
    monkeypatch.setattr(mailbox_api, "_mailbox_client", _FakeRelay())
    with pytest.raises(HTTPException):
        mailbox_api.mailbox_cursor_set(channel="room-1", agent="bob", start="yesterday")


def test_cursor_remove_deletes_file_and_subscription(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("AGENT_MAILBOX_DIR", str(tmp_path))
    fake = _FakeRelay()
    monkeypatch.setattr(mailbox_api, "_mailbox_client", fake)
    _write_jsonl(tmp_path / "messages.jsonl", [{"id": "1", "from": "a", "to": "room-1", "text": "hi"}])
    (tmp_path / "cursor_subscriptions.json").write_text(
        json.dumps({"cursors": {"bob": ["room-1", "room-2"]}}), encoding="utf-8"
    )
    mailbox_api.mailbox_cursor_set(channel="room-1", agent="bob", start="now")

    removed = mailbox_api.mailbox_cursor_remove(channel="room-1", agent="bob")
    assert removed["action"] == "removed"
    assert removed["initialized"] is False
    document = json.loads((tmp_path / "cursor_subscriptions.json").read_text(encoding="utf-8"))
    # Only the removed channel is forgotten; other subscriptions survive.
    assert document["cursors"]["bob"] == ["room-2"]

    again = mailbox_api.mailbox_cursor_remove(channel="room-1", agent="bob")
    assert again["action"] == "absent"


def test_cursor_reposition_backfills_subscription_map(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """A repositioned cursor file shows up in both the agent and channel JSONs."""

    monkeypatch.setenv("AGENT_MAILBOX_DIR", str(tmp_path))
    fake = _FakeRelay()
    monkeypatch.setattr(mailbox_api, "_mailbox_client", fake)
    _write_jsonl(tmp_path / "messages.jsonl", [{"id": "1", "from": "a", "to": "room-1", "text": "hi"}])
    # Cursor file exists but the pair is missing from cursor_subscriptions.json.
    fake._write_cursor(fake._cursor_path(tmp_path, "room-1:bob"), 0)
    assert mailbox_api._cursor_map(tmp_path) == {}

    result = mailbox_api.mailbox_cursor_set(channel="room-1", agent="bob", start="beginning")
    assert result["action"] == "repositioned"
    assert mailbox_api._cursor_map(tmp_path) == {"bob": ["room-1"]}
    agents = {a["id"]: a for a in mailbox_api.list_agents(tmp_path)}
    assert agents["bob"]["cursors"]["room-1"]["initialized"] is True
    channels = {c["id"]: c for c in mailbox_api.list_channels(tmp_path)}
    assert channels["room-1"]["subscribers"] == ["bob"]


def test_identifier_lookup_remembers_misses(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("AGENT_MAILBOX_DIR", str(tmp_path))
    fake = _FakeRelay(identifiers=[])
    calls: list[str] = []
    original = fake._rest_request

    def counting(method: str, path: str, payload=None, base_url=None):  # noqa: ANN001
        calls.append(path)
        return original(method, path, payload, base_url)

    fake._rest_request = counting  # type: ignore[method-assign]
    monkeypatch.setattr(mailbox_api, "_mailbox_client", fake)

    first = mailbox_api.mailbox_identifier_lookup(id="ghost-id")
    assert first["found"] is False
    assert first["requestedAt"] > 0
    assert len(calls) == 1

    # Asking again within the TTL is served from the miss cache: no relay call.
    second = mailbox_api.mailbox_identifier_lookup(id="ghost-id")
    assert second["source"] == "miss-cache"
    assert second["retryAfterSecs"] > 0
    assert len(calls) == 1

    # force=true re-asks, and a relay that has learned the id clears the miss.
    fake.identifiers.append({"identifier": "ghost-id", "text": "now-known"})
    third = mailbox_api.mailbox_identifier_lookup(id="ghost-id", force=True)
    assert third["found"] is True
    assert third["source"] == "relay"
    assert len(calls) == 2
    assert "ghost-id" not in mailbox_api._LOOKUP_MISSES




# ── lifetime traffic stats + server_worker_queue ─────────────────────────────


class _InlinePool:
    """Deterministic stand-in for the worker thread pool: runs submits inline."""

    def submit(self, fn, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003
        fn(*args, **kwargs)


def _fresh_worker_state(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(mailbox_api, "_WORKER_SEEN", set())
    monkeypatch.setattr(mailbox_api, "_worker_pool", lambda: _InlinePool())
    monkeypatch.setattr(mailbox_api, "_NAMES_CACHE", {"at": 0.0, "names": {}})


def test_traffic_stats_are_lifetime_and_incremental(tmp_path: Path) -> None:
    messages = tmp_path / "messages.jsonl"
    _write_jsonl(
        messages,
        [
            {"id": "1", "from": "alice", "to": "room-x", "channel_id": "room-x",
             "timestamp": "2026-01-01T00:00:00Z", "text": "hi"},
        ],
    )
    stats = mailbox_api._traffic_stats(tmp_path)
    assert stats["room-x"] == {
        "messages": 1,
        "entries": 1,
        "nextEntry": 1,
        "lastMessageAt": "2026-01-01T00:00:00Z",
        "channelName": None,
        "isChannel": True,
    }
    assert stats["alice"]["isChannel"] is False
    assert stats["alice"]["entries"] == 0  # mentioned as sender, owns no entries

    # Appended records are picked up incrementally (offset advances, no rescan).
    with messages.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps({
            "id": "2", "from": "bob", "to": "room-x", "channel_id": "room-x",
            "channel_name": "Room X", "timestamp": "2026-01-02T09:00:00Z",
        }) + "\n")
    stats = mailbox_api._traffic_stats(tmp_path)
    assert stats["room-x"]["messages"] == 2
    assert stats["room-x"]["lastMessageAt"] == "2026-01-02T09:00:00Z"
    assert stats["room-x"]["channelName"] == "Room X"
    assert stats["bob"]["messages"] == 1

    # A rewritten file no longer matches the checkpoint: stats rescan cleanly.
    _write_jsonl(messages, [{"id": "9", "from": "zed", "to": "fresh", "text": "x"}])
    stats = mailbox_api._traffic_stats(tmp_path)
    assert "room-x" not in stats
    assert stats["fresh"]["messages"] == 1


def test_list_channels_kinds_split_channels_from_mailboxes(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(mailbox_api, "_mailbox_client", None)
    _write_jsonl(
        tmp_path / "messages.jsonl",
        [
            {"id": "1", "from": "alice", "to": "bridge",
             "channel_id": "mm-opaque-bridge-channel", "text": "relayed"},
            {"id": "2", "from": "app", "to": mailbox_api.REGISTRY_CHANNEL,
             "type": "messaging_registry", "text": "{}"},
        ],
    )
    channels = {c["id"]: c for c in mailbox_api.list_channels(tmp_path)}
    # ids seen as a record's channel_id are channels, never agent mailboxes …
    assert channels["mm-opaque-bridge-channel"]["kind"] == "channel"
    # … and well-known channels keep their registry kind despite traffic.
    assert channels[mailbox_api.REGISTRY_CHANNEL]["kind"] == "registry"
    assert channels[mailbox_api.WORKER_QUEUE_CHANNEL]["kind"] == "registry"
    agent_ids = {a["id"] for a in mailbox_api.list_agents(tmp_path)}
    assert "alice" in agent_ids and "bridge" in agent_ids
    # channels no longer leak into the YOU/TO agent pickers.
    assert "mm-opaque-bridge-channel" not in agent_ids


def test_list_channels_merges_registry_record_and_inspires_lookup(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("AGENT_MAILBOX_DIR", str(tmp_path))
    fake = _FakeRelay()
    monkeypatch.setattr(mailbox_api, "_mailbox_client", fake)
    _fresh_worker_state(monkeypatch)
    workspace_id = "wsopaqueid0123456789abcdef"
    snapshot = {
        "version": 1,
        "agents": [],
        "channels": [
            {
                "id": "mm-host-room",
                "channel_type": "mattermost",
                "aliases": ["nice-room"],
                "subscribers": ["bridge-bot"],
                "metadata": {
                    "channel_name": "nice-room",
                    "workspace_id": workspace_id,
                    "workspace_name": "chat",
                },
            }
        ],
    }
    _write_jsonl(tmp_path / "messages.jsonl", [_registry_snapshot_record(snapshot)])

    channels = {c["id"]: c for c in mailbox_api.list_channels(tmp_path)}
    record = channels["mm-host-room"]
    # The registry record merged in whole — metadata and aliases included.
    assert record["metadata"]["workspace_id"] == workspace_id
    assert record["aliases"] == ["nice-room"]
    assert record["kind"] == "mattermost"
    assert "bridge-bot" in record["subscribers"]

    # The opaque workspace_id inspired a durable, REST-shaped lookup task …
    tasks = [r for r in fake.sent if r.get("type") == "worker_task"]
    assert len(tasks) == 1
    task = tasks[0]
    assert task["to"] == mailbox_api.WORKER_QUEUE_CHANNEL
    assert task["command"] == {"op": "identifier_lookup", "id": workspace_id}
    assert task["queue_mode"] == "enqueue"
    assert task["status"] == "queued"
    assert task["requested_because"] == {"channel": "mm-host-room", "metadata_key": "workspace_id"}

    # … the (inline) pool drained it immediately and posted the result record …
    results = [r for r in fake.sent if r.get("type") == "worker_task_result"]
    assert len(results) == 1
    assert results[0]["task_key"] == task["task_key"]
    assert results[0]["queue_mode"] == "immediate"
    assert results[0]["status"] == "done"
    assert results[0]["result"]["found"] is False

    # … and the unresolved id landed as a lookup request on the registry too.
    asks = [r for r in fake.sent if r.get("type") == "identifier_lookup_request"]
    assert [a["identifier"] for a in asks] == [workspace_id]

    # Listing again does not enqueue the same task twice (process-lifetime dedup).
    before = len(fake.sent)
    mailbox_api.list_channels(tmp_path)
    assert [r for r in fake.sent[before:] if r.get("type") == "worker_task"] == []


def test_worker_endpoint_immediate_enqueue_and_dedup(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("AGENT_MAILBOX_DIR", str(tmp_path))
    fake = _FakeRelay(identifiers=[{"identifier": "knownid0123456789abcdef", "text": "Known Thing"}])
    monkeypatch.setattr(mailbox_api, "_mailbox_client", fake)
    _fresh_worker_state(monkeypatch)
    command = {"op": "identifier_lookup", "id": "knownid0123456789abcdef"}

    # REST default: immediate — the command runs now and returns its result.
    ran = mailbox_api.mailbox_worker_command(command=dict(command))
    assert ran["queued"] is False
    assert ran["result"]["found"] is True
    assert ran["result"]["source"] == "relay"
    assert not [r for r in fake.sent if r.get("type") == "worker_task"]

    # Opt-in enqueue posts the durable task; the drained task runs immediate.
    queued = mailbox_api.mailbox_worker_command(command=dict(command), queue="enqueue")
    assert queued["queued"] is True
    tasks = [r for r in fake.sent if r.get("type") == "worker_task"]
    results = [r for r in fake.sent if r.get("type") == "worker_task_result"]
    assert len(tasks) == 1 and len(results) == 1
    assert results[0]["status"] == "done"

    # The same command enqueued again is a duplicate, not a second task.
    again = mailbox_api.mailbox_worker_command(command=dict(command), queue="enqueue")
    assert again == {"queued": False, "duplicate": True, "taskKey": queued["taskKey"]}
    assert len([r for r in fake.sent if r.get("type") == "worker_task"]) == 1

    # Unknown ops surface an error result instead of raising.
    bad = mailbox_api.mailbox_worker_command(command={"op": "frobnicate"})
    assert bad["result"]["error"] == "unknown op 'frobnicate'"
    with pytest.raises(mailbox_api.HTTPException):
        mailbox_api.mailbox_worker_command(command={})


def test_identifier_post_can_enqueue(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("AGENT_MAILBOX_DIR", str(tmp_path))
    fake = _FakeRelay()
    monkeypatch.setattr(mailbox_api, "_mailbox_client", fake)
    _fresh_worker_state(monkeypatch)
    outcome = mailbox_api.mailbox_identifier_lookup_post(
        id="mysteryid0123456789abc", message={"why": "strange"}, queue="enqueue"
    )
    assert outcome["queued"] is True
    tasks = [r for r in fake.sent if r.get("type") == "worker_task"]
    assert tasks and tasks[0]["command"] == {
        "op": "identifier_lookup",
        "id": "mysteryid0123456789abc",
        "force": False,
        "message": {"why": "strange"},
    }
    assert tasks[0]["requested_because"] == {"why": "strange"}


# ── channel grooming, keyed resolver, subscription sync ──────────────────────

_KEY = "abcdefghij1234567890zzzz"
_CANON = f"mm-chat-example-com-{_KEY}"
_WS_FORM = f"mm-chat-example-com-team-{_KEY}"
_SLASH_FORM = f"mm/chat.example.com/{_KEY}"


def _line_ends(path: Path) -> list[int]:
    ends, offset = [], 0
    for line in path.read_bytes().splitlines(keepends=True):
        offset += len(line)
        ends.append(offset)
    return ends


def _groom_fixture(tmp_path: Path) -> None:
    registry = {"channels": [{
        "id": _WS_FORM,
        "channel_type": "channel",
        "aliases": ["test-room"],
        "subscribers": ["agent-one"],
        "metadata": {
            "external_address": _SLASH_FORM,
            "endpoint": "chat.example.com",
            "workspace_name": "team",
            "channel_name": "Test Room",
        },
    }]}
    _write_jsonl(
        tmp_path / "messages.jsonl",
        [
            {"id": "m0", "from": "app", "to": mailbox_api.REGISTRY_CHANNEL,
             "type": "messaging_registry", "text": json.dumps(registry)},
            {"id": "m1", "from": "joe", "to": _WS_FORM, "channel_id": _WS_FORM,
             "channel_name": "Test Room", "text": "one"},
            {"id": "m2", "from": "joe", "to": _CANON, "channel_id": _CANON, "text": "two"},
            {"id": "m3", "from": "joe", "to": _SLASH_FORM, "channel_id": _SLASH_FORM,
             "text": "three"},
            {"id": "m4", "from": "joe", "to": _KEY, "text": "four"},
            {"id": "m5", "from": "x", "to": "other-agent", "text": "five"},
        ],
    )


def test_groom_channels_dry_run_reports_plan_without_touching_files(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("AGENT_MAILBOX_DIR", str(tmp_path))
    monkeypatch.setattr(mailbox_api, "_mailbox_client", _FakeRelay())
    _groom_fixture(tmp_path)
    before = (tmp_path / "messages.jsonl").read_bytes()

    plan = mailbox_api._groom_channels(apply=False)

    assert plan["applied"] is False
    assert plan["recordsToRemap"] == 3  # workspace, slash and bare forms
    channel = plan["channels"][_CANON]
    assert channel["key"] == _KEY
    assert set(channel["aliases"]) >= {_WS_FORM, _SLASH_FORM, _KEY}
    assert "Test Room" in channel["names"]
    assert (tmp_path / "messages.jsonl").read_bytes() == before


def test_groom_channels_apply_rewrites_log_cursors_and_registry(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("AGENT_MAILBOX_DIR", str(tmp_path))
    fake = _FakeRelay()
    monkeypatch.setattr(mailbox_api, "_mailbox_client", fake)
    _groom_fixture(tmp_path)
    old_ends = _line_ends(tmp_path / "messages.jsonl")
    # agent-one consumed through record index 2 of the old file (3 records).
    fake._write_cursor(fake._cursor_path(tmp_path, f"{_WS_FORM}:agent-one"), old_ends[2])
    (tmp_path / "cursor_subscriptions.json").write_text(
        json.dumps({"version": 1, "cursors": {"agent-one": [_WS_FORM]}}), encoding="utf-8"
    )

    summary = mailbox_api._groom_channels(apply=True)

    assert summary["applied"] is True
    records = [json.loads(line) for line in
               (tmp_path / "messages.jsonl").read_text(encoding="utf-8").splitlines()]
    # Every duplicate spelling now reads as the canonical id.
    assert [r.get("to") for r in records[1:5]] == [_CANON] * 4
    assert [r.get("entry_key") for r in records[1:5]] == [
        "entry_0", "entry_1", "entry_2", "entry_3"]
    assert records[5]["entry_key"] == "entry_0"  # other-agent keeps its own sequence
    # The stored registry doc converted to the keyed canonical scheme.
    stored = json.loads(records[0]["text"])
    assert stored["channels"][0]["id"] == _CANON
    assert stored["channels"][0]["key"] == _KEY
    assert set(stored["channels"][0]["aliases"]) >= {_WS_FORM, _SLASH_FORM, _KEY}
    # Cursor surgery: same records consumed, expressed in new-file offsets.
    new_ends = _line_ends(tmp_path / "messages.jsonl")
    moved = fake._read_cursor(fake._cursor_path(tmp_path, f"{_CANON}:agent-one"))
    assert moved == new_ends[2]
    document = json.loads((tmp_path / "cursor_subscriptions.json").read_text(encoding="utf-8"))
    assert document["cursors"] == {"agent-one": [_CANON]}
    assert list(tmp_path.glob("messages.jsonl.groomed-*.bak"))
    posted = [r["type"] for r in fake.sent]
    assert "messaging_registry" in posted and "resolver_index" in posted


def test_sync_subscriptions_projects_intent_and_autocursors(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("AGENT_MAILBOX_DIR", str(tmp_path))
    fake = _FakeRelay()
    monkeypatch.setattr(mailbox_api, "_mailbox_client", fake)
    registry = {"channels": [{"id": "room-1", "subscribers": ["declared-agent"]}]}
    _write_jsonl(
        tmp_path / "messages.jsonl",
        [
            {"id": "m0", "from": "app", "to": mailbox_api.REGISTRY_CHANNEL,
             "type": "messaging_registry", "text": json.dumps(registry)},
            {"id": "r1", "from": "a", "to": "room-1", "text": "one"},
            {"id": "r2", "from": "b", "to": "room-1", "text": "two"},
            {"id": "e1", "from": "app", "to": mailbox_api.AGENTS_CHANNEL,
             "type": "agent_entry",
             "entry": {"id": "opted-out", "subscriptions": {"room-1": "unsubscribed"}}},
            {"id": "e2", "from": "app", "to": mailbox_api.AGENTS_CHANNEL,
             "type": "agent_entry",
             "entry": {"id": "auto-sub", "subscriptions": {"room-1": "subscribed"}}},
        ],
    )
    ends = _line_ends(tmp_path / "messages.jsonl")
    fake._write_cursor(fake._cursor_path(tmp_path, "room-1:agent-a"), ends[1])
    (tmp_path / "cursor_subscriptions.json").write_text(
        json.dumps({"version": 1, "cursors": {"agent-a": ["room-1"]}}), encoding="utf-8"
    )

    result = mailbox_api._sync_subscriptions()

    # +2 monitor agents (bridge/loader) with their autocursored service queues
    # (the resolver holds both outbound relay queues).
    assert result == {"agents": 5, "channels": 4, "autocursored": 4}
    agents = {r["entry"]["id"]: r["entry"] for r in fake.sent if r["type"] == "agent_entry"}
    assert agents["agent-a"]["subscriptions"] == {"room-1": "subscribed"}
    cursor = agents["agent-a"]["cursors"]["room-1"]
    assert cursor["offset"] == ends[1]
    assert cursor["entries_consumed"] == 1 and cursor["entry_next"] == "entry_1"
    # Subscribed without a cursor -> autocursor at entry_0 and doc registration.
    assert agents["auto-sub"]["cursors"]["room-1"]["entry_next"] == "entry_0"
    assert fake._read_cursor(fake._cursor_path(tmp_path, "room-1:auto-sub")) == 0
    document = json.loads((tmp_path / "cursor_subscriptions.json").read_text(encoding="utf-8"))
    assert document["cursors"]["auto-sub"] == ["room-1"]
    # Sticky opt-out never re-subscribes and keeps no cursor projection.
    assert agents["opted-out"]["subscriptions"] == {"room-1": "unsubscribed"}
    assert agents["opted-out"]["cursors"] == {}
    channels = {r["entry"]["id"]: r["entry"] for r in fake.sent if r["type"] == "channel_entry"}
    assert channels["room-1"]["subscribers"] == ["agent-a", "auto-sub", "declared-agent"]


def test_resolver_index_typed_maps_and_endpoint(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("AGENT_MAILBOX_DIR", str(tmp_path))
    monkeypatch.setattr(mailbox_api, "_mailbox_client", _FakeRelay())
    workspace_id = "wsuuid098765432109876543"
    user_id = "useruuidabcdef1234567890"
    registry = {"channels": [{
        "id": _CANON,
        "aliases": ["test-room"],
        "metadata": {
            "external_address": _SLASH_FORM,
            "channel_name": "Test Room",
            "workspace_id": workspace_id,
            "workspace_name": "team",
        },
    }]}
    _write_jsonl(
        tmp_path / "messages.jsonl",
        [
            {"id": "m0", "from": "app", "to": mailbox_api.REGISTRY_CHANNEL,
             "type": "messaging_registry", "text": json.dumps(registry)},
            {"id": "i1", "from": "app", "to": mailbox_api.REGISTRY_CHANNEL,
             "type": "identifier_entry",
             "entry": {"identifier": user_id, "kind": "user", "display": "Joe Blow"}},
            {"id": "i2", "from": "app", "to": mailbox_api.REGISTRY_CHANNEL,
             "type": "identifier_entry",
             "entry": {"identifier": _KEY, "kind": "channel", "display": "Test Room"}},
        ],
    )

    index = mailbox_api._resolver_index(tmp_path)

    assert index["users"][user_id]["name"] == "Joe Blow"
    assert index["workspaces"][workspace_id]["name"] == "team"
    assert index["channels"][_KEY]["id"] == _CANON
    assert index["channels"][_KEY]["workspace"] == workspace_id
    assert {"type": "channel", "key": _KEY} in index["aliases"]["test-room"]
    assert {"type": "channel", "key": _KEY} in index["aliases"]["Test Room"]
    assert {"type": "user", "key": user_id} in index["aliases"]["Joe Blow"]
    assert {"type": "workspace", "key": workspace_id} in index["aliases"]["team"]

    resolved = mailbox_api.mailbox_resolve(name="test-room")
    assert resolved == {"name": "test-room",
                        "refs": [{"type": "channel", "key": _KEY}]}


def test_mailbox_send_stamps_next_entry_key(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("AGENT_MAILBOX_DIR", str(tmp_path))
    fake = _FakeRelay()
    monkeypatch.setattr(mailbox_api, "_mailbox_client", fake)
    _write_jsonl(
        tmp_path / "messages.jsonl",
        [
            {"id": "1", "from": "a", "to": "room-9", "channel_id": "room-9", "text": "x"},
            {"id": "2", "from": "b", "to": "room-9", "channel_id": "room-9", "text": "y"},
        ],
    )

    mailbox_api.mailbox_send(text="hi", to="agent-x", sender="me", channel_id="room-9")

    stamped = [r for r in fake.sent if r.get("entry_key")]
    assert stamped and stamped[0]["entry_key"] == "entry_2"


# ── worker loader agent, entry keys, dependencies, agent merging ─────────────


def test_worker_enqueue_stamps_entry_key_and_loader_overlays_status(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("AGENT_MAILBOX_DIR", str(tmp_path))
    fake = _FakeRelay()
    monkeypatch.setattr(mailbox_api, "_mailbox_client", fake)
    _fresh_worker_state(monkeypatch)
    queue = mailbox_api.WORKER_QUEUE_CHANNEL
    # An old task occupies entry_7: the next key is max+1 — never recycled —
    # even though the channel holds a single (leftover) entry.
    _write_jsonl(
        tmp_path / "messages.jsonl",
        [
            {"id": "t0", "from": "user", "to": queue, "channel_id": queue,
             "type": "worker_task", "entry_key": "entry_7", "status": "queued"},
        ],
    )

    outcome = mailbox_api.run_worker_command(
        {"op": "identifier_lookup", "id": "mysteryid0123456789abc"}, queue_mode="enqueue"
    )

    assert outcome["queued"] is True
    assert outcome["taskEntry"] == "entry_8"
    task = next(r for r in fake.sent if r["type"] == "worker_task")
    assert task["entry_key"] == "entry_8"
    assert task["status"] == "queued"
    # The loader agent leaves the entry in place and layers statuses over it.
    statuses = [r for r in fake.sent if r["type"] == "worker_task_status"]
    assert [s["status"] for s in statuses] == ["submitted"]
    assert statuses[0]["from"] == mailbox_api.WORKER_LOADER_AGENT
    assert statuses[0]["task_entry"] == "entry_8"
    result = next(r for r in fake.sent if r["type"] == "worker_task_result")
    assert result["from"] == mailbox_api.WORKER_LOADER_AGENT
    assert result["task_entry"] == "entry_8"


def test_worker_depends_on_gates_execution(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("AGENT_MAILBOX_DIR", str(tmp_path))
    fake = _FakeRelay()
    monkeypatch.setattr(mailbox_api, "_mailbox_client", fake)
    _fresh_worker_state(monkeypatch)
    monkeypatch.setattr(mailbox_api, "WORKER_DEP_WAIT_SECS", 0.3)
    monkeypatch.setattr(mailbox_api, "WORKER_DEP_POLL_SECS", 0.05)
    queue = mailbox_api.WORKER_QUEUE_CHANNEL
    _write_jsonl(
        tmp_path / "messages.jsonl",
        [
            # entry_4 is still queued (unsettled) …
            {"id": "t0", "from": "user", "to": queue, "channel_id": queue,
             "type": "worker_task", "entry_key": "entry_4", "status": "queued"},
            # … while entry_20 ran to completion (settled).
            {"id": "t1", "from": "user", "to": queue, "channel_id": queue,
             "type": "worker_task", "entry_key": "entry_20", "status": "queued"},
            {"id": "t2", "from": mailbox_api.WORKER_LOADER_AGENT, "to": queue,
             "channel_id": queue, "type": "worker_task_result",
             "task_entry": "entry_20", "status": "done"},
        ],
    )

    def statuses_for(key: str) -> list[str]:
        return [r["status"] for r in fake.sent
                if r["type"] == "worker_task_status" and r.get("task_key") == key]

    # A settled dependency is satisfied — and so is one whose entry no longer
    # exists (deleted/compacted away): no block, straight to submitted.
    done = mailbox_api.run_worker_command(
        {"op": "identifier_lookup", "id": "aaaa0123456789abcdefgh",
         "depends_on": ["entry_20"]}, queue_mode="enqueue")
    gone = mailbox_api.run_worker_command(
        {"op": "identifier_lookup", "id": "bbbb0123456789abcdefgh",
         "depends_on": ["entry_999"]}, queue_mode="enqueue")
    assert statuses_for(done["taskKey"]) == ["submitted"]
    assert statuses_for(gone["taskKey"]) == ["submitted"]

    # An unsettled dependency blocks the task; it still runs after the wait cap.
    blocked = mailbox_api.run_worker_command(
        {"op": "identifier_lookup", "id": "cccc0123456789abcdefgh",
         "depends_on": ["entry_4"]}, queue_mode="enqueue")
    assert statuses_for(blocked["taskKey"]) == ["blocked", "submitted"]
    task = next(r for r in fake.sent
                if r["type"] == "worker_task" and r.get("task_key") == blocked["taskKey"])
    assert task["depends_on"] == ["entry_4"]

    # A task can never block on its own entry key.
    selfdep = mailbox_api.run_worker_command(
        {"op": "identifier_lookup", "id": "dddd0123456789abcdefgh",
         "depends_on": ["entry_22"]}, queue_mode="enqueue")
    assert selfdep["taskEntry"] == "entry_22"
    assert statuses_for(selfdep["taskKey"]) == ["submitted"]


def test_agent_aliases_fold_into_first_class_agents(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("AGENT_MAILBOX_DIR", str(tmp_path))
    fake = _FakeRelay()
    monkeypatch.setattr(mailbox_api, "_mailbox_client", fake)
    monkeypatch.setattr(mailbox_api, "_NAMES_CACHE", {"at": 0.0, "names": {}})
    bridge = mailbox_api.MATTERMOST_BRIDGE_AGENT
    server = mailbox_api.MAILBOX_SERVER_AGENT
    registry = {"agents": [
        {"agent_id": "mattermost-bridge", "mailbox": "mattermost-bridge"},
        {"agent_id": "relay-registered-x", "mailbox": "relay-registered-x"},
    ]}
    _write_jsonl(
        tmp_path / "messages.jsonl",
        [
            {"id": "m0", "from": "app", "to": mailbox_api.REGISTRY_CHANNEL,
             "type": "messaging_registry", "text": json.dumps(registry)},
            {"id": "m1", "from": "mattermost", "to": "room-1", "channel_id": "room-1",
             "text": "hello"},
            {"id": "e0", "from": "app", "to": mailbox_api.AGENTS_CHANNEL,
             "type": "agent_entry", "entry": {"id": "mattermost", "note": "legacy"}},
        ],
    )
    (tmp_path / "cursor_subscriptions.json").write_text(json.dumps({
        "version": 1,
        "cursors": {
            "local-mattermost-server": ["room-1"],
            "channel-relay": ["room-1"],
            "server_registry": ["server_registry"],
        },
    }), encoding="utf-8")

    agents = {a["id"]: a for a in mailbox_api.list_agents(tmp_path)}

    # The alias trio folded into the first-class bridge agent …
    assert bridge in agents
    for alias in ("mattermost", "mattermost-bridge", "local-mattermost-server"):
        assert alias not in agents
    assert agents[bridge]["note"] == "legacy"      # stored entry folded in
    assert "room-1" in agents[bridge]["cursors"]   # alias cursor folded in
    # … the local server identities fold the same way …
    assert server in agents and "channel-relay" not in agents
    # … blackboard channels never masquerade as agents …
    assert "server_registry" not in agents
    # … the service agents declare their roles …
    assert agents[bridge]["role"] == mailbox_api.AGENT_ROLES[bridge]
    assert agents[mailbox_api.WORKER_LOADER_AGENT]["role"] == (
        mailbox_api.AGENT_ROLES[mailbox_api.WORKER_LOADER_AGENT])
    # … and registry entries carry provenance: entered by the bridge agent.
    assert agents["relay-registered-x"]["entered_by"] == bridge
    assert "entered_by" not in agents[bridge]

    # New traffic addressed to an alias lands on the canonical id too.
    mailbox_api.mailbox_send(text="hi", to="channel-relay", sender="me")
    assert fake.sent[-1]["to"] == server


def test_groom_apply_merges_agent_aliases(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("AGENT_MAILBOX_DIR", str(tmp_path))
    fake = _FakeRelay()
    monkeypatch.setattr(mailbox_api, "_mailbox_client", fake)
    bridge = mailbox_api.MATTERMOST_BRIDGE_AGENT
    _write_jsonl(
        tmp_path / "messages.jsonl",
        [
            {"id": "m0", "from": "mattermost", "to": "room-1", "channel_id": "room-1",
             "text": "one"},
            {"id": "m1", "from": "local-mattermost-server", "to": "room-1",
             "channel_id": "room-1", "text": "two"},
            {"id": "e0", "from": "app", "to": mailbox_api.AGENTS_CHANNEL,
             "channel_id": mailbox_api.AGENTS_CHANNEL, "type": "agent_entry",
             "entry": {"id": "mattermost-bridge"}},
        ],
    )
    old_ends = _line_ends(tmp_path / "messages.jsonl")
    # Two alias cursors at different positions: the merge keeps the furthest.
    fake._write_cursor(fake._cursor_path(tmp_path, "room-1:mattermost"), old_ends[0])
    fake._write_cursor(fake._cursor_path(tmp_path, "room-1:mattermost-bridge"), old_ends[1])
    (tmp_path / "cursor_subscriptions.json").write_text(json.dumps({
        "version": 1,
        "cursors": {"mattermost": ["room-1"], "mattermost-bridge": ["room-1"]},
    }), encoding="utf-8")

    summary = mailbox_api._groom_channels(apply=True)

    assert summary["agents"][bridge] == [
        "local-mattermost-server", "mattermost", "mattermost-bridge"]
    records = [json.loads(line) for line in
               (tmp_path / "messages.jsonl").read_text(encoding="utf-8").splitlines()]
    assert [r["from"] for r in records[:2]] == [bridge, bridge]
    assert records[2]["entry"]["id"] == bridge
    # One folded cursor at the furthest consumed position, canonical doc key.
    new_ends = _line_ends(tmp_path / "messages.jsonl")
    assert fake._read_cursor(fake._cursor_path(tmp_path, f"room-1:{bridge}")) == new_ends[1]
    document = json.loads((tmp_path / "cursor_subscriptions.json").read_text(encoding="utf-8"))
    assert document["cursors"] == {bridge: ["room-1"]}


def test_sync_subscriptions_folds_aliases_and_skips_well_known_channels(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("AGENT_MAILBOX_DIR", str(tmp_path))
    fake = _FakeRelay()
    monkeypatch.setattr(mailbox_api, "_mailbox_client", fake)
    _write_jsonl(
        tmp_path / "messages.jsonl",
        [{"id": "r1", "from": "a", "to": "room-1", "channel_id": "room-1", "text": "one"}],
    )
    (tmp_path / "cursor_subscriptions.json").write_text(json.dumps({
        "version": 1,
        "cursors": {
            "mattermost": ["room-1"],
            "server_registry": ["server_registry"],
        },
    }), encoding="utf-8")

    result = mailbox_api._sync_subscriptions()

    # The designated monitors join in: the resolver picks up both outbound
    # relay queues, the loader picks up server_worker_queue (autocursored at 0).
    assert result == {"agents": 3, "channels": 4, "autocursored": 3}
    entries = [r["entry"] for r in fake.sent if r["type"] == "agent_entry"]
    assert [e["id"] for e in entries] == [
        mailbox_api.MATTERMOST_BRIDGE_AGENT,
        mailbox_api.OUTBOUND_DELIVERY_RESOLVER_AGENT,
        mailbox_api.WORKER_LOADER_AGENT]
    assert entries[0]["subscriptions"] == {"room-1": "subscribed"}
    assert entries[1]["subscriptions"] == {
        mailbox_api.OUTBOUND_TO_AGENT_QUEUE: "subscribed",
        mailbox_api.OUTBOUND_TO_CHANNEL_QUEUE: "subscribed"}


def test_outbound_delivery_is_a_monitored_queue_not_an_agent(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("AGENT_MAILBOX_DIR", str(tmp_path))
    fake = _FakeRelay()
    monkeypatch.setattr(mailbox_api, "_mailbox_client", fake)
    _write_jsonl(
        tmp_path / "messages.jsonl",
        [
            # A codex worker drops an outbound post knowing nothing about
            # delivery — just its text and whatever address hint it has …
            {"id": "o1", "from": "symbolic-workbench-codex", "to": "outbound_delivery",
             "text": "hello", "endpoint_address": "mm/chat.example.io/abc123"},
            # … and the queue even answers as a sender (duplicate suppression).
            {"id": "o2", "from": "outbound_delivery", "to": "symbolic-workbench-codex",
             "type": "channel_delivery_suppressed", "text": "dup"},
        ],
    )

    mailbox_api._sync_subscriptions()

    channels = {c["id"]: c for c in mailbox_api.list_channels(tmp_path)}
    # The legacy outbound_delivery drop split by content: o1 carries endpoint
    # evidence -> agent_to_channel queue; both queues share the resolver.
    queue = channels[mailbox_api.OUTBOUND_TO_CHANNEL_QUEUE]
    assert queue["monitors"] == [mailbox_api.OUTBOUND_DELIVERY_RESOLVER_AGENT]
    assert mailbox_api.OUTBOUND_DELIVERY_RESOLVER_AGENT in queue["subscribers"]
    agent_queue = channels[mailbox_api.OUTBOUND_TO_AGENT_QUEUE]
    assert agent_queue["monitors"] == [mailbox_api.OUTBOUND_DELIVERY_RESOLVER_AGENT]
    assert "outbound_delivery" not in channels
    worker_queue = channels[mailbox_api.WORKER_QUEUE_CHANNEL]
    assert worker_queue["monitors"] == [mailbox_api.WORKER_LOADER_AGENT]
    # The queues never masquerade as agents, even when seen as a sender.
    agents = {a["id"] for a in mailbox_api.list_agents(tmp_path)}
    assert mailbox_api.OUTBOUND_TO_CHANNEL_QUEUE not in agents
    assert mailbox_api.OUTBOUND_TO_AGENT_QUEUE not in agents
    assert "outbound_delivery" not in agents


def test_filtered_messages_and_require_match_endpoint(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("AGENT_MAILBOX_DIR", str(tmp_path))
    _write_jsonl(
        tmp_path / "messages.jsonl",
        [
            {"id": "r0", "from": "a", "to": "b", "text": "alpha one"},
            {"id": "r1", "from": "b", "to": "a", "text": "beta two"},
            {"id": "r2", "from": "a", "to": "room-1", "channel_id": "room-1",
             "text": "gamma three"},
            {"id": "r3", "from": "a", "to": "b", "text": "alpha one",
             "audit_of": "r0"},
        ],
    )

    def ids(**kwargs: object) -> list[str]:
        return [m["id"] for m in mailbox_api.filtered_messages(tmp_path, **kwargs)]

    assert ids() == ["r0", "r1", "r2"]                 # everywhere, audit hidden
    assert ids(to="b") == ["r0"]
    assert ids(sender="a") == ["r0", "r2"]
    assert ids(channel="room-1") == ["r2"]             # involvement
    assert ids(channel_id="room-1") == ["r2"]          # routed send channel only
    assert ids(text="ALPHA") == ["r0"]                 # case-insensitive substring
    assert ids(text="/^(beta|gamma)/") == ["r1", "r2"]  # /regex/ form
    assert ids(sender="a", text="three") == ["r2"]     # constraints AND together
    assert ids(limit=2) == ["r1", "r2"]

    payload = mailbox_api.mailbox_messages(
        user="u", peer="p", channel=None, to="b", sender=None,
        channel_id=None, text=None, require=False, limit=200,
    )
    assert [m["id"] for m in payload["messages"]] == ["r0"]
    assert payload["filters"] == {
        "to": "b", "from": None, "channel": None, "channelId": None, "text": None}


def test_set_subscription_states_and_remove(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("AGENT_MAILBOX_DIR", str(tmp_path))
    fake = _FakeRelay()
    monkeypatch.setattr(mailbox_api, "_mailbox_client", fake)
    (tmp_path / "messages.jsonl").write_text("", encoding="utf-8")
    bridge = mailbox_api.MATTERMOST_BRIDGE_AGENT

    # Aliased agent folds; explicit subscribe records intent and syncs.
    result = mailbox_api._set_subscription("mattermost", "room-9", "subscribed")
    assert result["agent"] == bridge
    assert result["subscriptions"] == {"room-9": "subscribed"}
    assert result["sync"]["agents"] >= 1

    result = mailbox_api._set_subscription(bridge, "room-9", "unsubscribed")
    assert result["subscriptions"] == {"room-9": "unsubscribed"}

    # Remove clears the explicit setting (inference may still re-subscribe
    # cursor holders at sync time).
    result = mailbox_api._set_subscription(bridge, "room-9", "remove")
    assert result["subscriptions"] == {}

    assert "error" in mailbox_api._set_subscription(bridge, "room-9", "bogus")
    assert "error" in mailbox_api._set_subscription("server_registry", "room-9", "subscribed")
    assert "error" in mailbox_api._set_subscription("", "room-9", "subscribed")


def test_cursor_status_reports_entry_positions(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("AGENT_MAILBOX_DIR", str(tmp_path))
    fake = _FakeRelay()
    monkeypatch.setattr(mailbox_api, "_mailbox_client", fake)
    _write_jsonl(
        tmp_path / "messages.jsonl",
        [
            {"id": "c0", "from": "x", "to": "room-1", "channel_id": "room-1", "text": "one"},
            {"id": "c1", "from": "x", "to": "room-1", "channel_id": "room-1", "text": "two"},
            {"id": "c2", "from": "x", "to": "room-1", "channel_id": "room-1", "text": "three"},
        ],
    )
    ends = _line_ends(tmp_path / "messages.jsonl")
    fake._write_cursor(fake._cursor_path(tmp_path, "room-1:agent-a"), ends[1])

    status = mailbox_api._cursor_status(tmp_path, "room-1", "agent-a")

    assert status["entries_consumed"] == 2
    assert status["entry_next"] == "entry_2"
    assert status["entries_total"] == 3
    # An uninitialized cursor still reports how many entries the channel holds.
    empty = mailbox_api._cursor_status(tmp_path, "room-1", "agent-b")
    assert empty["initialized"] is False
    assert empty["entries_total"] == 3


def _fresh_remaps_cache() -> dict:
    return {
        "root": "", "size": -1, "at": 0.0,
        "channels": dict(mailbox_api.CHANNEL_ALIAS_CANONICAL),
        "agents": dict(mailbox_api.AGENT_ALIAS_CANONICAL),
    }


def test_outbound_legacy_records_split_by_content(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("AGENT_MAILBOX_DIR", str(tmp_path))
    monkeypatch.setattr(mailbox_api, "_REMAPS_CACHE", _fresh_remaps_cache())
    monkeypatch.setattr(mailbox_api, "_REMAP_USAGE", {})
    _write_jsonl(
        tmp_path / "messages.jsonl",
        [
            # Endpoint evidence -> an agent -> platform-channel delivery …
            {"id": "d1", "from": "codex", "to": "outbound_delivery", "text": "post",
             "endpoint_address": "mm/chat.example.io/abc"},
            # … no evidence -> an agent -> agent message.
            {"id": "d2", "from": "codex", "to": "outbound_delivery", "text": "ping"},
            # The old audit channel names fold straight into the queues.
            {"id": "d3", "from": "bridge", "to": "agent_to_agent", "text": "status"},
            {"id": "d4", "from": "bridge", "to": "agent_to_channel", "text": "copy"},
        ],
    )

    def ids(channel: str) -> list[str]:
        return [m["id"] for m in mailbox_api.channel_messages(tmp_path, channel)]

    assert ids(mailbox_api.OUTBOUND_TO_CHANNEL_QUEUE) == ["d1", "d4"]
    assert ids(mailbox_api.OUTBOUND_TO_AGENT_QUEUE) == ["d2", "d3"]
    # Legacy spellings keep working as queries: bare ids fold via the alias
    # table (outbound_delivery defaults to the channel queue).
    assert ids("outbound_delivery") == ["d1", "d4"]
    assert ids("agent_to_agent") == ["d2", "d3"]


def test_fold_usage_telemetry_counts_and_flushes(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("AGENT_MAILBOX_DIR", str(tmp_path))
    fake = _FakeRelay()
    monkeypatch.setattr(mailbox_api, "_mailbox_client", fake)
    monkeypatch.setattr(mailbox_api, "_REMAPS_CACHE", _fresh_remaps_cache())
    monkeypatch.setattr(mailbox_api, "_REMAP_USAGE", {})
    monkeypatch.setattr(mailbox_api, "_REMAP_USAGE_FLUSHED_AT", [0.0])
    _write_jsonl(
        tmp_path / "messages.jsonl",
        [
            {"id": "u1", "from": "a", "to": "server_registry",
             "channel_id": "server_registry", "text": "x"},
            {"id": "u2", "from": "a", "to": "server_registry", "text": "y"},
        ],
    )

    mailbox_api.channel_messages(tmp_path, mailbox_api.REGISTRY_CHANNEL)

    # One count per record per legacy id, keyed by the preposition set.
    usage = mailbox_api._REMAP_USAGE[("channel", "server_registry")]
    assert usage["canonical"] == mailbox_api.REGISTRY_CHANNEL
    assert usage["sets"] == {"to+channel_id": 1, "to": 1}

    mailbox_api._flush_remap_usage(tmp_path, force=True)
    assert mailbox_api._REMAP_USAGE == {}
    flushed = [r for r in fake.sent if r["type"] == "remap_usage"]
    assert len(flushed) == 1
    entry = flushed[0]["entry"]
    assert entry["id"] == "usage:channel:server_registry"
    assert entry["kind"] == "channel"
    assert entry["legacy"] == "server_registry"
    assert entry["sets"] == {"to+channel_id": 1, "to": 1}
    assert entry["total"] == 2


def test_set_remap_and_stored_folds_and_retire(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("AGENT_MAILBOX_DIR", str(tmp_path))
    fake = _FakeRelay()
    monkeypatch.setattr(mailbox_api, "_mailbox_client", fake)
    monkeypatch.setattr(mailbox_api, "_REMAPS_CACHE", _fresh_remaps_cache())
    monkeypatch.setattr(mailbox_api, "_REMAP_USAGE", {})
    (tmp_path / "messages.jsonl").write_text("", encoding="utf-8")

    result = mailbox_api._set_remap("old-room", "new-room", "channel")
    assert result["action"] == "set"
    sent = [r for r in fake.sent if r["type"] == "remap_entry"]
    assert sent[-1]["entry"] == {"id": "old-room", "canonical": "new-room", "kind": "channel"}

    # The fake relay does not persist; store the entries as the log would.
    def grooming(entry: dict, rid: str) -> dict:
        return {"id": rid, "from": "u", "to": mailbox_api.GROOMING_CHANNEL,
                "channel_id": mailbox_api.GROOMING_CHANNEL, "type": "remap_entry",
                "entry": entry}

    _write_jsonl(tmp_path / "messages.jsonl", [
        grooming({"id": "old-room", "canonical": "new-room", "kind": "channel"}, "m1"),
        grooming({"id": "old-bot", "canonical": "new-bot", "kind": "agent"}, "m2"),
    ])
    mailbox_api._refresh_remaps(tmp_path, force=True)
    assert mailbox_api._fold_channel("old-room") == "new-room"
    assert mailbox_api._fold_agent("old-bot") == "new-bot"

    # A later empty (or self) canonical retires the remap — seeds included.
    _write_jsonl(tmp_path / "messages.jsonl", [
        grooming({"id": "old-room", "canonical": "new-room", "kind": "channel"}, "m1"),
        grooming({"id": "old-bot", "canonical": "new-bot", "kind": "agent"}, "m2"),
        grooming({"id": "old-room", "canonical": "", "kind": "channel"}, "m3"),
        grooming({"id": "server_registry", "canonical": "server_registry",
                  "kind": "channel"}, "m4"),
    ])
    mailbox_api._refresh_remaps(tmp_path, force=True)
    assert mailbox_api._fold_channel("old-room") == "old-room"
    assert mailbox_api._fold_channel("server_registry") == "server_registry"
    assert mailbox_api._fold_agent("old-bot") == "new-bot"

    # Validation: no empty legacy, no bogus kind, no remapping service ids.
    assert "error" in mailbox_api._set_remap("", "x", "channel")
    assert "error" in mailbox_api._set_remap("x", "y", "bogus")
    assert "error" in mailbox_api._set_remap(
        mailbox_api.WORKER_QUEUE_CHANNEL, "y", "channel")

    # REST parity: the endpoint and worker op reach the same implementation.
    payload = mailbox_api.mailbox_remap(legacy="old-x", canonical="new-x", kind="agent")
    assert payload["action"] == "set"
    assert (payload["legacy"], payload["canonical"]) == ("old-x", "new-x")
    queued = mailbox_api.execute_worker_command(
        {"op": "set_remap", "legacy": "old-y", "canonical": "", "kind": "channel"})
    assert queued["action"] == "retired"
    listing = mailbox_api.mailbox_remaps()
    assert listing["channels"]["outbound_delivery"] == mailbox_api.OUTBOUND_TO_CHANNEL_QUEUE
    assert isinstance(listing["usage"], list)


def test_adapters_relays_registry_merges_seeds_config_and_stored(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(mailbox_api, "_REMAPS_CACHE", _fresh_remaps_cache())
    monkeypatch.setattr(mailbox_api, "_REMAP_USAGE", {})
    monkeypatch.delenv("MAILBOX_RELAY_CONFIG_DIR", raising=False)
    root = tmp_path / "mailbox"
    config_dir = tmp_path / "config"
    config_dir.mkdir(parents=True)
    config_dir.joinpath("relays.json").write_text(json.dumps({
        "connectors": [
            {"id": "mattermost-primary", "adapter": "mattermost", "enabled": True,
             "instance": "chat.example.org", "token_env": "MM_BOT_TOKEN"},
        ],
        "relays": [
            {"id": "retained-relay-1", "kind": "relay", "enabled": False,
             "source_channel": "general"},
        ],
    }), encoding="utf-8")
    _write_jsonl(root / "messages.jsonl", [
        # The adapter noted a login on the seeded IRC presence …
        {"id": "t1", "type": "relay_entry", "to": mailbox_api.ADAPTERS_RELAYS_CHANNEL,
         "entry": {"id": "irc_relay_presence_jllykifsh", "logged_in": True,
                   "session": "sock-7"}},
        # … and someone registered a brand-new adapter type as data.
        {"id": "t2", "type": "adapter_type_entry",
         "to": mailbox_api.ADAPTERS_RELAYS_CHANNEL,
         "entry": {"id": "xmpp", "presence": "single", "threads": False}},
    ])

    registry = mailbox_api.adapters_relays_registry(root)
    types = {item["id"]: item for item in registry["adapter_types"]}
    relays = {item["id"]: item for item in registry["relays"]}

    assert registry["channel"] == mailbox_api.ADAPTERS_RELAYS_CHANNEL
    # Code seeds are present and tagged.
    assert types["mattermost"]["source"] == "code"
    assert relays["mm_relay_presence_atom_ant"]["identity"] == "atom.ant"
    assert relays["mm_relay_presence_atom_ant"]["relay-chat"][0]["filter"] == {
        "as": "atom.ant"}
    assert relays["mm_relay_presence_min_botnick"]["token_env"] == "MM_BOT_TOKEN"
    # config/relays.json connectors + relays merge read-only; a connector's
    # "instance" is surfaced as the presence's "server".
    assert relays["mattermost-primary"]["source"] == "config"
    assert relays["mattermost-primary"]["server"] == "chat.example.org"
    assert relays["retained-relay-1"]["source_channel"] == "general"
    # Stored tracking overlays the seed declaration without erasing it.
    tracked = relays["irc_relay_presence_jllykifsh"]
    assert tracked["source"] == "stored"
    assert tracked["logged_in"] is True
    assert tracked["session"] == "sock-7"
    assert tracked["identity"] == "jllykifsh"
    assert tracked["channels"] == ["##logicmoo"]
    assert tracked["server"] == "irc.quakenet.org"
    assert types["xmpp"]["source"] == "stored"


def test_mailbox_adapters_relays_endpoint_returns_seeds(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("AGENT_MAILBOX_DIR", str(tmp_path))
    monkeypatch.delenv("MAILBOX_RELAY_CONFIG_DIR", raising=False)
    monkeypatch.setattr(mailbox_api, "_REMAPS_CACHE", _fresh_remaps_cache())
    monkeypatch.setattr(mailbox_api, "_REMAP_USAGE", {})
    _write_jsonl(tmp_path / "messages.jsonl", [])

    payload = mailbox_api.mailbox_adapters_relays()
    assert {item["id"] for item in payload["adapter_types"]} == set(
        mailbox_api.ADAPTER_TYPE_SEEDS)
    assert {item["id"] for item in payload["relays"]} >= set(mailbox_api.RELAY_SEEDS)


def test_edit_record_in_place_rewrites_line(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("AGENT_MAILBOX_DIR", str(tmp_path))
    monkeypatch.setattr(mailbox_api, "_mailbox_client", None)
    _write_jsonl(
        tmp_path / "messages.jsonl",
        [
            {"id": "r0", "from": "a", "to": "b", "text": "one"},
            {"id": "r1", "from": "a", "to": "b", "text": "two"},
            {"id": "r2", "from": "a", "to": "b", "text": "three"},
        ],
    )

    result = mailbox_api._edit_record(
        "r1",
        {"id": "IGNORED", "from": "a", "to": "b", "text": "TWO!", "note": 7},
        "in-place",
    )
    assert result["edited"] == "r1"
    assert result["mode"] == "in-place"
    assert result["record"]["id"] == "r1"  # log id survives the rewrite

    lines = [
        json.loads(line)
        for line in (tmp_path / "messages.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert [line["id"] for line in lines] == ["r0", "r1", "r2"]
    assert lines[1]["text"] == "TWO!"
    assert lines[1]["note"] == 7
    assert lines[0]["text"] == "one" and lines[2]["text"] == "three"
    assert list(tmp_path.glob("messages.jsonl.edited-*.bak"))

    missing = mailbox_api._edit_record("nope", {"to": "b"}, "in-place")
    assert str(missing["error"]).startswith("no record")
    assert "error" in mailbox_api._edit_record("r1", {"to": "b"}, "sideways")
    assert "error" in mailbox_api._edit_record("", {"to": "b"})
    assert "error" in mailbox_api._edit_record("r1", None)


def test_edit_record_at_end_appends_and_marks_replaced(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("AGENT_MAILBOX_DIR", str(tmp_path))
    fake = _FakeRelay()
    monkeypatch.setattr(mailbox_api, "_mailbox_client", fake)
    _write_jsonl(
        tmp_path / "messages.jsonl",
        [
            {"id": "r0", "from": "me", "to": "reg", "channel_id": "room",
             "type": "relay_entry", "text": "", "entry": {"x": 1}},
            {"id": "r1", "from": "me", "to": "reg", "channel_id": "room",
             "type": "relay_entry", "text": "", "entry": {"x": 2}},
        ],
    )

    result = mailbox_api._edit_record(
        "r0",
        {"from": "me", "to": "reg", "channel_id": "room", "type": "relay_entry",
         "text": "", "entry": {"x": 1, "enabled": True}},
        "at-end",
    )
    assert result["mode"] == "at-end"
    key = result["entryKey"]
    assert key.startswith("entry_")
    assert result["replacedByMarking"] == "ok"
    # The append went through the client with the fresh entry_key and payload.
    assert fake.sent
    appended = fake.sent[-1]
    assert appended["entry_key"] == key
    assert appended["entry"] == {"x": 1, "enabled": True}
    assert appended["channel_id"] == "room"
    assert appended["id"] != "r0"  # fresh log id, not the old one
    # The old line is still in place but marked as replaced.
    lines = [
        json.loads(line)
        for line in (tmp_path / "messages.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert [line["id"] for line in lines] == ["r0", "r1"]
    assert lines[0]["replaced-by"] == key
    assert lines[1].get("replaced-by") is None

    no_to = mailbox_api._edit_record("r0", {"text": "x"}, "at-end")
    assert "needs a 'to'" in str(no_to["error"])
    missing = mailbox_api._edit_record(
        "ghost", {"from": "me", "to": "reg", "text": ""}, "at-end"
    )
    assert str(missing["error"]).startswith("no record")
    assert len(fake.sent) == 1  # nothing appended for a record that isn't there


def test_edit_record_at_end_marks_old_line_for_shared_config_ids(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Config-entry versions share their entity id; at-end must mark the OLD line."""

    monkeypatch.setenv("AGENT_MAILBOX_DIR", str(tmp_path))

    class _WritingRelay(_FakeRelay):
        def __init__(self, path: Path) -> None:
            super().__init__()
            self._path = path

        def send(self, to, text, **kwargs):  # noqa: ANN001
            record = super().send(to, text, **kwargs)
            with self._path.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(record, ensure_ascii=False) + "\n")
            return record

    fake = _WritingRelay(tmp_path / "messages.jsonl")
    monkeypatch.setattr(mailbox_api, "_mailbox_client", fake)
    _write_jsonl(
        tmp_path / "messages.jsonl",
        [
            {"id": "rel_a", "kind": "relay_entry", "from": "me", "to": "reg",
             "channel_id": "reg", "type": "relay_entry", "text": "", "enabled": False},
            {"id": "rel_a", "kind": "relay_entry", "from": "me", "to": "reg",
             "channel_id": "reg", "type": "relay_entry", "text": "", "enabled": True},
        ],
    )

    result = mailbox_api._edit_record(
        "rel_a",
        {"id": "rel_a", "kind": "relay_entry", "from": "me", "to": "reg",
         "channel_id": "reg", "type": "relay_entry", "text": "", "enabled": False},
        "at-end",
    )
    key = result["entryKey"]
    assert result["replacedByMarking"] == "ok"
    # A config entry keeps its entity id on the appended version.
    assert fake.sent[-1]["id"] == "rel_a"
    lines = [
        json.loads(line)
        for line in (tmp_path / "messages.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert len(lines) == 3
    # The line that was current BEFORE the edit is the one marked, never the
    # fresh append (which shares the same id).
    assert lines[1]["replaced-by"] == key
    assert "replaced-by" not in lines[0]
    assert "replaced-by" not in lines[2]


def test_stored_entity_entries_reads_flat_and_folds_changed_keys(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(mailbox_api, "_REMAPS_CACHE", _fresh_remaps_cache())
    monkeypatch.setattr(mailbox_api, "_REMAP_USAGE", {})
    root = tmp_path / "mailbox"
    reg = mailbox_api.ADAPTERS_RELAYS_CHANNEL
    _write_jsonl(root / "messages.jsonl", [
        # Flat config entry: the blob IS the record top level.
        {"id": "rel_a", "kind": "relay_entry", "type": "relay_entry", "to": reg,
         "channel_id": reg, "from": "me", "text": "", "timestamp": "t",
         "entry_key": "entry_1", "adapter": "irc", "enabled": False},
        # Legacy nested record still reads.
        {"id": "log-uuid-1", "type": "relay_entry", "to": reg,
         "entry": {"id": "rel_b", "x": 1}},
        # changed_keys = MERGE: only the changed keys, folded over the current.
        {"id": "rel_a", "kind": "relay_entry_changed_keys",
         "type": "relay_entry_changed_keys", "to": reg, "channel_id": reg,
         "from": "adapter", "text": "", "logged_in": True},
        # Plain <type> = REPLACEMENT: the previous rel_b entry is discarded.
        {"id": "rel_b", "kind": "relay_entry", "type": "relay_entry", "to": reg,
         "channel_id": reg, "from": "me", "text": "", "y": 2},
    ])

    entries = mailbox_api.stored_entity_entries(root, "relay_entry", reg)
    assert set(entries) == {"rel_a", "rel_b"}
    # Envelope fields stay out; the changed-keys patch merged in; kind folds
    # back to the base type.
    assert entries["rel_a"] == {
        "id": "rel_a", "kind": "relay_entry", "adapter": "irc",
        "enabled": False, "logged_in": True,
    }
    assert entries["rel_b"] == {"id": "rel_b", "kind": "relay_entry", "y": 2}


def test_mailbox_record_endpoint_validates(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("AGENT_MAILBOX_DIR", str(tmp_path))
    monkeypatch.setattr(mailbox_api, "_mailbox_client", None)
    _write_jsonl(
        tmp_path / "messages.jsonl",
        [{"id": "r0", "from": "a", "to": "b", "text": "x"}],
    )

    with pytest.raises(mailbox_api.HTTPException) as missing:
        mailbox_api.mailbox_record_edit(id="nope", record={"to": "b"}, mode="in-place")
    assert missing.value.status_code == 404
    with pytest.raises(mailbox_api.HTTPException) as bad_mode:
        mailbox_api.mailbox_record_edit(id="r0", record={"to": "b"}, mode="sideways")
    assert bad_mode.value.status_code == 400
    with pytest.raises(mailbox_api.HTTPException) as no_client:
        mailbox_api.mailbox_record_edit(id="r0", record={"to": "b"}, mode="at-end")
    assert no_client.value.status_code == 503

    ok = mailbox_api.mailbox_record_edit(
        id="r0", record={"from": "a", "to": "b", "text": "edited"}, mode="in-place"
    )
    assert ok["record"]["text"] == "edited"
