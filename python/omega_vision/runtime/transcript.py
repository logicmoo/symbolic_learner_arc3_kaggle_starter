from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any, Iterable


def _canonical(event: Any) -> str:
    return json.dumps(event, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


@dataclass(frozen=True)
class TranscriptComparison:
    expected_events: int
    actual_events: int
    exact_matches: int
    ordered_prefix_matches: int
    event_recall: float
    exact: bool


class TranscriptScorer:
    """Compare structured transcripts without confusing order with membership."""

    def compare(
        self, expected: Iterable[Any], actual: Iterable[Any]
    ) -> TranscriptComparison:
        expected_values = tuple(_canonical(item) for item in expected)
        actual_values = tuple(_canonical(item) for item in actual)
        remaining = list(actual_values)
        matches = 0
        for item in expected_values:
            if item in remaining:
                matches += 1
                remaining.remove(item)
        prefix = 0
        for expected_item, actual_item in zip(expected_values, actual_values):
            if expected_item != actual_item:
                break
            prefix += 1
        return TranscriptComparison(
            expected_events=len(expected_values),
            actual_events=len(actual_values),
            exact_matches=matches,
            ordered_prefix_matches=prefix,
            event_recall=matches / len(expected_values) if expected_values else 1.0,
            exact=expected_values == actual_values,
        )
