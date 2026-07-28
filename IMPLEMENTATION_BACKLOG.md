# Reconciled Implementation Backlog

This backlog combines the three SoW phases, the approved *Image Perception to
Recognizable Memory* specification, and the architecture already present in this
repository. It is a working engineering plan, not a statement that Phase 2 or
Phase 3 is complete.

## Status legend

- **Existing** — working code that predates the object-memory additions.
- **Connected contract** — the class/module exists, participates in a runnable
  path, and delegates to replaceable providers; the final algorithm may still be
  incomplete.
- **Next** — the next integration work against the existing debugger and object
  engine.
- **Acceptance work** — required validation, benchmarks, or wider task coverage.
- **Future** — intentionally after the grid path is reliable.

## Non-duplication rules

- Keep `Arc3Runner`, `ActionTreeStore`, `GptArcAnalyzer`, `SWIPrologBridge`, and
  `turtle_dsl.pl`; do not create replacements under `object_memory/`.
- Keep the level-wide generated `object_registry.pl` as the authoritative
  friendly-identity store.
- Keep one backend-neutral contract and use PROLOG, GPT, or PYTHON providers.
- Keep symbolic inference in Prolog where it already exists; Python types may be
  records, facades, orchestration, or deterministic utilities.
- Do not add duplicate runners under both `examples/` and `scripts/`.
- Do not create phase directories.
- Do not change the protected Kaggle surface.

## Protected Kaggle surface

These paths and their existing Makefile workflow must remain compatible:

- `notebooks/submission.ipynb`
- `scripts/build_notebook.py`
- `scripts/play_local.py`
- `agent/my_agent.py`
- existing Kaggle-related Makefile targets, paths, imports, and packaging rules

---

# Phase 1 — ARC3 debugger foundation

## Existing

- [x] `python/arc3_runner.py` — game lifecycle, actions, history, replay, reset,
  restart, level detection, state export, and analysis commands.
- [x] `python/action_tree.py` — deterministic action tree, state images and JSON,
  parent/child links, generated READMEs, cache paths, and friendly identity
  normalization.
- [x] `python/gpt_bridge.py` — combined GPT request producing mutually consistent
  `objects.pl`, `differences.pl`, `similarities.pl`, Turtle artifacts, and rules.
- [x] `python/swipl_bridge.py` and `prolog/arc3_agent.pl` — SWI-Prolog control seam.
- [x] `prolog/turtle_dsl.pl` — authoritative Turtle execution semantics.
- [x] `examples/interactive_runner.py` — terminal debugger.
- [x] `webui/server.py` — browser terminal using the same runner.

## Existing-name mappings; do not duplicate

| Proposed name | Repository mapping |
|---|---|
| `Arc3Runner` | `python/arc3_runner.py::Arc3Runner` |
| `Arc3Debugger` | Existing runner commands plus `examples/interactive_runner.py` |
| `ActionRecord` | `python/arc3_runner.py::StepRecord` |
| `ActionTreeStore` | `python/action_tree.py::ActionTreeStore` |
| `CombinedAnalysisService` | `python/gpt_bridge.py::GptArcAnalyzer` |
| `ArtifactCache` | Existing missing-file/cache policy in `GptArcAnalyzer` and `ActionTreeStore` |
| `ReplayController` | `Arc3Runner.replay()` |
| `ObjectRegistryBridge` | Existing level-wide registry handling in `ActionTreeStore` |
| Turtle program engine | `prolog/turtle_dsl.pl` |

## Next cleanup and bridge work

- [ ] Define one canonical state ordinal and action ordinal in stored metadata.
- [ ] Add version fields to generated artifact schemas.
- [ ] Add a normalized `Observation`/state-snapshot record without replacing
  `StateNode` or `StepRecord`.
- [ ] Bridge `StateNode`, `state.json`, `image.png`, and `StepRecord` into that
  observation record.
- [ ] Validate cached artifacts before reuse, including schema version and object
  registry compatibility.
- [ ] Add deterministic replay and state-hash tests.
- [ ] Connect the six Prolog debugger commands to the object-memory Prolog APIs.
- [ ] Keep all combined-analysis artifacts on the same friendly identities.

---

# Shared execution modes

## Connected contract

- [x] `ExecutionMode`: `PROLOG`, `GPT`, `PYTHON`.
- [x] `NormalizedResult`: one return shape for every backend.
- [x] `CandidateObject.part(name)`: delegates to a provider.
- [x] `PrologProvider`: delegates symbolic requests to SWI-Prolog/query bridges.
- [x] `GptArtifactProvider`: reads existing generated/cached `.pl` artifacts.
- [x] `PythonProvider`: deterministic native resolver registry.
- [x] Tests demonstrate equivalent normalized values across all three modes.

## Next

- [ ] Add an `SWIPrologBridge` query method for normalized object-memory predicates,
  reusing the existing subprocess bridge rather than adding another bridge.
- [ ] Connect provider source references to action-tree artifact paths and
  provenance records.
- [ ] Add backend equivalence fixtures for properties, correspondence,
  differences, generative forms, and rules.

---

# Phase 2 — object perception, representation, correspondence, and memory

## Connected contracts

- [x] `CandidateObject` — provider-backed object facade.
- [x] `ResidualCandidate` and `ResidualDisposition`.
- [x] `CommittedAtom` — backend-neutral committed-record shape.
- [x] `GenerativeForm` and `CellLogoForm` — facade over the existing Turtle form.
- [x] `PerceptionAdapter` and thin `GridAdapter`.
- [x] `ResidualGate`.
- [x] `SymbolicMemory` reference implementation.
- [x] `SingleWriter`, including zero-confidence admission and gated residual
  commitment.
- [x] Prolog `object_memory_contract.pl`, `generative_form.pl`,
  `residual_gate.pl`, and `single_writer.pl`.
- [x] Python and Prolog unit tests for residual and commitment invariants.

## Proposed records still needed

Add these only when the first consumer is connected; keep them in
`python/object_memory/models.py` rather than creating a second model package.

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

- [ ] Implement append-only `EncounterLog` with stable IDs, deterministic replay,
  and transition retrieval.
- [ ] Implement a persistent `SymbolicStore` facade over the selected Atomspace or
  durable Prolog store.
- [ ] Implement `ArtifactIndex` referencing raw frames, masks, traces, embeddings,
  and reconstructions without storing raw frames as concepts.
- [ ] Add lifecycle operations: active, demoted, tombstoned; never hard-delete
  provenance.
- [ ] Add evidence records and confidence accrual only through `SingleWriter`.
- [ ] Add deterministic stable-ID generation for observations and encounters.
- [ ] Implement identity merge proposals while leaving committed identity exact.
- [ ] Ensure embeddings can retrieve candidates but cannot commit identity,
  merge atoms, or raise confidence.

## Grid perception and recognition — Next

- [ ] Inspect and wrap the existing grid object extractor behind `GridAdapter`.
- [ ] Implement or connect object extraction, representation, and canonicalization.
- [ ] Match corresponding objects across parent/current states and examples.
- [ ] Use the existing `object_registry.pl` rather than creating another identity
  database.
- [ ] Connect `CellLogoForm.render()` to `turtle_dsl.pl` through the existing SWI
  bridge.
- [ ] Implement form fitting, residual measurement, code length, and distance.
- [ ] Regenerate grid objects from stored forms.
- [ ] Add translation, rotation, reflection, recolor, and scale fixtures.
- [ ] Add duplicate-identity, false-merge, and false-split tests.
- [ ] Add replay-determinism and faithful-regeneration tests.

## Phase 2 Prolog modules — reconcile before adding

The following are desired capabilities. Extend existing modules or add one module
only when no equivalent predicate already exists.

- [ ] `arc3_state.pl` — normalized state facts over existing action-tree metadata.
- [ ] `object_analysis.pl` — normalized access to current object facts.
- [ ] `state_difference.pl` — deterministic parent/current differences.
- [ ] `state_similarity.pl` — deterministic correspondence and similarity.
- [ ] `encounter_log.pl` — append-only encounters and replay.
- [ ] `symbolic_store.pl` — durable atom/evidence/lifecycle access.
- [ ] `object_recognition.pl` — recognition accounts and re-recognition.
- [ ] `object_correspondence.pl` — matching and correspondence scores.
- [ ] `object_extraction.pl` — only if the existing object engine cannot be loaded
  directly as the provider.

## Raster and occlusion — Future after grid acceptance

- [ ] `ContourFillForm` and corresponding Prolog form predicates.
- [ ] `SpriteAdapter`.
- [ ] Connected components, contour extraction, and vector tracing provider.
- [ ] Noise, degradation, recolor, and partial-occlusion fixtures.
- [ ] Generative completion and consistency validation.
- [ ] Top-down manipulation demonstration.

---

# Phase 3 — game learner integration, transformations, rules, and prediction

The Phase 3 contracts are present and connected now. This does not assert that
rule induction, ranking quality, or benchmark coverage is complete.

## Connected Python path

- [x] `GameObjectLearnerPayload`.
- [x] `GameObjectLearnerResult`.
- [x] `GameObjectLearnerSchema`, `IntegrationValidator`, and `IntegrationError`.
- [x] `GameObjectLearnerPlugin` with state and transition entry points.
- [x] `PipelineGameObjectLearnerPlugin`.
- [x] `TransitionRecord` and `TransitionAnalyzer`.
- [x] `TransformationCandidate` and `TransformationLearner`.
- [x] `RuleInducer`, `RuleRanker`, `RuleExecutor`, and exact-identity `RuleStore`.
- [x] `RuleEvidence` and `RuleRivalSet` records.
- [x] `TransitionRule`.
- [x] `PredictionRecord`, append-only `PredictionLedger`, `OutcomeChannel`,
  `PredictionEvaluator`, and `PredictionGrade`.
- [x] `GameLearningPipeline` connects transition analysis → candidate generation →
  rule induction → ranking → storage → prediction-before-outcome → grading.
- [x] End-to-end Python test covers learning, rule application, prediction, and
  independent outcome grading.

## Connected Prolog path

- [x] `transition_analysis.pl`.
- [x] `transformation_learning.pl`.
- [x] `rule_induction.pl`.
- [x] `rule_ranking.pl`.
- [x] `transition_rules.pl`, using the canonical
  `object_memory_contract:transition_rule/2` store.
- [x] `prediction_ledger.pl`.
- [x] `prediction_evaluation.pl`.
- [x] `game_object_learner_api.pl`, connecting the above modules through one
  provider dictionary.
- [x] Prolog test exercises transition analysis, transformation candidates, rule
  induction/ranking/storage/application, prediction recording, and later grading.

## Next integration work

- [ ] Define and freeze the serialized Game Object Learner payload schema.
- [ ] Build payloads from actual Phase 2 recognized objects and correspondences.
- [ ] Connect `PipelineGameObjectLearnerPlugin` to `Arc3Runner` transitions.
- [ ] Connect Prolog providers to existing `objects.pl`, `differences.pl`,
  `similarities.pl`, `rules.pl`, and registry facts.
- [ ] Implement real transition analysis over object correspondences.
- [ ] Implement candidate transformation generation from observed deltas.
- [ ] Implement transformation validation and application to unseen cases.
- [ ] Implement rule induction over the existing `rules.pl` shape.
- [ ] Implement ranking using prediction evidence, simplicity, and contradiction.
- [ ] Preserve multiple competing interpretations and rival rules.
- [ ] Store rule evidence only through the authoritative writer/store path.
- [ ] Connect predictions to actions before executing those actions.
- [ ] Grade predictions from the ARC3 environment response, not from the proposer.
- [ ] Connect solver traces and prediction records back into action-tree READMEs.
- [ ] Provide action recommendations to `agent/my_agent.py` through a stable seam
  without changing the protected Kaggle entry-point contract.

## Evaluation and acceptance work

- [ ] `BenchmarkRunner`.
- [ ] `PerturbationGenerator`.
- [ ] `AcceptanceEvaluator` and `AcceptanceReport`.
- [ ] `AblationRunner` for PROLOG/GPT/PYTHON provider comparisons.
- [ ] ARC-style grid fixtures.
- [ ] Rendered arcade fixtures.
- [ ] Fixed-camera physics fixtures.
- [ ] Top-down manipulation and partial-occlusion fixtures.
- [ ] Prediction-improves-over-experience measurement.
- [ ] Reproducible commands and exact acceptance results.

---

# Cross-language mapping

| Concept | Python | Prolog |
|---|---|---|
| Candidate object | `CandidateObject` | `candidate_object/2` |
| Unexplained structure | `ResidualCandidate` | `residual_candidate/2` |
| Persistent concept | `CommittedAtom` | `committed_atom/2` |
| Generative representation | `GenerativeForm` | `generative_form.pl` |
| Grid form | `CellLogoForm` | `generative_form.pl` + `turtle_dsl.pl` |
| Domain front end | `PerceptionAdapter` | provider predicates |
| Grid front end | `GridAdapter` | existing grid engine/provider |
| Identity authority | existing action-tree registry | generated `object_registry.pl` |
| Admission decision | `ResidualGate` | `residual_gate.pl` |
| Commit path | `SingleWriter` | `single_writer.pl` |
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

---

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
12. Consider runner migration from `examples/` to `scripts/` only after every
    reference is updated; keep one implementation.

# Non-negotiable coding constraints

- Raw frames are artifacts, not durable concepts.
- Similarity may propose identity but may not define committed identity.
- Embeddings may accelerate lookup but may not create/merge identities or raise
  confidence.
- Components propose atoms at zero confidence.
- Only `SingleWriter` or its authoritative Prolog equivalent changes durable state
  or evidence.
- Objects are demoted or tombstoned, never erased with their provenance.
- A rule receives positive evidence only when its prediction existed before the
  outcome.
- Core contracts contain no ARC-specific or raster-specific assumptions.
- The same starting store and encounter log must replay to the same handles and
  confidence values.
- GPT artifacts are labeled GPT-backed and never presented as native Python
  symbolic implementations.
