from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "workbench/frontend/src/components/Arc3PromptPrologPage.tsx"
B1_B2_PAGE = ROOT / "workbench/workspaces/arc3_random_player/design/workflow_pages/b1_b2_pipeline.workflow_page.json"


def test_two_image_prolog_has_overlay_gap_loop_contract() -> None:
    source = SOURCE.read_text(encoding="utf-8")

    assert "const GAP_DISCOVERY_PASS_PROMPT = [" in source
    assert "Image #3 is debug_overlay_image for pass-N coverage gap discovery." in source
    assert "Prior pass current_identities" in source
    assert "Loop converged at pass" in source
    assert "(box as Record<string, unknown>).x" in source
    assert "VALIDATION_ERRORS:" in source
    assert "VALIDATION-REPAIR MODE:" in source
    assert "validatePassOutput(" in source
    assert "REMOVAL_DISCOVERY_PASS_PROMPT" in source
    assert "generateRemovalArtifacts(" in source
    assert "tryParseValidatorAssessment(" in source
    assert "VALIDATOR-REPAIR MODE" not in source  # guard accidental typo
    assert "Loop stopped at time limit" in source
    assert "llm_error|next_iteration|loop_complete|loop_overbudgeted|unran" in source


def test_two_image_prolog_exposes_auto_loop_control() -> None:
    source = SOURCE.read_text(encoding="utf-8")

    assert 'onClick={() => void runPrompt(stackIndex, runnerIndex, "loop")}' in source
    assert 'onClick={() => void runPrompt(stackIndex, runnerIndex, "until_exit")}' in source
    assert "Run Until Exit" in source
    assert "Run Loop" in source
    assert 'const afterPath = stackKey === "A" ? DEFAULT_BEFORE_PATH : DEFAULT_AFTER_PATH;' in source
    assert "Running Until Exit" in source
    assert "Running Loop" in source
    assert "Run ${runnerDisplay} Primary" in source
    assert "PRIMARY_MODEL" in source
    assert "LOOP_MODEL" in source
    assert "effectively" not in source
    assert "Effective page model:" not in source
    assert "<runner-model>" not in source
    assert "<column-model>" not in source
    assert "arc3-prolog-inline-select-label" in source
    assert "arc3-prolog-inline-composite-label" in source
    assert '<label className="arc3-prolog-inline-select-label">' in source
    assert '<label className="arc3-prolog-inline-select-label arc3-prolog-inline-composite-label">' in source
    assert "arc3-prolog-setup-inline-input" in source
    assert "title={`Effective:" in source
    assert "<span>GENERATED</span>" not in source
    assert "GENERATED (this column)" not in source
    assert "Primary prompt name for" in source
    assert "arc3-prolog-prompt-summary" in source
    assert "circle_one_identity_at_a_time" in source
    assert "remove_smallest_object" in source
    assert "const promptDrivenIteration = removalLoopRunner || regenerateRunner;" in source
    assert "if (promptDrivenIteration)" in source
    assert "Loop stopped at pass ${passNumber}: exit_value=${acceptedExitValue}." in source
    assert 'if (runnerIndex === 0) return "removal";' in source
    assert 'if (runnerIndex === 1) return "regenerated";' in source
    assert "return isB1B2PipelineRoute(routeView) ? 2 : 3;" in source
    assert "legacy_root_getter:" in source
    assert 'if (role === "removal") return REMOVAL_DISCOVERY_PASS_PROMPT;' in source
    assert 'if (role === "regenerated") return REGENERATED_IDENTITIES_PROMPT;' in source
    assert 'if (role === "regenerated") return "regenerated_identities_from_many_objects";' in source
    assert 'return pageDefinition.routeView === "arc3B1B2Pipeline" ? "B1" : "A1";' in source
    assert "regenerated_identities_from_many_objects:" in source
    assert 'return runnerRole(routeView, stackKey, runnerIndex) === "removal";' in source
    assert 'return runnerRole(routeView, stackKey, runnerIndex) === "regenerated";' in source
    assert "OBJECT SEARCH ORDER (look for these first):" in source
    assert "Try to remove an array of similar objects in one pass whenever the similarity evidence is clear." in source
    assert "removed_object_1, removed_object_2, ... removed_object_n in ascending numeric order" in source
    assert "must NOT contain any other identity/object" in source
    assert "Special corridor rule: if an object looks like a corridor/maze shell, remove only the shell/walls and leave interior objects/content behind." in source
    assert "Always carry BOTH images forward for downstream processing" in source
    assert "Container and composite hard gates: never remove a parent/container/group object while removable leaf objects exist." in source
    assert "Validator prompt name for" in source
    assert "|&gt; Loop/Validate Prompt -" in source
    assert "name={`prompt-mode-" not in source
    assert "no_uncircled_objects" in source
    assert "no_objects" in source
    assert "LOOP CONDITIONS PROMPT" in source
    assert "LOOP_FILES" in source
    assert "many_objects_1" in source
    assert "many_objects_2" in source
    assert "image_with_circles" in source
    assert "image_of_object_removed" in source
    assert "image_without_object" in source
    assert "without uncircled objects" in source
    assert "image_with_objects" in source
    assert "RAW_PARSED" in source
    assert "SETUP LIST" in source
    assert "${setupIndex + 1}. ${setup.label || `Setup${setupIndex + 1}`} - ${setup.command || \"null\"}" in source
    assert "function parentImagePath(path: string): string" in source
    assert "data\\/level_1(?:\\/[^/]+)*\\/image\\." in source
    assert "Next Setup" in source
    assert "max_primary_secs" in source
    assert "max_loop_secs" in source
    assert "max={3600}" in source
    assert "max_iterations" in source
    assert "LIMITS:" in source
    assert "arc3-prolog-runner-limits-line" in source
    assert "Setup Label" in source
    assert "<span>COMMAND</span>" in source
    assert "Before Image Path" in source
    assert "Image Path" in source
    assert "Before preview" in source
    assert "Image preview" in source
    assert "X_SETUP_LABEL" in source
    assert "X_SETUP_COMMAND" in source
    assert "X_SETUP_BEFORE_IMAGE" in source
    assert "_SETUP_BEFORE_PATH" in source
    assert 'return ["ALL-Setup1"];' in source
    assert "ALL-Setup" in source
    assert "TWO IMAGE PROLOG.md" in source
    assert "docs/TWO IMAGE PROLOG.md" in source
    assert "Source" in source
    assert "Render" in source
    assert "Save" in source
    assert source.index("|&gt; Primary Prompt -") < source.index("max_primary_secs")
    assert source.index("|&gt; Primary Prompt -") < source.index("|&gt; Loop/Validate Prompt -")
    assert source.index("|&gt; Loop/Validate Prompt -") < source.index("max_primary_secs")
    assert source.index("max_primary_secs") < source.index("Run Until Exit")
    assert source.index("Run Until Exit") < source.index("LOOP_FILES")
    assert source.index("|&gt; Loop/Validate Prompt -") < source.index("RAW_PARSED")
    assert source.index("RAW_PARSED") < source.index("<summary>OUTPUT_FILES</summary>")


def test_b1_b2_pipeline_page_is_single_stack_layout_contract() -> None:
    source = B1_B2_PAGE.read_text(encoding="utf-8")
    assert '"routeView": "arc3B1B2Pipeline"' in source
    assert '"renderer": "arc3_prompt_prolog"' in source
    assert '"label": "B1 THEN B2"' in source
    assert '"label": "Run B1 Then B2"' in source
    assert '"label": "B1/B2 Output Files"' in source
    assert '"label": "Combined Prompt Contract"' in source
    assert '"initialDisplayMode": "scroll"' in source
