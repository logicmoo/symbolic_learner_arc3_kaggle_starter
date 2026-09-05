# `worldworkbench.adapters.arc3`

> [← Project README](../../README.md)

## Classes

### `class Arc3InterventionAdapter`

Apply a selected workbench intervention through an Arc3Runner.

- `apply(self, runner: 'Any', request: 'SimulationRequest') -> 'Any'`
- `apply_human_choice(self, runner: 'Any', action: 'Any', *, data: 'Mapping[str, Any] | None' = None, intervention_id: 'str | None' = None) -> 'tuple[Intervention, Observation]'` — Apply a human-selected ARC3 action and capture its resulting state.

### `class Arc3ObservationAdapter`

Translate an Arc3Runner state into a domain-neutral observation.

- `capture(self, runner: 'Any', *, observation_id: 'str | None' = None) -> 'Observation'`

## Functions

### `arc3_artifact_metadata(runner: 'Any') -> 'dict[str, str | None]'`

Return portable links to the current ARC3 evidence artifacts.
