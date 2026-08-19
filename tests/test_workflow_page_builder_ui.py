from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "workbench/frontend/src/components/WorkflowPageBuilder.tsx"
SHELL = ROOT / "workbench/frontend/src/pages/FilesystemWorkbenchPage.tsx"
STYLES = ROOT / "workbench/frontend/src/styles/workflow_page_builder.css"


def test_workflow_page_builder_is_reachable_and_deep_linkable() -> None:
    shell = SHELL.read_text(encoding="utf-8")

    assert 'const WorkflowPageBuilder = lazy(() =>' in shell
    assert '| "workflowPageBuilder"' in shell
    assert 'label: "Page Builder", view: "workflowPageBuilder"' in shell
    assert 'value === "workflow-page-builder"' in shell
    assert 'view === "workflowPageBuilder"' in shell
    assert '<WorkflowPageBuilder initialDefinition={workflowNavigationEntries[0]?.definition}' in shell


def test_builder_parses_pasted_json_and_preserves_last_valid_preview() -> None:
    source = BUILDER.read_text(encoding="utf-8")

    assert "ResourceSourceEditor" in source
    assert 'label="Current page specification (MeTTa/JSON/Tree)"' in source
    assert "onValidityChange={setSourceValid}" in source
    assert "JSON.parse(source)" in source
    assert "function recoverDefinition" in source
    assert '(["left", "center", "right"] as const).map' in source
    assert "loadedDefinition" in source
    assert "The previous valid preview was preserved" in source
    assert '>CLEAR</button>' in source
    assert '>LOAD</button>' in source
    assert '>INIT</button>' in source
    assert "setInitialized(false)" in source
    assert "setInitialized(true)" in source
    assert "setSourceValid(true)" in source
    assert "and initialized components" in source
    assert "Page contents cleared. CURRENT PAGE SPECIFICATION remains ready" in source
    assert "Restore filesystem page" in source


def test_builder_recovers_bad_members_as_visible_error_components() -> None:
    source = BUILDER.read_text(encoding="utf-8")
    styles = STYLES.read_text(encoding="utf-8")

    assert "function errorMember" in source
    assert 'component: "WorkflowPageBuilderError"' in source
    assert "requires both id and component" in source
    assert "Duplicate ${columnId} columns; using the first" in source
    assert "RECOVERED COMPONENT ERROR" in source
    assert "recovered declaration error" in source
    assert ".workflow-page-builder-error" in styles


def test_builder_renders_every_declared_component_through_the_shared_host() -> None:
    source = BUILDER.read_text(encoding="utf-8")
    styles = STYLES.read_text(encoding="utf-8")

    assert "useMemo<WorkflowPageComponentRegistry>" in source
    assert "definition.layout.columns.forEach" in source
    assert "components.add" in source
    assert "Apply Component" in source
    assert "Apply Member JSON" in source
    assert "HEADER" in source
    assert "MEMBER JSON" in source
    assert "member JSON editor for ${member.id}" in source
    assert "header controls for ${member.id}" in source
    assert "itemHeader:" in source
    assert "workflow-page-builder-member-host" in source
    assert "workflow-page-builder-member-status" in source
    assert '<WorkflowPageHost definition={definition} componentRegistry={registry} deferComponentInitialization' in source
    assert "grid-template-columns: repeat(3" in styles
