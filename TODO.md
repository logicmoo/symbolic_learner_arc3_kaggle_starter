[← Back to top-level README](README.md)

# TODO — Work We Need to Do

## Document scope

This is the concrete implementation list for the work we are actively doing together. It is intentionally shorter than the architecture and avoids repeating the complete SOW.

Related documents:

- [SOW_PHASE_ARCHITECTURE.md](SOW_PHASE_ARCHITECTURE.md) — detailed classes, modules, contracts, and design rationale.
- [SOW_DELIVERABLES.md](SOW_DELIVERABLES.md) — contractual deliverables and check-off evidence.
- [FILE_TREE.md](FILE_TREE.md) — repository ownership map.

When a task here is completed, update the relevant checkbox in [SOW_DELIVERABLES.md](SOW_DELIVERABLES.md) and link the implementation or evidence.

## Working rules

- Keep one runner, action-tree store, provider pipeline, prompt config, transcript history, identity authority, and Turtle implementation.
- Keep runnable programs in `scripts/`.
- Do not create phase directories.
- Do not rename protected Kaggle files.
- Do not treat LLM artifacts as native deterministic reasoning.
- Do not let embeddings or similarity commit identity.
- Record predictions before observing outcomes.

---

# Now — Stabilize the Phase 1 evidence path

Architecture: [ARC3 debugger and state architecture](SOW_PHASE_ARCHITECTURE.md#arc3-debugger-and-state-architecture)

Deliverables: [Phase 1 checklist](SOW_DELIVERABLES.md#phase-1--grid-infrastructure-and-arc3-debugger-foundation)

- [ ] Define canonical state and action ordinals shared by history, action trees, replay, observations, and learner payloads.
- [ ] Add schema versions to `state.json`, transcript metadata, generated artifact metadata, and learner records.
- [ ] Add immutable `Observation` or `StateSnapshot` records without replacing `StateNode` or `StepRecord`.
- [ ] Bridge `StepRecord`, `StateNode`, image hash, action data, and environment state into normalized observations.
- [ ] Validate cached artifacts before reuse using schema version, image/state hash, registry version, provider/model/profile, prompt sections, and requested artifact set.
- [ ] Add explicit artifact-set hashes to LLM transcripts.
- [ ] Ensure every artifact from one combined request uses the same registry version and identity set.
- [ ] Add stable evidence and provenance references shared by LLM and native symbolic paths.
- [ ] Connect all six Prolog debugger commands to normalized Prolog APIs.
- [ ] Add a native Windows smoke test that records resolved paths and captures one ARC3 state.
- [ ] Add deterministic replay and state/image-hash tests.
- [ ] Add stale-cache rejection tests.
- [ ] Add Prolog syntax and artifact-schema validation before cache acceptance.

## Phase 1 demonstrations to record

- [ ] Record game and level selection.
- [ ] Record state, action, observation, image, and execution history capture.
- [ ] Record action-tree browsing and parent/child navigation.
- [ ] Record reset, restart, replay, and history navigation.
- [ ] Record stable object identities over a multi-step branch.
- [ ] Record current-state and parent-transition analysis.
- [ ] Compare at least two providers or analysis levels using Markdown transcripts.
- [ ] Restore an older transcript and verify the latest `.pl` files and README.

---

# Phase 2 — Object perception and persistent memory

Architecture: [Phase 2 object perception and memory architecture](SOW_PHASE_ARCHITECTURE.md#phase-2-object-perception-and-memory-architecture)

Deliverables: [Phase 2 checklist](SOW_DELIVERABLES.md#phase-2--object-perception-recognition-and-persistent-memory)

## Normalize the core records

- [ ] Add `Observation`.
- [ ] Add `EncounterRecord`.
- [ ] Add `RecognitionAccount`.
- [ ] Add `ArtifactRef` and `ProvenanceRef`.
- [ ] Add `InstanceParameters`.
- [ ] Add `MatchProposal`, `MergeDecision`, and `SplitDecision`.
- [ ] Add `EvidenceRecord`.
- [ ] Keep these in `python/object_memory/models.py`; do not create another model package.

## Connect the existing grid extractor

- [ ] Inspect the current symbolic grid-object extraction code.
- [ ] Wrap it behind `GridAdapter` instead of rewriting it.
- [ ] Normalize components, properties, relationships, topology, holes, enclosures, bars, lines, and compound objects.
- [ ] Preserve exact logical-grid coordinates and source artifact references.
- [ ] Add fixtures for irregular geometry and topology preservation.

## Make stored objects generative

- [ ] Connect `CellLogoForm.render()` to `prolog/turtle_dsl.pl` through `SWIPrologBridge`.
- [ ] Define normalized Turtle-program references.
- [ ] Implement `fit`, `distance`, residual measurement, and description length.
- [ ] Compare regenerated cells to observed cells.
- [ ] Preserve holes, disconnected strokes, and exact topology.

## Implement correspondence and recognition

- [ ] Match objects across parent/current states.
- [ ] Match objects across repeated encounters and examples.
- [ ] Record matched and changed properties plus supporting and contradicting evidence.
- [ ] Preserve multiple competing match proposals.
- [ ] Support translation, rotation, reflection, recolor, scale, noise, and partial visibility where appropriate.
- [ ] Detect moved, recolored, resized, reshaped, appeared, disappeared, split, and merged objects.
- [ ] Prevent duplicate durable storage when an object is recognized again.
- [ ] Route merge/split decisions through `SingleWriter` or authoritative Prolog logic.

## Implement persistence

- [ ] Implement append-only `EncounterLog` with deterministic hashes and replay.
- [ ] Implement `SymbolicStore` over the selected Prolog or Atomspace storage.
- [ ] Implement `ArtifactIndex` for frames, masks, Turtle programs, reconstructions, embeddings, transcripts, evidence, predictions, and outcomes.
- [ ] Add active, demoted, and tombstoned lifecycle states.
- [ ] Preserve provenance when identities are merged, split, demoted, or tombstoned.
- [ ] Keep embeddings advisory only.

## Phase 2 tests and demonstrations

- [ ] Stable identity across multiple encounters.
- [ ] Correspondence across before/after states.
- [ ] Movement, recolor, resize, addition, removal, and structural-change detection.
- [ ] Object regeneration and comparison with the observation.
- [ ] Duplicate-prevention test.
- [ ] False-merge and false-split tests.
- [ ] Translation, rotation, reflection, recolor, scale, and noise fixtures.
- [ ] Modest degradation and partial-occlusion fixtures.
- [ ] Deterministic encounter replay.

---

# Phase 3 — Game Object Learner and prediction

Architecture: [Phase 3 Game Object Learner architecture](SOW_PHASE_ARCHITECTURE.md#phase-3-game-object-learner-architecture)

Deliverables: [Phase 3 checklist](SOW_DELIVERABLES.md#phase-3--game-object-learner-integration-and-predictive-rule-learning)

## Freeze the learner boundary

- [ ] Freeze `GameObjectLearnerPayload` schema and version.
- [ ] Include observation and encounter IDs.
- [ ] Include stable identities, properties, relationships, correspondences, and differences.
- [ ] Include action information, generative forms, artifacts, history, evidence, and provenance.
- [ ] Exclude debugger implementation objects such as `StateNode` and adapter instances.
- [ ] Add structured validation errors and serialization compatibility tests.

## Connect real transitions

- [ ] Build payloads from real Phase 2 objects and encounters.
- [ ] Connect `Arc3Runner` transitions to `PipelineGameObjectLearnerPlugin`.
- [ ] Connect Prolog providers to registry, objects, differences, similarities, rules, and transcript evidence.
- [ ] Generate candidate object-level transformations from actual deltas.
- [ ] Preserve competing transformation and rule interpretations.
- [ ] Apply transformations to unseen cases.

## Make prediction evidence real

- [ ] Record predictions before ARC3 actions are executed.
- [ ] Predict object identities, properties, relationships, changes, later state, or action as appropriate.
- [ ] Capture the independent environment outcome.
- [ ] Grade success, failure, partial match, and contradiction deterministically.
- [ ] Update rule evidence through the authoritative writer/store path.
- [ ] Prove that post-hoc explanations receive no prediction credit.
- [ ] Link predictions, outcomes, grades, and rule evidence into action-tree artifacts and READMEs.
- [ ] Expose optional action recommendations to `agent/my_agent.py` through a stable seam.

## Phase 3 tests and demonstrations

- [ ] Payload validation and structured errors.
- [ ] Real Phase 2-to-Phase 3 handoff.
- [ ] Candidate transformation induction.
- [ ] Rival interpretations with positive and negative evidence.
- [ ] Learned transformation applied to a new case.
- [ ] Prediction recorded before outcome.
- [ ] Independent outcome grading.
- [ ] Post-hoc-credit rejection.
- [ ] Partial-occlusion recognition and completion.

---

# After exact-grid acceptance

Architecture: [Environment progression](SOW_PHASE_ARCHITECTURE.md#environment-progression)

- [ ] Rendered arcade fixtures.
- [ ] Fixed-camera physics fixtures.
- [ ] `SpriteAdapter` and contour/vector providers.
- [ ] Top-down manipulation fixtures.
- [ ] Partial-occlusion completion datasets.
- [ ] Benchmark runner.
- [ ] Perturbation generator.
- [ ] Provider/mode ablation runner.
- [ ] Transcript comparison and scoring tools.
- [ ] Acceptance report generator.

# Completion procedure

For each finished task:

1. merge the implementation and tests;
2. add or update the demonstration evidence;
3. link the relevant files, transcripts, tests, or reports from [SOW_DELIVERABLES.md](SOW_DELIVERABLES.md);
4. check off the deliverable only when the evidence is reproducible.

[← Back to top-level README](README.md)
