# `omega_vision.learning`

> [← Project README](../../README.md)

## Classes

### `class GameLearningPipeline`

Connected Phase 3 flow; algorithms remain replaceable providers.

- `__init__(self, transition_analyzer: 'TransitionAnalyzer', transformation_learner: 'TransformationLearner', rule_inducer: 'RuleInducer', rule_ranker: 'RuleRanker', rule_store: 'RuleStore', prediction_ledger: 'PredictionLedger', semantic_store: 'Any | None' = None) -> 'None'`
- `grade_prediction(self, *, prediction_id: 'str', outcome_sequence: 'int', outcome_channel: 'OutcomeChannel', evaluator: 'PredictionEvaluator') -> 'PredictionRecord'`
- `learn_transition(self, before: 'Any', action_or_event: 'Any', after: 'Any') -> 'LearningStepResult'`
- `predict(self, *, prediction_id: 'str', rule_id: 'str', source_state_id: 'str', state: 'Any', created_sequence: 'int', executor: 'RuleExecutor') -> 'tuple[Any, PredictionRecord]'`
- `recommend_action(self, *, source_state_id: 'str', attempted_action: 'Any', created_sequence: 'int', prediction_id: 'str | None' = None) -> 'ActionRecommendation | None'` — Rank all learned actions independently of the action being attempted.

### `class LearningStepResult`

Fields:
- `transition: TransitionRecord`
- `candidates: tuple[TransformationCandidate, ...]`
- `rules: tuple[TransitionRule, ...]`


### `class OutcomeChannel`

Independent observation channel used to grade a prior prediction.

- `__init__(self, read: 'Callable[[], Any]') -> 'None'`
- `read(self) -> 'Any'`

### `class PredictionEvaluator`

- `__init__(self, compare: 'Callable[[Any, Any], PredictionGrade]') -> 'None'`
- `evaluate(self, predicted: 'Any', observed: 'Any') -> 'PredictionGrade'`

### `class PredictionGrade`

Fields:
- `score: float | None`
- `evidence: tuple[Any, ...]`
- `status: PredictionGradeStatus | None`


### `class PredictionGradeStatus(str, Enum)`

str(object='') -> str str(bytes_or_buffer[, encoding[, errors]]) -> str

Values: `SUCCESS`, `FAILURE`, `PARTIAL_MATCH`, `CONTRADICTION`, `UNGRADABLE`

### `class RuleEvidence`

Fields:
- `rule_id: str`
- `confirming: tuple[Any, ...]`
- `refuting: tuple[Any, ...]`


### `class RuleExecutor`

Applies stored rules through caller-supplied domain semantics.

- `__init__(self, store: 'RuleStore', checker: 'Callable[[TransitionRule, Any], bool]', executor: 'Callable[[TransitionRule, Any], Any]') -> 'None'`
- `applicable(self, rule_id: 'str', state: 'Any') -> 'bool'`
- `apply(self, rule_id: 'str', state: 'Any') -> 'Any'`

### `class RuleInducer`

Converts transformation candidates into normalized TransitionRule records.

- `__init__(self, induce: 'Callable[[Sequence[TransformationCandidate]], Iterable[TransitionRule]]') -> 'None'`
- `induce(self, candidates: 'Sequence[TransformationCandidate]') -> 'tuple[TransitionRule, ...]'`

### `class RuleRanker`

- `__init__(self, score: 'Callable[[TransitionRule], float]') -> 'None'`
- `rank(self, rules: 'Iterable[TransitionRule]') -> 'tuple[TransitionRule, ...]'`

### `class RuleRivalSet`

Fields:
- `rules: tuple[TransitionRule, ...]`


### `class TransformationCandidate`

Fields:
- `candidate_id: str`
- `transformation: Any`
- `evidence: tuple[Any, ...]`
- `score: float`
- `source_state_id: str | None`
- `target_state_id: str | None`
- `action_or_event: Any`
- `assumptions: tuple[str, ...]`
- `critiques: tuple[str, ...]`
- `provenance: tuple[str, ...]`


### `class TransformationLearner`

Delegates candidate generation without fixing the learning algorithm.

- `__init__(self, learn: 'Callable[[TransitionRecord], Iterable[TransformationCandidate]]') -> 'None'`
- `learn(self, transition: 'TransitionRecord') -> 'tuple[TransformationCandidate, ...]'`

### `class TransitionAnalyzer`

Facade over a deterministic, Prolog, or GPT-backed transition analyzer.

- `__init__(self, analyze: 'Callable[[Any, Any, Any], TransitionRecord]') -> 'None'`
- `analyze(self, before: 'Any', action_or_event: 'Any', after: 'Any') -> 'TransitionRecord'`

### `class TransitionRecord`

Fields:
- `before_state_id: str`
- `action_or_event: Any`
- `after_state_id: str`
- `changes: tuple[Any, ...]`
- `provenance: tuple[str, ...]`
