from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .models import RecognitionAccount


@dataclass(frozen=True)
class ReliabilityBin:
    lower: float
    upper: float
    count: int
    mean_confidence: float
    acceptance_rate: float
    brier_score: float


@dataclass(frozen=True)
class RecognitionCalibrationReport:
    scope: str
    sample_count: int
    brier_score: float | None
    bins: tuple[ReliabilityBin, ...]


class RecognitionCalibrator:
    """Measure pre-decision confidence against later authority outcomes."""

    def report(
        self,
        accounts: Iterable[RecognitionAccount],
        *,
        scope: str = "all",
        bin_count: int = 10,
    ) -> RecognitionCalibrationReport:
        if bin_count < 1:
            raise ValueError("bin_count must be positive")
        samples = tuple(
            (float(account.decision_confidence), bool(account.decision_outcome))
            for account in accounts
            if account.decision_confidence is not None
            and account.decision_outcome is not None
        )
        for confidence, _outcome in samples:
            if not 0.0 <= confidence <= 1.0:
                raise ValueError("decision confidence must be in [0, 1]")
        bins = []
        for index in range(bin_count):
            lower = index / bin_count
            upper = (index + 1) / bin_count
            selected = tuple(
                sample
                for sample in samples
                if lower <= sample[0] <= upper
                and (index == bin_count - 1 or sample[0] < upper)
            )
            if not selected:
                continue
            errors = tuple(
                (confidence - float(outcome)) ** 2
                for confidence, outcome in selected
            )
            bins.append(
                ReliabilityBin(
                    lower=lower,
                    upper=upper,
                    count=len(selected),
                    mean_confidence=sum(item[0] for item in selected) / len(selected),
                    acceptance_rate=sum(float(item[1]) for item in selected)
                    / len(selected),
                    brier_score=sum(errors) / len(errors),
                )
            )
        errors = tuple(
            (confidence - float(outcome)) ** 2 for confidence, outcome in samples
        )
        return RecognitionCalibrationReport(
            scope=scope,
            sample_count=len(samples),
            brier_score=(sum(errors) / len(errors) if errors else None),
            bins=tuple(bins),
        )
