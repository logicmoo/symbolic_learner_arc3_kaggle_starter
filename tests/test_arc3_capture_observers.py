from pathlib import Path
from types import SimpleNamespace

from action_tree import StateNode
from arc3_runner import Arc3Runner


class RecordingObserver:
    def __init__(self) -> None:
        self.events: list[dict[str, object]] = []

    def on_state_captured(self, **event: object) -> None:
        self.events.append(event)


class FailingObserver:
    def on_state_captured(self, **_event: object) -> None:
        raise RuntimeError("semantic service offline")


def test_capture_observers_receive_external_phase1_node_events(capsys) -> None:
    recording = RecordingObserver()
    runner = Arc3Runner.__new__(Arc3Runner)
    runner.capture_observers = (FailingObserver(), recording)
    runner.tree_store = SimpleNamespace(object_registry_path=Path("registry.pl"))
    node = StateNode(Path("node"), "hash")
    parent = StateNode(Path("parent"), "parent-hash")

    runner._notify_state_captured(
        node,
        previous_node=parent,
        action="RIGHT",
        data={"x": 2},
    )

    assert len(recording.events) == 1
    assert recording.events[0]["runner"] is runner
    assert recording.events[0]["node"] is node
    assert recording.events[0]["previous_node"] is parent
    assert recording.events[0]["action"] == "RIGHT"
    assert recording.events[0]["data"] == {"x": 2}
    assert "capture observer failed (FailingObserver)" in capsys.readouterr().out
