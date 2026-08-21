from __future__ import annotations

import sys
from pathlib import Path

import pytest


SCRIPTS_ROOT = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_ROOT))

import mailbox_codex_listener as listener  # noqa: E402


class FakeRelayClient:
    """Stand-in for the mailbox_channels REST surface."""

    def __init__(self, records_by_source: dict[str, list[dict]] | None = None) -> None:
        self.records_by_source = records_by_source or {}
        self.sent: list[dict] = []
        self.acked: list[tuple[str, str]] = []
        self.registered: list[tuple[str, str]] = []
        self.cursors: list[tuple[str, str, str]] = []

    def peek_rest(self, recipient: str, *, base_url: str | None = None, cursor: str | None = None) -> list[dict]:
        return list(self.records_by_source.get(recipient, []))

    def send_rest(self, recipient: str, text: str, *, sender: str = "", base_url: str | None = None) -> dict:
        record = {"id": "sent-1", "from": sender, "to": recipient, "text": text, "type": "message", "timestamp": "t"}
        self.sent.append(record)
        return record

    def acknowledge_rest(self, recipient: str, message_id: str, *, base_url: str | None = None, cursor: str | None = None) -> bool:
        self.acked.append((recipient, message_id))
        return True

    def register_agent_rest(self, agent_id: str, *, presence_id: str = "", dry_run: bool = False, base_url: str | None = None) -> dict:
        self.registered.append((agent_id, presence_id))
        return {"agent_id": agent_id, "presence_id": presence_id}

    def initialize_cursor_rest(self, recipient: str, *, cursor: str, start: str = "now", base_url: str | None = None) -> dict:
        self.cursors.append((recipient, cursor, start))
        return {"recipient": recipient, "cursor": cursor, "start": start}

    def status_rest(self, *, base_url: str | None = None) -> dict:
        return {"agents": [{"agent_id": listener.DEFAULT_AGENT}]}


def test_default_sources_include_shared_channel_agent_and_events() -> None:
    assert listener.default_sources("github-copilot-facilitator-agent") == [
        "symbolic-workbench-user",
        "github-copilot-facilitator-agent",
        "server_events",
    ]


def test_poll_until_returns_on_first_message() -> None:
    batches = [[], [{"id": "1", "text": "hi"}]]
    state, messages = listener.poll_until(
        timeout=100,
        interval=1,
        peek=lambda: batches.pop(0),
        now=lambda: 0.0,
        sleep=lambda _seconds: None,
    )
    assert state == "message"
    assert messages == [{"id": "1", "text": "hi"}]


def test_poll_until_times_out_idle() -> None:
    clock = {"t": 0.0}

    def fake_now() -> float:
        clock["t"] += 1.0
        return clock["t"]

    state, messages = listener.poll_until(
        timeout=3,
        interval=1,
        peek=lambda: [],
        now=fake_now,
        sleep=lambda _seconds: None,
    )
    assert state == "idle"
    assert messages == []


def test_unread_across_sources_tags_source_and_skips_audit(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = FakeRelayClient({
        "github-copilot-facilitator-agent": [
            {"id": "1", "from": "user", "to": "github-copilot-facilitator-agent", "text": "hi"},
            {"id": "2", "from": "user", "to": "github-copilot-facilitator-agent", "text": "copy", "audit_of": "1"},
        ],
        "server_events": [{"id": "e1", "to": "server_events", "text": "started"}],
    })
    monkeypatch.setattr(listener, "_mailbox", fake)
    unread = listener.unread_across_sources(
        sources=["github-copilot-facilitator-agent", "server_events"],
        cursor="github-copilot-facilitator-agent",
    )
    assert [message["id"] for message in unread] == ["1", "e1"]
    assert {message["source"] for message in unread} == {"github-copilot-facilitator-agent", "server_events"}


def test_unread_across_sources_excludes_self(monkeypatch: pytest.MonkeyPatch) -> None:
    # Loop suppression: never react to the agent's own posts on a shared channel.
    fake = FakeRelayClient({
        "symbolic-workbench-user": [
            {"id": "1", "from": "symbolic-workbench-user", "to": "symbolic-workbench-user", "text": "hi"},
            {"id": "2", "from": "github-copilot-facilitator-agent", "to": "symbolic-workbench-user", "text": "my own reply"},
        ],
    })
    monkeypatch.setattr(listener, "_mailbox", fake)
    unread = listener.unread_across_sources(
        sources=["symbolic-workbench-user"],
        cursor="github-copilot-facilitator-agent",
        exclude_from="github-copilot-facilitator-agent",
    )
    assert [message["id"] for message in unread] == ["1"]


def test_register_worker_registers_and_inits_cursors(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = FakeRelayClient()
    monkeypatch.setattr(listener, "_mailbox", fake)
    result = listener.register_worker(
        "github-copilot-facilitator-agent",
        presence="github-copilot-facilitator-agent-app",
        sources=["github-copilot-facilitator-agent", "server_events"],
    )
    assert fake.registered == [("github-copilot-facilitator-agent", "github-copilot-facilitator-agent-app")]
    assert fake.cursors == [
        ("github-copilot-facilitator-agent", "github-copilot-facilitator-agent", "now"),
        ("server_events", "github-copilot-facilitator-agent", "now"),
    ]
    assert result["agent"] == "github-copilot-facilitator-agent"


def test_send_message_posts_over_rest(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = FakeRelayClient()
    monkeypatch.setattr(listener, "_mailbox", fake)
    record = listener.send_message("**hi**", sender="github-copilot-facilitator-agent", recipient="symbolic-workbench-user")
    assert record["from"] == "github-copilot-facilitator-agent"
    assert record["to"] == "symbolic-workbench-user"
    assert fake.sent and fake.sent[0]["text"] == "**hi**"


def test_send_message_rejects_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(listener, "_mailbox", FakeRelayClient())
    with pytest.raises(ValueError):
        listener.send_message("   ", sender="agent", recipient="user")


def test_ack_messages_acknowledges_each_id(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = FakeRelayClient()
    monkeypatch.setattr(listener, "_mailbox", fake)
    handled = listener.ack_messages("github-copilot-facilitator-agent", ["1", "", "2"], cursor="github-copilot-facilitator-agent")
    assert handled == 2
    assert fake.acked == [
        ("github-copilot-facilitator-agent", "1"),
        ("github-copilot-facilitator-agent", "2"),
    ]


def test_poll_command_exit_codes(monkeypatch: pytest.MonkeyPatch) -> None:
    outcomes = [[], [{"id": "1", "from": "user", "to": listener.DEFAULT_AGENT, "text": "ping", "source": listener.DEFAULT_AGENT}]]
    monkeypatch.setattr(listener, "unread_across_sources", lambda *a, **k: outcomes.pop(0))
    assert listener.main(["poll", "--timeout", "0", "--interval", "1"]) == listener.EXIT_IDLE
    assert listener.main(["poll", "--timeout", "0", "--interval", "1"]) == listener.EXIT_MESSAGE


def test_ensure_relay_reports_running_when_port_open() -> None:
    result = listener.ensure_relay(check=lambda: True, spawn=lambda command, cwd: 123)
    assert result["state"] == "running"
    assert result["action"] == "none"
