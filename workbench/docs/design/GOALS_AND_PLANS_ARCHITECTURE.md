# Goals and Plans Architecture

[Back to repository README](../../../README.md)

## Semantic Model

A goal describes a desired outcome; an interpretation or variant expresses a concrete way to evaluate or pursue it. A plan describes an ordered or conditional strategy; plan variants provide interchangeable strategies for the same plan contract. Specifications and variants are separate filesystem resources.

Expected resource relationships:

- `goal` → `goal_interpretation` or `goal_variant`
- `plan` → `plan_variant`
- goal runs reference the selected goal interpretation, plan variant, context, and resulting workflow runs

## Editor Contract

Goals and Plans should use the universal hierarchical editor behavior: specification parents, child alternatives, preferred selection, persistent tabs, dirty state, comparison, rich forms, raw JSON, filesystem save, inheritance, and documentation. Their implementation must use real resource loaders and must not begin with hard-coded sample arrays.

## Runtime Boundary

Design-time goals and plans are immutable inputs to a particular run version. Runtime records should preserve the resolved goal, selected strategy, context bindings, decisions, workflow/operation executions, events, state snapshots, and logs. Goal Runs is therefore a runtime history view, not another editor for goal definitions.

## Durable Goal Runs

`POST /api/goal-runs` resolves the preferred (or requested) goal and plan variants, verifies that the plan pursues the goal, resolves an optional Context, and starts the plan variant's filesystem workflow. The resulting SQLite record links all selected design resources to the durable workflow run. `GET /api/goal-runs` reloads that history after restart; the Runtime views then expose its executions, events, state artifacts, and logs.

Goal, Plan, and Context resources remain editable specifications. A Goal Run records the resolved IDs and execution version rather than copying runtime state back into those design files.
