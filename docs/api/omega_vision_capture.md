# `omega_vision.capture`

> [← Project README](../../README.md)

## Classes

### `class SemanticGridCaptureObserver`

External Arc3Runner observer that persists normalized Phase 2 records.

- `__init__(self, adapter: 'GridAdapter', grid_selector: 'Callable[[Any], Any]', symbolic_store: 'SymbolicStore | None' = None, turtle_form_factory: 'Callable[[str], GenerativeForm] | None' = None, identity_writer: 'SingleWriter | None' = None, learner_plugin: 'Any | None' = None) -> 'None'`
- `authorization_options(self) -> 'dict[str, tuple[str, ...]]'` — Return explicit friendly-identity choices for unresolved candidates.
- `authorize_candidate(self, *, candidate_id: 'str', selected_identity_id: 'str', decision_id: 'str', decision_source: 'str' = 'explicit_registry_selection') -> 'RecognitionAccount'` — Accept one pending proposal through the single identity writer.
- `before_action(self, *, runner: 'Any', store: 'Any', node: 'Any', action: 'str', data: 'Mapping[str, Any]') -> 'None'` — Record a learned-rule prediction before Arc3Runner observes the outcome.
- `on_state_captured(self, *, runner: 'Any', store: 'Any', node: 'Any', previous_node: 'Any', action: 'str | None', data: 'Mapping[str, Any]') -> 'None'`
- `reject_candidate(self, *, candidate_id: 'str', selected_identity_id: 'str', decision_id: 'str', decision_source: 'str' = 'explicit_registry_rejection') -> 'RecognitionAccount'` — Reject one pending friendly-identity proposal without calibrating it.

## Functions

### `standard_semantic_grid_observer(*, learner_plugin: 'Any | None' = None) -> "'SemanticGridCaptureObserver'"`

Compose the canonical live grid observer without coupling it to Phase 1.
