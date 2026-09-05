# `worldworkbench`

> [← Project README](../../README.md)

Domain-neutral world analysis, learning, goal reasoning, and simulation.

## Classes

### `class DemonstrationStep`

A before/action/after example observed from a human demonstrator.

Fields:
- `step_id: str`
- `before_observation: str`
- `intervention: Intervention`
- `after_observation: str`
- `metadata: Mapping[str, Any]`


### `class Goal`

Fields:
- `goal_id: str`
- `description: str`
- `criteria: Mapping[str, Any]`
- `priority: float`
- `source: str`


### `class GoalProvider(Protocol)`

Base class for protocol classes.

- `__init__(self, *args, **kwargs)`
- `goals(self, state: 'WorldAnalysisState', model: 'WorldModel') -> 'Sequence[Goal]'`

### `class HumanDemonstrationObserver`

Collect human play as learning examples without choosing actions itself.

- `__init__(self, *, analyzers: 'Sequence[ObservationAnalyzer]' = (), state: 'WorldAnalysisState | None' = None) -> 'None'`
- `begin(self, observation: 'Observation') -> 'SiloRecord'` — Record and objectify the first observation of an episode.
- `observe_human_step(self, intervention: 'Intervention', resulting_observation: 'Observation', *, step_id: 'str | None' = None) -> 'DemonstrationStep'` — Record a human-selected action and the observation it produced.

### `class Intervention`

An action observed in or applied to an external world.

Fields:
- `intervention_id: str`
- `actor: str`
- `action: str`
- `parameters: Mapping[str, Any]`
- `observed_at: str`


### `class Observation`

Fields:
- `observation_id: str`
- `payload: Any`
- `source: str`
- `representation_type: str`
- `observed_at: str`
- `metadata: Mapping[str, Any]`


### `class ObservationAnalyzer(Protocol)`

Base class for protocol classes.

- `__init__(self, *args, **kwargs)`
- `analyze(self, observation: 'Observation', state: 'WorldAnalysisState') -> 'Iterable[SiloRecord]'`

### `class ProducerRef`

Fields:
- `operation: str`
- `implementation: str`
- `run_id: str | None`


### `class SiloRecord`

One immutable version of a named, typed information silo.

Fields:
- `silo_id: str`
- `version: int`
- `semantic_type: str`
- `representation_type: str`
- `value: Any`
- `subject: str | None`
- `status: SiloStatus`
- `confidence: float`
- `produced_by: ProducerRef | None`
- `derived_from: tuple[str, ...]`
- `metadata: Mapping[str, Any]`
- `created_at: str`


### `class SiloStatus(str, Enum)`

str(object='') -> str str(bytes_or_buffer[, encoding[, errors]]) -> str

Values: `OBSERVED`, `GENERATED`, `HYPOTHETICAL`, `VALIDATED`, `REJECTED`

### `class SimulationPolicy(Protocol)`

Base class for protocol classes.

- `__init__(self, *args, **kwargs)`
- `select(self, state: 'WorldAnalysisState', model: 'WorldModel', goals: 'Sequence[Goal]') -> 'Iterable[SimulationRequest]'`

### `class SimulationRequest`

Fields:
- `simulation_id: str`
- `world_model_id: str`
- `goal_ids: tuple[str, ...]`
- `intervention: Mapping[str, Any]`
- `horizon: int`
- `assumptions: tuple[str, ...]`


### `class SimulationResult`

Fields:
- `simulation_id: str`
- `predicted_state: Mapping[str, Any]`
- `goal_scores: Mapping[str, float]`
- `evidence: tuple[str, ...]`
- `confidence: float`


### `class Simulator(Protocol)`

Base class for protocol classes.

- `__init__(self, *args, **kwargs)`
- `simulate(self, request: 'SimulationRequest', model: 'WorldModel') -> 'SimulationResult'`

### `class WorldAnalysisState`

Append-only analysis state shared by workbench processing resources.

- `__init__(self, analysis_id: 'str | None' = None) -> 'None'`
- `get(self, reference: 'str') -> 'SiloRecord'`
- `history(self, silo_id: 'str') -> 'tuple[SiloRecord, ...]'`
- `latest(self, silo_id: 'str') -> 'SiloRecord'`
- `latest_silos(self) -> 'Mapping[str, SiloRecord]'`
- `put(self, silo_id: 'str', *, semantic_type: 'str', representation_type: 'str', value: 'Any', subject: 'str | None' = None, status: 'SiloStatus' = <SiloStatus.GENERATED: 'generated'>, confidence: 'float' = 1.0, produced_by: 'ProducerRef | None' = None, derived_from: 'Iterable[str]' = (), metadata: 'Mapping[str, Any] | None' = None) -> 'SiloRecord'`
- `record_demonstration_step(self, step: 'DemonstrationStep', *, producer: 'ProducerRef | None' = None) -> 'SiloRecord'`
- `record_observation(self, observation: 'Observation', *, producer: 'ProducerRef | None' = None) -> 'SiloRecord'`
- `record_simulation(self, request: 'SimulationRequest', result: 'SimulationResult', *, derived_from: 'Iterable[str]' = (), producer: 'ProducerRef | None' = None) -> 'SiloRecord'`
- `set_goals(self, goals: 'Sequence[Goal]', *, derived_from: 'Iterable[str]' = (), producer: 'ProducerRef | None' = None) -> 'SiloRecord'`
- `set_world_model(self, model: 'WorldModel', *, derived_from: 'Iterable[str]' = (), producer: 'ProducerRef | None' = None) -> 'SiloRecord'`

### `class WorldLearningWorkbench`

Coordinates analysis, world learning, goals, and selected simulation.

- `__init__(self, *, learner: 'WorldModelLearner', goal_provider: 'GoalProvider', simulation_policy: 'SimulationPolicy', simulator: 'Simulator', analyzers: 'Sequence[ObservationAnalyzer]' = (), state: 'WorldAnalysisState | None' = None) -> 'None'`
- `process(self, observation: 'Observation') -> 'tuple[SimulationResult, ...]'`

### `class WorldModel`

Fields:
- `model_id: str`
- `revision: int`
- `state: Mapping[str, Any]`
- `entities: tuple[Any, ...]`
- `dynamics: tuple[Any, ...]`
- `evidence: tuple[str, ...]`
- `confidence: float`


### `class WorldModelLearner(Protocol)`

Base class for protocol classes.

- `__init__(self, *args, **kwargs)`
- `update(self, observation: 'Observation', state: 'WorldAnalysisState') -> 'WorldModel'`
