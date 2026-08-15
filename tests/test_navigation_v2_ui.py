from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ACTIVE_PAGE = ROOT / "workbench" / "frontend" / "src" / "pages" / "FilesystemWorkbenchPage.tsx"
APP = ROOT / "workbench" / "frontend" / "src" / "App.tsx"


def test_app_launches_filesystem_workbench_page() -> None:
    source = APP.read_text(encoding="utf-8")
    assert 'import { FilesystemWorkbenchPage } from "./pages/FilesystemWorkbenchPage"' in source
    assert "return <FilesystemWorkbenchPage />" in source


def test_removed_workflow_v2_route_redirects_to_the_legacy_workflow_page() -> None:
    source = ACTIVE_PAGE.read_text(encoding="utf-8")
    assert 'label: "Workflows (Legacy)"' in source
    assert 'label: "Workflows (New)"' not in source
    assert 'return "workflowV2"' not in source
    assert 'return "canvas"' in source
    assert "WorkflowWorkbenchV2" not in source
    assert not (ROOT / "workbench/frontend/src/components/WorkflowWorkbenchV2.tsx").exists()
    assert not (ROOT / "workbench/frontend/src/styles/workflow_v2.css").exists()


def test_navigation_v2_has_required_groups_and_labels() -> None:
    source = ACTIVE_PAGE.read_text(encoding="utf-8")
    compact = "".join(source.split())
    for group in ("WORKSPACE", "CAPABILITIES", "KNOWLEDGE", "RUNTIME", "SYSTEM"):
        assert f'group: "{group}"' in source
    for label in (
        "Goals",
        "Overview",
        "Planning",
        "Workflows (Legacy)",
        "Operations",
        "Source Code",
        "Systems",
        "Datatypes",
        "Models",
        "Policies",
        "Data",
        "Artifacts",
        "Goal Runs",
        "Executions",
        "Events",
        "States",
        "Logs",
        "Model Policy",
        "Benchmarks",
        "AtomSpaces",
        "Processes",
        "Settings",
    ):
        assert f'label: "{label}"' in source
    assert "page-breadcrumb-trail" in source
    assert "Visited workbench pages" in source
    assert "returnToBreadcrumb" in source
    assert "setViewTrail" in source
    assert "viewTrailIndex" in source
    assert "breadcrumbNavigation" in source
    assert "current.slice(0,viewTrailIndex+1)" in source
    assert 'window.addEventListener("workbench:navigation"' in source
    assert "BreadcrumbEntry" in source


def test_navigation_views_are_deep_linkable_for_visual_acceptance() -> None:
    source = ACTIVE_PAGE.read_text(encoding="utf-8")
    assert 'new URLSearchParams(window.location.search)' in source
    assert 'url.searchParams.set("view",next)' in source
    assert 'window.addEventListener("popstate",restoreView)' in source
    assert 'const restoredView=viewFromLocation()' in source
    assert 'setViewState(restoredView||"canvas")' in source


def test_navigation_accepts_menu_as_a_deep_link_alias() -> None:
    source = ACTIVE_PAGE.read_text(encoding="utf-8")
    assert 'parameters.get("view")||parameters.get("menu")' in source
    assert 'WORKBENCH_VIEWS.has(value as View)' in source
    assert 'if(view!=="overview")return' in source
    assert '["run","goalRun","runStep","runEvent","runtimeRecord",...' in source
    assert 'url.searchParams.get("menu")==="overview"?["view"]' in source


def test_overview_and_system_settings_have_distinct_responsibilities() -> None:
    page = ACTIVE_PAGE.read_text(encoding="utf-8")
    overview = (ROOT / "workbench/frontend/src/components/WorkspaceOverview.tsx").read_text(encoding="utf-8")
    settings = (ROOT / "workbench/frontend/src/components/WorkspaceSettingsPanel.tsx").read_text(encoding="utf-8")
    assert 'local · {counts.inherited' in overview
    assert "INHERITED WORKSPACES" in overview
    assert 'mode="workspace"' in page
    assert "SYSTEM-WIDE SETTINGS" in settings
    assert "WORKSPACE REGISTRY" in settings
    assert "RUN_WORKBENCH STARTUP" in settings
    assert 'method:"DELETE"' in settings


def test_right_inspector_is_documentation_on_every_page() -> None:
    source = ACTIVE_PAGE.read_text(encoding="utf-8")
    relationship = source.split("const relationshipView=", 1)[1].split(";", 1)[0]
    assert "artifactFocused||!artifactFocused" in relationship
    assert 'relationshipView?"DOCUMENTATION":"LIVE INSPECTOR"' in source


def test_artifact_editors_keep_the_resizable_resource_and_documentation_shell() -> None:
    source = ACTIVE_PAGE.read_text(encoding="utf-8")
    styles = (ROOT / "workbench" / "frontend" / "src" / "styles" / "workbench.css").read_text(encoding="utf-8")
    assert 'relationshipView?"artifact-focused":""' in source
    assert 'workbench.resourceBrowserWidth' in source
    assert 'aria-label="Resize Resource Browser"' in source
    assert 'aria-label="Resize Documentation"' in source
    assert 'var(--resource-browser-width,250px)' in styles


def test_workflow_editor_keeps_the_resource_tree_visible() -> None:
    source = ACTIVE_PAGE.read_text(encoding="utf-8")
    styles = (ROOT / "workbench" / "frontend" / "src" / "styles" / "workbench.css").read_text(encoding="utf-8")
    relationship = source.split("const relationshipView=", 1)[1].split(";", 1)[0]
    artifact_focused = source.split("const artifactFocused=", 1)[1].split(";", 1)[0]
    assert "workflowCombinedView" in relationship
    assert 'view==="canvas"||view==="states"' in source
    assert 'view==="editor"' in relationship
    assert 'view==="canvas"' not in artifact_focused
    assert 'view==="editor"' not in artifact_focused
    assert '.workspace.artifact-focused:has(.canvas-view)>.stages-panel' in styles
    assert '.workspace.artifact-focused:has(.editor-surface)>.stages-panel{display:flex}' in styles


def test_workflow_designer_shows_filesystem_documentation_in_right_panel() -> None:
    page = ACTIVE_PAGE.read_text(encoding="utf-8")
    help_tabs = (ROOT / "workbench" / "frontend" / "src" / "components" / "HelpDocumentTabs.tsx").read_text(encoding="utf-8")
    playground = (ROOT / "workbench" / "frontend" / "src" / "components" / "OperationPlayground.tsx").read_text(encoding="utf-8")
    controls = (ROOT / "workbench" / "frontend" / "src" / "components" / "UniversalExecutionControls.tsx").read_text(encoding="utf-8")
    playground_styles = (ROOT / "workbench" / "frontend" / "src" / "styles" / "operation_playground.css").read_text(encoding="utf-8")
    workflow_docs = ROOT / "workbench" / "workspaces" / "shared_library_system" / "docs" / "workflows.md"

    assert "workflowCombinedView" in page.split("const relationshipView=", 1)[1].split(";", 1)[0]
    assert '{id:"workflows",label:"Workflows",path:"docs/workflows.md"}' in help_tabs
    assert 'pageView===null||pageView==="canvas"' in help_tabs
    assert workflow_docs.is_file()
    docs = workflow_docs.read_text(encoding="utf-8")
    assert "## Populate Inputs" in docs
    assert "No inputs to populate" in docs
    assert "DELAYED TASK SPECIFICATION" not in playground
    assert "operation-task-contract" not in playground_styles
    assert "flex-wrap:nowrap" in playground_styles
    assert "No inputs to populate" in controls


def test_navigation_reuses_current_rich_editors() -> None:
    source = ACTIVE_PAGE.read_text(encoding="utf-8")
    compact = "".join(source.split())
    expected = {
        "Goals": ('view:"goals"', 'view==="goals"&&<GoalPlanLibraryEditor workspaceId={workspace.id} family="goal"'),
        "Planning": ('view:"plans"', 'view==="plans"&&<GoalPlanLibraryEditor workspaceId={workspace.id} family="plan"'),
        "AtomSpaces": ('view:"contexts"', 'view==="contexts"&&<GoalPlanLibraryEditor workspaceId={workspace.id} family="context"'),
        "Operations": ('view:"operations"', 'view==="operations"&&<OperationLibraryEditor'),
        "Datatypes": ('view:"data"', 'view==="data"&&<DataCatalogPanel'),
        "Source Code": ('view:"sourceCode"', 'view==="sourceCode"&&<SourceCodeEditor'),
        "Systems": ('view:"systems"', 'catalogMode="systems"'),
        "Models": ('view:"llms"', 'view==="llms"&&<LlmModelsEditor'),
        "Workflows (Legacy)": ('view:"canvas"', 'workflowCombinedView&&<section className="canvas-view"', 'view==="editor"&&<section className="editor-surface"'),
        "Settings": ('view:"setup"', 'view==="setup"&&<WorkspaceSettingsPanel'),
    }
    for label, tokens in expected.items():
        assert f'label: "{label}"' in source
        for token in tokens:
            assert token.replace(" ", "") in compact


def test_workflow_runs_are_combined_with_the_workflow_page() -> None:
    source = ACTIVE_PAGE.read_text(encoding="utf-8")
    runtime_navigation = source.split('{group:"RUNTIME"', 1)[1].split("}]},", 1)[0]
    assert 'label:"Workflow Runs"' not in runtime_navigation
    assert '>Workflow Runs</button>' in source
    assert 'workflowPaneFocus==="runs"?"active":""' in source
    assert 'setWorkflowPaneFocus("runs");setView("canvas")' in source
    assert 'if(view!=="workflowRuns")return;setWorkflowPaneFocus("runs");setView("canvas")' in source
    assert 'view==="canvas"||view==="editor"||view==="workflowRuns"' in source
    assert 'workflowCombinedView&&<RuntimeHistoryView mode="workflowRuns"' in source
    styles = (ROOT / "workbench" / "frontend" / "src" / "styles" / "workbench.css").read_text(encoding="utf-8")
    assert 'grid-template-columns:minmax(0,calc(var(--workflow-editor-percent) - 3px)) 6px' in styles
    assert 'className="workflow-pane-divider"' in source
    runtime_history = (ROOT / "workbench/frontend/src/components/RuntimeHistoryView.tsx").read_text(encoding="utf-8")
    assert 'aria-label="Filter workflow runs by status"' in runtime_history
    assert 'setRunStatusFilter("running")' in runtime_history
    assert 'setRunStatusFilter("failed")' in runtime_history
    assert 'setRunStatusFilter("cancelled")' in runtime_history
    assert '["running", "waiting", "paused"].includes(run.status)' in runtime_history
    assert 'workflow-run-spline-band' in runtime_history
    assert 'workflow-run-object-workspace' in runtime_history
    assert 'grid-template-rows:minmax(145px,20%) minmax(0,80%)' in styles
    assert 'PanelFrameControls panel="spline"' in runtime_history
    assert 'PanelFrameControls panel="runs"' in runtime_history
    assert 'PanelFrameControls panel="objects"' in runtime_history
    assert 'row.run.id === selectedRun?.id ? "selected"' in runtime_history
    assert 'aria-label="Resize Workflow Editor and Workflow Runs"' in source
    assert 'aria-label="Workflow Runner panel controls"' in source
    assert 'aria-label="Workflow Task Editor panel controls"' in source
    workflow_layout = (ROOT / "workbench" / "frontend" / "src" / "styles" / "workflow_layout.css").read_text(encoding="utf-8")
    assert "grid-row: 2 !important" in workflow_layout
    assert "grid-row: 3 !important" in workflow_layout
    assert "grid-row: 4 !important" in workflow_layout
    assert 'setWorkflowEditorPercent(percent)' in source
    assert 'margin-top:calc(var(--workflow-runner-height,0px) + 25px)' in styles


def test_workflow_canvas_and_editor_share_one_navigation_destination() -> None:
    source = ACTIVE_PAGE.read_text(encoding="utf-8")
    assert '>Workflow Editor</button>' in source
    assert '>Workflow Runs</button>' in source
    assert source.count('workflow-focus-tab') == 2
    assert 'if(value==="editor")return "canvas"' in source
    assert 'view==="canvas"||view==="editor"||view==="workflowRuns"' in source
    assert 'workflowCombinedView&&<section className="canvas-view"' in source
    assert 'view==="editor"&&<section className="editor-surface"' in source
    assert 'onClick={()=>openRuntimeResource("operation",operation.id)}' in source
    assert 'view==="operations"&&<OperationLibraryEditor workspaceId={workspace.id}/>' in source


def test_workflow_operations_link_to_the_full_rich_editor() -> None:
    playground = (ROOT / "workbench" / "frontend" / "src" / "components" / "OperationPlayground.tsx").read_text(encoding="utf-8")
    assert 'view=operations&resource=${encodeURIComponent(operation.id)}' in playground
    assert '>Edit Operation</a>' in playground
    for capability in ("alternatives", "tabs", "split comparison", "raw source", "save", "executable playground"):
        assert capability in playground


def test_every_workflow_operation_step_uses_tab_panes() -> None:
    playground = (ROOT / "workbench" / "frontend" / "src" / "components" / "OperationPlayground.tsx").read_text(encoding="utf-8")
    assert 'activePane,setActivePane]=useState<"run"|"edit">("run")' in playground
    assert 'className="operation-step-tabs"' in playground
    assert '>Run Workflow Step</button>' in playground
    assert '>Edit Workflow Step</button>' in playground
    assert 'className="operation-step-editor-pane"' in playground
    assert 'onWorkflowStepChange?.(next)' in playground
    assert "ResourceSourceEditor" in playground
    assert 'label="Edit this Workflow Step directly"' in playground
    assert "MeTTa and JSON are synchronized views" in playground


def test_workflow_step_controls_do_not_leak_into_operation_pages() -> None:
    page = ACTIVE_PAGE.read_text(encoding="utf-8")
    playground = (ROOT / "workbench" / "frontend" / "src" / "components" / "OperationPlayground.tsx").read_text(encoding="utf-8")
    styles = (ROOT / "workbench" / "frontend" / "src" / "styles" / "workbench.css").read_text(encoding="utf-8")
    assert '<main className="workbench" data-view={view}>' in page
    assert 'Workflow Step controls are only available in Workflow Editor.' in page
    assert 'workflowStep?"▶ Run Workflow Step":"▶ Run Operation"' in playground
    assert ':not([data-view="workflowRuns"]) .automated-runner-tools' in styles


def test_workflow_editor_has_complete_runner_setup_surface() -> None:
    page = ACTIVE_PAGE.read_text(encoding="utf-8")
    launcher = (ROOT / "workbench" / "frontend" / "src" / "components" / "DurableRunLauncher.tsx").read_text(encoding="utf-8")
    history = (ROOT / "workbench" / "frontend" / "src" / "components" / "RuntimeHistoryView.tsx").read_text(encoding="utf-8")
    assert 'className="workflow-runner-setup"' not in page
    assert 'left-durable-run-launcher-slot' in page
    assert 'document.querySelector(".left-durable-run-launcher-slot")' in history
    for label in ("WORKFLOW RUNNER", "WORKFLOW INPUTS · JSON", "Validate", "Save Workflow", "Run Selected Step", "Run Workflow", "Run All Games"):
        assert label in launcher or label in page
    assert 'unresolvedWorkflowSteps.length' in page
    assert 'runInputsValid' in page


def test_systems_are_separate_from_model_backends() -> None:
    page = ACTIVE_PAGE.read_text(encoding="utf-8")
    editor = (ROOT / "workbench" / "frontend" / "src" / "components" / "LlmModelsEditor.tsx").read_text(encoding="utf-8")
    api = (ROOT / "workbench" / "server" / "workspace_api.py").read_text(encoding="utf-8")
    assert 'label:"Systems",view:"systems"' in page
    assert 'catalogMode="systems"' in page
    assert 'if(value==="backends")return "llms"' in page
    assert "snapshot?.systems" in editor
    assert 'document.kind==="system"?"design/systems"' in editor
    assert 'view==="systems"?"systems"' in page
    assert 'systemResources:snapshot?.systems?.length||0' in page
    help_tabs = (ROOT / "workbench" / "frontend" / "src" / "components" / "HelpDocumentTabs.tsx").read_text(encoding="utf-8")
    assert '{id:"systems",label:"Systems",path:"docs/systems.md"}' in help_tabs
    systems_docs = ROOT / "workbench" / "workspaces" / "shared_library_system" / "docs" / "systems.md"
    assert systems_docs.is_file()
    documentation = systems_docs.read_text(encoding="utf-8")
    assert "Systems are not model backends" in documentation
    assert "Agent Mailbox" in documentation
    assert "OmegaClaw is the local autonomous agent runtime" in documentation
    assert "OmegaClaw is not the Symbolic Learner Workbench" in documentation
    assert 'view==="sourceCode"||view==="prompts"?"prompts"' in page
    assert '"systems": _load_systems(workspace)' in api
    for system_id in ("python", "prolog", "metta", "llm", "omegaclaw", "codex", "mailbox"):
        assert (ROOT / "workbench" / "workspaces" / "shared_library_system" / "design" / "systems" / f"{system_id}.system.metta").is_file()


def test_source_code_editor_reuses_prompt_and_operation_source_editors() -> None:
    source = (ROOT / "workbench" / "frontend" / "src" / "components" / "SourceCodeEditor.tsx").read_text(encoding="utf-8")
    for label in ("Prompts", "Prolog", "MeTTa", "Python"):
        assert f'label:"{label}"' in source
    assert '<PromptLibraryEditor workspaceId={workspaceId}/>' in source
    assert '<OperationLibraryEditor workspaceId={workspaceId} sourceLanguage={tab}/>' in source
    operation_editor = (ROOT / "workbench" / "frontend" / "src" / "components" / "OperationLibraryEditor.tsx").read_text(encoding="utf-8")
    assert 'sourceLanguage?:SourceLanguage' in operation_editor
    assert 'implementation?.startsWith(sourceLanguage)' in operation_editor


def test_workspace_settings_manage_keys_without_rendering_secret_values() -> None:
    source = (ROOT / "workbench" / "frontend" / "src" / "components" / "WorkspaceSettingsPanel.tsx").read_text(encoding="utf-8")
    assert "BACKEND CREDENTIALS" in source
    assert 'type="password"' in source
    assert "/credentials/${encodeURIComponent(name)}" in source
    assert "SYSTEM CREDENTIALS" in source
    assert "Workbench-wide API keys" in source
    assert "System credential supplied — no workspace key required" in source
    assert "Optional credential not configured — backend may run without it" in source
    assert 'optional?"OPTIONAL":"REQUIRED"' in source
    assert 'credentialTargetId = mode==="settings" ? "shared_library_system" : workspace.id' in source
    assert "/bootstrap" in source
    assert "Set up automatically" not in source  # the backend supplies its specific setup label
    assert "are never returned by the API" in source
    assert "Clear workspace override" in source
    assert "Clear system key" in source


def test_rich_editors_are_loaded_by_route_instead_of_blocking_initial_shell() -> None:
    source = ACTIVE_PAGE.read_text(encoding="utf-8")
    assert 'lazy(()=>import("../components/OperationLibraryEditor")' in source
    assert 'lazy(()=>import("../components/LlmModelsEditor")' in source
    assert 'lazy(()=>import("../components/RepositoryDocsPage")' in source
    assert 'lazy(()=>import("../components/HelpDocumentTabs")' in source
    assert '<Suspense fallback={<div className="studio-empty">Loading editor…</div>}>' in source


def test_pending_pages_are_derived_from_workspace_or_runtime_state() -> None:
    source = ACTIVE_PAGE.read_text(encoding="utf-8")
    assert "snapshot?.files" in source
    assert 'view==="benchmarks"&&<ModelPolicyPage workspaceId={workspace.id}' in source
    assert '<RuntimeHistoryView mode="workflowRuns"' in source
    assert '<RuntimeHistoryView mode="execs"' in source
    assert '<RuntimeHistoryView mode="events"' in source
    assert 'view==="states"?"canvas"' in source
    assert 'workflowCombinedView&&<RuntimeHistoryView mode="workflowRuns"' in source
    assert '<RuntimeHistoryView mode="runtimeContexts"' in source
    assert '<RuntimeHistoryView mode="logs"' in source


def test_runtime_artifacts_deep_link_to_datatype_resources() -> None:
    page = ACTIVE_PAGE.read_text(encoding="utf-8")
    data_editor = (ROOT / "workbench" / "frontend" / "src" / "components" / "DataCatalogPanel.tsx").read_text(encoding="utf-8")
    assert 'kind:"operation"|"model"|"datatype"' in page
    assert 'kind==="model"?"llms":kind==="goal"?"goals"' in page
    assert 'kind==="context"?"contexts":"data"' in page
    assert 'new URLSearchParams(window.location.search).get("resource")' in data_editor
    assert "resourceIdentity(row.document?.label)===requestedId" in data_editor


def test_workspace_entry_does_not_wait_for_capability_diagnostics() -> None:
    source = (ROOT / "workbench" / "frontend" / "src" / "pages" / "FilesystemWorkbenchPage.tsx").read_text(encoding="utf-8")
    load_workspace = source.split("const loadWorkspace=", 1)[1].split("const createWorkspace=", 1)[0]
    critical_load = load_workspace.split("const next=", 1)[0]
    assert 'engine("/capabilities")' not in critical_load
    assert 'void engine("/capabilities").then' in load_workspace


def test_goal_runs_use_durable_goal_plan_context_contract() -> None:
    page = ACTIVE_PAGE.read_text(encoding="utf-8")
    component = (ROOT / "workbench" / "frontend" / "src" / "components" / "RuntimeHistoryView.tsx").read_text(encoding="utf-8")
    assert '<RuntimeHistoryView mode="goalRuns"' in page
    assert "/api/goal-runs" in component
    assert "goalId" in component and "planId" in component and "contextId" in component
    assert "goalVariantId" in component and "planVariantId" in component and "contextVariantId" in component
    assert "Pursue goal" in component
    assert "Submit human input" in component
    assert "selectRuntimeRun" in page
    assert 'doc.kind === "goal" && isRootResource(doc)' in component
    assert 'doc.kind === "planning_strategy" || doc.kind === "plan"' in component
    assert 'doc.kind === "atomspace" || doc.kind === "context"' in component
    assert '(!goalId || (plan.goals || []).includes(goalId))' in component
    assert 'contextSpecs.map(doc =>' in component
    assert "function WorkflowInputsEditor" in component
    assert "WORKFLOW INPUT CONTRACT" in component
    assert "Datatype-aware fields update the advanced JSON source below." in component
    assert "ADVANCED WORKFLOW INPUTS (JSON)" in component


def test_topbar_offers_persistent_workbench_themes() -> None:
    page = ACTIVE_PAGE.read_text(encoding="utf-8")
    styles = (ROOT / "workbench" / "frontend" / "src" / "styles" / "workbench.css").read_text(encoding="utf-8")
    assert 'aria-label="Workbench theme"' in page
    assert 'localStorage.getItem("workbench.theme")' in page
    assert 'localStorage.setItem("workbench.theme",theme)' in page
    assert "Midnight Teal" in page
    assert "Ultraviolet" in page
    assert "Copper Terminal" in page
    assert "Arctic Blue" in page
    assert "Paper White" in page
    assert "MSDN Light" in page
    assert "GitHub Light" in page
    assert "Solarized Light" in page
    assert "Dracula" in page
    assert "Monokai" in page
    assert "Retro Green" in page
    assert "Windows Classic" in page
    assert "Visual Studio Blue" in page
    assert "Porcelain" in page
    assert "Parchment" in page
    assert "High Visibility" in page
    assert page.count('-light",label:') >= 30
    assert 'data-workbench-theme="ultraviolet"' in styles
    assert 'data-workbench-theme="copper"' in styles
    assert 'data-workbench-theme="arctic"' in styles
    assert 'data-workbench-theme="paper-light"' in styles
    assert 'data-workbench-theme="msdn-light"' in styles


def test_theme_selector_runs_from_darkest_to_lightest() -> None:
    page = ACTIVE_PAGE.read_text(encoding="utf-8")
    ordered = ["Retro Green", "Midnight Teal", "Nord Night", "Solarized Light", "Paper White", "High Visibility"]
    positions = [page.index(f'label:"{label}"') for label in ordered]
    assert positions == sorted(positions)


def test_design_trees_show_effective_enablement() -> None:
    components = ROOT / "workbench" / "frontend" / "src" / "components"
    helper = (components / "resourceEnablement.tsx").read_text(encoding="utf-8")
    assert 'source: "self" | "parent" | "default"' in helper
    assert 'resource?.enabled === true' in helper
    assert 'resource?.enabled === false' in helper
    assert 'inherited ${state.enabled ? "on" : "off"}' in helper
    for filename in (
        "OperationLibraryEditor.tsx",
        "DataCatalogPanel.tsx",
        "PromptLibraryEditor.tsx",
        "LlmModelsEditor.tsx",
        "GoalPlanLibraryEditor.tsx",
        "PolicyLibraryEditor.tsx",
    ):
        source = (components / filename).read_text(encoding="utf-8")
        assert "ResourceEnablementBadge" in source
        assert "resolveResourceEnablement" in source
        assert "enablementClass" in source
    page = ACTIVE_PAGE.read_text(encoding="utf-8")
    assert "stage-button ${enablementClass(itemEnablement)}" in page
    styles = (ROOT / "workbench" / "frontend" / "src" / "styles" / "workbench.css").read_text(encoding="utf-8")
    assert ".operation-tree-row.resource-disabled" in styles
    assert ".stage-button.resource-disabled" in styles


def test_workflows_use_a_stable_shareable_view_url() -> None:
    page = ACTIVE_PAGE.read_text(encoding="utf-8")
    assert 'value==="workflows"' in page
    assert 'next==="canvas"?"workflows":next' in page
    assert 'url.searchParams.delete("menu")' in page


def test_workflow_editor_children_reflow_with_the_split_column() -> None:
    page = ACTIVE_PAGE.read_text(encoding="utf-8")
    styles = (ROOT / "workbench" / "frontend" / "src" / "styles" / "workbench.css").read_text(encoding="utf-8")
    playground_styles = (ROOT / "workbench" / "frontend" / "src" / "styles" / "operation_playground.css").read_text(encoding="utf-8")
    assert "container:workflow-editor-column/size" in styles
    assert "@container workflow-editor-column (max-width:760px)" in styles
    assert "runner.style.width" not in page
    assert ".canvas-view>.canvas-heading,.canvas-view>.stage-story,.canvas-view>.workflow-playground-stack{width:100%;max-width:none" in styles
    assert "@container workflow-editor-column (max-width:760px)" in playground_styles


def test_detected_memory_values_preserve_the_global_object_prefill() -> None:
    component = (ROOT / "workbench" / "frontend" / "src" / "components" / "RuntimeHistoryView.tsx").read_text(encoding="utf-8")
    assert 'title="DETECTED MEMORY VALUES"' not in component
    for scope in ("VALUES OF STEPS", "VALUES OF CHAPTER", "VALUES OF GAME", "VALUES OF ALL TIME", "VALUES POST-MORTEM"):
        assert f'title: "{scope}"' in component
    assert 'new Set(["objects", "startup"])' in component
    for property_label in ("ENABLED", "DISABLED · ALWAYS IGNORE", "Datatype", "STARTUP", "STEPS", "CHAPTER", "GAME", "ALWAYS", "POST-MORTEM", "Preferred Renderer", "Treat As List"):
        assert property_label in component
    assert "enabled: boolean;" in component
    assert "datatype: string;" in component
    assert "data-properties={JSON.stringify(value)}" in component
    assert "const objects = allObjects" in component
    assert "Global pre-fill" in component
    for label in ("Guess", "Image", "MeTTa", "JSON", "Small textbox"):
        assert f">{label}</option>" in component


def test_states_navigation_deep_links_to_the_combined_workflow_inspector() -> None:
    page = ACTIVE_PAGE.read_text(encoding="utf-8")
    assert 'const workflowCombinedView=view==="canvas"||view==="states"' in page
    assert 'view==="states"?"canvas"' in page
    assert 'querySelector<HTMLElement>(".detected-memory-controls")' in page
    assert 'view==="states"&&<RuntimeHistoryView mode="states"' not in page


def test_workflow_runner_bootstraps_editable_state_value_definitions() -> None:
    page = ACTIVE_PAGE.read_text(encoding="utf-8")
    for token in ('kind:"state_value"', "BOOTSTRAPPED STATE VALUES", "effectivePreflightStateValues", "ALLOW REDEFINITION", "stateValues:effectivePreflightStateValues"):
        assert token in page
    assert "allowRedefinition:false" in page
    assert "allowRedefinition:true" in page
    api = (ROOT / "workbench" / "server" / "workflow_engine_api.py").read_text(encoding="utf-8")
    assert "state_values=body.get('stateValues') or []" in api


def test_repeated_outputs_create_preflight_value_groups_and_spline_loops() -> None:
    page = ACTIVE_PAGE.read_text(encoding="utf-8")
    history = (ROOT / "workbench" / "frontend" / "src" / "components" / "RuntimeHistoryView.tsx").read_text(encoding="utf-8")
    engine = (ROOT / "workbench" / "server" / "workflow_engine.py").read_text(encoding="utf-8")
    assert "captureGroupIds" in page
    assert "WorkflowPreflightSpline" in page
    assert "PREFLIGHT SPLINE" in page
    assert "captureLoopEdges" in history
    assert "run.captureGroups" in history
    assert "_infer_capture_group_plan" in engine
    assert "_infer_capture_groups" in engine
    runtime = (ROOT / "workbench" / "frontend" / "src" / "components" / "RuntimeHistoryView.tsx").read_text(encoding="utf-8")
    assert "BootstrappedStateValues" in runtime
    assert "displayedStateValues" in runtime
    assert "Frozen with the selected run" in runtime
    assert "preflightStateValues={effectivePreflightStateValues}" in page


def test_resource_browser_layout_responds_to_its_own_width() -> None:
    css = (ROOT / "workbench" / "frontend" / "src" / "styles" / "workflow_layout.css").read_text(encoding="utf-8")
    assert "container-name: resource-browser" in css
    assert "@container resource-browser (max-width: 360px)" in css
    assert "@container resource-browser (max-width: 210px)" in css
    assert ".workflow-resource-browser .artifact-tree-branch-head" in css
    assert "grid-template-columns: minmax(0, 1fr)" in css


def test_workflow_editor_and_runs_stack_in_right_middle_column() -> None:
    css = (ROOT / "workbench" / "frontend" / "src" / "styles" / "workflow_layout.css").read_text(encoding="utf-8")
    assert "Reserved left middle column" in css
    assert "grid-template-columns: minmax(0, 1fr) minmax(0, 2fr) !important" in css
    assert "> .canvas-view" in css
    assert "> .workflow-runs-control" in css
    assert "grid-column: 2 !important" in css
    assert "grid-row: 3 !important" in css


def test_workflow_runner_is_a_parent_sized_vertical_control_stack() -> None:
    page = ACTIVE_PAGE.read_text(encoding="utf-8")
    assert 'className="workflow-runner-setup"' not in page
    assert "WorkflowLaunchControl" not in page
    assert ".left-durable-run-launcher-slot" in (ROOT / "workbench" / "frontend" / "src" / "styles" / "three_state_accordion.css").read_text(encoding="utf-8")


def test_selected_stage_uses_the_shared_three_state_accordion_contract() -> None:
    page = ACTIVE_PAGE.read_text(encoding="utf-8")
    css = (ROOT / "workbench" / "frontend" / "src" / "styles" / "three_state_accordion.css").read_text(encoding="utf-8")
    assert 'accordionPanelClass("selected-stage-accordion", selectedStageDisplayMode)' in page
    assert "onChange={setSelectedStageDisplayMode}" in page
    assert "ThreeStateAccordionControls label={`Stage ${currentStepNumber}" in page
    assert 'title="Collapse or restore this stage"' in page
    assert ".selected-stage-accordion.three-state-accordion-scroll" in css


def test_dead_workflow_launch_replacements_are_deleted() -> None:
    page = ACTIVE_PAGE.read_text(encoding="utf-8")
    history = (ROOT / "workbench" / "frontend" / "src" / "components" / "RuntimeHistoryView.tsx").read_text(encoding="utf-8")
    assert "WorkflowLaunchControl" not in page
    assert "workflowRunInsert" not in page
    assert "modernWorkflowRuns" not in history
    assert "workflow-runs-replacements" not in history


def test_workflow_runs_scrolls_records_without_scrolling_header() -> None:
    css = (ROOT / "workbench" / "frontend" / "src" / "styles" / "workflow_layout.css").read_text(encoding="utf-8")
    assert "Workflow Runs keeps its controls fixed" in css
    assert ".workflow-run-list-pane > .resource-heading" in css
    assert ".workflow-run-list-pane > .runtime-history-tools" in css
    assert ".workflow-run-list-pane > .resource-table" in css
    assert "overflow: hidden auto !important" in css
    isolated = (ROOT / "workbench" / "frontend" / "src" / "styles" / "durable_runs_accordion.css").read_text(encoding="utf-8")
    history = (ROOT / "workbench" / "frontend" / "src" / "components" / "RuntimeHistoryView.tsx").read_text(encoding="utf-8")
    assert ".durable-runs-accordion.three-state-accordion-strip" in isolated
    assert ".durable-runs-accordion.three-state-accordion-full .durable-runs-records" in isolated
    assert 'useState<AccordionDisplayMode>("scroll")' in history
    assert "grid-row: 4 !important" in css
    assert ".workflow-run-list-pane > .resource-heading > .panel-title-toggle" in css
    assert "background: transparent !important" in css
    assert "justify-items: start" in css
    assert "durable-runs-collapsed-head" in isolated
    assert "durable-runs-collapsed-head" in history
    assert "workflow-run-list-pane panel-frame" not in history


def test_isolated_durable_run_launcher_sits_above_workflow_runs() -> None:
    page = ACTIVE_PAGE.read_text(encoding="utf-8")
    component = (ROOT / "workbench" / "frontend" / "src" / "components" / "DurableRunLauncher.tsx").read_text(encoding="utf-8")
    css = (ROOT / "workbench" / "frontend" / "src" / "styles" / "workflow_layout.css").read_text(encoding="utf-8")
    isolated_css = (ROOT / "workbench" / "frontend" / "src" / "styles" / "durable_run_launcher.css").read_text(encoding="utf-8")
    assert "<DurableRunLauncher" in page
    assert "durable-run-launcher" in component
    assert "workflow-runner-setup" not in component
    assert "workflow-launch-control" not in component
    assert "> .durable-run-launcher" in css
    assert "grid-row: 2 !important" in css
    assert "durable-run-launcher-scroll" in isolated_css
    assert "overflow:hidden auto" in isolated_css
    assert 'aria-expanded={!collapsed}' in component
    history = (ROOT / "workbench" / "frontend" / "src" / "components" / "RuntimeHistoryView.tsx").read_text(encoding="utf-8")
    shared = (ROOT / "workbench" / "frontend" / "src" / "components" / "ThreeStateAccordion.tsx").read_text(encoding="utf-8")
    assert "launcherDisplayMode" in history
    assert '"strip" | "scroll" | "full"' in shared
    assert "ThreeStateAccordionControls" in component
    assert "--durable-launcher-track" in css
    assert "--workflow-runs-track" in css
    assert "--memory-values-track" in css
    assert "grid-template-rows: 38px var(--durable-launcher-track) var(--workflow-runs-track) var(--memory-values-track) var(--run-spline-track) 34px !important" in css


def test_right_column_has_shared_three_state_master_controls() -> None:
    history = (ROOT / "workbench" / "frontend" / "src" / "components" / "RuntimeHistoryView.tsx").read_text(encoding="utf-8")
    shared = (ROOT / "workbench" / "frontend" / "src" / "components" / "ThreeStateAccordion.tsx").read_text(encoding="utf-8")
    assert 'type AccordionDisplayMode = "strip" | "scroll" | "full"' in shared
    assert "ThreeStateAccordionStripSummary" in shared
    assert 'className={`three-state-accordion-strip-summary ${alwaysVisible ? "always-visible" : ""}`.trim()}' in shared
    assert 'aria-label="Set all right column accordion sizes"' in history
    for setter in ("setWorkflowRunsDisplayMode", "setObjectDisplayMode", "setObjectsListDisplayMode"):
        assert f"{setter}(nextMode)" in history
    assert "setLauncherDisplayMode(nextMode)" not in history
    assert 'aria-label="Collapse all right column panels to strips"' in history
    assert "displayMode={referenceDisplayMode}" in history
    assert "splineDisplayMode={splineDisplayMode}" in history
    assert 'const [splineDisplayMode, setSplineDisplayMode] =\n    useState<AccordionDisplayMode>("full")' in history
    assert 'const [referenceDisplayMode, setReferenceDisplayMode] =\n    useState<AccordionDisplayMode>("strip")' in history


def test_all_strip_mode_keeps_nested_detected_objects_visible() -> None:
    css = (ROOT / "workbench" / "frontend" / "src" / "styles" / "three_state_accordion.css").read_text(encoding="utf-8")
    layout = (ROOT / "workbench" / "frontend" / "src" / "styles" / "workflow_layout.css").read_text(encoding="utf-8")
    assert ":has(>.three-state-accordion-nested>.three-state-accordion){height:68px!important" in css
    assert ">.three-state-accordion-nested>.three-state-accordion{display:flex!important" in css
    assert ">.three-state-accordion-nested>.three-state-accordion>.three-state-accordion-strip-summary{display:flex!important" in css
    history = (ROOT / "workbench" / "frontend" / "src" / "components" / "RuntimeHistoryView.tsx").read_text(encoding="utf-8")
    runs_control = (ROOT / "workbench" / "frontend" / "src" / "components" / "WorkflowRunsControl.tsx").read_text(encoding="utf-8")
    assert 'label="WORKFLOW RUNS"' in runs_control
    assert 'label="DETECTED OBJECTS"' in history
    for title in ("VALUES OF STEPS", "VALUES OF CHAPTER", "VALUES OF GAME", "VALUES OF ALL TIME", "VALUES POST-MORTEM"):
        assert f'title: "{title}"' in history
    assert "--memory-values-track: 68px" in layout


def test_global_scroll_and_full_modes_have_distinct_overflow_contracts() -> None:
    shared_css = (ROOT / "workbench" / "frontend" / "src" / "styles" / "three_state_accordion.css").read_text(encoding="utf-8")
    history = (ROOT / "workbench" / "frontend" / "src" / "components" / "RuntimeHistoryView.tsx").read_text(encoding="utf-8")
    assert "overflow-x:auto;overflow-y:hidden;overscroll-behavior-x:contain" in shared_css
    assert "style={{ minWidth: width }}" in history
    assert "style={{ minWidth: chronologyWidth }}" in history
    assert ".workflow-runner-reference.three-state-accordion-strip{height:38px!important;min-height:38px!important;align-self:end}" in shared_css
    layout = (ROOT / "workbench" / "frontend" / "src" / "styles" / "workflow_layout.css").read_text(encoding="utf-8")
    assert "grid-template-rows: 38px 0 0 0 0 minmax(0, 1fr)" in layout
    assert ".workflow-runner-reference.three-state-accordion-scroll{display:flex;min-height:0;flex-direction:column}" in shared_css
    reference = (ROOT / "workbench" / "frontend" / "src" / "components" / "WorkflowRunnerTodoReference.tsx").read_text(encoding="utf-8")
    accordion = (ROOT / "workbench" / "frontend" / "src" / "components" / "ThreeStateAccordion.tsx").read_text(encoding="utf-8")
    assert "ThreeStateAccordionHeader" in reference
    assert "onDoubleClick={toggle}" in accordion
    assert '<ThreeStateAccordionHeader\n          className="workflow-run-spline-head"' in history
    assert "spline-title-toggle" not in history
    assert 'aria-label="Set every accordion panel size"' not in history
    assert 'window.dispatchEvent(new CustomEvent("workbench:set-all-accordion-modes"' not in history
    assert "setRightColumnDisplayMode(nextMode);" in history
    assert "setLauncherDisplayMode(nextMode);" not in history
    assert 'aria-pressed={rightColumnDisplayMode === "scroll"}' in history
    assert "grid-template-rows:minmax(0,1fr) minmax(34px,45%)" in shared_css
    assert "overflow-x: hidden !important" in layout
    assert ".durable-runs-accordion.three-state-accordion-strip) > .runtime-history-view > .workflow-run-object-workspace" not in layout
    runs_css = (ROOT / "workbench" / "frontend" / "src" / "styles" / "durable_runs_accordion.css").read_text(encoding="utf-8")
    layout = (ROOT / "workbench" / "frontend" / "src" / "styles" / "workflow_layout.css").read_text(encoding="utf-8")
    assert ".three-state-accordion-scroll>.detected-memory-accordion-body{display:grid" in shared_css
    assert ".three-state-accordion-scroll>.three-state-accordion-member-body{overflow:hidden auto}" in shared_css
    assert ".three-state-accordion-full>.three-state-accordion-member-body{height:max-content;overflow:visible}" in shared_css
    assert "overflow:visible!important" in runs_css
    for track in ("--durable-launcher-track: 300px", "--workflow-runs-track: 380px", "--memory-values-track: 320px"):
        assert track in layout


def test_three_state_accordion_selected_mode_stays_highlighted() -> None:
    component = (ROOT / "workbench/frontend/src/components/ThreeStateAccordion.tsx").read_text(encoding="utf-8")
    css = (ROOT / "workbench/frontend/src/styles/three_state_accordion.css").read_text(encoding="utf-8")

    assert 'className={mode === "strip" ? "active" : ""}' in component
    assert 'className={mode === "scroll" ? "active" : ""}' in component
    assert 'className={mode === "full" ? "active" : ""}' in component
    assert '.three-state-accordion-controls button[aria-pressed="true"],.three-state-accordion-controls button.active' in css
    assert "background:#12302f!important" in css


def test_accordion_drag_temporarily_uses_strip_list_and_restores_saved_frames() -> None:
    component = (ROOT / "workbench/frontend/src/components/ThreeStateAccordion.tsx").read_text(encoding="utf-8")
    css = (ROOT / "workbench/frontend/src/styles/three_state_accordion.css").read_text(encoding="utf-8")
    layout = (ROOT / "workbench/frontend/src/styles/workflow_layout.css").read_text(encoding="utf-8")

    assert 'const effectiveMode = activeAccordionDrag?.stackId === stackId ? "strip" : mode' in component
    assert "publishAccordionChange({ stackId, label })" in component
    assert "publishAccordionChange(null)" in component
    assert "moveAccordionMember(stackId, source.label, label)" in component
    assert "const nextIndex = sourceIndex + (targetIndex < sourceIndex ? -1 : 1)" in component
    assert 'localStorage.setItem(`accordion-order:${stackId}`' in component
    assert '"--accordion-member-order": layoutOrder' in component
    assert 'window.dispatchEvent(new CustomEvent(ACCORDION_ORDER_EVENT' in component
    assert 'member.style.setProperty("--accordion-member-order", String(index))' in component
    assert 'className="three-state-accordion-member-summary" draggable title={`Drag to reorder ${label}`}' in component
    assert '.three-state-accordion-member-summary{cursor:grab;touch-action:none}' in css
    assert "grid-row: calc(6 + var(--accordion-member-order)) !important" in layout


def test_memory_value_scopes_use_workflow_runs_peer_strips() -> None:
    history = (ROOT / "workbench/frontend/src/components/RuntimeHistoryView.tsx").read_text(encoding="utf-8")
    css = (ROOT / "workbench/frontend/src/styles/three_state_accordion.css").read_text(encoding="utf-8")

    assert "<ThreeStateAccordionMember" in history
    assert "label={section.title}" in history
    assert "value={section.detail}" in history
    assert 'className="workflow-run-object-workspace right-column-values-stack"' not in history
    assert 'data-accordion-stack="right-column"]>.three-state-accordion-member' in css
    assert ".three-state-accordion-member-strip{box-sizing:border-box;display:flex;flex:0 0 38px" in css
    assert ".three-state-accordion-member-summary{box-sizing:border-box;display:flex" in css
    assert 'className="detected-memory-fields"' not in history
    assert 'className="detected-objects-configuration"' in history
    detected_member = history.split('label="DETECTED OBJECTS"', 1)[1].split("</ThreeStateAccordionMember>", 1)[0]
    assert 'propertiesFor("objects")' in detected_member


def test_accordion_member_api_owns_strip_header_body_and_footer() -> None:
    component = (ROOT / "workbench/frontend/src/components/ThreeStateAccordion.tsx").read_text(encoding="utf-8")
    css = (ROOT / "workbench/frontend/src/styles/three_state_accordion.css").read_text(encoding="utf-8")

    for region in (
        "three-state-accordion-member-strip",
        "three-state-accordion-member-item-header",
        "three-state-accordion-member-body",
        "three-state-accordion-member-footer",
    ):
        assert region in component
    assert ".three-state-accordion-member.three-state-accordion-strip>.three-state-accordion-member-item-header" in css
    assert ":not(.three-state-accordion-member-strip):not(.three-state-accordion-nested){display:none!important}" in css
    assert ".three-state-accordion-member.three-state-accordion-strip>.three-state-accordion-member-strip{display:flex!important" in css
    assert ".three-state-accordion-member.three-state-accordion-scroll>.three-state-accordion-member-body{overflow:hidden auto}" in css
    assert ".three-state-accordion-member.three-state-accordion-full>.three-state-accordion-member-body{height:max-content;overflow:visible}" in css
    assert ".three-state-accordion-member.three-state-accordion-strip>.three-state-accordion-member-footer{display:none!important}" in css
    assert '"--accordion-scroll-size": scrollSize' in component
    assert ".three-state-accordion-member.three-state-accordion-scroll{height:var(--accordion-scroll-size)" in css


def test_left_workflow_stack_uses_the_shared_member_renderer() -> None:
    page = ACTIVE_PAGE.read_text(encoding="utf-8")
    launcher = (ROOT / "workbench/frontend/src/components/DurableRunLauncher.tsx").read_text(encoding="utf-8")

    assert '<ThreeStateAccordionStack id="left-column"' in page
    assert 'label={`STAGE ${currentStepNumber} OF ${workflow?.steps.length || 0}`}' in page
    assert 'label={`WORKFLOW STEP ${index + 1}`}' in page
    assert '<ThreeStateAccordionMember' in launcher
    assert 'label="WORKFLOW RUNNER"' in launcher


def test_resource_browser_is_one_accordion_and_left_steps_are_members() -> None:
    page = ACTIVE_PAGE.read_text(encoding="utf-8")
    branch = (ROOT / "workbench" / "frontend" / "src" / "components" / "ArtifactTreeBranch.tsx").read_text(encoding="utf-8")
    css = (ROOT / "workbench" / "frontend" / "src" / "styles" / "three_state_accordion.css").read_text(encoding="utf-8")
    assert "workflowStepDisplayModes" in page
    assert 'accordionPanelClass("resource-browser-contents", resourceBrowserDisplayMode)' in page
    assert 'title="RESOURCE BROWSER CONTENTS"' in page
    assert '["completed", "failed", "skipped", "cancelled"]' in page
    assert 'next[id] = "strip"' in page
    assert 'aria-label="Set all workflow step accordion sizes"' not in page
    assert 'accordionPanelClass("workflow-step-playground", workflowStepDisplayModes[step.id] || "scroll")' in page
    assert 'title={`WORKFLOW STEP ${index + 1}`}' in page
    assert ".resource-browser-contents.three-state-accordion-scroll>.stage-list" in css
    assert ".workflow-step-playground.three-state-accordion-scroll" in css


def test_legacy_workflow_has_requested_outer_and_memory_scope_stacks() -> None:
    page = ACTIVE_PAGE.read_text(encoding="utf-8")
    history = (ROOT / "workbench" / "frontend" / "src" / "components" / "RuntimeHistoryView.tsx").read_text(encoding="utf-8")
    css = (ROOT / "workbench" / "frontend" / "src" / "styles" / "workflow_layout.css").read_text(encoding="utf-8")
    assert 'label="LEFT COLUMN / RIGHT COLUMN"' in page
    assert 'stackId="spline-stack"' in page
    assert 'label="Left Column"' in page
    assert 'label="Right Column"' in page
    assert 'itemHeader={<div className="workflow-column-control-groups">' in page
    assert 'workflow-column-control-description' in page
    assert 'footer={null}' in page
    assert 'className="workflow-columns-stack-footer"' in page
    assert 'leftColumnDisplayMode={workflowLeftColumnDisplayMode}' in page
    assert 'rightColumnDisplayMode={workflowRightColumnDisplayMode}' in page
    assert '{false && <div className="right-column-accordion-master"' in history
    assert ".workflow-columns-stack-control > .three-state-accordion-member-item-header" in css
    assert ".durable-runs-accordion.three-state-accordion-strip) > .runtime-history-view > .workflow-run-object-workspace" in css
    assert "padding-top: 34px" in css
    for title in ("VALUES OF STEPS", "VALUES OF CHAPTER", "VALUES OF GAME", "VALUES OF ALL TIME", "VALUES POST-MORTEM"):
        assert f'title: "{title}"' in history
    assert 'baseClass="detected-memory-scope-member"' in history
    assert 'label="SELECTED RUN SPLINE"' in history
    assert 'itemHeader={<><span className="run-projection-mode-description"' in history
    assert 'className="run-projection-modes"' in history
    assert 'className="run-projection-mode-description">SPLINE VIEW' in history
    reference = (ROOT / "workbench" / "frontend" / "src" / "components" / "WorkflowRunnerTodoReference.tsx").read_text(encoding="utf-8")
    assert 'stackId="spline-stack"' in reference
    assert 'label="RUNNER DESIGN REFERENCE"' in reference


def test_accordion_members_register_with_shared_stack_and_strip_accessories() -> None:
    page = ACTIVE_PAGE.read_text(encoding="utf-8")
    history = (ROOT / "workbench/frontend/src/components/RuntimeHistoryView.tsx").read_text(encoding="utf-8")
    shared = (ROOT / "workbench/frontend/src/components/ThreeStateAccordion.tsx").read_text(encoding="utf-8")

    assert "export function ThreeStateAccordionStack" in shared
    assert "data-accordion-stack={id}" in shared
    assert "three-state-accordion-strip-accessories" in shared
    assert "accessories?: ReactNode" in shared
    assert 'ThreeStateAccordionStack id="right-column"' in history
    assert "rightColumnAccordionHost={rightColumnAccordionHost}" in history
    assert 'label="DETECTED OBJECTS"' in history
    assert 'stackId="right-column"' in history
    assert 'stackId="spline-stack"' in page
    assert 'itemHeader={<div className="workflow-column-control-groups">' in page


def test_workflow_composition_does_not_render_left_detected_memory_panel() -> None:
    history = (ROOT / "workbench" / "frontend" / "src" / "components" / "RuntimeHistoryView.tsx").read_text(encoding="utf-8")
    rendered = history.split("return (", 1)[-1]
    assert "<BootstrappedStateValues" not in rendered
    assert 'className="workflow-run-object-workspace right-column-values-stack"' in history
