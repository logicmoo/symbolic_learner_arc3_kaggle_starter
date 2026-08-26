import json
from pathlib import Path

from operation_api import invoke_operation
from resource_store import get_filesystem_provider


ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "workbench/frontend/src/components/VisualImageDiffPage.tsx"
SHELL = ROOT / "workbench/frontend/src/pages/FilesystemWorkbenchPage.tsx"
MANIFEST = ROOT / "workbench/workspaces/arc3_random_player/design/visual_image_diffs/default.visual_image_diff.json"
PROMPTS = ROOT / "workbench/workspaces/shared_library_arc3/design/prompts/visual_image_diff_steps.prompt.metta"
ASSETS = ROOT / "workbench/workspaces/arc3_random_player/runtime/artifacts/visual_image_diff"
PAGE_DEFINITION = ROOT / "workbench/workspaces/arc3_random_player/design/workflow_pages/visual_sequencing.workflow_page.json"


def test_visual_image_diff_is_a_deep_linked_three_structural_stack_page() -> None:
    page = PAGE.read_text(encoding="utf-8")
    shell = SHELL.read_text(encoding="utf-8")

    definition = PAGE_DEFINITION.read_text(encoding="utf-8")
    assert '"id": "arc3.visual_sequencing"' in definition
    assert '"label": "Visual Sequencing"' in definition
    assert '"renderer": "visual_image_diff"' in definition
    assert 'workflowNavigationEntries.map' in shell
    assert 'workflowPageForView.renderer === "visual_image_diff"' in shell
    assert 'value === "visual-image-diff"' in shell
    assert '<WorkflowPageHost' in page
    assert 'componentRegistry={componentRegistry}' in page
    assert 'stackIdForColumn={(column) => `visual-image-diff-${column.id}-stack`}' in page
    assert 'freezeColumnControls' in page


def test_visual_image_diff_stacks_separate_data_authoring_and_source_details() -> None:
    definition = json.loads(PAGE_DEFINITION.read_text(encoding="utf-8"))
    columns = {column["id"]: column for column in definition["layout"]["columns"]}

    assert [column["id"] for column in definition["layout"]["columns"]] == ["left", "center", "right"]
    assert [member["component"] for member in columns["left"]["members"]] == [
        "VisualResourceOutputs", "ImageCommandSequence", "VisualSequenceContext",
    ]
    assert [member["component"] for member in columns["center"]["members"]] == [
        "VisualPipelineSubaccordion", "SelectedOperationPlayground",
    ]
    assert [member["component"] for member in columns["right"]["members"]] == [
        "ResourceSourceEditor",
        "ComposedGroupPrompt",
        *("VisualPromptInspector" for _ in range(11)),
    ]

    prompt_members = [
        member for member in columns["right"]["members"]
        if member["component"] == "VisualPromptInspector"
    ]
    assert [member["options"]["promptId"] for member in prompt_members] == [
        "visual_image_diff.pipeline.source",
        "visual_image_diff.pipeline.normalize",
        "visual_image_diff.pipeline.objects",
        "visual_image_diff.pipeline.sync_representations",
        "visual_image_diff.pipeline.render_turtle",
        "visual_image_diff.pipeline.display",
        "visual_image_diff.pipeline.compare",
        "visual_image_diff.pipeline.rules",
        "visual_image_diff.pipeline.cherry_pick",
        "visual_image_diff.pipeline.validate",
        "visual_image_diff.pipeline.report",
    ]
    assert [member["label"] for member in prompt_members] == [
        "Pipeline — Grab Image Source",
        "Pipeline — Normalize Image Collection",
        "Pipeline — Extract Individual Objects",
        "Pipeline — Synchronize Object Representations",
        "Pipeline — Render Turtle Objects",
        "Pipeline — Display Rendered Images",
        "Pipeline — Compare Scene Objects",
        "Pipeline — Induce Transition Rules",
        "Pipeline — Prolog Cherry-Pick Evidence",
        "Pipeline — Validate Artifact Bundle",
        "Pipeline — Publish Workflow Report",
    ]

    page = PAGE.read_text(encoding="utf-8")
    assert "<ResourceSourceEditor" in page
    assert "promptDrafts[prompt.id]" in page
    assert "Save Prompt" in page
    assert "/prompts/${encodeURIComponent(prompt.id)}" in page
    assert "editablePromptSource(prompt)" in page


def test_operation_playground_pulls_declared_inputs_from_left_stack_data() -> None:
    page = PAGE.read_text(encoding="utf-8")

    assert "function operationInputValues" in page
    assert '"current_image"' in page
    assert '"previous_image"' in page
    assert '"source_manifest"' in page
    assert '"sequence_context"' in page
    assert "const availableData = useMemo<Record<string, unknown>>" in page
    assert "const inputValues = operationInputValues(operation, availableData)" in page
    assert "inputValues={inputValues}" in page
    assert "expectedInputNames={Object.keys(inputValues)}" in page
    assert "onInvocationComplete={onInvocationComplete}" in page
    assert "setWorkflowData((current) => ({ ...current, ...nextOutputs }))" in page
    assert 'aria-label="Workflow data available to later steps"' in page


def test_visual_image_diff_columns_start_center_weighted_and_have_persistent_drag_boundaries() -> None:
    page = PAGE.read_text(encoding="utf-8")
    visual_styles = (ROOT / "workbench/frontend/src/styles/visual_image_diff.css").read_text(encoding="utf-8")

    assert "DEFAULT_VISUAL_COLUMN_RATIOS: VisualColumnRatios = { left: 1, center: 2.8, right: 1.9 }" in page
    assert 'VISUAL_COLUMN_RATIOS_STORAGE = "workbench.visualImageDiff.columnRatios.v2"' in page
    assert 'columnsRef={columnsRef}' in page
    assert 'columnsClassName="visual-image-diff-columns"' in page
    assert 'columnsStyle={columnGridStyle}' in page
    assert page.count('className="visual-image-diff-column-divider"') == 2
    assert 'aria-label="Resize data and authoring columns"' in page
    assert 'aria-label="Resize authoring and source detail columns"' in page
    assert 'onPointerDown={(event) => beginColumnResize("left", event)}' in page
    assert 'onPointerDown={(event) => beginColumnResize("right", event)}' in page
    assert page.count("onDoubleClick={() => setColumnRatios(DEFAULT_VISUAL_COLUMN_RATIOS)}") == 2
    assert 'window.addEventListener("pointermove", onPointerMove)' in page
    assert 'window.localStorage.setItem(VISUAL_COLUMN_RATIOS_STORAGE' in page
    assert "minmax(280px, var(--visual-image-center-width, 2.8fr))" in visual_styles
    assert "minmax(220px, var(--visual-image-right-width, 1.9fr))" in visual_styles
    assert ".visual-image-diff-column-divider" in visual_styles
    assert "cursor: col-resize" in visual_styles
    assert "@media (max-width: 1180px)" in visual_styles
    assert "display: none" in visual_styles


def test_sequence_comes_from_a_manifest_and_workspace_assets() -> None:
    page = PAGE.read_text(encoding="utf-8")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    assert manifest["kind"] == "visual_image_diff"
    assert manifest["id"] == "arc3.action3_then_action1"
    assert [command["label"] for command in manifest["commands"]] == ["ACTION3", "ACTION1"]
    assert len(manifest["frames"]) == 3
    for frame in manifest["frames"]:
        assert (ROOT / "workbench/workspaces/arc3_random_player" / frame["assetPath"]).is_file()
    assert "/asset?path=" in page
    assert "ACTION3" not in page
    assert "ACTION1" not in page


def test_initial_visual_pipeline_starts_with_the_image_pair_and_command_group() -> None:
    page = PAGE.read_text(encoding="utf-8")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    groups = manifest["promptGroups"]

    assert manifest["runtimeWorkflowId"] == "free_staged_symbolic_analysis"
    assert [group["transaction"] for group in groups] == [
        "inspect_image_pair_command",
        "render_and_display_objects",
        "explain_object_changes",
        "induce_rules_from_prolog",
        "audit_artifact_bundle",
    ]
    assert [group["operation"] for group in groups] == [
        "vision.extract_scene_objects",
        "vision.extract_scene_objects",
        "symbolic.explain_object_changes",
        "symbolic.induce_rules",
        "artifact.audit_bundle",
    ]
    assert groups[0]["implementation"] == "vision.extract_scene_objects.automatic_llm"
    assert all("profile" not in group for group in groups)
    assert [len(group["prompts"]) for group in groups] == [3, 3, 2, 1, 2]
    assert sum(len(group["prompts"]) for group in groups) == 11
    assert groups[0]["label"] == "IMAGE PAIR + COMMAND"
    assert groups[0]["focalGroup"] == "source_scene"
    assert [group["colorKey"] for group in groups] == ["S1", "S2", "S3", "S4", "S5"]
    assert 'fields.set("image_pair"' in page
    assert 'fields.set("transition_command"' in page
    assert "nextDocument.promptGroups" in page
    assert "setGenerationOrder(groupedEntries.length ? groupedEntries" in page
    assert "Restore profile groups" in page


def test_expanded_transaction_groups_embed_the_real_workflow_item_operation_debugger() -> None:
    page = PAGE.read_text(encoding="utf-8")
    shell = SHELL.read_text(encoding="utf-8")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    system_operation_root = ROOT / "workbench/workspaces/shared_library_system/design/operations"
    arc3_operation_root = ROOT / "workbench/workspaces/shared_library_arc3/design/operations"

    operation_files = {
        "vision.extract_scene_objects": system_operation_root / "vision.extract_scene_objects.operation.metta",
        "symbolic.explain_object_changes": system_operation_root / "symbolic.explain_object_changes.operation.metta",
        "symbolic.get_prolog_evidence": arc3_operation_root / "symbolic.get_prolog_evidence.operation.metta",
        "symbolic.induce_rules": system_operation_root / "symbolic.induce_rules.operation.metta",
        "artifact.audit_bundle": system_operation_root / "artifact.audit_bundle.operation.metta",
    }
    for group in manifest["promptGroups"]:
        source = operation_files[group["operation"]].read_text(encoding="utf-8")
        assert f"(id {group['operation']})" in source

    assert 'import {\n  OperationPlayground,' in page
    assert 'operationId: group.operation' in page
    assert 'aria-label={`${title} workflow item and Operation playground`}' in page
    assert 'const groupHeaderActions = isGroup ? <div className="generation-order-group-actions visual-image-diff-subaccordion-header-actions">' in page
    assert 'itemHeader={isGroup ? groupHeaderActions : null}' in page
    assert 'stripContent={(cycleMode) => <div className={`visual-image-diff-subaccordion-strip-control ${isGroup ? "group" : "prompt"} ${parentGroupId ? "nested" : "top-level"}`}' in page
    assert 'aria-label={`Select group ${ordinal} for insertion in subaccordion`}' in page
    assert 'aria-label={`Copy group ${ordinal} in subaccordion`}' in page
    assert 'aria-label={`Shuffle group ${ordinal} in subaccordion`}' in page
    assert 'aria-label={`Clear group ${ordinal} in subaccordion`}' in page
    assert 'footer={playgroundFooter}' in page
    assert 'const playgroundFooter = isGroup ?' in page
    assert 'aria-expanded={playgroundOpen}' in page
    assert '>INPUT / OUTPUT</button>' in page
    assert '>RUN GROUP</button>' in page
    assert '{isGroup && <div className="visual-image-diff-subaccordion-group-body">' in page
    assert 'from subaccordion">▶' not in page
    assert "WORKFLOW ITEM + PROMPT PLAYGROUND" in page
    assert "WORKFLOW ITEM + NON-PROMPT OPERATION PLAYGROUND" in page
    assert "PROMPT RESOURCES EXECUTED BY THIS VERSION" in page
    assert "It makes no Prompt or LLM request." in page
    assert '<OperationPlayground' in page
    assert 'workflowStep={workflowStepFor(entry, operation)}' in page
    assert 'onWorkflowStepChange={(workflowStep) => onWorkflowStep(entry.id, workflowStep)}' in page
    assert 'operationImplementations.filter' in page
    assert 'onImplementationVariantChange={(implementationId) => onImplementation(entry.id, implementationId)}' in page
    assert 'operations={operationLibrary.operations.flatMap' in shell
    assert 'operationImplementations={operationLibrary.operationImplementations.flatMap' in shell


def test_nested_composer_and_selected_group_share_the_operation_playground_surface() -> None:
    page = PAGE.read_text(encoding="utf-8")

    assert "function VisualImageDiffOperationSurface" in page
    assert "function resolveVisualImageDiffOperationBinding" in page
    assert page.count("<VisualImageDiffOperationSurface") == 2
    assert "!subaccordion && selectedGroup && <VisualImageDiffOperationSurface" not in page
    assert "binding={operationBinding}" in page
    assert "showHeader" in page
    assert "onWorkflowStep={(id, workflowStep) => updateEntry(id, { workflowStep })}" in page
    assert "onImplementation={(id, implementationId) => updateEntry(id, { implementationId })}" in page
    assert "Groups and Prompt steps are native nested accordion members." in page
    footer_start = page.index("const playgroundFooter = isGroup ?")
    playground_surface = page.index("<VisualImageDiffOperationSurface entry={entry}", footer_start)
    member_start = page.index("return <ThreeStateAccordionMember", footer_start)
    assert footer_start < playground_surface < member_start
    assert "playgroundOpen &&" in page[footer_start:member_start]


def test_prolog_transaction_can_switch_from_prompted_llm_to_python(tmp_path: Path) -> None:
    operation_source = (
        ROOT
        / "workbench/workspaces/shared_library_arc3/design/operations/symbolic.get_prolog_evidence.operation.metta"
    ).read_text(encoding="utf-8")
    node = tmp_path / "node"
    node.mkdir()
    registry = tmp_path / "object_registry.pl"
    registry.write_text("object_identity(sample, cell, 'sample').\n", encoding="utf-8")
    for name in (
        "objects.pl",
        "differences.pl",
        "similarities.pl",
        "turtle_from_image.pl",
        "turtle_from_diff.pl",
        "rules.pl",
    ):
        (node / name).write_text(f"artifact('{name}').\n", encoding="utf-8")

    assert "(preferredSpecialization symbolic.get_prolog_evidence.prompted_llm)" in operation_source
    assert "(id symbolic.get_prolog_evidence.prompted_llm)" in operation_source
    assert "(implementation llm.complete)" in operation_source
    assert "visual_image_diff.pipeline.cherry_pick" in operation_source
    assert "(id symbolic.get_prolog_evidence.python)" in operation_source
    assert "(implementation python.callable)" in operation_source
    assert "python/visual_image_diff_operations.py" in operation_source

    result = invoke_operation(
        "arc3_random_player",
        "symbolic.get_prolog_evidence",
        {
            "implementationVariant": "symbolic.get_prolog_evidence.python",
            "inputs": {"bundle": {"node": str(node), "registry": str(registry)}},
        },
    )

    assert result["implementation"]["id"] == "symbolic.get_prolog_evidence.python"
    assert result["implementation"]["route"] == "python.callable"
    assert result["outputs"]["validation"]["llmCalled"] is False
    assert result["outputs"]["validation"]["provider"] == "python.callable"
    assert set(result["outputs"]["bundle"]["prologArtifacts"]) == {
        "object_registry.pl",
        "objects.pl",
        "differences.pl",
        "similarities.pl",
        "turtle_from_image.pl",
        "turtle_from_diff.pl",
        "rules.pl",
    }


def test_pipeline_and_old_analysis_references_are_merged_into_one_starting_group() -> None:
    page = PAGE.read_text(encoding="utf-8")
    prompts = PROMPTS.read_text(encoding="utf-8")

    assert prompts.count("(applicability ([] visual_image_diff.pipeline_step))") == 11
    assert prompts.count("(applicability ([] visual_image_diff.analysis_step))") == 12
    assert "(kind prompt_profile)" in prompts
    assert "(id visual_image_diff.analysis_group)" in prompts
    assert "visual_image_diff.output_contract" in prompts
    assert "visual_image_diff.quality_control" in prompts
    pipeline_ids = [
        "source",
        "normalize",
        "objects",
        "sync_representations",
        "render_turtle",
        "display",
        "compare",
        "rules",
        "cherry_pick",
        "validate",
        "report",
    ]
    assert all(f"(id visual_image_diff.pipeline.{pipeline_id})" in prompts for pipeline_id in pipeline_ids)
    profile = prompts.split("(kind prompt_profile)", 1)[1]
    positions = [profile.index(f"visual_image_diff.pipeline.{pipeline_id}") for pipeline_id in pipeline_ids]
    assert positions == sorted(positions)
    assert "visual_image_diff.output_contract" not in profile
    assert "extract_scene_objects" in prompts
    assert "explain_object_changes" in prompts
    assert "induce_rules_from_prolog" in prompts
    assert "audit_artifact_bundle" in prompts
    assert "prolog_render_symbolic_evidence" in prompts
    pipeline_prompts = prompts.split("(id visual_image_diff.pipeline.source)", 1)[1].split(
        "(kind prompt_profile)", 1
    )[0]
    assert '\"profile\"' not in pipeline_prompts
    assert "openai-gpt" not in pipeline_prompts
    assert "openrouter-" not in pipeline_prompts
    assert "groq-" not in pipeline_prompts
    assert pipeline_prompts.count("The workbench supplies the selected backend and model") == 3
    assert 'const STEP_APPLICABILITY = "visual_image_diff.pipeline_step"' in page
    assert "profile?.prompts" in page
    assert "const initialPromptIds = profileSteps.length ? profileSteps" in page
    assert 'kind: "group"' in page
    assert "setSelectedGroupId(profileGroupId)" in page
    assert 'VisualPipelineComposer: () =>' not in page
    assert 'VisualPipelineSubaccordion: () =>' in page
    assert 'label="+ STEPS"' not in page
    assert 'aria-label="Add visual pipeline steps"' in page
    assert "addPrompt(prompt.id)" in page


def test_visual_generator_keeps_only_the_nested_composer_inside_the_center_accordion() -> None:
    page = PAGE.read_text(encoding="utf-8")
    accordion = (ROOT / "workbench/frontend/src/components/ThreeStateAccordion.tsx").read_text(encoding="utf-8")
    accordion_styles = (ROOT / "workbench/frontend/src/styles/three_state_accordion.css").read_text(encoding="utf-8")
    visual_styles = (ROOT / "workbench/frontend/src/styles/visual_image_diff.css").read_text(encoding="utf-8")

    assert 'VisualPipelineComposer: () =>' not in page
    assert 'VisualPipelineSubaccordion: () =>' in page
    assert 'label="GROUP PROMPT"' not in page
    assert 'className="english-workflow-generation-controls visual-image-generation-controls"' in page
    assert 'className="english-workflow-contract-order visual-image-diff-composer visual-image-diff-subaccordion-composer"' in page
    assert 'className="visual-image-group-list"' not in page
    assert "VISUAL PIPELINE ORDER · NESTED ACCORDION" in page
    assert "[+group]" in page
    assert "selectedGroupId" in page
    assert "COPY" in page
    assert "SHUFFLE" in page
    assert "CLEAR" in page
    assert "visibleToPeers" in page
    assert "visibleToUpdates" in page
    assert 'aria-label={`Prompt at position ${ordinal} in compact strip`}' in page
    assert 'aria-label={`Model override at position ${ordinal} in compact strip`}' in page
    assert '!parentGroupId && <select aria-label={`Model override at position ${ordinal} in compact strip`}' in page
    assert 'className="visual-image-diff-order-position"' in page
    assert 'title="Open the selected Prompt resource to edit or create a child override"' in page
    assert '>OVERRIDE</button>' in page
    assert '>REMOVE</button>' in page
    assert "const moveEntry =" in page
    assert "const moveEntry =" in page
    assert "promptEntries(generationOrder)" in page
    assert "models={workflowRunnerModels}" in SHELL.read_text(encoding="utf-8")
    assert '<header className="three-state-accordion-member three-state-accordion-stack-controls"' in accordion
    assert "three-state-accordion-stack-frozen-controls" in accordion
    assert ".three-state-accordion-stack-frozen-controls>.three-state-accordion-stack-controls{position:sticky" in accordion_styles
    assert "overflow:hidden auto" in accordion_styles
    assert 'data-accordion-stack="visual-image-diff-center-stack"' in visual_styles
    assert "scrollbar-gutter: stable" in visual_styles
    assert "grid-template-columns: 18px minmax(0, 1fr) 24px 24px 24px" in visual_styles
    assert "@container visual-diff-composer (min-width: 720px)" in visual_styles


def test_visual_generator_uses_the_nested_subaccordion_as_its_only_version() -> None:
    page = PAGE.read_text(encoding="utf-8")
    accordion = (ROOT / "workbench/frontend/src/components/ThreeStateAccordion.tsx").read_text(encoding="utf-8")
    visual_styles = (ROOT / "workbench/frontend/src/styles/visual_image_diff.css").read_text(encoding="utf-8")

    assert 'VisualPipelineComposer: () =>' not in page
    assert 'VisualPipelineSubaccordion: () =>' in page
    assert 'id="visual-image-diff-uix-pipeline-stack"' in page
    assert "CompositionOrderAccordionItem" in page
    assert "visual-image-diff-uix-group-${entry.id}" in page
    assert 'controlsLabel={`${ordinal} · NESTED PROMPT STACK`}' in page
    assert 'memberKey={entry.id}' in page
    assert 'managedOrder={index}' in page
    assert 'modeFor={subaccordionMode}' in page
    assert 'stripContent={(cycleMode)' in page
    assert 'mode={modeFor(entry.id, isGroup ? "scroll" : "strip")}' in page
    assert 'className="visual-image-diff-subaccordion-strip-ordinal"' in page
    assert 'aria-label={`Prompt at position ${ordinal} in compact strip`}' in page
    assert 'aria-label={`Model override at position ${ordinal} in compact strip`}' in page
    assert 'onDropPrompt(entry, promptId, parentGroupId)' in page
    assert 'event.dataTransfer.setData(VISUAL_PROMPT_DRAG_TYPE, prompt.id)' in page
    assert 'stripDragData: prompt ? { [VISUAL_PROMPT_DRAG_TYPE]: prompt.id, "text/plain": prompt.id } : undefined' in page
    assert '>DRAG PROMPT</button>' in page
    assert 'setMessage(`Replaced the Prompt at this position with ${promptId}.`)' in page
    assert "Groups and Prompt steps are native nested accordion members." in page
    assert "memberKey?: string" in accordion
    assert "managedOrder?: number" in accordion
    assert "stripContent?: (cycleMode: () => void) => ReactNode" in accordion
    assert 'className="three-state-accordion-member-custom-summary"' in accordion
    assert 'itemHeader !== null && <header className="three-state-accordion-member-item-header">' in accordion
    assert "const layoutOrder = managedOrder ?? memberOrder" in accordion
    assert ".visual-image-diff-uix-pipeline-stack" in visual_styles
    assert ".visual-image-diff-uix-nested-stack" in visual_styles
    assert ".visual-image-diff-subaccordion-strip-control" in visual_styles
    assert ".three-state-accordion-member-custom-summary > .visual-image-diff-subaccordion-header-actions" in visual_styles
    assert ".visual-image-diff-subaccordion-item > .three-state-accordion-member-footer" in visual_styles
    assert ".visual-image-diff-subaccordion-group-body" in visual_styles
    assert ".visual-image-diff-playground-footer-line" in visual_styles
    assert ".visual-image-diff-playground-footer-line > .visual-image-diff-operation-binding" in visual_styles


def test_visual_image_diff_runs_composed_prompts_with_submitted_images() -> None:
    page = PAGE.read_text(encoding="utf-8")
    shell = SHELL.read_text(encoding="utf-8")

    assert 'accept="image/*" multiple' in page
    assert "makeImageContactSheet(imageInputs)" in page
    assert 'VisualPipelineComposer: () =>' not in page
    assert 'aria-label="Visual Image Diff run model"' in page
    assert "▶ Run selected group" in page
    assert 'aria-label={`Run ${title} at position ${ordinal} from compact strip`}' in page
    assert 'title="Run only this visual prompt step"' in page
    assert "void runPrompts([entry], entry.modelId || parentModel || runModel)" in page
    assert 'const parentModel = parentId ? generationOrder.find((candidate) => candidate.id === parentId)?.modelId : ""' in page
    assert "const runnableEntries = promptEntries(entries)" in page
    assert "/models/${encodeURIComponent(modelId)}/invoke" in page
    assert "promptParts.join" in page
    assert 'VisualResourceOutputs: () =>' in page
    assert "runResult.text" in page
    assert "backendLabel: record.resolved?.backend?.label" in shell
    assert '`${model.backendLabel || model.backendId || model.id} · ${model.label || model.id}`' in page
    assert "Unknown backend" not in page


def test_graph_mode_edits_the_same_generation_order_as_columns() -> None:
    page = PAGE.read_text(encoding="utf-8")
    styles = (ROOT / "workbench/frontend/src/styles/visual_image_diff.css").read_text(encoding="utf-8")

    assert 'useState<"columns" | "graph">("columns")' in page
    assert "VisualPipelineGraph" in page
    assert 'onPrompt={(id, promptId, parentGroupId) => updateEntry(id, { promptId }, parentGroupId)}' in page
    assert "onDropPrompt={dropPromptOnEntry}" in page
    assert "onMove={moveEntry}" in page
    assert "onCopyGroup={copyGroup}" in page
    assert "onShuffleGroup={shuffleGroup}" in page
    assert "onClearGroup={clearGroup}" in page
    assert "const insertPromptAt =" in page
    assert "onInsertPrompt={insertPromptAt}" in page
    assert "const moveCallAcrossGroups =" in page
    assert "onMoveCall={moveCallAcrossGroups}" in page
    assert 'aria-label="Graph pipeline authoring controls"' in page
    assert 'aria-label={`Edit graph datafield ${field.name}`}' in page
    assert 'aria-label={`Graph Prompt call ${callOrdinal}`}' in page
    assert 'aria-label={`Insert or move Prompt to graph position ${position}`}' in page
    assert "onMoveCall(orderEntry.entryId, orderEntry.parentGroupId, stack.entry.id, insertionIndex)" in page
    assert "onReplaceCall(orderEntry.entryId, orderEntry.parentGroupId, step.id, stack.entry.id)" in page
    assert "sourceGroupId === targetGroupId && sourceIndex < targetIndex" in page
    assert "const replaceCallAcrossGroups =" in page
    assert "onReplaceCall={replaceCallAcrossGroups}" in page
    assert 'from "@xyflow/react"' in page
    assert 'from "@dagrejs/dagre"' in page
    assert "<ReactFlow nodes={nodes} edges={edges}" in page
    assert 'type: "smoothstep"' in page
    assert "<MiniMap pannable zoomable" in page
    assert 'position={Position.Left}' in page
    assert 'position={Position.Bottom}' in page
    assert 'className="visual-flow-prompt-content"' in page
    assert "visual-pipeline-graph-stack" not in page
    assert 'id: `sequence:${callRows[index].step.id}:${step.id}`' in page
    assert "Visual Image Diff run model" in page
    assert "onDataField={(name, value) => setWorkflowData" in page
    assert ".visual-image-diff-graph-mode .visual-image-diff-columns > .workflow-page-details" in styles
    assert "grid-template-columns: minmax(760px, 1fr) minmax(330px, 430px)" in styles
    assert ".visual-react-flow-canvas" in styles
    assert ".visual-flow-node.prompt" in styles
    assert 'stripDragData: prompt ? { [VISUAL_PROMPT_DRAG_TYPE]: prompt.id' in page


def test_touching_an_individual_pipeline_item_opens_its_full_prompt_in_the_right_stack() -> None:
    page = PAGE.read_text(encoding="utf-8")
    visual_styles = (ROOT / "workbench/frontend/src/styles/visual_image_diff.css").read_text(encoding="utf-8")

    assert 'const [inspectedPromptId, setInspectedPromptId] = useState("")' in page
    assert "onPointerDown={inspect}" in page
    assert "onFocusCapture={inspect}" in page
    assert "onInspectPrompt(event.target.value)" in page
    assert 'stackIdForColumn={(column) => `visual-image-diff-${column.id}-stack`}' in page
    assert 'VisualPromptInspector: (member) =>' in page
    assert 'typeof member.options?.promptId === "string"' in page
    assert '<ResourceSourceEditor' in page
    assert 'label={`Edit ${prompt.label || prompt.id}`}' in page
    assert ">Load</button>" in page
    assert '"Reload"' in page
    assert ">Clear</button>" in page
    assert '"Save Prompt"' in page
    assert "const reloadPrompt = async" in page
    assert "window.document.getElementById(promptMember.id)" in page
    assert 'scrollIntoView({ behavior: "smooth", block: "start", inline: "nearest" })' in page
    assert 'ComposedGroupPrompt: () =>' in page
    assert "generation-output-prompt.inspected" in visual_styles
    assert ".visual-image-diff-prompt-inspector pre" in visual_styles
    assert "white-space: pre-wrap" in visual_styles


def test_accordion_strip_click_cycles_through_all_three_states() -> None:
    accordion = (ROOT / "workbench/frontend/src/components/ThreeStateAccordion.tsx").read_text(encoding="utf-8")

    assert 'const ACCORDION_MODE_CYCLE: AccordionDisplayMode[] = ["strip", "scroll", "full"]' in accordion
    assert "nextAccordionMode(collectiveMode)" in accordion
    assert "changeMode(nextAccordionMode(mode))" in accordion
    assert "onChange(nextAccordionMode(mode))" in accordion


def test_visual_image_diff_does_not_embed_mock_prompt_or_image_arrays() -> None:
    page = PAGE.read_text(encoding="utf-8")

    assert "MANIFEST_PATH" in page
    assert "/prompts`" in page
    assert "promptLibrary" in page
    assert "classificationId" in page
    assert "const frames =" not in page
    assert "const prompts = [" not in page


def test_visual_sequencing_exposes_the_resolved_page_specification_json() -> None:
    page = PAGE.read_text(encoding="utf-8")
    definition = PAGE_DEFINITION.read_text(encoding="utf-8")

    assert 'ResourceSourceEditor: () =>' in page
    assert "<WorkflowPageSourceEditor" in page
    assert "pageId={pageDefinition.id}" in page
    assert '"component": "ResourceSourceEditor"' in definition
    assert '"kind": "workflow_page"' in definition
    assert '"id": "arc3.visual_sequencing"' in definition


def test_resource_outputs_generates_missing_left_datafield_editors_from_center_prompts() -> None:
    page = PAGE.read_text(encoding="utf-8")
    styles = (ROOT / "workbench/frontend/src/styles/visual_image_diff.css").read_text(encoding="utf-8")
    documents = get_filesystem_provider().read_json_documents(PROMPTS)
    actual_fields = {
        field
        for document in documents
        if "visual_image_diff.pipeline_step" in document.get("applicability", [])
        for field in document.get("produces", [])
    }

    assert actual_fields == {
        "source_images", "source_manifest", "normalized_images", "normalized_manifest",
        "scene_objects", "object_manifest", "turtle_programs", "objects_pl",
        "turtle_from_image_pl", "turtle_images", "turtle_render_manifest",
        "display_session", "transition_evidence", "differences_pl", "similarities_pl",
        "turtle_from_diff_pl", "artifact_bundle", "prolog_validation", "rule_set",
        "rules_pl", "validation_report", "audit_report", "workflow_report",
    }
    assert "function visualDataFieldPlan" in page
    assert "READ MIDDLE FLOW" in page
    assert "ADD MISSING FIELD EDITORS" in page
    assert "VisualDataFieldEditor" in page
    assert "renderedPageDefinition" in page
    assert "[first, ...generatedMembers, ...rest]" in page
    assert "liveDefinition={renderedPageDefinition}" in page
    assert "inputPromptIds" in page
    assert "outputPromptIds" in page
    assert ".visual-datafield-planner" in styles
    assert ".visual-datafield-editor textarea" in styles
