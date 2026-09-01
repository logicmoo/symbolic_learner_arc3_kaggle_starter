from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_workspace_inspector_has_persistent_drag_resize_support() -> None:
    page = (ROOT / "workbench" / "frontend" / "src" / "pages" / "FilesystemWorkbenchPage.tsx").read_text(encoding="utf-8")
    styles = (ROOT / "workbench" / "frontend" / "src" / "styles" / "workbench.css").read_text(encoding="utf-8")
    for token in ('role="separator"', 'aria-label="Resize Documentation"', "beginInspectorResize", "workbench.inspectorWidth", "onDoubleClick"):
        assert token in page
    assert "var(--inspector-width)" in styles
    assert ".inspector-resizer" in styles
    assert "cursor:col-resize" in styles


def test_video_import_temporarily_minimizes_both_side_frames() -> None:
    page = (ROOT / "workbench" / "frontend" / "src" / "pages" / "FilesystemWorkbenchPage.tsx").read_text(encoding="utf-8")

    assert "previousShellViewRef" in page
    assert 'if (view === "videoImport")' in page
    assert 'if (previousView !== "videoImport")' in page
    assert 'if (previousView === "videoImport")' in page
    assert "videoImportShellWidthsRef.current" in page
    assert "setNavigationWidth(36)" in page
    assert "setResourceBrowserWidth(36)" in page
    assert "setInspectorWidth(36)" in page
    assert "setDebugUiEnabled(false)" in page
    assert "pageUiToolsVisible: false" in page
    assert "generationsVisible: false" in page
    assert "setNavigationWidth(previous.navigation)" in page
    assert "setResourceBrowserWidth(previous.resourceBrowser)" in page
    assert "setInspectorWidth(previous.inspector)" in page
