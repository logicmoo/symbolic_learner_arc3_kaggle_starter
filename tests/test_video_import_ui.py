from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VIDEO_IMPORT_PAGE = (
    ROOT
    / "workbench"
    / "frontend"
    / "src"
    / "components"
    / "VideoImportPage.tsx"
)


def test_user_preview_picker_has_no_number_parameter() -> None:
    source = VIDEO_IMPORT_PAGE.read_text(encoding="utf-8")

    assert '{groupKind !== "user" && (' in source
    assert 'id === "select:user" ? {} : { n: "" }' in source
    assert 'step.entryId === "select:user" ? { ...step, params: {} } : step' in source

    user_picker = source.index('if (groupKind === "user")')
    numbered_picker = source.index(
        "const count = Math.max(1, Math.min(frames.length, Number(groupCount) || 6));"
    )
    assert user_picker < numbered_picker
