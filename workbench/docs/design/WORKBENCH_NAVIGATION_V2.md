# Workbench Navigation V2

[Back to repository README](../../../README.md)

## Purpose

Navigation V2 organizes the active filesystem-backed workbench by lifecycle without replacing existing editors. `workbench/frontend/src/App.tsx` remains the authority for the active page.

## Navigation Contract

| Group | Item | Backing surface |
| --- | --- | --- |
| Design | Goals | `GoalPlanLibraryEditor` with goal variants |
| Design | Plans | `GoalPlanLibraryEditor` with plan variants |
| Design | Workflows | Existing workflow canvas and source editor |
| Design | Operations | Existing `OperationLibraryEditor` |
| Design | Datatypes | Existing `DataCatalogPanel` |
| Design | Prompts | Existing `PromptLibraryEditor` |
| Design | Models | Existing `LlmModelsEditor` |
| Runtime | Goal Runs | Future goal-pursuit history |
| Runtime | Workflow Runs | Existing workflow-engine run state |
| Runtime | Execs | Operation invocations and playground executions |
| Runtime | Events | Existing durable engine events/evidence |
| Runtime | States | Persisted workflow/world-state snapshots |
| Runtime | Logs | Existing workflow-engine logs |
| System | Model Policy | TODO-backed view until a real API exists |
| System | Benchmarks | Filesystem benchmark definitions/results |
| System | Contexts | Runtime context and knowledge bindings |
| System | Settings | Existing workspace setup surface |

## Implementation Constraints

- Use Operations and Data to Datatypes without rewriting their editors.
- Route only the active page launched by `App.tsx`; old pages are references, not entrypoints.
- Unimplemented destinations must show real filesystem/backend status or documentation, never fabricated records.
- Preserve workspace selection, the workflow stage rail, the right documentation/inspector pane, and all rich editor features.
- Add route-label and component-mapping regression tests.
