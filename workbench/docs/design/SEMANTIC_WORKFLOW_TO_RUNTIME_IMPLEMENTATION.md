[← Back to repository README](../../../README.md)

# Semantic Workflow to Runtime Implementation

## Core idea

Workflow design and operation implementation are separate stages.

The first stage produces a complete **semantic workflow**. It describes what must happen: steps, dependencies, control flow, inputs, outputs, value bindings, limits, and required semantic operation IDs. The workflow should be understandable and valid before deciding how every operation will execute.

The second stage resolves each semantic operation to a concrete implementation. This happens after the entire workflow is available and may happen as late as runtime. A semantic operation can:

- map to an existing Python callable;
- map to an existing Prolog predicate;
- invoke an LLM with a selected prompt and model policy;
- call a human-input adapter or external service;
- select one inherited implementation variant;
- generate a new implementation, validate it, and save it as a concrete child of the semantic operation;
- remain unresolved and produce an explicit planning or runtime error when no allowed implementation exists.

## Why resolution happens later

The complete workflow provides information that an isolated operation does not have. Runtime resolution can consider:

- the actual input and output bindings;
- neighboring operations and their representations;
- loop bounds and retry behavior;
- workspace inheritance and local overrides;
- available Python, Prolog, model, prompt, and service capabilities;
- credentials and system policy;
- cost, latency, health, benchmark, and reproducibility requirements;
- the concrete values and datatypes present in the run.

Therefore, workflow generation must not prematurely hard-code an implementation merely because one is convenient. It should name the semantic operation and preserve enough contract information for the later resolver.

## Resolution lifecycle

1. A user or model writes an English workflow specification.
2. A constrained workflow compiler produces MeTTa or JSON containing semantic operations and validated dataflow.
3. Preflight validates step IDs, bindings, dependencies, loop targets, bounds, and operation availability.
4. For each semantic operation, the resolver gathers all inherited and workspace-local implementations.
5. Policy filters out implementations that are unavailable, unhealthy, unauthorized, incompatible, or too costly.
6. The resolver selects an existing implementation or asks an implementation-producing model to create a new implementation.
7. Generated code or logic is saved as a concrete operation child, never silently embedded into the semantic workflow.
8. The selected implementation is validated using its declared tests, probes, types, and sandbox policy.
9. The runtime freezes the resolved mapping with the run so later inspection can reproduce which Python callable, Prolog predicate, LLM prompt/model, or other adapter executed each step.
10. Runtime evidence can influence later selections without rewriting the semantic meaning of the workflow.

## Loop and reevaluation inference

The workflow compiler may help preflight propose where control should repeat or reconsider a prior decision. Useful evidence includes a value being overwritten repeatedly, a value accumulating across steps, a retry condition produced by an observed side effect, a time or item limit, or new evidence invalidating a downstream choice.

Each proposal must identify the condition-producing step, backward target, finite bound, values retained across iterations, values reset for the next iteration, new values that trigger reevaluation, and the choice or operation being reconsidered. Preflight remains authoritative. It validates side effects and dataflow, then accepts, adjusts, splits, merges, or rejects the proposal. No generated control edge may create an unbounded cycle.

## Two LLM execution modes

An LLM-backed operation can reason in two materially different ways.

### Runtime-adaptive reasoning

The operation receives the current context and decides what to do as the run unfolds. This is flexible and useful when observations are unpredictable, but it can meander, repeat work, change strategy silently, or consume an uncertain amount of time and tokens. The runtime must constrain it with a goal, allowed tools and operations, typed inputs and outputs, budgets, stopping rules, and validation checkpoints.

### Prepared Bicameral Mode CoT

A Coach prepares an explicit, inspectable reasoning plan before the Thinker begins execution. This is the low-frequency form of **Bicameral Mode CoT**: the Coach initially supplies the Thinker's questions, considerations, branches, and stopping tests, then updates them only at declared checkpoints or when replanning is required. This is not a request to expose a model's private chain-of-thought. The plan is a structured artifact containing goals, ordered actions, branches, evidence requirements, reevaluation conditions, tool permissions, budgets, and completion tests.

The prepared plan can be represented as MeTTa or JSON and versioned like any other semantic resource. Each plan node should declare:

- the question or subgoal being addressed;
- required inputs and evidence;
- the allowed operation, tool, prompt, or model call;
- the expected typed output;
- success and failure checks;
- branch and retry conditions;
- values retained or reset;
- reevaluation triggers;
- time, token, call, and iteration bounds.

At runtime, a plan controller gives the model only the current node, relevant evidence, and permitted actions. It validates the result before advancing. The model may not silently skip, insert, reorder, or rewrite plan nodes. When reality invalidates the prepared plan, the controller records a structured deviation and either follows an existing reevaluation branch or returns to preflight for a revised plan.

### Hybrid mode

Prepared and adaptive reasoning can be combined. The prepared plan fixes the high-level sequence, boundaries, and acceptance tests, while selected nodes permit bounded local reasoning. This preserves control and reproducibility without pretending every runtime observation can be known in advance.

### Interactive Bicameral Mode CoT

Interactive Bicameral Mode CoT is the high-frequency form. A Thinker model and a Coach model alternate in a bounded control loop. The Thinker receives the current task, evidence, and the Coach's latest questions and considerations, then returns a structured working result. The Coach evaluates that result against the goal, prepared plan when present, evidence requirements, budgets, and completion tests. It then updates the Thinker's questions and considerations and chooses exactly one next directive: continue, investigate a named gap, revise a named conclusion, call an allowed operation, return to a prior checkpoint, request replanning, or stop.

The Coach does not need access to private hidden chain-of-thought. It coaches from inspectable artifacts such as hypotheses, claims, cited evidence, uncertainties, attempted actions, tool results, proposed next actions, and validation failures. The Thinker is likewise asked for concise structured work products rather than private internal reasoning.

The Bicameral loop must declare:

- separate Thinker and Coach prompt/model policies;
- a shared typed working-state schema;
- which fields the Thinker may update;
- which directives the Coach may issue;
- evidence and validation requirements for advancing;
- maximum coaching rounds, tokens, calls, time, and tool usage;
- conditions under which the Coach must stop, fail, or return to preflight;
- whether a human or higher-level controller may override either model.

### Coaching cadence

Prepared and interactive Bicameral Mode CoT are the same architecture with different Coach update schedules:

- `prepared`: Coach once before execution, then only on failure or explicit replan.
- `milestone`: Coach after named workflow checkpoints or phase transitions.
- `per_round`: Coach after every Thinker work product.
- `adaptive`: Coach when a declared trigger fires, such as uncertainty, contradiction, missing evidence, validation failure, budget pressure, repeated output, or a changed world state.

The workflow must declare `coachCadence`, its triggers or milestones, and `maxCoachUpdates`. Preflight may recommend a cadence from workflow risk and dataflow. Runtime must not invoke the Coach more frequently than allowed, and the Thinker must not continue past a required coaching checkpoint without a directive.

The Coach must not silently perform the Thinker's task or rewrite accepted evidence. Its role is to select and constrain the next step. Every round records the Thinker's structured result, the Coach's directive and concise justification, validation outcomes, budgets consumed, and the resulting state transition.

Every LLM-backed run must record which mode and coaching cadence were used, the plan version when applicable, Coach and Thinker identities, Coach update triggers, permitted deviations, budgets, selected prompts and models, structured outputs and directives, validation results, and any replan event. The system records concise decision evidence and results; it does not require storage or disclosure of private hidden reasoning.

## Required separation

The semantic workflow owns:

- step identity and meaning;
- dependency and control-flow structure;
- input and output contracts;
- value bindings;
- loop and retry conditions;
- completion criteria.

The concrete operation child owns:

- implementation type;
- Python module and callable, Prolog module and predicate, or LLM prompt/model binding;
- executable parameters;
- dependency and environment requirements;
- tests, probes, and resource limits.

The frozen runtime record owns:

- the chosen concrete implementation for every step;
- resolved configuration and policy decisions;
- versions, hashes, timestamps, inputs, outputs, events, and evidence.

## Generation rule

A workflow-generation model should emit `implementationVariant` only when the user explicitly requests a concrete implementation or the supplied contract says that one implementation is mandatory. Otherwise it emits the semantic `operation` ID and leaves implementation resolution to preflight or runtime.

An implementation-generation model receives one unresolved semantic operation plus relevant whole-workflow context. It must create or select a concrete child without changing the workflow's semantic operation, ports, bindings, dependencies, or control flow.
