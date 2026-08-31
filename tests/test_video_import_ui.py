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


def test_inherited_model_is_available_before_full_model_enumeration() -> None:
    source = VIDEO_IMPORT_PAGE.read_text(encoding="utf-8")

    fast_selection = source.index("model-selection?include_models=false")
    full_registry = source.index("/model-policy")
    assert fast_selection < full_registry
    assert "inheritedModelRef.current = inherited" in source
    assert "mergeModels([{ id: inherited, name: inherited }])" in source
    assert 'model.id === inheritedModelId ? " · inherited" : ""' in source
    assert "memberModelTouchedRef.current = true" in source
    assert "turtleModelTouchedRef.current = true" in source


def test_each_video_import_image_collection_has_a_distinct_gallery_name() -> None:
    source = VIDEO_IMPORT_PAGE.read_text(encoding="utf-8")

    for name in (
        "USER PICK GALLERY",
        "EXTRACTED FRAME GALLERY",
        "FILTER EFFECT GALLERY",
        "PROCESSED OUTPUT GALLERY",
        "PROCESSING TRAIL GALLERY",
        "EXTRACTED MEMBER GALLERY",
    ):
        assert name in source
    assert 'aria-label="Extracted Frame Gallery"' in source
    assert 'role="listitem"' in source
    assert "Extracted Frame Gallery:" in source
