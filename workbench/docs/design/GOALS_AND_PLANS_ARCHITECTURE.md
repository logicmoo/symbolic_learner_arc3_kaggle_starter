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

- `goal` → specialized `goal` resources linked through `implements`
- `planning_strategy` → specialized `planning_strategy` resources linked through `implements`
- legacy plan and explicit variant kinds are accepted only as read-compatible aliases
- a strategy variant may select or generate a `workflow`
- Goal Runs reference the selected Goal interpretation, Planning Strategy alternative, resolved runtime Context, Workflow, and Workflow Run

## PDDL-facing contract

Operations serve as action schemas; Workflow steps serve as grounded action occurrences; Workflows serve as plans; and Workflow Runs serve as execution traces. PDDL importers and planners should emit Workflows rather than a second `planned_workflow` artifact kind.

Workflow Studio records a `planProvenance` map without changing the executable kind. Its `origin` distinguishes `human`, `pddl`, `llm`, `rules`, and generic `imported` generation. For PDDL output, `planner`, `domain`, `problem`, and the original grounded `sourcePlan` remain beside the normalized Workflow steps. This lets a PDDL tool round-trip its source vocabulary while the engine continues to execute the common Workflow representation.

`POST /workbench/engine/workflows/import-pddl-plan` converts conventional grounded planner output such as `0: (move robot room-a room-b) [1]` into an unsaved Workflow. Untimed actions become sequential `workflow_step` resources. In temporal output, actions with the same start time become parallel siblings and depend on the preceding start-time group. Each step's `operation` is the normalized PDDL action name, or the corresponding value supplied in `actionMap`. Positional objects remain in `parameters.pddlArguments`; the mapped Operation is responsible for binding those objects to its named input ports. The endpoint never silently saves or runs the result.

## Editor and runtime boundary

Goals and Planning Strategies retain hierarchical specifications, alternatives, preferred selection, tabs, comparison, raw source editing, filesystem save, and workspace inheritance. Runtime records preserve resolved IDs and frozen Workflow versions. Executions, Events, States, and Logs remain append-oriented execution evidence.
