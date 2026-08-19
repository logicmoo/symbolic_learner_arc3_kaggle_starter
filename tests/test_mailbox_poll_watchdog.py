from __future__ import annotations

import importlib.util
import os
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "scripts" / "mailbox_poll_watchdog.py"
SPEC = importlib.util.spec_from_file_location("mailbox_poll_watchdog", MODULE_PATH)
assert SPEC and SPEC.loader
watchdog = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(watchdog)


def test_current_process_is_alive() -> None:
    assert watchdog.process_alive(os.getpid())


def test_poll_command_is_scoped_to_one_agent() -> None:
    command = watchdog.poll_command("workbench-ui-codex-agent")
    assert command[command.index("--as") + 1] == "workbench-ui-codex-agent"
    assert command[command.index("--cursor") + 1] == "workbench-ui-codex-agent"
    assert command[command.index("--interval") + 1] == "5"
    assert command[command.index("--checks") + 1] == "61"


def test_runtime_state_is_isolated_per_agent(tmp_path: Path) -> None:
    first = watchdog.runtime_dir("agent-one", tmp_path)
    second = watchdog.runtime_dir("agent-two", tmp_path)
    assert first != second
    assert first.parent == second.parent == tmp_path


def test_spool_peek_requires_explicit_ack(tmp_path: Path) -> None:
    target = watchdog.runtime_dir("agent-one", tmp_path)
    target.mkdir(parents=True)
    spool = target / "deliveries.jsonl"
    spool.write_bytes(b'{"id":"one"}\n')

    assert watchdog.peek_spool("agent-one", tmp_path)[1] == b'{"id":"one"}\n'
    assert watchdog.peek_spool("agent-one", tmp_path)[1] == b'{"id":"one"}\n'

    watchdog.acknowledge_spool("agent-one", tmp_path)
    assert watchdog.peek_spool("agent-one", tmp_path)[1] == b""

    with spool.open("ab") as stream:
        stream.write(b'{"id":"two"}\n')
    assert watchdog.peek_spool("agent-one", tmp_path)[1] == b'{"id":"two"}\n'


def test_acknowledges_only_the_peeked_snapshot(tmp_path: Path) -> None:
    target = watchdog.runtime_dir("agent-one", tmp_path)
    target.mkdir(parents=True)
    spool = target / "deliveries.jsonl"
    first = b'{"id":"one"}\n'
    second = b'{"id":"two"}\n'
    spool.write_bytes(first)

    start, content = watchdog.peek_spool("agent-one", tmp_path)
    with spool.open("ab") as stream:
        stream.write(second)

    watchdog.acknowledge_spool(
        "agent-one",
        tmp_path,
        offset=start + len(content),
    )
    assert watchdog.peek_spool("agent-one", tmp_path)[1] == second
