# `omega_vision.transcript`

> [← Project README](../../README.md)

## Classes

### `class TranscriptComparison`

Fields:
- `expected_events: int`
- `actual_events: int`
- `exact_matches: int`
- `ordered_prefix_matches: int`
- `event_recall: float`
- `exact: bool`


### `class TranscriptScorer`

Compare structured transcripts without confusing order with membership.

- `compare(self, expected: 'Iterable[Any]', actual: 'Iterable[Any]') -> 'TranscriptComparison'`
