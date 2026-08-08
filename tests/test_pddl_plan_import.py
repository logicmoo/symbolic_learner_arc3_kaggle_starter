from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "workbench" / "server"
sys.path.insert(0, str(SERVER))

from pddl_plan import grounded_plan_to_workflow  # noqa: E402


def test_grounded_pddl_plan_becomes_sequential_operation_steps() -> None:
    workflow = grounded_plan_to_workflow({
        "id": "warehouse-delivery",
        "planner": "fast-downward",
        "domain": "warehouse.pddl",
        "problem": "delivery-7.pddl",
        "sourcePlan": "; cost = 2\n0: (MOVE ROBOT-A ROOM-1 ROOM-2) [1.5]\n1.5: (DROP ROBOT-A BOX-9 ROOM-2) [0.5]",
        "actionMap": {"move": "navigation.move", "drop": "manipulation.drop"},
    })
    assert workflow["kind"] == "workflow"
    assert workflow["planProvenance"]["origin"] == "pddl"
    assert workflow["planProvenance"]["sourcePlan"].startswith("; cost")
    assert [step["operation"] for step in workflow["steps"]] == ["navigation.move", "manipulation.drop"]
    assert workflow["steps"][0]["dependsOn"] == []
    assert workflow["steps"][1]["dependsOn"] == ["move_1"]
    assert workflow["steps"][0]["parameters"] == {
        "pddlAction": "MOVE",
        "pddlArguments": ["ROBOT-A", "ROOM-1", "ROOM-2"],
        "pddlStartTime": 0.0,
        "pddlDuration": 1.5,
    }


def test_pddl_import_rejects_non_action_text() -> None:
    with pytest.raises(ValueError, match="invalid grounded plan line 1"):
        grounded_plan_to_workflow({"sourcePlan": "this is not a grounded action"})


def test_active_workflow_editor_exposes_unsaved_pddl_conversion() -> None:
    page = (ROOT / "workbench" / "frontend" / "src" / "pages" / "FilesystemWorkbenchPage.tsx").read_text(encoding="utf-8")
    panel = (ROOT / "workbench" / "frontend" / "src" / "components" / "PddlPlanImportPanel.tsx").read_text(encoding="utf-8")
    assert 'workflow?.planProvenance?.origin==="pddl"&&<PddlPlanImportPanel' in page
    assert "/api/engine/workflows/import-pddl-plan" in panel
    assert "ACTION MAP · JSON" in panel
    assert "does not save or run" in panel
