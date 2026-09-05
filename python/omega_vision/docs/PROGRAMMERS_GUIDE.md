# omega_vision — SoW Programmer's Guide

A class-and-method reference for **Statement of Work — Image Perception to
Recognizable Memory (v1.9)** (Sponsor: Khellar Crawford, SingularityNET PLN;
Contractor: Douglas Miles / logicmoo; Program: OmegaClaw / Hyperon–PLN).

`omega_vision` **lays out the SoW-named surface** exactly as Appendix A.2/A.3/A.4/A.6
prescribe. The implementations live elsewhere — chiefly in the
[`object_memory`](../../object_memory) package (the deterministic core, forms,
adapters, store, recognition, learning, and benchmarks). `omega_vision` re-exports
those under the SoW names and adds only:

- compact implementations for SoW-laid-out names that had no prior home
  (`ContourFillForm`, `GridIndividuator`, `RasterSegmenter`, the recall
  accelerators, and `GridMetrics` / `RasterMetrics`);
- importable **§16 future stubs** (`LayeredStrokeForm`, `PartGraph3DForm`,
  `Robot3DAdapter`, `RGBDObjectProposer`, `AnimeRegionProposer`,
  `SketchformerEmbedding`); and
- a **factory method or two** that belong to the SoW entry layer
  (`new_memory`, `new_writer`, `build_store`, `process_observation`).

## Importing

```python
import omega_vision as ov          # 56 SoW-named symbols
from omega_vision.forms import GenerativeForm, CellLogoForm, ContourFillForm
from omega_vision.core import SingleWriter, ResidualGate, PredictionLedger
from omega_vision.core.schemas import Observation, CommittedAtom, PredictionRecord
```

`omega_vision` lives at `python/omega_vision/`. It is importable wherever the repo
puts `python/` on the path — this is already configured for the test suite
(`pyproject.toml` → `[tool.pytest.ini_options] pythonpath = ["python", ...]`) and it
is registered in `[tool.setuptools] packages`, so `pip install -e .` exposes it to
every entry point.

## At a glance — SoW Appendix A.2 layout → implementation

| SoW file (A.2)              | `omega_vision` module                     | Backing implementation |
|-----------------------------|-------------------------------------------|------------------------|
| `core/schemas.py`           | `omega_vision.core.schemas`               | `object_memory.models` |
| `core/single_writer.py`     | `omega_vision.core.single_writer`         | `object_memory.memory.SingleWriter` |
| `core/atom_store.py`        | `omega_vision.core.atom_store`            | `object_memory.memory.SymbolicMemory`, `object_memory.store.SymbolicStore`/`ArtifactIndex` |
| `core/encounter_log.py`     | `omega_vision.core.encounter_log`         | `object_memory.memory.EncounterLog` |
| `core/residual_gate.py`     | `omega_vision.core.residual_gate`         | `object_memory.memory.ResidualGate`, `object_memory.recognition.ResidualAnalyzer` |
| `core/identity_merge.py`    | `omega_vision.core.identity_merge`        | `SingleWriter.merge_identities`/`split_identity`, `object_memory.recognition.RegistryCorrespondenceAuthority` |
| `core/prediction_ledger.py` | `omega_vision.core.prediction_ledger`     | `object_memory.prediction.PredictionLedger`, `RuleStore` |
| `core/rule_induction.py`    | `omega_vision.core.rule_induction`        | `object_memory.learning.*`, `GameLearningPipeline` |
| `core/evaluation.py`        | `omega_vision.core.evaluation`            | `object_memory.learning`/`calibration`/`acceptance`/`benchmark` + `GridMetrics`/`RasterMetrics` (new) |
| `forms/base.py`             | `omega_vision.forms.base`                 | `object_memory.forms.GenerativeForm`, `FitResult` |
| `forms/cell_logo.py`        | `omega_vision.forms.cell_logo`            | `object_memory.forms.CellLogoForm` |
| `forms/contour_fill.py`     | `omega_vision.forms.contour_fill`         | **new** `ContourFillForm` |
| `forms/layered_stroke.py`   | `omega_vision.forms.layered_stroke`       | future stub (§16) |
| `forms/part_graph_3d.py`    | `omega_vision.forms.part_graph_3d`        | future stub (§16) |
| `adapters/grid/`            | `omega_vision.adapters.grid`              | `object_memory.adapters.GridAdapter` + **new** `GridIndividuator` |
| `adapters/sprite/`          | `omega_vision.adapters.sprite`            | `object_memory.sprite.SpriteAdapter`, `object_memory.adapters.ImageAdapter` + **new** `RasterSegmenter` |
| `accelerators/vector_trace/`| `omega_vision.accelerators.vector_trace`  | **new** `VectorTraceIndex` |
| `accelerators/perceptual_hash/` | `omega_vision.accelerators.perceptual_hash` | **new** `PerceptualHash` |
| `accelerators/faiss_index/` | `omega_vision.accelerators.faiss_index`   | **new** `FaissIndex` (FAISS-compatible, dependency-free) |
| `environments/`             | `omega_vision.environments`               | `object_memory.environment_fixtures` |
| `configs/`                  | `omega_vision/configs/adapters.yaml`      | A.6 adapter registry |
| `tests/`                    | `tests/test_omega_vision.py`              | repo test suite |

## §3.1 / A.1 — the deterministic core invariants

| Invariant | Where it is carried |
|-----------|---------------------|
| 1. Single writer | `SingleWriter` (`.commit`, `.commit_residual`, `.accrue_evidence`, `.merge_identities`, `.split_identity`, `.tombstone`, `.demote`) |
| 2. Confidence floor (author at `c=0`) | `SingleWriter.commit` sets `CommittedAtom.confidence = 0.0`; rises only via `.accrue_evidence` / `.apply_evidence` |
| 3. Committed identity is exact | `CommittedAtom.handle`; `MatchProposal` only *proposes* |
| 4. No embedding-owned identity | `PerceptualHash` / `VectorTraceIndex` / `FaissIndex` are recall-only |
| 5. Explicit, measurable residual | `ResidualCandidate.residual_length`, `ResidualGate.evaluate`, `ResidualAnalyzer.from_proposal` |
| 6. Demote, never delete | `SingleWriter.demote`, `SingleWriter.tombstone` (provenance preserved) |
| 7. Predict before effect | `PredictionLedger.record` before `.grade`; `GameLearningPipeline.grade_prediction` |
| 8. Replayable | `EncounterLog.replay`/`.deterministic_hash`, `SymbolicStore.snapshot`/`.replay`, `ActionTreeSemanticReplay` |
| 9. Domain code behind adapters | `PerceptionAdapter` seam; `GridAdapter` / `SpriteAdapter` |

## §5 / A.3 — the `GenerativeForm` interface

`omega_vision.forms.GenerativeForm` (= `object_memory.forms.GenerativeForm`).

| SoW A.3 method | Implemented as |
|----------------|----------------|
| `canonicalize()` | `GenerativeForm.canonicalize() -> str` (grid: normalized LOGO; raster: normalized fill program) |
| `render(params)` | `GenerativeForm.render(params=None)` |
| `fit_instance(candidate)` | `GenerativeForm.fit_instance(candidate) -> FitResult(parameters, residual)` |
| `distance(other)` | `GenerativeForm.distance(other) -> float` |
| `residual(candidate, params)` | `ContourFillForm.residual(...)`; for grids the residual is `FitResult.residual` fed to `ResidualAnalyzer`/`ResidualGate` |
| `code_length(...)` | `ContourFillForm.code_length()`; `CellLogoForm.description_length()` |
| `complete(partial)` | `ContourFillForm.complete(...)`; occlusion completion also via `RecognitionSession.complete_partial` → `PartialVisibilityCompletion` (§8) |

Form languages: `CellLogoForm` (grid, A.6), `ContourFillForm` (raster, A.6/A.8),
`LayeredStrokeForm` / `PartGraph3DForm` (future, §16).

## A.4 — core data types (`omega_vision.core.schemas`)

All are dataclasses in `object_memory.models`. Key fields (⇒ marks a name that
differs from the SoW's illustrative field name):

- **Observation** — `observation_id`, `source_modality` ⇐ *stream_id/modality*,
  `artifacts` ⇐ *raw_artifact_refs*, `dimensions`, `coordinate_contract`,
  `candidate_object_ids`, `action_tree_node`, `provenance`.
- **CandidateObject** — `candidate_id`, `observation_id`, `domain`, `provider`,
  `region_ref`, `provenance`; `.part(name)`.
- **RecognitionAccount** — `account_id`, `candidate_id`,
  `stored_identity_id` ⇐ *matched_handle*, `matched_properties`,
  `changed_properties`, `allowed_transformations`, `turtle_reconstruction_fit`,
  `residual_score` ⇐ *residual_length*, `supporting_evidence_ids`,
  `contradicting_evidence_ids`, `rival_proposal_ids`, `calibrated_confidence`,
  `decision_*`. (The `residual_disposition` lives on `ResidualCandidate`.)
- **ResidualCandidate** — `residual_id`, `source_candidate_id` ⇐ *source_account_id*,
  `disposition` (`ResidualDisposition`), `residual_length` ⇐ *code_length*,
  `structured`, `recurrence_count`, `prediction_gain`, `provenance`.
- **CommittedAtom** — `handle`, `atom_type`, `payload`, `confidence` (floor `0.0`),
  `provenance`, `lifecycle_state` (`provisional|active|demoted|tombstoned`).
  (SoW's `truth_value.frequency`, `promotion_weight`, `author`, `validity_interval`,
  `semantic_links`, `embedding_refs`, `merge_history` are tracked by
  `EvidenceRecord`, `ConfidenceHistoryRecord`, and `MergeDecision`/`SplitDecision`.)
- **TransitionRule** — `rule_id`, `preconditions`, `action_or_event`,
  `predicted_effects`, `bootstrap_probability`/`calibrated_probability` ⇐ *truth_value*,
  `rival_rule_ids` ⇐ *rivals*, `prediction_attempts`/`prediction_successes`/
  `prediction_history`, `assumptions`, `critiques`, `provenance`.
- **PredictionRecord** — `prediction_id`, `rule_id` ⇐ *rule_ids*,
  `source_state_id` ⇐ *observation_id_before*, `predicted_effects`,
  `created_sequence` ⇐ *timestamp_committed*, `outcome_sequence` ⇐ *outcome_observation_id*,
  `outcome`, `grade`.

Enums: `ResidualDisposition {ABSORBED, PROVISIONAL, COMMIT_REQUEST}`,
`IdentityDecision {PROPOSED, ACCEPTED, REJECTED, REVERSED}`,
`ExecutionMode {PROLOG, GPT, PYTHON}`, `EvidencePolarity {SUPPORTS, CONTRADICTS}`.
(Access by **member name**, e.g. `ResidualDisposition.PROVISIONAL`.)

## §4 / A.5 — the processing pipeline / kernel loop

| SoW A.5 step | omega_vision / object_memory |
|--------------|------------------------------|
| `adapter.propose_candidates(obs)` | `PerceptionAdapter.propose_candidates` (`GridAdapter`, `ImageAdapter`, `SpriteAdapter`); front step also in `process_observation(obs, adapter)` |
| `adapter.propose_accounts(...)` | `InstanceMatcher.proposals` + `RecognitionSession.propose` → `MatchProposal`; `InstanceMatcher.recognition_account` |
| `choose_min_description_length(...)` | `ContourFillForm.code_length` / `CellLogoForm.description_length` + `FitResult.residual` |
| `residual_gate.evaluate(...)` | `ResidualGate.evaluate` (+ `ResidualAnalyzer.from_proposal`) |
| `writer.commit_recognition_decision(...)` | `RegistryCorrespondenceAuthority.accept`/`reject` + `SingleWriter.commit`/`commit_residual` |
| `writer.grade_open_predictions(...)` | `PredictionLedger.grade`, `GameLearningPipeline.grade_prediction` (+ `OutcomeChannel`) |
| `rules.update_from_transition_log(...)` | `GameLearningPipeline.learn_transition` (`TransitionAnalyzer`→`TransformationLearner`→`RuleInducer`→`RuleRanker`→`RuleStore`) |
| `writer.commit_rule_updates(...)` | `RuleStore.store` / `RuleStore.record_prediction_grade` |

## §7 gate · §8 completion · §9 store · §10 rules

- **§7 salience gate** — `ResidualGate.evaluate(ResidualCandidate) -> ResidualDisposition`;
  `ResidualAnalyzer.from_proposal(MatchProposal) -> tuple[ResidualCandidate, ...]`.
- **§8 completion/occlusion** — `ContourFillForm.complete(...)`;
  `RecognitionSession.complete_partial(...) -> PartialVisibilityCompletion`.
- **§9 store (three layers)** — Atomspace: `AtomStore`/`SymbolicMemory`;
  encounter log: `EncounterLog`; artifact index: `ArtifactIndex`; record facade:
  `SymbolicStore` (backends: `InMemorySemanticBackend`, `PrologSemanticBackend`,
  `AtomSpaceSemanticBackend`).
- **§10 rules & prediction** — `TransitionRule`, `PredictionRecord`,
  `PredictionLedger`, `RuleStore`, `GameLearningPipeline`; grade through the
  independent `OutcomeChannel` + `PredictionEvaluator`.

## §15 / A.1.4 — accelerators (recall only)

`PerceptualHash` (average-hash + Hamming), `VectorTraceIndex` (handle→form recall
by shape distance), `FaissIndex` (dependency-free cosine recall). None may mint a
durable identity, decide a merge, or raise confidence.

## §13 / A.7 / A.8 — acceptance & benchmarks

`GridMetrics` (recognition rate, `false_merge_rate`, `false_split_rate`,
`determinism`), `RasterMetrics` (recognition/occlusion rate, coarse fidelity),
`PerceptionBenchmarkRunner`, `RecognitionBenchmarkRunner`, `ProviderAblationRunner`,
`RasterPerturbationGenerator`, `RecognitionCalibrator`, `AcceptanceReport`.

## §16 — future components (importable stubs)

`LayeredStrokeForm`, `PartGraph3DForm`, `Robot3DAdapter`, `RGBDObjectProposer`,
`AnimeRegionProposer`, `SketchformerEmbedding`. Importable so later models plug into
an existing typed name; instantiating one raises
`omega_vision._future.FutureComponentError`.

## Verified end-to-end example

```python
import omega_vision as ov
from omega_vision.core.schemas import (
    CommittedAtom, ResidualCandidate, ResidualDisposition,
)
from omega_vision.core import PredictionRecord

# 1. Single writer + confidence floor (A.1.1 / A.1.2)
writer = ov.new_writer()
atom = writer.commit(CommittedAtom(handle="obj:ship", atom_type="object", payload={"shape": "T"}))
assert atom.confidence == 0.0                       # authored at c = 0
writer.accrue_evidence("obj:ship", confidence=0.25, evidence="re-observed")

# 2. Salience gate on an explicit residual (§7)
gate = ov.ResidualGate()
disposition = gate.evaluate(ResidualCandidate(
    residual_id="res:1", source_candidate_id="cand:1",
    disposition=ResidualDisposition.PROVISIONAL, residual_length=4.0,
    structured=True, recurrence_count=3, prediction_gain=0.2, provenance=()))

# 3. Predict-before-check ledger (§10 / A.1.7)
ledger = ov.PredictionLedger()
ledger.record(PredictionRecord(prediction_id="pred:1", rule_id="rule:gravity",
              source_state_id="state:0", predicted_effects=("ball_down",), created_sequence=1))
graded = ledger.grade("pred:1", outcome_sequence=2, outcome="ball_down", grade=1.0)

# 4. A raster form: canonical, faithful, translation-invariant (§5, §13)
from omega_vision.forms import ContourFillForm
t = ContourFillForm({"red": [(0, 0), (1, 0), (2, 0), (1, 1)]})
assert t.canonicalize() == ContourFillForm({"red": [(9, 9), (10, 9), (11, 9), (10, 10)]}).canonicalize()
```

See `tests/test_omega_vision.py` for the executable acceptance of every claim above.
