# `omega_vision`

> [← Project README](../../README.md)

Shared object-memory contracts for PROLOG, GPT, and PYTHON backends.

The package supplements the existing ARC3 debugger. It does not replace
Arc3Runner, ActionTreeStore, GptArcAnalyzer, SWIPrologBridge, or the generated
Prolog artifact contracts.

## Classes

### `class AbstractGenerativeForm(ABC)`

Abstract typed contract for a generative form (Turtle/LOGO and later raster).

- `canonicalize(self) -> 'str'`
- `distance(self, other: "'AbstractGenerativeForm'") -> 'float'`
- `fit_instance(self, candidate: 'Any') -> 'FitResult'`
- `render(self, params: 'dict[str, Any] | None' = None) -> 'Any'`

### `class AcceptanceReport`

Fields:
- `accepted: bool`
- `checks: Mapping[str, bool]`
- `evidence: Mapping[str, Any]`

- `to_json(self) -> 'str'`
- `to_markdown(self) -> 'str'`

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


### `class ActionTreeSemanticReplay`

Rebuild a semantic store from the exact records linked by an action tree.

- `replay(self, action_tree_root: 'Path', store: 'SymbolicStore') -> 'SymbolicStore'`

### `class AlphaContourProvider`

Extract transparent sprites and exact pixel-boundary vector contours.


### `class ArtifactIndex`

Exact artifact lookup by stable ID and semantic artifact type.

- `__init__(self) -> 'None'`
- `by_type(self, artifact_type: 'str') -> 'tuple[ArtifactRef, ...]'`
- `get(self, artifact_id: 'str') -> 'ArtifactRef | None'`
- `register(self, artifact: 'ArtifactRef') -> 'ArtifactRef'`

### `class ArtifactProvider(ABC)`

One stable contract with backend-specific implementations.

- `capabilities(self) -> 'ProviderCapabilities'`
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


### `class AtomSpaceSemanticBackend`

Exact semantic records stored as queryable ``semantic_record`` Atoms.

- `__init__(self, transport: 'AtomSpaceTransport | None' = None, *, path: 'Path | None' = None) -> 'None'`
- `get(self, namespace: 'str', record_id: 'str') -> 'Any | None'`
- `values(self, namespace: 'str') -> 'tuple[Any, ...]'`
- `write_once(self, namespace: 'str', record_id: 'str', value: 'Any') -> 'Any'`

### `class AtomSpaceTransport(Protocol)`

Transport boundary for a MeTTa/OpenCog AtomSpace implementation.

- `__init__(self, *args, **kwargs)`
- `assert_expression(self, expression: 'str') -> 'None'`
- `query(self, head: 'str') -> 'Iterable[str]'`

### `class CalibrationPoint`

Fields:
- `upper_confidence: float`
- `probability: float`
- `sample_count: int`


### `class CandidateObject`

Fields:
- `candidate_id: str`
- `observation_id: str`
- `domain: str`
- `provider: 'ArtifactProviderProtocol'`
- `region_ref: str | None`
- `provenance: tuple[str, ...]`

- `part(self, name: 'str') -> 'NormalizedResult'`

### `class ChangeDetector`

Classify resolved before/after correspondences into semantic changes.

- `detect(self, *, proposals: 'Mapping[str, MatchProposal]', correspondence: 'Mapping[str, tuple[str, ...]]', before_identity_ids: 'tuple[str, ...]', after_candidate_ids: 'tuple[str, ...]', provenance: 'tuple[ProvenanceRef, ...]' = ()) -> 'tuple[ObjectChange, ...]'`

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


### `class CorrespondenceEvidenceBuilder`

Create attributable signed evidence from a proposal's property explanation.

- `build(self, proposal: 'MatchProposal', *, source: 'ProvenanceRef', created_sequence: 'int' = 0) -> 'tuple[EvidenceRecord, ...]'`

### `class EncounterChangeSession`

Persist correspondences, evidence, and changes across two observations.

- `__init__(self, store: 'SymbolicStore', matcher: 'InstanceMatcher | None' = None) -> 'None'`
- `detect(self, previous_observation_id: 'str', current_observation_id: 'str') -> 'tuple[tuple[MatchProposal, ...], tuple[ObjectChange, ...], tuple[ResidualCandidate, ...]]'`

### `class EncounterLog`

Append-only semantic encounters with deterministic, idempotent replay.

- `__init__(self) -> 'None'`
- `append(self, encounter: 'EncounterRecord') -> 'EncounterRecord'`
- `deterministic_hash(self) -> 'str'`
- `for_object(self, object_identity_id: 'str') -> 'tuple[EncounterRecord, ...]'`
- `get(self, encounter_id: 'str') -> 'EncounterRecord | None'`
- `records(self) -> 'tuple[EncounterRecord, ...]'`
- `replay(self, encounters: 'tuple[EncounterRecord, ...]') -> "'EncounterLog'"`

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


### `class EnvironmentProgressionFixtures`

Fields:
- `rendered_arcade: tuple[PerceptionFixture, ...]`
- `fixed_camera: tuple[PerceptionFixture, ...]`
- `top_down_manipulation: tuple[PerceptionFixture, ...]`

- `all(self) -> 'tuple[PerceptionFixture, ...]'`

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

### `class FitResult`

Fields:
- `parameters: dict[str, Any]`
- `residual: float`


### `class GameLearningPipeline`

Connected Phase 3 flow; algorithms remain replaceable providers.

- `__init__(self, transition_analyzer: 'TransitionAnalyzer', transformation_learner: 'TransformationLearner', rule_inducer: 'RuleInducer', rule_ranker: 'RuleRanker', rule_store: 'RuleStore', prediction_ledger: 'PredictionLedger', semantic_store: 'Any | None' = None) -> 'None'`
- `grade_prediction(self, *, prediction_id: 'str', outcome_sequence: 'int', outcome_channel: 'OutcomeChannel', evaluator: 'PredictionEvaluator') -> 'PredictionRecord'`
- `learn_transition(self, before: 'Any', action_or_event: 'Any', after: 'Any') -> 'LearningStepResult'`
- `predict(self, *, prediction_id: 'str', rule_id: 'str', source_state_id: 'str', state: 'Any', created_sequence: 'int', executor: 'RuleExecutor') -> 'tuple[Any, PredictionRecord]'`
- `recommend_action(self, *, source_state_id: 'str', attempted_action: 'Any', created_sequence: 'int', prediction_id: 'str | None' = None) -> 'ActionRecommendation | None'` — Rank all learned actions independently of the action being attempted.

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


### `class GenerativeForm(AbstractGenerativeForm)`

Canonical Turtle/LOGO generative form over the existing DSL program.

- `__init__(self, program: 'str', renderer: 'Any | None' = None, swi_bridge: 'Any | None' = None) -> 'None'`
- `canonicalize(self) -> 'str'`
- `description_length(self) -> 'int'`
- `distance(self, other: 'AbstractGenerativeForm') -> 'float'`
- `fit_instance(self, candidate: 'Any') -> 'FitResult'`
- `render(self, params: 'dict[str, Any] | None' = None) -> 'Any'`

### `class GptArtifactProvider(ArtifactProvider)`

Reads GPT-generated or cached artifacts; it does not emulate native analysis.

- `__init__(self, node_path: 'str | Path') -> 'None'`
- `capabilities(self) -> 'ProviderCapabilities'`
- `get_candidate_part(self, candidate: 'CandidateObject', name: 'str') -> 'NormalizedResult'`

### `class GridAdapter(PerceptionAdapter)`

Thin adapter around an existing grid object extractor.

- `__init__(self, extractor: 'Any', provider: 'Any', role_provider: 'Any | None' = None) -> 'None'`
- `candidate_detail(self, candidate_id: 'str') -> 'Mapping[str, Any]'`
- `normalize(self, *, observation_id: 'str', grid: 'Any', action_tree_node: 'str', artifact_uri: 'str') -> 'GridPerceptionBatch'` — Wrap the established extractor result in Phase 2 contracts.
- `propose_candidates(self, observation: 'Any') -> 'Iterable[CandidateObject]'`

### `class GridPerceptionBatch`

Fields:
- `observation: Observation`
- `candidates: tuple[CandidateObject, ...]`
- `extractor_details: Mapping[str, Mapping[str, Any]]`


### `class IdentityCatalogEntry`

Fields:
- `identity_id: str`
- `instance: InstanceParameters`
- `registry_fact: str | None`
- `evidence: tuple[EvidenceRecord, ...]`
- `provenance: tuple[str, ...]`


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

### `class ImageAdapter(PerceptionAdapter)`

Normalize raster extractor output without prescribing segmentation.

- `__init__(self, extractor: 'Any', provider: 'Any', role_provider: 'Any | None' = None) -> 'None'`
- `candidate_detail(self, candidate_id: 'str') -> 'Mapping[str, Any]'`
- `normalize(self, *, observation_id: 'str', image: 'Any', action_tree_node: 'str', artifact_uri: 'str', sequence: 'int | None' = None) -> 'MediaPerceptionBatch'`
- `propose_candidates(self, observation: 'Any') -> 'Iterable[CandidateObject]'`

### `class InMemorySemanticBackend`

Deterministic reference backend used by tests and local composition.

- `__init__(self) -> 'None'`
- `get(self, namespace: 'str', record_id: 'str') -> 'Any | None'`
- `values(self, namespace: 'str') -> 'tuple[Any, ...]'`
- `write_once(self, namespace: 'str', record_id: 'str', value: 'Any') -> 'Any'`

### `class InstanceMatcher`

Generate advisory correspondence proposals from normalized instances.

- `change_transformation(field: 'str') -> 'str'`
- `compare(self, *, candidate_id: 'str', current: 'InstanceParameters', stored_identity_id: 'str', stored: 'InstanceParameters', provenance: 'tuple[ProvenanceRef, ...]' = ()) -> 'MatchProposal'`
- `proposals(self, *, candidate_id: 'str', current: 'InstanceParameters', stored: 'Mapping[str, InstanceParameters]', provenance: 'tuple[ProvenanceRef, ...]' = (), retrieval_scores: 'Mapping[str, float] | None' = None, retrieval_source: 'str | None' = None, calibration_policy: 'RecognitionCalibrationPolicy | None' = None) -> 'tuple[MatchProposal, ...]'`
- `recognition_account(self, *, candidate_id: 'str', proposals: 'tuple[MatchProposal, ...]', selected_identity_id: 'str | None' = None, decision_source: 'str' = 'unresolved') -> 'RecognitionAccount'`

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


### `class IntegrationError(ValueError)`

Inappropriate argument value (of correct type).


### `class IntegrationValidator`

- `__init__(self, schema: 'GameObjectLearnerSchema | None' = None, *, registry_identity_ids: 'set[str] | frozenset[str] | None' = None, provenance_source_ids: 'set[str] | frozenset[str] | None' = None) -> 'None'`
- `validate(self, payload: 'GameObjectLearnerPayload') -> 'GameObjectLearnerPayload'`

### `class LearnedPartRoleProvider`

Infer semantic component roles from labeled structural examples.

- `__init__(self, examples: 'Iterable[Mapping[str, Any]]') -> 'None'`
- `infer_part_roles(self, _item: 'Mapping[str, Any]', components: 'tuple[tuple[tuple[int, int], ...], ...]') -> 'tuple[Mapping[str, Any], ...]'`

### `class LearningStepResult`

Fields:
- `transition: TransitionRecord`
- `candidates: tuple[TransformationCandidate, ...]`
- `rules: tuple[TransitionRule, ...]`


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


### `class MediaPerceptionBatch`

Fields:
- `observation: Observation`
- `candidates: tuple[CandidateObject, ...]`
- `extractor_details: Mapping[str, Mapping[str, Any]]`


### `class MergeDecision`

Fields:
- `decision_id: str`
- `identity_ids: tuple[str, ...]`
- `resulting_identity_id: str`
- `status: IdentityDecision`
- `evidence_ids: tuple[str, ...]`
- `provenance: tuple[ProvenanceRef, ...]`
- `schema_version: str`


### `class MettaFileAtomSpaceTransport`

Durable AtomSpace transport using an inspectable MeTTa expression file.

- `__init__(self, path: 'Path') -> 'None'`
- `assert_expression(self, expression: 'str') -> 'None'`
- `query(self, head: 'str') -> 'tuple[str, ...]'`

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


### `class OutcomeChannel`

Independent observation channel used to grade a prior prediction.

- `__init__(self, read: 'Callable[[], Any]') -> 'None'`
- `read(self) -> 'Any'`

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


### `class PerceptionAdapter(ABC)`

Domain seam; core code must not import ARC or raster assumptions.

- `propose_candidates(self, observation: 'Any') -> 'Iterable[CandidateObject]'`

### `class PerceptionBenchmarkResult`

Fields:
- `fixture_id: str`
- `expected_count: int`
- `detected_count: int`
- `count_score: float`
- `degradation: str`


### `class PerceptionBenchmarkRunner`

Evaluate any normalized image adapter against count-labeled fixtures.

- `__init__(self, adapter: 'ImageAdapter') -> 'None'`
- `run(self, fixtures: 'Iterable[PerceptionFixture]') -> 'tuple[PerceptionBenchmarkResult, ...]'`

### `class PerceptionFixture`

Fields:
- `fixture_id: str`
- `image: Image.Image`
- `expected_count: int`
- `degradation: str`


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

### `class PredictionEvaluator`

- `__init__(self, compare: 'Callable[[Any, Any], PredictionGrade]') -> 'None'`
- `evaluate(self, predicted: 'Any', observed: 'Any') -> 'PredictionGrade'`

### `class PredictionGrade`

Fields:
- `score: float | None`
- `evidence: tuple[Any, ...]`
- `status: PredictionGradeStatus | None`


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


### `class PredictionGradeStatus(str, Enum)`

str(object='') -> str str(bytes_or_buffer[, encoding[, errors]]) -> str

Values: `SUCCESS`, `FAILURE`, `PARTIAL_MATCH`, `CONTRADICTION`, `UNGRADABLE`

### `class PredictionLedger`

Append-only prediction records enforcing predict-before-check.

- `__init__(self) -> 'None'`
- `get(self, prediction_id: 'str') -> 'PredictionRecord'`
- `grade(self, prediction_id: 'str', *, outcome_sequence: 'int', outcome: 'Any', grade: 'float | None') -> 'PredictionRecord'`
- `record(self, prediction: 'PredictionRecord') -> 'PredictionRecord'`
- `records(self) -> 'tuple[PredictionRecord, ...]'`

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


### `class PrologProvider(ArtifactProvider)`

Delegates symbolic queries to SWI-Prolog through an injected query function.

- `__init__(self, query: 'Callable[[str, Mapping[str, Any]], Any]') -> 'None'`
- `capabilities(self) -> 'ProviderCapabilities'`
- `get_candidate_part(self, candidate: 'CandidateObject', name: 'str') -> 'NormalizedResult'`
- `get_semantic_records(self, name: 'str', filters: 'Mapping[str, Any] | None' = None) -> 'NormalizedResult'` — Query one normalized semantic namespace through the Prolog adapter.

### `class PrologSemanticBackend`

Durable exact-record backend represented as inspectable SWI-Prolog facts.

- `__init__(self, path: 'Path') -> 'None'`
- `get(self, namespace: 'str', record_id: 'str') -> 'Any | None'`
- `values(self, namespace: 'str') -> 'tuple[Any, ...]'`
- `write_once(self, namespace: 'str', record_id: 'str', value: 'Any') -> 'Any'`

### `class ProvenanceRef`

Fields:
- `source_id: str`
- `provider: str`
- `action_tree_node: str | None`
- `artifact_id: str | None`
- `sequence: int | None`
- `metadata: Mapping[str, Any]`
- `schema_version: str`


### `class ProviderAblationRunner`

Run identical fixtures across named provider/mode adapter variants.

- `__init__(self, adapters: 'Mapping[str, ImageAdapter]') -> 'None'`
- `run(self, fixtures: 'Iterable[PerceptionFixture]') -> 'Mapping[str, tuple[PerceptionBenchmarkResult, ...]]'`

### `class ProviderCapabilities`

Fields:
- `mode: ExecutionMode`
- `candidate_parts: tuple[str, ...]`
- `semantic_record_families: tuple[str, ...]`
- `dynamic_candidate_parts: bool`

- `supports_candidate_part(self, name: 'str') -> 'bool'`

### `class PythonProvider(ArtifactProvider)`

One stable contract with backend-specific implementations.

- `__init__(self, resolvers: 'Mapping[str, Callable[[CandidateObject], Any]]') -> 'None'`
- `capabilities(self) -> 'ProviderCapabilities'`
- `get_candidate_part(self, candidate: 'CandidateObject', name: 'str') -> 'NormalizedResult'`

### `class RasterPerturbationGenerator`

Create deterministic modest-noise and partial-occlusion fixtures.

- `__init__(self, seed: 'int' = 0) -> 'None'`
- `noise(self, image: 'Image.Image', probability: 'float' = 0.05) -> 'Image.Image'`
- `occlude(self, image: 'Image.Image', bounds: 'tuple[int, int, int, int]') -> 'Image.Image'`
- `partial_occlusion_dataset(self, fixture_id: 'str', image: 'Image.Image', *, expected_count: 'int', occlusion: 'tuple[int, int, int, int]') -> 'tuple[PerceptionFixture, ...]'`

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


### `class RecognitionBenchmarkResult`

Fields:
- `fixture_id: str`
- `scope: str`
- `accounts: tuple[RecognitionAccount, ...]`


### `class RecognitionBenchmarkRunner`

Exercise the real matcher and retain outcomes for every rival proposal.

- `__init__(self, matcher: 'InstanceMatcher | None' = None) -> 'None'`
- `accounts(results: 'tuple[RecognitionBenchmarkResult, ...]', *, scope: 'str | None' = None) -> 'tuple[RecognitionAccount, ...]'`
- `run(self, fixtures: 'tuple[RecognitionFixture, ...]') -> 'tuple[RecognitionBenchmarkResult, ...]'`

### `class RecognitionCalibrationPolicy`

Serializable monotone mapping learned from authoritative outcomes.

Fields:
- `scope: str`
- `sample_count: int`
- `points: tuple[CalibrationPoint, ...]`
- `method: str`

- `calibrate(self, confidence: 'float') -> 'float'`
- `to_dict(self) -> 'dict[str, Any]'`

### `class RecognitionCalibrationReport`

Fields:
- `scope: str`
- `sample_count: int`
- `brier_score: float | None`
- `bins: tuple[ReliabilityBin, ...]`


### `class RecognitionCalibrator`

Measure pre-decision confidence against later authority outcomes.

- `calibrated_report(self, accounts: 'Iterable[RecognitionAccount]', policy: 'RecognitionCalibrationPolicy', *, bin_count: 'int' = 10) -> 'RecognitionCalibrationReport'`
- `fit(self, accounts: 'Iterable[RecognitionAccount]', *, scope: 'str') -> 'RecognitionCalibrationPolicy'` — Fit a deterministic pool-adjacent-violators isotonic policy.
- `report(self, accounts: 'Iterable[RecognitionAccount]', *, scope: 'str' = 'all', bin_count: 'int' = 10) -> 'RecognitionCalibrationReport'`

### `class RecognitionFixture`

One authority-labeled candidate and its complete identity rival set.

Fields:
- `fixture_id: str`
- `scope: str`
- `current: InstanceParameters`
- `stored: Mapping[str, InstanceParameters]`
- `accepted_identity_id: str | None`


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

### `class ReliabilityBin`

Fields:
- `lower: float`
- `upper: float`
- `count: int`
- `mean_confidence: float`
- `acceptance_rate: float`
- `brier_score: float`


### `class ResidualAnalyzer`

Separate unexplained proposal structure from recognized transformations.

- `__init__(self, gate: 'ResidualGate | None' = None) -> 'None'`
- `from_proposal(self, proposal: 'MatchProposal') -> 'tuple[ResidualCandidate, ...]'`

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

### `class ResidualGate`

Deterministic admission policy; thresholds remain configuration choices.

- `evaluate(self, residual: 'ResidualCandidate') -> 'ResidualDisposition'`

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


### `class RuleStore`

Exact-identity rule registry with caller-supplied domain execution.

- `__init__(self) -> 'None'`
- `applicable(self, rule_id: 'str', state: 'Any', checker: 'Callable[[TransitionRule, Any], bool]') -> 'bool'`
- `apply(self, rule_id: 'str', state: 'Any', executor: 'Callable[[TransitionRule, Any], Any]') -> 'Any'`
- `get(self, rule_id: 'str') -> 'TransitionRule'`
- `record_prediction_grade(self, rule_id: 'str', *, prediction_id: 'str', grade: 'float', supporting_evidence_ids: 'tuple[str, ...]' = (), contradicting_evidence_ids: 'tuple[str, ...]' = ()) -> 'TransitionRule'` — Refine one rule only from an independently graded prior prediction.
- `rules(self) -> 'tuple[TransitionRule, ...]'`
- `store(self, rule: 'TransitionRule') -> 'TransitionRule'`

### `class SemanticGridCaptureObserver`

External Arc3Runner observer that persists normalized Phase 2 records.

- `__init__(self, adapter: 'GridAdapter', grid_selector: 'Callable[[Any], Any]', symbolic_store: 'SymbolicStore | None' = None, turtle_form_factory: 'Callable[[str], GenerativeForm] | None' = None, identity_writer: 'SingleWriter | None' = None, learner_plugin: 'Any | None' = None) -> 'None'`
- `authorization_options(self) -> 'dict[str, tuple[str, ...]]'` — Return explicit friendly-identity choices for unresolved candidates.
- `authorize_candidate(self, *, candidate_id: 'str', selected_identity_id: 'str', decision_id: 'str', decision_source: 'str' = 'explicit_registry_selection') -> 'RecognitionAccount'` — Accept one pending proposal through the single identity writer.
- `before_action(self, *, runner: 'Any', store: 'Any', node: 'Any', action: 'str', data: 'Mapping[str, Any]') -> 'None'` — Record a learned-rule prediction before Arc3Runner observes the outcome.
- `on_state_captured(self, *, runner: 'Any', store: 'Any', node: 'Any', previous_node: 'Any', action: 'str | None', data: 'Mapping[str, Any]') -> 'None'`
- `reject_candidate(self, *, candidate_id: 'str', selected_identity_id: 'str', decision_id: 'str', decision_source: 'str' = 'explicit_registry_rejection') -> 'RecognitionAccount'` — Reject one pending friendly-identity proposal without calibrating it.

### `class SemanticIdentityCatalog`

Portable durable identities for explicit reuse across examples.

Fields:
- `entries: tuple[IdentityCatalogEntry, ...]`
- `source: str`
- `schema_version: str`

- `import_into(self, store: 'SymbolicStore', *, writer: 'SingleWriter | None' = None) -> 'tuple[EncounterRecord, ...]'`
- `install_registry(self, action_tree_store: 'Any') -> 'Mapping[str, str]'` — Merge exact exported friendly facts into another level registry.
- `to_json(self) -> 'str'`

### `class SemanticRecordCodec`

Decode exact JSON artifacts emitted by the semantic capture observer.

- `decode(record_type: 'str', value: 'Mapping[str, Any]') -> 'Any'`
- `decode_namespace(namespace: 'str', value: 'Mapping[str, Any]') -> 'Any'`

### `class SemanticStoreBackend(Protocol)`

Minimal exact-record boundary implemented by Prolog or AtomSpace stores.

- `__init__(self, *args, **kwargs)`
- `get(self, namespace: 'str', record_id: 'str') -> 'Any | None'`
- `values(self, namespace: 'str') -> 'tuple[Any, ...]'`
- `write_once(self, namespace: 'str', record_id: 'str', value: 'Any') -> 'Any'`

### `class SimpleVideoAdapter(PerceptionAdapter)`

Adapt an ordered iterable of decoded frames through an ImageAdapter.

- `__init__(self, image_adapter: 'ImageAdapter') -> 'None'`
- `normalize(self, *, observation_id: 'str', frames: 'Iterable[Any]', action_tree_node: 'str', artifact_uri: 'str') -> 'tuple[MediaPerceptionBatch, ...]'`
- `propose_candidates(self, observation: 'Any') -> 'Iterable[CandidateObject]'`

### `class SingleWriter`

Only mutation path for committed atoms and their evidence.

- `__init__(self, memory: 'SymbolicMemory', checkpoint_sink: 'Callable[[IdentityMemoryCheckpoint], Any] | None' = None) -> 'None'`
- `accrue_evidence(self, handle: 'str', confidence: 'float', evidence: 'str') -> 'CommittedAtom'` — Compatibility path for legacy callers with pre-calibrated evidence.
- `apply_evidence(self, handle: 'str', evidence: 'EvidenceRecord') -> 'CommittedAtom'` — Derive calibrated confidence from attributable signed evidence.
- `commit(self, atom: 'CommittedAtom') -> 'CommittedAtom'`
- `commit_residual(self, residual: 'ResidualCandidate', atom: 'CommittedAtom', gate: 'ResidualGate') -> 'CommittedAtom'` — Commit only a residual that the configured gate admits.
- `demote(self, handle: 'str', reason: 'str', *, checkpoint: 'bool' = True) -> 'CommittedAtom'`
- `merge_identities(self, decision: 'MergeDecision', resulting_atom: 'CommittedAtom') -> 'CommittedAtom'`
- `reverse_identity_decision(self, decision_id: 'str', reason: 'str') -> 'None'`
- `split_identity(self, decision: 'SplitDecision', resulting_atoms: 'tuple[CommittedAtom, ...]') -> 'tuple[CommittedAtom, ...]'`
- `tombstone(self, handle: 'str', reason: 'str') -> 'CommittedAtom'`

### `class SplitDecision`

Fields:
- `decision_id: str`
- `source_identity_id: str`
- `resulting_identity_ids: tuple[str, ...]`
- `status: IdentityDecision`
- `evidence_ids: tuple[str, ...]`
- `provenance: tuple[ProvenanceRef, ...]`
- `schema_version: str`


### `class SpriteAdapter(ImageAdapter)`

Image adapter preconfigured for transparent sprite sheets.

- `__init__(self, provider: 'Any', extractor: 'Any | None' = None) -> 'None'`
- `candidate_detail(self, candidate_id: 'str') -> 'Mapping[str, Any]'`
- `normalize(self, *, observation_id: 'str', image: 'Any', action_tree_node: 'str', artifact_uri: 'str', sequence: 'int | None' = None) -> 'MediaPerceptionBatch'`
- `propose_candidates(self, observation: 'Any') -> 'Iterable[CandidateObject]'`

### `class StructuralCorrespondenceInferer`

Infer only exact one-to-one, split, or merge cell-set correspondences.

- `infer(self, previous: 'Mapping[str, Any]', current: 'Mapping[str, Any]') -> 'dict[str, tuple[str, ...]]'`

### `class SymbolicMemory`

Small in-memory reference store; durable stores may implement this API.

- `__init__(self) -> 'None'`
- `all_atoms(self) -> 'tuple[CommittedAtom, ...]'`
- `checkpoints(self) -> 'tuple[IdentityMemoryCheckpoint, ...]'`
- `confidence_history(self, handle: 'str') -> 'tuple[ConfidenceHistoryRecord, ...]'`
- `events(self) -> 'tuple[dict[str, Any], ...]'`
- `evidence_for(self, handle: 'str') -> 'tuple[EvidenceRecord, ...]'`
- `get(self, handle: 'str') -> 'CommittedAtom | None'`
- `identity_decision(self, decision_id: 'str') -> 'MergeDecision | SplitDecision | None'`
- `restore(self, checkpoint: 'IdentityMemoryCheckpoint') -> "'SymbolicMemory'"` — Restore an exact writer state from one durable checkpoint.

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

### `class TranscriptComparison`

Fields:
- `expected_events: int`
- `actual_events: int`
- `exact_matches: int`
- `ordered_prefix_matches: int`
- `event_recall: float`
- `exact: bool`


### `class TranscriptScorer`

Compare structured transcripts without confusing order with membership.

- `compare(self, expected: 'Iterable[Any]', actual: 'Iterable[Any]') -> 'TranscriptComparison'`

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


### `class TurtleReconstructionEvidenceBuilder`

Represent an exact or residual Turtle reconstruction fit as signed evidence.

- `build(self, *, identity_id: 'str', fit: 'FitResult', source: 'ProvenanceRef', artifact_id: 'str | None' = None, created_sequence: 'int' = 0) -> 'EvidenceRecord'`

### `class UnsupportedProviderCapability(KeyError)`

Machine-readable failure for a capability the provider does not expose.

- `__init__(self, *, mode: 'ExecutionMode', capability_kind: 'str', requested: 'str', available: 'tuple[str, ...]') -> 'None'`
- `as_dict(self) -> 'dict[str, Any]'`

## Functions

### `build_acceptance_report(*, object_memory: 'Mapping[str, Any]', environment_progression: 'Mapping[str, Any]', phase3_learning: 'Mapping[str, Any]', test_result: 'str', commit: 'str') -> 'AcceptanceReport'`

### `deterministic_identifier(record_type: 'str', identity: 'Mapping[str, Any]') -> 'str'`

Create a reproducible identifier from the record's immutable identity.

### `environment_progression_fixtures() -> 'EnvironmentProgressionFixtures'`

### `fixed_camera_physics_fixtures() -> 'tuple[PerceptionFixture, ...]'`

### `normalize_grid_structure(item: 'Mapping[str, Any]', role_provider: 'Any | None' = None) -> 'Mapping[str, Any]'`

Normalize extractor-specific grid structure into one semantic contract.

### `normalize_image_structure(item: 'Mapping[str, Any]', role_provider: 'Any | None' = None) -> 'Mapping[str, Any]'`

Preserve provider raster semantics in the shared normalized contract.

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

### `rendered_arcade_fixtures() -> 'tuple[PerceptionFixture, ...]'`

### `standard_semantic_grid_observer(*, learner_plugin: 'Any | None' = None) -> "'SemanticGridCaptureObserver'"`

Compose the canonical live grid observer without coupling it to Phase 1.

### `top_down_manipulation_fixtures() -> 'tuple[PerceptionFixture, ...]'`

### `write_acceptance_report(report: 'AcceptanceReport', output_root: 'Path') -> 'tuple[Path, Path]'`
