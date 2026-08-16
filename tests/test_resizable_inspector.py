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
