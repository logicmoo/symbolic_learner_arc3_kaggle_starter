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
        "Plans",
        "Workflows",
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
        "Contexts",
        "Settings",
    ):
        assert f'label:"{label}"' in source


def test_navigation_reuses_current_rich_editors() -> None:
    source = ACTIVE_PAGE.read_text(encoding="utf-8")
    expected = {
        "Goals": ('view:"goals"', 'view==="goals"&&<GoalPlanLibraryEditor workspaceId={workspace.id} family="goal"'),
        "Plans": ('view:"plans"', 'view==="plans"&&<GoalPlanLibraryEditor workspaceId={workspace.id} family="plan"'),
        "Operations": ('view:"tasks"', 'view==="tasks"&&<TaskLibraryEditor'),
        "Datatypes": ('view:"data"', 'view==="data"&&<DataCatalogPanel'),
        "Prompts": ('view:"prompts"', 'view==="prompts"&&<PromptLibraryEditor'),
        "Models": ('view:"llms"', 'view==="llms"&&<LlmModelsEditor'),
        "Workflows": ('view:"canvas"', 'view==="editor"&&<section className="editor-surface"'),
        "Settings": ('view:"setup"', 'view==="setup"&&<section className="resource-view"'),
    }
    for label, tokens in expected.items():
        assert f'label:"{label}"' in source
        for token in tokens:
            assert token in source


def test_pending_pages_are_derived_from_workspace_or_runtime_state() -> None:
    source = ACTIVE_PAGE.read_text(encoding="utf-8")
    assert "snapshot?.files" in source
    assert "benchmarkResourceCount" in source
    assert "run?.steps.length" in source
    assert "run?.logs.length" in source
