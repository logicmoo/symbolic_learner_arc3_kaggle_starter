from __future__ import annotations

import copy
import json
from pathlib import Path
from types import SimpleNamespace

from llm_providers import DEFAULT_CONFIG_PATH
from workflow_task_editor import ensure_example, load_example
from workflow_tasks import (
    DEFAULT_DATATYPE_PATH,
    DEFAULT_TASK_PATH,
    TaskAwareWorkflowRouter,
    await_human_arc3_action,
    continue_human_observation,
    expand_subworkflows,
    select_arc3_world,
)

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


def test_task_catalog_has_workbench_and_arc3_demonstration_tasks() -> None:
    raw = json.loads(DEFAULT_TASK_PATH.read_text(encoding="utf-8"))
    tasks = {item["id"]: item for item in raw["tasks"]}
    assert len(tasks) == 15
    assert {
        "select_arc3_world",
        "await_human_arc3_action",
        "continue_human_observation",
        "advance_observation",
    }.issubset(tasks)
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


def test_typed_example_uses_the_noninteractive_artifact_tasks() -> None:
    task_raw = json.loads(DEFAULT_TASK_PATH.read_text(encoding="utf-8"))
    task_ids = {item["id"] for item in task_raw["tasks"]}
    example = load_example()
    example_task_ids = {step["task"] for step in example["steps"]}
    assert example_task_ids.issubset(task_ids)
    assert len(example_task_ids) == 11
    assert example["steps"][0]["task"] == "grab_image_source"


def test_task_router_preprocesses_typed_steps(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("ARC3_OPENROUTER_VERIFY_MODELS", "0")
    raw = copy.deepcopy(json.loads(WORKFLOW_PATH.read_text(encoding="utf-8")))
    raw.setdefault("llm_workflows", []).append(load_example())
    path = tmp_path / "typed_workflows.json"
    path.write_text(json.dumps(raw), encoding="utf-8")
    router = TaskAwareWorkflowRouter(DEFAULT_CONFIG_PATH, workflow_path=path)
    workflow = router.workflow_by_id["typed_routed_artifact_pipeline"]
    assert len(router.tasks) == 15
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


def test_subworkflow_expansion_binds_ports_and_isolates_internal_slots() -> None:
    raw = [
        {
            "id": "objectify",
            "input_slots": {"image": "source"},
            "output_slots": {"objects": "objects"},
            "steps": [
                {
                    "id": "extract",
                    "task": "extract_individual_objects",
                    "inputs": {"images": "source"},
                    "outputs": {
                        "objects": "objects",
                        "object_manifest": "manifest",
                        "turtle": "turtle",
                    },
                }
            ],
        },
        {
            "id": "parent",
            "steps": [
                {
                    "id": "first",
                    "subworkflow": "objectify",
                    "inputs": {"image": "before_image"},
                    "outputs": {"objects": "before_objects"},
                },
                {
                    "id": "second",
                    "subworkflow": "objectify",
                    "inputs": {"image": "after_image"},
                    "outputs": {"objects": "after_objects"},
                },
            ],
        },
    ]
    parent = {item["id"]: item for item in expand_subworkflows(raw)}["parent"]
    assert [step["id"] for step in parent["steps"]] == [
        "first__extract",
        "second__extract",
    ]
    assert parent["steps"][0]["inputs"]["images"] == "before_image"
    assert parent["steps"][0]["outputs"]["objects"] == "before_objects"
    assert parent["steps"][0]["outputs"]["turtle"] == "first__turtle"
    assert parent["steps"][1]["outputs"]["turtle"] == "second__turtle"


def test_arc3_human_observation_is_runnable_after_subworkflow_expansion(
    monkeypatch,
) -> None:
    monkeypatch.setenv("ARC3_OPENROUTER_VERIFY_MODELS", "0")
    router = TaskAwareWorkflowRouter(DEFAULT_CONFIG_PATH)
    workflow = router.workflow_by_id["arc3_human_observation"]
    assert workflow.repeat_from == "human_chooses_action"
    assert workflow.repeat_while_slot == "continue_observing"
    assert len(workflow.steps) == 18
    assert all(step.transaction_id in router.transaction_by_id for step in workflow.steps)
    assert {
        "objectify_observation__extract_objects",
        "capture_resulting_observation__objectify__render_turtle",
        "update_world_understanding__continue",
        "update_world_understanding__advance",
    }.issubset({step.step_id for step in workflow.steps})


def test_arc3_desktop_handlers_restart_world_and_apply_human_choice() -> None:
    class Action:
        name = "ACTION1"

        def is_complex(self):
            return False

    class Runner:
        game_id = "ls20"
        detected_level = 1
        current_node = SimpleNamespace(path=Path("before"))

        def __init__(self):
            self.restarted = 0
            self.steps = []

        def restart_game(self):
            self.restarted += 1

        def action_table(self):
            return [{"index": 0, "name": "ACTION1", "complex": False}]

        def resolve_action(self, action):
            assert action == 0
            return Action()

        def step(self, action, data):
            self.steps.append((action.name, data))
            self.current_node = SimpleNamespace(path=Path("after"))

    runner = Runner()
    engine = SimpleNamespace(runner=runner)
    world = select_arc3_world(engine, {}, {"game_id": "ls20"})
    assert runner.restarted == 1
    assert world["world"]["environment_id"] == "ls20"
    intervention = await_human_arc3_action(engine, {}, {"action": "0"})
    assert runner.steps == [("ACTION1", {})]
    assert intervention["intervention"]["actor"] == "human"
    assert continue_human_observation(engine, {}, {"continue": False}) == {
        "continue": False
    }
