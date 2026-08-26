from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
ACTIVE_PAGE = ROOT / "workbench" / "frontend" / "src" / "pages" / "FilesystemWorkbenchPage.tsx"
APP = ROOT / "workbench" / "frontend" / "src" / "App.tsx"


class SourceText(str):
    """Formatting-insensitive text for this module's source-shape assertions."""

    @staticmethod
    def _compact(value: str) -> str:
        return "".join(value.split())

    def __contains__(self, value: object) -> bool:
        return isinstance(value, str) and self._compact(value) in self._compact(str(self))

    def split(self, separator: str | None = None, maxsplit: int = -1) -> list[str]:
        if separator is None:
            return super().split(separator, maxsplit)
        return self._compact(str(self)).split(self._compact(separator), maxsplit)

    def index(self, value: str, start: int = 0, stop: int | None = None) -> int:
        compact = self._compact(str(self))
        return compact.index(self._compact(value), start, len(compact) if stop is None else stop)

    def count(self, value: str, start: int = 0, stop: int | None = None) -> int:
        compact = self._compact(str(self))
        return compact.count(self._compact(value), start, len(compact) if stop is None else stop)


@pytest.fixture(autouse=True)
def formatting_insensitive_source(monkeypatch: pytest.MonkeyPatch) -> None:
    read_text = Path.read_text

    def read_source(path: Path, *args: object, **kwargs: object) -> SourceText:
        return SourceText(read_text(path, *args, **kwargs))

    monkeypatch.setattr(Path, "read_text", read_source)


def test_app_launches_filesystem_workbench_page() -> None:
    source = APP.read_text(encoding="utf-8")
    assert 'import { FilesystemWorkbenchPage } from "./pages/FilesystemWorkbenchPage"' in source
    assert "<FilesystemWorkbenchPage />" in source
    # Wrapped in the workbench-wide task registry so long-running actions
    # (e.g. Play & Record imports) can report status near the breadcrumbs
    # regardless of which page is active.
    assert 'import { TaskRegistryProvider } from "./taskRegistry"' in source
    assert "<TaskRegistryProvider>" in source


def test_removed_workflow_v2_route_redirects_to_the_active_workflow_page() -> None:
    source = ACTIVE_PAGE.read_text(encoding="utf-8")
    assert 'group: "WORKFLOWS"' in source
    assert 'label: "Workflows (Legacy)"' not in source
    assert 'label: "Workflows (New)"' not in source
    assert 'return "workflowV2"' not in source
    assert 'return "canvas"' in source
    assert "WorkflowWorkbenchV2" not in source
    assert not (ROOT / "workbench/frontend/src/components/WorkflowWorkbenchV2.tsx").exists()
    assert not (ROOT / "workbench/frontend/src/styles/workflow_v2.css").exists()


def test_navigation_v2_has_required_groups_and_labels() -> None:
    source = ACTIVE_PAGE.read_text(encoding="utf-8")
    compact = "".join(source.split())
    for group in ("WORKSPACE", "WORKFLOWS", "CAPABILITIES", "KNOWLEDGE", "RUNTIME", "SYSTEM"):
        assert f'group: "{group}"' in source
    for label in (
        "Goals",
        "Overview",
        "Planning",
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
    assert 'label: "Current Workflow", view: "currentWorkflow"' in source
    assert 'label: "Workflow Canvas", view: "canvas"' in source
    assert 'group: "WORKFLOWS"' in source
    assert 'workflowNavigationEntries.map' in source
    assert 'data-workflow-page-placement={entry.menuPlacement}' in source
    assert 'workflowPageMenuPlacementRank(left.menuPlacement)' in source
    assert '[workflowPageDefinitions]' in source
    assert "page-breadcrumb-trail" in source
    assert "Visited workbench pages" in source
    assert "returnToBreadcrumb" in source
    assert "setViewTrail" in source
    assert "viewTrailIndex" in source
    assert "breadcrumbNavigation" in source
    assert "current.slice(0,viewTrailIndex+1)" in source
    assert 'window.addEventListener("workbench:navigation"' in source
    assert "BreadcrumbEntry" in source
    assert 'label: "Artifacts", view: "knowledgeArtifacts"' in source


def test_plugin_contributed_rail_items_collapse_past_a_threshold() -> None:
    source = ACTIVE_PAGE.read_text(encoding="utf-8")
    assert "PLUGIN_MENU_COLLAPSE_THRESHOLD = 5" in source
    assert "sectionPluginEntries.length > PLUGIN_MENU_COLLAPSE_THRESHOLD" in source
    assert "data-plugin-group-toggle={section.group}" in source
    # The currently open plugin page must stay visible even when its group is collapsed.
    assert "hasSelectedEntry" in source
    assert (
        "explicitToggle !== undefined ? explicitToggle : !overThreshold || hasSelectedEntry"
        in source
    )


def test_navigation_scrollbar_reserves_space_inside_the_app_menu() -> None:
    styles = (ROOT / "workbench/frontend/src/styles/workbench.css").read_text(encoding="utf-8")

    assert ".rail.navigation-v2" in styles
    assert "box-sizing: border-box" in styles
    assert "scrollbar-gutter: stable" in styles
    assert ".rail.navigation-v2::-webkit-scrollbar" in styles


def test_navigation_menu_is_resizable_and_persistent() -> None:
    source = ACTIVE_PAGE.read_text(encoding="utf-8")
    styles = (ROOT / "workbench/frontend/src/styles/workbench.css").read_text(encoding="utf-8")

    assert "workbench.navigationWidth" in source
    assert "beginNavigationResize" in source
    assert 'aria-label="Resize App Menu"' in source
    assert "setNavigationWidth(220)" in source
    assert '"--nav-rail-width": `${navigationWidth}px`' in source
    assert ".navigation-resizer" in styles
    assert "left:calc(var(--nav-rail-width,220px) - 4px)" in styles
    assert "var(--nav-rail-width,220px) + var(--resource-browser-width,250px)" in styles
    assert ".rail.navigation-v2 .rail-icon{min-height:30px" in styles
    assert '.workbench[data-view="docs"] .workspace{grid-template-columns:var(--nav-rail-width,220px)' in styles
    assert "body.docs-focused .workspace{grid-template-columns:var(--nav-rail-width,220px)" in styles


def test_acceptance_debug_outlines_cover_all_control_types() -> None:
    styles = (ROOT / "workbench/frontend/src/styles/workbench.css").read_text(encoding="utf-8")

    for selector in (
        ".workbench.tsx-debug-enabled button",
        ".workbench.tsx-debug-enabled input",
        ".workbench.tsx-debug-enabled select",
        ".workbench.tsx-debug-enabled textarea",
        '.workbench.tsx-debug-enabled [contenteditable="true"]',
        '.workbench.tsx-debug-enabled [role="separator"]',
    ):
        assert selector in styles
    assert "RETAIN THROUGH 2026-09-02" in styles
    assert ".workbench.tsx-debug-enabled [class]" in styles
    assert "outline:1px dashed #b36bff" in styles
    popup = (ROOT / "workbench/frontend/src/components/TsxSourceLocationPopup.tsx").read_text(encoding="utf-8")
    assert 'closest("[data-tsx-source]")' in popup
    assert "target.location" in popup
    assert "event.clientX" in popup
    assert "event.clientY" in popup
    assert "pointermove" in popup
    assert "translateX(-100%)" in popup
    assert "<TsxSourceLocationPopup />" in ACTIVE_PAGE.read_text(encoding="utf-8")
    assert "[data-tsx-source-popup]" in styles
    vite = (ROOT / "workbench/frontend/vite.config.ts").read_text(encoding="utf-8")
    assert "workbench-tsx-source-locations" in vite
    assert 'from "@babel/parser"' in vite
    assert 'node.type === "JSXOpeningElement"' in vite
    assert 'id.split("?", 1)[0]' in vite
    assert 'replaceAll("\\\\", "/").toLowerCase()' in vite
    assert "data-tsx-source" in vite
    assert "normalizedSourceId.slice(normalizedSourceRoot.length + 1)" in vite
    assert "opening.loc?.start.line" in vite
    page = ACTIVE_PAGE.read_text(encoding="utf-8")
    assert "workbench.debugUiEnabled" in page
    assert "Debug UI On" in page
    assert "Debug UI Off" in page
    assert 'debugUiEnabled && <TsxSourceLocationPopup />' in page


def test_navigation_views_are_deep_linkable_for_visual_acceptance() -> None:
    source = ACTIVE_PAGE.read_text(encoding="utf-8")
    compact = "".join(source.split())
    assert 'new URLSearchParams(window.location.search)' in source
    assert 'url.searchParams.set("view",next==="canvas"?"workflows":next)' in compact
    assert 'window.addEventListener("popstate",restoreLocation)' in compact
    assert 'constrestoredView=viewFromLocation()' in compact
    assert 'setViewState(restoredView)' in compact
    assert 'workspaceOpeningViewFromLocation(next.workspace.effectiveIncludes||[])' in compact
    assert 'constrequested=workspaceFromLocation()' in compact
    assert 'requested===currentWorkspaceId.current' in compact
    assert 'loadRequestedWorkspace()' in compact
    assert 'loadingWorkspaceId.current!==null' in compact
    assert 'onClick={showWorkspaceChooser}' in compact
    assert '"workspace","resource","run","goalRun","runStep","runEvent","runtimeRecord","state"' in compact


def test_navigation_accepts_menu_as_a_deep_link_alias() -> None:
    source = ACTIVE_PAGE.read_text(encoding="utf-8")
    compact = "".join(source.split())
    assert 'parameters.get("view")||parameters.get("menu")' in compact
    assert 'parameters.has("state")?"states":null' in compact
    assert '[...WORKBENCH_VIEWS].find((candidate)=>candidate.toLowerCase()===value)' in compact
    assert 'if(view!=="overview")return' in compact
    assert '"run","goalRun","runStep","runEvent","runtimeRecord","state"' in compact
    assert 'url.searchParams.get("menu")==="overview"?["view"]' in compact


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
    layout_styles = (ROOT / "workbench" / "frontend" / "src" / "styles" / "workflow_layout.css").read_text(encoding="utf-8")
    relationship = source.split("const relationshipView=", 1)[1].split(";", 1)[0]
    artifact_focused = source.split("const artifactFocused=", 1)[1].split(";", 1)[0]
    assert "workflowCombinedView" in relationship
    assert 'view==="canvas"||view==="states"' in source
    assert 'view==="editor"' in relationship
    assert 'view==="canvas"' not in artifact_focused
    assert 'view==="editor"' not in artifact_focused
    assert '.workspace.artifact-focused:has(.canvas-view)>.stages-panel' in styles
    assert ".workbench .workspace > .stages-panel," in layout_styles
    assert ".workbench[data-view=\"currentWorkflow\"] .workspace > .stages-panel" in layout_styles


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
        "Goals": ('view:"goals"', 'view==="goals"&&(<GoalPlanLibraryEditor'),
        "Planning": ('view:"plans"', 'view==="plans"&&(<GoalPlanLibraryEditor'),
        "AtomSpaces": ('view:"contexts"', 'view==="contexts"&&(<GoalPlanLibraryEditor'),
        "Operations": ('view:"operations"', 'view==="operations"&&(<OperationLibraryEditor'),
        "Datatypes": ('view:"data"', 'view==="data"&&<DataCatalogPanel'),
        "Source Code": ('view:"sourceCode"', 'view==="sourceCode"&&(<SourceCodeEditor'),
        "Systems": ('view:"systems"', 'catalogMode="systems"'),
        "Models": ('view:"llms"', 'view==="llms"&&(<LlmModelsEditor'),
        "Settings": ('view:"setup"', 'view==="setup"&&(<WorkspaceSettingsPanel'),
    }
    for label, tokens in expected.items():
        assert f'label: "{label}"' in source
        for token in tokens:
            assert token.replace(" ", "") in compact
    assert 'label: "Current Workflow", view: "currentWorkflow"' in source
    assert 'label: "Workflow Canvas", view: "canvas"' in source
    assert 'setView("canvas")' in source
    assert 'workflowCombinedView&&workflowColumnsHost&&createPortal(<sectionclassName="canvas-view"' in compact
    assert 'className="editor-surface"' in compact


def test_source_code_language_tabs_are_deep_linkable() -> None:
    source = (ROOT / "workbench/frontend/src/components/SourceCodeEditor.tsx").read_text(encoding="utf-8")
    compact = "".join(source.split())
    assert 'get("sourceLanguage")' in source
    assert 'url.searchParams.set("sourceLanguage",next)' in source
    assert 'url.searchParams.delete("sourceLanguage")' in source
    assert 'window.history.pushState({},"",url)' in compact
    assert 'window.addEventListener("popstate",restore)' in compact
    page = ACTIVE_PAGE.read_text(encoding="utf-8")
    assert 'if (next !== "sourceCode") url.searchParams.delete("sourceLanguage")' in page


def test_workflow_authoring_pages_are_first_class_left_navigation_items() -> None:
    source = ACTIVE_PAGE.read_text(encoding="utf-8")
    compact = "".join(source.split())
    assert 'group:"WORKFLOWS",items:[{label:"WorkflowCanvas",view:"canvas",glyph:"⌘"},{label:"CurrentWorkflow",view:"currentWorkflow",glyph:"⌘"},{label:"PageBuilder",view:"workflowPageBuilder",glyph:"▦"}' in compact
    assert 'snapshot?.workflowPages' in source
    assert 'workflowNavigationEntries.map' in source
    assert 'data-workflow-page-resource={entry.id}' in source
    assert 'data-workflow-page-placement={entry.menuPlacement}' in source
    assert 'workflowPageDefinitions.map' in source
    assert '<WorkflowPageHost' in source
    assert 'workflow_generation_runtime' in source
    assert 'workflowPageForView.renderer === "visual_image_diff"' in source
    assert '<WorkflowPageBuilder initialDefinition={workflowNavigationEntries[0]?.definition}' in source
    nav_selection = compact.split("constnavSelected", 1)[1].split(";", 1)[0]
    assert 'view==="englishWorkflow"' not in nav_selection
    assert 'view==="visualImageDiff"' not in nav_selection


def test_workflow_runs_are_combined_with_the_workflow_page() -> None:
    source = ACTIVE_PAGE.read_text(encoding="utf-8")
    compact = "".join(source.split())
    runtime_navigation = source.split('{group:"RUNTIME"', 1)[1].split("}]},", 1)[0]
    assert 'label:"Workflow Runs"' not in runtime_navigation
    assert '>Workflow Runs</button>' in source
    assert 'workflowPaneFocus==="runs"?"active":""' in source
    assert 'setWorkflowPaneFocus("runs");setView("canvas")' in source
    assert 'if(view!=="workflowRuns")return;setWorkflowPaneFocus("runs");setView("canvas")' in source
    assert 'view==="canvas"||view==="editor"||view==="workflowRuns"' in source
    assert 'mode={view==="states"?"states":"workflowRuns"}' in compact
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
    assert 'ThreeStateAccordionStack id="right-stack"' in runtime_history
    assert 'grid-template-rows:minmax(145px,20%) minmax(0,80%)' in styles
    assert '<ThreeStateAccordionStack id="right-stack"' in runtime_history
    assert '<WorkflowRunsControl' in runtime_history
    assert '<WorkflowRunSplineWorkspace' in runtime_history
    assert 'mode === "workflowRuns"' in runtime_history
    assert 'row.key === selectedRecordKey' in runtime_history
    assert 'aria-label="Resize Workflow Editor and Workflow Runs"' in source
    assert 'controlsLabel="CENTER STACK"' in source
    assert '<ThreeStateAccordionStack id="center-stack" controlsLabel="CENTER STACK">' in source
    workflow_layout = (ROOT / "workbench" / "frontend" / "src" / "styles" / "workflow_layout.css").read_text(encoding="utf-8")
    assert "grid-row: 2 !important" in workflow_layout
    assert "grid-row: 3 !important" in workflow_layout
    assert "grid-row: 4 !important" in workflow_layout
    assert 'setWorkflowEditorPercent(percent)' in source
    assert 'margin-top:calc(var(--workflow-runner-height,0px) + 25px)' in styles


def test_state_uuid_deep_link_selects_a_durable_state_record() -> None:
    page = ACTIVE_PAGE.read_text(encoding="utf-8")
    runtime_history = (ROOT / "workbench/frontend/src/components/RuntimeHistoryView.tsx").read_text(encoding="utf-8")
    engine = (ROOT / "workbench/server/workflow_engine.py").read_text(encoding="utf-8")
    api = (ROOT / "workbench/server/workflow_engine_api.py").read_text(encoding="utf-8")
    page_compact = "".join(page.split())
    runtime_compact = "".join(runtime_history.split())

    assert 'mode={view==="states"?"states":"workflowRuns"}' in page_compact
    assert 'parameters.get(mode==="states"?"state":"runtimeRecord")' in runtime_compact
    assert 'url.searchParams.set("state",row.key)' in runtime_compact
    assert '`/api/engine/states/${encodeURIComponent(requestedStateId)}`' in runtime_history
    assert "def get_state(self, state_id: str)" in engine
    assert "@router.get('/states/{state_id}')" in api


def test_workflow_canvas_and_editor_share_one_navigation_destination() -> None:
    source = ACTIVE_PAGE.read_text(encoding="utf-8")
    assert '>Workflow Editor</button>' in source
    assert '>Workflow Runs</button>' in source
    assert source.count('workflow-focus-tab') == 2
    assert 'if(value==="editor")return "canvas"' in source
    assert 'view==="canvas"||view==="editor"||view==="workflowRuns"' in source
    assert 'workflowCombinedView&&workflowColumnsHost&&createPortal(<section className="canvas-view"' in source
    assert 'className="editor-surface"' in source
    assert 'onClick={()=>openRuntimeResource("operation",operation.id)}' in source
    assert '<OperationLibraryEditor workspaceId={workspace.id}/>' in source


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
    assert '<main className={`workbench ${debugUiEnabled ? "tsx-debug-enabled" : ""}`} data-view={view}>' in page
    assert 'Workflow Step controls are only available in Workflow Editor.' in page
    assert 'workflowStep?"▶ Run Workflow Step":"▶ Run Operation"' in playground
    assert ':not([data-view="workflowRuns"]) .automated-runner-tools' in styles


def test_workflow_editor_has_complete_runner_setup_surface() -> None:
    page = ACTIVE_PAGE.read_text(encoding="utf-8")
    launcher = (ROOT / "workbench" / "frontend" / "src" / "components" / "DurableRunLauncher.tsx").read_text(encoding="utf-8")
    history = (ROOT / "workbench" / "frontend" / "src" / "components" / "RuntimeHistoryView.tsx").read_text(encoding="utf-8")
    assert 'className="workflow-runner-setup"' not in page
    assert 'stackId="left-stack"' in launcher
    assert 'data-accordion-stack="left-stack"' in history
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
    assert 'constrootResource=backend||system' in "".join(editor.split())
    assert 'rootResource?(record.documentasBackendDef|SystemDef)?.provider' in "".join(editor.split())
    assert "SYSTEM CONFIGURATION" in editor
    assert '<SystemConfigForm source={doc.source}' in editor
    assert '<ResourceExecutionPlayground workspaceId={workspaceId} resource={document}' in editor
    help_tabs = (ROOT / "workbench" / "frontend" / "src" / "components" / "HelpDocumentTabs.tsx").read_text(encoding="utf-8")
    assert '{id:"systems",label:"Systems",path:"docs/systems.md"}' in help_tabs
    systems_docs = ROOT / "workbench" / "workspaces" / "shared_library_system" / "docs" / "systems.md"
    assert systems_docs.is_file()
    documentation = systems_docs.read_text(encoding="utf-8")
    assert "Systems are not model backends" in documentation
    assert "Agent Mailbox" in documentation
    assert "OmegaClaw is the local autonomous agent runtime" in documentation
    assert "OmegaClaw is not the Symbolic Learner Workbench" in documentation
    assert 'view==="sourceCode"?"sourceCode":view==="prompts"?"prompts"' in page
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
    assert 'view==="benchmarks"&&(<ModelPolicyPage workspaceId={workspace.id}' in source
    assert '<RuntimeHistoryView mode={view==="states"?"states":"workflowRuns"}' in source
    assert '<RuntimeHistoryView mode="execs"' in source
    assert '<RuntimeHistoryView mode="events"' in source
    assert 'view==="states"?"canvas"' in source
    assert 'workflowCombinedView&&workflowColumnsHost&&createPortal(<RuntimeHistoryView' in source
    assert '<RuntimeHistoryView mode="runtimeContexts"' in source
    assert '<RuntimeHistoryView mode="logs"' in source


def test_benchmarks_route_uses_a_distinct_filesystem_backed_catalog_view() -> None:
    page = ACTIVE_PAGE.read_text(encoding="utf-8")
    policy = (ROOT / "workbench" / "frontend" / "src" / "components" / "ModelPolicyPage.tsx").read_text(encoding="utf-8")
    styles = (ROOT / "workbench" / "frontend" / "src" / "styles" / "benchmark_catalog.css").read_text(encoding="utf-8")
    assert 'mode="benchmarks"' in page
    assert '"Benchmark Definitions & Results"' in policy
    assert '"SYSTEM · FILESYSTEM BENCHMARKS"' in policy
    assert ".benchmark-catalog-page .vendor-card" in styles
    assert ".benchmark-catalog-page .matrix-card" in styles
    assert 'view === "benchmarks"' in page and '? "benchmarks"' in page
    help_tabs = (ROOT / "workbench" / "frontend" / "src" / "components" / "HelpDocumentTabs.tsx").read_text(encoding="utf-8")
    assert 'id:"benchmarks",label:"Benchmarks",path:"docs/benchmarks.md"' in help_tabs


def test_source_code_has_dedicated_help_and_atomspace_paths_are_current() -> None:
    help_tabs = (ROOT / "workbench" / "frontend" / "src" / "components" / "HelpDocumentTabs.tsx").read_text(encoding="utf-8")
    page = (ROOT / "workbench" / "frontend" / "src" / "pages" / "FilesystemWorkbenchPage.tsx").read_text(encoding="utf-8")
    source_code = (ROOT / "workbench" / "workspaces" / "shared_library_system" / "docs" / "source_code.md").read_text(encoding="utf-8")
    atomspaces = (ROOT / "workbench" / "workspaces" / "shared_library_system" / "docs" / "contexts.md").read_text(encoding="utf-8")
    assert 'id:"sourceCode",label:"Source Code",path:"docs/source_code.md"' in help_tabs
    assert 'view === "sourceCode"' in page and '? "sourceCode"' in page
    assert all(language in source_code for language in ("Prolog", "MeTTa", "Python"))
    assert "`design/atomspaces/`" in atomspaces


def test_operations_use_one_categorized_hierarchy_renderer() -> None:
    editor = (ROOT / "workbench" / "frontend" / "src" / "components" / "OperationLibraryEditor.tsx").read_text(encoding="utf-8")
    assert editor.count("<CategorizedArtifactTree") == 1
    assert "(snapshot.operations||[]).map(operation=>" not in editor
    assert "same-kind parent is a concrete implementation alternative" in editor


def test_operations_are_capabilities_and_runtime_attempts_are_executions() -> None:
    guide = (ROOT / "workbench" / "workspaces" / "shared_library_system" / "docs" / "operations.md").read_text(encoding="utf-8")
    architecture = ROOT / "workbench" / "docs" / "design" / "OPERATIONS_AND_EXECUTIONS.md"
    assert "durable capability specification" in guide
    assert "durable delayed task" not in guide
    assert architecture.is_file()
    content = architecture.read_text(encoding="utf-8")
    assert "An Execution is one runtime attempt" in content
    assert "Codex task or thread is a separate collaboration record" in content
    assert not (ROOT / "workbench" / "docs" / "design" / "OPERATIONS_AS_DELAYED_AGENT_TASKS.md").exists()


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
    load_workspace = source.split("const loadWorkspaceById =", 1)[1].split("const loadWorkspace =", 1)[0]
    assert "setWorkspace(next.workspace)" in load_workspace
    assert "currentWorkspaceId.current=next.workspace.id" in load_workspace
    assert 'void engine("/capabilities").then' in source


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
    assert 'contextSpecs.map((doc) =>' in component
    assert "function WorkflowInputsEditor" in component
    assert "WORKFLOW INPUT CONTRACT" in component
    assert "Datatype-aware fields update the advanced JSON source below." in component
    assert "ADVANCED WORKFLOW INPUTS (JSON)" in component
    assert all(label in component for label in ("GOAL INTERPRETATION", "STRATEGY ALTERNATIVE", "ATOMSPACE", "ATOMSPACE ALTERNATIVE"))
    assert "GOAL VARIANT" not in component and "CONTEXT VARIANT" not in component
    assert 'execs: "Executions"' in component


def test_atomspace_editor_uses_atomspace_language_for_new_resources() -> None:
    component = (ROOT / "workbench" / "frontend" / "src" / "components" / "GoalPlanLibraryEditor.tsx").read_text(encoding="utf-8")
    assert 'family === "context" ? "AtomSpace" : family' in component
    assert "`Abstract ${familyNoun} specification.`" in component
    assert "`Concrete ${familyNoun} alternative.`" in component


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
    assert 'propertiesFor("objects")' in component
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
    compact = "".join(page.split())
    assert 'constworkflowCombinedView=view==="canvas"||view==="states"' in compact
    assert 'mode={view==="states"?"states":"workflowRuns"}' in compact
    assert 'if(!rawValue)returnparameters.has("state")?"states":null' in compact


def test_workflow_runner_bootstraps_editable_state_value_definitions() -> None:
    page = ACTIVE_PAGE.read_text(encoding="utf-8")
    for token in ('kind:"state_value"', "MEMORY / VALUE PLAN", "effectivePreflightStateValues", "allowRedefinition", "stateValues:effectivePreflightStateValues"):
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
    assert 'baseClass="selected-stage-accordion"' in page
    assert 'stackId="left-stack"' in page
    assert "onChange={setSelectedStageDisplayMode}" in page
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
    assert ".durable-runs-accordion" in isolated
    assert ".durable-runs-accordion.three-state-accordion-full .durable-runs-records" in isolated
    assert 'useState<AccordionDisplayMode>("scroll")' in history
    assert "grid-row: 4 !important" in css
    assert ".workflow-run-list-pane > .resource-heading > .panel-title-toggle" in css
    assert "background: transparent !important" in css
    assert "justify-items: start" in css
    assert ".durable-runs-accordion" in isolated
    assert "<WorkflowRunsControl" in history
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
    assert '<ThreeStateAccordionMember' in component
    assert 'stackId="left-stack"' in component
    history = (ROOT / "workbench" / "frontend" / "src" / "components" / "RuntimeHistoryView.tsx").read_text(encoding="utf-8")
    shared = (ROOT / "workbench" / "frontend" / "src" / "components" / "ThreeStateAccordion.tsx").read_text(encoding="utf-8")
    assert "launcherDisplayMode" in history
    assert '"strip" | "scroll" | "full"' in shared
    assert "ThreeStateAccordionMember" in component
    assert 'baseClass="durable-run-launcher panel-frame"' in component
    assert "--durable-launcher-track" in css
    assert "--workflow-runs-track" in css
    assert "--memory-values-track" in css
    assert "grid-template-rows: 38px var(--durable-launcher-track) var(--workflow-runs-track) var(--memory-values-track) var(--run-spline-track) max-content !important" in css


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
    assert "grid-template-rows: 38px minmax(34px, 30%) minmax(68px, 1fr) 0 var(--run-spline-track) 38px" in layout
    assert ".workflow-runner-reference.three-state-accordion-scroll{display:flex;min-height:0;flex-direction:column}" in shared_css
    reference = (ROOT / "workbench" / "frontend" / "src" / "components" / "WorkflowRunnerTodoReference.tsx").read_text(encoding="utf-8")
    accordion = (ROOT / "workbench" / "frontend" / "src" / "components" / "ThreeStateAccordion.tsx").read_text(encoding="utf-8")
    assert "ThreeStateAccordionMember" in reference
    assert "onDoubleClick={cycle}" in accordion
    assert "onChange(nextAccordionMode(mode))" in accordion
    assert 'label="SELECTED RUN SPLINE"' in history
    assert "spline-title-toggle" not in history
    assert 'aria-label="Set every accordion panel size"' not in history
    assert 'window.dispatchEvent(new CustomEvent("workbench:set-all-accordion-modes"' not in history
    assert "setWorkflowRunsDisplayMode(nextMode);" in history
    assert "setObjectDisplayMode(nextMode);" in history
    assert "setLauncherDisplayMode(nextMode);" not in history
    assert 'aria-pressed={rightColumnDisplayMode === "scroll"}' in history
    assert ".right-column-values-stack>.detected-memory-accordion-body" in shared_css
    assert "overflow:hidden auto;overscroll-behavior:contain" in shared_css
    assert "overflow-x: hidden !important" in layout
    assert ".durable-runs-accordion.three-state-accordion-strip) > .runtime-history-view > .workflow-run-object-workspace" in layout
    runs_css = (ROOT / "workbench" / "frontend" / "src" / "styles" / "durable_runs_accordion.css").read_text(encoding="utf-8")
    layout = (ROOT / "workbench" / "frontend" / "src" / "styles" / "workflow_layout.css").read_text(encoding="utf-8")
    assert ".workflow-run-object-workspace.three-state-accordion-scroll>.detected-memory-accordion-body{display:flex" in shared_css
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
    assert "publishAccordionChange({ stackId, label: orderKey })" in component
    assert "publishAccordionChange(null)" in component
    assert "moveAccordionMember(stackId, source.label, label)" in component
    assert "const nextIndex = sourceIndex + (targetIndex < sourceIndex ? -1 : 1)" in component
    assert 'localStorage.setItem(`accordion-order:${stackId}`' in component
    assert '"--accordion-member-order": layoutOrder' in component
    assert 'window.dispatchEvent(new CustomEvent(ACCORDION_ORDER_EVENT' in component
    assert 'member.style.setProperty("--accordion-member-order", String(index))' in component
    assert 'draggable={managedOrder === undefined}' in component
    assert 'managedOrder === undefined ? `Drag to reorder or click to cycle ${label}` : `Click to cycle ${label}`' in component
    assert '.three-state-accordion-member-summary{cursor:grab;touch-action:none}' in css
    assert "grid-row: calc(6 + var(--accordion-member-order)) !important" in layout


def test_memory_value_scopes_use_workflow_runs_peer_strips() -> None:
    history = (ROOT / "workbench/frontend/src/components/RuntimeHistoryView.tsx").read_text(encoding="utf-8")
    css = (ROOT / "workbench/frontend/src/styles/three_state_accordion.css").read_text(encoding="utf-8")

    assert "<ThreeStateAccordionMember" in history
    assert "label={section.title}" in history
    assert "value={section.detail}" in history
    assert 'className="workflow-run-object-workspace right-column-values-stack"' not in history
    assert 'data-accordion-stack="right-stack"]>.three-state-accordion-member' in css
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

    assert '<ThreeStateAccordionStack id="left-stack"' in page
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
    assert 'mode={workflowStepDisplayModes[step.id] || "scroll"}' in page
    assert 'stackId="left-stack"' in page
    assert 'label={`WORKFLOW STEP ${index + 1}`}' in page
    assert ".resource-browser-contents.three-state-accordion-scroll>.stage-list" in css
    assert ".workflow-step-playground.three-state-accordion-scroll" in css


def test_legacy_workflow_has_requested_outer_and_memory_scope_stacks() -> None:
    page = ACTIVE_PAGE.read_text(encoding="utf-8")
    history = (ROOT / "workbench" / "frontend" / "src" / "components" / "RuntimeHistoryView.tsx").read_text(encoding="utf-8")
    css = (ROOT / "workbench" / "frontend" / "src" / "styles" / "workflow_layout.css").read_text(encoding="utf-8")
    assert 'controlsLabel="CENTER STACK"' in page
    assert 'id="left-stack"' in page
    assert 'id="right-stack"' in history
    assert 'className="workflow-columns-stack-footer"' in page
    assert 'leftColumnDisplayMode={workflowLeftColumnDisplayMode}' in page
    assert 'rightColumnDisplayMode={workflowRightColumnDisplayMode}' in page
    assert 'ThreeStateAccordionStack id="right-stack"' in history
    for title in ("VALUES OF STEPS", "VALUES OF CHAPTER", "VALUES OF GAME", "VALUES OF ALL TIME", "VALUES POST-MORTEM"):
        assert f'title: "{title}"' in history
    assert 'baseClass="detected-memory-scope-member"' in history
    assert 'label="SELECTED RUN SPLINE"' in history
    assert 'className="run-projection-modes"' in history
    assert 'className="run-projection-mode-description">SPLINE VIEW' in history
    reference = (ROOT / "workbench" / "frontend" / "src" / "components" / "WorkflowRunnerTodoReference.tsx").read_text(encoding="utf-8")
    assert 'stackId="center-stack"' in reference
    assert 'label="RUNNER DESIGN REFERENCE"' in reference


def test_accordion_members_register_with_shared_stack_and_strip_accessories() -> None:
    page = ACTIVE_PAGE.read_text(encoding="utf-8")
    history = (ROOT / "workbench/frontend/src/components/RuntimeHistoryView.tsx").read_text(encoding="utf-8")
    shared = (ROOT / "workbench/frontend/src/components/ThreeStateAccordion.tsx").read_text(encoding="utf-8")

    assert "export function ThreeStateAccordionStack" in shared
    assert "data-accordion-stack={id}" in shared
    assert "three-state-accordion-strip-accessories" in shared
    assert "accessories?: ReactNode" in shared
    assert 'ThreeStateAccordionStack id="right-stack"' in history
    assert "rightColumnAccordionHost={rightColumnAccordionHost}" in history
    assert 'label="DETECTED OBJECTS"' in history
    assert 'stackId="right-stack"' in history
    assert 'stackId="center-stack"' in page
    assert 'stackId="left-stack"' in page


def test_workflow_composition_does_not_render_left_detected_memory_panel() -> None:
    history = (ROOT / "workbench" / "frontend" / "src" / "components" / "RuntimeHistoryView.tsx").read_text(encoding="utf-8")
    rendered = history.split("return (", 1)[-1]
    assert "<BootstrappedStateValues" not in rendered
    assert 'ThreeStateAccordionStack id="right-stack"' in history
