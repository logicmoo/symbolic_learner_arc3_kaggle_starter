from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    from _runtime import configure_runtime_home
except ModuleNotFoundError:
    from scripts._runtime import configure_runtime_home

configure_runtime_home(__file__)

from omega_vision import (
    GameLearningPipeline,
    GameObjectLearnerPayload,
    InMemorySemanticBackend,
    OutcomeChannel,
    PipelineGameObjectLearnerPlugin,
    PredictionEvaluator,
    PredictionGrade,
    PredictionLedger,
    RuleExecutor,
    RuleInducer,
    RuleRanker,
    RuleStore,
    SymbolicStore,
    TransformationCandidate,
    TransformationLearner,
    TransitionAnalyzer,
    TransitionRecord,
    TransitionRule,
)


def run_demo(output_root: Path) -> dict[str, Any]:
    rule_store = RuleStore()
    ledger = PredictionLedger()
    semantic_store = SymbolicStore(InMemorySemanticBackend())
    pipeline = GameLearningPipeline(
        TransitionAnalyzer(
            lambda before, action, after: TransitionRecord(
                before.state_id, action, after.state_id, ("moved_right",)
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
    learned = PipelineGameObjectLearnerPlugin(pipeline).consume_transition(
        GameObjectLearnerPayload("state-1", ({"id": "player", "x": 1},)),
        "right",
        GameObjectLearnerPayload("state-2", ({"id": "player", "x": 2},)),
    ).value.learning_step
    executor = RuleExecutor(
        rule_store,
        checker=lambda _rule, state: bool(state.get("player_present")),
        executor=lambda rule, state: {**state, "effect": rule.predicted_effects[0]},
    )
    predicted, prediction = pipeline.predict(
        prediction_id="phase3-demo-prediction",
        rule_id=learned.rules[0].rule_id,
        source_state_id="state-2",
        state={"player_present": True},
        created_sequence=20,
        executor=executor,
    )
    persisted_before_grade = semantic_store.get("predictions", prediction.prediction_id)
    closed = pipeline.grade_prediction(
        prediction_id=prediction.prediction_id,
        outcome_sequence=21,
        outcome_channel=OutcomeChannel(lambda: predicted),
        evaluator=PredictionEvaluator(
            lambda expected, observed: PredictionGrade(
                1.0 if expected == observed else 0.0,
                evidence=("independent_outcome",),
            )
        ),
    )
    refined = rule_store.get(learned.rules[0].rule_id)
    grade_record = semantic_store.get("prediction_grades", prediction.prediction_id)
    replayed = SymbolicStore(InMemorySemanticBackend()).replay(
        semantic_store.snapshot()
    )
    summary = {
        "transition_changes": list(learned.transition.changes),
        "transformation_candidates": [item.candidate_id for item in learned.candidates],
        "rules": [item.rule_id for item in learned.rules],
        "assumptions": list(learned.rules[0].assumptions),
        "critiques": list(learned.rules[0].critiques),
        "prediction_id": prediction.prediction_id,
        "prediction_recorded_before_outcome": (
            persisted_before_grade.outcome_sequence is None
            and persisted_before_grade.grade is None
        ),
        "independent_grade": closed.grade,
        "grade_evidence": list(grade_record.evidence),
        "calibrated_probability": refined.calibrated_probability,
        "probability_source": refined.probability_source,
        "replayed_prediction": (
            replayed.get("predictions", prediction.prediction_id) == persisted_before_grade
        ),
        "replayed_grade": replayed.get("prediction_grades", prediction.prediction_id)
        is not None,
    }
    output_root = output_root.expanduser().resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    summary_path = output_root / "phase3_learning_summary.json"
    summary_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    summary["summary"] = str(summary_path)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the reproducible Phase 3 learning flow.")
    parser.add_argument(
        "--output", type=Path, default=Path("runtime") / "phase3_learning_demo"
    )
    args = parser.parse_args()
    print(json.dumps(run_demo(args.output), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
