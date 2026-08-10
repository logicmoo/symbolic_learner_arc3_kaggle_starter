from pathlib import Path


FRONTEND = Path(__file__).resolve().parents[1] / "workbench" / "frontend" / "src"


def test_active_resource_editors_share_metta_json_source_editor() -> None:
    expected = {
        "components/OperationLibraryEditor.tsx",
        "components/DataCatalogPanel.tsx",
        "components/GoalPlanLibraryEditor.tsx",
        "components/PromptLibraryEditor.tsx",
        "components/LlmModelsEditor.tsx",
        "components/PolicyLibraryEditor.tsx",
        "pages/FilesystemWorkbenchPage.tsx",
    }
    for relative in expected:
        source = (FRONTEND / relative).read_text(encoding="utf-8")
        assert "ResourceSourceEditor" in source, relative


def test_resource_source_editor_defaults_to_metta_and_keeps_json_available() -> None:
    source = (FRONTEND / "components/ResourceSourceEditor.tsx").read_text(encoding="utf-8")
    assert 'useState<"metta" | "json">("metta")' in source
    assert '>MeTTa</button>' in source
    assert '>JSON</button>' in source
    assert "mettaDocumentToJson" in source
    assert "jsonDocumentToMetta" in source


def test_primary_design_editors_display_physical_metta_paths() -> None:
    path_helper = (FRONTEND / "components/resourcePath.ts").read_text(encoding="utf-8")
    assert 'replace(/\\.json$/i, ".metta")' in path_helper
    for relative in (
        "components/OperationLibraryEditor.tsx",
        "components/LlmModelsEditor.tsx",
        "components/PolicyLibraryEditor.tsx",
    ):
        source = (FRONTEND / relative).read_text(encoding="utf-8")
        assert "displayResourcePath(doc.record.path)" in source, relative
    models = (FRONTEND / "components/LlmModelsEditor.tsx").read_text(encoding="utf-8")
    assert "RESOURCE SPECIFICATION (JSON)" not in models
    assert "RESOURCE SOURCE" in models


def test_runtime_object_previews_render_as_metta() -> None:
    expected = {
        "pages/FilesystemWorkbenchPage.tsx": ("selectedStep.inputs", "selectedArtifact"),
        "components/OperationPlayground.tsx": ("result.outputs",),
        "components/RuntimeHistoryView.tsx": ("event.payload", "item.payload"),
    }
    for relative, values in expected.items():
        source = (FRONTEND / relative).read_text(encoding="utf-8")
        assert "jsonValueToMetta" in source, relative
        for value in values:
            assert f"jsonValueToMetta({value}" in source, (relative, value)
