> [← Project README](../../README.md)

# Table of Contents

* [worldworkbench.adapters.arc3](#worldworkbench.adapters.arc3)
  * [Arc3ObservationAdapter](#worldworkbench.adapters.arc3.Arc3ObservationAdapter)
    * [capture](#worldworkbench.adapters.arc3.Arc3ObservationAdapter.capture)
  * [Arc3InterventionAdapter](#worldworkbench.adapters.arc3.Arc3InterventionAdapter)
    * [apply](#worldworkbench.adapters.arc3.Arc3InterventionAdapter.apply)
    * [apply\_human\_choice](#worldworkbench.adapters.arc3.Arc3InterventionAdapter.apply_human_choice)
  * [arc3\_artifact\_metadata](#worldworkbench.adapters.arc3.arc3_artifact_metadata)
* [worldworkbench.core](#worldworkbench.core)
  * [SiloStatus](#worldworkbench.core.SiloStatus)
    * [OBSERVED](#worldworkbench.core.SiloStatus.OBSERVED)
    * [GENERATED](#worldworkbench.core.SiloStatus.GENERATED)
    * [HYPOTHETICAL](#worldworkbench.core.SiloStatus.HYPOTHETICAL)
    * [VALIDATED](#worldworkbench.core.SiloStatus.VALIDATED)
    * [REJECTED](#worldworkbe[omega_vision.md](omega_vision.md)nch.core.SiloStatus.REJECTED)
  * [ProducerRef](#worldworkbench.core.ProducerRef)
    * [operation](#worldworkbench.core.ProducerRef.operation)
    * [implementation](#worldworkbench.core.ProducerRef.implementation)
    * [run\_id](#worldworkbench.core.ProducerRef.run_id)
  * [SiloRecord](#worldworkbench.core.SiloRecord)
    * [silo\_id](#worldworkbench.core.SiloRecord.silo_id)
    * [version](#worldworkbench.core.SiloRecord.version)
    * [semantic\_type](#worldworkbench.core.SiloRecord.semantic_type)
    * [representation\_type](#worldworkbench.core.SiloRecord.representation_type)
    * [value](#worldworkbench.core.SiloRecord.value)
    * [subject](#worldworkbench.core.SiloRecord.subject)
    * [status](#worldworkbench.core.SiloRecord.status)
    * [confidence](#worldworkbench.core.SiloRecord.confidence)
    * [produced\_by](#worldworkbench.core.SiloRecord.produced_by)
    * [derived\_from](#worldworkbench.core.SiloRecord.derived_from)
    * [metadata](#worldworkbench.core.SiloRecord.metadata)
    * [created\_at](#worldworkbench.core.SiloRecord.created_at)
    * [\_\_post\_init\_\_](#worldworkbench.core.SiloRecord.__post_init__)
    * [reference](#worldworkbench.core.SiloRecord.reference)
  * [Observation](#worldworkbench.core.Observation)
    * [observation\_id](#worldworkbench.core.Observation.observation_id)
    * [payload](#worldworkbench.core.Observation.payload)
    * [source](#worldworkbench.core.Observation.source)
    * [representation\_type](#worldworkbench.core.Observation.representation_type)
    * [observed\_at](#worldworkbench.core.Observation.observed_at)
    * [metadata](#worldworkbench.core.Observation.metadata)
    * [\_\_post\_init\_\_](#worldworkbench.core.Observation.__post_init__)
  * [Intervention](#worldworkbench.core.Intervention)
    * [intervention\_id](#worldworkbench.core.Intervention.intervention_id)
    * [actor](#worldworkbench.core.Intervention.actor)
    * [action](#worldworkbench.core.Intervention.action)
    * [parameters](#worldworkbench.core.Intervention.parameters)
    * [observed\_at](#worldworkbench.core.Intervention.observed_at)
    * [\_\_post\_init\_\_](#worldworkbench.core.Intervention.__post_init__)
  * [DemonstrationStep](#worldworkbench.core.DemonstrationStep)
    * [step\_id](#worldworkbench.core.DemonstrationStep.step_id)
    * [before\_observation](#worldworkbench.core.DemonstrationStep.before_observation)
    * [intervention](#worldworkbench.core.DemonstrationStep.intervention)
    * [after\_observation](#worldworkbench.core.DemonstrationStep.after_observation)
    * [metadata](#worldworkbench.core.DemonstrationStep.metadata)
    * [\_\_post\_init\_\_](#worldworkbench.core.DemonstrationStep.__post_init__)
  * [Goal](#worldworkbench.core.Goal)
    * [goal\_id](#worldworkbench.core.Goal.goal_id)
    * [description](#worldworkbench.core.Goal.description)
    * [criteria](#worldworkbench.core.Goal.criteria)
    * [priority](#worldworkbench.core.Goal.priority)
    * [source](#worldworkbench.core.Goal.source)
    * [\_\_post\_init\_\_](#worldworkbench.core.Goal.__post_init__)
  * [WorldModel](#worldworkbench.core.WorldModel)
    * [model\_id](#worldworkbench.core.WorldModel.model_id)
    * [revision](#worldworkbench.core.WorldModel.revision)
    * [state](#worldworkbench.core.WorldModel.state)
    * [entities](#worldworkbench.core.WorldModel.entities)
    * [dynamics](#worldworkbench.core.WorldModel.dynamics)
    * [evidence](#worldworkbench.core.WorldModel.evidence)
    * [confidence](#worldworkbench.core.WorldModel.confidence)
    * [\_\_post\_init\_\_](#worldworkbench.core.WorldModel.__post_init__)
  * [SimulationRequest](#worldworkbench.core.SimulationRequest)
    * [simulation\_id](#worldworkbench.core.SimulationRequest.simulation_id)
    * [world\_model\_id](#worldworkbench.core.SimulationRequest.world_model_id)
    * [goal\_ids](#worldworkbench.core.SimulationRequest.goal_ids)
    * [intervention](#worldworkbench.core.SimulationRequest.intervention)
    * [horizon](#worldworkbench.core.SimulationRequest.horizon)
    * [assumptions](#worldworkbench.core.SimulationRequest.assumptions)
    * [\_\_post\_init\_\_](#worldworkbench.core.SimulationRequest.__post_init__)
  * [SimulationResult](#worldworkbench.core.SimulationResult)
    * [simulation\_id](#worldworkbench.core.SimulationResult.simulation_id)
    * [predicted\_state](#worldworkbench.core.SimulationResult.predicted_state)
    * [goal\_scores](#worldworkbench.core.SimulationResult.goal_scores)
    * [evidence](#worldworkbench.core.SimulationResult.evidence)
    * [confidence](#worldworkbench.core.SimulationResult.confidence)
    * [\_\_post\_init\_\_](#worldworkbench.core.SimulationResult.__post_init__)
  * [WorldAnalysisState](#worldworkbench.core.WorldAnalysisState)
    * [\_\_init\_\_](#worldworkbench.core.WorldAnalysisState.__init__)
    * [put](#worldworkbench.core.WorldAnalysisState.put)
    * [latest](#worldworkbench.core.WorldAnalysisState.latest)
    * [get](#worldworkbench.core.WorldAnalysisState.get)
    * [history](#worldworkbench.core.WorldAnalysisState.history)
    * [latest\_silos](#worldworkbench.core.WorldAnalysisState.latest_silos)
    * [record\_observation](#worldworkbench.core.WorldAnalysisState.record_observation)
    * [set\_world\_model](#worldworkbench.core.WorldAnalysisState.set_world_model)
    * [set\_goals](#worldworkbench.core.WorldAnalysisState.set_goals)
    * [record\_simulation](#worldworkbench.core.WorldAnalysisState.record_simulation)
    * [record\_demonstration\_step](#worldworkbench.core.WorldAnalysisState.record_demonstration_step)
  * [ObservationAnalyzer](#worldworkbench.core.ObservationAnalyzer)
    * [analyze](#worldworkbench.core.ObservationAnalyzer.analyze)
  * [WorldModelLearner](#worldworkbench.core.WorldModelLearner)
    * [update](#worldworkbench.core.WorldModelLearner.update)
  * [GoalProvider](#worldworkbench.core.GoalProvider)
    * [goals](#worldworkbench.core.GoalProvider.goals)
  * [SimulationPolicy](#worldworkbench.core.SimulationPolicy)
    * [select](#worldworkbench.core.SimulationPolicy.select)
  * [Simulator](#worldworkbench.core.Simulator)
    * [simulate](#worldworkbench.core.Simulator.simulate)
  * [WorldLearningWorkbench](#worldworkbench.core.WorldLearningWorkbench)
    * [\_\_init\_\_](#worldworkbench.core.WorldLearningWorkbench.__init__)
    * [process](#worldworkbench.core.WorldLearningWorkbench.process)
  * [HumanDemonstrationObserver](#worldworkbench.core.HumanDemonstrationObserver)
    * [\_\_init\_\_](#worldworkbench.core.HumanDemonstrationObserver.__init__)
    * [begin](#worldworkbench.core.HumanDemonstrationObserver.begin)
    * [observe\_human\_step](#worldworkbench.core.HumanDemonstrationObserver.observe_human_step)

<a id="worldworkbench.adapters.arc3"></a>

# worldworkbench.adapters.arc3

<a id="worldworkbench.adapters.arc3.Arc3ObservationAdapter"></a>

## Arc3ObservationAdapter Objects

```python
class Arc3ObservationAdapter()
```

Translate an Arc3Runner state into a domain-neutral observation.

<a id="worldworkbench.adapters.arc3.Arc3ObservationAdapter.capture"></a>

#### capture

```python
def capture(runner: Any, *, observation_id: str | None = None) -> Observation
```

<a id="worldworkbench.adapters.arc3.Arc3InterventionAdapter"></a>

## Arc3InterventionAdapter Objects

```python
class Arc3InterventionAdapter()
```

Apply a selected workbench intervention through an Arc3Runner.

<a id="worldworkbench.adapters.arc3.Arc3InterventionAdapter.apply"></a>

#### apply

```python
def apply(runner: Any, request: SimulationRequest) -> Any
```

<a id="worldworkbench.adapters.arc3.Arc3InterventionAdapter.apply_human_choice"></a>

#### apply\_human\_choice

```python
def apply_human_choice(
        runner: Any,
        action: Any,
        *,
        data: Mapping[str, Any] | None = None,
        intervention_id: str | None = None
) -> tuple[Intervention, Observation]
```

Apply a human-selected ARC3 action and capture its resulting state.

<a id="worldworkbench.adapters.arc3.arc3_artifact_metadata"></a>

#### arc3\_artifact\_metadata

```python
def arc3_artifact_metadata(runner: Any) -> dict[str, str | None]
```

Return portable links to the current ARC3 evidence artifacts.

<a id="worldworkbench.core"></a>

# worldworkbench.core

<a id="worldworkbench.core.SiloStatus"></a>

## SiloStatus Objects

```python
class SiloStatus(str, Enum)
```

<a id="worldworkbench.core.SiloStatus.OBSERVED"></a>

#### OBSERVED

<a id="worldworkbench.core.SiloStatus.GENERATED"></a>

#### GENERATED

<a id="worldworkbench.core.SiloStatus.HYPOTHETICAL"></a>

#### HYPOTHETICAL

<a id="worldworkbench.core.SiloStatus.VALIDATED"></a>

#### VALIDATED

<a id="worldworkbench.core.SiloStatus.REJECTED"></a>

#### REJECTED

<a id="worldworkbench.core.ProducerRef"></a>

## ProducerRef Objects

```python
@dataclass(frozen=True)
class ProducerRef()
```

<a id="worldworkbench.core.ProducerRef.operation"></a>

#### operation: `str`

<a id="worldworkbench.core.ProducerRef.implementation"></a>

#### implementation: `str`

<a id="worldworkbench.core.ProducerRef.run_id"></a>

#### run\_id: `str | None`

<a id="worldworkbench.core.SiloRecord"></a>

## SiloRecord Objects

```python
@dataclass(frozen=True)
class SiloRecord()
```

One immutable version of a named, typed information silo.

<a id="worldworkbench.core.SiloRecord.silo_id"></a>

#### silo\_id: `str`

<a id="worldworkbench.core.SiloRecord.version"></a>

#### version: `int`

<a id="worldworkbench.core.SiloRecord.semantic_type"></a>

#### semantic\_type: `str`

<a id="worldworkbench.core.SiloRecord.representation_type"></a>

#### representation\_type: `str`

<a id="worldworkbench.core.SiloRecord.value"></a>

#### value: `Any`

<a id="worldworkbench.core.SiloRecord.subject"></a>

#### subject: `str | None`

<a id="worldworkbench.core.SiloRecord.status"></a>

#### status: `SiloStatus`

<a id="worldworkbench.core.SiloRecord.confidence"></a>

#### confidence: `float`

<a id="worldworkbench.core.SiloRecord.produced_by"></a>

#### produced\_by: `ProducerRef | None`

<a id="worldworkbench.core.SiloRecord.derived_from"></a>

#### derived\_from: `tuple[str, ...]`

<a id="worldworkbench.core.SiloRecord.metadata"></a>

#### metadata: `Mapping[str, Any]`

<a id="worldworkbench.core.SiloRecord.created_at"></a>

#### created\_at: `str`

<a id="worldworkbench.core.SiloRecord.__post_init__"></a>

#### \_\_post\_init\_\_

```python
def __post_init__() -> None
```

<a id="worldworkbench.core.SiloRecord.reference"></a>

#### reference

```python
@property
def reference() -> str
```

<a id="worldworkbench.core.Observation"></a>

## Observation Objects

```python
@dataclass(frozen=True)
class Observation()
```

<a id="worldworkbench.core.Observation.observation_id"></a>

#### observation\_id: `str`

<a id="worldworkbench.core.Observation.payload"></a>

#### payload: `Any`

<a id="worldworkbench.core.Observation.source"></a>

#### source: `str`

<a id="worldworkbench.core.Observation.representation_type"></a>

#### representation\_type: `str`

<a id="worldworkbench.core.Observation.observed_at"></a>

#### observed\_at: `str`

<a id="worldworkbench.core.Observation.metadata"></a>

#### metadata: `Mapping[str, Any]`

<a id="worldworkbench.core.Observation.__post_init__"></a>

#### \_\_post\_init\_\_

```python
def __post_init__() -> None
```

<a id="worldworkbench.core.Intervention"></a>

## Intervention Objects

```python
@dataclass(frozen=True)
class Intervention()
```

An action observed in or applied to an external world.

<a id="worldworkbench.core.Intervention.intervention_id"></a>

#### intervention\_id: `str`

<a id="worldworkbench.core.Intervention.actor"></a>

#### actor: `str`

<a id="worldworkbench.core.Intervention.action"></a>

#### action: `str`

<a id="worldworkbench.core.Intervention.parameters"></a>

#### parameters: `Mapping[str, Any]`

<a id="worldworkbench.core.Intervention.observed_at"></a>

#### observed\_at: `str`

<a id="worldworkbench.core.Intervention.__post_init__"></a>

#### \_\_post\_init\_\_

```python
def __post_init__() -> None
```

<a id="worldworkbench.core.DemonstrationStep"></a>

## DemonstrationStep Objects

```python
@dataclass(frozen=True)
class DemonstrationStep()
```

A before/action/after example observed from a human demonstrator.

<a id="worldworkbench.core.DemonstrationStep.step_id"></a>

#### step\_id: `str`

<a id="worldworkbench.core.DemonstrationStep.before_observation"></a>

#### before\_observation: `str`

<a id="worldworkbench.core.DemonstrationStep.intervention"></a>

#### intervention: `Intervention`

<a id="worldworkbench.core.DemonstrationStep.after_observation"></a>

#### after\_observation: `str`

<a id="worldworkbench.core.DemonstrationStep.metadata"></a>

#### metadata: `Mapping[str, Any]`

<a id="worldworkbench.core.DemonstrationStep.__post_init__"></a>

#### \_\_post\_init\_\_

```python
def __post_init__() -> None
```

<a id="worldworkbench.core.Goal"></a>

## Goal Objects

```python
@dataclass(frozen=True)
class Goal()
```

<a id="worldworkbench.core.Goal.goal_id"></a>

#### goal\_id: `str`

<a id="worldworkbench.core.Goal.description"></a>

#### description: `str`

<a id="worldworkbench.core.Goal.criteria"></a>

#### criteria: `Mapping[str, Any]`

<a id="worldworkbench.core.Goal.priority"></a>

#### priority: `float`

<a id="worldworkbench.core.Goal.source"></a>

#### source: `str`

<a id="worldworkbench.core.Goal.__post_init__"></a>

#### \_\_post\_init\_\_

```python
def __post_init__() -> None
```

<a id="worldworkbench.core.WorldModel"></a>

## WorldModel Objects

```python
@dataclass(frozen=True)
class WorldModel()
```

<a id="worldworkbench.core.WorldModel.model_id"></a>

#### model\_id: `str`

<a id="worldworkbench.core.WorldModel.revision"></a>

#### revision: `int`

<a id="worldworkbench.core.WorldModel.state"></a>

#### state: `Mapping[str, Any]`

<a id="worldworkbench.core.WorldModel.entities"></a>

#### entities: `tuple[Any, ...]`

<a id="worldworkbench.core.WorldModel.dynamics"></a>

#### dynamics: `tuple[Any, ...]`

<a id="worldworkbench.core.WorldModel.evidence"></a>

#### evidence: `tuple[str, ...]`

<a id="worldworkbench.core.WorldModel.confidence"></a>

#### confidence: `float`

<a id="worldworkbench.core.WorldModel.__post_init__"></a>

#### \_\_post\_init\_\_

```python
def __post_init__() -> None
```

<a id="worldworkbench.core.SimulationRequest"></a>

## SimulationRequest Objects

```python
@dataclass(frozen=True)
class SimulationRequest()
```

<a id="worldworkbench.core.SimulationRequest.simulation_id"></a>

#### simulation\_id: `str`

<a id="worldworkbench.core.SimulationRequest.world_model_id"></a>

#### world\_model\_id: `str`

<a id="worldworkbench.core.SimulationRequest.goal_ids"></a>

#### goal\_ids: `tuple[str, ...]`

<a id="worldworkbench.core.SimulationRequest.intervention"></a>

#### intervention: `Mapping[str, Any]`

<a id="worldworkbench.core.SimulationRequest.horizon"></a>

#### horizon: `int`

<a id="worldworkbench.core.SimulationRequest.assumptions"></a>

#### assumptions: `tuple[str, ...]`

<a id="worldworkbench.core.SimulationRequest.__post_init__"></a>

#### \_\_post\_init\_\_

```python
def __post_init__() -> None
```

<a id="worldworkbench.core.SimulationResult"></a>

## SimulationResult Objects

```python
@dataclass(frozen=True)
class SimulationResult()
```

<a id="worldworkbench.core.SimulationResult.simulation_id"></a>

#### simulation\_id: `str`

<a id="worldworkbench.core.SimulationResult.predicted_state"></a>

#### predicted\_state: `Mapping[str, Any]`

<a id="worldworkbench.core.SimulationResult.goal_scores"></a>

#### goal\_scores: `Mapping[str, float]`

<a id="worldworkbench.core.SimulationResult.evidence"></a>

#### evidence: `tuple[str, ...]`

<a id="worldworkbench.core.SimulationResult.confidence"></a>

#### confidence: `float`

<a id="worldworkbench.core.SimulationResult.__post_init__"></a>

#### \_\_post\_init\_\_

```python
def __post_init__() -> None
```

<a id="worldworkbench.core.WorldAnalysisState"></a>

## WorldAnalysisState Objects

```python
class WorldAnalysisState()
```

Append-only analysis state shared by workbench processing resources.

Processors enrich the state by writing new silo versions. Older versions
remain available for provenance, comparison, replay, and debugging.

<a id="worldworkbench.core.WorldAnalysisState.__init__"></a>

#### \_\_init\_\_

```python
def __init__(analysis_id: str | None = None) -> None
```

<a id="worldworkbench.core.WorldAnalysisState.put"></a>

#### put

```python
def put(silo_id: str,
        *,
        semantic_type: str,
        representation_type: str,
        value: Any,
        subject: str | None = None,
        status: SiloStatus = SiloStatus.GENERATED,
        confidence: float = 1.0,
        produced_by: ProducerRef | None = None,
        derived_from: Iterable[str] = (),
        metadata: Mapping[str, Any] | None = None) -> SiloRecord
```

<a id="worldworkbench.core.WorldAnalysisState.latest"></a>

#### latest

```python
def latest(silo_id: str) -> SiloRecord
```

<a id="worldworkbench.core.WorldAnalysisState.get"></a>

#### get

```python
def get(reference: str) -> SiloRecord
```

<a id="worldworkbench.core.WorldAnalysisState.history"></a>

#### history

```python
def history(silo_id: str) -> tuple[SiloRecord, ...]
```

<a id="worldworkbench.core.WorldAnalysisState.latest_silos"></a>

#### latest\_silos

```python
def latest_silos() -> Mapping[str, SiloRecord]
```

<a id="worldworkbench.core.WorldAnalysisState.record_observation"></a>

#### record\_observation

```python
def record_observation(observation: Observation,
                       *,
                       producer: ProducerRef | None = None) -> SiloRecord
```

<a id="worldworkbench.core.WorldAnalysisState.set_world_model"></a>

#### set\_world\_model

```python
def set_world_model(model: WorldModel,
                    *,
                    derived_from: Iterable[str] = (),
                    producer: ProducerRef | None = None) -> SiloRecord
```

<a id="worldworkbench.core.WorldAnalysisState.set_goals"></a>

#### set\_goals

```python
def set_goals(goals: Sequence[Goal],
              *,
              derived_from: Iterable[str] = (),
              producer: ProducerRef | None = None) -> SiloRecord
```

<a id="worldworkbench.core.WorldAnalysisState.record_simulation"></a>

#### record\_simulation

```python
def record_simulation(request: SimulationRequest,
                      result: SimulationResult,
                      *,
                      derived_from: Iterable[str] = (),
                      producer: ProducerRef | None = None) -> SiloRecord
```

<a id="worldworkbench.core.WorldAnalysisState.record_demonstration_step"></a>

#### record\_demonstration\_step

```python
def record_demonstration_step(
        step: DemonstrationStep,
        *,
        producer: ProducerRef | None = None) -> SiloRecord
```

<a id="worldworkbench.core.ObservationAnalyzer"></a>

## ObservationAnalyzer Objects

```python
class ObservationAnalyzer(Protocol)
```

<a id="worldworkbench.core.ObservationAnalyzer.analyze"></a>

#### analyze

```python
def analyze(observation: Observation,
            state: WorldAnalysisState) -> Iterable[SiloRecord]
```

<a id="worldworkbench.core.WorldModelLearner"></a>

## WorldModelLearner Objects

```python
class WorldModelLearner(Protocol)
```

<a id="worldworkbench.core.WorldModelLearner.update"></a>

#### update

```python
def update(observation: Observation, state: WorldAnalysisState) -> WorldModel
```

<a id="worldworkbench.core.GoalProvider"></a>

## GoalProvider Objects

```python
class GoalProvider(Protocol)
```

<a id="worldworkbench.core.GoalProvider.goals"></a>

#### goals

```python
def goals(state: WorldAnalysisState, model: WorldModel) -> Sequence[Goal]
```

<a id="worldworkbench.core.SimulationPolicy"></a>

## SimulationPolicy Objects

```python
class SimulationPolicy(Protocol)
```

<a id="worldworkbench.core.SimulationPolicy.select"></a>

#### select

```python
def select(state: WorldAnalysisState, model: WorldModel,
           goals: Sequence[Goal]) -> Iterable[SimulationRequest]
```

<a id="worldworkbench.core.Simulator"></a>

## Simulator Objects

```python
class Simulator(Protocol)
```

<a id="worldworkbench.core.Simulator.simulate"></a>

#### simulate

```python
def simulate(request: SimulationRequest,
             model: WorldModel) -> SimulationResult
```

<a id="worldworkbench.core.WorldLearningWorkbench"></a>

## WorldLearningWorkbench Objects

```python
class WorldLearningWorkbench()
```

Coordinates analysis, world learning, goals, and selected simulation.

<a id="worldworkbench.core.WorldLearningWorkbench.__init__"></a>

#### \_\_init\_\_

```python
def __init__(*,
             learner: WorldModelLearner,
             goal_provider: GoalProvider,
             simulation_policy: SimulationPolicy,
             simulator: Simulator,
             analyzers: Sequence[ObservationAnalyzer] = (),
             state: WorldAnalysisState | None = None) -> None
```

<a id="worldworkbench.core.WorldLearningWorkbench.process"></a>

#### process

```python
def process(observation: Observation) -> tuple[SimulationResult, ...]
```

<a id="worldworkbench.core.HumanDemonstrationObserver"></a>

## HumanDemonstrationObserver Objects

```python
class HumanDemonstrationObserver()
```

Collect human play as learning examples without choosing actions itself.

<a id="worldworkbench.core.HumanDemonstrationObserver.__init__"></a>

#### \_\_init\_\_

```python
def __init__(*,
             analyzers: Sequence[ObservationAnalyzer] = (),
             state: WorldAnalysisState | None = None) -> None
```

<a id="worldworkbench.core.HumanDemonstrationObserver.begin"></a>

#### begin

```python
def begin(observation: Observation) -> SiloRecord
```

Record and objectify the first observation of an episode.

<a id="worldworkbench.core.HumanDemonstrationObserver.observe_human_step"></a>

#### observe\_human\_step

```python
def observe_human_step(intervention: Intervention,
                       resulting_observation: Observation,
                       *,
                       step_id: str | None = None) -> DemonstrationStep
```

Record a human-selected action and the observation it produced.
