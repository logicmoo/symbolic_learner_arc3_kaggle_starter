# Workbench Navigation V2

[Back to repository README](../../../README.md)

## Purpose

Navigation V2 organizes the active filesystem-backed workbench by purpose without replacing existing editors. `workbench/frontend/src/App.tsx` remains the authority for the active page.

## Navigation Contract

| Group | Item | Backing surface |
| --- | --- | --- |
| Workspace | Overview | Workspace purpose, inheritance, and resource totals |
| Workspace | Goals | `GoalPlanLibraryEditor` with goal alternatives |
| Workspace | Planning | Planning strategies used by human, PDDL, LLM, or rule planners |
| Workspace | Workflows | Executable plans in the existing workflow canvas/editor |
| Capabilities | Operations | Existing `OperationLibraryEditor` |
| Capabilities | Source Code | Prompts plus Prolog, MeTTa, and Python implementation source |
| Capabilities | Systems | Shell, runtime, MCP, and implementation-provider configuration |
| Capabilities | Models | Existing backend/model/model-preset editor |
| Capabilities | Datatypes | Existing `DataCatalogPanel` |
| Capabilities | Policies | Filesystem policy specifications |
| Knowledge | Data | Workspace-held images, datasets, and other values |
| Knowledge | AtomSpaces | Hierarchical AtomSpace declarations and alternatives |
| Knowledge | Artifacts | Produced and imported typed artifacts |
| Runtime | Goal Runs | Durable Goal/Plan/Context-to-workflow pursuit records |
| Runtime | Executions | Workflow runs and operation attempts |
| Runtime | Events | Durable engine event history |
| Runtime | States | Persisted workflow artifacts/state values |
| Runtime | Logs | Persistent operation logs |
| System | Docs | Repository documentation and exposed filesystem files |
| System | Model Policy | Filesystem registry, policy, health, and eligibility UI |
| System | Benchmarks | Executable filesystem benchmark definitions/results |
| System | Processes | Workbench-managed service and process monitor |
| System | Settings | Existing workspace setup surface |

## System model

The workbench is a blackboard where a human and an AI jointly construct and control a tool-using workflow. Goals state desired outcomes. Planning strategies guide a human, PDDL planner, LLM, or rules engine. The resulting Workflow is the executable plan and its steps invoke Operations.

Operations describe what can be done. Their implementations describe how it is done by binding source code to a configured system: an LLM and Prompt, SWI-Prolog source, MeTTa, Python, a shell, or an MCP service. Models are therefore capability configuration, while Prompts are maintained alongside other implementation source.

Data, AtomSpaces, and Artifacts are shared knowledge rather than design instructions or runtime history. Runtime pages show what actually happened: executions, events, states, and logs.

## Workspace Composition

`Default` is the editable minimal starter template copied by **Create A New Workspace**. `Shared` is an editable reusable library selected by default for new workspaces, but it is removable. A workspace may include any ordered combination of other workspace libraries and can choose whether each inclusion also brings its inherited layers.

## Implementation Constraints

- Use Operations and Data to Datatypes without rewriting their editors.
- Route only the active page launched by `App.tsx`; old pages are references, not entrypoints.
- Unimplemented destinations must show real filesystem/backend status or documentation, never fabricated records.
- Preserve workspace selection, the workflow stage rail, the right documentation/inspector pane, and all rich editor features.
- Add route-label and component-mapping regression tests.
