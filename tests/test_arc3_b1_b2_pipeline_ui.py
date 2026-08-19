from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "workbench/frontend/src/components/Arc3B1B2PipelinePage.tsx"
STYLES = ROOT / "workbench/frontend/src/styles/arc3_prompt_prolog.css"
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


def test_b1_b2_identity_parser_accepts_bbox_and_corners() -> None:
    source = COMPONENT.read_text(encoding="utf-8")
    # The identity parser must accept the bbox/box aliases (not just
    # bounding_box) and convert [x1,y1,x2,y2] corner boxes to [x,y,w,h].
    assert "function coerceIdentityBoundingBox" in source
    assert "record.bounding_box ?? record.bbox ?? record.box" in source
    assert "const corners = cornerHint || (nc > na && nd > nb)" in source
    # Prompt documents the accepted bounding-box shape.
    assert "BOUNDING BOX CONTRACT:" in source
    assert "bbox is accepted as an alias" in source


def test_b1_b2_setup_field_labeled_after_image() -> None:
    source = COMPONENT.read_text(encoding="utf-8")
    # The setup image fields use explicit BEFORE/AFTER labels, never a bare "IMAGE PATH".
    assert "<span>AFTER</span>" in source
    assert "<span>BEFORE</span>" in source
    assert "<span>IMAGE PATH</span>" not in source
    assert "_IMAGE PATH</span>" not in source


def test_b1_b2_setup_generated_files_in_input_picker() -> None:
    source = COMPONENT.read_text(encoding="utf-8")
    # Options builder: each setup's generated subimages + text outputs become
    # individual INPUT_FILES options keyed by setup id + analysis item key.
    assert "value: `setup-file:${setup.id}:${item.key}`," in source
    assert "label: `SETUP ${setupOrdinal + 1} FILE ${item.label} (${columnState.key})`," in source
    assert "...(setup.analysis?.subimages || [])," in source
    assert "...(setup.analysis?.textFiles || [])," in source
    # Resolver: setup-file tokens resolve to the analysis item content.
    assert "const setupFileMatch = /^setup-file:([^:]+):(.+)$/i.exec(trimmed);" in source
    assert "[...setup.analysis.subimages, ...setup.analysis.textFiles]" in source
    # Chip display stays readable for the new token.
    assert "const setupFile = /^setup-file:[^:]+:(.+)$/i.exec(trimmed);" in source
    assert 'if (setupFile) return `SETUP_FILE ${setupFile[1]}`;' in source


def test_b1_b2_setup_has_before_image_and_command_fields() -> None:
    source = COMPONENT.read_text(encoding="utf-8")
    # Each setup exposes editable COMMAND and BEFORE image fields
    # alongside the existing AFTER image field.
    assert "<span>COMMAND</span>" in source
    assert "<span>BEFORE</span>" in source
    assert "<span>AFTER</span>" in source
    # Wired to dedicated setters that update the setup in place.
    assert "const setSetupCommand = (stackIndex: number, imageIndex: number, command: string) =>" in source
    assert "const setBeforeImagePath = (stackIndex: number, imageIndex: number, path: string) =>" in source
    assert "onChange={(event) => setSetupCommand(stackIndex, imageIndex, event.target.value)}" in source
    assert "onChange={(event) => setBeforeImagePath(stackIndex, imageIndex, event.target.value)}" in source
    assert "value={setup.command}" in source
    assert 'value={setup.beforeImage?.name || ""}' in source
    # BEFORE_IMAGE + COMMAND are tucked into a collapsed (default) expander.
    assert '<details className="arc3-prolog-setup-extra">' in source
    assert "<summary>BEFORE_IMAGE &amp; COMMAND</summary>" in source
    # The expander stays collapsed by default: closed details hide their non-summary
    # children (author display:grid on the labels otherwise overrides the UA hiding).
    styles = STYLES.read_text(encoding="utf-8")
    assert ".arc3-prolog-setup-extra:not([open]) > *:not(summary)" in styles
    assert "display: none !important;" in styles


def test_b1_b2_setup_has_object_and_group_image_groups() -> None:
    source = COMPONENT.read_text(encoding="utf-8")
    # User-managed per-setup collections (images + file lists) share one generic,
    # field-keyed implementation.
    assert "objectImages?: ImageSelection[];" in source
    assert "groupImages?: ImageSelection[];" in source
    for field in ("plFiles", "engFiles", "jsonFiles", "mettaFiles", "promptFiles"):
        assert f"{field}?: ImageSelection[];" in source
    assert "type SetupCollectionField =" in source
    assert "const addSetupEntry = (stackIndex: number, imageIndex: number, field: SetupCollectionField) =>" in source
    assert "const setSetupEntryPath = (stackIndex: number, imageIndex: number, field: SetupCollectionField, entryIndex: number, path: string) =>" in source
    assert "const removeSetupEntry = (stackIndex: number, imageIndex: number, field: SetupCollectionField, entryIndex: number) =>" in source
    assert 'const renderSetupCollectionGroup = (field: SetupCollectionField, title: string, itemLabel: string, kind: "image" | "file", accept: string[]) =>' in source
    assert "`${title} (${entries.length})`" in source
    # Image groups render previews; file groups do not.
    assert 'renderSetupCollectionGroup("objectImages", "OBJ_IMAGES", "OBJECT", "image", [...IMAGE_SUFFIXES])' in source
    assert 'renderSetupCollectionGroup("groupImages", "GRP_IMAGES", "GROUP", "image", [...IMAGE_SUFFIXES])' in source
    assert 'renderSetupCollectionGroup("plFiles", "PL_FILES", "PL", "file", [".pl"])' in source
    assert 'renderSetupCollectionGroup("engFiles", "ENG_FILES", "ENG", "file", [".eng"])' in source
    assert 'renderSetupCollectionGroup("jsonFiles", "JSON_FILES", "JSON", "file", [".json"])' in source
    assert 'renderSetupCollectionGroup("mettaFiles", "METTA_FILES", "METTA", "file", [".metta"])' in source
    assert 'renderSetupCollectionGroup("promptFiles", "PROMPT_FILES", "PROMPT", "file", [".prompt"])' in source
    assert "OBJECT_IMAGES" not in source


def test_b1_b2_setup_group_rows_have_browse_buttons() -> None:
    source = COMPONENT.read_text(encoding="utf-8")
    styles = STYLES.read_text(encoding="utf-8")
    # Each collection row exposes a tiny [load] (native file dialog) then [select]
    # (workspace-file picker) pair to the right of the path input.
    assert "const [openBrowseKey, setOpenBrowseKey] = useState<string | null>(null);" in source
    assert 'const rowKey = `${field}:${setup.id}:${entryIndex}`;' in source
    assert 'title="Pick from workspace files"' in source
    assert "setOpenBrowseKey(openBrowseKey === rowKey ? null : rowKey)" in source
    assert 'title="Load a file from your computer"' in source
    assert 'accept={acceptAttr}' in source
    assert "webkitRelativePath" in source
    # [load] is rendered before [select].
    load_index = source.index('title="Load a file from your computer"')
    select_index = source.index(">select</button>")
    assert load_index < select_index
    # The [select] picker lists workspace files filtered by the group's accepted suffixes.
    assert "acceptLower.includes((file.suffix || \"\").toLowerCase())" in source
    assert "openBrowseKey === rowKey &&" in source
    assert "arc3-prolog-browse-option" in source
    assert "No matching workspace files" in source
    assert ".arc3-prolog-browse-inputwrap" in styles
    assert ".arc3-prolog-browse-list" in styles


def test_b1_b2_setup_text_files_group_renamed_unknown_files() -> None:
    source = COMPONENT.read_text(encoding="utf-8")
    assert "`UNKNOWN_FILES (${textFiles.length})`" in source
    assert "TEXT FILES (${textFiles.length})" not in source


def test_b1_b2_setup_sub_images_grouped_after_obj_images() -> None:
    source = COMPONENT.read_text(encoding="utf-8")
    obj_index = source.index('renderSetupCollectionGroup("objectImages", "OBJ_IMAGES"')
    sub_index = source.index("`SUB_IMAGES (${subimages.length})`")
    grp_index = source.index('renderSetupCollectionGroup("groupImages", "GRP_IMAGES"')
    assert obj_index < sub_index < grp_index
