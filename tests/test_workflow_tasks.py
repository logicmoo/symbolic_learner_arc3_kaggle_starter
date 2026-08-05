from __future__ import annotations

import copy
import json
from pathlib import Path

from llm_providers import DEFAULT_CONFIG_PATH
from workflow_task_editor import ensure_example, load_example
from workflow_tasks import DEFAULT_DATATYPE_PATH, DEFAULT_TASK_PATH, TaskAwareWorkflowRouter

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = ROOT / "config" / "llm_workflows.json"
GRAPH_PATH = ROOT / "config" / "workflow_datatypes.svg"


def test_semantic_object_has_multiple_representations() -> None:
    raw = json.loads(DEFAULT_DATATYPE_PATH.read_text(encoding="utf-8"))
    types = {item["id"]: item for item in raw["types"]}
    individual = types["individual_object"]
    assert individual["kind"] == "semantic"
    assert set(individual["representations"]) == {
        "image_region",
        "turtle_program",
        "object_properties",
    }
    assert types["artifact_bundle"]["kind"] == "aggregate"
    assert GRAPH_PATH.exists()
    assert "Individual object" in GRAPH_PATH.read_text(encoding="utf-8")


def test_task_catalog_has_eleven_tasks_and_three_species() -> None:
    raw = json.loads(DEFAULT_TASK_PATH.read_text(encoding="utf-8"))
    tasks = {item["id"]: item for item in raw["tasks"]}
    assert len(tasks) == 11
    routes = {item["id"] for item in tasks["grab_image_source"]["implementations"]}
    assert {
        "arc3_state",
        "video_to_frames",
        "ask_user_to_upload",
        "disk_directory",
        "clipboard_image",
        "remote_image_url",
        "camera_capture",
        "generated_test_pattern",
    }.issubset(routes)
    assert "turtlized_objects_to_images" in tasks
    assert "images_displayer" in tasks
    species = {
        implementation["species"]
        for task in tasks.values()
        for implementation in task["implementations"]
    }
    assert species == {"llm", "prolog", "python"}


def test_typed_example_uses_every_task() -> None:
    task_raw = json.loads(DEFAULT_TASK_PATH.read_text(encoding="utf-8"))
    task_ids = {item["id"] for item in task_raw["tasks"]}
    example = load_example()
    assert {step["task"] for step in example["steps"]} == task_ids
    assert example["steps"][0]["task"] == "grab_image_source"


def test_task_router_preprocesses_typed_steps(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("ARC3_OPENROUTER_VERIFY_MODELS", "0")
    raw = copy.deepcopy(json.loads(WORKFLOW_PATH.read_text(encoding="utf-8")))
    raw.setdefault("llm_workflows", []).append(load_example())
    path = tmp_path / "typed_workflows.json"
    path.write_text(json.dumps(raw), encoding="utf-8")
    router = TaskAwareWorkflowRouter(DEFAULT_CONFIG_PATH, workflow_path=path)
    workflow = router.workflow_by_id["typed_routed_artifact_pipeline"]
    assert len(router.tasks) == 11
    assert len(workflow.steps) == 11
    assert all(
        step.transaction_id in router.task_step_by_transaction_id
        for step in workflow.steps
    )


def test_editor_adds_example_once() -> None:
    raw = {"llm_workflows": []}
    assert ensure_example(raw) is True
    assert ensure_example(raw) is False
    assert raw["llm_workflows"][0]["id"] == "typed_routed_artifact_pipeline"
