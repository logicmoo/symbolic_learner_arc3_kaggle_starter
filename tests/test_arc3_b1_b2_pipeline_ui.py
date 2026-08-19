from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "workbench/frontend/src/components/Arc3B1B2PipelinePage.tsx"
WORKBENCH = ROOT / "workbench/frontend/src/pages/FilesystemWorkbenchPage.tsx"
PAGE = ROOT / "workbench/workspaces/arc3_random_player/design/workflow_pages/b1_b2_pipeline.workflow_page.json"


def test_b1_b2_page_uses_dedicated_renderer() -> None:
    source = PAGE.read_text(encoding="utf-8")
    assert '"routeView": "arc3B1B2Pipeline"' in source
    assert '"renderer": "arc3_b1_b2_pipeline"' in source
    assert '"renderer": "arc3_prompt_prolog"' not in source
    assert '"label": "DATA"' in source
    assert '"label": "RUNNERS"' in source
    assert '"label": "SOURCE"' in source
    assert '"label": "Run B1 Then B2"' in source
    assert '"label": "B1/B2 Output Files"' in source
    assert '"label": "Combined Prompt Contract"' in source
    assert '"initialDisplayMode": "scroll"' in source


def test_b1_b2_renderer_is_wired_in_workbench() -> None:
    source = WORKBENCH.read_text(encoding="utf-8")
    assert 'workflowPageForView.renderer === "arc3_b1_b2_pipeline"' in source
    assert 'import("../components/Arc3B1B2PipelinePage")' in source
    assert "default: module.Arc3B1B2PipelinePage," in source
    assert "<Arc3B1B2PipelinePage" in source
    # The shared prolog renderer must remain wired for the Two-Image page.
    assert 'workflowPageForView.renderer === "arc3_prompt_prolog"' in source
    assert "<Arc3PromptPrologPage" in source


def test_b1_b2_component_has_pipeline_contract() -> None:
    source = COMPONENT.read_text(encoding="utf-8")
    assert "export function Arc3B1B2PipelinePage(" in source
    assert "export function Arc3PromptPrologPage(" not in source
    assert "remove_smallest_object" in source
    assert "regenerated_identities_from_many_objects" in source
    assert "REMOVAL_DISCOVERY_PASS_PROMPT" in source
    assert "REGENERATED_IDENTITIES_PROMPT" in source
    assert "isB1B2PipelineRoute" in source
    assert "return isB1B2PipelineRoute(routeView) ? 2 : 3;" in source
    assert 'return pageDefinition.routeView === "arc3B1B2Pipeline" ? "B1" : "A1";' in source
    assert "many_objects_1" in source
    assert "many_objects_2" in source
    assert "llm_error|next_iteration|loop_complete|loop_overbudgeted|unran" in source
    # Per-image Column A data model: An bucket is the shared per-image store.
    assert "selectedImageIndex" in source
    assert "const selectImage" in source
    assert "const captureImageAnalysis" in source
    assert "analysis?: ImageAnalysis" in source
