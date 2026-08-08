from pathlib import Path

from resource_store import get_filesystem_provider


ROOT = Path(__file__).resolve().parents[1]
SHARED = ROOT / "workbench" / "workspaces" / "shared"
WORKSPACES = SHARED.parent

KIND_DIRECTORIES = {
    "artifact_category": "categories",
    "artifact_catalog": "artifact_catalogs",
    "backend": "backends",
    "config": "configs",
    "atomspace": "atomspaces",
    "concrete_datatype": "concrete_datatypes",
    "goal": "goals",
    "manifest": "manifests",
    "model": "models",
    "operation": "operations",
    "planning_strategy": "planning_strategies",
    "prompt": "prompts",
    "representation_datatype": "representation_datatypes",
    "schema": "schemas",
    "semantic_datatype": "semantic_datatypes",
    "workflow": "workflows",
}


def assert_resource_file_layout(path: Path, root: Path) -> None:
    documents = get_filesystem_provider().read_json_documents(path.with_suffix(".json"))
    assert documents
    for document in documents:
        assert document.get("kind") in KIND_DIRECTORIES, path.relative_to(root).as_posix()
    # A combined file is physically organized by its first (owning) resource;
    # sibling variants may follow it as additional top-level forms.
    assert path.parent.name == KIND_DIRECTORIES[documents[0]["kind"]], path.relative_to(root).as_posix()


def test_shared_uses_lifecycle_first_top_level_directories() -> None:
    assert {path.name for path in SHARED.iterdir() if path.is_dir()} == {"design", "runtime", "policies", "docs"}


def test_shared_design_metta_directories_match_declared_kinds() -> None:
    resources = get_filesystem_provider()
    paths = list((SHARED / "design").rglob("*.metta"))
    assert paths
    for path in paths:
        assert_resource_file_layout(path, SHARED)


def test_shared_runtime_contains_no_design_documents() -> None:
    assert not list((SHARED / "runtime").rglob("*.metta"))


def test_every_workspace_uses_lifecycle_first_resource_directories() -> None:
    allowed = {"design", "runtime", "policies", "docs"}
    for workspace in WORKSPACES.iterdir():
        if not workspace.is_dir():
            continue
        assert {path.name for path in workspace.iterdir() if path.is_dir()} <= allowed, workspace.name
        for path in (workspace / "design").rglob("*.metta") if (workspace / "design").is_dir() else []:
            assert_resource_file_layout(path, WORKSPACES)
