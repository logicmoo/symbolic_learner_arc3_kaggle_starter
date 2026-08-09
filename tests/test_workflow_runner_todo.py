from __future__ import annotations

from pathlib import Path

from workflow_runner_todo_api import (
    get_workflow_runner_chronology_mockup,
    get_workflow_runner_human_input_mockup,
    get_workflow_runner_mockup,
    get_workflow_runner_todo,
)


ROOT = Path(__file__).resolve().parents[1]


def test_workflow_runner_reference_is_read_from_checked_in_files() -> None:
    payload = get_workflow_runner_todo()
    assert payload["mockupAvailable"] is True
    assert payload["status"] == "design-reference"
    assert "Restore the Rich Workflow Runner Experience" in str(payload["markdown"])
    assert get_workflow_runner_mockup().path.name == "workflow_runner_mockup.png"
    assert get_workflow_runner_chronology_mockup().path.name == "workflow_runner_chronology_mockup.png"
    assert get_workflow_runner_human_input_mockup().path.name == "workflow_runner_human_input_mockup.png"
    assert [item["view"] for item in payload["mockups"]] == ["Topology", "Chronology", "Human Input"]
    assert "same operation may appear more than once" in str(payload["markdown"])
    assert "human_input.received" in str(payload["markdown"])


def test_workflow_runs_page_displays_reference_without_replacing_history() -> None:
    source = (ROOT / "workbench" / "frontend" / "src" / "components" / "RuntimeHistoryView.tsx").read_text(encoding="utf-8")
    assert 'mode === "workflowRuns" && <Suspense' in source
    assert '<WorkflowRunnerTodoReference /></Suspense>' in source
    assert '<WorkflowRunProjection run={selectedRun} workflow={frozenWorkflow}' in source
    assert '"topology" | "chronology"' in source
    assert "/api/engine/workflows/" in source
    assert "run.events.map" in source
    assert "commandWorkflowRun" in source
    assert "Replay as new run" in source
    assert 'onCommand("pause")' in source
    assert "item.contentHash" in source
    assert "item.provenance" in source
    assert "logs: run.logs || []" in source
    assert "run-stage-narrative" in source
    assert "latestStepEvent" in source
    assert "DURABLE EVIDENCE" in source
    assert "visualArtifactPayload" in source
    assert "SOURCE / RENDER COMPARISON" in source
    assert 'startsWith("data:image/")' in source
    assert "Records are loaded from the durable workflow-engine database" in source


def test_workflow_runner_reference_is_collapsed_after_real_projection_exists() -> None:
    source = (ROOT / "workbench" / "frontend" / "src" / "components" / "WorkflowRunnerTodoReference.tsx").read_text(encoding="utf-8")
    assert '<details className="workflow-runner-reference">' in source
    assert "Mockups and remaining experience TODO" in source


def test_goal_run_human_pause_uses_the_frozen_step_form_contract() -> None:
    source = (ROOT / "workbench" / "frontend" / "src" / "components" / "RuntimeHistoryView.tsx").read_text(encoding="utf-8")
    assert "function HumanInputForm" in source
    assert "waitingStepDefinition" in source
    assert "step?.form" in source
    assert 'type="checkbox"' in source
    assert "JSON.stringify(values)" in source
    assert "Draft autosave ready" in source
    assert 'method: "PUT"' in source
    assert 'type="password"' in source
    assert 'type="file" accept="image/*"' in source
    assert "human-grid-preview" in source
    assert "reader.readAsDataURL(file)" in source
    assert "hypothesisRecords" in source
    assert "experimentRecords" in source
    assert "Typed artifacts persisted by this run" in source
    assert "run={selectedGoalRun.workflowRun}" in source
    assert 'commands={["pause", "resume", "advance", "cancel"]}' in source
    assert 'get("goalRun")' in source
    assert '/api/goal-runs/${encodeURIComponent(requestedGoalRunId)}' in source
    assert 'persistRuntimeSelection("goalRun", goalRun.id)' in source
    assert 'persistRuntimeSelection("run", run.id)' in source
    assert 'onOpenResource("datatype", datatypeId)' in source
    assert "Open Datatype" in source
    assert "!selectedStep || !item.stepId || item.stepId === selectedStep.id" in source
    assert "workflow={goalRunWorkflow}" in source


def test_runner_panels_are_user_resizable() -> None:
    styles = (ROOT / "workbench" / "frontend" / "src" / "styles" / "workbench.css").read_text(encoding="utf-8")
    assert ".run-topology-scroll,.run-chronology,.run-visual-comparison,.run-projection-inspector{resize:vertical" in styles


def test_runtime_history_initial_load_is_bounded_and_expandable() -> None:
    source = (ROOT / "workbench" / "frontend" / "src" / "components" / "RuntimeHistoryView.tsx").read_text(encoding="utf-8")
    assert '[runLimit, setRunLimit] = useState(50)' in source
    assert "limit=${runLimit}" in source
    assert "Load 50 older runs" in source
    assert "Math.min(500, limit + 50)" in source
    assert '[goalRunLimit, setGoalRunLimit] = useState(50)' in source
    assert "limit=${goalRunLimit}" in source
    assert "Load 50 older goal runs" in source
    assert 'const includeGoalRuns = mode === "goalRuns" || mode === "runtimeContexts"' in source
    assert "includeWorkflowRuns ? api(" in source


def test_runtime_records_link_back_to_executable_resources() -> None:
    runtime = (ROOT / "workbench" / "frontend" / "src" / "components" / "RuntimeHistoryView.tsx").read_text(encoding="utf-8")
    shell = (ROOT / "workbench" / "frontend" / "src" / "pages" / "FilesystemWorkbenchPage.tsx").read_text(encoding="utf-8")
    operations = (ROOT / "workbench" / "frontend" / "src" / "components" / "OperationLibraryEditor.tsx").read_text(encoding="utf-8")
    models = (ROOT / "workbench" / "frontend" / "src" / "components" / "LlmModelsEditor.tsx").read_text(encoding="utf-8")

    assert "Open Operation ·" in runtime
    assert "Open producing Model ·" in runtime
    assert "OpenRuntimeResource" in runtime
    assert 'url.searchParams.set("resource",id)' in shell
    assert 'kind==="operation"?"operations":kind==="model"?"llms":"data"' in shell
    assert 'new URLSearchParams(window.location.search).get("resource")' in operations
    assert 'new URLSearchParams(window.location.search).get("resource")' in models
