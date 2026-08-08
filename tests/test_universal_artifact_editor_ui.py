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
        "MODEL / PROFILE DISPATCH",
        "PROMPT COMPOSITION",
        "Split view",
        "operation-document-tabs",
        "operation-tree-children",
        "echo_into_titlecased",
        "OperationPlayground",
    )
    for token in required:
        assert token in source, f"rich Operations baseline feature disappeared: {token}"


def test_operations_tree_supports_global_and_per_operation_folding() -> None:
    source = _text("OperationLibraryEditor.tsx")
    for token in (
        "Operations & implementations",
        "OPERATION CONTRACT SYSTEM",
        "collapsedOperations",
        "variantsHidden",
        "Only Toplevel",
        "Show Tree",
        'branchCollapsed?"Unhide Variants":"Hide Variants"',
        '<b>{branchCollapsed?"Unhide Variants":"Hide Variants"}</b>',
        "tree-branch-toggle",
        "branch-collapsed",
        "toggleTopLevel",
        "setCollapsedOperations(topLevel?new Set(operationIds):new Set())",
    ):
        assert token in source


def test_operation_playground_exposes_typed_inputs_variant_switching_and_results() -> None:
    source = _text("OperationPlayground.tsx")
    for token in (
        "OPERATION PLAYGROUND",
        "RUN VARIANT",
        "OUTPUT CONTRACT",
        "implementationVariant",
        "/invoke",
        "elapsedMs",
        "resolvedPrompts",
    ):
        assert token in source


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
        "variantsHidden",
        "variantsCollapsed",
        "Collapse hierarchy",
        "Expand hierarchy",
        "Only Toplevel",
        "Show Tree",
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
        assert "Show Parents" in source
        assert "useArtifactTreeFilter" in source
    assert "childBranchMatch" in filtering
    assert "head.hidden = !ownMatch && !showParents" in filtering
    assert "MutationObserver(applyFilter)" in filtering
    assert 'branch.dataset.filterOwnMatch = ownMatch ? "true" : "false"' in filtering
    assert "children: _children" in filtering
    assert "preferredChild: _preferredChild" in filtering
    assert "searchableData(branch)" in filtering
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
        assert "No Categories (All)" in source
        assert "Show Categories" in source
        assert "Only Categories" in source
        assert "Expand Categories" in source
    assert "showCategories" in category_tree
    assert "category-flat-all" in category_tree
    assert "branchCommand={categoryCommand}" in category_tree
    assert 'label="All" branchCommand={null}' in category_tree
    assert 'label="Uncategorized" branchCommand={null}' in category_tree
    assert "appearanceCategoryPath" in operations
    assert "operationBelongsHere" in operations
    assert "visibleVariants=categoryPath&&!operationBelongsHere" in operations
    assert "visibleVariants.map" in operations
