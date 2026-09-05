# `omega_vision.recognition`

> [← Project README](../../README.md)

## Classes

### `class ChangeDetector`

Classify resolved before/after correspondences into semantic changes.

- `detect(self, *, proposals: 'Mapping[str, MatchProposal]', correspondence: 'Mapping[str, tuple[str, ...]]', before_identity_ids: 'tuple[str, ...]', after_candidate_ids: 'tuple[str, ...]', provenance: 'tuple[ProvenanceRef, ...]' = ()) -> 'tuple[ObjectChange, ...]'`

### `class CorrespondenceEvidenceBuilder`

Create attributable signed evidence from a proposal's property explanation.

- `build(self, proposal: 'MatchProposal', *, source: 'ProvenanceRef', created_sequence: 'int' = 0) -> 'tuple[EvidenceRecord, ...]'`

### `class EncounterChangeSession`

Persist correspondences, evidence, and changes across two observations.

- `__init__(self, store: 'SymbolicStore', matcher: 'InstanceMatcher | None' = None) -> 'None'`
- `detect(self, previous_observation_id: 'str', current_observation_id: 'str') -> 'tuple[tuple[MatchProposal, ...], tuple[ObjectChange, ...], tuple[ResidualCandidate, ...]]'`

### `class InstanceMatcher`

Generate advisory correspondence proposals from normalized instances.

- `change_transformation(field: 'str') -> 'str'`
- `compare(self, *, candidate_id: 'str', current: 'InstanceParameters', stored_identity_id: 'str', stored: 'InstanceParameters', provenance: 'tuple[ProvenanceRef, ...]' = ()) -> 'MatchProposal'`
- `proposals(self, *, candidate_id: 'str', current: 'InstanceParameters', stored: 'Mapping[str, InstanceParameters]', provenance: 'tuple[ProvenanceRef, ...]' = (), retrieval_scores: 'Mapping[str, float] | None' = None, retrieval_source: 'str | None' = None, calibration_policy: 'RecognitionCalibrationPolicy | None' = None) -> 'tuple[MatchProposal, ...]'`
- `recognition_account(self, *, candidate_id: 'str', proposals: 'tuple[MatchProposal, ...]', selected_identity_id: 'str | None' = None, decision_source: 'str' = 'unresolved') -> 'RecognitionAccount'`

### `class PartialVisibilityCompletion`

A reconstructed instance that keeps inferred and observed data distinct.

Fields:
- `candidate_id: str`
- `stored_identity_id: str`
- `observed: InstanceParameters`
- `completed: InstanceParameters`
- `inferred_fields: tuple[str, ...]`
- `proposal_id: str`
- `evidence_ids: tuple[str, ...]`


### `class RecognitionSession`

Persist unresolved proposals between a candidate and known encounter histories.

- `__init__(self, store: 'SymbolicStore', matcher: 'InstanceMatcher | None' = None) -> 'None'`
- `complete_partial(self, encounter_id: 'str', stored_identity_id: 'str') -> 'PartialVisibilityCompletion'` — Complete an occluded encounter from one prior durable identity form.
- `latest_known_instances(self) -> 'dict[str, InstanceParameters]'`
- `propose(self, encounter_id: 'str', *, retrieval_scores: 'Mapping[str, float] | None' = None, retrieval_source: 'str | None' = None) -> 'tuple[MatchProposal, ...]'`
- `unresolved_account(self, candidate_id: 'str') -> 'RecognitionAccount | None'`

### `class RegistryCorrespondenceAuthority`

Apply an explicit registry selection only when attributable evidence exists.

- `__init__(self, writer: 'SingleWriter | None', action_tree_store: 'object') -> 'None'`
- `accept(self, *, candidate_id: 'str', selected_identity_id: 'str', proposals: 'tuple[MatchProposal, ...]', evidence: 'tuple[EvidenceRecord, ...]', encounter_id: 'str', decision_id: 'str', decision_source: 'str') -> 'RecognitionAccount'`
- `reject(self, *, candidate_id: 'str', selected_identity_id: 'str', proposals: 'tuple[MatchProposal, ...]', encounter_id: 'str', decision_id: 'str', decision_source: 'str', evidence_ids: 'tuple[str, ...]' = ()) -> 'RecognitionAccount'`
- `reverse(self, *, identity_id: 'str', encounter_id: 'str', decision_id: 'str', evidence_ids: 'tuple[str, ...]') -> 'None'`

### `class ResidualAnalyzer`

Separate unexplained proposal structure from recognized transformations.

- `__init__(self, gate: 'ResidualGate | None' = None) -> 'None'`
- `from_proposal(self, proposal: 'MatchProposal') -> 'tuple[ResidualCandidate, ...]'`

### `class StructuralCorrespondenceInferer`

Infer only exact one-to-one, split, or merge cell-set correspondences.

- `infer(self, previous: 'Mapping[str, Any]', current: 'Mapping[str, Any]') -> 'dict[str, tuple[str, ...]]'`

### `class TurtleReconstructionEvidenceBuilder`

Represent an exact or residual Turtle reconstruction fit as signed evidence.

- `build(self, *, identity_id: 'str', fit: 'FitResult', source: 'ProvenanceRef', artifact_id: 'str | None' = None, created_sequence: 'int' = 0) -> 'EvidenceRecord'`
