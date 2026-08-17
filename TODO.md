[← Back to top-level README](README.md)

# TODO — Work We Need to Do

## Document scope

This is the concrete implementation list for the work we are actively doing together. It is intentionally shorter than the architecture and does not repeat the complete SOW.

Related documents:

- [SOW_PHASE_ARCHITECTURE.md](SOW_PHASE_ARCHITECTURE.md) — detailed classes, modules, contracts, boundaries, and design rationale.
- [SOW_DELIVERABLES.md](SOW_DELIVERABLES.md) — delivered, partial, and open SOW outcomes with evidence links.
- [FILE_TREE.md](FILE_TREE.md) — repository ownership map.

When a operation here is completed, update the relevant checkbox in [SOW_DELIVERABLES.md](SOW_DELIVERABLES.md) and link the implementation or evidence.

## Working rules

- Treat Phase 1 as the delivered debugger, evidence, replay, provider-hook, README, transcript, and artifact-inspection foundation.
- Keep semantic object perception, persistent recognition, calibrated confidence, learning, and prediction out of the debugger core.
- Keep one runner, action-tree store, provider pipeline, prompt config, transcript history, debugger identity registry, and Turtle interpreter.
- Extend `object_registry.pl`; do not create an unrelated identity namespace.
- Keep runnable programs in `scripts/`.
- Do not create phase directories.
- Do not rename protected Kaggle files.
- Do not present provider-generated artifacts as independently verified native reasoning.
- Do not let embeddings or similarity alone commit identity.
- Store grid objects with movement-and-pen-width Turtle programs rather than box-filling programs.
- Record predictions before observing outcomes.

---

# Phase 1 — Post-delivery debugger maintenance

Architecture: [Phase 1 debugger architecture](SOW_PHASE_ARCHITECTURE.md#phase-1--arc3-debugger-and-extensible-inspection-foundation)

Deliverables: [Completed Phase 1 checklist](SOW_DELIVERABLES.md#phase-1--arc3-debugger-and-extensible-inspection-foundation)

These are maintenance and extension operations, not missing Phase 1 SOW deliverables:

- [ ] Keep command registration pluggable so new Phase 2 and Phase 3 services can be added without changing the debugger UI loop.
- [ ] Add explicit provider capability discovery and structured unsupported-command messages.
- [ ] Keep provider outputs visibly labeled by provider, model, prompt sections, source node, and generation time.
- [ ] Add stronger cache compatibility checks where useful without changing the delivered inspection behavior.
- [ ] Keep restored transcript provenance and `object_registry.pl` identity provenance visible in node READMEs.
- [ ] Add optional native Windows smoke coverage for launch-path resolution and one recorded ARC3 node.
- [x] Keep Phase 2 semantic records and Phase 3 prediction records linked from nodes rather than embedded into `Arc3Runner`.

---

# Phase 2 — Object Perception, Recognition, and Persistent Memory

Architecture: [Phase 2 object architecture](SOW_PHASE_ARCHITECTURE.md#phase-2--object-perception-recognition-and-persistent-memory)

Deliverables: [Phase 2 checklist](SOW_DELIVERABLES.md#phase-2--object-perception-recognition-and-persistent-memory)

## Freeze the Phase 2 records

Keep the shared records in `python/object_memory/models.py`; do not create another model package.

- [x] Add or finalize `Observation` as a semantic record layered over the rendered observation already stored by Phase 1.
- [x] Add or finalize `EncounterRecord` with a reference to its Phase 1 action-tree node.
- [x] Add `RecognitionAccount` explaining matches, changes, rivals, residuals, confidence, and decision source.
- [x] Add `ArtifactRef` and `ProvenanceRef`.
- [x] Add `InstanceParameters` for position, orientation, scale, appearance, and supported transformations.
- [x] Add `MatchProposal`, `MergeDecision`, and `SplitDecision`.
- [x] Add `EvidenceRecord` supporting positive and negative evidence.
- [x] Add normalized per-object Turtle-program references.
- [x] Add schema versions and deterministic identifiers for observations, encounters, artifacts, evidence, proposals, recognition accounts, and identity decisions. Persistent object identifiers remain governed by `object_registry.pl`.

## Connect perception providers

- [x] Inspect the current symbolic grid-object extraction code.
- [x] Wrap it behind `GridAdapter` rather than rewriting it.
- [ ] Normalize components, geometry, properties, relationships, topology, holes, enclosures, bars, lines, and compound objects.
- [x] Preserve exact logical-grid coordinates and source artifact references.
- [ ] Add pluggable image and simple-video adapters behind the same normalized contracts.
- [x] Keep provider-specific intermediate data out of persistent object records unless referenced through provenance.
- [x] Add fixtures for irregular geometry, topology, holes, enclosure, line thickness, and disconnected strokes.

## Store one Turtle program per recognized grid object

- [x] Make each recognized grid object store or reference a Turtle program that redraws that object.
- [x] Use forward movement and rotation rather than coordinate-box enumeration.
- [x] Use pen-up and pen-down state for stroke positioning and repositioning.
- [x] Use pen width for supported thick lines rather than drawing adjacent filled rectangles.
- [x] Preserve supported color or drawing-state changes.
- [x] Connect `CellLogoForm.render()` to `prolog/turtle_dsl.pl` through `SWIPrologBridge`.
- [x] Define normalized Turtle-program storage and artifact references.
- [x] Implement `fit`, `distance`, residual measurement, and description length.
- [x] Compare regenerated cells with the source object.
- [x] Preserve holes, disconnected strokes, topology, and line thickness.
- [ ] Retain competing Turtle programs with their fit scores and provenance when the representation is ambiguous.
- [x] Add tests rejecting box-filling shortcuts for shapes that should use movement and pen width.

## Extend `object_registry.pl` into persistent identity

- [x] Reuse the readable identities maintained by the Phase 1 debugger.
- [x] Map provider-proposed identities to persistent semantic identities without discarding provenance.
- [x] Match stable candidates across consecutive parent/current observations and persist their correspondence proposals and signed evidence.
- [x] Match objects across repeated encounters and examples through unresolved, persisted proposals over the latest known instance for every durable identity.
- [x] Preserve multiple competing match proposals.
- [x] Record matched and changed properties plus supporting and contradicting evidence.
- [x] Route identity merge and split decisions through `SingleWriter` or authoritative Prolog logic.
- [x] Prevent repeat commits from overwriting or duplicating an existing durable identity; return the calibrated object for the same contract and reject conflicting payloads.
- [x] Keep false merges and false splits reversible through evidence and provenance.

## Implement recognition and change detection

- [x] Recognize declared translation, rotation, reflection, recoloring, scaling, noise, and partial visibility as explicit correspondence transformations with signed evidence.
- [x] Detect moved, recolored, resized, reshaped, appeared, disappeared, split, and merged objects from explicit correspondences.
- [x] Distinguish declared transformations from provisional residual candidates representing unexplained, potentially new structure; persist and inspect residuals through live capture and replay.
- [x] Keep incomplete or noisier encounters from overwriting the best complete stored form while retaining their latest position and supported transformations.
- [x] Compare Turtle reconstruction fit as one attributable source of signed recognition evidence.
- [ ] Keep embeddings advisory for retrieval and proposal generation only.

## Implement evidence and calibrated confidence

- [x] Accumulate attributable positive and negative recognition evidence through `SingleWriter`.
- [x] Derive calibrated object-identity confidence reproducibly from accumulated signed evidence.
- [x] Prevent similarity scores from being treated directly as committed confidence.
- [x] Make confidence updates reproducible and attributable to evidence records.
- [x] Preserve typed confidence and lifecycle history through evidence, merge, split, demotion, tombstoning, and reversal; include it in semantic snapshots and durable Prolog storage.
- [x] Show recognition accounts, evidence, rivals, advisory similarity, decision source, and calibrated confidence through the Phase 1 README inspection surface.

## Implement persistent memory

- [x] Implement append-only semantic `EncounterLog` linked to the encounter history already recorded by Phase 1.
- [x] Implement deterministic, idempotent replay of semantic observations, encounters, artifacts, Turtle references, proposals, accounts, evidence, and atoms from an exact store snapshot.
- [x] Implement `SymbolicStore` over durable, reloadable `semantic_record/3` SWI-Prolog storage while retaining the backend seam for AtomSpace.
- [x] Implement `ArtifactIndex` for exact artifact lookup by stable identifier and semantic artifact type; populate it as observations, encounters, and Turtle programs enter `SymbolicStore`.
- [x] Add active, demoted, and tombstoned lifecycle states.
- [x] Preserve provenance when identities are merged, split, demoted, or tombstoned.
- [x] Store observations, encounters, Turtle programs, proposals, recognition accounts, signed evidence, object changes, confidence history, atoms, and associated artifacts through the semantic-store boundary.

## Phase 2 tests and demonstrations

- [x] Stable persistent identity across multiple encounters and state transitions.
- [x] Correspondence across before/after states and repeated examples.
- [x] Movement, recolor, resize, addition, removal, split, merge, and structural-change detection.
- [x] Per-object Turtle regeneration using movement, rotation, pen state, and pen width.
- [x] Regenerated/source comparison and residual measurement.
- [x] Duplicate-prevention test.
- [x] False-merge and false-split tests.
- [x] Translation, rotation, reflection, recolor, scale, noise, and partial-visibility fixtures.
- [ ] Modest degradation and partial-occlusion recognition.
- [x] Positive and negative evidence accumulation.
- [x] Confidence calibration and reproducibility.
- [x] Deterministic semantic-memory replay over exact records linked from Phase 1 action-tree manifests, including predecessor-ordered encounter chains.

## Phase 2 demonstration workflow

Run `python scripts/phase2_object_memory_demo.py` for a deterministic real-grid
demonstration. See
[`workbench/docs/design/PHASE2_OBJECT_MEMORY_DEMONSTRATION.md`](workbench/docs/design/PHASE2_OBJECT_MEMORY_DEMONSTRATION.md)
for the command, inspectable output paths, and regression evidence.

```text
Input image or game state
    → object extraction
    → normalized object representation and Turtle program
    → matching and correspondence
    → before-and-after comparison
    → evidence and confidence update
    → persistent storage
    → Turtle regeneration
    → later recognition as the same object
```

---

# Phase 3 — Game Object Learner Integration and Predictive Rule Learning

Architecture: [Phase 3 learner architecture](SOW_PHASE_ARCHITECTURE.md#phase-3--game-object-learner-integration-and-predictive-rule-learning)

Deliverables: [Phase 3 checklist](SOW_DELIVERABLES.md#phase-3--game-object-learner-integration-and-predictive-rule-learning)

## Freeze the learner boundary

- [ ] Freeze the serialized `GameObjectLearnerPayload` schema and version.
- [ ] Include semantic observation and encounter IDs.
- [ ] Include stable identities, properties, relationships, correspondences, and direct differences.
- [ ] Include action information, Turtle-program references, artifacts, history, evidence, confidence, and provenance.
- [ ] Include competing object and correspondence interpretations where relevant.
- [ ] Exclude debugger implementation objects such as `StateNode`, terminal controls, and adapter instances.
- [ ] Add structured validation errors and serialization compatibility tests.
- [ ] Validate source, Turtle-program, identity, evidence, and provenance references.

## Connect real Phase 2 transitions

- [ ] Build learner payloads from real Phase 2 objects, correspondences, and semantic encounters.
- [ ] Connect `Arc3Runner` transitions to `PipelineGameObjectLearnerPlugin` through normalized payloads.
- [ ] Connect Prolog providers to registry, objects, differences, similarities, rules, transcripts, and evidence.
- [ ] Analyze actual before/action/after object transitions.
- [ ] Generate candidate object-level transformations from real deltas.
- [ ] Preserve competing transformation interpretations.
- [ ] Apply transformations to previously unseen cases.

## Learn, critique, and rank competing rules

- [ ] Induce multiple candidate rules with explicit assumptions.
- [ ] Generate critiques identifying missing evidence, contradictions, and overgeneralization.
- [ ] Attach supporting and contradicting evidence.
- [ ] Maintain rival rule sets rather than selecting one explanation too early.
- [ ] Rank rules using simplicity, coverage, contradiction, applicability precision, and prediction history.
- [ ] Refine calibrated rule confidence or probability from actual prediction results.
- [ ] Keep bootstrap probabilities displayed by Phase 1 separate from verified Phase 3 probability updates.
- [ ] Store rule identity, assumptions, critiques, probability, evidence, and provenance.

## Make prediction evidence real

- [ ] Record predictions before ARC3 actions or later outcomes are observed.
- [ ] Predict object identities, properties, relationships, changes, later state, or action recommendation as appropriate.
- [ ] Store the evidence available at prediction time.
- [ ] Capture the independent environment outcome through a separate outcome channel.
- [ ] Grade success, failure, partial match, contradiction, and ungradable outcomes deterministically.
- [ ] Update positive and negative rule evidence, probability, and ranking from prediction results.
- [ ] Prove that post-hoc explanations receive no prediction credit.
- [ ] Preserve the original prediction, outcome, grade, and update history.

## Write learner evidence back to the debugger

- [ ] Link candidate transformations into action-tree evidence.
- [ ] Link competing rules, assumptions, critiques, and confidence or probability estimates.
- [ ] Link pre-outcome predictions and independently observed outcomes.
- [ ] Link grades and positive or negative evidence updates.
- [ ] Link learned rules and optional action recommendations.
- [ ] Make node READMEs trace each result back to source observations, Phase 2 objects, provider calls, and learner records.
- [ ] Keep this writeback pluggable so the debugger remains independent of learner internals.

## Phase 3 tests and demonstrations

- [ ] Payload validation and structured errors.
- [ ] Real Phase 2-to-Phase 3 handoff.
- [ ] Candidate transformation induction from actual object deltas.
- [ ] Rival interpretations with assumptions, critiques, positive evidence, and negative evidence.
- [ ] Learned transformation applied to a new case.
- [ ] Rule ranking and confidence refinement from prediction history.
- [ ] Prediction recorded before outcome.
- [ ] Independent outcome grading.
- [ ] Post-hoc-credit rejection.
- [ ] Debugger README writeback of rules, critiques, probabilities, predictions, and grades.
- [ ] Partial-occlusion recognition and completion.

## Phase 3 demonstration workflow

```text
Input game state
    → object perception and persistent identity
    → structured learner handoff
    → transition analysis
    → competing transformations and rules
    → assumptions, critiques, confidence, and evidence
    → pre-outcome prediction
    → application to a new case
    → independent evaluation
    → updated evidence, learned rule, or action recommendation
```

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

For each finished operation:

1. merge the implementation and tests;
2. add or update demonstration evidence;
3. link the relevant files, action-tree nodes, Turtle programs, transcripts, tests, predictions, or reports from [SOW_DELIVERABLES.md](SOW_DELIVERABLES.md);
4. check off the deliverable only when the evidence is reproducible.

[← Back to top-level README](README.md)
