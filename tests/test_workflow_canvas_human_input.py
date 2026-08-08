from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "workbench" / "frontend" / "src" / "pages" / "FilesystemWorkbenchPage.tsx"
HISTORY = ROOT / "workbench" / "frontend" / "src" / "components" / "RuntimeHistoryView.tsx"


def test_active_workflow_canvas_reuses_typed_human_input_form_and_drafts():
    page = PAGE.read_text(encoding="utf-8")
    history = HISTORY.read_text(encoding="utf-8")

    assert "export function HumanInputForm" in history
    assert "<HumanInputForm step={selectedStep}" in page
    assert "humanDraftStatus" in page
    assert "/draft`" in page
    assert 'method:"PUT",body:JSON.stringify(humanValues)' in page
    assert 'body:JSON.stringify(humanValues)' in page
    assert 'value={humanValues}' not in page
