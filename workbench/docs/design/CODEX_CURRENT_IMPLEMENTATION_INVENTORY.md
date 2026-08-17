# Codex Current Implementation Inventory

[Back to repository README](../../../README.md)

## Scope and Active Entrypoint

This living inventory records the active Navigation V2 implementation. `workbench/frontend/src/main.tsx` renders `App`; `workbench/frontend/src/App.tsx` imports and returns only `FilesystemWorkbenchPage`. Therefore `workbench/frontend/src/pages/FilesystemWorkbenchPage.tsx` is the active application. No other page under `src/pages/` is reachable through the current entrypoint.

The backend is FastAPI, launched from `workbench/server/app.py`. The active page uses `/api/workspaces/{id}/snapshot` for filesystem state and `/api/engine/*` for workflow execution.

## Navigation Mapping

| Navigation V2 item | Current backing component/data | Status |
| --- | --- | --- |
| Overview | `WorkspaceOverview` and workspace inclusion/configuration APIs | Real, reuse |
| Goals | `GoalPlanLibraryEditor`, `/api/workspaces/{id}/goals`, shared same-kind alternatives | Real, reuse |
| Planning | `GoalPlanLibraryEditor`, `/api/workspaces/{id}/plans`, shared planning strategies | Real, reuse |
| Workflows | Active canvas and raw workflow editor in `FilesystemWorkbenchPage` | Real, reuse |
| Operations | `OperationLibraryEditor` and `OperationPlayground` | Real, relabel Operations |
| Source Code | `PromptLibraryEditor` plus language-filtered `OperationLibraryEditor` tabs | Real, reuse |
| Systems | `LlmModelsEditor` in systems catalog mode | Real, reuse |
| Datatypes | `DataCatalogPanel` | Real, relabel Data |
| Models | `LlmModelsEditor` | Real, reuse |
| Policies | `PolicyLibraryEditor` | Real, reuse |
| Data | `KnowledgeDataExplorer` over real workspace files | Real |
| AtomSpaces | `GoalPlanLibraryEditor`, AtomSpace API, shared alternatives | Real, reuse |
| Artifacts | Persisted/imported workflow artifacts | Real |
| Goal Runs | `/api/goal-runs` plus `RuntimeHistoryView` | Durable and real |
| Executions | `/api/engine/runs`, persisted step attempts, and playground invocations | Durable and real |
| Events | Ordered events across durable engine runs | Real |
| States | Persisted workflow artifacts and payloads | Real |
| Logs | Persisted operation streams across runs | Real |
| Model Policy | Filesystem policy/registry/health API and editor | Real |
| Benchmarks | Executable policies, jobs, and persisted results | Real |
| Processes | `WorkspaceSettingsPanel` managed-service/process mode | Real |
| Settings | `WorkspaceSettingsPanel` system/workspace setup | Real, reuse |

## Active Editors and Baseline Features

`OperationLibraryEditor`, `DataCatalogPanel`, `PromptLibraryEditor`, and `LlmModelsEditor` use `HierarchyResourceEditor`, a compatibility export of `UniversalArtifactEditor`. The shared shell provides hierarchy chrome, persistent closeable tabs, dirty markers, split comparison, common inspector space, variant controls, and bottom docks.

The Operations editor additionally has abstract operation/implementation hierarchy, default implementation selection, Python, SWI-Prolog, MeTTa, and model/preset dispatch panels, prompt composition, raw JSON, filesystem save, and the typed `OperationPlayground`. Datatypes provides representation selection, conversions, and usage. Source Code provides prompt alternatives plus Prolog, MeTTa, and Python implementation views. Models provides backend/model/preset inheritance, resolved settings, rich configuration, and raw JSON. The active right pane loads real shared Markdown through `HelpDocumentTabs` for these families.

## Real, Obsolete, and Mock Pages

- **Active and real:** `FilesystemWorkbenchPage.tsx`; its workspace lists, snapshots, workflow definitions, capabilities, editors, artifacts, and events come from backend APIs.
- **Inactive but mostly filesystem/backend-backed predecessors:** `PolishedFilesystemWorkbenchPage.tsx`, `PolishedFilesystemWorkbenchPageV2.tsx`, `RealWorkspaceDesktopPage.tsx`, `WorkspaceBackedWorkbenchPage.tsx`, `WorkspaceWorkbenchPage.tsx`, `BackendWorkbenchPage.tsx`, `RealWorkbenchPage.tsx`, and `UnmockedWorkflowEnginePage.tsx`. They may be consulted for behavior, but are not routing targets.
- **Inactive mock/reference pages:** `WorkflowEnginePage.tsx` declares a local sample workflow. `WorkbenchPage.tsx` includes hard-coded validation results and presentation/demo data and talks to deprecated compatibility endpoints. Neither may supply active Navigation V2 data.

Some inactive pages expose views not currently promoted to dedicated active navigation items, including chronology-oriented run presentations and older command/configuration surfaces. Reuse only behavior that can be wired to current real APIs; do not copy their embedded sample records.

## Backend Routes Already Available

Workspace and file APIs:

- `GET /api/workspaces`, `GET /api/workspaces/{id}`
- `GET /api/workspaces/{id}/snapshot`
- `GET|PUT /api/workspaces/{id}/file`
- Workspace operation, datatype, representation, backend, model, and prompt collection routes
- Prompt hierarchy, implementation, and resolution routes
- Datatype resolution, representation graph, inventory, and conversion-planning routes
- `POST /api/workspaces/{id}/operations/{operation_id}/invoke`

Workflow-engine and pursuit APIs:

- capabilities and implementations
- workflow list/create/get/validate
- run create/list/get, commands, human step input, events, and logs
- Goal Run create/list/get with resolved Goal, Plan, Context, and workflow linkage

The app also exposes health, analysis, SQLite-backed legacy run/event/operation APIs, artifact lookup, and session workflow/reset routes. `/api/workflows` is explicitly deprecated for the retired mock client; Navigation V2 should use workspace snapshots and engine routes.

## Filesystem Resource Kinds

Canonical first-class resources include `workflow`, `goal`, `planning_strategy`, `atomspace`, `operation`, `semantic_datatype`, `representation_datatype`, `concrete_datatype`, `prompt`, `prompt_profile`, `backend`, `model`, `system`, model-policy resources, and benchmark resources. Same-family variants normally keep the same kind and become implicit alternatives through `parents`. Loaders still accept legacy variant kinds and directories such as `operation_implementation`, `prompt_implementation`, `goal_variant`, `plan_variant`, `context_variant`, and `profile` so older workspaces remain readable; new saves use the lifecycle-first canonical directories.

Shared inheritance plus workspace override resolution exists for Goals, Planning Strategies, AtomSpaces, Operations, Datatypes, Source Code, Systems, Models/Presets, and Policies. Goal Runs and execution evidence are deliberately SQLite runtime records; artifact records serve as durable workflow state snapshots.

## Navigation V2 Implementation Surface

The active shell and grouped navigation live in `FilesystemWorkbenchPage.tsx`; `App.tsx` remains the unchanged entrypoint. Purpose-specific wrappers such as `SourceCodeEditor`, `KnowledgeDataExplorer`, and the systems catalog mode compose existing rich editors rather than replacing them. `tests/test_navigation_v2_ui.py` protects labels, deep links, and component mappings, while the existing universal-editor and playground suites protect editor behavior.

## Current Rich Operations Regression Checklist

Before and after Navigation V2:

- [ ] `App.tsx` still launches the page containing `OperationLibraryEditor`.
- [ ] Operations opens the existing `OperationLibraryEditor`, not a replacement.
- [ ] Abstract operations remain parents and implementations remain children.
- [ ] Default implementation selection edits the abstract operation document.
- [ ] Python, SWI-Prolog, MeTTa, model/preset dispatch, and prompt-composition panels remain available.
- [ ] Persistent tabs open, activate, show dirty state, close, and retain unsaved drafts.
- [ ] Split comparison works and returns to single-pane mode.
- [ ] Raw JSON edits and rich controls update the intended document.
- [ ] Saving inherited resources creates/updates the correct workspace override; shared resources remain protected.
- [ ] Save followed by snapshot reload preserves changes.
- [ ] `OperationPlayground` resolves a real implementation, accepts typed input, switches variants, runs, and shows outputs/prompts/timing.
- [ ] Right-side documentation remains visible and filesystem-backed.
- [ ] Horizontal and vertical scrolling expose all editor content.
- [ ] Existing universal-editor and operation-playground tests pass, with no historical commit identifier used as the baseline.
- [ ] Frontend build succeeds and the running application works after restart.

## Review Gate

Navigation V2 is active. Future changes must preserve the current rich editors, filesystem-backed data, grouped purpose model, and compatibility reads for legacy workspaces.
