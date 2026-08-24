from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_workspace_opening_preferences_are_scoped_and_default_to_overview():
    source = (ROOT / "workbench/frontend/src/lib/workspacePagePreferences.ts").read_text(encoding="utf-8")

    assert "metta-workbench.workspace-page-preferences.v1" in source
    assert "openingPageByWorkspace" in source
    assert "lastPageByWorkspace" in source
    assert 'systemOpeningPage: "overview"' in source
    assert "inheritedWorkspaceIds" in source
    assert "preferences.systemOpeningPage || \"overview\"" in source
    assert 'value: "inherit", label: "Automatic: Last Page, then Inherited / System"' in source


def test_missing_view_uses_workspace_preference_but_explicit_view_wins():
    source = (ROOT / "workbench/frontend/src/pages/FilesystemWorkbenchPage.tsx").read_text(encoding="utf-8")

    assert "const workspaceOpeningViewFromLocation = (inheritedWorkspaceIds: string[] = []): View =>" in source
    assert "const explicitView = viewFromLocation();" in source
    assert "if (explicitView) return explicitView;" in source
    assert "resolveWorkspaceOpeningPage(workspaceId, inheritedWorkspaceIds)" in source
    assert "rememberWorkspaceLastPage(workspace.id" in source
    assert 'if (value === "workflows" || value === "workflow") return "canvas";' in source


def test_settings_expose_workspace_opening_page_choice():
    source = (ROOT / "workbench/frontend/src/components/WorkspaceSettingsPanel.tsx").read_text(encoding="utf-8")

    assert "THIS WORKSPACE · OPENING PAGE" in source
    assert "WORKSPACE_OPENING_PAGE_OPTIONS" in source
    assert "setWorkspaceOpeningPage(workspace.id" in source
    assert "SYSTEM · OPENING PAGE FALLBACK" in source
    assert "setSystemOpeningPage" in source
    assert "Used only when the URL has no view=" in source
