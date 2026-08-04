[← Back to top-level README](README.md)

# Architecture — Image Perception to Recognizable Memory

## Document scope

This is the large technical overview. It describes class and module ownership, runtime and provider boundaries, recorded evidence, persistent object memory, learning, prediction, and the detailed architecture work required after the delivered debugger foundation.

Related documents:

- [TODO.md](TODO.md) — the concrete work we are actively implementing, in execution order.
- [SOW_DELIVERABLES.md](SOW_DELIVERABLES.md) — the phase-by-phase deliverable checklist and evidence links.
- [FILE_TREE.md](FILE_TREE.md) — the complete repository ownership map.

The architecture document explains **how the system is organized**. The TODO explains **what we need to implement next**. The deliverables document explains **what has been delivered and what must still be checked off**.

## Phase boundary summary

The three phases deliberately separate debugger infrastructure from semantic intelligence:

1. **Phase 1 — ARC3 Debugger and Extensible Inspection Foundation** records and displays ARC3 observations, actions, history, provider calls, generated artifacts, readable identities, and replay evidence. It exposes pluggable command hooks but does not require the debugger itself to implement final perception, memory, learning, or prediction algorithms.
2. **Phase 2 — Object Perception, Recognition, and Persistent Memory** implements the semantic object layer behind the debugger. It turns observations and provider demonstrations into persistent identities, correspondence, calibrated evidence, regenerating Turtle object programs, and reusable memory.
3. **Phase 3 — Game Object Learner Integration and Predictive Rule Learning** learns object-level transformations and competing rules, records predictions before outcomes, evaluates them independently, updates rule evidence, and writes inspectable results back into the debugger.

The Phase 1 demonstration included visible Turtle mocks, candidate rules, critiques, and confidence or probability outputs. Phase 1 delivered the ability to invoke providers and inspect, preserve, compare, and restore those outputs. Later phases improve their semantic and predictive quality.

## Architectural principles

- Extend the delivered ARC3 debugger rather than replacing it.
- Keep one runtime resolver, one ARC3 runner, one action-tree store, one provider router, one artifact pipeline, one debugger identity registry, and one Turtle execution semantics.
- Keep runnable entry points under `scripts/`; do not recreate `examples/`.
- Do not create phase directories.
- Keep the ARC3 environment and its rendered observations authoritative for Phase 1 recording.
- Keep provider-generated interpretations explicitly attributable to their provider, prompt, model, configuration, and source observations.
- Preserve prompts, images, actions, raw responses, normalized artifacts, timing, token usage, repairs, critiques, confidence outputs, and restored selections as inspectable provenance.
- Treat Phase 1 object, difference, similarity, Turtle, rule, critique, and confidence files as **displayed provider artifacts**, not proof that the debugger itself implemented those algorithms.
- Extend `object_registry.pl` from a debugger browsing and provider-identity registry into persistent semantic identity during Phase 2; do not introduce an unrelated second identity namespace.
- Store each Phase 2 object with a Turtle program that redraws it through movement, rotation, pen state, and pen width; do not reconstruct objects by emitting filled coordinate boxes.
- Treat similarity and embeddings as retrieval and proposal mechanisms only; they may not independently commit identity, merge objects, or increase confidence.
- Route durable memory and evidence mutation through `SingleWriter` or its authoritative Prolog equivalent.
- Credit a learned rule only when its prediction existed before the independently observed outcome.
- Preserve the protected Kaggle surface.

## End-to-end data flow

```text
PHASE 1 — DEBUGGER AND EVIDENCE
ARC3 game
    → rendered observation and available environment metadata
    → user, agent, or provider-triggered command
    → action and resulting rendered observation
    → deterministic action-tree node
    → optional provider calls
    → optional objects, differences, similarities, Turtle mocks,
      rules, critiques, and confidence outputs
    → README/transcript inspection, comparison, restoration, and replay

PHASE 2 — OBJECT PERCEPTION AND MEMORY
recorded observation or external grid/image/video input
    → object extraction and normalized representation
    → per-object Turtle program using movement and pen width
    → regeneration and source comparison
    → stable persistent identity and correspondence
    → positive and negative recognition evidence
    → calibrated confidence and persistent symbolic memory

PHASE 3 — LEARNING AND PREDICTION
persistent objects, correspondences, actions, and observed changes
    → Game Object Learner payload
    → candidate transformations and competing rules
    → assumptions, critiques, probabilities, and evidence
    → prediction recorded before outcome
    → independently observed environment outcome
    → deterministic grading and rule-evidence update
    → debugger-visible rule, prediction, grade, or action recommendation
```

---

# Shared pluggable command and provider architecture

The debugger is intentionally expandable. A command can invoke a provider without requiring the debugger to own the provider’s internal algorithm.

Supported and planned execution modes share one normalized result boundary:

1. **PROLOG** — SWI-Prolog predicates and generated or persistent `.pl` data.
2. **GPT/LLM** — provider-generated artifacts with explicit prompt, model, and request provenance.
3. **PYTHON** — deterministic native resolvers and orchestration.
4. **External providers** — later perception, memory, learner, or evaluation services connected through adapters.

Core shared classes:

- `ExecutionMode` — identifies PROLOG, GPT, or PYTHON execution.
- `NormalizedResult` — common result envelope.
- `CandidateObject` — provider-backed facade for object capabilities used by Phase 2.
- `PrologProvider` — delegates to SWI-Prolog predicates.
- `GptArtifactProvider` — reads provider-generated artifacts and transcripts.
- `PythonProvider` — invokes deterministic native resolvers.

A debugger command may initially:

- call a stub;
- report an unsupported capability;
- invoke a configured provider;
- load a previously generated artifact;
- display a normalized placeholder result;
- delegate to a Phase 2 or Phase 3 component.

The command surface should remain expandable without redesigning the debugger, terminal UI, web UI, or action-tree layout.

Shared architecture work:

- add explicit provider capability discovery;
- return structured unsupported-operation errors;
- attach source observations, artifacts, transcripts, provider details, and evidence references to every normalized result;
- add equivalence fixtures where PROLOG, GPT/LLM, and PYTHON implementations claim the same capability;
- keep provider outputs visibly distinguishable from independently verified results.

---

# Phase 1 — ARC3 Debugger and Extensible Inspection Foundation

## Phase 1 purpose and boundary

Phase 1 is the delivered debugger, evidence-recording surface, and expandable command framework. It makes ARC3 gameplay and provider output visible, navigable, repeatable, and inspectable.

Phase 1 does **not** require the debugger itself to determine:

- what semantic objects exist;
- whether two observations contain the same persistent object;
- what truly moved, changed, split, merged, or disappeared;
- which Turtle program is the canonical object representation;
- which rule is correct;
- whether a confidence estimate is calibrated;
- what later state will occur;
- which action should be recommended.

Those outputs may be shown during Phase 1 when generated by a bootstrap provider. Their final implementation and quality belong to later phases.

## `Arc3Runner`

Location: `python/arc3_runner.py`

Phase 1 responsibilities:

- create and control the ARC3 environment;
- select games and levels;
- expose legal actions;
- execute simple and coordinate actions;
- capture rendered observations and available environment metadata;
- manage action and execution history through `StepRecord`;
- replay previously recorded actions;
- reset levels and restart games;
- export state and score information;
- expose LLM, Prolog, Python, and future external command entry points.

The runner records environment observations and actions. It does not need a final semantic state model in order to satisfy Phase 1.

Later integration work:

- expose recorded transitions to Phase 2 and Phase 3 without moving their algorithms into `Arc3Runner`;
- record Phase 3 predictions before action execution;
- capture resulting observations independently for prediction grading;
- keep optional semantic records linked rather than embedded into the runner’s core lifecycle.

## `StepRecord`

`StepRecord` remains the lightweight execution-history record used by the debugger. It captures enough information to reproduce and inspect the action sequence.

Phase 2 may associate semantic encounters and persistent object identities with this history. Phase 3 may associate predictions and outcomes with it. Neither extension should turn `StepRecord` into the semantic memory or rule database.

## `ActionTreeStore`

Location: `python/action_tree.py`

Phase 1 responsibilities:

- create deterministic state-node directories;
- store `image.png` and `state.json`;
- encode action paths in directory names;
- maintain parent and child navigation;
- generate GitHub-browsable node READMEs;
- preserve encounter and action history for deterministic replay;
- maintain the level-wide `object_registry.pl` used to keep provider identities readable across state transitions;
- reject opaque provider object IDs when friendly identities are required;
- save, link, compare, and restore provider-generated artifacts;
- provide deterministic hashes and replay paths.

The action tree is an evidence and debugging surface. It records what was observed, what action occurred, which providers were invoked, and what they returned.

## `StateNode`

`StateNode` is the filesystem-backed handle to a debugger node. It identifies the rendered observation, metadata, action path, provider artifacts, transcripts, and navigation links.

Later phases may attach semantic observations, persistent encounters, predictions, grades, and evidence references to a node. The node itself should not become the implementation of those systems.

## `object_registry.pl`

Phase 1 maintains `object_registry.pl` as part of the debugger’s readable evidence layer.

Phase 1 rules:

- keep provider object names stable and human-readable across state transitions;
- let node-local artifact files reference rather than duplicate level identities;
- preserve provenance showing which provider proposed or reused an identity;
- allow restored transcripts to restore their corresponding latest artifact view;
- keep identities inspectable in generated README files.

Phase 2 extension:

- connect or extend these readable provider identities into persistent semantic object identities;
- govern cross-encounter recognition, merge, split, and duplicate-prevention decisions;
- retain the original Phase 1 provider and encounter provenance.

The debugger’s maintenance of `object_registry.pl` is therefore a delivered Phase 1 capability and an intentional bootstrap point for later object memory.

## Pluggable analysis commands

Phase 1 contains menus, command stubs, provider adapters, callbacks, and artifact slots for analyses that may be implemented by different systems.

Examples include commands for:

- object descriptions;
- current/previous observation comparison;
- similarities and proposed correspondence;
- Turtle reconstruction or mock visualization;
- candidate rules;
- rule critiques;
- probability or confidence output;
- Prolog queries;
- future memory, learner, prediction, and action-recommendation services.

Phase 1 owns:

- invoking the selected provider;
- supplying current and previous images, action context, metadata, and available history;
- displaying provider status and errors;
- saving the exact request and response;
- splitting normalized artifacts into inspectable files;
- linking artifacts into the node README;
- comparing runs and restoring a historical run.

The provider owns the interpretation it returned.

## Provider artifacts displayed by the debugger

Phase 1 can display and preserve:

- `objects.pl` — provider-proposed object descriptions;
- `differences.pl` — provider-proposed current/previous differences;
- `similarities.pl` — provider-proposed correspondence or similarity;
- `turtle_from_image.pl` — a Turtle mock or reconstruction supplied for inspection;
- `turtle_from_diff.pl` — a provider-supplied visual transformation description;
- `rules.pl` — candidate rules, critiques, probabilities, confidence values, and supporting context;
- future provider-defined artifacts registered through the same extensible mechanism.

Their presence demonstrates the debugger’s invocation, display, caching, and evidence capabilities. It does not, by itself, claim that Phase 1 completed the final algorithms represented by those files.

## Turtle mocks in Phase 1

The Phase 1 demonstration video showed Turtle mock outputs. The debugger can:

- request or load a Turtle artifact;
- display its source;
- execute it for visualization when the interpreter is available;
- compare the rendered mock with the recorded observation;
- preserve alternative provider versions;
- link the mock and its provenance from the node README.

Phase 1 does not require the debugger to learn the Turtle program or establish it as the persistent semantic object representation.

Phase 2 requires each recognized object to carry a regenerating Turtle program with movement, rotation, pen state, and pen width semantics rather than filled coordinate boxes.

## LLM provider, prompt, and transcript architecture

### `config/llm_providers.json`

Unified source for:

- reusable `prompt_text` sections;
- ordered provider definitions;
- provider-specific prompt-section lists;
- model, key, endpoint, health, and reasoning capabilities.

A provider may omit a section such as `transitions` without duplicating the complete prompt.

### `LlmProviderRouter`

Location: `python/llm_providers.py`

Responsibilities:

- select and cycle configured providers;
- compose the selected provider’s prompt sections;
- adapt OpenAI-compatible Responses and Anthropic Messages calls;
- capture provider response metadata and usage;
- return a normalized result to the shared analyzer.

### `StudioAwareLlmProviderRouter`

Location: `python/unsloth_studio.py`

Responsibilities:

- authenticate to Unsloth Studio;
- inspect inference status;
- detect missing or different models;
- load the configured model variant;
- wait for readiness;
- retry a no-model race once.

### `GptArcAnalyzer`

Location: `python/gpt_bridge.py`

Phase 1 responsibilities:

- configure demo, deep, and extreme provider profiles;
- compose the selected provider prompt;
- include available persistent context and current/previous images;
- request the selected artifact set;
- split the normalized response into inspectable `.pl` artifacts;
- maintain readable provider identities through `object_registry.pl`;
- refresh node READMEs.

It is a provider bridge retained under its compatibility name, not the final native object learner.

### JSON recovery

- `python/llm_json.py` — strict parsing, local repair, required-key validation, and normalized serialization.
- `python/llm_json_patch.py` — records initial output, performs local repair or one text-only repair request, and keeps the interactions in one transcript.

### `LlmTranscriptRun`

Location: `python/llm_transcripts.py`

Responsibilities:

- produce unique provider/model/profile/token filenames;
- place restorable Prolog artifacts at the top;
- record state/action context, images, prompt sections, exact sent prompt, timing, usage, repair path, normalized JSON, and raw responses;
- preserve raw responses at the bottom;
- parse embedded artifacts;
- restore historical artifacts into the mutable latest view.

### README transcript integration

`python/llm_readme_patch.py` marks the active completed transcript, links every historical run, and prevents recursive transcript embedding.

## Runtime and workspace architecture

### `scripts/_runtime.py`

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

### `python/project_paths.py`

Responsibilities:

- expose the selected config file;
- expose the writable action-tree root;
- create history and export directories;
- retain compatibility aliases without restoring a separate prompt directory.

### Windows launchers

- `scripts/setup_windows.bat` — environment creation and dependency verification.
- `scripts/interactive_runner.bat` — venv-direct execution while preserving caller workspace discovery.

## Phase 1 delivered outcome

Phase 1 delivers the ability to:

- run and inspect selected ARC3 games and levels;
- record rendered observations, actions, available metadata, and execution history;
- browse gameplay encounters through a GitHub action tree;
- replay, reset, restart, and navigate recorded paths;
- invoke replaceable providers through expandable commands;
- provide current/previous observations and action context to those providers;
- maintain readable provider identities through `object_registry.pl`;
- display objects, differences, similarities, Turtle mocks, rules, critiques, and confidence outputs;
- preserve every provider request and response through README-linked artifacts and transcripts;
- cache, compare, and restore provider-generated artifacts;
- provide the integration seams used by Phase 2 and Phase 3.

Post-delivery debugger hardening may continue, but it is not reclassified as an undelivered Phase 1 semantic algorithm.

Corresponding deliverables: [Phase 1 checklist](SOW_DELIVERABLES.md#phase-1--arc3-debugger-and-extensible-inspection-foundation).

---

# Phase 2 — Object Perception, Recognition, and Persistent Memory

## Phase 2 purpose and boundary

Phase 2 implements the semantic object layer behind the Phase 1 debugger. It converts observations and bootstrap provider demonstrations into repeatable object extraction, persistent identity, correspondence, generative reconstruction, calibrated recognition evidence, and reusable memory.

The debugger remains the inspection surface. Phase 2 supplies and improves the object capabilities shown through that surface.

## `CandidateObject`

A stable facade representing a candidate semantic object. `part(name)` delegates a requested capability to the selected provider.

Required capabilities:

- geometry and properties;
- structure and topology;
- relationships;
- position, orientation, scale, and appearance;
- generative Turtle form;
- correspondence proposals;
- changed-property descriptions;
- recognition evidence and confidence;
- provenance.

## `PerceptionAdapter`

A modality-neutral front end converting a grid, image, or simple video source into normalized observations and object candidates.

## `GridAdapter`

A thin adapter over the existing grid extractor. It must not become a second object engine.

Architecture work:

- inspect and wrap the current extractor;
- normalize components, topology, holes, enclosures, bars, lines, and compound objects;
- emit exact logical-grid geometry;
- preserve source artifact references;
- produce one or more candidate object records suitable for persistent recognition.

## Raster and simple-video adapters

Pluggable providers should extend the same normalized object and encounter contracts to:

- image inputs;
- rendered arcade frames;
- fixed-camera sequences;
- simple video inputs;
- top-down manipulation scenes.

These adapters should not change the persistent identity or learner interfaces.

## `GenerativeForm`

Interface for a normalized representation capable of regenerating an object.

Required methods conceptually include:

- `render()`;
- `fit(observation)`;
- `distance(observation)`;
- `residual(observation)`;
- `description_length()`;
- `supports(transform)`.

## `CellLogoForm` and per-object Turtle programs

`CellLogoForm` is the exact-grid generative form backed by `prolog/turtle_dsl.pl`.

Every recognized grid object should store or reference a Turtle program that redraws that object using:

- forward movement;
- rotation;
- pen-up and pen-down state;
- pen width;
- color or other supported drawing state when needed.

The implementation must avoid regenerating objects by enumerating or filling coordinate boxes. A thick line should be represented using pen width rather than a sequence of adjacent rectangles.

Architecture work:

- establish normalized per-object Turtle-program references;
- render through `SWIPrologBridge`;
- compare regenerated cells with the source object;
- measure residuals explicitly;
- preserve exact holes, topology, disconnected strokes, and supported thickness;
- retain both the source observation and generated program as evidence;
- allow alternative candidate programs while preserving their fit scores and provenance.

## `ResidualCandidate` and `ResidualGate`

A residual is unexplained structure remaining after known forms are fitted. The gate decides whether the residual remains provisional, is rejected, or becomes a request for a new persistent object or substructure.

## Persistent identity and `object_registry.pl`

Phase 2 extends the readable identities already maintained by the debugger.

Required behavior:

- reuse compatible identities across examples, encounters, and transitions;
- retain provider and observation provenance from Phase 1;
- represent competing identity proposals;
- route merge and split decisions through controlled logic;
- prevent duplicate persistent storage when an existing object is recognized again;
- keep false merges and false splits reversible through evidence and provenance.

## Correspondence and change detection

The correspondence pipeline should:

1. generate candidates using identity, geometry, topology, properties, relationships, and optional embeddings;
2. score matched and changed properties;
3. preserve multiple competing proposals;
4. recognize supported translation, rotation, scale, reflection, recoloring, noise, and partial visibility;
5. distinguish moved, recolored, resized, reshaped, appeared, disappeared, split, and merged objects;
6. record positive and negative evidence;
7. update calibrated confidence without letting similarity alone commit identity.

## `CommittedAtom`

Backend-neutral durable semantic record. New atoms begin at zero confidence and accumulate positive or negative evidence through controlled mutation.

## `SingleWriter`

The only authoritative mutation path for durable objects and evidence.

Responsibilities:

- commit admitted objects;
- add positive or negative evidence;
- update calibrated confidence;
- merge or split identities through explicit decisions;
- demote or tombstone concepts;
- preserve provenance;
- prevent uncontrolled confidence changes.

## Planned `Observation`

Normalized immutable semantic observation containing:

- observation ID;
- source modality;
- source action-tree node when applicable;
- image/grid/video artifact references;
- dimensions and coordinate contract;
- candidate-object references;
- provenance and schema version.

This is a Phase 2 semantic record layered over the rendered observation already preserved by Phase 1.

## Planned `EncounterRecord` and `EncounterLog`

Phase 1 already preserves gameplay and provider encounter history. Phase 2 adds semantic encounter records and deterministic replay of memory updates.

Required fields:

- encounter ID;
- observation ID and Phase 1 node reference;
- object identity or candidate identity;
- instance parameters;
- matched and changed properties;
- Turtle-program and reconstruction references;
- residuals;
- confidence and evidence links;
- previous/next semantic encounter references;
- deterministic hash.

## Planned `RecognitionAccount`

Explains why a candidate was or was not recognized as an existing object.

It should contain:

- candidate and stored identity references;
- matched properties;
- changed properties;
- allowed transformations;
- Turtle reconstruction fit;
- residual score;
- supporting and contradicting evidence;
- rival identity proposals;
- calibrated confidence;
- final decision source.

## Planned `SymbolicStore`

Durable access facade over Prolog or Atomspace storage. It should expose exact identity, atoms, Turtle programs, evidence, confidence, lifecycle, and provenance without making embeddings authoritative.

## Planned `ArtifactIndex`

Indexes:

- source frames and grids;
- masks and components;
- per-object Turtle programs;
- reconstructed objects and images;
- embeddings;
- traces;
- transcripts;
- correspondence evidence;
- recognition accounts;
- predictions and outcomes.

## Phase 2 recognition invariants

- recognition does not duplicate a known durable object;
- new residual structure remains explicit;
- partial visibility does not silently overwrite the complete form;
- false merges and false splits remain reversible through provenance;
- each stored object has a regenerating Turtle program or an explicitly documented alternative form;
- Turtle reconstruction uses movement and pen-width semantics rather than filled-box shortcuts;
- regeneration is compared with the source object;
- confidence reflects accumulated positive and negative evidence;
- replay from the same Phase 1 history, semantic store, and encounter log is deterministic.

## Phase 2 demonstration workflow

```text
Input image or game state
    → object extraction
    → normalized object representation and Turtle program
    → object matching and correspondence
    → before-and-after comparison
    → evidence and confidence update
    → persistent storage
    → Turtle regeneration
    → later recognition as the same object
```

Corresponding work: [TODO — Phase 2 active work](TODO.md#phase-2--object-perception-recognition-and-persistent-memory).

Corresponding deliverables: [Phase 2 checklist](SOW_DELIVERABLES.md#phase-2--object-perception-recognition-and-persistent-memory).

---

# Phase 3 — Game Object Learner Integration and Predictive Rule Learning

## Phase 3 purpose and boundary

Phase 3 implements learning and prediction over the persistent objects, Turtle forms, correspondences, actions, changes, evidence, and encounter history produced by Phase 2.

The Game Object Learner remains independent of debugger internals. The Phase 1 debugger continues to display Phase 3 rules, critiques, confidence estimates, probabilities, predictions, grades, and recommendations as inspectable evidence.

## `GameObjectLearnerPayload`

Stable, versioned serialized boundary from perception and memory to learning.

It should include:

- schema version;
- observation and encounter IDs;
- stable object identities;
- normalized properties and relationships;
- parent/current correspondences;
- direct state differences;
- action information;
- Turtle-program and other generative-form references;
- source artifacts;
- encounter history;
- positive and negative evidence;
- confidence and provenance;
- competing interpretations.

It must not contain debugger implementation objects such as `StateNode` or adapter instances.

## `IntegrationValidator`

Responsibilities:

- validate schema version;
- validate unique and resolvable identities;
- validate artifact, Turtle-program, and provenance references;
- validate before/action/after ordering;
- reject duplicate objects and malformed transitions;
- return structured integration errors.

## `GameObjectLearnerPlugin`

Stable interface used by callers. It accepts normalized state or transition payloads and returns normalized results without directly mutating perception memory.

## `PipelineGameObjectLearnerPlugin`

Concrete plugin wrapping `GameLearningPipeline`.

## `TransitionAnalyzer`

Consumes normalized before/action/after data and emits direct observations suitable for candidate learning.

It should distinguish:

- unchanged;
- moved;
- appeared or disappeared;
- recolored;
- resized or reshaped;
- split or merged;
- opened or closed;
- consumed, created, or destroyed;
- overwritten;
- HUD or status changes.

## `TransformationLearner`

Generates candidate object-level transformations from observed deltas.

Required behavior:

- preserve competing candidates;
- cite concrete supporting evidence;
- expose assumptions and critiques;
- attach confidence or probability estimates;
- apply candidates to new states;
- compare predicted and actual transformed states.

## `RuleInducer`

Builds candidate rules from transformations and context. It should support specialization, generalization, rival interpretations, explicit assumptions, critiques, and evidence references.

## `RuleRanker`

Ranks and refines rules using:

- prior prediction success and failure;
- supporting and contradicting evidence;
- simplicity and description length;
- coverage;
- rival interpretations;
- applicability precision;
- calibrated confidence or probability;
- critique results.

Probability and confidence values shown in Phase 1 provider artifacts are bootstrap displays. Phase 3 implements and evaluates rule-level confidence using actual prediction history.

## `RuleStore` and `RuleExecutor`

`RuleStore` maintains exact rule identity, assumptions, critiques, probability, and evidence. `RuleExecutor` applies a selected rule through domain-supplied applicability and execution callbacks.

## `PredictionLedger`

Append-only record proving prediction-before-outcome ordering.

Each prediction should include:

- prediction ID;
- rule and source-state IDs;
- predicted objects, relationships, changes, state, or action recommendation;
- prediction confidence;
- creation timestamp or sequence ordinal;
- evidence available at prediction time;
- later outcome and grade references.

## `OutcomeChannel` and `PredictionEvaluator`

The outcome channel receives independently observed ARC3 results. The evaluator compares them with predictions without allowing later observations to rewrite the original prediction.

Grades should distinguish:

- success;
- failure;
- partial match;
- contradiction;
- ungradable or unsupported outcome.

## Evidence update

Prediction grading should:

- add positive evidence for successful prior predictions;
- add negative evidence for failures and contradictions;
- update rule confidence and ranking;
- preserve rival rules;
- prevent post-hoc explanations from receiving predictive credit;
- retain the original prediction and outcome as inspectable evidence.

## Debugger and README writeback

Phase 3 should write normalized artifacts back through the Phase 1 inspection surface, including:

- candidate transformations;
- competing rules;
- assumptions;
- critiques;
- probability or confidence estimates;
- pre-outcome predictions;
- independent outcomes;
- grades;
- positive and negative evidence updates;
- learned rules;
- optional action recommendations.

The action-tree README should link the source observations, Phase 2 objects, rule evidence, prediction record, outcome, and grade.

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

## Environment progression

```text
ARC-style grids
    → rendered arcade environments
    → fixed-camera physics examples
    → top-down manipulation with partial occlusion
```

Exact-grid identity, Turtle regeneration, memory replay, and prediction ordering should be deterministic before broader raster and occlusion environments are treated as accepted.

Corresponding work: [TODO — Phase 3 active work](TODO.md#phase-3--game-object-learner-integration-and-predictive-rule-learning).

Corresponding deliverables: [Phase 3 checklist](SOW_DELIVERABLES.md#phase-3--game-object-learner-integration-and-predictive-rule-learning).

---

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
- another debugger UI for each provider;
- another LLM analyzer or provider pipeline;
- another prompt directory separate from `config/`;
- another raw-response cache separate from the Markdown transcript history;
- another SWI subprocess bridge;
- another Turtle interpreter;
- another debugger identity registry unrelated to `object_registry.pl`;
- another persistent semantic identity namespace without an explicit mapping to the debugger registry;
- parallel runners under `examples/`;
- phase-specific source directory trees;
- unrelated Python and Prolog rule-storage formats.

# Recommended integration order

1. Preserve Phase 1 as the delivered debugger and evidence surface; do not move semantic algorithms into it.
2. Freeze Phase 2 observation, encounter, object, Turtle-program, evidence, confidence, and provenance schemas.
3. Connect the existing grid extractor through `GridAdapter`.
4. Store and execute one movement-and-pen-width Turtle program per recognized object.
5. Compare regenerated objects with their source observations and record residuals.
6. Implement persistent identity, correspondence, duplicate prevention, and calibrated recognition evidence.
7. Implement semantic encounter memory and deterministic replay over Phase 1 history.
8. Build real Game Object Learner payloads from Phase 2 objects and transitions.
9. Learn, critique, rank, and apply competing transformations and rules.
10. Record predictions before ARC3 actions and grade independent outcomes.
11. Write rules, critiques, probabilities, predictions, grades, and recommendations back through the debugger evidence surface.
12. Add raster, physics, degradation, and occlusion providers after the exact-grid path is stable.
13. Produce reproducible acceptance evidence for Phase 2 and Phase 3.

See [TODO.md](TODO.md) for active implementation work and [SOW_DELIVERABLES.md](SOW_DELIVERABLES.md) for delivery status.

[← Back to top-level README](README.md)
