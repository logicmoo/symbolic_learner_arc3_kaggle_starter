# `omega_vision.integration`

> [← Project README](../../README.md)

## Classes

### `class GameObjectLearnerPayload`

Fields:
- `state_id: str`
- `objects: tuple[Mapping[str, Any], ...]`
- `correspondences: tuple[Mapping[str, Any], ...]`
- `transitions: tuple[Mapping[str, Any], ...]`
- `provenance: tuple[str, ...]`
- `observation_id: str | None`
- `encounter_ids: tuple[str, ...]`
- `identity_ids: tuple[str, ...]`
- `artifacts: tuple[Mapping[str, Any], ...]`
- `evidence: tuple[Mapping[str, Any], ...]`
- `schema_version: str`

- `to_dict(self) -> 'dict[str, Any]'`

### `class GameObjectLearnerPlugin(ABC)`

Phase 3 boundary; implementations consume normalized Phase 2 results.

- `consume(self, payload: 'GameObjectLearnerPayload') -> 'NormalizedResult'` — Backward-compatible alias for earlier single-state plugins.
- `consume_state(self, payload: 'GameObjectLearnerPayload') -> 'NormalizedResult'`
- `consume_transition(self, before: 'GameObjectLearnerPayload', action_or_event: 'Any', after: 'GameObjectLearnerPayload') -> 'NormalizedResult'`

### `class GameObjectLearnerResult`

Fields:
- `state_id: str`
- `learning_step: LearningStepResult | None`
- `prediction_id: str | None`
- `recommendation: Any`


### `class GameObjectLearnerSchema`

Small stable contract; providers may add metadata without changing it.


### `class IntegrationError(ValueError)`

Inappropriate argument value (of correct type).


### `class IntegrationValidator`

- `__init__(self, schema: 'GameObjectLearnerSchema | None' = None, *, registry_identity_ids: 'set[str] | frozenset[str] | None' = None, provenance_source_ids: 'set[str] | frozenset[str] | None' = None) -> 'None'`
- `validate(self, payload: 'GameObjectLearnerPayload') -> 'GameObjectLearnerPayload'`

### `class Phase2LearnerPayloadBuilder`

Build the frozen learner handoff exclusively from exact Phase 2 records.

- `__init__(self, store: 'SymbolicStore') -> 'None'`
- `for_observation(self, observation_id: 'str') -> 'GameObjectLearnerPayload'`

### `class PipelineGameObjectLearnerPlugin(GameObjectLearnerPlugin)`

Runnable integration of validated payloads with GameLearningPipeline.

- `__init__(self, pipeline: 'GameLearningPipeline', *, mode: 'ExecutionMode' = <ExecutionMode.PYTHON: 'PYTHON'>, validator: 'IntegrationValidator | None' = None) -> 'None'`
- `consume(self, payload: 'GameObjectLearnerPayload') -> 'NormalizedResult'` — Backward-compatible alias for earlier single-state plugins.
- `consume_state(self, payload: 'GameObjectLearnerPayload') -> 'NormalizedResult'`
- `consume_transition(self, before: 'GameObjectLearnerPayload', action_or_event: 'Any', after: 'GameObjectLearnerPayload') -> 'NormalizedResult'`

## Functions

### `phase2_rule_executor(store: 'RuleStore', action_or_event: 'Any') -> 'RuleExecutor'`

Apply an induced object transformation relative to a new object state.

### `phase2_rule_inducer() -> 'RuleInducer'`

Induce inspectable rival rules without treating one observation as proof.

### `phase2_rule_ranker() -> 'RuleRanker'`

Rank by verified history first, then evidence and explicit simplicity.

### `phase2_transformation_learner() -> 'TransformationLearner'`

Convert direct changes into evidence-linked competing interpretations.

### `phase2_transition_analyzer() -> 'TransitionAnalyzer'`

Analyze one real handoff using the direct Phase 2 change records.
