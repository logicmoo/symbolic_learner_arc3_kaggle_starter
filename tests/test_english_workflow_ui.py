from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_english_workflow_page_uses_real_resources_and_native_accordion_stacks() -> None:
    page = (ROOT / "workbench" / "frontend" / "src" / "components" / "EnglishWorkflowPage.tsx").read_text(encoding="utf-8")
    shell = (ROOT / "workbench" / "frontend" / "src" / "pages" / "FilesystemWorkbenchPage.tsx").read_text(encoding="utf-8")

    assert 'label: "English Workflow", view: "englishWorkflow"' in shell
    assert 'view === "englishWorkflow"' in shell
    assert page.count("<ThreeStateAccordionStack") == 3
    assert 'id="english-workflow-left-stack"' in page
    assert 'id="english-workflow-center-stack"' in page
    assert 'id="english-workflow-right-stack"' in page
    assert "/model-selection" in page
    assert "/operations/${encodeURIComponent(contractOperation.id)}/invoke" in page
    assert "/api/engine/workflows/validate" in page


def test_generation_order_is_one_call_audited_and_selectively_revisable() -> None:
    page = (ROOT / "workbench" / "frontend" / "src" / "components" / "EnglishWorkflowPage.tsx").read_text(encoding="utf-8")

    assert '"summary", "memory", "checklist", "outputs", "rules", "englishsteps", "steps", "workflow", "libops", "matchops", "inventops", "codeops", "promptops", "libdt", "matchdt", "inventdt", "codedt", "libwf", "matchwf", "inventwf", "codewf"' in page
    assert 'summary: "workflow.generation.summary"' in page
    assert 'memory: "workflow.generation.memory"' in page
    assert 'checklist: "workflow.generation.checklist"' in page
    assert 'outputs: "workflow.generation.outputs"' in page
    assert 'rules: "workflow.generation.rules"' in page
    assert 'englishsteps: "workflow.generation.englishsteps"' in page
    assert 'steps: "workflow.generation.steps"' in page
    assert 'workflow: "workflow.generation.workflow"' in page
    assert 'libops: "workflow.generation.libops"' in page
    assert 'matchops: "workflow.generation.matchops"' in page
    assert 'inventops: "workflow.generation.inventops"' in page
    assert 'codeops: "workflow.generation.codeops"' in page
    assert 'promptops: "workflow.generation.promptops"' in page
    assert 'libdt: "workflow.generation.libdt"' in page
    assert 'matchdt: "workflow.generation.matchdt"' in page
    assert 'inventdt: "workflow.generation.inventdt"' in page
    assert 'codedt: "workflow.generation.codedt"' in page
    assert 'libwf: "workflow.generation.libwf"' in page
    assert 'matchwf: "workflow.generation.matchwf"' in page
    assert 'inventwf: "workflow.generation.inventwf"' in page
    assert 'codewf: "workflow.generation.codewf"' in page
    assert "promptId: DEFAULT_PROMPT_BY_OUTPUT[name]" in page
    assert "GENERATION ORDER · BUTTON PRESS HISTORY" in page
    assert "recordGenerationStep" in page
    assert "generation_steps: requestedSteps" in page
    assert "existing_generation_contract: analysisContract || {}" in page
    assert "existing_workflow: draft || workflow" in page
    assert 'aria-label="Add outputs to Generation Order"' in page
    assert 'id: "operations", names: CONTRACT_SECTIONS.slice(8, 13)' in page
    assert 'id: "datatypes", names: CONTRACT_SECTIONS.slice(13, 17)' in page
    assert 'id: "workflows", names: CONTRACT_SECTIONS.slice(17)' in page
    assert 'className={`english-workflow-output-composer-row generation-${row.id}-buttons`}' in page
    assert "onAdd(entry.name)" in page
    assert 'addGenerationOutput("group")' in page
    assert ">[+group]</button>" in page
    assert 'aria-label={isGroup ? `Run group ${ordinal}`' in page
    assert "generation-order-group-picker" in page
    assert "generation-order-group-actions" in page
    assert "Select group ${ordinal} for insertion" in page
    assert "Shuffle group ${ordinal}" in page
    assert "Clear group ${ordinal}" in page
    assert "clearGenerationGroup" in page
    assert "shuffleGenerationGroup" in page
    assert "setSelectedGroupId(groupId)" in page
    assert "steps: shuffledGenerationOrder(entry.steps || [])" in page
    assert "copyGenerationGroup" in page
    assert "onCopyGroup" in page
    assert ">COPY</button>" in page
    assert 'aria-label={`Prompt at position ${ordinal}`}' in page
    assert 'aria-label={`Model override at position ${ordinal}`}' in page
    assert "generation-output-${entry.name}" in page
    assert "/prompts`" in page
    assert "effective_prompt_catalog: promptChoices" in page
    assert "effective_datatype_catalog: datatypeCatalog" in page
    assert "effective_workflow_catalog: workflowCatalog" in page
    assert 'onRunGroup={(group, ordinal) => void analyze([group]' in page
    assert "group.modelId || selectedModel" in page
    assert 'containsGenerationOutput(generationOrder, name) || containsGenerationOutput(generationOrder, "group")' in page
    assert "function initialGenerationOrder(): GenerationOrderEntry[]" in page
    assert "return [];" in page
    assert "generation-order-flags" in page
    assert "visibleToPeers: true" in page
    assert "visibleToUpdates: false" in page
    assert "visibility: { peers: visibleToPeers, updates: visibleToUpdates }" in page
    assert "Share ${entry.name} with peers at position ${ordinal}" in page
    assert "Share ${entry.name} with updates at position ${ordinal}" in page
    assert "GenerationOutputMode" not in page
    assert "allowReuse" not in page
    assert "rotateGenerationEntry" in page
    assert "onRotate(entry.id, -1, parentGroupId)" in page
    assert "onRotate(entry.id, 1, parentGroupId)" in page
    assert "(source + direction + entries.length) % entries.length" in page
    assert "Wrap from the beginning to the end" in page
    assert "Wrap from the end to the beginning" in page
    assert page.index("Rotate ${entry.name} left") < page.index("Remove ${entry.name}") < page.index("Rotate ${entry.name} right")
    assert "contractTrials" in page
    assert "validationIssues" in page


def test_analyze_runs_and_persists_the_composed_generation_sequence() -> None:
    page = (ROOT / "workbench" / "frontend" / "src" / "components" / "EnglishWorkflowPage.tsx").read_text(encoding="utf-8")
    workflow = (ROOT / "workbench" / "workspaces" / "generate_count_to_ten" / "design" / "workflows" / "generate_count_to_ten.workflow.metta").read_text(encoding="utf-8")

    assert 'generationOrderPath || "docs/WORKFLOW_GENERATION_ORDER.txt"' in page
    assert "generationSteps: generationRequest(generationOrder)" in page
    assert "lastRunSteps: requestedSteps" in page
    assert "orderUsed: trial.returnedOrder" in page
    assert "generationContract: nextContract" in page
    assert '"⌕ Analyze & Save"' in page
    assert "/file?path=${encodeURIComponent(generationOrderPath)}" in page
    assert "generationOrderPath docs/WORKFLOW_GENERATION_ORDER.txt" in workflow


def test_contract_analyzer_is_a_filesystem_backed_single_llm_operation() -> None:
    root = ROOT / "workbench" / "workspaces" / "shared_library_system" / "design"
    operation = (root / "operations" / "analyze_workflow_generation_contract.operation.metta").read_text(encoding="utf-8")
    prompt = (root / "prompts" / "analyze_workflow_generation_contract.json.prompt.metta").read_text(encoding="utf-8")

    assert "workflow.analyze_generation_contract" in operation
    assert "(implementation llm.complete)" in operation
    assert "(generation_steps Array)" in operation
    assert "(effective_prompt_catalog Array)" in operation
    assert "(effective_datatype_catalog Array)" in operation
    assert "(effective_workflow_catalog Array)" in operation
    assert "(existing_generation_contract Object)" in operation
    assert "(workflow Object)" in operation
    assert "name is summary, memory, checklist, outputs, rules, englishsteps, steps, workflow, libops, matchops, inventops, codeops, promptops, libdt, matchdt, inventdt, codedt, libwf, matchwf, inventwf, codewf, or group" in prompt
    assert "names may repeat" in prompt
    assert "Process every item in the exact listed order" in prompt
    assert "A group item contains a nested steps array" in prompt
    assert "those nested outputs together as one simultaneous batch" in prompt
    assert "promptId and modelId routing declarations" in prompt
    assert "Resolve promptId only against effective_prompt_catalog" in prompt
    assert "completely replace the former new/reuse/preserve/hide mode" in prompt
    assert "Every listed occurrence executes" in prompt
    assert "exactly one response" in prompt


def test_generation_contract_sections_have_matching_shared_prompts() -> None:
    prompts = (ROOT / "workbench" / "workspaces" / "shared_library_system" / "design" / "prompts" / "workflow_generation_sections.prompt.metta").read_text(encoding="utf-8")

    for section in ("summary", "memory", "checklist", "outputs", "rules", "englishsteps", "steps", "workflow", "libops", "matchops", "inventops", "codeops", "promptops", "libdt", "matchdt", "inventdt", "codedt", "libwf", "matchwf", "inventwf", "codewf"):
        assert f"(id workflow.generation.{section})" in prompts
    assert "Generate Summary From Current Workflow Information" in prompts
    assert "Generate Memory Plan From Current Workflow Information" in prompts
    assert "Generate Acceptance Checklist From Current Workflow Information" in prompts
    assert "Generate Output Requirements From Current Workflow Information" in prompts
    assert "Generate Validation Rules From Current Workflow Information" in prompts
    assert "Generate English Steps From Current Workflow Information" in prompts
    assert "Generate Formal Steps From Current Workflow Information" in prompts
    assert "Generate Workflow From Current Workflow Information" in prompts
    assert "Select Library Operations From Current Workflow Information" in prompts
    assert "Match Operations From Current Workflow Information" in prompts
    assert "Invent Operations From Current Workflow Information" in prompts
    assert "Code Operations From Current Workflow Information" in prompts
    assert "Generate Prompts for New Operations From Current Workflow Information" in prompts
    assert "Select Library Datatypes From Current Workflow Information" in prompts
    assert "Match Datatypes From Current Workflow Information" in prompts
    assert "Invent Datatypes From Current Workflow Information" in prompts
    assert "Code Datatypes From Current Workflow Information" in prompts
    assert "Select Library Workflows From Current Workflow Information" in prompts
    assert "Match Workflows From Current Workflow Information" in prompts
    assert "Invent Workflows From Current Workflow Information" in prompts
    assert "Code Workflow From Current Workflow Information" in prompts
    assert "deterministic python, prolog, metta, or resource.tool implementations" in prompts


def test_experimental_candidate_cannot_be_applied() -> None:
    page = (ROOT / "workbench" / "frontend" / "src" / "components" / "EnglishWorkflowPage.tsx").read_text(encoding="utf-8")

    assert "setDraftReadyToApply(false)" in page
    assert "setDraftReadyToApply(errors.length === 0)" in page
    assert "!draftReadyToApply" in page
    assert "Experimental contract trials never enable Apply" in page
    assert "withoutInventedNamespace" in page
