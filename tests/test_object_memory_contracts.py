from __future__ import annotations

from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from object_memory import (  # noqa: E402
    CandidateObject,
    CommittedAtom,
    ExecutionMode,
    GptArtifactProvider,
    PredictionLedger,
    PredictionRecord,
    PrologProvider,
    PythonProvider,
    ResidualCandidate,
    ResidualDisposition,
    ResidualGate,
    RuleStore,
    SingleWriter,
    SymbolicMemory,
    TransitionRule,
)


def test_python_provider_delegates_and_normalizes() -> None:
    provider = PythonProvider({"properties": lambda candidate: {"id": candidate.candidate_id}})
    candidate = CandidateObject("ball", "obs-1", "grid", provider)
    result = candidate.part("properties")
    assert result.mode is ExecutionMode.PYTHON
    assert result.value == {"id": "ball"}


def test_three_modes_share_one_normalized_contract() -> None:
    artifact = "object_property(ball, color, red)."
    python_provider = PythonProvider({"properties": lambda _candidate: artifact})
    prolog_provider = PrologProvider(lambda _predicate, _payload: artifact)

    with tempfile.TemporaryDirectory() as directory:
        node = Path(directory)
        (node / "objects.pl").write_text(artifact, encoding="utf-8")
        gpt_provider = GptArtifactProvider(node)

        results = []
        for provider in (python_provider, prolog_provider, gpt_provider):
            candidate = CandidateObject("ball", "obs-1", "grid", provider)
            results.append(candidate.part("properties"))

    assert {result.mode for result in results} == {
        ExecutionMode.PYTHON,
        ExecutionMode.PROLOG,
        ExecutionMode.GPT,
    }
    assert {result.value for result in results} == {artifact}


def test_single_writer_forces_zero_confidence() -> None:
    writer = SingleWriter(SymbolicMemory())
    atom = writer.commit(CommittedAtom("ball", "object", {}, confidence=0.9))
    assert atom.confidence == 0.0


def test_residual_gate_promotes_structured_recurring_candidate() -> None:
    residual = ResidualCandidate(
        "r1",
        "ball",
        ResidualDisposition.PROVISIONAL,
        3.0,
        structured=True,
        recurrence_count=2,
    )
    assert ResidualGate().evaluate(residual) is ResidualDisposition.COMMIT_REQUEST


def test_single_writer_commits_only_an_admitted_residual() -> None:
    writer = SingleWriter(SymbolicMemory())
    gate = ResidualGate()
    provisional = ResidualCandidate(
        "r1", "ball", ResidualDisposition.PROVISIONAL, 3.0, structured=True
    )
    atom = CommittedAtom("ball", "object", {})
    try:
        writer.commit_residual(provisional, atom, gate)
    except ValueError:
        pass
    else:
        raise AssertionError("provisional residual must not be committed")

    admitted = ResidualCandidate(
        "r2",
        "ball",
        ResidualDisposition.PROVISIONAL,
        3.0,
        structured=True,
        recurrence_count=2,
    )
    assert writer.commit_residual(admitted, atom, gate).confidence == 0.0


def test_rule_store_uses_caller_supplied_domain_execution() -> None:
    store = RuleStore()
    rule = TransitionRule("rule-1", ("player",), "right", ("moved",))
    store.store(rule)
    assert store.applicable("rule-1", {"player": True}, lambda _rule, state: state["player"])
    result = store.apply(
        "rule-1",
        {"x": 2},
        lambda stored_rule, state: {**state, "effect": stored_rule.predicted_effects[0]},
    )
    assert result == {"x": 2, "effect": "moved"}


def test_prediction_must_precede_outcome() -> None:
    ledger = PredictionLedger()
    ledger.record(PredictionRecord("p1", "rule-1", "state-1", ("move",), 10))
    try:
        ledger.grade("p1", outcome_sequence=10, outcome="move", grade=1.0)
    except ValueError:
        pass
    else:
        raise AssertionError("same-sequence outcome must be rejected")
    assert ledger.get("p1").outcome_sequence is None
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


def test_no_duplicate_debugger_runner_was_added() -> None:
    assert (ROOT / "examples" / "interactive_runner.py").exists()
    assert not (ROOT / "scripts" / "interactive_runner.py").exists()
    assert not (ROOT / "scripts" / "prolog_controlled_runner.py").exists()


def test_architecture_and_annotated_tree_are_present() -> None:
    assert (ROOT / "docs" / "SOW_PHASE_ARCHITECTURE.md").exists()
    assert (ROOT / "docs" / "FILE_TREE.md").exists()
