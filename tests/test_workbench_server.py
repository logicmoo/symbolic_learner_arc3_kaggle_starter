from __future__ import annotations

import sys
from pathlib import Path


SERVER_ROOT = Path(__file__).resolve().parents[1] / "workbench" / "server"
sys.path.insert(0, str(SERVER_ROOT))

from store import WorkbenchStore  # noqa: E402


def test_execution_task_records_loop_back(tmp_path: Path) -> None:
    store = WorkbenchStore(tmp_path / "workbench.db")
    run = store.create_run()

    run = store.command_run(run["id"], "run_next")
    assert run["stage"] == 4
    assert run["status"] == "waiting"

    run = store.command_run(run["id"], "human_action", {"action": "RIGHT"})
    run = store.command_run(run["id"], "run_next")
    run = store.command_run(run["id"], "run_next")
    assert run["stage"] == 7

    run = store.command_run(run["id"], "repeat")
    steps = [event["step"] for event in run["task"]["events"]]
    assert run["stage"] == 4
    assert steps[-2:] == [7, 4]


def test_design_task_validates_and_hands_off(tmp_path: Path) -> None:
    store = WorkbenchStore(tmp_path / "workbench.db")
    workflow = store.list_workflows()[0]

    workflows, task = store.save_workflow(workflow, workflow["id"])

    assert task["kind"] == "workflow_design"
    assert task["status"] == "completed"
    assert task["currentStep"] == 5

    run = store.create_run(workflows[0]["id"], parent_task_id=task["id"])
    assert run["task"]["parentTaskId"] == task["id"]
