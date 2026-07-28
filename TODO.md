[← Back to top-level README](README.md)

# Reconciled Implementation TODO

This TODO combines the three SoW phases, the approved *Image Perception to Recognizable Memory* specification, the architectural plan developed in this project, and the code already connected on this branch. It is an engineering backlog, not a claim that Phase 2 or Phase 3 is complete.

## Status legend

- **Existing** — working code that predates the object-memory additions.
- **Connected contract** — the class/module exists and participates in a runnable path, while the final learning algorithm may still be incomplete.
- **Next** — immediate integration work.
- **Acceptance work** — required tests, benchmarks, and evidence.
- **Future** — intentionally after the exact grid path is reliable.

## Non-duplication rules

- Keep `Arc3Runner`, `ActionTreeStore`, `GptArcAnalyzer`, `SWIPrologBridge`, and `turtle_dsl.pl`.
- Keep generated level-wide `object_registry.pl` as the identity authority.
- Use one backend-neutral contract with PROLOG, GPT, and PYTHON providers.
- Do not duplicate native Prolog inference in Python.
- Keep one runnable implementation under `scripts/`; do not recreate `examples/`.
- Do not create phase directories.
- Do not alter protected Kaggle entry points.

## Protected Kaggle surface

- `agent/my_agent.py`
- `scripts/play_local.py`
- `scripts/build_notebook.py`
- `notebooks/submission.ipynb`
- `notebooks/kernel-metadata.json`
- existing Kaggle-related Makefile targets, imports, paths, and packaging behavior

---

# Phase 1 — ARC3 debugger foundation

## Existing

- [x] `python/arc3_runner.py` — game lifecycle, actions, level handling, state capture, history, replay, reset, restart, export, and symbolic command entry points.
- [x] `python/action_tree.py` — deterministic action tree, state images, JSON, parent/child navigation, README generation, cache paths, hashes, and friendly identity normalization.
- [x] `python/gpt_bridge.py` — combined GPT request producing mutually consistent `objects.pl`, `differences.pl`, `similarities.pl`, Turtle artifacts, and rules.
- [x] `python/swipl_bridge.py` and `prolog/arc3_agent.pl` — SWI-Prolog action-selection seam.
- [x] `prolog/turtle_dsl.pl` — authoritative Turtle execution semantics.
- [x] `scripts/interactive_runner.py` — terminal debugger.
- [x] `scripts/prolog_controlled_runner.py` — executable SWI-Prolog controller demonstration.
- [x] `webui/server.py` — browser terminal launching the same debugger script.

## Existing-name mappings; do not duplicate

| Proposed concept | Repository mapping |
|---|---|
| `Arc3Runner` | `python/arc3_runner.py::Arc3Runner` |
| `Arc3Debugger` | `Arc3Runner` commands plus `scripts/interactive_runner.py` |
| `ActionRecord` | `python/arc3_runner.py::StepRecord` |
| `ActionTreeStore` | `python/action_tree.py::ActionTreeStore` |
| `CombinedAnalysisService` | `python/gpt_bridge.py::GptArcAnalyzer` |
| `ArtifactCache` | existing cache/missing-artifact policy in `GptArcAnalyzer` and `ActionTreeStore` |
| `ReplayController` | `Arc3Runner.replay()` |
| `ObjectRegistryBridge` | level-wide registry handling in `ActionTreeStore` |
| Turtle execution | `prolog/turtle_dsl.pl` |

## Next Phase 1 normalization

- [ ] Define one canonical state ordinal and action ordinal.
- [ ] Add schema versions to generated artifacts.
- [ ] Add a normalized immutable `Observation` or `StateSnapshot` record without replacing `StateNode` or `StepRecord`.
- [ ] Bridge `StateNode`, `state.json`, `image.png`, and `StepRecord` into the normalized observation record.
- [ ] Validate cached artifacts before reuse, including schema version and registry compatibility.
- [ ] Add deterministic replay and state-hash tests.
- [ ] Connect all six Prolog debugger commands to normalized Prolog APIs.
- [ ] Ensure combined-analysis artifacts use exactly the same friendly identities.
- [ ] Record analyzer mode and provenance in generated artifact metadata.

---

# Shared execution modes

## Connected contract

- [x] `ExecutionMode`: `PROLOG`, `GPT`, `PYTHON`.
- [x] `NormalizedResult`: one return shape for every backend.
- [x] `CandidateObject.part(name)`: provider delegation.
- [x] `PrologProvider`: SWI-Prolog/query delegation.
- [x] `GptArtifactProvider`: reads generated/cached `.pl` artifacts.
- [x] `PythonProvider`: deterministic native resolver registry.
- [x] Equivalent-result tests across all three modes.

## Next

- [ ] Add normalized object-memory query methods to the existing `SWIPrologBridge`.
- [ ] Connect provider source references to action-tree paths and provenance.
- [ ] Add backend-equivalence fixtures for properties, correspondence, differences, generative forms, and rules.
- [ ] Add explicit provider capability discovery rather than speculative empty interfaces.

---

# Phase 2 — object perception, recognition, and persistent memory

## Connected contracts

- [x] `CandidateObject` provider-backed facade.
- [x] `ResidualCandidate` and `ResidualDisposition`.
- [x] `CommittedAtom` backend-neutral record.
- [x] `GenerativeForm` and `CellLogoForm` facade.
- [x] `PerceptionAdapter` and thin `GridAdapter`.
- [x] `ResidualGate`.
- [x] `SymbolicMemory` reference implementation.
- [x] `SingleWriter` with zero-confidence admission and gated residual commitment.
- [x] Prolog `object_memory_contract.pl`, `generative_form.pl`, `residual_gate.pl`, and `single_writer.pl`.
- [x] Python and Prolog tests for residual and commitment invariants.

## Shared records to add when first consumed

Keep them in `python/object_memory/models.py`; do not create a second model package.

- [ ] `Observation`
- [ ] `RecognitionAccount`
- [ ] `TruthValue`
- [ ] `InstanceParameters`
- [ ] `ArtifactRef`
- [ ] `ProvenanceRef`
- [ ] `Residual`
- [ ] `MatchProposal`
- [ ] `MergeDecision`
- [ ] `GateDecision`
- [ ] `EvidenceRecord`
- [ ] `WorkingState`
- [ ] `CompletionCandidate`

## Persistence and governance — Next

- [ ] Implement append-only `EncounterLog` with stable IDs, transition retrieval, hashing, and deterministic replay.
- [ ] Implement a durable `SymbolicStore` facade over the selected Prolog or Atomspace store.
- [ ] Implement `ArtifactIndex` for frames, masks, traces, embeddings, and reconstructions.
- [ ] Keep raw frames as artifacts, not durable concepts.
- [ ] Add lifecycle states: active, demoted, tombstoned; never hard-delete provenance.
- [ ] Add confidence/evidence updates only through `SingleWriter` or its authoritative Prolog equivalent.
- [ ] Implement deterministic observation and encounter IDs.
- [ ] Implement identity merge and split proposals while keeping committed identity exact.
- [ ] Ensure embeddings may retrieve candidates but cannot commit identity, merge atoms, or increase confidence.

## Grid perception and recognition — Next

- [ ] Inspect and wrap the existing grid object extractor behind `GridAdapter`.
- [ ] Connect object extraction, representation, and canonicalization.
- [ ] Match corresponding objects across parent/current states and across examples.
- [ ] Use generated `object_registry.pl`; do not create another identity database.
- [ ] Connect `CellLogoForm.render()` to `turtle_dsl.pl` through the existing bridge.
- [ ] Implement form fitting, explicit residual measurement, description length, and distance.
- [ ] Regenerate objects from stored forms and compare with observations.
- [ ] Add translation, rotation, reflection, recolor, and scale fixtures.
- [ ] Add duplicate-identity, false-merge, and false-split tests.
- [ ] Add replay-determinism and faithful-regeneration tests.

## Phase 2 Prolog capability modules — reconcile before adding

Add only where no equivalent predicate already exists.

- [ ] `arc3_state.pl` — normalized state facts over action-tree metadata.
- [ ] `object_analysis.pl` — normalized current-state object facts.
- [ ] `state_difference.pl` — deterministic parent/current differences.
- [ ] `state_similarity.pl` — deterministic correspondence and similarity.
- [ ] `encounter_log.pl` — append-only encounters and replay.
- [ ] `symbolic_store.pl` — durable atom, evidence, and lifecycle access.
- [ ] `object_recognition.pl` — recognition accounts and re-recognition.
- [ ] `object_correspondence.pl` — matching and correspondence scores.
- [ ] `object_extraction.pl` — only if the existing object engine cannot be loaded as a provider.

## Raster and occlusion — Future after grid acceptance

- [ ] `ContourFillForm` and matching Prolog form predicates.
- [ ] `SpriteAdapter`.
- [ ] Connected components, contour extraction, and vector tracing provider.
- [ ] Noise, degradation, recolor, and partial-occlusion fixtures.
- [ ] Generative completion and consistency validation.
- [ ] Top-down manipulation demonstration.

---

# Phase 3 — game learner integration, transformations, rules, and prediction

The Phase 3 contracts are present and connected. This does not assert that rule induction quality, ranking quality, task coverage, or benchmark acceptance is complete.

## Connected Python path

- [x] `GameObjectLearnerPayload` and `GameObjectLearnerResult`.
- [x] `GameObjectLearnerSchema`, `IntegrationValidator`, and `IntegrationError`.
- [x] `GameObjectLearnerPlugin` state/transition entry points.
- [x] `PipelineGameObjectLearnerPlugin`.
- [x] `TransitionRecord` and `TransitionAnalyzer`.
- [x] `TransformationCandidate` and `TransformationLearner`.
- [x] `RuleInducer`, `RuleRanker`, `RuleExecutor`, and exact-identity `RuleStore`.
- [x] `RuleEvidence` and `RuleRivalSet` records.
- [x] `TransitionRule`.
- [x] `PredictionRecord`, append-only `PredictionLedger`, `OutcomeChannel`, `PredictionEvaluator`, and `PredictionGrade`.
- [x] `GameLearningPipeline` connects transition analysis → transformation candidates → rule induction → ranking → storage → application → prior prediction → independent grading.
- [x] End-to-end Python test for learning, rule application, prediction, and grading.

## Connected Prolog path

- [x] `transition_analysis.pl`.
- [x] `transformation_learning.pl`.
- [x] `rule_induction.pl`.
- [x] `rule_ranking.pl`.
- [x] `transition_rules.pl` using canonical `object_memory_contract:transition_rule/2` storage.
- [x] `prediction_ledger.pl`.
- [x] `prediction_evaluation.pl`.
- [x] `game_object_learner_api.pl` connecting the modules through one provider dictionary.
- [x] Prolog test for transition analysis, candidate generation, rule induction/ranking/storage/application, prior prediction, and later grading.

## Next Phase 3 integration

- [ ] Freeze the serialized Game Object Learner payload schema.
- [ ] Build payloads from real Phase 2 objects and correspondences.
- [ ] Connect `PipelineGameObjectLearnerPlugin` to actual `Arc3Runner` transitions.
- [ ] Connect Prolog providers to existing `objects.pl`, `differences.pl`, `similarities.pl`, `rules.pl`, and registry facts.
- [ ] Implement transition analysis over real object correspondences.
- [ ] Generate candidate transformations from observed deltas.
- [ ] Validate and apply transformations to unseen cases.
- [ ] Induce rules using the existing `rules.pl` shape.
- [ ] Rank rules using prediction evidence, simplicity, contradiction, and rival interpretations.
- [ ] Preserve multiple competing interpretations.
- [ ] Store rule evidence only through the authoritative writer/store path.
- [ ] Record predictions before ARC3 actions are executed.
- [ ] Grade predictions from independent ARC3 environment responses.
- [ ] Connect prediction records and solver traces into action-tree READMEs.
- [ ] Provide action recommendations to `agent/my_agent.py` through a stable seam without changing its protected contract.

## Evaluation and acceptance work

- [ ] `BenchmarkRunner`.
- [ ] `PerturbationGenerator`.
- [ ] `AcceptanceEvaluator` and `AcceptanceReport`.
- [ ] `AblationRunner` comparing PROLOG/GPT/PYTHON providers.
- [ ] ARC grid fixtures.
- [ ] Rendered arcade fixtures.
- [ ] Fixed-camera physics fixtures.
- [ ] Top-down manipulation and partial-occlusion fixtures.
- [ ] Prediction-improvement-over-experience measurement.
- [ ] Reproducible commands and exact acceptance results.

---

# Cross-language mapping

| Concept | Python | Prolog |
|---|---|---|
| Candidate object | `CandidateObject` | `candidate_object/2` |
| Recognition explanation | `RecognitionAccount` | `recognition_account/2` |
| Unexplained structure | `ResidualCandidate` | `residual_candidate/2` |
| Persistent concept | `CommittedAtom` | `committed_atom/2` |
| Generative representation | `GenerativeForm` | `generative_form.pl` |
| Exact grid form | `CellLogoForm` | `generative_form.pl` + `turtle_dsl.pl` |
| Domain front end | `PerceptionAdapter` | provider predicates |
| Grid front end | `GridAdapter` | existing grid engine/provider |
| Identity authority | action-tree registry | generated `object_registry.pl` |
| Admission decision | `ResidualGate` | `residual_gate.pl` |
| Commit path | `SingleWriter` | `single_writer.pl` |
| Encounter history | planned `EncounterLog` | planned `encounter_log.pl` |
| Transition analysis | `TransitionAnalyzer` | `transition_analysis.pl` |
| Transformation learner | `TransformationLearner` | `transformation_learning.pl` |
| Learned rule | `TransitionRule` | `transition_rule/2` |
| Rule induction | `RuleInducer` | `rule_induction.pl` |
| Rule ranking | `RuleRanker` | `rule_ranking.pl` |
| Rule application | `RuleExecutor` / `RuleStore` | `transition_rules.pl` |
| Prior prediction | `PredictionRecord` | `prediction_record/2` |
| Prediction history | `PredictionLedger` | `prediction_ledger.pl` |
| Outcome grading | `PredictionEvaluator` | `prediction_evaluation.pl` |
| Game learner boundary | `GameObjectLearnerPlugin` | `game_object_learner_api.pl` |

# Recommended implementation order

1. Freeze observation, object, committed-atom, transition, and payload schemas.
2. Implement encounter persistence and artifact indexing.
3. Bridge action-tree state nodes into Phase 2 observations.
4. Connect the exact grid form to the existing Turtle interpreter.
5. Connect the existing object engine through `GridAdapter`.
6. Implement deterministic correspondence, recognition, and regeneration.
7. Pass grid identity, replay, and regeneration tests.
8. Feed real Phase 2 transitions into the connected Phase 3 pipeline.
9. Record predictions before ARC3 actions and grade the environment response.
10. Add raster, degradation, and occlusion providers after the grid path is stable.
11. Add benchmark, ablation, and acceptance reporting.
12. Keep runnable entry points in `scripts/`; maintain one implementation per runner.

# Non-negotiable coding constraints

- Raw frames are artifacts, not durable concepts.
- Similarity may propose identity but may not define committed identity.
- Embeddings may accelerate lookup but may not create or merge identities or raise confidence.
- Components propose atoms at zero confidence.
- Only `SingleWriter` or its authoritative Prolog equivalent changes durable state or evidence.
- Objects are demoted or tombstoned, never erased with their provenance.
- A rule receives positive evidence only when its prediction existed before the outcome.
- Core contracts contain no ARC-specific or raster-specific assumptions.
- The same starting store and encounter log must replay to the same handles and confidence values.
- GPT artifacts remain explicitly GPT-backed and are never presented as native Python symbolic implementations.

[← Back to top-level README](README.md)
