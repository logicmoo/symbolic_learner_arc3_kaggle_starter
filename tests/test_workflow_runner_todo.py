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
    assert 'mode === "workflowRuns" && <WorkflowRunnerTodoReference />' in source
    assert '<WorkflowRunProjection run={selectedRun} workflow={frozenWorkflow}' in source
    assert '"topology" | "chronology"' in source
    assert "/api/engine/workflows/" in source
    assert "run.events.map" in source
    assert "commandWorkflowRun" in source
    assert "Replay as new run" in source
    assert 'onCommand("pause")' in source
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
