from pathlib import Path

from resource_store import get_filesystem_provider


ROOT = Path(__file__).resolve().parents[1]
WORKSPACES = ROOT / "workbench" / "workspaces"


def test_editable_workspace_workflows_do_not_claim_runtime_versions() -> None:
    provider = get_filesystem_provider()
    for path in WORKSPACES.glob("*/design/workflows/*.workflow.metta"):
        for document in provider.read_json_documents(path):
            assert document.get("kind") == "workflow"
            assert "version" not in document, f"{path} must be registered by the runtime before receiving a version"


def test_libraries_have_no_runnable_workflows_and_apps_have_at_most_one() -> None:
    for library in ("shared_library_system", "shared_library_arc3"):
        assert not list((WORKSPACES / library).glob("design/workflows/*.workflow.metta"))
    for workspace in WORKSPACES.iterdir():
        if workspace.is_dir():
            assert len(list(workspace.glob("design/workflows/*.workflow.metta"))) <= 1, workspace


def test_current_project_workflows_have_bound_english_descriptions() -> None:
    provider = get_filesystem_provider()
    described_workspaces = {
        "arc3_random_player",
        "arc3_rule_learning_demo",
        "atom_ant",
        "generate_count_to_ten",
        "image_perception_to_recognizable_memory_and_arc3",
        "omegaclaw_microatomspacing",
        "review_with_approval",
        "tic_tac_toe_learner",
        "titlecase_demo",
        "vision_learn_by_observation",
        "vision_observe_choose_record",
        "visual_learning_from_examples",
        "workflow_engine_tour",
    }

    for workspace_id in described_workspaces:
        workflow_paths = list((WORKSPACES / workspace_id).glob("design/workflows/*.workflow.metta"))
        assert len(workflow_paths) == 1, workspace_id
        workflow_path = workflow_paths[0]
        documents = provider.read_json_documents(workflow_path)
        assert len(documents) == 1, workflow_path

        generation = documents[0].get("generation")
        assert isinstance(generation, dict), workflow_path
        assert generation.get("operation") == "workflow.populate_from_english", workflow_path

        relative_path = generation.get("englishDescriptionPath")
        assert isinstance(relative_path, str) and relative_path.endswith(".md"), workflow_path
        description_path = workflow_path.parents[2] / relative_path
        assert description_path.is_file(), description_path
        assert len(description_path.read_text(encoding="utf-8").strip()) >= 200, description_path


def test_visual_learning_workflow_owns_an_application_workspace() -> None:
    assert (WORKSPACES / "vision_learn_by_observation" / "design" / "workflows" / "vision_learn_by_observation.workflow.metta").is_file()
    assert not (WORKSPACES / "default" / "design" / "workflows" / "vision_learn_by_observation.workflow.metta").exists()


def test_retired_router_probe_is_removed() -> None:
    assert not (ROOT / "tests" / "test_openrouter.py").exists()
def test_arc3_random_player_workflow_resolves_shared_operations() -> None:
    from workspace_api import workspace_snapshot

    snapshot = workspace_snapshot("arc3_random_player", "full")
    operation_ids = {row["document"]["id"] for row in snapshot["operations"] if row.get("document")}
    implementation_ids = {row["document"]["id"] for row in snapshot["operationImplementations"] if row.get("document")}
    assert "arc3_random.discover_games" in operation_ids
    assert "arc3_random.discover_games.python" in implementation_ids
