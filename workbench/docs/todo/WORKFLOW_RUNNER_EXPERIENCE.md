# TODO: Restore the Rich Workflow Runner Experience

[Back to repository README](../../../README.md)

The supplied workflow-runner mockup is the visual acceptance reference for a future rich runtime surface. It is not executable data and must not replace the current durable Workflow Runs table until every panel is backed by real engine, workspace, or artifact resources.

## Implementation Status

The active Workflow Runs page now keeps the durable history table and adds:

- topology over the frozen workflow version, with dependency edges and runtime status;
- chronology over every persisted event, including repeated stages;
- selection-linked stage narrative, artifacts, logs, hashes, and provenance;
- persisted stdout/stderr logs for subprocess-backed operations;
- real pause, resume, advance, replay, and cancel commands;
- source/render comparison for persisted numeric grids and image data URLs; and
- human-input forms derived from the frozen workflow step contract.

Automated acceptance captures are available through `scripts/capture_workflow_runner_visuals.ps1`. The script opens deep-linked, filesystem-backed Workflow Runs topology and chronology views and writes 1920×1080 images under `workbench/docs/todo/assets/actual/`; it never injects mock run data. Hypothesis, transition-evidence, and suggested-experiment artifacts have explicit runtime contracts and render only when a run actually persists matching typed artifacts. Persisted safe form drafts, image/grid input widgets, independently resizable runner panels, and direct navigation from stages, invocation traces, and artifact provenance to their executable Operation, Model, Datatype, or Representation resources are also active. Human submissions emit durable `human_input.received` events that identify the produced artifacts while listing sensitive fields only as redacted field names.

## Preserve from the Reference

- A persistent run pipeline showing completed, active, and pending stages.
- A central stage narrative with topology and chronology views.
- Live hypotheses, confidence, suggested experiments, and run events.
- A resizable inspector comparing source and rendered artifacts.
- Direct links from selected objects to executable representations and provenance.
- Run health, pause/stop/advance controls, and durable event counts.

## Spline Views

The spline is a functional projection of the run and must retain two switchable interpretations:

- **Topology** shows workflow structure. Nodes represent operations or nested workflow stages; solid curves show declared dependencies and branches, while visually distinct paths may show selected, inferred, or feedback relationships. Parallel branches may share horizontal space because their position describes structure rather than execution time.
- **Chronology** shows what actually happened. Nodes are ordered left to right from persisted events, including repeated stages, retries, human-input boundaries, and nested executions. The same operation may appear more than once. Curves connect causal or parent/child execution relationships without reordering the event sequence into a cleaner topology.

Both views must preserve selection: choosing a spline node selects the corresponding stage, execution, events, artifacts, and inspector evidence. Switching views must not change the run or discard that selection. Large splines require horizontal scrolling, readable labels, status coloring, and accessible node descriptions.

## Human Input Boundaries

A workflow step that requires user input must visibly suspend the run at that stage and render a form derived from the operation's declared input datatypes. Grid, image, choice, text, and structured-object inputs should use suitable editors rather than a single hard-coded control. The form must identify the waiting operation, expected values, current context, and the action that resumes execution.

Submitting input creates a durable `human_input.received` event linked to the run, step, input artifact, and user-visible timestamp. The runner then resumes the same suspended execution—never a new mock run—and updates the spline, stage status, event stream, artifacts, and inspector together. Refreshing or restarting while paused must restore the waiting form and any safely persisted draft values. Submitted values remain inspectable through provenance, with secrets redacted according to policy.

## Required Backend Contracts

The runner must load workflow definitions, run steps, events, logs, artifacts, states, and provenance from the existing filesystem and workflow-engine APIs. Image comparisons and detected objects need explicit artifact datatypes rather than UI-only structures. Hypotheses and confidence values must be stored as execution evidence. No values visible in the reference may be hard-coded into the active application.

## Original Implementation Order

1. Define artifact and provenance records needed by the inspector.
2. Add separate topology and chronology projections over workflow definitions and persisted run events.
3. Build the stage narrative from operation outputs and evidence.
4. Add source/render comparison for compatible image artifacts.
5. Restore runner controls using real workflow-engine commands.
6. Add datatype-driven human-input forms and durable resume behavior.
7. Add restart, save/reload, scrolling, and visual-regression coverage.

## Completion Criteria

The rich runner may replace this reference only when it survives an application restart, reloads the same run from durable storage, exposes no mock arrays, supports large pipelines with both-axis scrolling, and preserves the current Workflow Runs history and selection behavior.
