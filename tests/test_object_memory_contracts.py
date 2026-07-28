from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from object_memory import (  # noqa: E402
    CandidateObject,
    CommittedAtom,
    ExecutionMode,
    PredictionLedger,
    PredictionRecord,
    PythonProvider,
    ResidualCandidate,
    ResidualDisposition,
    ResidualGate,
    SingleWriter,
    SymbolicMemory,
)


def test_python_provider_delegates_and_normalizes() -> None:
    provider = PythonProvider({"properties": lambda candidate: {"id": candidate.candidate_id}})
    candidate = CandidateObject("ball", "obs-1", "grid", provider)
    result = candidate.part("properties")
    assert result.mode is ExecutionMode.PYTHON
    assert result.value == {"id": "ball"}


def test_single_writer_forces_zero_confidence() -> None:
    writer = SingleWriter(SymbolicMemory())
    atom = writer.commit(CommittedAtom("ball", "object", {}, confidence=0.9))
    assert atom.confidence == 0.0


def test_residual_gate_promotes_structured_recurring_candidate() -> None:
    residual = ResidualCandidate(
        "r1", "ball", ResidualDisposition.PROVISIONAL, 3.0,
        structured=True, recurrence_count=2,
    )
    assert ResidualGate().evaluate(residual) is ResidualDisposition.COMMIT_REQUEST


def test_prediction_must_precede_outcome() -> None:
    ledger = PredictionLedger()
    ledger.record(PredictionRecord("p1", "rule-1", "state-1", ("move",), 10))
    try:
        ledger.grade("p1", outcome_sequence=10, outcome="move", grade=1.0)
    except ValueError:
        pass
    else:
        raise AssertionError("same-sequence outcome must be rejected")
    closed = ledger.grade("p1", outcome_sequence=11, outcome="move", grade=1.0)
    assert closed.grade == 1.0


def test_protected_kaggle_paths_exist() -> None:
    for relative in (
        "notebooks/submission.ipynb",
        "scripts/build_notebook.py",
        "scripts/play_local.py",
        "agent/my_agent.py",
    ):
        assert (ROOT / relative).exists(), relative
