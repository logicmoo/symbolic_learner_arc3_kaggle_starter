> [← Project README](../../README.md)

# Table of Contents

* [omega\_vision](#omega_vision)
* [omega\_vision.acceptance](#omega_vision.acceptance)
* [omega\_vision.adapters](#omega_vision.adapters)
  * [LearnedPartRoleProvider](#omega_vision.adapters.LearnedPartRoleProvider)
  * [normalize\_grid\_structure](#omega_vision.adapters.normalize_grid_structure)
  * [normalize\_image\_structure](#omega_vision.adapters.normalize_image_structure)
  * [PerceptionAdapter](#omega_vision.adapters.PerceptionAdapter)
  * [GridAdapter](#omega_vision.adapters.GridAdapter)
    * [normalize](#omega_vision.adapters.GridAdapter.normalize)
  * [ImageAdapter](#omega_vision.adapters.ImageAdapter)
  * [SimpleVideoAdapter](#omega_vision.adapters.SimpleVideoAdapter)
* [omega\_vision.benchmark](#omega_vision.benchmark)
  * [RasterPerturbationGenerator](#omega_vision.benchmark.RasterPerturbationGenerator)
  * [PerceptionBenchmarkRunner](#omega_vision.benchmark.PerceptionBenchmarkRunner)
  * [ProviderAblationRunner](#omega_vision.benchmark.ProviderAblationRunner)
* [omega\_vision.calibration](#omega_vision.calibration)
  * [RecognitionCalibrationPolicy](#omega_vision.calibration.RecognitionCalibrationPolicy)
  * [RecognitionCalibrator](#omega_vision.calibration.RecognitionCalibrator)
    * [fit](#omega_vision.calibration.RecognitionCalibrator.fit)
* [omega\_vision.capture](#omega_vision.capture)
  * [standard\_semantic\_grid\_observer](#omega_vision.capture.standard_semantic_grid_observer)
  * [SemanticGridCaptureObserver](#omega_vision.capture.SemanticGridCaptureObserver)
    * [authorization\_options](#omega_vision.capture.SemanticGridCaptureObserver.authorization_options)
    * [authorize\_candidate](#omega_vision.capture.SemanticGridCaptureObserver.authorize_candidate)
    * [reject\_candidate](#omega_vision.capture.SemanticGridCaptureObserver.reject_candidate)
    * [before\_action](#omega_vision.capture.SemanticGridCaptureObserver.before_action)
* [omega\_vision.catalog](#omega_vision.catalog)
  * [SemanticIdentityCatalog](#omega_vision.catalog.SemanticIdentityCatalog)
    * [install\_registry](#omega_vision.catalog.SemanticIdentityCatalog.install_registry)
* [omega\_vision.environment\_fixtures](#omega_vision.environment_fixtures)
* [omega\_vision.forms](#omega_vision.forms)
  * [AbstractGenerativeForm](#omega_vision.forms.AbstractGenerativeForm)
  * [GenerativeForm](#omega_vision.forms.GenerativeForm)
* [omega\_vision.integration](#omega_vision.integration)
  * [GameObjectLearnerSchema](#omega_vision.integration.GameObjectLearnerSchema)
  * [Phase2LearnerPayloadBuilder](#omega_vision.integration.Phase2LearnerPayloadBuilder)
  * [phase2\_transition\_analyzer](#omega_vision.integration.phase2_transition_analyzer)
  * [phase2\_transformation\_learner](#omega_vision.integration.phase2_transformation_learner)
  * [phase2\_rule\_inducer](#omega_vision.integration.phase2_rule_inducer)
  * [phase2\_rule\_ranker](#omega_vision.integration.phase2_rule_ranker)
  * [phase2\_rule\_executor](#omega_vision.integration.phase2_rule_executor)
  * [GameObjectLearnerPlugin](#omega_vision.integration.GameObjectLearnerPlugin)
    * [consume](#omega_vision.integration.GameObjectLearnerPlugin.consume)
  * [PipelineGameObjectLearnerPlugin](#omega_vision.integration.PipelineGameObjectLearnerPlugin)
* [omega\_vision.learning](#omega_vision.learning)
  * [TransitionAnalyzer](#omega_vision.learning.TransitionAnalyzer)
  * [TransformationLearner](#omega_vision.learning.TransformationLearner)
  * [RuleInducer](#omega_vision.learning.RuleInducer)
  * [RuleExecutor](#omega_vision.learning.RuleExecutor)
  * [OutcomeChannel](#omega_vision.learning.OutcomeChannel)
  * [GameLearningPipeline](#omega_vision.learning.GameLearningPipeline)
    * [recommend\_action](#omega_vision.learning.GameLearningPipeline.recommend_action)
* [omega\_vision.memory](#omega_vision.memory)
  * [EncounterLog](#omega_vision.memory.EncounterLog)
  * [ResidualGate](#omega_vision.memory.ResidualGate)
  * [SymbolicMemory](#omega_vision.memory.SymbolicMemory)
    * [restore](#omega_vision.memory.SymbolicMemory.restore)
  * [SingleWriter](#omega_vision.memory.SingleWriter)
    * [commit\_residual](#omega_vision.memory.SingleWriter.commit_residual)
    * [accrue\_evidence](#omega_vision.memory.SingleWriter.accrue_evidence)
    * [apply\_evidence](#omega_vision.memory.SingleWriter.apply_evidence)
* [omega\_vision.models](#omega_vision.models)
  * [deterministic\_identifier](#omega_vision.models.deterministic_identifier)
  * [IdentityMemoryCheckpoint](#omega_vision.models.IdentityMemoryCheckpoint)
    * [as\_compaction\_root](#omega_vision.models.IdentityMemoryCheckpoint.as_compaction_root)
  * [NormalizedResult](#omega_vision.models.NormalizedResult)
  * [PredictionGradeRecord](#omega_vision.models.PredictionGradeRecord)
* [omega\_vision.prediction](#omega_vision.prediction)
  * [RuleStore](#omega_vision.prediction.RuleStore)
    * [record\_prediction\_grade](#omega_vision.prediction.RuleStore.record_prediction_grade)
  * [PredictionLedger](#omega_vision.prediction.PredictionLedger)
* [omega\_vision.providers](#omega_vision.providers)
  * [UnsupportedProviderCapability](#omega_vision.providers.UnsupportedProviderCapability)
  * [ArtifactProvider](#omega_vision.providers.ArtifactProvider)
  * [GptArtifactProvider](#omega_vision.providers.GptArtifactProvider)
  * [PrologProvider](#omega_vision.providers.PrologProvider)
    * [get\_semantic\_records](#omega_vision.providers.PrologProvider.get_semantic_records)
* [omega\_vision.recognition](#omega_vision.recognition)
  * [PartialVisibilityCompletion](#omega_vision.recognition.PartialVisibilityCompletion)
  * [InstanceMatcher](#omega_vision.recognition.InstanceMatcher)
  * [RecognitionSession](#omega_vision.recognition.RecognitionSession)
    * [complete\_partial](#omega_vision.recognition.RecognitionSession.complete_partial)
  * [CorrespondenceEvidenceBuilder](#omega_vision.recognition.CorrespondenceEvidenceBuilder)
  * [EncounterChangeSession](#omega_vision.recognition.EncounterChangeSession)
  * [StructuralCorrespondenceInferer](#omega_vision.recognition.StructuralCorrespondenceInferer)
  * [ResidualAnalyzer](#omega_vision.recognition.ResidualAnalyzer)
  * [TurtleReconstructionEvidenceBuilder](#omega_vision.recognition.TurtleReconstructionEvidenceBuilder)
  * [ChangeDetector](#omega_vision.recognition.ChangeDetector)
  * [RegistryCorrespondenceAuthority](#omega_vision.recognition.RegistryCorrespondenceAuthority)
* [omega\_vision.recognition\_benchmark](#omega_vision.recognition_benchmark)
  * [RecognitionFixture](#omega_vision.recognition_benchmark.RecognitionFixture)
  * [RecognitionBenchmarkRunner](#omega_vision.recognition_benchmark.RecognitionBenchmarkRunner)
* [omega\_vision.replay](#omega_vision.replay)
  * [SemanticRecordCodec](#omega_vision.replay.SemanticRecordCodec)
  * [PrologSemanticBackend](#omega_vision.replay.PrologSemanticBackend)
  * [AtomSpaceTransport](#omega_vision.replay.AtomSpaceTransport)
  * [MettaFileAtomSpaceTransport](#omega_vision.replay.MettaFileAtomSpaceTransport)
  * [AtomSpaceSemanticBackend](#omega_vision.replay.AtomSpaceSemanticBackend)
  * [ActionTreeSemanticReplay](#omega_vision.replay.ActionTreeSemanticReplay)
* [omega\_vision.sprite](#omega_vision.sprite)
  * [AlphaContourProvider](#omega_vision.sprite.AlphaContourProvider)
  * [SpriteAdapter](#omega_vision.sprite.SpriteAdapter)
* [omega\_vision.store](#omega_vision.store)
  * [SemanticStoreBackend](#omega_vision.store.SemanticStoreBackend)
  * [InMemorySemanticBackend](#omega_vision.store.InMemorySemanticBackend)
  * [ArtifactIndex](#omega_vision.store.ArtifactIndex)
  * [SymbolicStore](#omega_vision.store.SymbolicStore)
    * [restore\_identity\_memory](#omega_vision.store.SymbolicStore.restore_identity_memory)
    * [compacted\_snapshot](#omega_vision.store.SymbolicStore.compacted_snapshot)
    * [snapshot](#omega_vision.store.SymbolicStore.snapshot)
    * [replay](#omega_vision.store.SymbolicStore.replay)
    * [hydrate](#omega_vision.store.SymbolicStore.hydrate)
* [omega\_vision.transcript](#omega_vision.transcript)
  * [TranscriptScorer](#omega_vision.transcript.TranscriptScorer)

<a id="omega_vision"></a>

# omega\_vision

Shared object-memory contracts for PROLOG, GPT, and PYTHON backends.

The package supplements the existing ARC3 debugger. It does not replace
Arc3Runner, ActionTreeStore, GptArcAnalyzer, SWIPrologBridge, or the generated
Prolog artifact contracts.

<a id="omega_vision.acceptance"></a>

# omega\_vision.acceptance

<a id="omega_vision.adapters"></a>

# omega\_vision.adapters

<a id="omega_vision.adapters.LearnedPartRoleProvider"></a>

## LearnedPartRoleProvider Objects

```python
class LearnedPartRoleProvider()
```

Infer semantic component roles from labeled structural examples.

The provider deliberately learns only the label boundary. Component
extraction and role-reference validation remain deterministic adapter
responsibilities.

<a id="omega_vision.adapters.normalize_grid_structure"></a>

#### normalize\_grid\_structure

```python
def normalize_grid_structure(
        item: Mapping[str, Any],
        role_provider: Any | None = None) -> Mapping[str, Any]
```

Normalize extractor-specific grid structure into one semantic contract.

<a id="omega_vision.adapters.normalize_image_structure"></a>

#### normalize\_image\_structure

```python
def normalize_image_structure(
        item: Mapping[str, Any],
        role_provider: Any | None = None) -> Mapping[str, Any]
```

Preserve provider raster semantics in the shared normalized contract.

<a id="omega_vision.adapters.PerceptionAdapter"></a>

## PerceptionAdapter Objects

```python
class PerceptionAdapter(ABC)
```

Domain seam; core code must not import ARC or raster assumptions.

<a id="omega_vision.adapters.GridAdapter"></a>

## GridAdapter Objects

```python
class GridAdapter(PerceptionAdapter)
```

Thin adapter around an existing grid object extractor.

<a id="omega_vision.adapters.GridAdapter.normalize"></a>

#### normalize

```python
def normalize(*, observation_id: str, grid: Any, action_tree_node: str,
              artifact_uri: str) -> GridPerceptionBatch
```

Wrap the established extractor result in Phase 2 contracts.

<a id="omega_vision.adapters.ImageAdapter"></a>

## ImageAdapter Objects

```python
class ImageAdapter(PerceptionAdapter)
```

Normalize raster extractor output without prescribing segmentation.

<a id="omega_vision.adapters.SimpleVideoAdapter"></a>

## SimpleVideoAdapter Objects

```python
class SimpleVideoAdapter(PerceptionAdapter)
```

Adapt an ordered iterable of decoded frames through an ImageAdapter.

<a id="omega_vision.benchmark"></a>

# omega\_vision.benchmark

<a id="omega_vision.benchmark.RasterPerturbationGenerator"></a>

## RasterPerturbationGenerator Objects

```python
class RasterPerturbationGenerator()
```

Create deterministic modest-noise and partial-occlusion fixtures.

<a id="omega_vision.benchmark.PerceptionBenchmarkRunner"></a>

## PerceptionBenchmarkRunner Objects

```python
class PerceptionBenchmarkRunner()
```

Evaluate any normalized image adapter against count-labeled fixtures.

<a id="omega_vision.benchmark.ProviderAblationRunner"></a>

## ProviderAblationRunner Objects

```python
class ProviderAblationRunner()
```

Run identical fixtures across named provider/mode adapter variants.

<a id="omega_vision.calibration"></a>

# omega\_vision.calibration

<a id="omega_vision.calibration.RecognitionCalibrationPolicy"></a>

## RecognitionCalibrationPolicy Objects

```python
@dataclass(frozen=True)
class RecognitionCalibrationPolicy()
```

Serializable monotone mapping learned from authoritative outcomes.

<a id="omega_vision.calibration.RecognitionCalibrator"></a>

## RecognitionCalibrator Objects

```python
class RecognitionCalibrator()
```

Measure pre-decision confidence against later authority outcomes.

<a id="omega_vision.calibration.RecognitionCalibrator.fit"></a>

#### fit

```python
def fit(accounts: Iterable[RecognitionAccount], *,
        scope: str) -> RecognitionCalibrationPolicy
```

Fit a deterministic pool-adjacent-violators isotonic policy.

<a id="omega_vision.capture"></a>

# omega\_vision.capture

<a id="omega_vision.capture.standard_semantic_grid_observer"></a>

#### standard\_semantic\_grid\_observer

```python
def standard_semantic_grid_observer(*,
                                    learner_plugin: Any | None = None
                                    ) -> "SemanticGridCaptureObserver"
```

Compose the canonical live grid observer without coupling it to Phase 1.

<a id="omega_vision.capture.SemanticGridCaptureObserver"></a>

## SemanticGridCaptureObserver Objects

```python
class SemanticGridCaptureObserver()
```

External Arc3Runner observer that persists normalized Phase 2 records.

<a id="omega_vision.capture.SemanticGridCaptureObserver.authorization_options"></a>

#### authorization\_options

```python
def authorization_options() -> dict[str, tuple[str, ...]]
```

Return explicit friendly-identity choices for unresolved candidates.

<a id="omega_vision.capture.SemanticGridCaptureObserver.authorize_candidate"></a>

#### authorize\_candidate

```python
def authorize_candidate(
    *,
    candidate_id: str,
    selected_identity_id: str,
    decision_id: str,
    decision_source: str = "explicit_registry_selection"
) -> RecognitionAccount
```

Accept one pending proposal through the single identity writer.

<a id="omega_vision.capture.SemanticGridCaptureObserver.reject_candidate"></a>

#### reject\_candidate

```python
def reject_candidate(
    *,
    candidate_id: str,
    selected_identity_id: str,
    decision_id: str,
    decision_source: str = "explicit_registry_rejection"
) -> RecognitionAccount
```

Reject one pending friendly-identity proposal without calibrating it.

<a id="omega_vision.capture.SemanticGridCaptureObserver.before_action"></a>

#### before\_action

```python
def before_action(*, runner: Any, store: Any, node: Any, action: str,
                  data: Mapping[str, Any]) -> None
```

Record a learned-rule prediction before Arc3Runner observes the outcome.

<a id="omega_vision.catalog"></a>

# omega\_vision.catalog

<a id="omega_vision.catalog.SemanticIdentityCatalog"></a>

## SemanticIdentityCatalog Objects

```python
@dataclass(frozen=True)
class SemanticIdentityCatalog()
```

Portable durable identities for explicit reuse across examples.

<a id="omega_vision.catalog.SemanticIdentityCatalog.install_registry"></a>

#### install\_registry

```python
def install_registry(action_tree_store: Any) -> Mapping[str, str]
```

Merge exact exported friendly facts into another level registry.

<a id="omega_vision.environment_fixtures"></a>

# omega\_vision.environment\_fixtures

<a id="omega_vision.forms"></a>

# omega\_vision.forms

<a id="omega_vision.forms.AbstractGenerativeForm"></a>

## AbstractGenerativeForm Objects

```python
class AbstractGenerativeForm(ABC)
```

Abstract typed contract for a generative form (Turtle/LOGO and later raster).

<a id="omega_vision.forms.GenerativeForm"></a>

## GenerativeForm Objects

```python
class GenerativeForm(AbstractGenerativeForm)
```

Canonical Turtle/LOGO generative form over the existing DSL program.

<a id="omega_vision.integration"></a>

# omega\_vision.integration

<a id="omega_vision.integration.GameObjectLearnerSchema"></a>

## GameObjectLearnerSchema Objects

```python
class GameObjectLearnerSchema()
```

Small stable contract; providers may add metadata without changing it.

<a id="omega_vision.integration.Phase2LearnerPayloadBuilder"></a>

## Phase2LearnerPayloadBuilder Objects

```python
class Phase2LearnerPayloadBuilder()
```

Build the frozen learner handoff exclusively from exact Phase 2 records.

<a id="omega_vision.integration.phase2_transition_analyzer"></a>

#### phase2\_transition\_analyzer

```python
def phase2_transition_analyzer() -> TransitionAnalyzer
```

Analyze one real handoff using the direct Phase 2 change records.

<a id="omega_vision.integration.phase2_transformation_learner"></a>

#### phase2\_transformation\_learner

```python
def phase2_transformation_learner() -> TransformationLearner
```

Convert direct changes into evidence-linked competing interpretations.

<a id="omega_vision.integration.phase2_rule_inducer"></a>

#### phase2\_rule\_inducer

```python
def phase2_rule_inducer() -> RuleInducer
```

Induce inspectable rival rules without treating one observation as proof.

<a id="omega_vision.integration.phase2_rule_ranker"></a>

#### phase2\_rule\_ranker

```python
def phase2_rule_ranker() -> RuleRanker
```

Rank by verified history first, then evidence and explicit simplicity.

<a id="omega_vision.integration.phase2_rule_executor"></a>

#### phase2\_rule\_executor

```python
def phase2_rule_executor(store: RuleStore,
                         action_or_event: Any) -> RuleExecutor
```

Apply an induced object transformation relative to a new object state.

Numeric ``from``/``to`` observations describe a delta, not an absolute
destination.  This lets a translation learned at one location operate on
an unseen object at another location.  Non-numeric changes use their
observed ``to`` value.  The caller still has to supply the action/event
that selects the rule; execution never silently ignores that condition.

<a id="omega_vision.integration.GameObjectLearnerPlugin"></a>

## GameObjectLearnerPlugin Objects

```python
class GameObjectLearnerPlugin(ABC)
```

Phase 3 boundary; implementations consume normalized Phase 2 results.

<a id="omega_vision.integration.GameObjectLearnerPlugin.consume"></a>

#### consume

```python
def consume(payload: GameObjectLearnerPayload) -> NormalizedResult
```

Backward-compatible alias for earlier single-state plugins.

<a id="omega_vision.integration.PipelineGameObjectLearnerPlugin"></a>

## PipelineGameObjectLearnerPlugin Objects

```python
class PipelineGameObjectLearnerPlugin(GameObjectLearnerPlugin)
```

Runnable integration of validated payloads with GameLearningPipeline.

<a id="omega_vision.learning"></a>

# omega\_vision.learning

<a id="omega_vision.learning.TransitionAnalyzer"></a>

## TransitionAnalyzer Objects

```python
class TransitionAnalyzer()
```

Facade over a deterministic, Prolog, or GPT-backed transition analyzer.

<a id="omega_vision.learning.TransformationLearner"></a>

## TransformationLearner Objects

```python
class TransformationLearner()
```

Delegates candidate generation without fixing the learning algorithm.

<a id="omega_vision.learning.RuleInducer"></a>

## RuleInducer Objects

```python
class RuleInducer()
```

Converts transformation candidates into normalized TransitionRule records.

<a id="omega_vision.learning.RuleExecutor"></a>

## RuleExecutor Objects

```python
class RuleExecutor()
```

Applies stored rules through caller-supplied domain semantics.

<a id="omega_vision.learning.OutcomeChannel"></a>

## OutcomeChannel Objects

```python
class OutcomeChannel()
```

Independent observation channel used to grade a prior prediction.

<a id="omega_vision.learning.GameLearningPipeline"></a>

## GameLearningPipeline Objects

```python
class GameLearningPipeline()
```

Connected Phase 3 flow; algorithms remain replaceable providers.

<a id="omega_vision.learning.GameLearningPipeline.recommend_action"></a>

#### recommend\_action

```python
def recommend_action(
        *,
        source_state_id: str,
        attempted_action: Any,
        created_sequence: int,
        prediction_id: str | None = None) -> ActionRecommendation | None
```

Rank all learned actions independently of the action being attempted.

<a id="omega_vision.memory"></a>

# omega\_vision.memory

<a id="omega_vision.memory.EncounterLog"></a>

## EncounterLog Objects

```python
class EncounterLog()
```

Append-only semantic encounters with deterministic, idempotent replay.

Phase 1 remains the owner of action-tree history. This log only records the
Phase 2 semantic encounters linked to those immutable node references.

<a id="omega_vision.memory.ResidualGate"></a>

## ResidualGate Objects

```python
class ResidualGate()
```

Deterministic admission policy; thresholds remain configuration choices.

<a id="omega_vision.memory.SymbolicMemory"></a>

## SymbolicMemory Objects

```python
class SymbolicMemory()
```

Small in-memory reference store; durable stores may implement this API.

<a id="omega_vision.memory.SymbolicMemory.restore"></a>

#### restore

```python
def restore(checkpoint: IdentityMemoryCheckpoint) -> "SymbolicMemory"
```

Restore an exact writer state from one durable checkpoint.

<a id="omega_vision.memory.SingleWriter"></a>

## SingleWriter Objects

```python
class SingleWriter()
```

Only mutation path for committed atoms and their evidence.

<a id="omega_vision.memory.SingleWriter.commit_residual"></a>

#### commit\_residual

```python
def commit_residual(residual: ResidualCandidate, atom: CommittedAtom,
                    gate: ResidualGate) -> CommittedAtom
```

Commit only a residual that the configured gate admits.

<a id="omega_vision.memory.SingleWriter.accrue_evidence"></a>

#### accrue\_evidence

```python
def accrue_evidence(handle: str, confidence: float,
                    evidence: str) -> CommittedAtom
```

Compatibility path for legacy callers with pre-calibrated evidence.

<a id="omega_vision.memory.SingleWriter.apply_evidence"></a>

#### apply\_evidence

```python
def apply_evidence(handle: str, evidence: EvidenceRecord) -> CommittedAtom
```

Derive calibrated confidence from attributable signed evidence.

<a id="omega_vision.models"></a>

# omega\_vision.models

<a id="omega_vision.models.deterministic_identifier"></a>

#### deterministic\_identifier

```python
def deterministic_identifier(record_type: str, identity: Mapping[str,
                                                                 Any]) -> str
```

Create a reproducible identifier from the record's immutable identity.

<a id="omega_vision.models.IdentityMemoryCheckpoint"></a>

## IdentityMemoryCheckpoint Objects

```python
@dataclass(frozen=True)
class IdentityMemoryCheckpoint()
```

Append-only, self-contained identity-writer state for durable recovery.

<a id="omega_vision.models.IdentityMemoryCheckpoint.as_compaction_root"></a>

#### as\_compaction\_root

```python
def as_compaction_root() -> "IdentityMemoryCheckpoint"
```

Create a standalone root retaining the exact current writer state.

<a id="omega_vision.models.NormalizedResult"></a>

## NormalizedResult Objects

```python
@dataclass(frozen=True)
class NormalizedResult()
```

Backend-neutral return shape used by all providers.

<a id="omega_vision.models.PredictionGradeRecord"></a>

## PredictionGradeRecord Objects

```python
@dataclass(frozen=True)
class PredictionGradeRecord()
```

Immutable outcome and grade linked to an earlier prediction.

<a id="omega_vision.prediction"></a>

# omega\_vision.prediction

<a id="omega_vision.prediction.RuleStore"></a>

## RuleStore Objects

```python
class RuleStore()
```

Exact-identity rule registry with caller-supplied domain execution.

<a id="omega_vision.prediction.RuleStore.record_prediction_grade"></a>

#### record\_prediction\_grade

```python
def record_prediction_grade(
    rule_id: str,
    *,
    prediction_id: str,
    grade: float,
    supporting_evidence_ids: tuple[str, ...] = (),
    contradicting_evidence_ids: tuple[str, ...] = ()
) -> TransitionRule
```

Refine one rule only from an independently graded prior prediction.

<a id="omega_vision.prediction.PredictionLedger"></a>

## PredictionLedger Objects

```python
class PredictionLedger()
```

Append-only prediction records enforcing predict-before-check.

<a id="omega_vision.providers"></a>

# omega\_vision.providers

<a id="omega_vision.providers.UnsupportedProviderCapability"></a>

## UnsupportedProviderCapability Objects

```python
class UnsupportedProviderCapability(KeyError)
```

Machine-readable failure for a capability the provider does not expose.

<a id="omega_vision.providers.ArtifactProvider"></a>

## ArtifactProvider Objects

```python
class ArtifactProvider(ABC)
```

One stable contract with backend-specific implementations.

<a id="omega_vision.providers.GptArtifactProvider"></a>

## GptArtifactProvider Objects

```python
class GptArtifactProvider(ArtifactProvider)
```

Reads GPT-generated or cached artifacts; it does not emulate native analysis.

<a id="omega_vision.providers.PrologProvider"></a>

## PrologProvider Objects

```python
class PrologProvider(ArtifactProvider)
```

Delegates symbolic queries to SWI-Prolog through an injected query function.

<a id="omega_vision.providers.PrologProvider.get_semantic_records"></a>

#### get\_semantic\_records

```python
def get_semantic_records(
        name: str,
        filters: Mapping[str, Any] | None = None) -> NormalizedResult
```

Query one normalized semantic namespace through the Prolog adapter.

<a id="omega_vision.recognition"></a>

# omega\_vision.recognition

<a id="omega_vision.recognition.PartialVisibilityCompletion"></a>

## PartialVisibilityCompletion Objects

```python
@dataclass(frozen=True)
class PartialVisibilityCompletion()
```

A reconstructed instance that keeps inferred and observed data distinct.

<a id="omega_vision.recognition.InstanceMatcher"></a>

## InstanceMatcher Objects

```python
class InstanceMatcher()
```

Generate advisory correspondence proposals from normalized instances.

<a id="omega_vision.recognition.RecognitionSession"></a>

## RecognitionSession Objects

```python
class RecognitionSession()
```

Persist unresolved proposals between a candidate and known encounter histories.

<a id="omega_vision.recognition.RecognitionSession.complete_partial"></a>

#### complete\_partial

```python
def complete_partial(encounter_id: str,
                     stored_identity_id: str) -> PartialVisibilityCompletion
```

Complete an occluded encounter from one prior durable identity form.

<a id="omega_vision.recognition.CorrespondenceEvidenceBuilder"></a>

## CorrespondenceEvidenceBuilder Objects

```python
class CorrespondenceEvidenceBuilder()
```

Create attributable signed evidence from a proposal's property explanation.

<a id="omega_vision.recognition.EncounterChangeSession"></a>

## EncounterChangeSession Objects

```python
class EncounterChangeSession()
```

Persist correspondences, evidence, and changes across two observations.

<a id="omega_vision.recognition.StructuralCorrespondenceInferer"></a>

## StructuralCorrespondenceInferer Objects

```python
class StructuralCorrespondenceInferer()
```

Infer only exact one-to-one, split, or merge cell-set correspondences.

<a id="omega_vision.recognition.ResidualAnalyzer"></a>

## ResidualAnalyzer Objects

```python
class ResidualAnalyzer()
```

Separate unexplained proposal structure from recognized transformations.

<a id="omega_vision.recognition.TurtleReconstructionEvidenceBuilder"></a>

## TurtleReconstructionEvidenceBuilder Objects

```python
class TurtleReconstructionEvidenceBuilder()
```

Represent an exact or residual Turtle reconstruction fit as signed evidence.

<a id="omega_vision.recognition.ChangeDetector"></a>

## ChangeDetector Objects

```python
class ChangeDetector()
```

Classify resolved before/after correspondences into semantic changes.

<a id="omega_vision.recognition.RegistryCorrespondenceAuthority"></a>

## RegistryCorrespondenceAuthority Objects

```python
class RegistryCorrespondenceAuthority()
```

Apply an explicit registry selection only when attributable evidence exists.

<a id="omega_vision.recognition_benchmark"></a>

# omega\_vision.recognition\_benchmark

<a id="omega_vision.recognition_benchmark.RecognitionFixture"></a>

## RecognitionFixture Objects

```python
@dataclass(frozen=True)
class RecognitionFixture()
```

One authority-labeled candidate and its complete identity rival set.

<a id="omega_vision.recognition_benchmark.RecognitionBenchmarkRunner"></a>

## RecognitionBenchmarkRunner Objects

```python
class RecognitionBenchmarkRunner()
```

Exercise the real matcher and retain outcomes for every rival proposal.

<a id="omega_vision.replay"></a>

# omega\_vision.replay

<a id="omega_vision.replay.SemanticRecordCodec"></a>

## SemanticRecordCodec Objects

```python
class SemanticRecordCodec()
```

Decode exact JSON artifacts emitted by the semantic capture observer.

<a id="omega_vision.replay.PrologSemanticBackend"></a>

## PrologSemanticBackend Objects

```python
class PrologSemanticBackend()
```

Durable exact-record backend represented as inspectable SWI-Prolog facts.

<a id="omega_vision.replay.AtomSpaceTransport"></a>

## AtomSpaceTransport Objects

```python
class AtomSpaceTransport(Protocol)
```

Transport boundary for a MeTTa/OpenCog AtomSpace implementation.

<a id="omega_vision.replay.MettaFileAtomSpaceTransport"></a>

## MettaFileAtomSpaceTransport Objects

```python
class MettaFileAtomSpaceTransport()
```

Durable AtomSpace transport using an inspectable MeTTa expression file.

The transport deliberately knows nothing about Phase 2 record types. A future
Hyperon, OpenCog, or remote MeTTa transport only needs to provide the same two
operations; ``AtomSpaceSemanticBackend`` retains all identity and codec rules.

<a id="omega_vision.replay.AtomSpaceSemanticBackend"></a>

## AtomSpaceSemanticBackend Objects

```python
class AtomSpaceSemanticBackend()
```

Exact semantic records stored as queryable ``semantic_record`` Atoms.

<a id="omega_vision.replay.ActionTreeSemanticReplay"></a>

## ActionTreeSemanticReplay Objects

```python
class ActionTreeSemanticReplay()
```

Rebuild a semantic store from the exact records linked by an action tree.

<a id="omega_vision.sprite"></a>

# omega\_vision.sprite

<a id="omega_vision.sprite.AlphaContourProvider"></a>

## AlphaContourProvider Objects

```python
class AlphaContourProvider()
```

Extract transparent sprites and exact pixel-boundary vector contours.

<a id="omega_vision.sprite.SpriteAdapter"></a>

## SpriteAdapter Objects

```python
class SpriteAdapter(ImageAdapter)
```

Image adapter preconfigured for transparent sprite sheets.

<a id="omega_vision.store"></a>

# omega\_vision.store

<a id="omega_vision.store.SemanticStoreBackend"></a>

## SemanticStoreBackend Objects

```python
class SemanticStoreBackend(Protocol)
```

Minimal exact-record boundary implemented by Prolog or AtomSpace stores.

<a id="omega_vision.store.InMemorySemanticBackend"></a>

## InMemorySemanticBackend Objects

```python
class InMemorySemanticBackend()
```

Deterministic reference backend used by tests and local composition.

<a id="omega_vision.store.ArtifactIndex"></a>

## ArtifactIndex Objects

```python
class ArtifactIndex()
```

Exact artifact lookup by stable ID and semantic artifact type.

<a id="omega_vision.store.SymbolicStore"></a>

## SymbolicStore Objects

```python
class SymbolicStore()
```

Backend-neutral facade for exact Phase 2 semantic records.

Similarity indexes may propose identifiers to query here, but only exact
stable identifiers address or commit records through this boundary.

<a id="omega_vision.store.SymbolicStore.restore_identity_memory"></a>

#### restore\_identity\_memory

```python
def restore_identity_memory() -> "SymbolicMemory"
```

Restore the newest complete identity state stored by a SingleWriter.

<a id="omega_vision.store.SymbolicStore.compacted_snapshot"></a>

#### compacted\_snapshot

```python
def compacted_snapshot() -> dict[str, tuple[Any, ...]]
```

Export one self-contained checkpoint root plus all other semantic records.

<a id="omega_vision.store.SymbolicStore.snapshot"></a>

#### snapshot

```python
def snapshot() -> dict[str, tuple[Any, ...]]
```

Capture exact semantic records in deterministic replay order.

<a id="omega_vision.store.SymbolicStore.replay"></a>

#### replay

```python
def replay(snapshot: dict[str, tuple[Any, ...]]) -> "SymbolicStore"
```

Idempotently reconstruct this facade and its indexes from a snapshot.

<a id="omega_vision.store.SymbolicStore.hydrate"></a>

#### hydrate

```python
def hydrate() -> "SymbolicStore"
```

Populate facade indexes from records already present in the backend.

<a id="omega_vision.transcript"></a>

# omega\_vision.transcript

<a id="omega_vision.transcript.TranscriptScorer"></a>

## TranscriptScorer Objects

```python
class TranscriptScorer()
```

Compare structured transcripts without confusing order with membership.
