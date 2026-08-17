from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_workflow_actions_are_stacked_above_preflight_and_columns() -> None:
    source = (ROOT / "workbench" / "frontend" / "src" / "pages" / "FilesystemWorkbenchPage.tsx").read_text(encoding="utf-8")
    actions = source.index('label="ENGLISH SPECIFICATION EDITOR"')
    preflight = source.index("<WorkflowPreflightSpline")
    columns = source.index('label="LEFT + RIGHT"')
    assert actions < preflight < columns
    assert 'workflow?.generation?.operation || "workflow.populate_from_english"' in source
    assert "workflowAuthoringOperations" in source
    assert 'aria-label="Editable English workflow description"' in source
    assert "saveWorkflowEnglishDescription" in source
    assert "These come from current startup inputs and generated step outputs—not from the English description." in source
    assert "inferred startup input" in source
    assert "inferred step output" in source
    assert "Current/default value" in source
    assert "effective_operation_catalog:operationLibrary.operations" in source
    assert 'expectedInputNames={["english_specification","effective_operation_catalog","workflow_schema"]}' in source
    assert "new_memory_values_plan" in source
    assert "Authoring output is missing the combined new_memory_values_plan.values array." in source
    generate_section = source[source.index('label="GENERATE DRAFT"'):source.index('label="VALIDATION RESULTS"')]
    assert "<OperationPlayground" in generate_section
    assert "models={workflowRunnerModels}" in generate_section
    assert "setWorkflowRunnerModels" in source
    assert '/models`)' in source
    assert 'setView("operations")' not in generate_section
    assert "showDesignReference={false}" in source
    assert "<WorkflowRunnerTodoReference displayMode={workflowReferenceDisplayMode}" in source
    assert source.index('label="LEFT + RIGHT"') < source.index("<WorkflowRunnerTodoReference displayMode={workflowReferenceDisplayMode}")
    reference = (ROOT / "workbench" / "frontend" / "src" / "components" / "WorkflowRunnerTodoReference.tsx").read_text(encoding="utf-8")
    assert 'stackId="center-stack" initialIndex={7} label="RUNNER DESIGN REFERENCE"' in reference
    for label in (
        "ENGLISH SPECIFICATION EDITOR",
        "MEMORY / VALUE PLAN",
        "GENERATE DRAFT",
        "VALIDATION RESULTS",
        "APPLY TO WORKFLOW",
    ):
        assert label in source
    assert 'label="MODEL AND OUTPUT FORMAT"' not in source
    assert 'filter(([input])=>input!=="workspace_root")' in source


def test_workflow_actions_default_to_top_but_remain_draggable() -> None:
    source = (ROOT / "workbench" / "frontend" / "src" / "components" / "ThreeStateAccordion.tsx").read_text(encoding="utf-8")
    page = (ROOT / "workbench" / "frontend" / "src" / "pages" / "FilesystemWorkbenchPage.tsx").read_text(encoding="utf-8")
    assert '<ThreeStateAccordionStack id="center-stack" controlsLabel="CENTER STACK">' in page
    assert 'stackId="center-stack" initialIndex={0} label="ENGLISH SPECIFICATION EDITOR"' in page
    assert 'stackId="center-stack" initialIndex={4} label="APPLY TO WORKFLOW"' in page
    assert "accordion-order-initial-placement" in source
    assert "draggable={managedOrder === undefined}" in source
    assert 'managedOrder === undefined ? `Drag to reorder or click to cycle ${label}` : `Click to cycle ${label}`' in source
    assert 'item !== "LEFT + RIGHT"' not in source
    assert 'label !== "LEFT + RIGHT"' not in source


def test_workflow_authoring_members_are_owned_by_the_accordion_stack() -> None:
    page = (ROOT / "workbench" / "frontend" / "src" / "pages" / "FilesystemWorkbenchPage.tsx").read_text(encoding="utf-8")
    section = page[page.index('<ThreeStateAccordionStack id="center-stack" controlsLabel="CENTER STACK">'):page.index("<WorkflowPreflightSpline")]
    assert section.count('stackId="center-stack"') == 5
    assert "workflow-authoring-${operation.id}" not in section
    assert "memoryStackId" not in section
    assert "workflow-authoring-rich-runner" not in section


def test_workflow_runner_is_first_in_the_left_stack() -> None:
    launcher = (ROOT / "workbench" / "frontend" / "src" / "components" / "DurableRunLauncher.tsx").read_text(encoding="utf-8")
    runtime = (ROOT / "workbench" / "frontend" / "src" / "components" / "RuntimeHistoryView.tsx").read_text(encoding="utf-8")
    page = (ROOT / "workbench" / "frontend" / "src" / "pages" / "FilesystemWorkbenchPage.tsx").read_text(encoding="utf-8")
    assert 'stackId="left-stack"' in launcher
    assert "initialIndex={0}" in launcher
    assert 'initialPlacementVersion="runner-first-v1"' in launcher
    assert 'document.querySelector(\'[data-accordion-stack="left-stack"]:not([data-accordion-member])\')' in runtime
    assert "left-durable-run-launcher-slot" not in page


def test_workflow_page_has_only_center_left_and_right_stacks() -> None:
    page = (ROOT / "workbench" / "frontend" / "src" / "pages" / "FilesystemWorkbenchPage.tsx").read_text(encoding="utf-8")
    runtime = (ROOT / "workbench" / "frontend" / "src" / "components" / "RuntimeHistoryView.tsx").read_text(encoding="utf-8")
    assert '<ThreeStateAccordionStack id="center-stack" controlsLabel="CENTER STACK">' in page
    assert '<ThreeStateAccordionStack id="left-stack"' in page
    assert '<ThreeStateAccordionStack id="right-stack"' in runtime
    assert 'label="LEFT + RIGHT"' in page
    assert 'baseClass="workflow-columns-stack-member"' in page
    assert 'baseClass="workflow-columns-stack-control"' not in page
    assert "ref={setWorkflowColumnsHost}" in page
    assert "createPortal(" in page
    assert "workflowColumnsHost" in page
    assert "spline-stack" not in page
    assert "workflow-authoring-workflow.populate_from_english" not in page
    assert "workflow-authoring-workflow.populate_from_english-memory-values" not in page


def test_center_stack_has_one_native_control_for_all_members() -> None:
    accordion = (ROOT / "workbench" / "frontend" / "src" / "components" / "ThreeStateAccordion.tsx").read_text(encoding="utf-8")
    page = (ROOT / "workbench" / "frontend" / "src" / "pages" / "FilesystemWorkbenchPage.tsx").read_text(encoding="utf-8")
    assert 'controlsLabel="CENTER STACK"' in page
    assert "publishAccordionMode(id, mode)" in accordion
    assert "Array.from(accordionModeListeners.get(stackId)" in accordion
    assert "Set every member in this stack" in accordion
    assert "<ThreeStateAccordionControls label={controlsLabel}" in accordion


def test_count_to_ten_declares_editable_english_description() -> None:
    workspace = ROOT / "workbench" / "workspaces" / "generate_count_to_ten"
    workflow = (workspace / "design" / "workflows" / "generate_count_to_ten.workflow.metta").read_text(encoding="utf-8")
    assert "englishDescriptionPath docs/WORKFLOW_DESCRIPTION.md" in workflow
    assert (workspace / "docs" / "WORKFLOW_DESCRIPTION.md").is_file()


def test_english_workflow_prompts_require_complete_single_resource_and_operation_prototypes() -> None:
    prompt_root = ROOT / "workbench" / "workspaces" / "shared_library_system" / "design" / "prompts"
    for name in ("generate_workflow_from_english.json.prompt.metta", "generate_workflow_from_english.metta.prompt.metta"):
        source = (prompt_root / name).read_text(encoding="utf-8")
        assert "full operation prototypes" in source or "operation prototypes" in source
        assert "typed inputs" in source
        assert "typed outputs" in source
        assert "one complete" in source
        assert "value.compare" in source
