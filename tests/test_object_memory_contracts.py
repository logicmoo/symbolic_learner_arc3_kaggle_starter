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
    GameLearningPipeline,
    GameObjectLearnerPayload,
    GptArtifactProvider,
    IntegrationError,
    IntegrationValidator,
    InMemorySemanticBackend,
    OutcomeChannel,
    PipelineGameObjectLearnerPlugin,
    PredictionEvaluator,
    PredictionGrade,
    PredictionGradeStatus,
    PredictionLedger,
    PredictionRecord,
    PrologProvider,
    PythonProvider,
    ResidualCandidate,
    ResidualDisposition,
    ResidualGate,
    RuleExecutor,
    RuleInducer,
    RuleRanker,
    RuleStore,
    SingleWriter,
    SymbolicMemory,
    SymbolicStore,
    TransformationCandidate,
    TransformationLearner,
    TransitionAnalyzer,
    TransitionRecord,
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


def test_prolog_provider_exposes_every_normalized_learner_record_family() -> None:
    calls = []
    provider = PrologProvider(
        lambda predicate, payload: calls.append((predicate, payload)) or [payload]
    )

    for family, namespace in provider.SEMANTIC_NAMESPACES.items():
        result = provider.get_semantic_records(family, {"source": "fixture"})
        assert result.metadata["payload"] == {
            "namespace": namespace,
            "filters": {"source": "fixture"},
        }
        assert result.source_refs == (f"prolog:semantic_record/3:{namespace}",)
    assert [predicate for predicate, _payload in calls] == [
        "semantic_records"
    ] * len(provider.SEMANTIC_NAMESPACES)


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


def test_prediction_grades_classify_outcomes_without_penalizing_ungradable() -> None:
    assert PredictionGrade(1.0).status is PredictionGradeStatus.SUCCESS
    assert PredictionGrade(0.0).status is PredictionGradeStatus.FAILURE
    assert PredictionGrade(0.5).status is PredictionGradeStatus.PARTIAL_MATCH
    assert (
        PredictionGrade(
            0.0, status=PredictionGradeStatus.CONTRADICTION
        ).status
        is PredictionGradeStatus.CONTRADICTION
    )
    assert PredictionGrade(None).status is PredictionGradeStatus.UNGRADABLE
    for invalid in (
        lambda: PredictionGrade(None, status=PredictionGradeStatus.FAILURE),
        lambda: PredictionGrade(0.0, status=PredictionGradeStatus.SUCCESS),
        lambda: PredictionGrade(1.0, status=PredictionGradeStatus.UNGRADABLE),
    ):
        try:
            invalid()
        except ValueError:
            pass
        else:
            raise AssertionError("inconsistent prediction grade must be rejected")


def test_phase3_pipeline_learns_predicts_and_grades() -> None:
    rule_store = RuleStore()
    ledger = PredictionLedger()
    semantic_store = SymbolicStore(InMemorySemanticBackend())
    pipeline = GameLearningPipeline(
        TransitionAnalyzer(
            lambda before, action, after: TransitionRecord(
                before.state_id,
                action,
                after.state_id,
                ("moved_right",),
            )
        ),
        TransformationLearner(
            lambda transition: (
                TransformationCandidate(
                    "move-right",
                    transition.changes[0],
                    evidence=(transition.before_state_id, transition.after_state_id),
                ),
            )
        ),
        RuleInducer(
            lambda candidates: (
                TransitionRule(
                    "rule-move-right",
                    ("player_present",),
                    "right",
                    (candidates[0].transformation,),
                    assumptions=("player identity is stable",),
                    critiques=("single observation",),
                    supporting_evidence_ids=("learning-evidence",),
                    bootstrap_probability=0.4,
                ),
            )
        ),
        RuleRanker(lambda rule: float(len(rule.predicted_effects))),
        rule_store,
        ledger,
        semantic_store,
    )
    plugin = PipelineGameObjectLearnerPlugin(pipeline)
    before = GameObjectLearnerPayload("state-1", ({"id": "player", "x": 1},))
    after = GameObjectLearnerPayload("state-2", ({"id": "player", "x": 2},))

    learned = plugin.consume_transition(before, "right", after)
    assert learned.mode is ExecutionMode.PYTHON
    assert learned.value.learning_step.rules[0].rule_id == "rule-move-right"

    executor = RuleExecutor(
        rule_store,
        checker=lambda _rule, state: bool(state.get("player_present")),
        executor=lambda rule, state: {**state, "effect": rule.predicted_effects[0]},
    )
    predicted, record = pipeline.predict(
        prediction_id="prediction-1",
        rule_id="rule-move-right",
        source_state_id="state-2",
        state={"player_present": True},
        created_sequence=20,
        executor=executor,
    )
    assert record.outcome_sequence is None
    assert record.available_evidence_ids == ("learning-evidence",)
    assert record.rule_assumptions == ("player identity is stable",)
    assert record.rule_critiques == ("single observation",)
    assert record.rule_probability == 0.4
    assert record.rule_probability_source == "bootstrap"
    closed = pipeline.grade_prediction(
        prediction_id="prediction-1",
        outcome_sequence=21,
        outcome_channel=OutcomeChannel(lambda: predicted),
        evaluator=PredictionEvaluator(
            lambda expected, observed: PredictionGrade(
                1.0 if expected == observed else 0.0,
                evidence=("independent_outcome",),
            )
        ),
    )
    assert closed.grade == 1.0
    refined = rule_store.get("rule-move-right")
    assert refined.prediction_attempts == 1
    assert refined.prediction_successes == 1
    assert refined.prediction_history == ("prediction-1",)
    assert refined.calibrated_probability == 2.0 / 3.0
    assert refined.probability_source == "verified_prediction_history"
    assert len(refined.supporting_evidence_ids) == 2
    assert refined.supporting_evidence_ids[0] == "learning-evidence"
    assert refined.contradicting_evidence_ids == ()
    persisted_prediction = semantic_store.get("predictions", "prediction-1")
    persisted_grade = semantic_store.get("prediction_grades", "prediction-1")
    assert persisted_prediction.outcome_sequence is None
    assert persisted_prediction.grade is None
    assert persisted_grade.outcome == predicted
    assert persisted_grade.grade == 1.0
    assert persisted_grade.evidence == ("independent_outcome",)
    assert persisted_grade.evidence_record_ids == refined.supporting_evidence_ids[1:]
    assert persisted_grade.calibrated_probability == 2.0 / 3.0
    persisted_evidence = semantic_store.get(
        "evidence", persisted_grade.evidence_record_ids[0]
    )
    assert persisted_evidence.subject_id == "rule-move-right"
    assert persisted_evidence.polarity.value == "supports"
    assert persisted_evidence.weight == 1.0

    replayed = SymbolicStore(InMemorySemanticBackend()).replay(
        semantic_store.snapshot()
    )
    assert replayed.get("predictions", "prediction-1") == persisted_prediction
    assert replayed.get("prediction_grades", "prediction-1") == persisted_grade

    _predicted_again, _ = pipeline.predict(
        prediction_id="prediction-2",
        rule_id="rule-move-right",
        source_state_id="state-3",
        state={"player_present": True},
        created_sequence=22,
        executor=executor,
    )
    pipeline.grade_prediction(
        prediction_id="prediction-2",
        outcome_sequence=23,
        outcome_channel=OutcomeChannel(lambda: {"effect": "did-not-move"}),
        evaluator=PredictionEvaluator(
            lambda expected, observed: PredictionGrade(
                1.0 if expected == observed else 0.0,
                evidence=("independent_contradiction",),
            )
        ),
    )
    contradicted = rule_store.get("rule-move-right")
    assert contradicted.prediction_attempts == 2
    assert contradicted.calibrated_probability == 0.5
    assert len(contradicted.contradicting_evidence_ids) == 1
    negative = semantic_store.get(
        "evidence", contradicted.contradicting_evidence_ids[0]
    )
    assert negative.polarity.value == "contradicts"
    assert negative.weight == 1.0

    _predicted_third, _ = pipeline.predict(
        prediction_id="prediction-3",
        rule_id="rule-move-right",
        source_state_id="state-4",
        state={"player_present": True},
        created_sequence=24,
        executor=executor,
    )
    pipeline.grade_prediction(
        prediction_id="prediction-3",
        outcome_sequence=25,
        outcome_channel=OutcomeChannel(lambda: {"observation": "occluded"}),
        evaluator=PredictionEvaluator(
            lambda _expected, _observed: PredictionGrade(
                None,
                evidence=("outcome_obscured",),
                status=PredictionGradeStatus.UNGRADABLE,
            )
        ),
    )
    ungraded = semantic_store.get("prediction_grades", "prediction-3")
    assert ungraded.status == "ungradable"
    assert ungraded.grade is None
    assert ungraded.evidence_record_ids == ()
    assert rule_store.get("rule-move-right").prediction_attempts == 2

    for duplicate_or_invalid in (
        {"prediction_id": "prediction-1", "grade": 1.0},
        {"prediction_id": "prediction-2", "grade": 1.1},
    ):
        try:
            rule_store.record_prediction_grade(
                "rule-move-right", **duplicate_or_invalid
            )
        except ValueError:
            pass
        else:
            raise AssertionError("invalid prediction feedback must be rejected")


def test_integration_validator_rejects_duplicate_object_identities() -> None:
    validator = IntegrationValidator()
    payload = GameObjectLearnerPayload(
        "state-1",
        ({"id": "player"}, {"id": "player"}),
    )
    try:
        validator.validate(payload)
    except IntegrationError:
        pass
    else:
        raise AssertionError("duplicate object identities must be rejected")


def test_protected_kaggle_paths_and_generated_notebook_contract() -> None:
    for relative in (
        "scripts/build_notebook.py",
        "scripts/play_local.py",
        "agent/my_agent.py",
        "notebooks/kernel-metadata.json",
    ):
        assert (ROOT / relative).exists(), relative

    builder = (ROOT / "scripts" / "build_notebook.py").read_text(encoding="utf-8")
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert 'NOTEBOOK_PATH = ROOT / "notebooks" / "submission.ipynb"' in builder
    assert "notebooks/submission.ipynb" in gitignore


def test_runnable_scripts_are_canonical() -> None:
    assert (ROOT / "scripts" / "interactive_runner.py").exists()
    assert (ROOT / "scripts" / "prolog_controlled_runner.py").exists()
    assert not (ROOT / "examples" / "interactive_runner.py").exists()
    assert not (ROOT / "examples" / "prolog_controlled_runner.py").exists()


def test_architecture_and_todo_documents_are_present() -> None:
    for relative in (
        "DEBUGGER.md",
        "KAGGLE.md",
        "SOW_PHASE_ARCHITECTURE.md",
        "TODO.md",
        "FILE_TREE.md",
    ):
        assert (ROOT / relative).exists(), relative
