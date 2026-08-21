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

