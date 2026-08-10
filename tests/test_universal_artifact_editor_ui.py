from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPONENTS = ROOT / "workbench" / "frontend" / "src" / "components"


def _text(name: str) -> str:
    return (COMPONENTS / name).read_text(encoding="utf-8")


def test_universal_editor_keeps_compatibility_chrome_for_adapted_panels() -> None:
    universal = _text("UniversalArtifactEditor.tsx")
    compatibility = _text("HierarchyResourceEditor.tsx")
    assert 'UNIVERSAL_ARTIFACT_EDITOR_BASELINE = "current-rich-editor"' in universal
    assert "UniversalArtifactEditor as HierarchyResourceEditor" in compatibility
    for component in (
        "DataCatalogPanel.tsx",
        "PromptLibraryEditor.tsx",
        "LlmModelsEditor.tsx",
    ):
        source = _text(component)
        assert 'from "./HierarchyResourceEditor"' in source or 'from "./UniversalArtifactEditor"' in source


def test_operations_preserve_rich_baseline_features() -> None:
    source = _text("OperationLibraryEditor.tsx")
    required = (
        "DEFAULT IMPLEMENTATION",
        "PYTHON SOURCE",
        "SWI-PROLOG SOURCE",
        "METTA SOURCE",
        "MODEL / PRESET DISPATCH",
        "PROMPT COMPOSITION",
        "Split view",
        "operation-document-tabs",
        "operation-tree-children",
        "echo_into_titlecased",
        "OperationPlayground",
    )
    for token in required:
        assert token in source, f"rich Operations baseline feature disappeared: {token}"


def test_prompt_profiles_are_independent_editable_operation_bindings() -> None:
    prompts = _text("PromptLibraryEditor.tsx")
    operations = _text("OperationLibraryEditor.tsx")
    for token in (
        'kind:"prompt_profile"',
        "+ Prompt profile",
        "PROMPT PROFILE",
        "Choose and order the semantic prompts this profile contributes",
        "promptProfiles",
    ):
        assert token in prompts
    for token in (
        "PROMPT PROFILES",
        "selectedPromptProfiles",
        "togglePromptProfile",
        "promptLibrary?.hierarchy?.promptProfiles",
    ):
        assert token in operations


def test_operations_tree_supports_global_and_per_operation_folding() -> None:
    source = _text("OperationLibraryEditor.tsx")
    for token in (
        "Operations & implementations",
        "OPERATION CONTRACT SYSTEM",
        "collapsedOperations",
        'branchCollapsed?"Unhide Variants":"Hide Variants"',
        '<b>{branchCollapsed?"Unhide Variants":"Hide Variants"}</b>',
        "tree-branch-toggle",
        "branch-collapsed",
        "commandOperations",
        'commandBranches("collapse","all")',
    ):
        assert token in source
    assert "TreeViewControls" in source
    assert "RepeatSwitch" in source
    assert 'commandBranches("expand","all")' in source
    assert 'document.enabled===false?"Enable Resource":"Disable Resource"' in source


def test_every_generic_resource_source_is_enableable() -> None:
    source = _text("ResourceSourceEditor.tsx")
    assert "showEnablement = true" in source
    assert 'resource?.enabled !== false' in source
    assert 'enabled }, null, 2' in source
    assert '"Disable Resource":"Enable Resource"' in source
    assert "showEnablement={false}" in _text("LlmModelsEditor.tsx")


def test_operation_playground_exposes_typed_inputs_variant_switching_and_results() -> None:
    source = _text("OperationPlayground.tsx")
    for token in (
        "OPERATION PLAYGROUND",
        "RUN WITH (THIS RUN ONLY)",
        "OUTPUT CONTRACT",
        "implementationVariant",
        "/invoke",
        "elapsedMs",
        "resolvedPrompts",
        'type="checkbox"',
        'type="number"',
        "example?.options",
        'accept="image/*"',
        "readAsDataURL",
        "Operation input preview",
    ):
        assert token in source


def test_operation_playground_formats_structured_datatype_contracts() -> None:
    source = _text("OperationPlayground.tsx")
    assert "type DatatypeContract=string|Record<string,unknown>" in source
    assert "function datatypeLabel(contract:DatatypeContract)" in source
    assert "contract.representation" in source
    assert "datatypeLabel(datatype)" in source
    assert source.index("if(isTextDatatype(datatype))return <textarea") < source.index(
        'if(/image|bitmap|png|jpe?g/i.test(datatype))return <div className="operation-image-input"'
    )


def test_operation_playground_offers_automatic_llm_fallback() -> None:
    source = _text("OperationPlayground.tsx")
    assert ".automatic_llm_fallback" in source
    assert "Automatic LLM fallback (openrouter/free)" in source
    assert "const concreteVariants=variants.length?variants:direct?[direct]:[]" in source
    assert "const runnableVariants=[...concreteVariants,fallback]" in source
    assert "RUN WITH (THIS RUN ONLY)" in source
    assert "The saved default implementation is unchanged" in source


def test_operation_playground_can_run_default_and_populate_from_runtime_artifacts() -> None:
    source = _text("OperationPlayground.tsx")
    assert "Run Default" in source
    assert "Run Selected" in source
    controls = _text("UniversalExecutionControls.tsx")
    assert '"last_outputs"' in controls
    assert '"random_outputs"' in controls
    assert '"sample_input"' in controls
    assert '"empty_null"' in controls
    assert 'className="operation-run-route"' in source
    assert 'className="operation-run-actions"' in source
    assert "/api/engine/runs?workspace_id=${encodeURIComponent(workspaceId)}&limit=100" in source
    assert "/api/goal-runs?workspace_id=" in source
    assert "artifactScore" in source
    assert "valueShapeMatches" in source
    assert 'if(actualAny&&!valueShapeMatches(expected,artifact.value))return 0' in source
    assert 'return typeof value==="string"' in source
    assert "type RuntimeValueDictionary=" in source
    assert "byDatatype:Map" in source
    assert "byRepresentation:Map" in source
    assert "byName:Map" in source
    assert "workspaceValueBanks" in source
    assert "rememberInvocation" in source
    assert "const pool=dictionary.any" in source
    assert 'rememberInvocation(workspaceId,operation,' in source
    assert "POPULATE INPUTS" in controls
    assert "Last Output" in controls
    assert "Random Output" in controls
    assert "outputs produced by any operation in this workspace" in source
    assert "chosen.operationLabel" in source
    assert "Sample's Input" in controls
    assert "Empty/Null" in controls
    assert "implementationVariant?{implementationVariant}" in source


def test_operation_playground_displays_persisted_complete_debug_trace() -> None:
    source = (ROOT / "workbench/frontend/src/components/OperationPlayground.tsx").read_text(encoding="utf-8")
    trace_viewer = (ROOT / "workbench/frontend/src/components/InvocationDebugTrace.tsx").read_text(encoding="utf-8")
    assert "<InvocationDebugTrace" in source
    assert "COMPLETE DEBUG TRACE" in trace_viewer
    assert "collectStringBlocks" in trace_viewer
    assert 'aria-label="Debug trace views"' in trace_viewer
    assert "/operations/debug-log?path=" in source
    assert "debugLogPath" in source


def test_operation_playground_runs_direct_routes_and_accepts_plain_any_values() -> None:
    source = _text("OperationPlayground.tsx")
    editor = _text("OperationLibraryEditor.tsx")
    assert "operation.implementation?" in source
    assert "direct?[direct]:[]" in source
    assert 'if(/^any$/i.test(datatype.trim()))' in source
    assert '"Enter text or a JSON value…"' in source
    assert "Direct — {directRoute}" in editor


def test_other_artifact_families_keep_their_variant_controls() -> None:
    assert "PREFERRED REPRESENTATION" in _text("DataCatalogPanel.tsx")
    assert "PREFERRED ALTERNATIVE" in _text("PromptLibraryEditor.tsx")
    models = _text("LlmModelsEditor.tsx")
    assert "INHERITS FROM" in models
    assert "RESOLVED INHERITANCE" in models
    for component in ("DataCatalogPanel.tsx", "PromptLibraryEditor.tsx", "GoalPlanLibraryEditor.tsx", "LlmModelsEditor.tsx"):
        assert "ArtifactTreeBranch" in _text(component)


def test_universal_shell_keeps_tabs_compare_inspector_and_docks() -> None:
    source = _text("UniversalArtifactEditor.tsx")
    for token in (
        "artifact-breadcrumb",
        "artifact-common-inspector",
        "operation-document-tabs",
        "operation-editor-panes",
        "compareKey",
        "bottomPanels",
        "artifact-bottom-dock",
        "variantControls",
        "navigatorCollapsed",
        "visibilityRules",
        "TreeViewControls",
        "Collapse hierarchy",
        "Expand hierarchy",
        "Expand All",
        "Collapse All",
        "artifact-navigator-content",
    ):
        assert token in source


def test_universal_tree_is_collapsible_and_independently_scrollable() -> None:
    source = _text("UniversalArtifactEditor.tsx")
    styles = (ROOT / "workbench" / "frontend" / "src" / "styles" / "operation_editor.css").read_text(encoding="utf-8")
    assert 'aria-expanded={!navigatorCollapsed}' in source
    assert "navigator-collapsed" in source
    assert ".artifact-navigator-content" in styles
    assert "overflow-y:auto" in styles
    assert "scrollbar-gutter:stable" in styles
    assert ".operation-hierarchy-layout.navigator-collapsed" in styles
    assert ".variants-collapsed .operation-tree-children" in styles
    assert ".variants-collapsed .inheritance-children" in styles
    assert ".variants-hidden .operation-tree-children" in styles
    assert ".main-stage>.operation-hierarchy-page" in styles
    assert "overflow-y:scroll" in styles
    workbench_styles = (ROOT / "workbench" / "frontend" / "src" / "styles" / "workbench.css").read_text(encoding="utf-8")
    assert ".main-stage{min-height:0;overflow:hidden}" in workbench_styles


def test_all_artifact_trees_share_filter_and_parent_path_controls() -> None:
    universal = _text("UniversalArtifactEditor.tsx")
    operations = _text("OperationLibraryEditor.tsx")
    filtering = _text("useArtifactTreeFilter.ts")
    for source in (universal, operations):
        assert "Filter tree…" in source
        assert "useArtifactTreeFilter" in source
    assert "Parent" in _text("TreeViewControls.tsx")
    assert "TreeViewControls" in operations
    assert "descendantVisible" in filtering
    assert "info.head.hidden = !showParents" in filtering
    assert "MutationObserver(applyFilter)" in filtering
    assert "children: _children" in filtering
    assert "preferredChild: _preferredChild" in filtering
    assert "searchableData(element)" in filtering
    assert "dataset.treeSearch" in filtering
    assert "searchValue" in _text("ArtifactTreeBranch.tsx")
    for component in ("OperationLibraryEditor.tsx", "DataCatalogPanel.tsx", "PromptLibraryEditor.tsx", "GoalPlanLibraryEditor.tsx", "LlmModelsEditor.tsx"):
        assert "tree-search" in _text(component) or "searchValue" in _text(component)
    styles = (ROOT / "workbench" / "frontend" / "src" / "styles" / "operation_editor.css").read_text(encoding="utf-8")
    assert '[data-filter-own-match="false"]>.inheritance-row' in styles


def test_design_trees_share_virtual_categories() -> None:
    category_tree = _text("CategorizedArtifactTree.tsx")
    universal = _text("UniversalArtifactEditor.tsx")
    operations = _text("OperationLibraryEditor.tsx")
    for token in ('label="All"', 'label="Uncategorized"', 'split("/")', "categoryPaths", "CategorizedArtifactTree"):
        assert token in category_tree or token in operations
    assert "CategorizedArtifactNodes" in universal
    assert "CategorizedArtifactTree items={categorizedOperations}" in operations
    assert "variant.document?.categories" in operations
    for source in (universal, operations):
        assert "No Categories (All)" not in source
        assert "Show Categories" not in source
        assert "Expand Categories" not in source
    assert "Only Categories" not in universal
    assert "Only Categories" not in operations
    assert "onlyCategories" in category_tree
    assert "!onlyCategories&&" not in category_tree
    assert 'data-category-collapse-mode={onlyCategories ? "resources" : "none"}' in category_tree
    assert "branchCommand={categoryCommand}" in category_tree
    assert 'label="All" branchCommand={null}' in category_tree
    assert 'label="Uncategorized" branchCommand={null}' in category_tree
    assert "appearanceCategoryPath" in operations
    assert "operationBelongsHere" in operations
    assert "visibleVariants=categoryPath&&!operationBelongsHere" in operations
    assert "visibleVariants.map" in operations


def test_universal_tree_exposes_composable_tri_state_view_controls() -> None:
    universal = _text("UniversalArtifactEditor.tsx")
    controls = _text("TreeViewControls.tsx")
    filtering = _text("useArtifactTreeFilter.ts")
    styles = (ROOT / "workbench/frontend/src/styles/operation_editor.css").read_text(encoding="utf-8")
    assert 'TreeVisibilityRule = "show" | "hide" | "unspecified"' in filtering
    assert 'TreeRepeatMode = "first" | "all" | "last"' in filtering
    assert "groupAllows" in filtering
    assert "availabilityStates" in filtering
    assert "activeRules.search === \"show\"" in filtering
    assert "activeRules.search === \"unspecified\"" in filtering
    assert "LEGACY_FILTERING_RULES" in filtering
    assert ".operation-tree-row.operation-child" in filtering
    assert "nestedKinds" in filtering
    assert "treeKinds" in filtering
    assert "[...current, ...kinds]" in filtering
    assert "repeatedPositions" in filtering
    assert 'activeRules.repeats === "first"' in filtering
    for label in ('label="Search"', 'label="All"', "Enabled", "Disabled", "Categories", "Non-"):
        assert label in controls
    assert 'aria-label="Repeated resources"' in controls
    assert "tree-repeat-permanent" in universal
    assert "RepeatSwitch value={visibilityRules.repeats}" in universal
    assert '`top-${kind}`' in controls
    assert '`child-${kind}`' in controls
    assert '`childless-${kind}`' in controls
    assert "Childless ${plural(title(kind))}" in controls
    assert "setAll" in controls
    assert "roleKeys.map(key => [key, value])" in controls
    assert 'aria-label="Tree View Controls"' in controls
    assert "useState(true)" in universal
    assert 'aria-label="Tree View Controls"' in universal
    assert 'viewControlsOpen ? "Hide View" : "Show View"' in universal
    assert "updateVisibilityRules" in universal
    assert 'commandCategories("expand");commandTree("expand")' in universal
    assert 'commandTree("collapse");commandCategories("collapse")' in universal
    assert ".tree-view-controls" in styles
    assert ".tree-rule-switch" in styles
    assert ".tree-control-band" in styles
    assert "onBranchAction(\"expand\", \"disabled\")" in controls
    assert "onBranchAction(\"collapse\", \"all\")" in controls
    branch = _text("ArtifactTreeBranch.tsx")
    assert 'command.target === "disabled"' in branch
    assert 'command.target === "search"' in branch
    assert "values.some(value => states[value] === \"hide\")" in filtering


def test_first_class_categories_are_visually_distinct_from_virtual_folders() -> None:
    category_tree = _text("CategorizedArtifactTree.tsx")
    styles = (ROOT / "workbench" / "frontend" / "src" / "styles" / "operation_editor.css").read_text(encoding="utf-8")
    assert '"First-class category" : "Virtual category"' in category_tree
    assert 'firstClass ? "category-first-class" : "category-virtual"' in category_tree
    assert "/artifact-categories" in category_tree
    assert "document.trees?.includes(categoryTree)" in category_tree
    assert ".operation-category-row.category-first-class" in styles
    assert "var(--green)" in styles


def test_operation_implementations_inherit_parent_playground() -> None:
    operations = _text("OperationLibraryEditor.tsx")
    playground = _text("OperationPlayground.tsx")
    assert "parentOperation=selectedImplementation" in operations
    assert "relationshipIds(selectedImplementation.parents)" in operations
    assert "selectedImplementation&&parentOperation&&<OperationPlayground" in operations
    assert "variants={[selectedImplementation]}" in operations
    assert "runnableVariants.some(item=>item.id===operation.preferredChild)" in playground
    assert "invocationVariant=runnableVariants.length===1?runnableVariants[0].id:variant" in playground
    assert "run(invocationVariant)" in playground
    assert "implementationVariant?{implementationVariant}" in playground
    assert "disabled={runnableVariants.length===1}" in playground
