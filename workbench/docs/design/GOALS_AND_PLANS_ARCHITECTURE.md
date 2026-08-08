# Goals, Planning Strategies, and Workflows

[Back to repository README](../../../README.md)

## Semantic model

A Goal describes a desired outcome. A Planning Strategy describes heuristics, constraints, decomposition rules, or planner configuration used to obtain an executable plan. A Workflow is that executable plan: an aggregation of planned operation, human-interaction, or nested-workflow steps.

Human-authored plans and PDDL-generated plans use the same Workflow resource. Their provenance differs, but their execution contract does not.

```text
Goal + AtomSpaces + Planning Strategy
                    |
          human / PDDL / LLM / rules
                    |
                 Workflow
                    |
                Workflow Run
```

Resource relationships are:

- `goal` → `goal_interpretation` or `goal_variant`
- `planning_strategy` → `planning_strategy_variant`
- legacy `plan` → `plan_variant` resources are accepted as read-compatible aliases
- a strategy variant may select or generate a `workflow`
- Goal Runs reference the selected Goal variant, Strategy variant, Context, Workflow, and Workflow Run

## PDDL-facing contract

Operations serve as action schemas; Workflow steps serve as grounded action occurrences; Workflows serve as plans; and Workflow Runs serve as execution traces. PDDL importers and planners should emit Workflows rather than a second `planned_workflow` artifact kind.

## Editor and runtime boundary

Goals and Planning Strategies retain hierarchical specifications, alternatives, preferred selection, tabs, comparison, raw source editing, filesystem save, and workspace inheritance. Runtime records preserve resolved IDs and frozen Workflow versions. Events, States, Execs, and Logs remain append-oriented execution evidence.
