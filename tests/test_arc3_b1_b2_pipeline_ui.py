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
    assert "return isB1B2PipelineRoute(routeView) ? 6 : 3;" in source
    assert 'const B1B2_RUNNER_NAMES = ["FIRST_GUESSER", "FIRST_REMOVER", "IMPROVED_GUESSER", "MERGE", "IMPROVED_REMOVER", "REGENERATOR"];' in source
    assert 'return pageDefinition.routeView === "arc3B1B2Pipeline" ? "IMPROVED_GUESSER" : "A1";' in source
    # Scatter-gather chain: FIRST_GUESSER -> FIRST_REMOVER -> IMPROVED_GUESSER -> MERGE -> IMPROVED_REMOVER -> REGENERATOR.
    assert 'if (runnerIndex === 0) return "guess";' in source
    assert 'if (runnerIndex === 1) return "removal";' in source
    assert 'if (runnerIndex === 2) return "extraction";' in source
    assert 'if (runnerIndex === 3) return "merge";' in source
    assert 'if (runnerIndex === 4) return "removal";' in source
    assert 'if (runnerIndex === 5) return "regenerated";' in source
    assert 'if (role === "extraction") return COMBINED_PROMPT;' in source
    assert 'if (role === "extraction") return "generate_prolog_and_english";' in source
    assert 'if (role === "merge") return "merge_identities";' in source
    assert "const MERGE_IDENTITIES_PROMPT = [" in source
    # Each B1B2 runner's prompt name is derived from the runner name: <RUNNER>_RUNNER_PROMPT.
    assert "${runnerDisplayId(routeView, stackKey, runnerIndex)}_RUNNER_PROMPT" in source
    assert '["runner:FIRST_GUESSER"]' in source
    assert '["runner:FIRST_REMOVER"]' in source
    assert '["runner:IMPROVED_GUESSER"]' in source
    assert '["runner:MERGE"]' in source
    # The remover extracts one leaf object (not nested), emits obj_<ID>.png, and mutates
    # the received document instead of regenerating an identity catalog.
    assert "SELECT ONE LEAF OBJECT THAT IS NOT INSIDE ANOTHER" in source
    assert "obj_<ID>.png" in source
    assert "DOCUMENT MUTATION" in source
    # Experimental write-back: REGENERATOR result can replace IMPROVED_GUESSER's list.
    assert "replaceGuesserOnFinish" in source
    assert "Replace IMPROVED_GUESSER list with this result on finish" in source
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


def test_b1_b2_first_guesser_single_image_first_pass() -> None:
    source = COMPONENT.read_text(encoding="utf-8")
    # A "FIRST_GUESSER" runner goes first in the 6-stage scatter-gather chain.
    assert 'const B1B2_RUNNER_NAMES = ["FIRST_GUESSER", "FIRST_REMOVER", "IMPROVED_GUESSER", "MERGE", "IMPROVED_REMOVER", "REGENERATOR"];' in source
    # The pipeline now has six runners in stack B.
    assert "return isB1B2PipelineRoute(routeView) ? 6 : 3;" in source
    # Roles: guess, removal, extraction, merge, removal, regenerated.
    assert 'if (runnerIndex === 0) return "guess";' in source
    assert 'if (runnerIndex === 1) return "removal";' in source
    assert 'if (runnerIndex === 2) return "extraction";' in source
    assert 'if (runnerIndex === 3) return "merge";' in source
    assert 'if (runnerIndex === 4) return "removal";' in source
    assert 'if (runnerIndex === 5) return "regenerated";' in source
    # Input: a single image, and no INPUT_FILES text sources.
    assert 'if (role === "guess") return [];' in source
    assert 'const guessRole = role === "guess";' in source
    assert "const image = guessRole" in source
    assert "Image #1 is the current ARC3 state; there is no parent image." in source
    # Output: only first_identities, via a dedicated lean prompt (not COMBINED_PROMPT).
    assert 'if (role === "guess") return "generate_first_pass_object_guesses";' in source
    assert 'if (role === "guess") return FIRST_PASS_OBJECT_GUESSES_PROMPT;' in source
    assert "const FIRST_PASS_OBJECT_GUESSES_PROMPT = [" in source
    assert "single required key: first_identities" in source
    assert "Return only first_identities in the JSON response." in source
    # The extraction runner (IMPROVED_GUESSER) consumes the removal pngs from FIRST_REMOVER.
    assert 'if (role === "extraction") return ["runner:FIRST_REMOVER"];' in source


def test_b1_b2_identity_records_require_pixel_count_and_colors_list() -> None:
    source = COMPONENT.read_text(encoding="utf-8")
    # Every identity record must carry pixel_count and colors_list across all identity-producing prompts.
    assert source.count("pixel_count") >= 3
    assert source.count("colors_list") >= 3
    # Full extraction (COMBINED_PROMPT) OUTPUT TYPES lists them.
    assert "Each identity must also include pixel_count" in source
    # First-pass guess prompt lists them.
    assert "pixel_count (an integer count of the logical grid cells the object occupies), and colors_list" in source
    # Merge prompt preserves/requires them.
    assert "Every merged identity must include pixel_count" in source


def test_b1_b2_loop_models_default_disabled() -> None:
    source = COMPONENT.read_text(encoding="utf-8")
    # Every B1B2 runner defaults its LOOP_MODEL (validator model) to Disabled.
    assert "validatorModelId: isB1B2PipelineRoute(routeView) ? RUNNER_VALIDATOR_DISABLED : RUNNER_VALIDATOR_PRIMARY_MODEL," in source
    assert 'const RUNNER_VALIDATOR_DISABLED = "__runner_validator_disabled__";' in source
    assert "<span>LOOP_MODEL</span>" in source
    assert "<option value={RUNNER_VALIDATOR_DISABLED}>Disabled</option>" in source
    # Every B1B2 runner also defaults its Loop/Validate Prompt to <disabled>.
    assert "validatorPromptName: isB1B2PipelineRoute(routeView) ? VALIDATOR_PROMPT_DISABLED : validatorPromptName(routeView, stackKey, runnerIndex)," in source
    assert 'const VALIDATOR_PROMPT_DISABLED = "__validator_prompt_disabled__";' in source
    assert "Loop/Validate Prompt" in source
    assert "<option value={VALIDATOR_PROMPT_DISABLED}>&lt;disabled&gt;</option>" in source


def test_b1_b2_input_files_combo_lists_all_setup_files() -> None:
    source = COMPONENT.read_text(encoding="utf-8")
    # The INPUT_FILES combo auto-populates with every file in column A (all setup collection files).
    assert "const SETUP_COLLECTION_FIELDS: SetupCollectionField[] = [" in source
    assert "SETUP_COLLECTION_FIELDS.flatMap((field) => (" in source
    assert "value: `setup-file:${setup.id}:${entry.name}`," in source
    # And the file-source resolver can resolve those collection-file tokens.
    assert "const entry = (setup[field] || []).find((file) => file.name === fileKey);" in source
    # It also lists every data/ file directly from the files prop (reliable, no scan needed).
    assert 'value: `data-file:${path}`,' in source
    assert 'const dataFileMatch = /^data-file:(.+)$/i.exec(trimmed);' in source
    # The combo prefers the full /data/files listing (which includes images) when available.
    assert "...(dataFiles.length ? dataFiles : files)" in source


def test_b1_b2_runner_submits_picked_image_and_tolerates_missing_frame() -> None:
    source = COMPONENT.read_text(encoding="utf-8")
    # A runner can submit an image picked in INPUT_FILES (data-file/setup-file image path).
    assert "if (path && /\\.(png|jpe?g|gif|webp|bmp)$/i.test(path)) return path;" in source
    assert "dataUrl: workspaceAssetUrl(workspaceId, pickedImagePath)" in source
    assert "const guessImageSource = pickedImage?.dataUrl" in source
    assert "const image = guessRole" in source
    assert "? guessImageSource" in source
    # The image validation frame no longer crashes the run when no image loads.
    assert ").catch(() => null);" in source
    assert "frame: ImageValidationFrame | null," in source
    # The full data listing (with images) is captured for the combo/image resolution.
    assert "setDataFiles(records);" in source
    # The guess image is encoded to a data: URL (via singleSheet) so the backend accepts it.
    assert "async function singleSheet(" in source
    assert 'return canvas.toDataURL("image/png");' in source
    assert "await singleSheet({ label: baseImageLabels.after, source: guessImageSource })" in source


def test_b1_b2_primary_prompt_combo_lists_all_prompts() -> None:
    source = COMPONENT.read_text(encoding="utf-8")
    # A canonical list of every B1B2 prompt (per-runner slots + content contracts) exists.
    assert "const B1B2_ALL_PRIMARY_PROMPT_NAMES = [" in source
    assert "...B1B2_RUNNER_NAMES.map((name) => `${name}_RUNNER_PROMPT`)," in source
    assert '"generate_first_pass_object_guesses",' in source
    assert '"merge_identities",' in source
    # The PRIMARY PROMPT combo includes that full list on the B1B2 route.
    assert "...(isB1B2PipelineRoute(pageDefinition.routeView) ? B1B2_ALL_PRIMARY_PROMPT_NAMES : [])," in source


def test_b1_b2_prompt_registry_is_typed_and_sorted_by_applicability() -> None:
    source = COMPONENT.read_text(encoding="utf-8")
    # A typed operation/implementation registry stores each implementation with
    # input/output types and tags; prompt implementations are derived by filtering.
    assert "type ImplementationDefinition = {" in source
    assert "const B1B2_IMPLEMENTATION_REGISTRY: ImplementationDefinition[] = [" in source
    assert 'const B1B2_PROMPT_REGISTRY = B1B2_IMPLEMENTATION_REGISTRY.filter((impl) => impl.kind === "prompt");' in source
    # Concrete + semantic type tags are used.
    for tag in ['"file_png"', '"file_json"', '"file_pl"', '"image"', '"object_identities"', '"first_identities"', '"removal_images"', '"regenerated_identities"']:
        assert tag in source
    # Each runner role has an input/output profile used for scoring applicability.
    assert "const B1B2_ROLE_PROFILE: Record<string, { inputs: PromptTypeTag[]; outputs: PromptTypeTag[] }>" in source
    assert "function promptApplicabilityScore(optionName: string, role: string): number {" in source
    # The combo is sorted by applicability (own runner slot first).
    assert "primaryPromptNameOptions.sort((left, right) => {" in source
    assert "promptApplicabilityScore(left, runnerRoleMode)" in source
    # Options are labeled with their input/output types.
    assert "function promptOptionLabel(optionName: string): string {" in source
    assert "promptOptionLabel(option)" in source


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
    assert 'value={setup.beforeImage?.name || "../image.png"}' in source
    # BEFORE_IMAGE + COMMAND are tucked into a collapsed (default) expander.
    assert '<details className="arc3-prolog-setup-extra">' in source
    assert "<summary>BEFORE &amp; COMMAND</summary>" in source
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
    # The "Add" entry button + its addSetupEntry handler were removed; entries are
    # populated by the disk scan / browse picker, not a manual add control.
    assert "const addSetupEntry =" not in source
    assert "const setSetupEntryPath = (stackIndex: number, imageIndex: number, field: SetupCollectionField, entryIndex: number, path: string) =>" in source
    assert "const removeSetupEntry = (stackIndex: number, imageIndex: number, field: SetupCollectionField, entryIndex: number) =>" in source
    assert "const renderSetupCollectionGroup = (" in source
    assert "options?: { defaultOpen?: boolean; derivedCount?: number; derived?: ReactNode; placeholder?: string; editable?: boolean }," in source
    assert "`${title} (${totalCount})`" in source
    # Image groups render previews; file groups do not. Each call now carries an
    # options object (defaultOpen/placeholder/editable), so match the call prefix.
    assert 'renderSetupCollectionGroup("objectImages", "OBJ_IMAGES", "OBJECT", "image", [...IMAGE_SUFFIXES], {' in source
    assert 'renderSetupCollectionGroup("groupImages", "GRP_IMAGES", "GROUP", "image", [...IMAGE_SUFFIXES], {' in source
    assert 'renderSetupCollectionGroup("plFiles", "PL_FILES", "PL", "file", [".pl"], {' in source
    assert 'renderSetupCollectionGroup("engFiles", "ENG_FILES", "ENG", "file", [".eng"], {' in source
    assert 'renderSetupCollectionGroup("jsonFiles", "JSON_FILES", "JSON", "file", [".json"], {' in source
    assert 'renderSetupCollectionGroup("mettaFiles", "METTA_FILES", "METTA", "file", [".metta"], {' in source
    assert 'renderSetupCollectionGroup("promptFiles", "PROMPT_FILES", "PROMPT", "file", [".prompt"], {' in source
    assert "OBJECT_IMAGES" not in source


def test_b1_b2_setup_group_rows_have_browse_buttons() -> None:
    source = COMPONENT.read_text(encoding="utf-8")
    styles = STYLES.read_text(encoding="utf-8")
    # Each collection row exposes [load/edit] (editable only) then [select]
    # (workspace-file picker) then [browse] (native file dialog).
    assert "const [openBrowseKey, setOpenBrowseKey] = useState<string | null>(null);" in source
    assert 'const rowKey = `${field}:${setup.id}:${entryIndex}`;' in source
    assert 'title="Pick from workspace files"' in source
    assert "setOpenBrowseKey(openBrowseKey === rowKey ? null : rowKey)" in source
    assert 'title="Browse for a file on your computer"' in source
    assert 'accept={acceptAttr}' in source
    assert "relativeToSetupDir(picked.name)" in source
    # Row order is [Select] then [Browse]; the first three buttons are capitalized.
    assert ">Load/Edit</button>" in source
    assert ">Select</button>" in source
    assert "Browse</label>" in source or 'title="Browse for a file on your computer"' in source
    select_index = source.index(">Select</button>")
    browse_index = source.index('title="Browse for a file on your computer"')
    assert select_index < browse_index
    # The per-row item label is derived from the entry filename (dots -> underscores),
    # e.g. differences.pl -> differences_pl, falling back to "<Label> <n>" when empty.
    assert "const entryBase = normalizeAssetPath(entry.name).split(\"/\").pop() || \"\";" in source
    assert "const entryLabel = entryBase ? entryBase.replace(/\\./g, \"_\") : `${itemLabel} ${entryIndex + 1}`;" in source
    assert "<span>{entryLabel}{entryLineCount !== undefined ? ` (~${entryLineCount} lines)` : \"\"}</span>" in source
    # The [select] picker lists workspace files filtered by the group's accepted suffixes.
    assert "acceptLower.includes((file.suffix || \"\").toLowerCase())" in source
    assert "openBrowseKey === rowKey &&" in source
    assert "arc3-prolog-browse-option" in source
    assert "No matching workspace files" in source
    assert ".arc3-prolog-browse-inputwrap" in styles
    assert ".arc3-prolog-browse-list" in styles


def test_b1_b2_setup_groups_have_group_load_select() -> None:
    source = COMPONENT.read_text(encoding="utf-8")
    styles = STYLES.read_text(encoding="utf-8")
    # Every collection group has a group-level [load]/[select] footer that appends
    # a new entry (from the local file dialog or the workspace picker).
    assert "const appendSetupEntryPath = (stackIndex: number, imageIndex: number, field: SetupCollectionField, path: string) =>" in source
    assert "const addKey = `${field}:${setup.id}:__add`;" in source
    assert 'className="arc3-prolog-object-image-actions"' in source
    assert "appendSetupEntryPath(stackIndex, imageIndex, field, relativeToSetupDir(picked.name))" in source
    assert "setOpenBrowseKey(openBrowseKey === addKey ? null : addKey)" in source
    assert "openBrowseKey === addKey &&" in source
    assert "appendSetupEntryPath(stackIndex, imageIndex, field, path)" in source
    assert ".arc3-prolog-object-image-actions" in styles


def test_b1_b2_setup_text_files_group_renamed_unknown_files() -> None:
    source = COMPONENT.read_text(encoding="utf-8")
    assert 'renderSetupCollectionGroup("unknownFiles", "UNKNOWN_FILES", "UNKNOWN", "file", []' in source
    assert "TEXT FILES (${textFiles.length})" not in source
    # The derived text outputs are still shown inside the group.
    assert "derivedCount: textFiles.length," in source


def test_b1_b2_setup_sub_images_grouped_after_obj_images() -> None:
    source = COMPONENT.read_text(encoding="utf-8")
    obj_index = source.index('renderSetupCollectionGroup("objectImages", "OBJ_IMAGES"')
    sub_index = source.index('renderSetupCollectionGroup("subImages", "SUB_IMAGES"')
    grp_index = source.index('renderSetupCollectionGroup("groupImages", "GRP_IMAGES"')
    # Image groups are ordered OBJ, then GRP, then SUB.
    assert obj_index < grp_index < sub_index


def test_b1_b2_setup_header_and_before_after_controls() -> None:
    source = COMPONENT.read_text(encoding="utf-8")
    # Setups group by their root folder; each name begins with the folder right below
    # data (e.g., data/1l111/Level_1 -> "1l111.Level_1").
    assert "const setupLocalLabel = setupRoot && rawSetupLabel !== setupRoot && !rawSetupLabel.startsWith(`${setupRoot}.`)" in source
    assert "label={setupLocalLabel}" in source
    assert 'value={isActive ? `${setupLocalLabel} · ACTIVE` : setupLocalLabel}' in source
    assert "const setupGroups: Array<{ groupName: string; items: Array<{ setup: StackSetup; imageIndex: number }> }> = [];" in source
    assert "<ThreeStateAccordionStack id={groupStackId}" in source
    assert "detail={`Images (${setupImageCount}) NonImages (${setupNonImageCount})`}" in source
    # BEFORE and AFTER each expose a single-image [load]/[select] pair.
    assert "const renderSingleImageControls = (browseKey: string, setter: (path: string) => void) =>" in source
    assert "const renderSingleImageList = (browseKey: string, setter: (path: string) => void) =>" in source
    assert "renderSingleImageControls(`before:${setup.id}`, (path) => setBeforeImagePath(stackIndex, imageIndex, path))" in source
    assert "renderSingleImageList(`before:${setup.id}`, (path) => setBeforeImagePath(stackIndex, imageIndex, path))" in source
    assert "renderSingleImageControls(`after:${setup.id}`, (path) => setImagePath(stackIndex, imageIndex, path))" in source
    assert "renderSingleImageList(`after:${setup.id}`, (path) => setImagePath(stackIndex, imageIndex, path))" in source
    # File groups carry placeholders and are flagged editable for the [edit]/[new] phase.
    assert "placeholder: `${pathPrefix}/*.pl`," in source
    assert "editable: true," in source


def test_b1_b2_setup_has_no_properties_editor() -> None:
    source = COMPONENT.read_text(encoding="utf-8")
    styles = STYLES.read_text(encoding="utf-8")
    # The per-setup key/value PROPERTIES editor has been removed entirely.
    assert "type SetupProperty = {" not in source
    assert "properties?: SetupProperty[];" not in source
    assert "addSetupProperty" not in source
    assert "setSetupProperty" not in source
    assert "removeSetupProperty" not in source
    assert "`PROPERTIES (${(setup.properties || []).length})`" not in source
    assert ">Add property</button>" not in source
    assert ".arc3-prolog-property-fields" not in styles


def test_b1_b2_setup_has_no_add_buttons() -> None:
    source = COMPONENT.read_text(encoding="utf-8")
    # All "[ Add xxx ]" controls were removed; setups/runners/entries are populated
    # by the disk scan and browse pickers instead of manual add buttons.
    assert ">Add Image</button>" not in source
    assert ">Add Runner</button>" not in source
    assert "`Add ${itemLabel.toLowerCase()}`" not in source
    assert "const addImage =" not in source
    assert "const addRunner =" not in source
    assert "const addSetupEntry =" not in source


def test_b1_b2_setup_has_dir_properties_node() -> None:
    source = COMPONENT.read_text(encoding="utf-8")
    styles = STYLES.read_text(encoding="utf-8")
    # Per-setup state fields + a single setter.
    assert "stateDir?: string;" in source
    assert "stateFile?: string;" in source
    assert "stateJson?: string;" in source
    assert 'const setSetupStateField = (stackIndex: number, imageIndex: number, field: "stateDir" | "stateFile" | "stateJson", value: string) =>' in source
    # A default-collapsed DIR & PROPERTIES node (reuses the setup-extra collapse behavior).
    assert 'className="arc3-prolog-setup-extra arc3-prolog-setup-dir-props"' in source
    assert "DIR &amp; PROPERTIES" in source
    # PATH + PROP_FILE (state.json) fields and an editable JSON textarea below.
    assert "<span>PATH</span>" in source
    assert 'placeholder="data/level_1/LEFT"' in source
    assert "<span>PROP_FILE</span>" in source
    assert 'value={setup.stateFile ?? "state.json"}' in source
    assert 'className="arc3-prolog-setup-state-json"' in source
    assert 'setSetupStateField(stackIndex, imageIndex, "stateJson", event.target.value)' in source
    assert ".arc3-prolog-setup-state-json" in styles
    # The JSON editor loads the contents of <PATH>/<PROP_FILE> from the workspace.
    assert "const loadSetupStateJson = async (stackIndex: number, imageIndex: number, dir: string, fileName: string) =>" in source
    assert "fetch(workspaceAssetUrl(workspaceId, rel)" in source
    assert 'loadSetupStateJson(stackIndex, imageIndex, setup.stateDir ?? stateDirDefault, setup.stateFile ?? "state.json")' in source
    # Load button carries no filename in its label; a Save as.. button sits beside it.
    assert ">Load</button>" in source
    assert "Load {(setup.stateFile ?? " not in source
    assert ">Save as..</button>" in source
    assert "const saveSetupStateJson = async (fileName: string, content: string) =>" in source
    assert 'saveSetupStateJson(setup.stateFile ?? "state.json", setup.stateJson ?? "")' in source
    assert "showSaveFilePicker" in source
    assert ".arc3-prolog-setup-state-actions" in styles
    # The editor is hidden inside the DIR & PROPERTIES expander (before BEFORE & COMMAND).
    assert source.index("DIR &amp; PROPERTIES") < source.index('className="arc3-prolog-setup-state-json"') < source.index("<summary>BEFORE &amp; COMMAND</summary>")
    # DIR & PROPERTIES sits at the top of each setup, before BEFORE & COMMAND.
    assert source.index("DIR &amp; PROPERTIES") < source.index("<summary>BEFORE &amp; COMMAND</summary>")


def test_b1_b2_setup_path_scan_writes_scan_results() -> None:
    source = COMPONENT.read_text(encoding="utf-8")
    # A [scan] button beside the DIR & PROPERTIES PATH input lists the files in that
    # directory and writes a scan.results object into the state.json editor.
    assert "const scanSetupStatePath = async (stackIndex: number, imageIndex: number, fallbackDir: string, prefetched?: WorkspaceFileRecord[], persist = false) =>" in source
    # Scan reads the PATH from the latest committed state (ref) so editing PATH then
    # scanning immediately uses the new value, not a stale render closure.
    assert "const liveSetup = stackColumnsRef.current?.[stackIndex]?.setups?.[imageIndex];" in source
    assert "liveSetup?.stateDir ?? fallbackDir" in source
    assert 'className="secondary arc3-prolog-browse-btn arc3-prolog-setup-scan"' in source
    assert "scanSetupStatePath(stackIndex, imageIndex, setup.stateDir ?? stateDirDefault)" in source
    # Fresh listing (with a files-prop fallback), scoped to direct children of PATH.
    assert "/data/files" in source
    assert 'if (!candidate.startsWith(`${prefix}/`)) return false;' in source
    assert "return !candidate.slice(prefix.length + 1).includes" in source
    # Categorized result buckets.
    for bucket in (
        "obj_images",
        "grp_images",
        "sub_images",
        "pl_files",
        "eng_files",
        "json_files",
        "metta_files",
        "prompt_files",
        "unknown_files",
    ):
        assert f"{bucket}:" in source or f"results.{bucket}.push" in source
    assert 'if (name.startsWith("obj")) results.obj_images.push(candidate);' in source
    assert 'else if (name.startsWith("grp")) results.grp_images.push(candidate);' in source
    # ENG uses a *eng* filename mask (matches e.g. .english), checked after the specific
    # suffixes and just before the unknown fallthrough.
    assert 'else if (name.includes("eng")) results.eng_files.push(candidate);' in source
    assert source.index("results.prompt_files.push") < source.index('name.includes("eng")') < source.index("results.unknown_files.push")
    # The scan merges into (rather than replaces) a parseable state.json document.
    assert "base.scan = { path: prefix, results };" in source
    assert "JSON.stringify(base, null, 2)" in source
    # The scan button lives inside the DIR & PROPERTIES expander, before PROP_FILE.
    assert source.index("DIR &amp; PROPERTIES") < source.index("arc3-prolog-setup-scan") < source.index("<span>PROP_FILE</span>")
    # A scan button also sits on the DIR & PROPERTIES summary itself, so you can scan
    # without expanding the panel; clicking it must not toggle the <details>.
    assert 'className="secondary arc3-prolog-browse-btn arc3-prolog-setup-scan arc3-prolog-setup-scan-summary"' in source
    assert "event.preventDefault();" in source
    assert "event.stopPropagation();" in source


def test_b1_b2_setup_command_and_groups_hydrate_from_state() -> None:
    source = COMPONENT.read_text(encoding="utf-8")
    # The command is derived from the node's action: explicit command, else action_directory
    # (e.g. DOWN), else observation.action_input.id (e.g. RESET for a level's reset node).
    assert "const commandFromParsedState = (parsed: Record<string, unknown>): string | undefined =>" in source
    assert "const actionDir = parsed.action_directory;" in source
    assert "const actionInput = (observation as Record<string, unknown>).action_input;" in source
    assert "const command = commandFromParsedState(base);" in source
    # Loading a setup's state.json hydrates its file groups from the persisted scan.results,
    # so README.md (an unknown file) shows in UNKNOWN_FILES without needing a fresh scan.
    assert "const applyScanResultsToSetup = (stackIndex: number, imageIndex: number, results: Record<string, unknown>) =>" in source
    assert "unknownFiles: toEntries(asPaths(results.unknown_files))," in source
    assert "applyScanResultsToSetup(stackIndex, imageIndex, results as Record<string, unknown>);" in source


def test_b1_b2_setup_path_has_workspace_folder_browse() -> None:
    source = COMPONENT.read_text(encoding="utf-8")
    # A [browse] button beside the PATH input opens a picker of existing data/ folders.
    assert "const pathBrowseKey = `path:${setup.id}`;" in source
    assert "setOpenBrowseKey(openBrowseKey === pathBrowseKey ? null : pathBrowseKey)" in source
    assert "openBrowseKey === pathBrowseKey && <div className=\"arc3-prolog-browse-list\">" in source
    # Folder options are derived from workspace files (dirs under data/, numeric-aware).
    assert "const workspaceDirs = (() => {" in source
    assert '/^data(\\/|$)/i.test(dir)' in source
    assert '{ numeric: true }' in source
    # Picking a folder sets the setup's PATH (stateDir) and closes the list.
    assert 'setSetupStateField(stackIndex, imageIndex, "stateDir", dir);' in source
    assert "No workspace folders" in source
    # The browse button sits between the PATH input and the scan button.
    assert source.index(">browse</button>") < source.index("arc3-prolog-setup-scan\"")


def test_b1_b2_setups_enumerate_all_data_folders() -> None:
    source = COMPONENT.read_text(encoding="utf-8")
    # Setups are the LEAF directories of the data/ tree (walk each trail down to a folder
    # with no child directories; that leaf is one setup).
    assert "const compareByTree = (left: string, right: string) =>" in source
    assert "^data\\/level_1(?:" not in source
    assert "const isLeaf = (dir: string) => !dirs.some((other) => other !== dir && other.startsWith(`${dir}/`));" in source
    assert "if (!isLeaf(dir)) continue;" in source
    # Only trails passing through a level* folder become setups.
    assert "const hasLevelSegment = (dir: string) => relPath(dir).split(\"/\").some((seg) => /^level/i.test(seg));" in source
    assert "if (!hasLevelSegment(dir)) continue;" in source
    # exports/histories bookkeeping folders and any dot-directory are skipped by the scan.
    assert 'const SCAN_IGNORED_DIR_NAMES = new Set(["exports", "histories"]);' in source
    assert "!hasIgnoredScanSegment(entry.p)" in source
    assert 'seg.startsWith(".") || SCAN_IGNORED_DIR_NAMES.has(seg.toLowerCase())' in source
    # Deep leaves are grouped by their root folder; the trail below the root is the command.
    assert "const group = segments[0] || relPath(dir);" in source
    assert "setupEntries.push({ dir, group, command });" in source
    assert "command ?? setupCommandFromPath(`${dir}/frame`)" in source
    # Numeric-aware ordering (level_10 after level_1); each leaf's label is the dotted path.
    assert "{ numeric: true }" in source
    assert 'const dottedName = relPath(dir).split("/").filter(Boolean).map((seg, index) => index === 0 ? seg : abbreviateSegment(seg)).join(".");' in source
    assert 'label: dottedName || group || "default",' in source
    # Each setup's PATH is its own folder; the default/initial setup points to level_1.
    assert 'stateDir: "data/level_1",' in source
    assert "stateDir: dir," in source
    assert 'label: "default.Setup_0",' in source


def test_b1_b2_setups_auto_scan_on_create() -> None:
    source = COMPONENT.read_text(encoding="utf-8")
    # Each newly created setup is auto-scanned once (guarded by a ref) using a single
    # shared /data/files fetch passed to scanSetupStatePath as prefetched records.
    assert "const autoScannedSetupsRef = useRef<Set<string>>(new Set());" in source
    assert "if (autoScannedSetupsRef.current.has(setup.id)) return;" in source
    assert "autoScannedSetupsRef.current.add(setup.id);" in source
    assert "prefetched?: WorkspaceFileRecord[]" in source
    assert "let records: WorkspaceFileRecord[] = prefetched ?? files;" in source
    assert "await scanSetupStatePath(stackIndex, imageIndex, fallbackDir, records);" in source


def test_b1_b2_setup_scans_on_open() -> None:
    source = COMPONENT.read_text(encoding="utf-8")
    # Opening a setup (leaving strip mode) scans it once if it has not been scanned yet.
    assert "const openScannedSetupsRef = useRef<Set<string>>(new Set());" in source
    assert "if (!openScannedSetupsRef.current.has(setup.id)) {" in source
    assert "openScannedSetupsRef.current.add(setup.id);" in source
    assert 'void scanSetup(stackIndex, imageIndex, setup.stateDir || "");' in source


def test_b1_b2_setup_file_rows_show_non_blank_line_count() -> None:
    source = COMPONENT.read_text(encoding="utf-8")
    # File rows append the file's non-blank line count after the name label.
    assert "const [lineCounts, setLineCounts] = useState<Record<string, number>>({});" in source
    # Line counts are fetched in one batched request (not one asset fetch per file).
    assert "const loadLineCounts = async (paths: string[], force = false) =>" in source
    assert "/data/line-counts`" in source
    assert 'method: "POST"' in source
    assert "void loadLineCounts(paths);" in source
    # Line counts are lazy: only fetched when the user opens a setup (mode != strip).
    assert "const loadLineCountsForSetup = (setup: StackSetup) =>" in source
    assert 'if (mode !== "strip") {' in source
    assert "loadLineCountsForSetup(setup);" in source
    assert "const entryLineCount = kind === \"file\" ? lineCounts[entryPath] : undefined;" in source
    assert "<span>{entryLabel}{entryLineCount !== undefined ? ` (~${entryLineCount} lines)` : \"\"}</span>" in source
    # File-group summaries total the per-file line counts (~N lines).
    assert "const groupLineTotal = kind === \"file\"" in source
    assert "`${title} (${totalCount}) ~${groupLineTotal} lines`" in source
    # Counts are refreshed after an in-place editor save.
    assert "void loadLineCounts([path], true);" in source


def test_b1_b2_setup_expand_button_opens_non_empty_groups() -> None:
    source = COMPONENT.read_text(encoding="utf-8")
    # An [expand] button next to [scan] on the DIR & PROPERTIES summary opens every
    # non-empty file group. Group open state is controlled so it can be driven.
    assert "const [groupOpen, setGroupOpen] = useState<Record<string, boolean>>({});" in source
    assert "const groupKey = `${field}:${setup.id}`;" in source
    assert "const groupIsOpen = groupOpen[groupKey] ?? ((options?.defaultOpen ?? true) && totalCount > 0);" in source
    assert "open={groupIsOpen}" in source
    assert "const expandNonEmptyGroups = () =>" in source
    assert "if (count > 0) next[`${groupField}:${setup.id}`] = true;" in source
    assert 'className="secondary arc3-prolog-browse-btn arc3-prolog-setup-scan-summary arc3-prolog-setup-expand-summary"' in source
    assert "expandNonEmptyGroups();" in source
    # The expand button sits on the summary, after the scan button.
    assert source.index("arc3-prolog-setup-scan-summary arc3-prolog-setup-expand-summary") > source.index("arc3-prolog-setup-scan arc3-prolog-setup-scan-summary")


def test_b1_b2_setup_scan_populates_collection_fields() -> None:
    source = COMPONENT.read_text(encoding="utf-8")
    # [scan] populates the file silos below (not just the state.json editor), so images
    # render: it maps each result bucket into the setup's collection fields.
    assert "const toEntries = (paths: string[]) => paths.map((path) => imageSelectionFromPath(workspaceId, path" in source
    for field, bucket in (
        ("objectImages", "obj_images"),
        ("groupImages", "grp_images"),
        ("subImages", "sub_images"),
        ("plFiles", "pl_files"),
        ("engFiles", "eng_files"),
        ("jsonFiles", "json_files"),
        ("mettaFiles", "metta_files"),
        ("promptFiles", "prompt_files"),
        ("unknownFiles", "unknown_files"),
    ):
        assert f"{field}: toEntries(results.{bucket})," in source


def test_b1_b2_setup_load_uses_setup_relative_path() -> None:
    source = COMPONENT.read_text(encoding="utf-8")
    # [load] picks a local file and stores the path relative to the setup's dir
    # (setupDir/basename), rather than the bare name or webkitRelativePath.
    assert "const relativeToSetupDir = (fileName: string) =>" in source
    assert "return cleanStateDir ? `${cleanStateDir}/${base}` : base;" in source
    assert "setter(relativeToSetupDir(picked.name))" in source
    assert "setSetupEntryPath(stackIndex, imageIndex, field, entryIndex, relativeToSetupDir(picked.name))" in source
    assert "appendSetupEntryPath(stackIndex, imageIndex, field, relativeToSetupDir(picked.name))" in source
    # The old webkitRelativePath-or-name behavior is gone.
    assert "relative || picked.name" not in source


def test_b1_b2_file_groups_have_edit_new_editors() -> None:
    source = COMPONENT.read_text(encoding="utf-8")
    styles = STYLES.read_text(encoding="utf-8")
    # Single-open editor state.
    assert "const [openEditorKey, setOpenEditorKey] = useState<string | null>(null);" in source
    assert "const [editorText, setEditorText] = useState" in source
    assert "const [editorName, setEditorName] = useState" in source
    # Raw-write handler with download fallback, targeting the verbatim data-file endpoint.
    assert "const saveDataFile = async (path: string, content: string): Promise<boolean> =>" in source
    assert "/data-file`" in source
    assert 'method: "PUT"' in source
    assert "const downloadTextFallback = (fileName: string, content: string) =>" in source
    # [edit] per row + [new] in the footer, both gated on the editable option.
    assert "options?.editable && <button" in source
    assert 'className="secondary arc3-prolog-browse-btn arc3-prolog-setup-edit"' in source
    assert 'className="secondary arc3-prolog-browse-btn arc3-prolog-setup-new"' in source
    assert "void openEntryEditor(field, entryIndex, entry.name)" in source
    assert "openNewEditor(field, `${pathPrefix}/untitled${accept[0] ?? \".txt\"}`)" in source
    # Editor renders with Save/Save-as/Close on one line with the FILE path input;
    # [edit] loads content, [new] appends on save.
    assert "const renderFileEditor = (editorKey: string, onSaved: (path: string) => void) =>" in source
    assert 'className="arc3-prolog-setup-file-editor-head"' in source
    assert "arc3-prolog-setup-editor-save" in source
    assert "arc3-prolog-setup-editor-saveas" in source
    assert "arc3-prolog-setup-editor-close" in source
    assert "const saveTextFileAs = async (fileName: string, content: string) =>" in source
    assert "void saveTextFileAs(editorName, editorText)" in source
    assert "showSaveFilePicker" in source
    # Each editable row also exposes a [Save as..] that downloads the file's content.
    assert "const saveEntryFileAs = async (path: string) =>" in source
    assert 'className="secondary arc3-prolog-browse-btn arc3-prolog-setup-entry-saveas"' in source
    assert "void saveEntryFileAs(entry.name)" in source
    assert "const ok = await saveDataFile(path, editorText);" in source
    assert "renderFileEditor(`edit:${field}:${setup.id}:${entryIndex}`," in source
    assert "renderFileEditor(`new:${field}:${setup.id}`, (path) => appendSetupEntryPath(stackIndex, imageIndex, field, path))" in source
    assert ".arc3-prolog-setup-file-editor" in styles
    assert ".arc3-prolog-setup-file-editor-head" in styles
    # .md files get a live markdown preview rendered with the app's ReactMarkdown + GFM.
    assert "import ReactMarkdown from \"react-markdown\";" in source
    assert "import remarkGfm from \"remark-gfm\";" in source
    assert "/^.+\\.md$/i.test(editorName.trim())" in source
    assert "<ReactMarkdown remarkPlugins={[remarkGfm]}>{editorText}</ReactMarkdown>" in source
    assert ".arc3-prolog-md-preview" in styles


def test_b1_b2_columns_are_resizable() -> None:
    source = COMPONENT.read_text(encoding="utf-8")
    styles = STYLES.read_text(encoding="utf-8")
    # Columns get draggable splitters via the host's columnsRef/columnsStyle/columnsOverlay
    # extension points, adjusting an inline grid-template-columns on drag.
    assert "const columnsElRef = useRef<HTMLDivElement | null>(null);" in source
    assert "const [columnTemplate, setColumnTemplate] = useState<string | null>(null);" in source
    assert "const startColumnResize = (index: number, event: { clientX: number; preventDefault: () => void }) =>" in source
    assert "columnRef={columnsElRef}" in source or "columnsRef={columnsElRef}" in source
    assert "...(columnTemplate ? { gridTemplateColumns: columnTemplate } : {})" in source
    assert 'className="arc3-b1b2-col-resizer"' in source
    assert "onPointerDown={(event) => startColumnResize(index, event)}" in source
    # Adjacent columns trade width; a minimum width is enforced.
    assert "const minWidth = 220;" in source
    assert ".arc3-b1b2-page .arc3-b1b2-col-resizer" in styles


def test_b1_b2_buttons_have_readable_theme() -> None:
    source = COMPONENT.read_text(encoding="utf-8")
    styles = STYLES.read_text(encoding="utf-8")
    # The shared .primary/.secondary chrome is scoped to other pages, so this page
    # themes its own buttons; otherwise they fall back to the UA light-grey default
    # (light text on a near-white background = invisible).
    assert ".arc3-prolog-page-panel button.secondary" in styles
    assert ".arc3-prolog-page-panel button.primary" in styles
    assert ".arc3-prolog-page-panel button.arc3-prolog-browse-btn" in styles
    assert ".arc3-prolog-page-panel label.arc3-prolog-browse-btn" in styles
    assert ".arc3-prolog-page-panel button.arc3-prolog-active-toggle" in styles
    # The active setup toggle carries a real class (not an empty string) so it can be
    # styled as a selected/accent state.
    assert 'className={isActive ? "arc3-prolog-active-toggle" : "secondary"}' in source
    assert 'className={isActive ? "" : "secondary"}' not in source
