from __future__ import annotations

from dataclasses import replace
from typing import Any, Callable

from .models import PredictionRecord, TransitionRule


class RuleStore:
    """Exact-identity rule registry with caller-supplied domain execution."""

    def __init__(self) -> None:
        self._rules: dict[str, TransitionRule] = {}

    def store(self, rule: TransitionRule) -> TransitionRule:
        existing = self._rules.get(rule.rule_id)
        if existing is not None and existing != rule:
            raise ValueError(f"Rule identity conflict for {rule.rule_id!r}")
        self._rules[rule.rule_id] = rule
        return rule

    def get(self, rule_id: str) -> TransitionRule:
        return self._rules[rule_id]

    def rules(self) -> tuple[TransitionRule, ...]:
        return tuple(self._rules.values())

    def applicable(
        self,
        rule_id: str,
        state: Any,
        checker: Callable[[TransitionRule, Any], bool],
    ) -> bool:
        return bool(checker(self.get(rule_id), state))

    def apply(
        self,
        rule_id: str,
        state: Any,
        executor: Callable[[TransitionRule, Any], Any],
    ) -> Any:
        return executor(self.get(rule_id), state)


class PredictionLedger:
    """Append-only prediction records enforcing predict-before-check."""

    def __init__(self) -> None:
        self._records: dict[str, PredictionRecord] = {}

    def record(self, prediction: PredictionRecord) -> PredictionRecord:
        if prediction.prediction_id in self._records:
            raise ValueError(f"Duplicate prediction id {prediction.prediction_id!r}")
        if prediction.outcome_sequence is not None:
            raise ValueError("A new prediction cannot already contain an outcome")
        self._records[prediction.prediction_id] = prediction
        return prediction

    def grade(
        self,
        prediction_id: str,
        *,
        outcome_sequence: int,
        outcome: Any,
        grade: float,
    ) -> PredictionRecord:
        prediction = self._records[prediction_id]
        if outcome_sequence <= prediction.created_sequence:
            raise ValueError("Outcome must occur after the prediction was recorded")
        if prediction.outcome_sequence is not None:
            raise ValueError(f"Prediction {prediction_id!r} is already closed")
        closed = replace(
            prediction,
            outcome_sequence=outcome_sequence,
            outcome=outcome,
            grade=float(grade),
        )
        self._records[prediction_id] = closed
        return closed

    def get(self, prediction_id: str) -> PredictionRecord:
        return self._records[prediction_id]

    def records(self) -> tuple[PredictionRecord, ...]:
        return tuple(self._records.values())
