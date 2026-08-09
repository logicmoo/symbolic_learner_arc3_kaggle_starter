from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ACTIVE_PAGE = ROOT / "workbench" / "frontend" / "src" / "pages" / "FilesystemWorkbenchPage.tsx"
APP = ROOT / "workbench" / "frontend" / "src" / "App.tsx"


def test_app_launches_filesystem_workbench_page() -> None:
    source = APP.read_text(encoding="utf-8")
    assert 'import { FilesystemWorkbenchPage } from "./pages/FilesystemWorkbenchPage"' in source
    assert "return <FilesystemWorkbenchPage />" in source


def test_navigation_v2_has_required_groups_and_labels() -> None:
    source = ACTIVE_PAGE.read_text(encoding="utf-8")
    for group in ("DESIGN", "RUNTIME", "SYSTEM"):
        assert f'group:"{group}"' in source
    for label in (
        "Goals",
        "Planning Strategies",
        "Workflows / Plans",
        "Operations",
        "Datatypes",
        "Prompts",
        "Models",
        "Goal Runs",
        "Workflow Runs",
        "Execs",
        "Events",
        "States",
        "Logs",
        "Model Policy",
        "Benchmarks",
        "AtomSpaces",
        "Contexts",
        "Settings",
    ):
        assert f'label:"{label}"' in source


def test_artifact_editors_hide_the_run_pipeline_column() -> None:
    source = ACTIVE_PAGE.read_text(encoding="utf-8")
    styles = (ROOT / "workbench" / "frontend" / "src" / "styles" / "workbench.css").read_text(encoding="utf-8")
    assert 'relationshipView?"artifact-focused":""' in source
    assert ".workspace.artifact-focused>.stages-panel{display:none}" in styles


def test_navigation_reuses_current_rich_editors() -> None:
    source = ACTIVE_PAGE.read_text(encoding="utf-8")
    expected = {
        "Goals": ('view:"goals"', 'view==="goals"&&<GoalPlanLibraryEditor workspaceId={workspace.id} family="goal"'),
        "Planning Strategies": ('view:"plans"', 'view==="plans"&&<GoalPlanLibraryEditor workspaceId={workspace.id} family="plan"'),
        "AtomSpaces": ('view:"contexts"', 'view==="contexts"&&<GoalPlanLibraryEditor workspaceId={workspace.id} family="context"'),
        "Operations": ('view:"operations"', 'view==="operations"&&<OperationLibraryEditor'),
        "Datatypes": ('view:"data"', 'view==="data"&&<DataCatalogPanel'),
        "Prompts": ('view:"prompts"', 'view==="prompts"&&<PromptLibraryEditor'),
        "Models": ('view:"llms"', 'view==="llms"&&<LlmModelsEditor'),
        "Workflows / Plans": ('view:"canvas"', 'view==="editor"&&<section className="editor-surface"'),
        "Settings": ('view:"setup"', 'view==="setup"&&<WorkspaceSettingsPanel'),
    }
    for label, tokens in expected.items():
        assert f'label:"{label}"' in source
        for token in tokens:
            assert token in source


def test_workspace_settings_manage_keys_without_rendering_secret_values() -> None:
    source = (ROOT / "workbench" / "frontend" / "src" / "components" / "WorkspaceSettingsPanel.tsx").read_text(encoding="utf-8")
    assert "BACKEND CREDENTIALS" in source
    assert 'type="password"' in source
    assert "/credentials/${encodeURIComponent(name)}" in source
    assert "/bootstrap" in source
    assert "Set up automatically" not in source  # the backend supplies its specific setup label
    assert "are never returned by the API" in source
    assert "Clear workspace key" in source


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
    assert '<RuntimeHistoryView mode="states"' in source
    assert '<RuntimeHistoryView mode="runtimeContexts"' in source
    assert '<RuntimeHistoryView mode="logs"' in source


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
