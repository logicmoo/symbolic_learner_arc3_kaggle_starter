# `omega_vision.models`

> [← Project README](../../README.md)

## Classes

### `class ActionRecommendation`

Fields:
- `recommendation_id: str`
- `rule_id: str`
- `source_state_id: str`
- `recommended_action: Any`
- `attempted_action: Any`
- `created_sequence: int`
- `rival_rule_ids: tuple[str, ...]`
- `available_evidence_ids: tuple[str, ...]`
- `assumptions: tuple[str, ...]`
- `critiques: tuple[str, ...]`
- `probability: float | None`
- `probability_source: str`
- `prediction_id: str | None`
- `schema_version: str`


### `class ArtifactProviderProtocol`

- `get_candidate_part(self, candidate: 'CandidateObject', name: 'str') -> 'NormalizedResult'`

### `class ArtifactRef`

Fields:
- `artifact_id: str`
- `artifact_type: str`
- `uri: str`
- `content_hash: str | None`
- `media_type: str | None`
- `provenance: tuple[ProvenanceRef, ...]`
- `schema_version: str`


### `class CandidateObject`

Fields:
- `candidate_id: str`
- `observation_id: str`
- `domain: str`
- `provider: 'ArtifactProviderProtocol'`
- `region_ref: str | None`
- `provenance: tuple[str, ...]`

- `part(self, name: 'str') -> 'NormalizedResult'`

### `class CommittedAtom`

Fields:
- `handle: str`
- `atom_type: str`
- `payload: Mapping[str, Any]`
- `confidence: float`
- `provenance: tuple[str, ...]`
- `lifecycle_state: str`


### `class ConfidenceHistoryRecord`

Fields:
- `sequence: int`
- `handle: str`
- `confidence: float`
- `lifecycle_state: str`
- `event: str`
- `reference_id: str | None`


### `class EncounterRecord`

Fields:
- `encounter_id: str`
- `observation_id: str`
- `action_tree_node: str`
- `object_identity_id: str | None`
- `candidate_identity_id: str | None`
- `instance: InstanceParameters`
- `matched_properties: tuple[str, ...]`
- `changed_properties: Mapping[str, Any]`
- `turtle_programs: tuple[TurtleProgramRef, ...]`
- `reconstruction_artifacts: tuple[ArtifactRef, ...]`
- `residual_ids: tuple[str, ...]`
- `confidence: float`
- `evidence_ids: tuple[str, ...]`
- `previous_encounter_id: str | None`
- `next_encounter_id: str | None`
- `provenance: tuple[ProvenanceRef, ...]`
- `deterministic_hash: str`
- `schema_version: str`


### `class EvidencePolarity(str, Enum)`

str(object='') -> str str(bytes_or_buffer[, encoding[, errors]]) -> str

Values: `SUPPORTS`, `CONTRADICTS`

### `class EvidenceRecord`

Fields:
- `evidence_id: str`
- `subject_id: str`
- `polarity: EvidencePolarity`
- `source: ProvenanceRef`
- `weight: float`
- `detail: Mapping[str, Any]`
- `created_sequence: int`
- `schema_version: str`


### `class ExecutionMode(str, Enum)`

str(object='') -> str str(bytes_or_buffer[, encoding[, errors]]) -> str

Values: `PROLOG`, `GPT`, `PYTHON`

### `class IdentityDecision(str, Enum)`

str(object='') -> str str(bytes_or_buffer[, encoding[, errors]]) -> str

Values: `PROPOSED`, `ACCEPTED`, `REJECTED`, `REVERSED`

### `class IdentityMemoryCheckpoint`

Append-only, self-contained identity-writer state for durable recovery.

Fields:
- `checkpoint_id: str`
- `sequence: int`
- `event: str`
- `reference_id: str | None`
- `parent_checkpoint_id: str | None`
- `atoms: tuple[CommittedAtom, ...]`
- `evidence: tuple[EvidenceRecord, ...]`
- `merge_decisions: tuple[MergeDecision, ...]`
- `split_decisions: tuple[SplitDecision, ...]`
- `decision_snapshots: Mapping[str, Mapping[str, CommittedAtom | None]]`
- `confidence_history: tuple[ConfidenceHistoryRecord, ...]`
- `schema_version: str`

- `as_compaction_root(self) -> "'IdentityMemoryCheckpoint'"` — Create a standalone root retaining the exact current writer state.

### `class InstanceParameters`

Fields:
- `position: tuple[float, ...]`
- `orientation: float | str | None`
- `scale: tuple[float, ...]`
- `appearance: Mapping[str, Any]`
- `supported_transformations: tuple[str, ...]`
- `reflection: str | None`
- `visibility: float`
- `noise_score: float`
- `geometry: Mapping[str, Any]`
- `topology: Mapping[str, Any]`
- `relationships: tuple[Mapping[str, Any], ...]`
- `schema_version: str`


### `class MatchProposal`

Fields:
- `proposal_id: str`
- `candidate_id: str`
- `stored_identity_id: str`
- `matched_properties: tuple[str, ...]`
- `changed_properties: Mapping[str, Any]`
- `allowed_transformations: tuple[str, ...]`
- `similarity: float | None`
- `retrieval_score: float | None`
- `retrieval_source: str | None`
- `probability: float | None`
- `probability_source: str | None`
- `evidence_ids: tuple[str, ...]`
- `provenance: tuple[ProvenanceRef, ...]`
- `schema_version: str`


### `class MergeDecision`

Fields:
- `decision_id: str`
- `identity_ids: tuple[str, ...]`
- `resulting_identity_id: str`
- `status: IdentityDecision`
- `evidence_ids: tuple[str, ...]`
- `provenance: tuple[ProvenanceRef, ...]`
- `schema_version: str`


### `class NormalizedResult`

Backend-neutral return shape used by all providers.

Fields:
- `value: Any`
- `mode: ExecutionMode`
- `source_refs: tuple[str, ...]`
- `evidence: tuple[str, ...]`
- `metadata: Mapping[str, Any]`


### `class ObjectChange`

Fields:
- `change_id: str`
- `kind: str`
- `before_identity_ids: tuple[str, ...]`
- `after_candidate_ids: tuple[str, ...]`
- `properties: Mapping[str, Any]`
- `evidence_ids: tuple[str, ...]`
- `provenance: tuple[ProvenanceRef, ...]`
- `schema_version: str`


### `class Observation`

Fields:
- `observation_id: str`
- `source_modality: str`
- `artifacts: tuple[ArtifactRef, ...]`
- `dimensions: tuple[int, ...]`
- `coordinate_contract: str`
- `candidate_object_ids: tuple[str, ...]`
- `action_tree_node: str | None`
- `provenance: tuple[ProvenanceRef, ...]`
- `schema_version: str`


### `class PredictionGradeRecord`

Immutable outcome and grade linked to an earlier prediction.

Fields:
- `prediction_id: str`
- `rule_id: str`
- `outcome_sequence: int`
- `outcome: Any`
- `grade: float | None`
- `status: str`
- `evidence: tuple[str, ...]`
- `evidence_record_ids: tuple[str, ...]`
- `prior_probability: float | None`
- `calibrated_probability: float | None`
- `schema_version: str`


### `class PredictionRecord`

Fields:
- `prediction_id: str`
- `rule_id: str`
- `source_state_id: str`
- `predicted_effects: tuple[Any, ...]`
- `created_sequence: int`
- `available_evidence_ids: tuple[str, ...]`
- `rule_assumptions: tuple[str, ...]`
- `rule_critiques: tuple[str, ...]`
- `rule_probability: float | None`
- `rule_probability_source: str`
- `outcome_sequence: int | None`
- `outcome: Any`
- `grade: float | None`


### `class ProvenanceRef`

Fields:
- `source_id: str`
- `provider: str`
- `action_tree_node: str | None`
- `artifact_id: str | None`
- `sequence: int | None`
- `metadata: Mapping[str, Any]`
- `schema_version: str`


### `class RecognitionAccount`

Fields:
- `account_id: str`
- `candidate_id: str`
- `stored_identity_id: str | None`
- `matched_properties: tuple[str, ...]`
- `changed_properties: Mapping[str, Any]`
- `allowed_transformations: tuple[str, ...]`
- `turtle_reconstruction_fit: float | None`
- `residual_score: float | None`
- `supporting_evidence_ids: tuple[str, ...]`
- `contradicting_evidence_ids: tuple[str, ...]`
- `rival_proposal_ids: tuple[str, ...]`
- `calibrated_confidence: float`
- `decision_confidence: float | None`
- `decision_outcome: bool | None`
- `decision_source: str`
- `provenance: tuple[ProvenanceRef, ...]`
- `schema_version: str`


### `class ResidualCandidate`

Fields:
- `residual_id: str`
- `source_candidate_id: str`
- `disposition: ResidualDisposition`
- `residual_length: float`
- `structured: bool`
- `recurrence_count: int`
- `prediction_gain: float`
- `provenance: tuple[str, ...]`


### `class ResidualDisposition(str, Enum)`

str(object='') -> str str(bytes_or_buffer[, encoding[, errors]]) -> str

Values: `ABSORBED`, `PROVISIONAL`, `COMMIT_REQUEST`

### `class SplitDecision`

Fields:
- `decision_id: str`
- `source_identity_id: str`
- `resulting_identity_ids: tuple[str, ...]`
- `status: IdentityDecision`
- `evidence_ids: tuple[str, ...]`
- `provenance: tuple[ProvenanceRef, ...]`
- `schema_version: str`


### `class TransitionRule`

Fields:
- `rule_id: str`
- `preconditions: tuple[Any, ...]`
- `action_or_event: Any`
- `predicted_effects: tuple[Any, ...]`
- `provenance: tuple[str, ...]`
- `assumptions: tuple[str, ...]`
- `critiques: tuple[str, ...]`
- `supporting_evidence_ids: tuple[str, ...]`
- `contradicting_evidence_ids: tuple[str, ...]`
- `rival_rule_ids: tuple[str, ...]`
- `bootstrap_probability: float`
- `calibrated_probability: float | None`
- `probability_source: str`
- `coverage: float`
- `applicability_precision: float | None`
- `prediction_attempts: int`
- `prediction_successes: int`
- `prediction_score_total: float`
- `prediction_history: tuple[str, ...]`


### `class TurtleProgramRef`

Fields:
- `artifact: ArtifactRef`
- `language: str`
- `entrypoint: str | None`
- `fit_score: float | None`
- `distance: float | None`
- `residual_score: float | None`
- `description_length: float | None`
- `schema_version: str`


## Functions

### `deterministic_identifier(record_type: 'str', identity: 'Mapping[str, Any]') -> 'str'`

Create a reproducible identifier from the record's immutable identity.
