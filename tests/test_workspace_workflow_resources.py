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


def test_default_inherits_shared_visual_learning_workflow() -> None:
    assert (WORKSPACES / "shared_library_system" / "design" / "workflows" / "vision_learn_by_observation.workflow.metta").is_file()
    assert not (WORKSPACES / "default" / "design" / "workflows" / "vision_learn_by_observation.workflow.metta").exists()


def test_openrouter_probe_never_prints_the_key() -> None:
    source = (ROOT / "tests" / "test_openrouter.py").read_text(encoding="utf-8")
    assert 'print("my_api_key used:"' not in source
    assert "its value will not be displayed" in source
