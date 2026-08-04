[← Back to top-level README](README.md)

# SoW Phase Architecture — Image Perception to Recognizable Memory

## Purpose

This document maps the current repository and its planned integration work to the three deliverable-based phases in the *Image Perception to Recognizable Memory* Statement of Work. It describes engineering scope, repository ownership, demonstration workflows, and acceptance evidence. Commercial terms are intentionally outside this repository document.

## Schedule baseline

| Scope | Anticipated delivery window |
|---|---:|
| Phase 1 — Grid Infrastructure and ARC3 Debugger Foundation | 3 weeks |
| Phase 2 — Object Perception, Recognition, and Persistent Memory | 1 month |
| Phase 3 — Game Object Learner Integration and Predictive Rule Learning | 1 month |
| Overall sequence | Approximately 3 months from the effective date |

Deliverables may be completed earlier or may require additional time. Any material schedule change should be communicated in writing.

## Governing principles

- Extend the working repository rather than replacing delivered components.
- Keep one ARC3 runner, one action-tree store, one provider router, one artifact pipeline, and one Turtle execution semantics.
- Preserve stable, human-readable object identities across states, encounters, providers, and learned rules.
- Keep generated evidence, provenance, prompts, raw responses, artifacts, and prediction outcomes inspectable and replayable.
- Use PROLOG, GPT/LLM, and deterministic PYTHON implementations behind shared contracts rather than maintaining three unrelated object models.
- Do not create phase directories or duplicate runnable examples outside `scripts/`.
- Do not rename or repurpose the protected Kaggle notebook, build scripts, submission agent, or runner scripts.
- Treat similarity and embeddings as candidate-retrieval aids; they do not independently commit identity or evidence.
- Give positive rule evidence only to predictions recorded before the independently observed outcome.

## End-to-end architecture

```text
ARC3 game, grid, image, or simple video input
    → captured observation and action-tree state
    → object extraction and generative representation
    → stable identity and object correspondence
    → before/after differences and transition evidence
    → persistent encounter and artifact memory
    → Game Object Learner payload
    → candidate transformations and competing rules
    → prediction recorded before outcome
    → independent outcome observation and grading
    → updated evidence, learned rule, or action recommendation
```

The mutable node-local `.pl` files represent the latest selected analysis. Per-run LLM Markdown transcripts preserve immutable comparison snapshots containing the generated Prolog artifacts, exact prompt, provider configuration, images, timing, token details, repair history, and raw provider responses. Restoring a transcript rewrites the latest `.pl` view without erasing the historical run.

---

# Phase 1 — Grid Infrastructure and ARC3 Debugger Foundation

## Required outcomes

Phase 1 establishes the working ARC3 experimentation and evidence surface:

- adapt the existing ARC debugger workflow to ARC3;
- load and interact with selected games and levels;
- capture game states, actions, observations, and execution history;
- store explored states in a GitHub-browsable action tree;
- generate structured artifacts for states, objects, differences, similarities, reconstructions, and candidate rules;
- maintain stable, readable object identities across transitions;
- support replay, reset, restart, and navigation through captured states;
- analyze the current state together with its transition from the parent state;
- cache generated artifacts for repeatable inspection and reuse;
- establish grid infrastructure for extraction, correspondence, transformation analysis, and rule inspection;
- document the debugger, state trees, artifacts, and evidence records.

## Current repository mapping

### Runtime and interaction

- `python/arc3_runner.py` — authoritative ARC3 game lifecycle, actions, level handling, observations, history, replay, reset, restart, exports, and analysis commands.
- `scripts/interactive_runner.py` — runtime-aware terminal entry point.
- `python/interactive_runner.py` — full keyboard debugger implementation.
- `scripts/run_webui.py` and `webui/server.py` — browser terminal exposing the same runner rather than a second debugger.
- `scripts/prolog_controlled_runner.py` — executable SWI-Prolog-controlled demonstration.

### State, action trees, and evidence

- `python/action_tree.py` — deterministic action-tree directories, images, `state.json`, parent/child links, hashes, generated node READMEs, and the shared level identity registry.
- `object_registry.pl` — authoritative friendly identity source for the level.
- node-local `objects.pl`, `differences.pl`, `similarities.pl`, Turtle artifacts, and `rules.pl` — the mutable latest analysis view.
- per-run `llm_adapter_*.md` transcripts — immutable provider/model/profile comparison and restorable artifact snapshots.
- node `README.md` — state navigation, active transcript, historical transcript links, image, metadata, and embedded latest artifacts.

### LLM analysis and caching

- `config/llm_providers.json` — one provider registry plus reusable `prompt_text` sections. Each provider selects an ordered section list and may omit sections such as `transitions` when appropriate.
- `python/llm_providers.py` and `python/unsloth_studio.py` — OpenAI Responses, Anthropic Messages, and local Unsloth Studio routing and lifecycle management.
- `python/gpt_bridge.py` — one combined multimodal request and artifact-splitting pipeline.
- `python/llm_json.py` and `python/llm_json_patch.py` — strict parsing, deterministic repair, one text-only recovery pass, and required-key validation.
- `python/llm_transcripts.py` and `python/llm_readme_patch.py` — Markdown interaction records, artifact restoration, and README history integration.

### Symbolic execution

- `python/swipl_bridge.py` plus `prolog/arc3_agent.pl` — SWI-Prolog control seam.
- `prolog/turtle_dsl.pl` — authoritative motion-based Turtle execution semantics.

### Runtime resource discovery

Code, configuration, and generated action trees are resolved independently:

1. explicit path environment variables;
2. the launch directory and its parents;
3. `ARC3_RUNTIME_HOME` when it contains the requested resource;
4. the script/code checkout.

Startup reports the launch directory, code root, environment files, selected LLM configuration, and action-tree output path. The Windows launcher preserves the caller’s working directory so workspace-local `config/` and `action_trees/` remain discoverable.

## Phase 1 completion evidence

Phase 1 acceptance should include:

- repeatable game and level selection;
- captured actions, observations, images, and histories;
- deterministic action-tree navigation and replay;
- stable identity reuse through `object_registry.pl`;
- current-state and parent-transition artifacts;
- provider/model/profile comparison transcripts;
- restoration of a historical transcript into the latest artifact view;
- reset, restart, history navigation, and replay demonstrations;
- validation of cached artifacts before reuse;
- documentation for terminal, browser, Windows, provider configuration, and generated evidence;
- automated tests for action-tree storage, replay hashes, prompt composition, transcript layout/restoration, provider routing, and path discovery.

Phase 1 infrastructure is substantially present. Remaining work is normalization and acceptance hardening rather than creation of a second debugger.

---

# Phase 2 — Object Perception, Recognition, and Persistent Memory

## Required outcomes

Phase 2 extends captured states into reusable object knowledge:

- extract and represent objects from grids, images, and simple video inputs;
- represent properties, structure, relationships, position, orientation, scale, and appearance;
- maintain stable identities across examples, encounters, and transitions;
- match corresponding objects between states and repeated encounters;
- recognize recurring objects under supported translation, rotation, scale, reflection, recolor, noise, and partial visibility;
- detect movement, recoloring, resizing, addition, removal, and structural change;
- store objects in normalized generative forms;
- distinguish recognized content from potentially new object structure;
- prevent duplicate storage of already recognized objects;
- accumulate evidence and provenance across encounters;
- preserve encounter history and deterministic replay;
- provide persistent symbolic memory for objects, observations, and artifacts;
- regenerate objects from stored representations;
- demonstrate recognition under modest degradation and partial occlusion;
- provide tests and documentation for identity, recognition, regeneration, memory, and replay.

## Demonstration workflow

```text
Input image or game state
    → object extraction
    → object representation
    → object matching and correspondence
    → before-and-after comparison
    → persistent storage
    → later recognition as the same object
```

## Current repository mapping

The `python/object_memory/` package supplies shared contracts around existing and future providers:

- `CandidateObject` — stable provider-backed object facade.
- `PerceptionAdapter` and `GridAdapter` — modality and grid front ends without replacing the existing extractor.
- `GenerativeForm` and `CellLogoForm` — normalized regeneration interface reusing Turtle programs.
- `ResidualCandidate`, `ResidualDisposition`, and `ResidualGate` — explicit unexplained structure and admission policy.
- `CommittedAtom`, `SymbolicMemory`, and `SingleWriter` — normalized durable records and the single mutation path.
- shared provenance, rule, prediction, and transition records in `python/object_memory/models.py`.

The corresponding Prolog contracts include:

- `prolog/object_memory_contract.pl`;
- `prolog/generative_form.pl`;
- `prolog/residual_gate.pl`;
- `prolog/single_writer.pl`.

Persistent friendly identity continues to use the generated level-wide `object_registry.pl`; Phase 2 must not introduce a second identity database.

## Required Phase 2 services

The final Phase 2 implementation should expose:

- normalized observation and encounter identifiers;
- object extraction and canonicalization;
- object property and relationship queries;
- correspondence proposals with explicit evidence;
- identity merge/split proposals governed by the authoritative writer;
- generative-form fitting and residual measurement;
- faithful regeneration and observation comparison;
- append-only encounter history;
- durable symbolic object storage;
- artifact indexing for frames, masks, traces, embeddings, and reconstructions;
- lifecycle states such as active, demoted, and tombstoned without deleting provenance;
- deterministic replay from the same starting store and encounter log.

## Phase 2 completion evidence

Acceptance should demonstrate:

- extraction and normalized representation on ARC-style grids;
- stable correspondence across parent/current states and repeated encounters;
- recognition under modest translation, rotation, reflection, recolor, scale change, noise, and partial occlusion where supported;
- no duplicate durable identity when the same object is recognized again;
- explicit handling of genuinely new residual structure;
- successful regeneration through Turtle or another approved generative form;
- faithful comparison between regenerated and observed content;
- deterministic encounter replay;
- tests for false merge, false split, duplicate identity, evidence updates, and provenance preservation;
- documentation and runnable scripts showing the complete demonstration workflow.

The contracts and reference implementations are connected, but full perception, durable encounter storage, re-recognition quality, degradation handling, and acceptance demonstrations remain active work.

---

# Phase 3 — Game Object Learner Integration and Predictive Rule Learning

## Required outcomes

Phase 3 connects persistent object memory to learning and prediction:

- define a stable interface and data contract between perception/memory and the Game Object Learner;
- provide detected objects, properties, relationships, correspondences, differences, and encounter history;
- keep the learner independent of debugger and perception internals;
- validate interfaces and return structured errors;
- provide integration tests and example workflows;
- infer candidate object-level transformations and transition rules;
- retain multiple interpretations and evidence for successful and unsuccessful rules;
- apply learned transformations to new cases;
- record predictions before outcomes are observed;
- compare predictions with independently observed outcomes;
- update rule evidence from prediction success or failure;
- prevent post-hoc explanation from being counted as successful prediction;
- demonstrate recognition and completion of partly occluded objects;
- demonstrate operation across approved grid and raster environments;
- provide integration documentation, examples, acceptance results, and developer notes.

## Demonstration workflow

```text
Input game state
    → object perception and recognition
    → persistent object identity
    → structured Game Object Learner handoff
    → transition analysis
    → candidate transformation learning
    → prediction of a later state
    → application to a new case
    → independent evaluation
    → prediction, learned rule, or action recommendation
```

## Representative environment progression

```text
ARC-style grids
    → rendered arcade environments
    → fixed-camera physics examples
    → top-down manipulation with partial occlusion
```

The exact grid path should be made deterministic before broader raster and occlusion demonstrations are treated as accepted.

## Current repository mapping

### Python path

- `python/object_memory/integration.py` — `GameObjectLearnerPayload`, result records, validation, structured integration errors, plugin interface, and pipeline plugin.
- `python/object_memory/learning.py` — transition analysis, transformation candidates, rule induction, ranking, storage, execution, prediction ledger, independent outcome channel, and grading.
- `GameLearningPipeline` — connected orchestration from observed transition through prediction and later evaluation.

### Prolog path

- `prolog/transition_analysis.pl`;
- `prolog/transformation_learning.pl`;
- `prolog/rule_induction.pl`;
- `prolog/rule_ranking.pl`;
- `prolog/transition_rules.pl`;
- `prolog/prediction_ledger.pl`;
- `prolog/prediction_evaluation.pl`;
- `prolog/game_object_learner_api.pl`.

Generated `rules.pl` remains a valid LLM-backed evidence artifact. Native learning should extend the same observable/evidence-oriented shape rather than creating an unrelated rule format.

## Stable learner boundary

The learner payload must contain normalized references instead of debugger implementation objects. At minimum it should provide:

- observation and encounter IDs;
- object identities and properties;
- relationships and spatial structure;
- parent/current correspondence;
- direct state differences;
- action information;
- generative representations and artifact references;
- encounter history and provenance;
- candidate interpretations and confidence/evidence records.

The learner returns normalized transformation candidates, competing rules, predictions, evidence updates, and optional action recommendations. It must not mutate perception memory directly.

## Phase 3 completion evidence

Acceptance should include:

- payload-schema validation and stable serialization;
- structured error demonstrations;
- real handoff from Phase 2 objects and correspondences;
- transformation induction over observed transitions;
- multiple competing interpretations with retained evidence;
- application of learned transformations to unseen cases;
- predictions recorded before actions or outcomes;
- independent environment outcomes and deterministic grading;
- positive and negative rule evidence updates;
- proof that post-hoc rules do not receive prediction credit;
- integration demonstrations across the approved environment progression;
- partial-occlusion recognition/completion demonstration;
- reproducible benchmark and acceptance commands;
- integration documentation, examples, developer notes, and acceptance reports.

The Python and Prolog contracts are connected and tested with provider-driven examples. Real Phase 2 payloads, task-quality rule induction, prediction quality, broad environment coverage, and formal acceptance results remain incomplete.

---

# Shared execution modes

One normalized contract supports three implementations:

1. **PROLOG** — SWI-Prolog predicates and existing/generated `.pl` artifacts.
2. **GPT/LLM** — provider-generated, cached, and restorable analysis artifacts with explicit provenance.
3. **PYTHON** — deterministic native resolvers where appropriate.

Every provider returns a `NormalizedResult`. Provider capability discovery should state which operations are available rather than returning speculative empty interfaces.

# Protected Kaggle surface

These paths and their behavior remain protected:

- `agent/my_agent.py`;
- `scripts/play_local.py`;
- `scripts/build_notebook.py`;
- generated `notebooks/submission.ipynb`;
- `notebooks/kernel-metadata.json`;
- existing Kaggle Makefile targets, imports, paths, and packaging behavior.

Game Object Learner recommendations may be connected through a stable seam, but these protected entry points must not be renamed or repurposed.

# Components intentionally not duplicated

- another ARC3 runner;
- another action-tree store;
- another LLM analyzer or provider pipeline;
- another prompt directory separate from `config/`;
- another raw-response cache separate from the Markdown transcript history;
- another SWI subprocess bridge;
- another Turtle interpreter;
- another friendly identity database;
- parallel runners under `examples/`;
- phase-specific source directory trees;
- unrelated Python and Prolog rule-storage formats.

# Recommended integration order

1. Freeze observation, object, committed-atom, transition, artifact-reference, and learner-payload schemas.
2. Complete Phase 1 artifact validation, replay hashes, provenance, and acceptance demonstrations.
3. Implement append-only encounter persistence and artifact indexing.
4. Connect the existing grid extractor through `GridAdapter`.
5. Fit and regenerate exact grid objects through the existing Turtle semantics.
6. Implement deterministic correspondence, recognition, duplicate prevention, and identity governance.
7. Pass grid identity, replay, regeneration, and degradation tests.
8. Build real Game Object Learner payloads from Phase 2 objects and transitions.
9. Learn and apply candidate transformations while retaining rival interpretations.
10. Record predictions before ARC3 actions and grade independent responses.
11. Add raster, physics, degradation, and occlusion providers after the exact grid path is stable.
12. Produce reproducible acceptance reports for each phase.

See [TODO.md](TODO.md) for the executable backlog and [FILE_TREE.md](FILE_TREE.md) for the repository map.

[← Back to top-level README](README.md)
