from __future__ import annotations

from dataclasses import replace
from typing import Any

from .models import PredictionRecord


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
