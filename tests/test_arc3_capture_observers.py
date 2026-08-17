from pathlib import Path
from types import SimpleNamespace

from action_tree import StateNode
from arc3_runner import Arc3Runner
from object_memory import SemanticGridCaptureObserver, standard_semantic_grid_observer


class RecordingObserver:
    def __init__(self) -> None:
        self.events: list[dict[str, object]] = []

    def on_state_captured(self, **event: object) -> None:
        self.events.append(event)


class FailingObserver:
    def on_state_captured(self, **_event: object) -> None:
        raise RuntimeError("semantic service offline")


class AuthorizationObserver:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, str]]] = []

    def authorization_options(self) -> dict[str, tuple[str, ...]]:
        return {"candidate-blue": ("blue_shape", "blue_block")}

    def authorize_candidate(self, **values: str) -> str:
        self.calls.append(("accept", values))
        return "accepted"

    def reject_candidate(self, **values: str) -> str:
        self.calls.append(("reject", values))
        return "rejected"


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


def test_runner_exposes_explicit_semantic_authorization_controls() -> None:
    observer = AuthorizationObserver()
    runner = Arc3Runner.__new__(Arc3Runner)
    runner.capture_observers = (RecordingObserver(), observer)

    assert runner.semantic_authorization_options() == {
        "candidate-blue": ("blue_shape", "blue_block")
    }
    assert runner.authorize_semantic_candidate(
        candidate_id="candidate-blue",
        selected_identity_id="blue_shape",
        decision_id="human-accept-1",
    ) == "accepted"
    assert runner.reject_semantic_candidate(
        candidate_id="candidate-blue",
        selected_identity_id="blue_block",
        decision_id="human-reject-1",
    ) == "rejected"
    assert observer.calls == [
        (
            "accept",
            {
                "candidate_id": "candidate-blue",
                "selected_identity_id": "blue_shape",
                "decision_id": "human-accept-1",
                "decision_source": "explicit_registry_selection",
            },
        ),
        (
            "reject",
            {
                "candidate_id": "candidate-blue",
                "selected_identity_id": "blue_block",
                "decision_id": "human-reject-1",
                "decision_source": "explicit_registry_rejection",
            },
        ),
    ]


def test_standard_semantic_observer_uses_runner_grid_and_single_writer() -> None:
    observer = standard_semantic_grid_observer()
    runner = Arc3Runner.__new__(Arc3Runner)
    runner.current_observation = {"grid": [[0, 1], [2, 0]]}
    runner.env = SimpleNamespace(observation_space=None)

    assert isinstance(observer, SemanticGridCaptureObserver)
    assert observer.identity_writer is not None
    assert observer.grid_selector(runner).tolist() == [[0, 1], [2, 0]]


def test_canonical_runners_enable_semantic_capture_with_an_explicit_opt_out() -> None:
    root = Path(__file__).resolve().parents[1]
    interactive = (root / "python" / "interactive_runner.py").read_text(encoding="utf-8")
    prolog = (root / "scripts" / "prolog_controlled_runner.py").read_text(encoding="utf-8")

    for source in (interactive, prolog):
        assert "standard_semantic_grid_observer" in source
        assert "--no-semantic-capture" in source
        assert "capture_observers=observers" in source
