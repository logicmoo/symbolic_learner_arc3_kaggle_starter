from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from omega_vision.core.models import RecognitionAccount


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


@dataclass(frozen=True)
class CalibrationPoint:
    upper_confidence: float
    probability: float
    sample_count: int


@dataclass(frozen=True)
class RecognitionCalibrationPolicy:
    """Serializable monotone mapping learned from authoritative outcomes."""

    scope: str
    sample_count: int
    points: tuple[CalibrationPoint, ...]
    method: str = "isotonic_pav"

    def __post_init__(self) -> None:
        if self.sample_count < 2 or not self.points:
            raise ValueError("calibration policy requires labeled samples and points")
        thresholds = tuple(item.upper_confidence for item in self.points)
        probabilities = tuple(item.probability for item in self.points)
        if any(not 0.0 <= item <= 1.0 for item in (*thresholds, *probabilities)):
            raise ValueError("calibration thresholds and probabilities must be in [0, 1]")
        if thresholds != tuple(sorted(set(thresholds))):
            raise ValueError("calibration thresholds must be strictly increasing")
        if probabilities != tuple(sorted(probabilities)):
            raise ValueError("calibration probabilities must be monotone")
        if sum(item.sample_count for item in self.points) != self.sample_count:
            raise ValueError("calibration point counts must equal the sample count")

    def calibrate(self, confidence: float) -> float:
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("confidence must be in [0, 1]")
        for point in self.points:
            if confidence <= point.upper_confidence:
                return point.probability
        return self.points[-1].probability

    def to_dict(self) -> dict[str, Any]:
        return {
            "scope": self.scope,
            "sample_count": self.sample_count,
            "method": self.method,
            "points": [
                {
                    "upper_confidence": item.upper_confidence,
                    "probability": item.probability,
                    "sample_count": item.sample_count,
                }
                for item in self.points
            ],
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "RecognitionCalibrationPolicy":
        return cls(
            scope=str(value["scope"]),
            sample_count=int(value["sample_count"]),
            method=str(value.get("method", "isotonic_pav")),
            points=tuple(
                CalibrationPoint(
                    upper_confidence=float(item["upper_confidence"]),
                    probability=float(item["probability"]),
                    sample_count=int(item["sample_count"]),
                )
                for item in value.get("points") or ()
            ),
        )


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

    def fit(
        self,
        accounts: Iterable[RecognitionAccount],
        *,
        scope: str,
    ) -> RecognitionCalibrationPolicy:
        """Fit a deterministic pool-adjacent-violators isotonic policy."""

        samples = sorted(
            (
                float(account.decision_confidence),
                float(bool(account.decision_outcome)),
            )
            for account in accounts
            if account.decision_confidence is not None
            and account.decision_outcome is not None
        )
        if len(samples) < 2:
            raise ValueError("calibration requires at least two labeled outcomes")
        if any(not 0.0 <= confidence <= 1.0 for confidence, _outcome in samples):
            raise ValueError("decision confidence must be in [0, 1]")
        grouped: list[list[float]] = []
        for confidence, outcome in samples:
            if grouped and grouped[-1][0] == confidence:
                grouped[-1][1] += outcome
                grouped[-1][2] += 1.0
            else:
                grouped.append([confidence, outcome, 1.0])
        blocks: list[list[float]] = []
        for confidence, outcome_sum, count in grouped:
            blocks.append([confidence, confidence, outcome_sum, count])
            while len(blocks) >= 2:
                previous, current = blocks[-2:]
                if previous[2] / previous[3] <= current[2] / current[3]:
                    break
                blocks[-2:] = [[
                    previous[0],
                    current[1],
                    previous[2] + current[2],
                    previous[3] + current[3],
                ]]
        points = tuple(
            CalibrationPoint(
                upper_confidence=(
                    1.0
                    if index == len(blocks) - 1
                    else (upper + blocks[index + 1][0]) / 2.0
                ),
                probability=outcome_sum / count,
                sample_count=int(count),
            )
            for index, (_lower, upper, outcome_sum, count) in enumerate(blocks)
        )
        return RecognitionCalibrationPolicy(scope, len(samples), points)

    def calibrated_report(
        self,
        accounts: Iterable[RecognitionAccount],
        policy: RecognitionCalibrationPolicy,
        *,
        bin_count: int = 10,
    ) -> RecognitionCalibrationReport:
        calibrated = tuple(
            RecognitionAccount(
                **{
                    **account.__dict__,
                    "decision_confidence": policy.calibrate(
                        float(account.decision_confidence)
                    ),
                }
            )
            for account in accounts
            if account.decision_confidence is not None
            and account.decision_outcome is not None
        )
        return self.report(
            calibrated,
            scope=f"{policy.scope}:calibrated",
            bin_count=bin_count,
        )
