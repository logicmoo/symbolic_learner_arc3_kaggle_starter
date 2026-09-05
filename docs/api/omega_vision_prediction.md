# `omega_vision.prediction`

> [← Project README](../../README.md)

## Classes

### `class PredictionLedger`

Append-only prediction records enforcing predict-before-check.

- `__init__(self) -> 'None'`
- `get(self, prediction_id: 'str') -> 'PredictionRecord'`
- `grade(self, prediction_id: 'str', *, outcome_sequence: 'int', outcome: 'Any', grade: 'float | None') -> 'PredictionRecord'`
- `record(self, prediction: 'PredictionRecord') -> 'PredictionRecord'`
- `records(self) -> 'tuple[PredictionRecord, ...]'`

### `class RuleStore`

Exact-identity rule registry with caller-supplied domain execution.

- `__init__(self) -> 'None'`
- `applicable(self, rule_id: 'str', state: 'Any', checker: 'Callable[[TransitionRule, Any], bool]') -> 'bool'`
- `apply(self, rule_id: 'str', state: 'Any', executor: 'Callable[[TransitionRule, Any], Any]') -> 'Any'`
- `get(self, rule_id: 'str') -> 'TransitionRule'`
- `record_prediction_grade(self, rule_id: 'str', *, prediction_id: 'str', grade: 'float', supporting_evidence_ids: 'tuple[str, ...]' = (), contradicting_evidence_ids: 'tuple[str, ...]' = ()) -> 'TransitionRule'` — Refine one rule only from an independently graded prior prediction.
- `rules(self) -> 'tuple[TransitionRule, ...]'`
- `store(self, rule: 'TransitionRule') -> 'TransitionRule'`
