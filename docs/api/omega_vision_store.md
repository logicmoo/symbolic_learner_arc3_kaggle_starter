# `omega_vision.store`

> [← Project README](../../README.md)

## Classes

### `class ArtifactIndex`

Exact artifact lookup by stable ID and semantic artifact type.

- `__init__(self) -> 'None'`
- `by_type(self, artifact_type: 'str') -> 'tuple[ArtifactRef, ...]'`
- `get(self, artifact_id: 'str') -> 'ArtifactRef | None'`
- `register(self, artifact: 'ArtifactRef') -> 'ArtifactRef'`

### `class InMemorySemanticBackend`

Deterministic reference backend used by tests and local composition.

- `__init__(self) -> 'None'`
- `get(self, namespace: 'str', record_id: 'str') -> 'Any | None'`
- `values(self, namespace: 'str') -> 'tuple[Any, ...]'`
- `write_once(self, namespace: 'str', record_id: 'str', value: 'Any') -> 'Any'`

### `class SemanticStoreBackend(Protocol)`

Minimal exact-record boundary implemented by Prolog or AtomSpace stores.

- `__init__(self, *args, **kwargs)`
- `get(self, namespace: 'str', record_id: 'str') -> 'Any | None'`
- `values(self, namespace: 'str') -> 'tuple[Any, ...]'`
- `write_once(self, namespace: 'str', record_id: 'str', value: 'Any') -> 'Any'`

### `class SymbolicStore`

Backend-neutral facade for exact Phase 2 semantic records.

- `__init__(self, backend: 'SemanticStoreBackend') -> 'None'`
- `compacted_snapshot(self) -> 'dict[str, tuple[Any, ...]]'` — Export one self-contained checkpoint root plus all other semantic records.
- `get(self, namespace: 'str', record_id: 'str') -> 'Any | None'`
- `hydrate(self) -> "'SymbolicStore'"` — Populate facade indexes from records already present in the backend.
- `put_action_recommendation(self, value: 'ActionRecommendation') -> 'ActionRecommendation'`
- `put_artifact(self, value: 'ArtifactRef') -> 'ArtifactRef'`
- `put_atom(self, value: 'CommittedAtom') -> 'CommittedAtom'`
- `put_confidence_history(self, value: 'ConfidenceHistoryRecord') -> 'ConfidenceHistoryRecord'`
- `put_encounter(self, value: 'EncounterRecord') -> 'EncounterRecord'`
- `put_evidence(self, value: 'EvidenceRecord') -> 'EvidenceRecord'`
- `put_identity_checkpoint(self, value: 'IdentityMemoryCheckpoint') -> 'IdentityMemoryCheckpoint'`
- `put_match_proposal(self, value: 'MatchProposal') -> 'MatchProposal'`
- `put_object_change(self, value: 'ObjectChange') -> 'ObjectChange'`
- `put_observation(self, value: 'Observation') -> 'Observation'`
- `put_prediction(self, value: 'PredictionRecord') -> 'PredictionRecord'`
- `put_prediction_grade(self, value: 'PredictionGradeRecord') -> 'PredictionGradeRecord'`
- `put_recognition(self, value: 'RecognitionAccount') -> 'RecognitionAccount'`
- `put_recognition_calibration(self, value: 'RecognitionCalibrationPolicy') -> 'RecognitionCalibrationPolicy'`
- `put_residual(self, value: 'ResidualCandidate') -> 'ResidualCandidate'`
- `put_transition_rule(self, value: 'TransitionRule') -> 'TransitionRule'`
- `put_turtle(self, value: 'TurtleProgramRef') -> 'TurtleProgramRef'`
- `replay(self, snapshot: 'dict[str, tuple[Any, ...]]') -> "'SymbolicStore'"` — Idempotently reconstruct this facade and its indexes from a snapshot.
- `restore_identity_memory(self) -> "'SymbolicMemory'"` — Restore the newest complete identity state stored by a SingleWriter.
- `snapshot(self) -> 'dict[str, tuple[Any, ...]]'` — Capture exact semantic records in deterministic replay order.
- `values(self, namespace: 'str') -> 'tuple[Any, ...]'`
