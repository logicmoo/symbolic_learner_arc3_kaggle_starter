"""SoW Appendix A.2 ``core/evaluation.py`` / §13, A.6 metrics + A.7 acceptance.

Prediction grading (SoW §10) is done by
:class:`object_memory.learning.PredictionEvaluator` reading the independent
:class:`object_memory.learning.OutcomeChannel`; calibration by
:class:`object_memory.calibration.RecognitionCalibrator`; the acceptance summary by
:class:`object_memory.acceptance.AcceptanceReport`; and the runnable benchmarks by
the ``*BenchmarkRunner`` / ``ProviderAblationRunner`` classes.

``GridMetrics`` / ``RasterMetrics`` are the SoW A.6 registry metric names; they had
no prior home, so compact deterministic implementations live here. They score the
strict grid-baseline and raster-rung criteria of SoW §13 from
``(assigned_handle, gold_handle)`` pairs — mechanism-neutral, results only.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Iterable, Sequence

from object_memory.acceptance import AcceptanceReport, build_acceptance_report
from object_memory.benchmark import (
    PerceptionBenchmarkResult,
    PerceptionBenchmarkRunner,
    ProviderAblationRunner,
)
from object_memory.calibration import RecognitionCalibrator
from object_memory.learning import OutcomeChannel, PredictionEvaluator, PredictionGrade, PredictionGradeStatus
from object_memory.recognition_benchmark import RecognitionBenchmarkResult, RecognitionBenchmarkRunner

Pair = tuple[str | None, str]


class GridMetrics:
    """Strict grid-baseline scores (SoW §13): recognition, uniqueness, determinism."""

    @staticmethod
    def recognition_rate(pairs: Iterable[Pair]) -> float:
        pairs = list(pairs)
        if not pairs:
            return 0.0
        hits = sum(1 for assigned, gold in pairs if assigned is not None and assigned == gold)
        return hits / len(pairs)

    @staticmethod
    def false_merge_rate(pairs: Iterable[Pair]) -> float:
        """Fraction of observations whose handle is shared by >1 distinct gold id."""
        pairs = [(a, g) for a, g in pairs if a is not None]
        if not pairs:
            return 0.0
        golds_by_handle: dict[str, set[str]] = defaultdict(set)
        for assigned, gold in pairs:
            golds_by_handle[assigned].add(gold)
        merged = sum(1 for a, _ in pairs if len(golds_by_handle[a]) > 1)
        return merged / len(pairs)

    @staticmethod
    def false_split_rate(pairs: Iterable[Pair]) -> float:
        """Fraction of observations whose gold id is spread across >1 handle."""
        pairs = [(a, g) for a, g in pairs if a is not None]
        if not pairs:
            return 0.0
        handles_by_gold: dict[str, set[str]] = defaultdict(set)
        for assigned, gold in pairs:
            handles_by_gold[gold].add(assigned)
        split = sum(1 for _, g in pairs if len(handles_by_gold[g]) > 1)
        return split / len(pairs)

    @staticmethod
    def determinism(run_a: Sequence[str], run_b: Sequence[str]) -> bool:
        """SoW §13: identical input yields the same committed identities."""
        return tuple(run_a) == tuple(run_b)


class RasterMetrics:
    """Raster-rung floor scores (SoW §13): recognition, degradation, occlusion."""

    @staticmethod
    def recognition_rate(pairs: Iterable[Pair]) -> float:
        return GridMetrics.recognition_rate(pairs)

    @staticmethod
    def occlusion_recognition_rate(pairs: Iterable[Pair]) -> float:
        """Re-recognition under partial occlusion (SoW §13 raster rungs)."""
        return GridMetrics.recognition_rate(pairs)

    @staticmethod
    def coarse_fidelity(scores: Iterable[float]) -> float:
        """Mean regeneration fidelity to a recognizable gist (SoW §13)."""
        scores = list(scores)
        return sum(scores) / len(scores) if scores else 0.0


__all__ = [
    "PredictionEvaluator",
    "OutcomeChannel",
    "PredictionGrade",
    "PredictionGradeStatus",
    "RecognitionCalibrator",
    "AcceptanceReport",
    "build_acceptance_report",
    "PerceptionBenchmarkRunner",
    "PerceptionBenchmarkResult",
    "RecognitionBenchmarkRunner",
    "RecognitionBenchmarkResult",
    "ProviderAblationRunner",
    "GridMetrics",
    "RasterMetrics",
]
