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
| Design | AtomSpaces | Hierarchical filesystem AtomSpace declarations and alternatives |
| Design | Prompts | Existing `PromptLibraryEditor` |
| Design | Models | Existing `LlmModelsEditor` |
| Runtime | Goal Runs | Durable Goal/Plan/Context-to-workflow pursuit records |
| Runtime | Workflow Runs | Persistent workflow-engine history |
| Runtime | Execs | Step attempts across persistent runs |
| Runtime | Events | Durable engine event history |
| Runtime | States | Persisted workflow artifacts/state values |
| Runtime | Contexts | Resolved AtomSpace bindings captured for Goal and Workflow Runs |
| Runtime | Logs | Persistent operation logs |
| System | Model Policy | Filesystem registry, policy, health, and eligibility UI |
| System | Benchmarks | Executable filesystem benchmark definitions/results |
| System | Settings | Existing workspace setup surface |

## Workspace Composition

`Default` is the editable minimal starter template copied by **Create A New Workspace**. `Shared` is an editable reusable library selected by default for new workspaces, but it is removable. A workspace may include any ordered combination of other workspace libraries and can choose whether each inclusion also brings its inherited layers.

## Implementation Constraints

- Use Operations and Data to Datatypes without rewriting their editors.
- Route only the active page launched by `App.tsx`; old pages are references, not entrypoints.
- Unimplemented destinations must show real filesystem/backend status or documentation, never fabricated records.
- Preserve workspace selection, the workflow stage rail, the right documentation/inspector pane, and all rich editor features.
- Add route-label and component-mapping regression tests.
