[← Back to top-level README](README.md)

# Architecture — Image Perception to Recognizable Memory

## Document scope

This is the large technical overview. It describes the runtime, class and module ownership, data flow, cross-language contracts, persistent-memory model, learning architecture, and detailed architecture work still required.

Related documents:

- [TODO.md](TODO.md) — the concrete work we are actively doing, in execution order.
- [SOW_DELIVERABLES.md](SOW_DELIVERABLES.md) — the phase-by-phase deliverable checklist and evidence links.
- [FILE_TREE.md](FILE_TREE.md) — the complete repository ownership map.

The architecture document explains **how the system is intended to work**. The TODO explains **what we need to implement next**. The deliverables document explains **what must be demonstrated and checked off**.

## Architectural principles

- Extend the working ARC3 debugger rather than replacing it.
- Keep one runtime resolver, one ARC3 runner, one action-tree store, one provider router, one artifact pipeline, one identity authority, and one Turtle execution semantics.
- Keep runnable entry points under `scripts/`; do not recreate `examples/`.
- Do not create phase directories.
- Keep stable, human-readable identities across states, encounters, providers, transformations, predictions, and learned rules.
- Preserve prompts, provider settings, images, raw responses, normalized artifacts, timing, token usage, repairs, outcomes, and evidence as inspectable provenance.
- Keep raw observations as artifacts rather than durable semantic concepts.
- Treat similarity and embeddings as retrieval and proposal mechanisms only; they may not independently commit identity, merge objects, or increase evidence.
- Route durable memory and evidence mutation through `SingleWriter` or its authoritative Prolog equivalent.
- Credit a learned rule only when its prediction existed before the independently observed outcome.
- Preserve the protected Kaggle surface.

## End-to-end data flow

```text
ARC3 game, grid, image, or simple video
    → runtime and resource resolution
    → captured state, image, action, and history
    → deterministic action-tree node
    → object extraction
    → normalized object representation
    → generative form and residual analysis
    → stable identity and correspondence
    → direct parent/current differences
    → persistent encounter and artifact memory
    → Game Object Learner payload
    → candidate transformations
    → competing transition rules
    → prediction recorded before outcome
    → independent environment outcome
    → deterministic prediction grading
    → evidence update, learned rule, predicted state, or action recommendation
```

## Shared execution modes

The same contracts support three implementations:

1. **PROLOG** — SWI-Prolog predicates and generated or persistent `.pl` data.
2. **GPT/LLM** — provider-generated artifacts with explicit prompt and provider provenance.
3. **PYTHON** — deterministic native resolvers and orchestration.

Core shared classes:

- `ExecutionMode` — identifies PROLOG, GPT, or PYTHON execution.
- `NormalizedResult` — common result envelope.
- `CandidateObject` — provider-backed facade for object capabilities.
- `PrologProvider` — delegates to SWI-Prolog predicates.
- `GptArtifactProvider` — reads provider-generated artifacts and transcripts.
- `PythonProvider` — invokes deterministic native resolvers.

Architecture work:

- add explicit provider capability discovery;
- return structured unsupported-operation errors;
- attach source artifact, transcript, provider, and evidence references to every result;
- add equivalence fixtures across all three modes.

---

# Runtime and workspace architecture

## `scripts/_runtime.py`

Responsibilities:

- preserve the launch directory;
- locate the code checkout;
- load applicable `.env` files without overriding shell or IDE variables;
- resolve `config/llm_providers.json` independently;
- resolve writable `action_trees/` independently;
- configure import paths;
- optionally attach the PyCharm debugger;
- print the resolved path summary.

Resolution order for config and action trees:

1. explicit environment path;
2. launch directory and parents;
3. `ARC3_RUNTIME_HOME` when it contains the requested resource;
4. script/code checkout.

## `python/project_paths.py`

Responsibilities:

- expose the selected config file;
- expose the writable action-tree root;
- create history and export directories;
- retain compatibility aliases without restoring a separate prompt directory.

## Windows launchers

- `scripts/setup_windows.bat` — environment creation and dependency verification.
- `scripts/interactive_runner.bat` — venv-direct execution while preserving caller workspace discovery.

Architecture work:

- keep launcher behavior thin and deterministic;
- keep configuration in `.env` and `config/`, not in batch scripts;
- add a native Windows smoke test that records the resolved paths and launches one ARC3 state.

Corresponding deliverables: [Phase 1 runtime and interaction](SOW_DELIVERABLES.md#phase-1--grid-infrastructure-and-arc3-debugger-foundation).

---

# ARC3 debugger and state architecture

## `Arc3Runner`

Location: `python/arc3_runner.py`

Responsibilities:

- create and control the ARC3 environment;
- select games and levels;
- expose legal actions;
- execute simple and coordinate actions;
- capture observations and game state;
- manage `StepRecord` history;
- replay actions;
- reset levels and restart games;
- export state and score information;
- expose LLM and Prolog command entry points.

Detailed architecture work:

- define canonical state and action ordinals;
- add immutable `Observation` or `StateSnapshot` records;
- connect `StepRecord`, image hash, action data, and environment state to normalized observations;
- expose real transitions to object memory and learning;
- record predictions before action execution;
- capture post-action outcomes independently for grading.

## `StepRecord`

`StepRecord` remains the lightweight execution-history record. It should reference normalized observations and transitions instead of becoming the persistent semantic memory model.

## `ActionTreeStore`

Location: `python/action_tree.py`

Responsibilities:

- create deterministic state-node directories;
- store `image.png` and `state.json`;
- encode action paths in directory names;
- maintain parent and child navigation;
- generate GitHub-browsable READMEs;
- maintain the level-wide `object_registry.pl`;
- reject opaque object IDs;
- normalize state-local object files against the registry;
- provide deterministic hashes and replay paths.

Detailed architecture work:

- add schema versions to node metadata;
- add normalized observation and encounter IDs;
- include artifact-set, registry-version, and provenance metadata;
- validate cache compatibility before reuse;
- attach prediction, outcome, and grading references;
- expose stable artifact and evidence references to Phase 2 and Phase 3.

## `StateNode`

`StateNode` is the filesystem-backed handle. It should reference semantic observations, encounters, artifacts, and evidence rather than absorbing those schemas itself.

## `object_registry.pl`

The level-wide registry is the authoritative debugger identity source.

Rules:

- state-local files load rather than duplicate identities;
- newly observed identities are proposed and merged through controlled logic;
- opaque IDs are rejected;
- persistent Phase 2 identity either extends or explicitly maps to this authority;
- identity merge/split decisions preserve provenance.

Corresponding work: [TODO — Phase 1 normalization](TODO.md#phase-1-normalization-and-acceptance).

---

# LLM provider, prompt, and transcript architecture

## `config/llm_providers.json`

This is the unified source for:

- reusable `prompt_text` sections;
- ordered provider definitions;
- provider-specific prompt-section lists;
- model, key, endpoint, health, and reasoning capabilities.

A provider may omit a section such as `transitions` without duplicating the complete prompt.

## `LlmProviderRouter`

Location: `python/llm_providers.py`

Responsibilities:

- select and cycle configured providers;
- compose the selected provider’s prompt sections;
- adapt OpenAI-compatible Responses and Anthropic Messages calls;
- capture provider response metadata and usage;
- return a Responses-shaped result to the shared analyzer.

## `StudioAwareLlmProviderRouter`

Location: `python/unsloth_studio.py`

Responsibilities:

- authenticate to Unsloth Studio;
- inspect inference status;
- detect missing or different models;
- load the configured GGUF variant;
- wait for readiness;
- retry a no-model race once.

## `GptArcAnalyzer`

Location: `python/gpt_bridge.py`

Responsibilities:

- configure demo/deep/extreme analysis profiles;
- compose the selected provider prompt;
- add persistent context and parent/current images;
- request only needed artifact keys;
- split the normalized response into `.pl` artifacts;
- merge friendly identities;
- normalize `objects.pl` against the registry;
- refresh state READMEs.

## JSON recovery

- `python/llm_json.py` — strict parsing, local repair, required-key validation, normalized serialization.
- `python/llm_json_patch.py` — wraps the provider call, records the initial output, performs local repair or one text-only repair request, and keeps all interactions in one transcript.

## `LlmTranscriptRun`

Location: `python/llm_transcripts.py`

Responsibilities:

- produce unique provider/model/profile/token filenames;
- place restorable Prolog artifacts at the top;
- record state/action context, images, prompt sections, exact sent prompt, timing, usage, repair path, normalized JSON, and raw responses;
- preserve raw responses at the bottom;
- parse embedded artifacts;
- restore historical artifacts into the mutable latest view.

## README transcript integration

`python/llm_readme_patch.py` marks the active completed transcript, links every historical run, and prevents recursive transcript embedding.

Detailed architecture work:

- add transcript schema-version migration;
- add explicit artifact-set hashes;
- compare providers and analysis levels automatically;
- score restored/generated artifacts against later observations;
- link prediction and rule evidence into transcripts.

Corresponding deliverables: [Phase 1 generated artifacts and caching](SOW_DELIVERABLES.md#phase-1--grid-infrastructure-and-arc3-debugger-foundation).

---

# Phase 2 object perception and memory architecture

## `CandidateObject`

A stable facade representing a candidate semantic object. `part(name)` delegates a requested capability to the selected provider.

Required capabilities:

- properties;
- structure;
- relationships;
- generative form;
- correspondence proposals;
- differences;
- recognition evidence;
- provenance.

## `PerceptionAdapter`

A modality-neutral front end that converts a raw source into normalized observations and candidates.

## `GridAdapter`

A thin adapter over the existing grid extractor. It must not become a second object engine.

Architecture work:

- inspect and wrap the current extractor;
- normalize components, topology, holes, enclosures, bars, lines, and compounds;
- emit exact logical-grid geometry;
- preserve source artifact references.

## `GenerativeForm`

Interface for a normalized representation capable of regenerating an object.

Required methods conceptually include:

- `render()`;
- `fit(observation)`;
- `distance(observation)`;
- `residual(observation)`;
- `description_length()`;
- `supports(transform)`.

## `CellLogoForm`

Exact-grid generative form backed by existing Turtle programs and `prolog/turtle_dsl.pl`.

Architecture work:

- establish normalized Turtle program references;
- render through `SWIPrologBridge`;
- compare regenerated cells to observed cells;
- measure residuals explicitly;
- preserve exact holes, topology, and disconnected strokes.

## `ResidualCandidate` and `ResidualGate`

A residual is unexplained structure remaining after known forms are fitted. The gate decides whether it remains provisional, is rejected, or becomes a commit request.

## `CommittedAtom`

Backend-neutral durable semantic record. New atoms begin at zero confidence and accumulate evidence through controlled mutation.

## `SingleWriter`

The only authoritative mutation path for durable objects and evidence.

Responsibilities:

- commit admitted objects;
- add positive or negative evidence;
- merge or split identities through explicit decisions;
- demote or tombstone concepts;
- preserve provenance;
- prevent uncontrolled confidence changes.

## Planned `Observation`

Normalized immutable observation containing:

- observation ID;
- source modality;
- state/action ordinal;
- image/grid artifact references;
- dimensions and coordinate contract;
- candidate-object references;
- provenance and schema version.

## Planned `EncounterRecord` and `EncounterLog`

Append-only persistent record of an object encounter.

Required fields:

- encounter ID;
- observation ID;
- object identity or candidate identity;
- instance parameters;
- matched and changed properties;
- residuals;
- artifacts;
- evidence links;
- previous/next encounter references;
- deterministic hash.

## Planned `RecognitionAccount`

Explains why a candidate was or was not recognized as an existing object.

It should contain:

- candidate and stored identity references;
- matched properties;
- changed properties;
- allowed transformations;
- residual score;
- supporting and contradicting evidence;
- rival identity proposals;
- final decision source.

## Planned `SymbolicStore`

Durable access facade over Prolog or Atomspace storage. It should expose exact identity, atoms, evidence, lifecycle, and provenance without making embeddings authoritative.

## Planned `ArtifactIndex`

Indexes:

- frames;
- masks;
- Turtle programs;
- reconstructed images;
- embeddings;
- traces;
- transcripts;
- correspondence evidence;
- predictions and outcomes.

## Phase 2 correspondence architecture

The correspondence pipeline should:

1. generate candidates using geometry, identity, properties, topology, and optional embeddings;
2. score matched and changed properties;
3. preserve multiple proposals;
4. distinguish moved/recolored/resized/reshaped objects from appeared/disappeared objects;
5. submit merge/split decisions to the authoritative writer;
6. record evidence and provenance.

## Phase 2 recognition invariants

- recognition does not duplicate a known durable object;
- new residual structure remains explicit;
- partial visibility does not silently overwrite the complete form;
- false merges and false splits remain reversible through provenance;
- regeneration can be compared against the source observation;
- replay from the same store and encounter log is deterministic.

Corresponding work: [TODO — Phase 2 active work](TODO.md#phase-2-object-perception-and-persistent-memory).

Corresponding deliverables: [Phase 2 checklist](SOW_DELIVERABLES.md#phase-2--object-perception-recognition-and-persistent-memory).

---

# Phase 3 Game Object Learner architecture

## `GameObjectLearnerPayload`

Stable serialized boundary from perception/memory to learning.

It should include:

- schema version;
- observation and encounter IDs;
- stable object identities;
- normalized properties and relationships;
- parent/current correspondences;
- direct state differences;
- action information;
- generative-form and artifact references;
- encounter history;
- evidence and provenance;
- competing interpretations.

It must not contain debugger implementation objects such as `StateNode` or adapter instances.

## `IntegrationValidator`

Responsibilities:

- validate schema version;
- validate unique and resolvable identities;
- validate artifact and provenance references;
- validate before/after ordering;
- reject duplicate objects and malformed transitions;
- return structured integration errors.

## `GameObjectLearnerPlugin`

Stable interface used by callers. It should accept normalized state or transition payloads and return normalized results without directly mutating perception memory.

## `PipelineGameObjectLearnerPlugin`

Concrete plugin wrapping `GameLearningPipeline`.

## `TransitionAnalyzer`

Consumes normalized before/action/after data and emits direct observations only.

It should distinguish:

- unchanged;
- moved;
- appeared/disappeared;
- recolored;
- resized/reshaped;
- split/merged;
- opened/closed;
- consumed/created/destroyed;
- overwritten;
- HUD/status changes.

## `TransformationLearner`

Generates candidate transformations from observed deltas.

Required behavior:

- preserve competing candidates;
- cite concrete supporting evidence;
- expose assumptions;
- apply candidates to new states;
- compare predicted and actual transformed states.

## `RuleInducer`

Builds candidate rules from transformations and context. It should support specialization, generalization, rival interpretations, and explicit assumptions.

## `RuleRanker`

Ranks rules using:

- prior prediction success and failure;
- contradiction evidence;
- simplicity and description length;
- coverage;
- rival interpretations;
- applicability precision.

## `RuleStore` and `RuleExecutor`

`RuleStore` maintains exact rule identity and evidence. `RuleExecutor` applies a selected rule through domain-supplied applicability and execution callbacks.

## `PredictionLedger`

Append-only record proving prediction-before-outcome ordering.

Each prediction should include:

- prediction ID;
- rule and source-state IDs;
- predicted objects, relationships, changes, state, or action;
- creation ordinal and timestamp;
- evidence available at prediction time;
- later outcome reference;
- grade and grading evidence.

## `OutcomeChannel`

Obtains the independent later observation. It must not reuse the prediction as the outcome.

## `PredictionEvaluator`

Compares expected and observed results and returns a `PredictionGrade` with concrete evidence.

## `GameLearningPipeline`

Connected orchestration:

```text
transition analysis
    → transformation candidates
    → rule induction
    → rule ranking
    → rule storage
    → rule application
    → prior prediction
    → independent outcome
    → prediction grading
    → rule evidence update
```

## Prolog modules

- `transition_analysis.pl`;
- `transformation_learning.pl`;
- `rule_induction.pl`;
- `rule_ranking.pl`;
- `transition_rules.pl`;
- `prediction_ledger.pl`;
- `prediction_evaluation.pl`;
- `game_object_learner_api.pl`.

These modules should remain provider-driven and use the canonical object-memory contracts rather than duplicating Python models.

## Phase 3 integration architecture work

- freeze serialized payload and result schemas;
- build real payloads from Phase 2 objects and encounters;
- connect `Arc3Runner` transitions to the plugin;
- connect generated artifacts and native Prolog facts through providers;
- preserve competing transformations and rules;
- record predictions before actions;
- capture independent outcomes;
- update evidence through the authoritative writer;
- expose optional action recommendations to `agent/my_agent.py` through a stable seam.

Corresponding work: [TODO — Phase 3 active work](TODO.md#phase-3-game-object-learner-and-prediction).

Corresponding deliverables: [Phase 3 checklist](SOW_DELIVERABLES.md#phase-3--game-object-learner-integration-and-predictive-rule-learning).

---

# Environment progression

The implementation should progress in this order:

1. ARC-style exact grids;
2. rendered arcade environments;
3. fixed-camera physics examples;
4. top-down manipulation with partial occlusion.

The exact grid path should become deterministic and reproducible before broader raster environments are treated as accepted.

# Protected Kaggle surface

Do not rename or repurpose:

- `agent/my_agent.py`;
- `scripts/play_local.py`;
- `scripts/build_notebook.py`;
- generated `notebooks/submission.ipynb`;
- `notebooks/kernel-metadata.json`;
- existing Kaggle Makefile targets and packaging behavior.

# Components intentionally not duplicated

- another ARC3 runner;
- another action-tree store;
- another LLM analyzer/provider pipeline;
- another prompt directory;
- another raw-response cache outside transcripts;
- another SWI subprocess bridge;
- another Turtle interpreter;
- another friendly identity database;
- parallel example runners;
- phase-specific source trees;
- unrelated Python and Prolog rule formats.

# Architecture implementation sequence

1. Freeze observation, object, atom, transition, artifact-reference, evidence, payload, and result schemas.
2. Complete Phase 1 cache validation, replay hashes, provenance, and acceptance evidence.
3. Implement encounter persistence and artifact indexing.
4. Connect the existing object extractor through `GridAdapter`.
5. Fit and regenerate exact grid forms through `turtle_dsl.pl`.
6. Implement deterministic correspondence, recognition, duplicate prevention, and identity governance.
7. Feed real Phase 2 transitions into the connected Phase 3 pipeline.
8. Learn and apply competing transformations and rules.
9. Record predictions before ARC3 actions and grade independent outcomes.
10. Add raster, physics, degradation, and occlusion providers after exact-grid acceptance.
11. Add benchmark, ablation, provider comparison, and acceptance reporting.

[TODO.md](TODO.md) tracks the concrete implementation steps. [SOW_DELIVERABLES.md](SOW_DELIVERABLES.md) tracks delivery completion.

[← Back to top-level README](README.md)
