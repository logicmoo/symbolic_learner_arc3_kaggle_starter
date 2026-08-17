[← Back to repository README](../../../README.md)

# Workflow Control Language

## Purpose

This language lets a constrained model generate executable workflows without generating arbitrary host-language code. The model composes a small catalog of semantic operations. Preflight validates the program, and the workflow engine interprets the frozen result.

The language is intentionally small. Named values, mutable memory, conditional branches, and bounded repetition provide general computation, while required bounds and typed operation contracts make generated programs inspectable and controllable.

## Machine state

An execution state contains:

- `programCounter`: current step ID;
- `values`: immutable step outputs addressed by producer and output port;
- `aliases`: current named-value bindings used by `$name` references;
- `memory`: explicitly mutable scoped `atomspace_cell` records;
- `frames`: workflow, operation-call, loop, and branch frames;
- `events`: append-only state-transition evidence;
- `budgets`: remaining steps, loop iterations, calls, time, tokens, and cost;
- `status`: ready, running, waiting, completed, failed, or cancelled.

Every transition records its source step, selected primitive or operation, resolved inputs, outputs, target step, budget delta, and validation result. Secret values are referenced by handles and are never copied into events.

## Value rules

Step outputs are immutable. Reusing a friendly output name changes an alias; it does not erase the earlier produced value. The runtime keeps both values and records the alias transition. `value.set` creates or updates an alias. Durable mutation occurs only through `memory.write`.

A `$name` binding resolves in this order: current operation frame, current loop iteration, workflow run aliases, workflow inputs. Ambiguous bindings fail preflight rather than selecting a writer by textual proximity.

## Primitive set

### `value.set`

Bind a supplied value to a named alias and return the prior and current value. It does not create durable memory.

### `value.compare`

Compare two supplied values using a declared operator and return a Boolean. Supported operators are `truthy`, `falsy`, `empty`, `not_empty`, `equals`, `not_equals`, `less_than`, `less_than_or_equal`, `greater_than`, and `greater_than_or_equal`. Invalid type/operator combinations fail explicitly.

### `memory.read`

Read one `atomspace_cell` from a declared scope and scope key. Missing-cell behavior must be `error`, `null`, or `default` and cannot be implicit.

### `memory.write`

Write one `atomspace_atom` into an `atomspace_cell` using `replace`, `append`, `merge`, `increment`, `min`, or `max`. It records the prior atom, new atom, writer, `evidenceLink`, and persistence decision. Writes must satisfy the memory model produced during preflight.

## Understanding memory read and write

Ordinary workflow values and workflow memory solve different problems.

A step output is an immutable historical fact. For example, an action step may produce `proposal=LEFT`, and an assessment step may produce `frame_changed=false`. Those exact outputs remain attached to those exact step executions. The runtime does not rewrite them when a later iteration produces a different proposal or assessment.

A named alias points to whichever immutable value is currently convenient to reference. Updating an alias changes the pointer while retaining the older produced values and their provenance.

An `atomspace_cell` is intentionally mutable state backed by the workbench's AtomSpace memory model. It lets later steps or later iterations remember and update information such as ineffective actions, accumulated evidence, games already played, learned rules, counters, or user preferences. Depending on its declared scope and retention policy, an AtomSpace cell may survive one step, one loop iteration, one game, one run, or multiple runs in a workspace.

`memory.write` changes a declared `atomspace_cell`. The caller must specify:

- `atomspace_scope`: lifetime and ownership category, such as game, run, or workspace;
- `atomspace_scope_key`: the particular game, run, user, or other owner;
- `atomspace_cell`: stable AtomSpace memory-cell name;
- `atomspace_atom`: information being written;
- `change_mode`: replace, append, merge, increment, min, or max;
- `evidenceLink`: the observation, assessment, event, or artifact that justifies the change.

For example, when ARC3 action `MOVE_LEFT` produces no visible change:

```text
memory.write(
  atomspace_scope = "game",
  atomspace_scope_key = "game-123",
  atomspace_cell = "ineffective_actions",
  atomspace_atom = "MOVE_LEFT",
  change_mode = "append",
  evidenceLink = "assessment-42"
)
```

The evidence reference prevents the system from retaining an unexplained conclusion. Inspectors can follow the memory entry back to the before/after observation that caused it.

`memory.read` retrieves a declared AtomSpace cell. The caller supplies `atomspace_scope`, `atomspace_scope_key`, the `atomspace_cell` name, and an explicit policy for a missing cell. It returns the stored value as `atomspace_atom`:

```text
memory.read(
  atomspace_scope = "game",
  atomspace_scope_key = "game-123",
  atomspace_cell = "ineffective_actions",
  missingPolicy = "default",
  default = []
)
```

The returned list can be passed to action selection so the next choice excludes `MOVE_LEFT`. If the `atomspace_cell` is absent, the declared default produces an empty list. Other callers may require `missingPolicy=error` when absence indicates an invalid workflow state, or `missingPolicy=null` when absence is a meaningful result.

Preflight uses the workflow's memory model to verify that the `atomspace_cell` exists, its `atomspace_scope` and datatype are correct, the selected `change_mode` is legal, and every reader can receive either a stored `atomspace_atom` or its declared missing-cell result. Runtime records the previous atom, new atom, writer, `evidenceLink`, and persistence outcome for every mutation.

Secrets and credentials are never copied into workflow memory. Memory may retain an authorized credential reference or handle, while the credential value remains in the protected system credential store.

### `control.if_cond.do_operation`

Evaluate a condition. When it matches, call one cataloged semantic operation with declared inputs and return its outputs. Otherwise return `called=false` and a typed skipped result. Concrete implementation selection occurs at runtime.

### `control.if_cond.jumpt_branch`

Evaluate a condition and choose either `targetStepId` or `elseStepId`. Both targets must exist. A backward target must enter a declared bounded loop region.

### `control.while`

Create a loop frame, evaluate the condition before each iteration, enter at `targetStepId` while it matches, and leave through `exitStepId` otherwise. `maxIterations` is mandatory. The frame declares retained, reset, accumulated, and exported values.

The current executable workflow encoding places a `while` object (or ordered
array of objects) on the step that controls the backward edge. After that step
produces its outputs, the engine resolves `condition` against the newest
artifact values. A matching condition resets the contiguous region from
`targetStepId` through the controller to `pending`; the scheduler then
reevaluates dependencies and executes that region again. A false condition
leaves the region through its normal downstream dependencies. Every backward
jump emits a durable `loop.iteration` event containing the loop index,
iteration number, bound, condition value, target, and reset step IDs.

Supported controller operators are `truthy`, `not_empty`, `equals`, and
`less_than`. `conditionPort` supplies the comparison value for `equals` and
`less_than`; it may itself be an artifact binding. `targetStepId` defaults to
the controller, which repeats only that step. Targets after the controller,
missing targets, and non-positive bounds fail validation. If the condition is
still true after `maxIterations` executions, the run fails explicitly instead
of silently leaving or continuing the loop.

Bindings may address nested data, for example `$assessment.frame_changed`,
`$game.game_id`, or `$state.history.0`. Namespace forms such as
`$workflow.input`, `$slots.output`, and `$steps.stepId.output` remain supported.

### `control.for_each`

Snapshot the input collection, create a loop frame, bind one item and index per iteration, and enter at `targetStepId`. `maxItems` is mandatory. Mutation of the source collection does not alter the snapshot unless an explicit live-collection mode is added later.

### `control.loop.continue`

Validate the named active loop frame, finalize the current iteration evidence, apply reset/accumulation rules, and return to its condition or next-item check.

### `control.loop.break`

Validate the named active loop frame, finalize iteration evidence, export declared loop values, remove the frame, and jump to its `exitStepId`.

### `control.return`

Validate declared workflow outputs, unwind the current operation or workflow frame, and return a typed result to its caller. Top-level return completes the run.

## Preflight requirements

Preflight must reject programs with missing targets, missing semantic operations, undeclared bindings, incompatible types, ambiguous aliases, reads before production, illegal memory scopes, unbounded backward edges, unreachable required outputs, calls without typed contracts, or loops whose exit cannot be reached within their declared budget.

Preflight may infer loop regions and reevaluation checkpoints, but the frozen executable must contain explicit targets, exits, conditions, bounds, retained/reset/exported values, and memory effects.

## Runtime safety

Bounds are semantic, not optional safeguards. Exceeding a bound produces a structured failure or declared fallback; it never silently continues. An overall run-step budget remains mandatory even when every individual loop is bounded.

Generated workflows cannot name filesystem paths, network endpoints, credentials, Python callables, Prolog predicates, models, or prompts unless those resources are present in the effective catalog and permitted by policy. Semantic operation selection and concrete implementation resolution remain separate.

## Completeness and constraints

Mutable memory plus comparison, conditional branching, and bounded loops can express arbitrary computations up to the supplied resource bounds. The workbench therefore provides a practically general control language while retaining termination limits for every individual run. Turing completeness describes the language model; a particular execution is always resource-bounded.
