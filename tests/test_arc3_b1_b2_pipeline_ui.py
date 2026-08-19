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
    assert "return isB1B2PipelineRoute(routeView) ? 3 : 3;" in source
    assert 'const B1B2_RUNNER_NAMES = ["GUESSER", "REMOVER", "REGENERATOR"];' in source
    assert 'return pageDefinition.routeView === "arc3B1B2Pipeline" ? "GUESSER" : "A1";' in source
    # GUESSER full-extraction runner feeds REMOVER (removal), which feeds REGENERATOR (regeneration).
    assert 'if (runnerIndex === 0) return "extraction";' in source
    assert 'if (role === "extraction") return COMBINED_PROMPT;' in source
    assert 'if (role === "extraction") return "generate_prolog_and_english";' in source
    assert 'return ["runner:GUESSER"];' in source
    assert "SEED FROM GUESSER" in source
    # Experimental write-back: REGENERATOR result can replace GUESSER's list.
    assert "replaceGuesserOnFinish" in source
    assert "Replace GUESSER list with this result on finish" in source
    assert "many_objects_1" in source
    assert "many_objects_2" in source
    assert "llm_error|next_iteration|loop_complete|loop_overbudgeted|unran" in source
    # Per-image Column A data model: An bucket is the shared per-image store.
    assert "selectedImageIndex" in source
    assert "const selectImage" in source
    assert "const captureImageAnalysis" in source
    assert "analysis?: ImageAnalysis" in source
    # B1->B2 uses its own 3-column page class (A/B/C), not the prolog single-column layout.
    assert "english-workflow-page arc3-b1b2-page" in source
    assert "english-workflow-page arc3-prolog-page" not in source


def test_b1_b2_setup_switch_expands_selected_to_full() -> None:
    source = COMPONENT.read_text(encoding="utf-8")
    # Switching setups collapses every column-1 image to a strip and expands the
    # newly selected setup to full view, then scrolls it into view.
    assert 'for (const key of setupModeKeys) next[key] = "strip";' in source
    assert 'if (selectedModeKey) next[selectedModeKey] = "full";' in source
    assert 'scrollIntoView({ behavior: "smooth", block: "nearest" });' in source


def test_b1_b2_setup_image_members_keep_natural_height() -> None:
    css = (ROOT / "workbench/frontend/src/styles/arc3_prompt_prolog.css").read_text(encoding="utf-8")
    # Full-mode setup images must not shrink, so expanding one pushes the setups
    # below it down instead of overlapping them.
    assert '.arc3-b1b2-page .three-state-accordion-member[data-accordion-member^="image-"]' in css


def test_b1_b2_loop_validate_prompt_allows_disabled() -> None:
    source = COMPONENT.read_text(encoding="utf-8")
    # The Loop/Validate prompt dropdown must offer an explicit <disabled> choice
    # that turns the external validator off (loop still runs prompt-driven).
    assert 'VALIDATOR_PROMPT_DISABLED = "__validator_prompt_disabled__"' in source
    assert "<option value={VALIDATOR_PROMPT_DISABLED}>&lt;disabled&gt;</option>" in source
    assert "runner.validatorPromptName !== VALIDATOR_PROMPT_DISABLED" in source


def test_b1_b2_prompts_require_descriptive_object_ids() -> None:
    source = COMPONENT.read_text(encoding="utf-8")
    # A shared naming rule must force position/location-aware, descriptive
    # snake_case ids (not numeric/opaque) and be wired into every prompt.
    assert "const DESCRIPTIVE_ID_RULE =" in source
    assert "players_top_hud" in source
    assert "northern_most_exit" in source
    assert "position/location and orientation" in source
    # Primary extraction prompt (GUESSER) carries the naming contract.
    assert '"NAMING CONTRACT: " + DESCRIPTIVE_ID_RULE' in source
    # Removal (REMOVER) and gap-discovery prompts reference the shared rule.
    assert source.count("DESCRIPTIVE_ID_RULE") >= 4
    # Validator must reject non-descriptive ids.
    assert "Reject when any identity id is not descriptive" in source
