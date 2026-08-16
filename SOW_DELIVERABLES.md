[← Back to top-level README](README.md)

# SOW Deliverables Checklist — Image Perception to Recognizable Memory

## Document scope

This is the delivery checklist. It follows the revised three-phase SOW language and links each outcome to implementation evidence or remaining work.

Related documents:

- [SOW_PHASE_ARCHITECTURE.md](SOW_PHASE_ARCHITECTURE.md) — detailed technical design, classes, modules, boundaries, and architecture work.
- [TODO.md](TODO.md) — the concrete work we are actively implementing.
- [FILE_TREE.md](FILE_TREE.md) — repository ownership map.

## Status rules

- `[x]` — delivered with repository or demonstration evidence.
- `[ ] **Partial**` — meaningful contracts or infrastructure exist, but the complete deliverable or acceptance evidence is unfinished.
- `[ ] **Open**` — not yet implemented or not yet demonstrated.

A Phase 1 provider artifact can be delivered as a visible debugger output even when later phases are responsible for improving the underlying semantic or predictive algorithm.

## Delivery windows

| Phase | Anticipated delivery window |
|---|---:|
| Phase 1 — ARC3 Debugger and Extensible Inspection Foundation | 3 weeks |
| Phase 2 — Object Perception, Recognition, and Persistent Memory | 1 month |
| Phase 3 — Game Object Learner Integration and Predictive Rule Learning | 1 month |
| Overall sequence | Approximately 3 months |

---

# Phase 1 — ARC3 Debugger and Extensible Inspection Foundation

Architecture: [Phase 1 debugger architecture](SOW_PHASE_ARCHITECTURE.md#phase-1--arc3-debugger-and-extensible-inspection-foundation)

Post-delivery maintenance: [TODO — Phase 1 maintenance](TODO.md#phase-1--post-delivery-debugger-maintenance)

Phase 1 delivers the debugger, evidence-recording surface, expandable command framework, provider-artifact inspection, and replay foundation. It does not claim that the debugger itself implements the final algorithms shown by bootstrap providers.

## ARC3 interaction and recorded evidence

- [x] Adapt the existing ARC debugger workflow to ARC3.  
  Evidence: [`python/arc3_runner.py`](python/arc3_runner.py), [`scripts/interactive_runner.py`](scripts/interactive_runner.py), [`DEBUGGER.md`](DEBUGGER.md).

- [x] Load and interact with selected ARC3 games and levels.  
  Evidence: game/level lifecycle and interactive controls in `Arc3Runner`.

- [x] Display and record rendered observations, actions, available metadata, and execution history.  
  Evidence: `StepRecord`, `image.png`, `state.json`, action history, exports, and node READMEs.

- [x] Store gameplay encounters and explored action paths in a GitHub-browsable action tree.  
  Evidence: [`python/action_tree.py`](python/action_tree.py), deterministic action directories, parent/child links, and generated READMEs.

- [x] Preserve encounter and action history with deterministic replay, reset, restart, and path navigation.  
  Evidence: runner history/replay/reset/restart behavior and action-tree navigation.

## Pluggable command and provider framework

- [x] Provide expandable command hooks for replaceable LLM, Prolog, Python, and external providers.  
  Evidence: `python/multillm_runner.py`, `python/gpt_bridge.py`, `python/swipl_bridge.py`, provider cycling, and symbolic command entry points.

- [x] Supply current and previous observations, action context, and available metadata to providers and display their results.  
  Evidence: combined parent/current image and context requests in `GptArcAnalyzer`.

- [x] Keep the debugger independent of the provider’s internal algorithm.  
  Evidence: provider routing, normalized artifact handling, separate `.pl` outputs, and replaceable command hooks.

## Readable identities and inspectable provider artifacts

- [x] Maintain `object_registry.pl` plus readable provider identities and provenance for browsing and later workflows.  
  Evidence: level-wide registry handling, friendly-ID enforcement, registry-backed state artifacts, and restored-transcript provenance.

- [x] Display provider-generated object descriptions.  
  Evidence: `objects.pl` embedded and linked from node READMEs.

- [x] Display provider-generated differences and proposed changes.  
  Evidence: `differences.pl` and current/previous observation context.

- [x] Display provider-generated similarities and proposed correspondences.  
  Evidence: `similarities.pl`.

- [x] Display Turtle mocks and reconstructions.  
  Evidence: `turtle_from_image.pl`, `turtle_from_diff.pl`, Turtle interpreter support, and the Phase 1 demonstration video.

- [x] Display candidate rules, critiques, and probability or confidence outputs.  
  Evidence: `rules.pl`, provider prompt/output schema, and README-visible provider artifacts demonstrated during Phase 1.

- [x] Make the provider artifacts inspectable through node README files.  
  Evidence: generated README embedding and transcript links.

The checked items above claim the delivered ability to **show and preserve** these outputs. Phase 2 implements and calibrates object, identity, correspondence, confidence, and Turtle-object quality. Phase 3 implements and evaluates transformation rules, predictions, probabilities, and recommendations.

## Artifact cache, comparison, and restoration

- [x] Save, cache, link, compare, and restore provider-generated artifacts.  
  Evidence: mutable latest `.pl` view, immutable `llm_adapter_*.md` transcripts, transcript selection, and `restore_transcript()`.

- [x] Preserve provider, adapter, model, analysis level, profile, token budget, images, exact prompt, timing, repair history, and raw response.  
  Evidence: [`python/llm_transcripts.py`](python/llm_transcripts.py).

- [x] Place restorable generated artifacts at the top of each completed transcript.  
  Evidence: artifact-first transcript layout and tests.

- [x] Keep debugging details and raw provider responses below the artifact snapshot.  
  Evidence: transcript layout and response-at-bottom tests.

- [x] Make node `README.md` identify the active transcript and link historical runs.  
  Evidence: [`python/llm_readme_patch.py`](python/llm_readme_patch.py).

## Runtime and documentation

- [x] Keep provider definitions and reusable prompt text together under `config/`.  
  Evidence: [`config/llm_providers.json`](config/llm_providers.json).

- [x] Allow each provider to select an ordered prompt-section list and omit sections such as `transitions`.  
  Evidence: provider prompt-section configuration and tests.

- [x] Resolve code, config, and action-tree storage independently.  
  Evidence: [`scripts/_runtime.py`](scripts/_runtime.py), [`python/project_paths.py`](python/project_paths.py).

- [x] Print where configuration is loaded from and where action trees are saved.  
  Evidence: startup resolved-path report.

- [x] Provide integration seams for later perception, memory, transformation, rule-learning, prediction, and action-recommendation stages.  
  Evidence: shared providers, object-memory contracts, learner plugin contracts, Prolog bridge, and action-tree artifact slots.

- [x] Document debugger architecture, action trees, hooks, artifacts, evidence, provenance, and replay controls.  
  Evidence: [`README.md`](README.md), [`DEBUGGER.md`](DEBUGGER.md), [`config/README.md`](config/README.md), [`SOW_PHASE_ARCHITECTURE.md`](SOW_PHASE_ARCHITECTURE.md), and [`FILE_TREE.md`](FILE_TREE.md).

## Phase 1 status

**Phase 1 is delivered.** Optional cache hardening, capability discovery, schema improvements, additional smoke tests, and later-phase integration are maintenance or extension work, not missing Phase 1 semantic deliverables.

---

# Phase 2 — Object Perception, Recognition, and Persistent Memory

Architecture: [Phase 2 object architecture](SOW_PHASE_ARCHITECTURE.md#phase-2--object-perception-recognition-and-persistent-memory)

Active work: [TODO — Phase 2](TODO.md#phase-2--object-perception-recognition-and-persistent-memory)

Phase 2 implements the semantic object layer behind the Phase 1 debugger. It uses the history and provider demonstrations already preserved by the debugger but is responsible for repeatable object quality, persistent identity, regeneration, evidence, confidence, and memory.

## Perception and normalized representation

- [ ] **Partial** Implement pluggable perception providers for grid inputs.  
  Existing evidence: `CandidateObject`, `PerceptionAdapter`, and `GridAdapter`; the adapter now wraps the existing `workbench.server.runtime.analyze_grid` extractor and emits normalized `Observation`, artifact/provenance, and candidate contracts without duplicating extraction logic.
  Remaining: broaden normalized topology/relationship coverage and connect the adapter to live semantic encounter creation.

- [ ] **Open** Implement pluggable perception providers for image and simple-video inputs.

- [ ] **Partial** Extract objects and represent geometry, structure, properties, relationships, position, orientation, scale, and appearance.  
  Existing evidence: frozen versioned contracts plus deterministic grid extraction of cells, exact bounds, boundary geometry, shape/color/appearance, hole regions, connected topology, line thickness, and pairwise spatial relationships; semantic capture persists normalized instance position/scale/appearance and source provenance.
  Remaining: compound-object structure, orientation inference, richer relations, and normalization for raster/video adapters.

## Persistent identity and correspondence

- [ ] **Partial** Extend `object_registry.pl` into persistent identities across examples, encounters, and transitions while preserving Phase 1 provenance.  
  Existing evidence: readable state-transition identities, lifecycle governance, and a managed append-only `semantic_identity_decisions.pl` extension loaded by every registry rewrite. Only canonical friendly IDs are accepted; encounter, decision, evidence, accepted/reversed status, and live SWI-Prolog queries are covered.
  Remaining: automatically propose and authorize identity decisions from consecutive live encounters and carry registry state across examples.

- [ ] **Partial** Match corresponding objects between states and repeated encounters while retaining competing proposals.  
  Existing evidence: deterministic proposals retain every rival and explain matched/changed properties; `RecognitionSession` derives the latest known instance for each durable identity from encounter history and persists every proposal plus an unresolved recognition account. `RegistryCorrespondenceAuthority` requires explicit friendly-ID selection plus attributable evidence, calibrates through `SingleWriter`, creates a resolved recognition account, and records Prolog decision history. Perfect similarity alone is rejected.
  Live `SemanticGridCaptureObserver` sessions now invoke this path when durable identity history is available and link proposal/account artifacts into the action-tree node. Remaining: add topology/Turtle evidence generation and explicit authorization controls.

- [ ] **Open** Recognize recurring objects under supported translation, rotation, scale, reflection, recoloring, noise, and partial visibility.

  Existing partial evidence: correspondence proposals explicitly recognize declared translation, rotation, scale, and recoloring changes. Reflection, noise, partial visibility, and real-history recognition remain open.

- [ ] **Partial** Detect movement, recoloring, resizing, addition, removal, splitting, merging, and structural change.  
  Existing evidence: provider difference artifacts and transition contracts plus deterministic `ObjectChange` records and `ChangeDetector` coverage for moved, recolored, resized, reoriented, reshaped, appeared, disappeared, one-to-many split, and many-to-one merge cases.
  Remaining: connect detection to live before/after semantic encounters and persist evidence-backed changes.

## Per-object Turtle programs and regeneration

- [ ] **Partial** Store every recognized grid object with a Turtle program.  
  Existing evidence: `GenerativeForm`, `CellLogoForm`, Turtle artifacts, Turtle DSL, and normalized versioned `TurtleProgramRef`/`ArtifactRef` contracts.
  Remaining: persistent one-program-per-object storage and normalized references.

- [ ] **Partial** Require the Turtle program to redraw the object through movement, rotation, pen state, and pen width rather than filled coordinate boxes.
  Existing evidence: extracted programs use `set_pos`, `rot`, `fwd`, `penup`/`pendown`, and canonical `pen_width`; supported thick rectangles render as one width-aware stroke and a regression test rejects row-by-row box filling.
  Remaining: extend stroke optimization beyond exactly representable width-1-through-4 rectangles and line forms.

- [ ] **Partial** Execute the stored Turtle program to regenerate the object and compare it with the source observation.  
  Existing evidence: `CellLogoForm` now executes extracted programs through `SWIPrologBridge` and the canonical `prolog/turtle_dsl.pl`; regenerated-cell fit, distance, normalized residual, and description-length metrics have live SWI-Prolog coverage.
  Remaining: invoke and persist these metrics automatically in the recognition pipeline.

- [ ] **Open** Preserve exact holes, disconnected strokes, topology, and supported thickness through the stored Turtle program.

## Residuals, duplicates, evidence, and confidence

- [ ] **Open** Distinguish recognized or explained content from residual, potentially new object structure.

- [ ] **Open** Prevent duplicate persistent storage when an existing object is recognized again.

  Existing partial evidence: semantic store writes and merge/split decisions are idempotent by deterministic identity and reject conflicting reuse. Recognition-driven duplicate prevention remains open.

- [ ] **Partial** Accumulate positive and negative recognition evidence and provenance across the encounter history preserved by Phase 1.  
  Existing evidence: `SingleWriter` accepts frozen positive/negative `EvidenceRecord` values, checks their subject, deduplicates stable evidence IDs, preserves base provenance, and derives confidence from signed weights independently of arrival order.
  Remaining: durable encounter-linked recognition evidence and domain calibration against fixtures.

- [ ] **Partial** Refine and calibrate confidence for object identity, correspondence, and competing interpretations.
  Existing evidence: deterministic Laplace-style confidence derived from attributable supporting and contradicting evidence, with event history and order-independence tests.
  Remaining: correspondence/rival interpretation calibration, empirical calibration curves, and lifecycle-history preservation.

## Persistent symbolic memory and replay

- [ ] **Partial** Maintain persistent symbolic memory for recognized objects, observations, Turtle programs, and associated artifacts.  
  Existing evidence: `SymbolicMemory`, a backend-neutral `SymbolicStore` facade with write-once exact identity, a replaceable `SemanticStoreBackend` boundary, observation/encounter/Turtle composition, and an `ArtifactIndex` populated by stable identifier and semantic type.
  Remaining: durable Prolog or AtomSpace backend implementation and lifecycle governance.

- [ ] **Partial** Associate semantic encounters and memory updates with the history already preserved by Phase 1.  
  Existing evidence: deterministic debugger history, versioned records, append-only `EncounterLog`, external manifests/README links, and the isolated runner observer seam; `SemanticGridCaptureObserver` now normalizes captured grids, persists observation/encounter/Turtle artifacts, chains repeated candidates, composes `SymbolicStore`, and links records to nodes.
  Remaining: configure observer enablement in additional runner entry points and connect unresolved candidate proposals to explicit registry authorization controls.

- [ ] **Open** Support deterministic semantic-memory replay and reproducible updates from the debugger’s recorded history.

- [ ] **Open** Demonstrate recognition and reconstruction under modest degradation and partial occlusion.

## Phase 2 tests and documentation

- [ ] **Open** Provide tests for identity, correspondence, Turtle regeneration, confidence, duplicate prevention, false merge, false split, degradation, partial visibility, memory, and replay.

- [ ] **Open** Provide a reproducible Phase 2 workflow demonstration:

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

- [ ] **Open** Provide Phase 2 identity, correspondence, regeneration, confidence, memory, and replay documentation with linked evidence.

---

# Phase 3 — Game Object Learner Integration and Predictive Rule Learning

Architecture: [Phase 3 learner architecture](SOW_PHASE_ARCHITECTURE.md#phase-3--game-object-learner-integration-and-predictive-rule-learning)

Active work: [TODO — Phase 3](TODO.md#phase-3--game-object-learner-integration-and-predictive-rule-learning)

Phase 3 implements learning and prediction over the persistent objects and evidence produced by Phase 2. The Phase 1 debugger remains the inspection surface for its rules, critiques, probabilities, predictions, grades, and recommendations.

## Stable learner boundary

- [ ] **Partial** Define a stable, versioned data contract from object perception and memory to the Game Object Learner.  
  Existing evidence: `GameObjectLearnerPayload`, result records, plugin interface.  
  Remaining: freeze serialized schema and build real Phase 2 payloads.

- [ ] **Partial** Provide objects, properties, relationships, correspondences, state differences, actions, encounter history, evidence, confidence, and provenance.  
  Existing evidence: fields and provider contracts.  
  Remaining: real data wiring.

- [x] Keep the learner independent of debugger and perception internals while returning normalized artifacts the debugger can display.  
  Evidence: plugin and normalized payload/result boundaries.

- [x] Add interface validation and structured errors.  
  Evidence: `IntegrationValidator`, `IntegrationError`.

- [ ] **Partial** Add integration tests and example workflows.  
  Existing evidence: synthetic Python and Prolog pipeline tests.  
  Remaining: real ARC3/Phase 2 integration workflow.

## Transformations, rules, critiques, and ranking

- [ ] **Partial** Analyze observed transitions and infer candidate object-level transformations.  
  Existing evidence: `TransitionAnalyzer`, `TransformationLearner`, and Prolog equivalents.  
  Remaining: real object-transition inputs and quality evaluation.

- [ ] **Partial** Induce multiple candidate rules with assumptions, critiques, confidence estimates, and supporting or contradicting evidence.  
  Existing evidence: rule, rival, and evidence structures.  
  Remaining: real induction, critique, and confidence refinement.

- [ ] **Partial** Rank and refine competing rules using simplicity, coverage, contradiction, applicability, and prediction history.  
  Existing evidence: `RuleRanker` contracts.  
  Remaining: real evidence and prediction-history integration.

- [ ] **Partial** Apply learned transformations and rules to previously unseen cases.  
  Existing evidence: rule execution contracts.  
  Remaining: unseen-case demonstration from learned real examples.

## Prediction and independent outcome grading

- [x] Provide a prediction ledger that enforces prediction-before-outcome ordering.  
  Evidence: Python and Prolog prediction-ledger tests.

- [ ] **Partial** Record real ARC3 predictions before outcomes, including expected objects, relationships, state changes, or action recommendations.  
  Existing evidence: connected synthetic pipeline.  
  Remaining: real predictions before action execution.

- [x] Compare predictions with independently supplied outcomes through a separate outcome channel.  
  Evidence: `OutcomeChannel`, `PredictionEvaluator`, and Prolog evaluation module.

- [x] Update positive and negative rule evidence from prediction success or failure through grading records.  
  Evidence: connected Python and Prolog tests.

- [x] Prevent post-hoc explanations from receiving predictive credit.  
  Evidence: ordering enforcement in prediction ledgers.

- [ ] **Open** Refine rule probability, confidence, and ranking from real prediction history.

## Debugger evidence writeback

- [ ] **Partial** Write rules, critiques, probabilities, predictions, and grades back to the debugger and action-tree README evidence.  
  Existing evidence: Phase 1 can already display provider-generated rules, critiques, and confidence outputs.  
  Remaining: normalized real learner records, outcome links, grades, and evidence updates.

- [ ] **Open** Link learned rules and action recommendations to their source observations, Phase 2 objects, evidence, predictions, and outcomes.

## Environment and acceptance demonstrations

- [ ] **Open** Demonstrate recognition and completion of partly occluded objects.

- [ ] **Open** Demonstrate the approved environment progression:
  - ARC-style grids;
  - rendered arcade environments;
  - fixed-camera physics examples;
  - top-down manipulation with partial occlusion.

- [ ] **Open** Demonstrate the complete Phase 3 workflow:

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

- [ ] **Open** Provide reproducible integration commands, example scripts, acceptance-test results, and developer notes.

---

# Project-level completion checklist

- [x] Phase 1 debugger and inspection deliverables are identified separately from later semantic and learning quality.
- [ ] Every checked Phase 2 and Phase 3 deliverable has reproducible implementation, tests, and demonstration evidence.
- [ ] Every partial deliverable is completed or explicitly deferred with written rationale.
- [ ] Architecture, TODO, deliverables, file tree, debugger, provider, and Kaggle documentation agree.
- [ ] Protected Kaggle files remain unchanged in name and purpose.
- [ ] Exact-grid identity, Turtle regeneration, memory replay, and prediction ordering are deterministic before raster/occlusion environments are accepted.
- [ ] Final acceptance evidence links repository commits, tests, action-tree artifacts, Turtle programs, transcripts, predictions, outcomes, and demonstrations.

[← Back to top-level README](README.md)
