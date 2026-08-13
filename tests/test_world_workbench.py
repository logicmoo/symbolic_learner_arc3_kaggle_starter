from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
sys.path.insert(0, str(ROOT / "workbench" / "server"))

from resource_store import get_filesystem_provider  # noqa: E402

from worldworkbench import (  # noqa: E402
    Goal,
    HumanDemonstrationObserver,
    Intervention,
    Observation,
    ProducerRef,
    SimulationRequest,
    SimulationResult,
    SiloStatus,
    WorldAnalysisState,
    WorldLearningWorkbench,
    WorldModel,
)
from worldworkbench.adapters import (  # noqa: E402
    Arc3InterventionAdapter,
    Arc3ObservationAdapter,
)


def test_silos_are_versioned_and_addressable() -> None:
    state = WorldAnalysisState("test-analysis")
    first = state.put(
        "entities",
        semantic_type="entity_collection",
        representation_type="json_object",
        value=[{"id": "ball"}],
        status=SiloStatus.OBSERVED,
    )
    second = state.put(
        "entities",
        semantic_type="entity_collection",
        representation_type="json_object",
        value=[{"id": "ball"}, {"id": "wall"}],
        derived_from=(first.reference,),
        produced_by=ProducerRef("analyze_observation", "test"),
    )
    assert first.reference == "entities:v1"
    assert second.reference == "entities:v2"
    assert state.get(first.reference).value == [{"id": "ball"}]
    assert state.latest("entities") is second


class Learner:
    def update(self, observation, state):
        return WorldModel(
            "tiny-world",
            revision=len(state.history("world/model")) + 1,
            state={"x": observation.payload["x"]},
            confidence=0.75,
        )


class Goals:
    def goals(self, state, model):
        return (Goal("reach-right", "Move right", {"x": {"gte": 2}}),)


class Policy:
    def select(self, state, model, goals):
        return (
            SimulationRequest(
                "sim-right",
                model.model_id,
                tuple(goal.goal_id for goal in goals),
                {"action": "right"},
            ),
        )


class TinySimulator:
    def simulate(self, request, model):
        x = model.state["x"] + 1
        return SimulationResult(
            request.simulation_id,
            {"x": x},
            {"reach-right": 1.0 if x >= 2 else 0.0},
            confidence=0.8,
        )


def test_goals_select_what_the_workbench_simulates() -> None:
    workbench = WorldLearningWorkbench(
        learner=Learner(),
        goal_provider=Goals(),
        simulation_policy=Policy(),
        simulator=TinySimulator(),
    )
    results = workbench.process(Observation("frame-1", {"x": 1}, "tiny-world"))
    assert results[0].predicted_state["x"] == 2
    assert results[0].goal_scores["reach-right"] == 1.0
    assert workbench.state.latest("world/model").value.model_id == "tiny-world"
    assert workbench.state.latest("goals/active").value[0].goal_id == "reach-right"


class FakeNode:
    path = Path("run/episode-1/step-0")
    image_path = path / "image.png"


class FakeArc3Runner:
    game_id = "ls20"
    detected_level = 3
    current_observation = {"state": "NOT_FINISHED"}
    current_node = FakeNode()

    def state_name(self):
        return "NOT_FINISHED"

    def step(self, action, *, data=None, **kwargs):
        return {"action": action, "data": data, **kwargs}


def test_arc3_is_an_adapter_not_a_core_dependency() -> None:
    runner = FakeArc3Runner()
    observation = Arc3ObservationAdapter().capture(runner, observation_id="arc-frame")
    assert observation.source == "arc3:ls20"
    assert observation.metadata["episode"] == 3
    assert observation.representation_type == "arc3_state"
    request = SimulationRequest(
        "arc-step",
        "arc-world",
        ("win",),
        {"action": "ACTION1", "data": {"x": 2, "y": 4}},
    )
    assert Arc3InterventionAdapter().apply(runner, request) == {
        "action": "ACTION1",
        "data": {"x": 2, "y": 4},
    }


def test_human_demonstration_mode_observes_without_selecting_actions() -> None:
    observer = HumanDemonstrationObserver()
    before = observer.begin(Observation("before", {"x": 1}, "tiny-world"))
    step = observer.observe_human_step(
        Intervention("human-right", "human", "right"),
        Observation("after", {"x": 2}, "tiny-world"),
        step_id="demo-1",
    )
    assert step.before_observation == before.reference
    assert step.intervention.actor == "human"
    stored = observer.state.latest("demonstration/demo-1")
    assert stored.semantic_type == "demonstration_step"
    assert stored.metadata["actor"] == "human"


def test_domain_neutral_manifests_keep_arc3_at_the_adapter_boundary() -> None:
    shared_config = ROOT / "workbench" / "workspaces" / "shared_library_system" / "design" / "configs"
    semantic_dir = shared_config.parent / "semantic_datatypes"
    resources = get_filesystem_provider()
    semantic = [
        document
        for path in semantic_dir.glob("*.semantic_datatype.metta")
        for document in resources.read_json_documents(path)
    ]
    by_id = {item["id"]: item for item in semantic}
    assert {"world_model", "goal_set", "simulation_result"}.issubset(by_id)
    assert not {item_id for item_id in by_id if item_id.startswith("arc3_")}

    legacy = resources.read_json(shared_config / "world_workbench_datatypes.legacy.config.json")
    legacy_by_id = {item["id"]: item for item in legacy["types"]}
    assert legacy["legacy"] is True
    assert legacy_by_id["arc3_state"]["kind"] == "adapter"
    assert "observation" in legacy_by_id["arc3_state"]["extends"]

    operations = resources.read_json(shared_config / "world_workbench_operations.config.json")
    operation_ids = {item["id"] for item in operations["operations"]}
    assert {
        "select_world",
        "begin_episode",
        "observe_world",
        "objectify_observation",
        "observe_human_intervention",
        "analyze_demonstration_step",
        "update_world_model",
        "identify_goals",
        "select_simulations",
        "simulate_candidates",
        "record_outcome",
    }.issubset(operation_ids)

    workflow_catalog = json.loads(
        (ROOT / "config" / "llm_workflows.json").read_text(encoding="utf-8")
    )
    workflow = next(
        item
        for item in workflow_catalog["llm_workflows"]
        if item["id"] == "arc3_human_observation"
    )
    assert workflow["mode"] == "human_demonstration"
    workflow_steps = {item["id"]: item for item in workflow["steps"]}
    assert len(workflow_steps) == 7
    assert workflow_steps["select_world"]["parameters"]["game_id"] == "ls20"
    assert (
        workflow_steps["objectify_observation"]["subworkflow"]
        == "arc3_objectify_observation"
    )
    assert workflow_steps["human_chooses_action"]["operation"] == "await_human_arc3_action"
    subworkflow = next(
        item
        for item in workflow_catalog["llm_workflows"]
        if item["id"] == "arc3_objectify_observation"
    )
    objectify_operations = {item["operation"] for item in subworkflow["steps"]}
    assert {"extract_individual_objects", "turtlized_objects_to_images"}.issubset(
        objectify_operations
    )
