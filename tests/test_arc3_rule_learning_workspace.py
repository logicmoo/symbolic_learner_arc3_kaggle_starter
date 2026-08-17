from pathlib import Path

import workspace_api
from operation_resolution import materialize_workflow


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "workbench" / "workspaces" / "arc3_rule_learning_demo"


def test_arc3_rule_learning_demo_is_loadable_and_materializes_every_operation() -> None:
    workspace = {"id": WORKSPACE.name, "root": str(WORKSPACE)}
    workflow = next(
        record["document"]
        for record in workspace_api._load_workflows(workspace)
        if record.get("workspaceId") == WORKSPACE.name
    )
    local_operations = {
        record["document"]["id"]
        for record in workspace_api._load_operations(workspace)
        if record.get("workspaceId") == WORKSPACE.name and record.get("document")
    }

    assert local_operations == {
        "phase3.apply_learned_rule",
        "phase3.grade_prediction",
    }
    assert [step["id"] for step in workflow["steps"]] == [
        "capture_before",
        "capture_after",
        "analyze_transition",
        "induce_rival_rules",
        "review_rule",
        "predict_unseen_case",
        "grade_independent_outcome",
    ]
    assert workflow["steps"].index(
        next(step for step in workflow["steps"] if step["id"] == "predict_unseen_case")
    ) < workflow["steps"].index(
        next(step for step in workflow["steps"] if step["id"] == "grade_independent_outcome")
    )

    executable = materialize_workflow(
        {**workflow, "workspaceId": WORKSPACE.name}
    )
    assert all(
        step.get("kind") == "human" or step.get("implementation")
        for step in executable["steps"]
    )
    assert next(
        step for step in executable["steps"] if step["id"] == "predict_unseen_case"
    )["implementation"] == "llm.complete"
