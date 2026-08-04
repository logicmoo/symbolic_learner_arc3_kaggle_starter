[← Back to top-level README](README.md)

# SOW Deliverables Checklist — Image Perception to Recognizable Memory

## Document scope

This is the delivery checklist. It restates the three SOW phases as checkable outcomes and links each item to current evidence or remaining work.

Related documents:

- [SOW_PHASE_ARCHITECTURE.md](SOW_PHASE_ARCHITECTURE.md) — detailed technical design, classes, modules, and architecture work.
- [TODO.md](TODO.md) — the concrete work we are actively implementing.
- [FILE_TREE.md](FILE_TREE.md) — repository ownership map.

## Status rules

- `[x]` — implemented with repository evidence.
- `[ ] **Partial**` — meaningful infrastructure exists, but the complete deliverable or acceptance evidence is not yet finished.
- `[ ] **Open**` — not yet implemented or not yet demonstrated.

A deliverable should be checked only when its implementation, tests, and demonstration evidence are reproducible.

## Delivery windows

| Phase | Anticipated delivery window |
|---|---:|
| Phase 1 — Grid Infrastructure and ARC3 Debugger Foundation | 3 weeks |
| Phase 2 — Object Perception, Recognition, and Persistent Memory | 1 month |
| Phase 3 — Game Object Learner Integration and Predictive Rule Learning | 1 month |
| Overall sequence | Approximately 3 months |

---

# Phase 1 — Grid Infrastructure and ARC3 Debugger Foundation

Architecture: [ARC3 debugger and state architecture](SOW_PHASE_ARCHITECTURE.md#arc3-debugger-and-state-architecture)

Active work: [TODO — Phase 1 normalization and acceptance](TODO.md#now--stabilize-the-phase-1-evidence-path)

## Runtime and interaction

- [x] Adapt the existing ARC debugger workflow to the ARC3 environment.  
  Evidence: [`python/arc3_runner.py`](python/arc3_runner.py), [`scripts/interactive_runner.py`](scripts/interactive_runner.py), [`DEBUGGER.md`](DEBUGGER.md).

- [x] Load and interact with selected ARC3 games and levels.  
  Evidence: `Arc3Runner` game/level lifecycle and interactive controls.

- [x] Capture game states, actions, observations, and execution history.  
  Evidence: `StepRecord`, `state.json`, `image.png`, history and export paths.

- [x] Support replay, reset, restart, and navigation through previously captured states.  
  Evidence: `Arc3Runner` replay/history/reset/restart commands and action-tree navigation.

## Action trees and structured artifacts

- [x] Store explored states in a GitHub-browsable action tree.  
  Evidence: [`python/action_tree.py`](python/action_tree.py), generated node READMEs and parent/child links.

- [x] Generate structured artifacts describing states, objects, differences, similarities, reconstructions, and candidate rules.  
  Evidence: `state.json`, `objects.pl`, `differences.pl`, `similarities.pl`, `turtle_from_image.pl`, `turtle_from_diff.pl`, and `rules.pl`.

- [x] Maintain stable and human-readable object identities across state transitions.  
  Evidence: level-wide `object_registry.pl`, opaque-ID rejection, registry-backed state files.

- [x] Provide combined analysis of the current state and its transition from the previous state.  
  Evidence: [`python/gpt_bridge.py`](python/gpt_bridge.py), parent/current context and images.

- [x] Cache generated artifacts for repeatable inspection and reuse.  
  Evidence: mutable latest `.pl` files, cache checks, immutable Markdown transcripts, transcript restoration.

- [x] Establish the initial grid infrastructure for object extraction, correspondence, transformation analysis, and rule inspection.  
  Evidence: action-tree artifacts, Turtle reconstruction, object-memory provider contracts, transition/rule modules.

## LLM comparison and debugging evidence

- [x] Preserve provider, adapter, model, analysis level, profile, token budget, images, exact prompt, timing, repair history, and raw response for each LLM run.  
  Evidence: [`python/llm_transcripts.py`](python/llm_transcripts.py).

- [x] Keep restorable generated artifacts in the upper part of each transcript and debugging interaction details below.  
  Evidence: artifact-first `llm_adapter_*.md` layout.

- [x] Keep the raw provider response at the bottom of the transcript.  
  Evidence: transcript rendering tests.

- [x] Restore a historical transcript into the current individual `.pl` files.  
  Evidence: LLM command `1`, `restore_transcript()`, `llm_provider.json` restored provenance.

- [x] Make node `README.md` identify the active transcript and link all historical runs.  
  Evidence: [`python/llm_readme_patch.py`](python/llm_readme_patch.py).

## Configuration and runtime locations

- [x] Keep provider definitions and reusable prompt text together under `config/`.  
  Evidence: [`config/llm_providers.json`](config/llm_providers.json).

- [x] Allow each provider to select an ordered prompt-section list and omit sections such as `transitions`.  
  Evidence: `prompt_text` provider configuration and tests.

- [x] Resolve code, config, and action-tree storage independently.  
  Evidence: [`scripts/_runtime.py`](scripts/_runtime.py), [`python/project_paths.py`](python/project_paths.py).

- [x] Print where configuration is loaded from and where action trees are saved.  
  Evidence: startup resolved-path report.

## Phase 1 completion evidence still required

- [ ] **Partial** Provide one canonical state/action ordinal and normalized immutable observation record.  
  Work: [TODO Phase 1](TODO.md#now--stabilize-the-phase-1-evidence-path).

- [ ] **Partial** Validate every cached artifact against schema, state/image hash, registry version, provider/model/profile, prompt sections, and requested artifact set.  
  Work: stale-cache and compatibility validation.

- [ ] **Partial** Connect all six Prolog debugger commands to normalized Prolog APIs.  
  Work: shared Prolog provider boundary.

- [ ] **Open** Record a complete Phase 1 acceptance demonstration with reproducible commands and linked evidence.  
  Required evidence: game/level interaction, history capture, replay/reset/restart, multi-step identity reuse, provider comparison, and transcript restoration.

- [ ] **Open** Add native Windows smoke evidence for one captured ARC3 state.  
  Work: [TODO Phase 1 demonstrations](TODO.md#phase-1-demonstrations-to-record).

---

# Phase 2 — Object Perception, Recognition, and Persistent Memory

Architecture: [Phase 2 object perception and memory architecture](SOW_PHASE_ARCHITECTURE.md#phase-2-object-perception-and-memory-architecture)

Active work: [TODO — Phase 2](TODO.md#phase-2--object-perception-and-persistent-memory)

## Perception and representation

- [ ] **Partial** Extract and represent objects from grid inputs.  
  Existing evidence: `CandidateObject`, `PerceptionAdapter`, `GridAdapter`, current LLM object artifacts.  
  Remaining: connect the existing deterministic grid extractor through `GridAdapter`.

- [ ] **Open** Extract and represent objects from image and simple video inputs.  
  Remaining: raster adapters and fixed-camera sequence support after exact-grid acceptance.

- [ ] **Partial** Represent object properties, structure, relationships, position, orientation, scale, and appearance.  
  Existing evidence: object-memory records and generated Prolog predicates.  
  Remaining: normalized deterministic extraction and shared schemas.

- [ ] **Partial** Store objects in a normalized form from which they can be regenerated.  
  Existing evidence: `GenerativeForm`, `CellLogoForm`, Turtle artifacts.  
  Remaining: connected render/fit/distance/residual implementation.

- [ ] **Partial** Demonstrate object regeneration from stored representations.  
  Existing evidence: Turtle reconstruction artifacts.  
  Remaining: persistent-form regeneration with source comparison.

## Identity, correspondence, and recognition

- [ ] **Partial** Maintain stable object identities across examples, encounters, and state transitions.  
  Existing evidence: state-transition identity through `object_registry.pl`.  
  Remaining: persistent cross-encounter identity governance.

- [ ] **Partial** Match corresponding objects between states and across repeated encounters.  
  Existing evidence: `similarities.pl` and correspondence contracts.  
  Remaining: deterministic correspondence implementation and evidence records.

- [ ] **Open** Recognize recurring objects under supported position, orientation, scale, reflection, color, noise, and partial-visibility changes.

- [ ] **Partial** Detect movement, recoloring, resizing, addition, removal, and structural change.  
  Existing evidence: generated difference artifacts and transition contracts.  
  Remaining: deterministic object-level implementation and fixtures.

- [ ] **Open** Distinguish recognized content from genuinely new object structure through residual analysis.

- [ ] **Open** Prevent duplicate durable storage of already recognized objects.

## Persistent memory and provenance

- [ ] **Partial** Accumulate evidence and provenance across repeated encounters.  
  Existing evidence: `SingleWriter`, evidence records, action-tree/transcript provenance.  
  Remaining: durable encounter-linked evidence.

- [ ] **Open** Preserve encounter history and support deterministic replay through an append-only `EncounterLog`.

- [ ] **Partial** Provide persistent symbolic memory for recognized objects, observations, and associated artifacts.  
  Existing evidence: `SymbolicMemory` reference implementation and generated action-tree storage.  
  Remaining: durable `SymbolicStore`, `ArtifactIndex`, and lifecycle governance.

- [ ] **Open** Demonstrate recognition under modest degradation and partial occlusion.

## Phase 2 tests and documentation

- [ ] **Open** Provide tests for stable identity, correspondence, duplicate prevention, false merge, false split, regeneration, degradation, partial visibility, and deterministic encounter replay.

- [ ] **Open** Provide a reproducible demonstration of the full Phase 2 workflow:

```text
Input image or game state
    → object extraction
    → object representation
    → object matching and correspondence
    → before-and-after state comparison
    → persistent storage
    → later recognition as the same object
```

- [ ] **Open** Provide Phase 2 identity, recognition, regeneration, memory, and replay documentation with linked evidence.

---

# Phase 3 — Game Object Learner Integration and Predictive Rule Learning

Architecture: [Phase 3 Game Object Learner architecture](SOW_PHASE_ARCHITECTURE.md#phase-3-game-object-learner-architecture)

Active work: [TODO — Phase 3](TODO.md#phase-3--game-object-learner-and-prediction)

## Stable integration boundary

- [ ] **Partial** Define the interface and data contract connecting perception/memory to the Game Object Learner.  
  Existing evidence: `GameObjectLearnerPayload`, result records, plugin interface.  
  Remaining: freeze serialized schema and build real Phase 2 payloads.

- [ ] **Partial** Provide objects, properties, relationships, correspondences, state differences, and encounter history to the learner.  
  Existing evidence: fields and provider contracts.  
  Remaining: real data wiring and persistent encounter history.

- [x] Keep the Game Object Learner independent of debugger and perception-layer internals.  
  Evidence: plugin and normalized payload boundary.

- [x] Add interface validation and structured errors.  
  Evidence: `IntegrationValidator`, `IntegrationError`.

- [ ] **Partial** Add integration tests and example workflows.  
  Existing evidence: synthetic Python and Prolog pipeline tests.  
  Remaining: real ARC3/Phase 2 integration workflow.

## Transformations and rules

- [ ] **Partial** Infer candidate object-level transformations and transition rules.  
  Existing evidence: `TransitionAnalyzer`, `TransformationLearner`, `RuleInducer`, and Prolog equivalents.  
  Remaining: real object-transition inputs and quality evaluation.

- [x] Support multiple candidate interpretations and retain rule evidence structures.  
  Evidence: transformation candidates, rule rival/evidence records, provider-driven pipelines.

- [ ] **Partial** Apply learned object-level transformations to new cases.  
  Existing evidence: rule execution contracts.  
  Remaining: learned transformations from real cases and unseen-case demonstration.

## Prediction and independent outcome grading

- [x] Provide a prediction ledger that enforces prediction-before-outcome ordering.  
  Evidence: Python and Prolog prediction-ledger tests.

- [ ] **Partial** Predict later states before outcomes are observed.  
  Existing evidence: connected synthetic pipeline.  
  Remaining: predictions generated from real ARC3 transitions before action execution.

- [x] Compare predictions with independently supplied outcomes through a separate outcome channel.  
  Evidence: `OutcomeChannel`, `PredictionEvaluator`, Prolog evaluation module.

- [x] Update rule evidence from prediction success or failure through grading records.  
  Evidence: connected Python and Prolog tests.

- [x] Prevent post-hoc explanations from being treated as successful predictions.  
  Evidence: ordering enforcement in prediction ledgers.

## Environment and occlusion demonstrations

- [ ] **Open** Demonstrate recognition and completion of partly occluded objects.

- [ ] **Open** Demonstrate the approved environment progression:
  - ARC-style grids;
  - rendered arcade environments;
  - fixed-camera physics examples;
  - top-down manipulation with partial occlusion.

## Phase 3 delivery evidence

- [ ] **Open** Demonstrate the complete Phase 3 workflow:

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

- [ ] **Open** Provide reproducible integration commands, example scripts, acceptance-test results, and developer notes.

- [ ] **Open** Link predictions, outcomes, grades, learned rules, and action recommendations into action-tree evidence.

---

# Project-level completion checklist

- [ ] Every checked deliverable has reproducible implementation, tests, and demonstration evidence.
- [ ] Every partial deliverable is either completed or explicitly deferred with written rationale.
- [ ] Architecture, TODO, deliverables, file tree, debugger, provider, and Kaggle documentation agree.
- [ ] Protected Kaggle files remain unchanged in name and purpose.
- [ ] Exact-grid behavior is deterministic before raster/occlusion environments are accepted.
- [ ] Final acceptance report links repository commits, tests, action-tree artifacts, transcripts, predictions, and demonstrations.

[← Back to top-level README](README.md)
