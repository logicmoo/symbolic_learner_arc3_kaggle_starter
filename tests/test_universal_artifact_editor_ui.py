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


def test_tasks_preserve_rich_baseline_features() -> None:
    source = _text("TaskLibraryEditor.tsx")
    required = (
        "DEFAULT IMPLEMENTATION",
        "PYTHON SOURCE",
        "SWI-PROLOG SOURCE",
        "METTA SOURCE",
        "MODEL / PROFILE DISPATCH",
        "PROMPT COMPOSITION",
        "Split view",
        "task-document-tabs",
        "task-tree-children",
        "echo_into_titlecased",
        "TaskPlayground",
    )
    for token in required:
        assert token in source, f"rich Tasks baseline feature disappeared: {token}"


def test_operations_tree_supports_global_and_per_operation_folding() -> None:
    source = _text("TaskLibraryEditor.tsx")
    for token in (
        "collapsedTasks",
        "Only Toplevel",
        "Show Tree",
        'branchCollapsed?"Unhide Variants":"Hide Variants"',
        "tree-branch-toggle",
        "branch-collapsed",
    ):
        assert token in source


def test_task_playground_exposes_typed_inputs_variant_switching_and_results() -> None:
    source = _text("TaskPlayground.tsx")
    for token in (
        "TASK PLAYGROUND",
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


def test_universal_shell_keeps_tabs_compare_inspector_and_docks() -> None:
    source = _text("UniversalArtifactEditor.tsx")
    for token in (
        "artifact-breadcrumb",
        "artifact-common-inspector",
        "task-document-tabs",
        "task-editor-panes",
        "compareKey",
        "bottomPanels",
        "artifact-bottom-dock",
        "variantControls",
        "navigatorCollapsed",
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
    styles = (ROOT / "workbench" / "frontend" / "src" / "styles" / "task_editor.css").read_text(encoding="utf-8")
    assert 'aria-expanded={!navigatorCollapsed}' in source
    assert "navigator-collapsed" in source
    assert ".artifact-navigator-content" in styles
    assert "overflow-y:auto" in styles
    assert "scrollbar-gutter:stable" in styles
    assert ".task-hierarchy-layout.navigator-collapsed" in styles
    assert ".variants-collapsed .task-tree-children" in styles
    assert ".variants-collapsed .inheritance-children" in styles
    assert ".main-stage>.task-hierarchy-page" in styles
    assert "overflow-y:scroll" in styles
    workbench_styles = (ROOT / "workbench" / "frontend" / "src" / "styles" / "workbench.css").read_text(encoding="utf-8")
    assert ".main-stage{min-height:0;overflow:hidden}" in workbench_styles
