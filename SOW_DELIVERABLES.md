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

- [x] Implement pluggable perception providers for grid inputs.
  Evidence: `GridAdapter` wraps the existing `workbench.server.runtime.analyze_grid` extractor without duplicating it, emits normalized observation/artifact/provenance/candidate contracts, and normalizes cells, components, compound parts, boundaries, holes, enclosures, bars, properties, and relationships. `SemanticGridCaptureObserver` converts those results into live encounters and action-tree evidence; focused capture and replay tests preserve the normalized structure exactly.

- [x] Implement pluggable perception providers for image and simple-video inputs.
  Evidence: `ImageAdapter` accepts Pillow images, encoded bytes, or paths and normalizes injected extractor results through the same observation/candidate contracts. `SimpleVideoAdapter` preserves ordered decoded-frame provenance without imposing a codec dependency. `SpriteAdapter` and `AlphaContourProvider` provide a concrete raster implementation, while the deterministic environment progression exercises rendered arcade, fixed-camera sequence, and top-down occlusion inputs. Additional learned providers and video decoders remain replaceable integrations rather than missing contract work.

- [ ] **Partial** Extract objects and represent geometry, structure, properties, relationships, position, orientation, scale, and appearance.  
  Existing evidence: frozen versioned contracts plus deterministic grid extraction of cells, exact bounds, boundary geometry, shape/color/appearance, hole and enclosure regions, connected components, compound parts, horizontal and vertical bars, line thickness, and pairwise spatial relationships; semantic capture persists normalized instance position/scale/orientation/appearance, geometry, topology, source provenance, and canonical relationship records. Deterministic principal-axis orientation is inferred for asymmetric cell structures while symmetric structures remain explicitly unoriented. Raster candidates now retain relative mask cells, contours, dimensions, compound components, properties, appearance, relationships, orientation, and scale through `ImageAdapter`; ordered video frames inherit the same contract. Providers can attach named semantic part roles and properties to one or more validated structural components; invalid component references fail at the adapter boundary, while valid roles survive AtomSpace reload. The raster adapter conservatively derives reciprocal left/right, above/below, contains/inside, and overlap facts from bounds and merges them with provider relations. Relationship equality and change participate in correspondence evidence and survive snapshot, Prolog, AtomSpace, and action-tree replay.
  Remaining: add learned providers that infer domain-semantic roles rather than supplying them explicitly.

## Persistent identity and correspondence

- [x] Extend `object_registry.pl` into persistent identities across examples, encounters, and transitions while preserving Phase 1 provenance.
  Evidence: readable state-transition identities, lifecycle governance, and a managed append-only `semantic_identity_decisions.pl` extension are loaded by every registry rewrite. Only canonical friendly IDs are accepted; encounter, decision, evidence, accepted/reversed status, and live SWI-Prolog queries are covered. `SemanticIdentityCatalog` exports the best complete durable form, provenance, attributable evidence, and exact friendly registry fact; JSON round-trip and explicit import seed recognition and merge the destination level registry while rejecting conflicting facts. Imported identities remain unresolved proposals until explicit authority selects them, so cross-example continuity never turns similarity into authorization.

- [x] Match corresponding objects between states and repeated encounters while retaining competing proposals.
  Existing evidence: deterministic proposals retain every rival and explain matched/changed properties; `RecognitionSession` derives the latest known instance for each durable identity from encounter history and persists every proposal plus an unresolved recognition account. `RegistryCorrespondenceAuthority` requires explicit friendly-ID selection plus attributable evidence, calibrates through `SingleWriter`, creates a resolved recognition account, and records Prolog decision history. Perfect similarity alone is rejected.
  Live `SemanticGridCaptureObserver` sessions now invoke this path when durable identity history is available and link proposal/account artifacts into the action-tree node. Every captured Turtle program is also regenerated through the real SWI-Prolog Turtle DSL; fit score, distance, residual, description length, and separately attributable signed reconstruction evidence persist with the encounter and replay from the action tree. Exact property matches, declared transformations, and exact Turtle reconstruction fits produce attributable support records; unexplained changes and nonzero Turtle residuals produce contradiction records. Aggregate similarity is never copied into evidence or confidence. The observer exposes pending friendly-registry selections, and `Arc3Runner` forwards explicit accept/reject controls. Acceptance admits a missing selected registry atom at zero confidence through the `SingleWriter`, then applies only the selected proposal's attributable evidence; rejection records history without changing confidence. Both persist a resolved account beside the originating node, and later recognition resolves the immutable candidate encounter through that accepted account so the durable identity is not forgotten.

- [x] Recognize recurring objects under supported translation, rotation, scale, reflection, recoloring, noise, and partial visibility.

  Evidence: correspondence proposals explicitly recognize declared translation, rotation, scale, reflection, recoloring, noise, and partial-visibility changes. The complete transformation fixture matrix covers every named transform. Missing properties under declared partial visibility produce support rather than false contradiction, incomplete/noisier encounters cannot replace the best complete stored form, and deterministic noise/occlusion raster fixtures exercise degraded inputs. `ResidualAnalyzer` absorbs declared transformations but preserves every unexplained property change as a deterministic provisional residual through live capture, README inspection, action-tree replay, and Prolog persistence.

- [x] Detect movement, recoloring, resizing, addition, removal, splitting, merging, and structural change.
  Evidence: deterministic `ObjectChange` records and `ChangeDetector` coverage include moved, recolored, resized, reoriented, reshaped, appeared, disappeared, one-to-many split, and many-to-one merge cases. `StructuralCorrespondenceInferer` now resolves renamed exact matches and exact disjoint-union splits/merges from absolute normalized cell geometry while refusing overlapping or partial-coverage ambiguities. `EncounterChangeSession` persists the inferred pairwise proposals and authoritative structural change without emitting misleading child geometry residuals. Snapshot, action-tree, and Prolog replay retain the exact changes and proposals.

## Per-object Turtle programs and regeneration

- [x] Store every recognized grid object with a Turtle program.
  Evidence: live semantic capture persists one or more normalized, versioned `TurtleProgramRef` values and exact Turtle source artifacts for every extracted candidate, links them through its encounter and action-tree manifest, and restores them during deterministic replay. When an extractor supplies ambiguous `turtlePrograms`, every distinct interpretation retains its entrypoint, provenance, fit, distance, residual, description length, and separately attributable reconstruction evidence rather than being collapsed to the first program. The Phase 2 demonstration asserts four programs for four captured encounters, and ambiguity coverage verifies two rival programs survive action-tree replay.

- [ ] **Partial** Require the Turtle program to redraw the object through movement, rotation, pen state, and pen width rather than filled coordinate boxes.
  Existing evidence: extracted programs use `set_pos`, `rot`, `fwd`, `penup`/`pendown`, and canonical `pen_width`; supported thick rectangles render as one width-aware stroke and a regression test rejects row-by-row box filling.
  Remaining: extend stroke optimization beyond exactly representable width-1-through-4 rectangles and line forms.

- [ ] **Partial** Execute the stored Turtle program to regenerate the object and compare it with the source observation.  
  Existing evidence: `CellLogoForm` now executes extracted programs through `SWIPrologBridge` and the canonical `prolog/turtle_dsl.pl`; regenerated-cell fit, distance, normalized residual, and description-length metrics have live SWI-Prolog coverage.
  `TurtleReconstructionEvidenceBuilder` now converts exact fit or residual measurements into attributable signed evidence without hiding the measured residual. Live semantic capture invokes the real SWI-Prolog renderer for every candidate, persists the metrics on its Turtle reference, attaches evidence to the encounter, links the evidence artifact into the action tree, and restores it during replay.

- [x] Preserve exact holes, disconnected strokes, topology, and supported thickness through the stored Turtle program.
  Evidence: live SWI-Prolog regeneration exactly preserves hollow objects without filling their holes, disconnected components retain separate programs, and supported thick rectangles use canonical pen width. Semantic instances now retain translation-normalized boundary geometry, hole cells, component count, and thickness; exact topology/geometry matches create attributable support evidence.

## Residuals, duplicates, evidence, and confidence

- [x] Distinguish recognized or explained content from residual, potentially new object structure.
  Evidence: `ResidualAnalyzer` excludes declared transformations, emits deterministic structured residuals for unexplained fields, tracks recurrence, and advances repeated structure from provisional to `commit_request` only through `ResidualGate`. Live capture, README inspection, action-tree replay, snapshots, and Prolog persistence retain every occurrence.

- [x] Prevent duplicate persistent storage when an existing object is recognized again.

  Evidence: semantic store writes, identity commits, residual occurrences, and merge/split decisions are idempotent by deterministic identity. Compatible repeat commits return the existing calibrated object, while conflicting reuse fails rather than overwriting memory.

- [ ] **Partial** Accumulate positive and negative recognition evidence and provenance across the encounter history preserved by Phase 1.  
  Existing evidence: `SingleWriter` accepts frozen positive/negative `EvidenceRecord` values, checks their subject, deduplicates stable evidence IDs, preserves base provenance, and derives confidence from signed weights independently of arrival order. Live encounter matching writes property-attributable evidence into node manifests and the durable Prolog backend.
  Remaining: domain calibration against representative fixtures.

- [ ] **Partial** Refine and calibrate confidence for object identity, correspondence, and competing interpretations.
  Existing evidence: deterministic Laplace-style confidence is derived from attributable supporting and contradicting evidence, with event history and order-independence tests. Authority decisions now preserve pre-decision confidence separately from the later accepted/rejected outcome, avoiding post-outcome leakage. `RecognitionCalibrator` computes scoped reliability bins, acceptance rates, and Brier error only from resolved decisions; unresolved proposals are excluded. Typed confidence-history and decision-calibration fields survive snapshots and durable replay.
  Remaining: learn and validate an optional recalibration policy from representative domain/provider datasets; rival proposal scores remain advisory rather than calibrated probabilities.

## Persistent symbolic memory and replay

- [ ] **Partial** Maintain persistent symbolic memory for recognized objects, observations, Turtle programs, and associated artifacts.  
  Existing evidence: `SymbolicMemory`, a backend-neutral `SymbolicStore` facade with write-once exact identity, a replaceable `SemanticStoreBackend` boundary, observation/encounter/Turtle/change composition, and an `ArtifactIndex` populated by stable identifier and semantic type. Repeat identity commits return the existing calibrated object and conflicting payloads fail instead of overwriting durable memory. Exact snapshots replay every semantic namespace, including confidence and object-change history, in dependency order and rebuild encounter/artifact indexes idempotently. `PrologSemanticBackend` durably stores typed contracts as inspectable `semantic_record/3` facts, safely round-trips nested JSON/unicode, loads in live SWI-Prolog, and hydrates fresh facade indexes. `AtomSpaceSemanticBackend` provides the equivalent write-once contract as queryable MeTTa `semantic_record` Atoms; its durable MeTTa-file transport reloads nested typed records exactly, while its injected transport protocol is the boundary for Hyperon, OpenCog, or a remote MeTTa server. The single identity writer now emits append-only, self-contained checkpoints containing exact atoms, attributable evidence, accepted merge/split decisions, pre-decision snapshots, and confidence history. A fresh AtomSpace-backed process restores that state and can reverse either decision without losing the original identities.
  Remaining: define retention/compaction policy and external multi-writer coordination for long-running remote AtomSpaces.

- [ ] **Partial** Associate semantic encounters and memory updates with the history already preserved by Phase 1.  
  Existing evidence: deterministic debugger history, versioned records, append-only `EncounterLog`, external manifests/README links, and the isolated runner observer seam; `SemanticGridCaptureObserver` now normalizes captured grids, persists observation/encounter/Turtle/proposal/account/evidence artifacts, chains repeated candidates, composes `SymbolicStore`, and links records to nodes. Node READMEs summarize unresolved proposals, advisory similarity, evidence polarity, selected identity, decision source, confidence, and rivals with links to exact records.
  Explicit accept/reject controls now connect unresolved candidate proposals to friendly registry identities through `Arc3Runner` and persist the resulting account and Prolog decision. The canonical interactive and Prolog-controlled runners now install a standard semantic observer by default, sharing the established grid extractor, real SWI Turtle renderer, semantic store, and single identity writer; both offer an explicit `--no-semantic-capture` opt-out.

- [x] Support deterministic semantic-memory replay and reproducible updates from the debugger’s recorded history.
  Existing evidence: complete `SymbolicStore` snapshots deterministically restore artifacts, Turtle references, atoms, observations, encounters, proposals, recognition accounts, and evidence; repeated replay is idempotent and encounter hashes remain stable. `ActionTreeSemanticReplay` rebuilds a fresh store directly from exact records linked by Phase 1 `semantic_records.json` manifests, restores encounter chains in predecessor order, deduplicates repeated links, and rejects missing/cyclic history. A newly composed live observer replays its level once before capture and restores terminal candidate/observation cursors, so post-restart encounters continue the durable history rather than starting a disconnected memory.
  Recorded trees can replay into either the durable Prolog backend or `AtomSpaceSemanticBackend`, then hydrate exact typed records and facade indexes after process restart. Dedicated AtomSpace coverage replays a real Phase 1 manifest, reloads the MeTTa Atom file into a fresh store, and proves that both the snapshot and artifact index are identical.

- [x] Demonstrate recognition and reconstruction under modest degradation and partial occlusion.
  Evidence: degraded normalized encounters explicitly carry visibility, noise,
  reflection, and supported-transformation metadata. Correspondence produces
  property-attributable support for missing occluded fields, and
  `RecognitionSession.complete_partial` reconstructs only from a selected
  durable identity's best prior complete form. The completion retains the
  current position and visible properties, restores missing appearance/
  geometry/topology where justified, resets reconstruction visibility/noise,
  reports every inferred field separately, and persists its proposal and
  evidence without rewriting the observed encounter.

## Phase 2 tests and documentation

- [x] Provide tests for identity, correspondence, Turtle regeneration, confidence, duplicate prevention, false merge, false split, degradation, partial visibility, memory, and replay.
  Evidence: the deterministic Phase 2 suites cover identity lifecycle and registry authority; competing correspondence proposals and signed evidence; real SWI-Prolog Turtle regeneration, topology, width, and rival forms; confidence calibration and reversal; write-once duplicate conflicts; reversible false merge/split handling; noise and partial-visibility completion; snapshot/Prolog memory; and action-tree replay with predecessor, conflict, and restart checks.

- [x] Provide a reproducible Phase 2 workflow demonstration:

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

  Evidence: `scripts/phase2_object_memory_demo.py` runs this path over two real logical-grid states, uses the established extractor and SWI-Prolog Turtle renderer, explicitly authorizes a friendly identity through `SingleWriter`, persists moved-object evidence, rebuilds a fresh store from action-tree manifests, and emits a machine-readable summary. `tests/test_phase2_object_memory_demo.py` asserts stable identity, four exact reconstructions, change capture, and deterministic replay. See [Phase 2 object-memory demonstration](workbench/docs/design/PHASE2_OBJECT_MEMORY_DEMONSTRATION.md).

- [x] Provide Phase 2 identity, correspondence, regeneration, confidence, memory, and replay documentation with linked evidence.
  Evidence: [Phase 2 object-memory demonstration](workbench/docs/design/PHASE2_OBJECT_MEMORY_DEMONSTRATION.md) documents the complete executable path, inspectable action-tree artifacts, exact record types, restart replay, and regression assertions.

---

# Phase 3 — Game Object Learner Integration and Predictive Rule Learning

Architecture: [Phase 3 learner architecture](SOW_PHASE_ARCHITECTURE.md#phase-3--game-object-learner-integration-and-predictive-rule-learning)

Active work: [TODO — Phase 3](TODO.md#phase-3--game-object-learner-integration-and-predictive-rule-learning)

Phase 3 implements learning and prediction over the persistent objects and evidence produced by Phase 2. The Phase 1 debugger remains the inspection surface for its rules, critiques, probabilities, predictions, grades, and recommendations.

## Stable learner boundary

- [x] Define a stable, versioned data contract from object perception and memory to the Game Object Learner.
  Evidence: versioned `GameObjectLearnerPayload`, lossless dictionary serialization, result records, and the plugin interface. `Phase2LearnerPayloadBuilder` derives the contract from exact semantic observations and encounters without leaking debugger objects.

- [x] Provide objects, properties, relationships, correspondences, state differences, actions, encounter history, evidence, confidence, and provenance.
  Evidence: the real Phase 2 payload builder includes observation/encounter IDs, normalized instances and relationships, stable/candidate identities, action-bearing changed properties, Turtle and source artifacts, competing proposals, direct changes, evidence, confidence, and provenance. Validation enforces encounter, Turtle-artifact, and evidence referential integrity. Strict durable-reference validation now requires every registry identity to be backed by a committed Atom or durable prior encounter and every advertised provenance source to occur in the exact semantic-store snapshot used for the handoff. Generic imported payload validation retains an explicit authority injection point rather than assuming that provider names are semantic-record IDs.

- [x] Keep the learner independent of debugger and perception internals while returning normalized artifacts the debugger can display.  
  Evidence: plugin and normalized payload/result boundaries. `PrologProvider`
  exposes explicit registry, object, difference, similarity, rule, transcript,
  and evidence families through the shared `semantic_record/3` query contract.
  `TransitionRule` is now a first-class `SymbolicStore` namespace alongside
  the previously durable atoms, encounters, proposals, changes, evidence,
  predictions, and grades; learning persists induced rules through either the
  in-memory or reloadable Prolog backend.

- [x] Add interface validation and structured errors.  
  Evidence: `IntegrationValidator`, `IntegrationError`.

- [x] Add integration tests and example workflows.
  Evidence: synthetic Python and Prolog pipeline tests plus a real semantic-store-to-learner handoff test cover serialization and linked relationships, correspondence, evidence, action, Turtle artifact, encounter, and provenance data. `SemanticGridCaptureObserver` sends its first real payload to `consume_state`, sends subsequent before/action/after payloads to `consume_transition` after change detection, and links each normalized learner result into the current action-tree node. A real ARC3 logical-grid integration test moves the extracted hollow blue object, learns absolute and relative rules from the normalized position delta, applies the relative rule to an unseen position, records the prediction, and verifies action-tree rule links. The selectable `ARC3 Rule Learning Demonstration` filesystem workspace inherits the system and ARC3 libraries and supplies a seven-stage Workflow for capture, transition analysis, rival induction, human review, unseen prediction, and independent grading. Its load/materialization test proves every non-human step resolves to an implementation. The standard runner composition accepts the plugin without coupling `Arc3Runner` to learner internals.

## Transformations, rules, critiques, and ranking

- [ ] **Partial** Analyze observed transitions and infer candidate object-level transformations.  
  Existing evidence: `TransitionAnalyzer`, `TransformationLearner`, and Prolog equivalents plus canonical Phase 2 adapters. The analyzer validates real before/after payloads and preserves action and provenance. The learner retains every persisted direct object change and infers explicit absolute-target and relative-delta rivals for numeric changes, plus multiplicative scaling for resize events, Boolean toggles, and collection membership edits. Every interpretation preserves common evidence while carrying distinct assumptions and critiques; the rule inducer keeps them as mutual rivals, and unseen-case execution demonstrates observably different predictions for translation, scaling, toggling, and set edits. Remaining: infer and evaluate relational/topological alternatives such as attachment, containment, and object-relative motion.

- [x] Induce multiple candidate rules with assumptions, critiques, confidence estimates, and supporting or contradicting evidence.
  Evidence: canonical Phase 2 induction creates one deterministic rule per real transformation candidate, retains all alternatives as mutual rivals, records identity-presence and representativeness assumptions, flags missing evidence and single-observation/unseen-case limitations, and carries exact evidence and provenance. Independent prediction outcomes append normalized supporting or contradicting records while bootstrap and calibrated probability remain distinct.

- [x] Rank and refine competing rules using simplicity, coverage, contradiction, applicability, and prediction history.
  Evidence: the canonical ranker orders rivals by calibrated probability, verified prediction success, applicability precision, coverage, supporting/contradicting evidence, simplicity, and only then a small bootstrap tie-breaker. Live ARC3 outcomes now feed prediction history, normalized evidence, and calibration.

- [x] Apply learned transformations and rules to previously unseen cases.
  Evidence: the canonical Phase 2 executor checks the learned action condition,
  applies observed numeric deltas relative to a new object's current values,
  applies categorical target values without mutating the input, and rejects
  structurally inapplicable states. An end-to-end test learns a RIGHT
  translation from a known object at `[1, 1]`, applies the induced rule to an
  unseen red object at `[7, 4]`, obtains `[8, 4]`, and records that predicted
  state through the append-only prediction ledger before any outcome exists.

## Prediction and independent outcome grading

- [x] Provide a prediction ledger that enforces prediction-before-outcome ordering.  
  Evidence: Python and Prolog prediction-ledger tests.

- [x] Record ARC3 predictions before outcomes, including expected state changes from learned rules.
  Evidence: `Arc3Runner` invokes `before_action` observers before `env.step`; the canonical semantic observer selects a matching ranked rule, writes the immutable prediction into the current node, and grades it only after the next captured transition.

- [x] Compare predictions with independently supplied outcomes through a separate outcome channel.  
  Evidence: `OutcomeChannel`, `PredictionEvaluator`, and Prolog evaluation module. The Python pipeline now persists the pre-outcome prediction and later grade as separate immutable semantic records.

- [x] Update positive and negative rule evidence from prediction success or failure through grading records.  
  Evidence: connected Python and Prolog tests; Python prediction grades now create normalized supporting or contradicting `EvidenceRecord` values, attach their IDs to the rule, and persist them beside the immutable grade.

- [x] Prevent post-hoc explanations from receiving predictive credit.  
  Evidence: ordering enforcement in prediction ledgers.

- [x] Refine rule probability, confidence, and ranking from prediction history.
  Evidence: independently graded predictions append to each rule's immutable history, update a smoothed calibrated probability, and feed the Phase 2/3 ranker without rewriting rule identity.

## Debugger evidence writeback

- [x] Write rules, critiques, probabilities, predictions, and grades back to the debugger and action-tree README evidence.
  Existing evidence: Phase 1 can display provider-generated outputs; live semantic capture now decomposes normalized learner transitions, transformation candidates, and competing rules into individually linked artifacts with README summaries of assumptions, critiques, rivals, probability, and evidence.
  Existing prediction bridge: `ActionTreeStore.link_prediction_history` materializes a persisted pre-outcome prediction, its independent grade, and linked evidence into a node manifest and README without mutating the original prediction.
  Live integration: the canonical semantic observer invokes the bridge before the ARC3 action and again after independent transition grading; action-tree replay restores predictions, grades, and evidence after restart.

- [x] Link learned rules and action recommendations to their source observations, Phase 2 objects, evidence, predictions, and outcomes.
  Evidence: immutable `ActionRecommendation` records rank every learned rule independently of the attempted action and retain the selected rule, source state, attempted and recommended actions, rivals, assumptions, critiques, available evidence, and probability provenance. A recommendation links a prediction only when that prediction used the recommended rule; the independently persisted prediction grade then links the later outcome without rewriting either record. Live capture writes recommendations into action-tree manifests and README summaries, and both filesystem and Prolog semantic replay restore them after restart.

## Environment and acceptance demonstrations

- [x] Demonstrate recognition and completion of partly occluded objects.
  Evidence: the degradation fixture matches a 40%-visible noisy blue hook to
  its complete durable identity, preserves the complete stored form, then
  produces an evidence-linked completed instance at the newly observed
  position. The result explicitly identifies `appearance.shape` and
  `appearance.texture` as inferred rather than observed.

- [x] Demonstrate the approved environment progression:
  - ARC-style grids;
  - rendered arcade environments;
  - fixed-camera physics examples;
  - top-down manipulation with partial occlusion.
  Evidence: `scripts/phase2_environment_progression_demo.py` runs seven deterministic fixtures through the normalized raster contracts and emits a machine-readable acceptance summary. It covers a rendered multi-sprite arcade frame, a three-frame fixed-camera motion sequence, and clean/noisy/partly occluded top-down manipulation scenes. See [Phase 2 environment progression](workbench/docs/design/PHASE2_ENVIRONMENT_PROGRESSION.md).

- [x] Demonstrate the complete Phase 3 workflow:

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
  Evidence: `scripts/phase3_learning_demo.py` executes transition analysis, candidate transformation learning, rule induction with assumptions and critiques, a persisted pre-outcome prediction, independent outcome grading, evidence-backed probability calibration, and deterministic semantic replay. Its machine-readable summary is required by the fail-closed Phase 2 acceptance report generator.

- [x] Provide reproducible integration commands, example scripts, acceptance-test results, and developer notes.
  Evidence: the object-memory and environment-progression demonstrations emit deterministic machine-readable summaries. `scripts/generate_phase2_acceptance_report.py` verifies those summaries together with an explicit regression result and repository commit, fails closed when evidence is missing, and writes JSON plus Markdown reports. Commands and scope are documented in [Phase 2 object-memory demonstration](workbench/docs/design/PHASE2_OBJECT_MEMORY_DEMONSTRATION.md) and [Phase 2 environment progression](workbench/docs/design/PHASE2_ENVIRONMENT_PROGRESSION.md).

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
