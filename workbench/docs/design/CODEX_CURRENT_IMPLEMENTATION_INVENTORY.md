# Codex Current Implementation Inventory

[Back to repository README](../../../README.md)

## Scope and Active Entrypoint

This living inventory records the active Navigation V2 implementation. `workbench/frontend/src/main.tsx` renders `App`; `workbench/frontend/src/App.tsx` imports and returns only `FilesystemWorkbenchPage`. Therefore `workbench/frontend/src/pages/FilesystemWorkbenchPage.tsx` is the active application. No other page under `src/pages/` is reachable through the current entrypoint.

The backend is FastAPI, launched from `workbench/server/app.py`. The active page uses `/api/workspaces/{id}/snapshot` for filesystem state and `/api/engine/*` for workflow execution.

## Navigation Mapping

| Navigation V2 item | Current backing component/data | Status |
| --- | --- | --- |
| Goals | `GoalPlanLibraryEditor`, `/api/workspaces/{id}/goals`, shared goal variants | Real, reuse |
| Plans | `GoalPlanLibraryEditor`, `/api/workspaces/{id}/plans`, shared plan variants | Real, reuse |
| Workflows | Active canvas and raw workflow editor in `FilesystemWorkbenchPage` | Real, reuse |
| Operations | `OperationLibraryEditor` and `OperationPlayground` | Real, relabel Operations |
| Datatypes | `DataCatalogPanel` | Real, relabel Data |
| Prompts | `PromptLibraryEditor` | Real, reuse |
| Models | `LlmModelsEditor` | Real, reuse |
| Goal Runs | `/api/goal-runs` plus `RuntimeHistoryView` | Durable and real |
| Workflow Runs | `/api/engine/runs` persistent history | Durable and real |
| Execs | Persisted step attempts plus operation playground invocations | Real |
| Events | Ordered events across durable engine runs | Real |
| States | Persisted workflow artifacts and payloads | Real |
| Logs | Persisted operation streams across runs | Real |
| Model Policy | Filesystem policy/registry/health API and editor | Real |
| Benchmarks | Executable policies, jobs, and persisted results | Real |
| Contexts | `GoalPlanLibraryEditor`, context API, shared context variants | Real, reuse |
| Settings | Active workspace Setup view in `FilesystemWorkbenchPage` | Real, reuse |

## Active Editors and Baseline Features

`OperationLibraryEditor`, `DataCatalogPanel`, `PromptLibraryEditor`, and `LlmModelsEditor` use `HierarchyResourceEditor`, a compatibility export of `UniversalArtifactEditor`. The shared shell provides hierarchy chrome, persistent closeable tabs, dirty markers, split comparison, common inspector space, variant controls, and bottom docks.

The Operations editor additionally has abstract operation/implementation hierarchy, default implementation selection, Python, SWI-Prolog, MeTTa, and model/profile dispatch panels, prompt composition, raw JSON, filesystem save, and the typed `OperationPlayground`. Datatypes provides representation selection, conversions, and usage. Prompts provides preferred implementations. Models provides backend/model/profile inheritance, resolved settings, rich configuration, and raw JSON. The active right pane loads real shared Markdown through `HelpDocumentTabs` for these families.

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

Existing first-class loaders cover `workflow`, `goal`, `goal_variant`, `plan`, `plan_variant`, `context`, `context_variant`, `operation`, `operation_implementation`, `semantic_datatype`, `representation_datatype`, `concrete_datatype`, `prompt`, `prompt_implementation`, `backend`, `model`, `profile`, model-policy resources, and benchmark resources. Workspaces also contain catalog/config/Markdown files that appear in the editable-file inventory but are not all first-class semantic loaders.

Shared inheritance plus workspace override resolution exists for Goals, Plans, Contexts, Operations, Datatypes, Prompts, backends, models, profiles, and policies. Goal Runs and workflow evidence are deliberately SQLite runtime records; artifact records serve as durable workflow state snapshots. AtomSpace semantics are represented by the datatype and Context resources rather than a separate mock catalog.

## Exact Navigation V2 Change Surface

Operation 2 should remain narrowly scoped to:

1. `workbench/frontend/src/pages/FilesystemWorkbenchPage.tsx` — replace the flat `View`/`nav` contract with grouped Design, Runtime, and System navigation; map existing components without editing their internals; add real pending/resource views.
2. `workbench/frontend/src/styles/workbench.css` and, only if required by the active shell, `workspace_backed.css` — style grouped navigation and overflow while preserving current editor CSS.
3. A focused Python source-regression test under `tests/` — assert all Navigation V2 labels and their component/view mappings.
4. `tests/test_universal_artifact_editor_ui.py` and `workbench/frontend/src/components/UniversalArtifactEditor.tsx` — remove the stale historical commit-name assertion/constant and express the baseline as current behavior. This is regression-test semantics, not an editor redesign.

`App.tsx` needs no change unless the active entrypoint itself changes; Navigation V2 should not change it. No backend file is required merely to establish the shell because the active snapshot and engine APIs can support real status/TODO views.

## Current Rich Operations Regression Checklist

Before and after Navigation V2:

- [ ] `App.tsx` still launches the page containing `OperationLibraryEditor`.
- [ ] Operations opens the existing `OperationLibraryEditor`, not a replacement.
- [ ] Abstract operations remain parents and implementations remain children.
- [ ] Default implementation selection edits the abstract operation document.
- [ ] Python, SWI-Prolog, MeTTa, model/profile dispatch, and prompt-composition panels remain available.
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

Do not implement Navigation V2 until this inventory is reviewed. The next change must alter the active shell only, preserve all current rich editors, and avoid normalization, broad renames, or unrelated cleanup.
