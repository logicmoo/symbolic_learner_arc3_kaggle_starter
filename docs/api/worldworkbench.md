> [← Project README](../../README.md)

# Table of Contents

* [worldworkbench](#worldworkbench)
* [worldworkbench.adapters.arc3](#worldworkbench.adapters.arc3)
  * [Arc3ObservationAdapter](#worldworkbench.adapters.arc3.Arc3ObservationAdapter)
  * [Arc3InterventionAdapter](#worldworkbench.adapters.arc3.Arc3InterventionAdapter)
    * [apply\_human\_choice](#worldworkbench.adapters.arc3.Arc3InterventionAdapter.apply_human_choice)
  * [arc3\_artifact\_metadata](#worldworkbench.adapters.arc3.arc3_artifact_metadata)
* [worldworkbench.adapters](#worldworkbench.adapters)
* [worldworkbench.core](#worldworkbench.core)
  * [SiloRecord](#worldworkbench.core.SiloRecord)
  * [Intervention](#worldworkbench.core.Intervention)
  * [DemonstrationStep](#worldworkbench.core.DemonstrationStep)
  * [WorldAnalysisState](#worldworkbench.core.WorldAnalysisState)
  * [WorldLearningWorkbench](#worldworkbench.core.WorldLearningWorkbench)
  * [HumanDemonstrationObserver](#worldworkbench.core.HumanDemonstrationObserver)
    * [begin](#worldworkbench.core.HumanDemonstrationObserver.begin)
    * [observe\_human\_step](#worldworkbench.core.HumanDemonstrationObserver.observe_human_step)

<a id="worldworkbench"></a>

# worldworkbench

Domain-neutral world analysis, learning, goal reasoning, and simulation.

<a id="worldworkbench.adapters.arc3"></a>

# worldworkbench.adapters.arc3

<a id="worldworkbench.adapters.arc3.Arc3ObservationAdapter"></a>

## Arc3ObservationAdapter Objects

```python
class Arc3ObservationAdapter()
```

Translate an Arc3Runner state into a domain-neutral observation.

<a id="worldworkbench.adapters.arc3.Arc3InterventionAdapter"></a>

## Arc3InterventionAdapter Objects

```python
class Arc3InterventionAdapter()
```

Apply a selected workbench intervention through an Arc3Runner.

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

<a id="worldworkbench.adapters"></a>

# worldworkbench.adapters

<a id="worldworkbench.core"></a>

# worldworkbench.core

<a id="worldworkbench.core.SiloRecord"></a>

## SiloRecord Objects

```python
@dataclass(frozen=True)
class SiloRecord()
```

One immutable version of a named, typed information silo.

<a id="worldworkbench.core.Intervention"></a>

## Intervention Objects

```python
@dataclass(frozen=True)
class Intervention()
```

An action observed in or applied to an external world.

<a id="worldworkbench.core.DemonstrationStep"></a>

## DemonstrationStep Objects

```python
@dataclass(frozen=True)
class DemonstrationStep()
```

A before/action/after example observed from a human demonstrator.

<a id="worldworkbench.core.WorldAnalysisState"></a>

## WorldAnalysisState Objects

```python
class WorldAnalysisState()
```

Append-only analysis state shared by workbench processing resources.

Processors enrich the state by writing new silo versions. Older versions
remain available for provenance, comparison, replay, and debugging.

<a id="worldworkbench.core.WorldLearningWorkbench"></a>

## WorldLearningWorkbench Objects

```python
class WorldLearningWorkbench()
```

Coordinates analysis, world learning, goals, and selected simulation.

<a id="worldworkbench.core.HumanDemonstrationObserver"></a>

## HumanDemonstrationObserver Objects

```python
class HumanDemonstrationObserver()
```

Collect human play as learning examples without choosing actions itself.

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
