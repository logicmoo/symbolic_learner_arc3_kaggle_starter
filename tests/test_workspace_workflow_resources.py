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


def test_visual_learning_workflow_owns_an_application_workspace() -> None:
    assert (WORKSPACES / "vision_learn_by_observation" / "design" / "workflows" / "vision_learn_by_observation.workflow.metta").is_file()
    assert not (WORKSPACES / "default" / "design" / "workflows" / "vision_learn_by_observation.workflow.metta").exists()


def test_openrouter_probe_never_prints_the_key() -> None:
    source = (ROOT / "tests" / "test_openrouter.py").read_text(encoding="utf-8")
    assert 'print("my_api_key used:"' not in source
    assert "its value will not be displayed" in source
def test_arc3_random_player_workflow_resolves_shared_operations() -> None:
    from workspace_api import workspace_snapshot

    snapshot = workspace_snapshot("arc3_random_player", "full")
    operation_ids = {row["document"]["id"] for row in snapshot["operations"] if row.get("document")}
    implementation_ids = {row["document"]["id"] for row in snapshot["operationImplementations"] if row.get("document")}
    assert "arc3_random.discover_games" in operation_ids
    assert "arc3_random.discover_games.python" in implementation_ids
