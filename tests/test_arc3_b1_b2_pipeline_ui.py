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
    # Each collection row exposes a tiny [load] (native file dialog) then [select]
    # (workspace-file picker) pair to the right of the path input.
    assert "const [openBrowseKey, setOpenBrowseKey] = useState<string | null>(null);" in source
    assert 'const rowKey = `${field}:${setup.id}:${entryIndex}`;' in source
    assert 'title="Pick from workspace files"' in source
    assert "setOpenBrowseKey(openBrowseKey === rowKey ? null : rowKey)" in source
    assert 'title="Load a file from your computer"' in source
    assert 'accept={acceptAttr}' in source
    assert "relativeToSetupDir(picked.name)" in source
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
    # The member header shows Setup_N and an image/text-file count summary.
    assert "label={`Setup_${imageIndex + 1}`}" in source
    assert 'value={isActive ? "ACTIVE" : `Setup_${imageIndex + 1}`}' in source
    assert "detail={`${subimages.length} image(s) / ${textFiles.length} textual file(s)`}" in source
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
    assert "<summary>DIR &amp; PROPERTIES</summary>" in source
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
    assert source.index("<summary>DIR &amp; PROPERTIES</summary>") < source.index('className="arc3-prolog-setup-state-json"') < source.index("<summary>BEFORE &amp; COMMAND</summary>")
    # DIR & PROPERTIES sits at the top of each setup, before BEFORE & COMMAND.
    assert source.index("<summary>DIR &amp; PROPERTIES</summary>") < source.index("<summary>BEFORE &amp; COMMAND</summary>")


def test_b1_b2_setup_path_scan_writes_scan_results() -> None:
    source = COMPONENT.read_text(encoding="utf-8")
    # A [scan] button beside the DIR & PROPERTIES PATH input lists the files in that
    # directory and writes a scan.results object into the state.json editor.
    assert "const scanSetupStatePath = async (stackIndex: number, imageIndex: number, fallbackDir: string) =>" in source
    # Scan reads the PATH from the latest committed state (ref) so editing PATH then
    # scanning immediately uses the new value, not a stale render closure.
    assert "const liveSetup = stackColumnsRef.current?.[stackIndex]?.setups?.[imageIndex];" in source
    assert "normalizeAssetPath(liveSetup?.stateDir ?? fallbackDir)" in source
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
    # The scan merges into (rather than replaces) a parseable state.json document.
    assert "base.scan = { path: prefix, results };" in source
    assert "JSON.stringify(base, null, 2)" in source
    # The scan button lives inside the DIR & PROPERTIES expander, before PROP_FILE.
    assert source.index("<summary>DIR &amp; PROPERTIES</summary>") < source.index("arc3-prolog-setup-scan") < source.index("<span>PROP_FILE</span>")


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
    # Editor renders with Save/Close; [edit] loads content, [new] appends on save.
    assert "const renderFileEditor = (editorKey: string, onSaved: (path: string) => void) =>" in source
    assert 'className="secondary arc3-prolog-setup-editor-save"' in source
    assert 'className="secondary arc3-prolog-setup-editor-close"' in source
    assert "const ok = await saveDataFile(path, editorText);" in source
    assert "renderFileEditor(`edit:${field}:${setup.id}:${entryIndex}`," in source
    assert "renderFileEditor(`new:${field}:${setup.id}`, (path) => appendSetupEntryPath(stackIndex, imageIndex, field, path))" in source
    assert ".arc3-prolog-setup-file-editor" in styles


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
