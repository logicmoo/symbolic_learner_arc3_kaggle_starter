[← Back to top-level README](README.md)

# Reconciled Implementation TODO — Image Perception to Recognizable Memory

This backlog maps the current repository to the three deliverable-based phases in the *Image Perception to Recognizable Memory* Statement of Work. It distinguishes working infrastructure, connected contracts, remaining implementation, and acceptance evidence. It does not claim that Phase 2 or Phase 3 is complete.

## Delivery sequence

| Phase | Anticipated delivery window | Current characterization |
|---|---:|---|
| Phase 1 — Grid Infrastructure and ARC3 Debugger Foundation | 3 weeks | Substantially implemented; normalization and acceptance hardening remain |
| Phase 2 — Object Perception, Recognition, and Persistent Memory | 1 month | Contracts connected; full perception, persistence, recognition, and demonstrations remain |
| Phase 3 — Game Object Learner Integration and Predictive Rule Learning | 1 month | Python and Prolog orchestration connected; real payloads, prediction quality, and acceptance remain |

The overall sequence is anticipated to take approximately three months. Material schedule changes should be communicated in writing.

## Status legend

- **Existing** — working repository behavior.
- **Connected contract** — class/module participates in a runnable path, but final capability or quality is incomplete.
- **Next** — immediate implementation work.
- **Acceptance work** — tests, demonstrations, benchmarks, and evidence required for delivery.
- **Future** — intentionally after the deterministic grid path is reliable.

## Non-duplication and governance rules

- Keep `Arc3Runner`, `ActionTreeStore`, `GptArcAnalyzer`, `SWIPrologBridge`, and `turtle_dsl.pl`.
- Keep generated level-wide `object_registry.pl` as the identity authority.
- Keep one provider registry and one prompt-section source in `config/llm_providers.json`.
- Keep one combined artifact pipeline and one Markdown transcript history per LLM run.
- Use one backend-neutral contract with PROLOG, GPT/LLM, and PYTHON providers.
- Do not duplicate native Prolog inference in Python.
- Keep runnable entry points under `scripts/`; do not recreate `examples/`.
- Do not create phase directories.
- Do not alter protected Kaggle entry points.
- Similarity and embeddings may retrieve candidates but may not independently commit identity or evidence.
- Only `SingleWriter` or its authoritative Prolog equivalent changes durable memory or evidence.
- A learned rule receives prediction credit only when the prediction existed before the independently observed outcome.

## Protected Kaggle surface

- `agent/my_agent.py`
- `scripts/play_local.py`
- `scripts/build_notebook.py`
- generated `notebooks/submission.ipynb`
- `notebooks/kernel-metadata.json`
- existing Kaggle-related Makefile targets, imports, paths, and packaging behavior

---

# Phase 1 — Grid Infrastructure and ARC3 Debugger Foundation

## Existing runtime and debugger

- [x] `python/arc3_runner.py` — game lifecycle, selected game/level interaction, legal actions, observations, state capture, history, replay, reset, restart, export, and symbolic commands.
- [x] `scripts/interactive_runner.py` — runtime-aware terminal launcher.
- [x] `python/interactive_runner.py` — full terminal debugger UI.
- [x] `scripts/run_webui.py` and `webui/server.py` — browser terminal using the same interactive runner.
- [x] `scripts/prolog_controlled_runner.py` — SWI-Prolog-controlled demonstration.
- [x] Native Windows setup and launcher support.

## Existing state and action-tree evidence

- [x] `python/action_tree.py` — deterministic action-tree nodes, state images, `state.json`, parent/child navigation, hashes, and generated READMEs.
- [x] GitHub-browsable action paths with coordinate-bearing action directory names.
- [x] Level-wide friendly identity authority in `object_registry.pl`.
- [x] Latest node-local `objects.pl`, `differences.pl`, `similarities.pl`, Turtle artifacts, and `rules.pl`.
- [x] Replay, reset, restart, history navigation, and previously captured state inspection.
- [x] Parent/current context supplied to combined analysis.

## Existing provider, prompt, and transcript infrastructure

- [x] Ordered OpenAI, Claude, and Unsloth provider registry.
- [x] Unified reusable `prompt_text` sections in `config/llm_providers.json`.
- [x] Provider-specific ordered prompt-section lists, including support for omitting sections such as `transitions`.
- [x] Unsloth authentication, model-status detection, automatic model loading, and model reuse.
- [x] Strict JSON parsing, deterministic repair, required-key validation, and one text-only recovery pass.
- [x] One Markdown transcript per LLM request with provider, adapter, model, analysis level/profile, token budget, request images, prompt, timing, repair history, normalized response, and raw responses.
- [x] Restorable Prolog artifact snapshots at the top of completed transcripts.
- [x] Mutable latest `.pl` files plus immutable historical transcript cache.
- [x] LLM command `1` transcript listing and restoration.
- [x] Node README active-transcript summary and historical transcript links without recursive embedding.

## Existing runtime resource discovery

- [x] Resolve code/runtime root independently from configuration and action-tree storage.
- [x] Search upward from the launch directory for `config/llm_providers.json` and `action_trees/`.
- [x] Use `ARC3_RUNTIME_HOME` resources when the launch workspace does not provide them.
- [x] Fall back to the actual script/code checkout.
- [x] Load nearest workspace/runtime/script `.env` files without overriding shell values.
- [x] Print launch directory, code root, environment files, LLM config, and action-tree output at startup.
- [x] Preserve the caller directory in the Windows launcher.

## Phase 1 normalization — Next

- [ ] Define one canonical state ordinal and action ordinal across history, action tree, replay, and learner payloads.
- [ ] Add schema versions to `state.json`, generated artifact metadata, transcript metadata, and learner-facing records.
- [ ] Add a normalized immutable `Observation` or `StateSnapshot` record without replacing `StateNode` or `StepRecord`.
- [ ] Bridge `StateNode`, `state.json`, `image.png`, and `StepRecord` into the normalized observation record.
- [ ] Validate cached artifacts before reuse, including schema version, state/image hash, registry compatibility, provider/model/profile, and requested artifact set.
- [ ] Ensure every combined artifact uses exactly the same friendly identities and registry version.
- [ ] Record normalized analyzer mode, provider, prompt sections, model, token settings, image hashes, and generation source in provenance.
- [ ] Connect all six Prolog debugger commands to normalized Prolog APIs.
- [ ] Add a stable evidence-record schema shared by LLM and native symbolic paths.

## Phase 1 acceptance work

- [ ] Demonstrate loading and interacting with selected ARC3 games and levels.
- [ ] Demonstrate capture of state, action, observation, image, and execution history.
- [ ] Demonstrate GitHub-browsable action-tree navigation.
- [ ] Demonstrate reset, restart, replay, and history navigation.
- [ ] Demonstrate stable object identities across at least one multi-step branch.
- [ ] Demonstrate combined current-state and parent-transition analysis.
- [ ] Demonstrate provider/model/profile comparison across Markdown transcripts.
- [ ] Restore an older transcript and verify that latest `.pl` files and README state match it.
- [ ] Add deterministic replay and state/image-hash tests.
- [ ] Add cache-validity and stale-cache rejection tests.
- [ ] Add artifact-schema and Prolog-syntax plausibility checks.
- [ ] Preserve current Python 3.12 test workflow and add native Windows smoke evidence.
- [ ] Ensure debugger, Windows, provider, transcript, action-tree, and evidence documentation is current.

---

# Shared execution modes

## Connected contract

- [x] `ExecutionMode`: `PROLOG`, `GPT`, `PYTHON`.
- [x] `NormalizedResult`: one result shape for every backend.
- [x] `CandidateObject.part(name)`: provider delegation.
- [x] `PrologProvider`: SWI-Prolog/query delegation.
- [x] `GptArtifactProvider`: generated/cached artifact access.
- [x] `PythonProvider`: deterministic native resolver registry.
- [x] Equivalent-result tests across the three modes.

## Next

- [ ] Add normalized object-memory queries to the existing `SWIPrologBridge`.
- [ ] Attach provider source references to action-tree nodes, transcripts, artifacts, and evidence records.
- [ ] Add backend-equivalence fixtures for properties, correspondences, differences, generative forms, transformations, and rules.
- [ ] Add explicit provider capability discovery.
- [ ] Reject unsupported operations with structured errors instead of empty placeholder results.

---

# Phase 2 — Object Perception, Recognition, and Persistent Memory

## Connected contracts

- [x] `CandidateObject` provider-backed facade.
- [x] `PerceptionAdapter` and thin `GridAdapter`.
- [x] `GenerativeForm` and `CellLogoForm` facade over existing Turtle programs.
- [x] `ResidualCandidate`, `ResidualDisposition`, and `ResidualGate`.
- [x] `CommittedAtom` backend-neutral record.
- [x] `SymbolicMemory` reference implementation.
- [x] `SingleWriter` with zero-confidence admission and gated residual commitment.
- [x] Prolog `object_memory_contract.pl`, `generative_form.pl`, `residual_gate.pl`, and `single_writer.pl`.
- [x] Python and Prolog tests for residual and commitment invariants.

## Shared records to add when first consumed

Keep these in `python/object_memory/models.py`; do not create a second model package.

- [ ] `Observation`
- [ ] `EncounterRecord`
- [ ] `RecognitionAccount`
- [ ] `TruthValue`
- [ ] `InstanceParameters`
- [ ] `ArtifactRef`
- [ ] `ProvenanceRef`
- [ ] `Residual`
- [ ] `MatchProposal`
- [ ] `MergeDecision`
- [ ] `SplitDecision`
- [ ] `GateDecision`
- [ ] `EvidenceRecord`
- [ ] `WorkingState`
- [ ] `CompletionCandidate`

## Object extraction and representation — Next

- [ ] Inspect and wrap the existing grid object extractor behind `GridAdapter`.
- [ ] Normalize object properties, structure, relationships, coordinates, orientation, scale, colors, and appearance.
- [ ] Preserve exact topology, connectivity, cavities, holes, borders, and enclosure relationships.
- [ ] Canonicalize objects without reducing irregular geometry to oversized rectangles.
- [ ] Store generative forms capable of reconstructing the object.
- [ ] Connect `CellLogoForm.render()` to `turtle_dsl.pl` through the existing bridge.
- [ ] Implement form fitting, explicit residual measurement, description length, and distance.
- [ ] Distinguish recognized structure from genuinely new residual structure.

## Correspondence and recognition — Next

- [ ] Match corresponding objects across parent/current states.
- [ ] Match objects across repeated encounters and examples.
- [ ] Reuse generated `object_registry.pl`; do not create another identity store.
- [ ] Implement translation, rotation, reflection, recolor, scale, noise, and partial-visibility comparisons where supported.
- [ ] Implement movement, recoloring, resizing, addition, removal, and structural-change detection.
- [ ] Produce explicit correspondence evidence and competing match proposals.
- [ ] Implement identity merge and split proposals without bypassing the authoritative writer.
- [ ] Prevent duplicate durable storage when an existing object is recognized again.
- [ ] Keep embeddings limited to retrieval and proposal generation.

## Persistence and provenance — Next

- [ ] Implement append-only `EncounterLog` with stable IDs, hashes, transition retrieval, and deterministic replay.
- [ ] Implement durable `SymbolicStore` access over the selected Prolog or Atomspace storage.
- [ ] Implement `ArtifactIndex` for frames, masks, traces, embeddings, reconstructions, transcripts, and derived artifacts.
- [ ] Keep raw frames as referenced artifacts rather than durable concepts.
- [ ] Add lifecycle states: active, demoted, tombstoned; never hard-delete provenance.
- [ ] Route confidence and evidence changes only through `SingleWriter` or its authoritative Prolog equivalent.
- [ ] Implement deterministic observation, encounter, object, artifact, and evidence identifiers.
- [ ] Preserve encounter history across repeated recognition and regeneration.

## Prolog capability modules — reconcile before adding

Add only when an equivalent predicate cannot be exposed from existing code.

- [ ] `arc3_state.pl` — normalized state facts over action-tree metadata.
- [ ] `object_analysis.pl` — normalized current-state object facts.
- [ ] `state_difference.pl` — deterministic parent/current differences.
- [ ] `state_similarity.pl` — deterministic correspondence and similarity.
- [ ] `encounter_log.pl` — append-only encounters and replay.
- [ ] `symbolic_store.pl` — durable atoms, evidence, lifecycle, and provenance access.
- [ ] `object_recognition.pl` — recognition accounts and re-recognition.
- [ ] `object_correspondence.pl` — matching and correspondence scores.
- [ ] `object_extraction.pl` — only if the existing object engine cannot be loaded through a provider.

## Phase 2 demonstration workflow

```text
Input image or game state
    → object extraction
    → object representation
    → object matching and correspondence
    → before-and-after state comparison
    → persistent storage
    → later recognition as the same object
```

## Phase 2 acceptance work

- [ ] Demonstrate extraction and normalized representation on ARC-style grids.
- [ ] Demonstrate stable identity across multiple encounters and transitions.
- [ ] Demonstrate correspondence between parent/current states and repeated examples.
- [ ] Demonstrate movement, recolor, resize, addition, removal, and structural-change detection.
- [ ] Demonstrate regeneration from stored forms and compare regenerated content with observations.
- [ ] Demonstrate duplicate prevention for a re-recognized object.
- [ ] Demonstrate explicit admission of genuinely new residual structure.
- [ ] Add translation, rotation, reflection, recolor, scale, and noise fixtures.
- [ ] Add modest degradation and partial-occlusion fixtures.
- [ ] Add duplicate-identity, false-merge, and false-split tests.
- [ ] Add deterministic encounter replay tests.
- [ ] Add faithful regeneration and topology-preservation tests.
- [ ] Document identity governance, recognition evidence, regeneration, persistence, and replay.

## Raster and occlusion — Future after grid acceptance

- [ ] `ContourFillForm` and matching Prolog predicates.
- [ ] `SpriteAdapter`.
- [ ] Connected-component, contour-extraction, and vector-tracing providers.
- [ ] Fixed-camera raster sequence adapter.
- [ ] Noise, degradation, recolor, and partial-occlusion datasets.
- [ ] Generative completion and consistency validation.
- [ ] Top-down manipulation demonstration.

---

# Phase 3 — Game Object Learner Integration and Predictive Rule Learning

The Phase 3 contracts are connected. This does not assert that rule induction quality, ranking quality, environment coverage, or benchmark acceptance is complete.

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
- [x] `game_object_learner_api.pl` connecting modules through one provider dictionary.
- [x] Prolog test for transition analysis, candidate generation, rule induction/ranking/storage/application, prior prediction, and later grading.

## Stable learner payload — Next

- [ ] Freeze the serialized Game Object Learner payload schema and schema version.
- [ ] Include observation and encounter IDs.
- [ ] Include stable object identities and properties.
- [ ] Include relationships and spatial structure.
- [ ] Include parent/current correspondences and direct differences.
- [ ] Include action information.
- [ ] Include generative representations and artifact references.
- [ ] Include encounter history and provenance.
- [ ] Include competing interpretations and evidence records.
- [ ] Keep debugger, action-tree, and adapter implementation objects outside the serialized boundary.
- [ ] Add structured validation errors and compatibility tests.

## Real transition and rule integration — Next

- [ ] Build payloads from real Phase 2 objects and correspondences.
- [ ] Connect `PipelineGameObjectLearnerPlugin` to actual `Arc3Runner` transitions.
- [ ] Connect Prolog providers to `objects.pl`, `differences.pl`, `similarities.pl`, `rules.pl`, transcripts, and registry facts.
- [ ] Implement transition analysis over real object correspondence evidence.
- [ ] Generate candidate object-level transformations from observed deltas.
- [ ] Preserve multiple competing transformation and rule interpretations.
- [ ] Validate and apply transformations to unseen cases.
- [ ] Induce rules compatible with the evidence-oriented `rules.pl` shape.
- [ ] Rank rules using prior prediction evidence, simplicity, contradiction, and rival interpretations.
- [ ] Store rule evidence only through the authoritative writer/store path.

## Prediction and independent grading — Next

- [ ] Record predictions before ARC3 actions are executed or later outcomes are observed.
- [ ] Capture predicted object identities, properties, relationships, state changes, and optional action recommendations.
- [ ] Grade predictions only from independent ARC3 environment responses.
- [ ] Record successful, failed, partial, and contradicted predictions.
- [ ] Update rule evidence from prediction success or failure.
- [ ] Prove that post-hoc explanations receive no prediction credit.
- [ ] Connect prediction records, outcomes, grades, and solver traces into action-tree READMEs and artifacts.
- [ ] Provide action recommendations to `agent/my_agent.py` through a stable seam without changing its protected contract.

## Phase 3 demonstration workflow

```text
Input game state
    → object perception and recognition
    → persistent object identity
    → structured Game Object Learner handoff
    → state-transition analysis
    → candidate transformation learning
    → prediction of a later state
    → application to a new case
    → independent prediction evaluation
    → prediction, learned rule, or action recommendation
```

## Representative environment progression

- [ ] ARC-style grids.
- [ ] Rendered arcade environments.
- [ ] Fixed-camera physics examples.
- [ ] Top-down manipulation with partial occlusion.

Do not treat the later raster environments as accepted until the exact grid path is deterministic and reproducible.

## Phase 3 acceptance work

- [ ] Demonstrate payload validation, versioning, structured errors, and stable serialization.
- [ ] Demonstrate real Phase 2 object and correspondence handoff.
- [ ] Demonstrate candidate transformation induction from observed examples.
- [ ] Demonstrate multiple competing interpretations and retained positive/negative evidence.
- [ ] Demonstrate learned transformation application to a new case.
- [ ] Demonstrate a prediction recorded before the outcome.
- [ ] Demonstrate independent outcome observation and deterministic grading.
- [ ] Demonstrate positive and negative rule-evidence updates.
- [ ] Demonstrate rejection of post-hoc prediction credit.
- [ ] Demonstrate recognition and completion of a partly occluded object.
- [ ] Demonstrate operation across the approved grid and raster progression.
- [ ] Add integration tests and example workflows.
- [ ] Produce reproducible acceptance commands and exact results.
- [ ] Provide integration documentation, developer notes, and acceptance reports.

---

# Evaluation and reporting infrastructure

- [ ] `BenchmarkRunner`.
- [ ] `PerturbationGenerator`.
- [ ] `AcceptanceEvaluator` and `AcceptanceReport`.
- [ ] `AblationRunner` comparing PROLOG, GPT/LLM, and PYTHON providers.
- [ ] Provider/model/profile transcript comparison tooling.
- [ ] Artifact and prediction evidence summaries in node READMEs.
- [ ] Prediction-improvement-over-experience measurement.
- [ ] Reproducible environment setup and exact command recording.
- [ ] Per-phase acceptance checklist with links to artifacts, transcripts, tests, and demonstrations.

# Cross-language mapping

| Concept | Python | Prolog |
|---|---|---|
| Candidate object | `CandidateObject` | `candidate_object/2` |
| Recognition explanation | planned `RecognitionAccount` | `recognition_account/2` |
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

1. Freeze observation, object, atom, transition, artifact-reference, evidence, and learner-payload schemas.
2. Complete Phase 1 cache validation, replay hashes, provenance, and acceptance evidence.
3. Implement encounter persistence and artifact indexing.
4. Bridge action-tree nodes into Phase 2 observations.
5. Connect the existing object extractor through `GridAdapter`.
6. Fit and regenerate exact grid forms through `turtle_dsl.pl`.
7. Implement deterministic correspondence, recognition, duplicate prevention, and identity governance.
8. Pass grid identity, replay, regeneration, degradation, and partial-visibility tests.
9. Feed real Phase 2 transitions into the connected Phase 3 pipeline.
10. Learn and apply competing transformations and rules.
11. Record predictions before ARC3 actions and grade independent responses.
12. Add rendered arcade, physics, raster, and occlusion providers after the exact grid path is stable.
13. Add benchmark, ablation, transcript comparison, and acceptance reporting.
14. Keep one implementation per runner and all runnable entry points under `scripts/`.

# Non-negotiable technical constraints

- Raw frames are artifacts, not durable concepts.
- Similarity may propose identity but may not define committed identity.
- Embeddings may accelerate lookup but may not create or merge identities or raise confidence.
- New components propose atoms at zero confidence.
- Only `SingleWriter` or its authoritative Prolog equivalent changes durable state or evidence.
- Objects are demoted or tombstoned, never erased with their provenance.
- A rule receives positive evidence only when its prediction existed before the outcome.
- Core contracts contain no unnecessary ARC-specific or raster-specific assumptions.
- The same starting store and encounter log must replay to the same handles and confidence values.
- LLM artifacts remain explicitly provider-backed and are never presented as native Python symbolic implementations.
- Historical Markdown transcripts remain immutable comparison/cache records; latest `.pl` files remain the selected working view.

See [SOW_PHASE_ARCHITECTURE.md](SOW_PHASE_ARCHITECTURE.md) for the architectural mapping and [FILE_TREE.md](FILE_TREE.md) for repository ownership.

[← Back to top-level README](README.md)
