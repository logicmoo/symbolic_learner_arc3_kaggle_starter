# Runtime Persistence Architecture

[Back to repository README](../../../README.md)

## Design and Runtime Boundary

Goals, Plans, Contexts, workflows, operations, policies, and benchmarks are versionable filesystem specifications. Executions are append-oriented evidence stored in the workflow engine's SQLite database. This keeps hand-authored semantics inspectable while preserving history across server restarts.

## Goal Pursuit

A Goal Run resolves:

1. a root `goal` and preferred or requested child `goal`;
2. a compatible `planning_strategy` and child strategy;
3. an optional `context` containing AtomSpace bindings; and
4. the workflow named by the plan variant.

The engine stores a Goal Run that references the resulting workflow-run ID. The design resources remain unchanged. Retrieval joins the Goal Run with current durable workflow status.

The Goal Runs UI exposes explicit Goal, Plan, and Context variant selectors. Selecting a historical pursuit loads its frozen workflow version into the pipeline, highlights the waiting/running/failed step, and permits human-step input or cancellation without leaving the history view.

## Workflow Evidence

Each workflow run persists inputs, outputs, status, timestamps, step attempts, artifacts, events, operation logs, and nested-run relationships. The Runtime navigation reads complete history from `GET /api/engine/runs`, not only React session state:

- **Workflow Runs** shows run identity and status.
- **Execs** flattens persisted step attempts.
- **Events** shows ordered engine evidence.
- **States** displays persisted artifacts and values.
- **Logs** displays operation streams and messages.

Selecting any history record restores that run to the live inspector and pipeline context.
