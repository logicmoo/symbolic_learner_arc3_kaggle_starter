import json
import hashlib
from pathlib import Path

from scripts import agent_mailbox


def test_send_and_receive_are_filtered_and_consumed(tmp_path: Path) -> None:
    first = agent_mailbox.send("agent-a", "hello λ", sender="agent-b", root=tmp_path)
    agent_mailbox.send("agent-c", "not yours", root=tmp_path)

    assert agent_mailbox.receive("agent-a", root=tmp_path) == [first]
    assert agent_mailbox.receive("agent-a", root=tmp_path) == []
    assert [item["text"] for item in agent_mailbox.receive("agent-c", root=tmp_path)] == ["not yours"]


def test_receive_leaves_partial_last_record_for_next_call(tmp_path: Path) -> None:
    path = tmp_path / "messages.jsonl"
    tmp_path.mkdir(exist_ok=True)
    record = {"id": "1", "timestamp": "now", "from": "a", "to": "b", "type": "message", "text": "hi"}
    encoded = json.dumps(record).encode("utf-8")
    path.write_bytes(encoded)

    assert agent_mailbox.receive("b", root=tmp_path) == []
    with path.open("ab") as stream:
        stream.write(b"\n")
    assert agent_mailbox.receive("b", root=tmp_path) == [record]


def test_environment_override_controls_cli_storage(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.setenv(agent_mailbox.MAILBOX_ENV, str(tmp_path))

    assert agent_mailbox.main(["send", "omegaclaw-core-codex", "ready"]) == 0
    sent = json.loads(capsys.readouterr().out)
    assert sent["from"] == agent_mailbox.DEFAULT_SENDER

    assert agent_mailbox.main(["receive", "omegaclaw-core-codex"]) == 0
    received = json.loads(capsys.readouterr().out)
    assert received["id"] == sent["id"]


def test_status_does_not_create_mailbox(tmp_path: Path) -> None:
    result = agent_mailbox.status(root=tmp_path)
    assert result["size_bytes"] == 0
    assert result["peers"] == ["omegaclaw-core-codex", "omegaclaw-min"]
    assert not (tmp_path / "messages.jsonl").exists()
    assert not (tmp_path / "cursors").exists()


def test_send_copies_repeatable_attachments_with_metadata(tmp_path: Path) -> None:
    first_dir = tmp_path / "sources-a"
    second_dir = tmp_path / "sources-b"
    first_dir.mkdir()
    second_dir.mkdir()
    first = first_dir / "result.png"
    second = second_dir / "result.png"
    first.write_bytes(b"first image")
    second.write_bytes(b"second image")

    sent = agent_mailbox.send("agent-a", "screenshots", attachments=[first, second], root=tmp_path)

    assert [item["name"] for item in sent["attachments"]] == ["result.png", "result-2.png"]
    for attachment, expected in zip(sent["attachments"], (b"first image", b"second image")):
        copied = Path(attachment["path"])
        assert copied.parent == tmp_path / "attachments" / sent["id"]
        assert copied.read_bytes() == expected
        assert attachment["mime_type"] == "image/png"
        assert attachment["size"] == len(expected)
        assert attachment["sha256"] == hashlib.sha256(expected).hexdigest()
    assert agent_mailbox.receive("agent-a", root=tmp_path) == [sent]


def test_cli_send_accepts_repeated_attach_options(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.setenv(agent_mailbox.MAILBOX_ENV, str(tmp_path / "mailbox"))
    first = tmp_path / "one.txt"
    second = tmp_path / "two.json"
    first.write_text("one", encoding="utf-8")
    second.write_text("{}", encoding="utf-8")

    assert agent_mailbox.main(
        ["send", "agent-a", "files", "--attach", str(first), "--attach", str(second)]
    ) == 0

    sent = json.loads(capsys.readouterr().out)
    assert [item["mime_type"] for item in sent["attachments"]] == ["text/plain", "application/json"]


def test_send_preserves_optional_relay_routing_context(tmp_path: Path) -> None:
    sent = agent_mailbox.send(
        "agent-a",
        "thread reply",
        sender="agent-b",
        message_type="mattermost_reply",
        channel_id="channel-1",
        channel_type="mattermost",
        source_id="post-2",
        thread_id="thread-3",
        root_id="post-1",
        root=tmp_path,
    )

    assert sent["from"] == "agent-b"
    assert sent["to"] == "agent-a"
    assert sent["type"] == "mattermost_reply"
    assert sent["timestamp"].endswith("Z")
    assert {key: sent[key] for key in ("channel_id", "channel_type", "source_id", "thread_id", "root_id")} == {
        "channel_id": "channel-1",
        "channel_type": "mattermost",
        "source_id": "post-2",
        "thread_id": "thread-3",
        "root_id": "post-1",
    }
    assert agent_mailbox.receive("agent-a", root=tmp_path) == [sent]


def test_flat_channel_send_does_not_invent_thread_context(tmp_path: Path) -> None:
    sent = agent_mailbox.send(
        "agent-a",
        "flat relay",
        channel_id="channel-1",
        channel_type="mattermost",
        source_id="post-1",
        root=tmp_path,
    )

    assert sent["channel_id"] == "channel-1"
    assert "thread_id" not in sent
    assert "root_id" not in sent


def test_cli_send_accepts_routing_context_without_requiring_thread(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.setenv(agent_mailbox.MAILBOX_ENV, str(tmp_path))

    assert agent_mailbox.main(
        [
            "send", "agent-a", "routed", "--type", "mattermost_message",
            "--channel-id", "channel-1", "--channel-type", "mattermost", "--source-id", "post-1",
        ]
    ) == 0

    sent = json.loads(capsys.readouterr().out)
    assert sent["type"] == "mattermost_message"
    assert sent["channel_id"] == "channel-1"
    assert sent["source_id"] == "post-1"
    assert "thread_id" not in sent
    assert "root_id" not in sent
