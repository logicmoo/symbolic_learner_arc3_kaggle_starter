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
    "context": "atomspaces",
    "context_variant": "atomspace_variants",
    "concrete_datatype": "concrete_datatypes",
    "goal": "goals",
    "goal_interpretation": "goal_interpretations",
    "goal_variant": "goal_variants",
    "manifest": "manifests",
    "model": "models",
    "operation": "operations",
    "operation_implementation": "operation_implementations",
    "plan": "plans",
    "plan_variant": "plan_variants",
    "profile": "profiles",
    "prompt": "prompts",
    "prompt_implementation": "prompt_implementations",
    "representation_datatype": "representation_datatypes",
    "schema": "schemas",
    "semantic_datatype": "semantic_datatypes",
    "workflow": "workflows",
}


def test_shared_uses_lifecycle_first_top_level_directories() -> None:
    assert {path.name for path in SHARED.iterdir() if path.is_dir()} == {"design", "runtime", "policies", "docs"}


def test_shared_design_metta_directories_match_declared_kinds() -> None:
    resources = get_filesystem_provider()
    paths = list((SHARED / "design").rglob("*.metta"))
    assert paths
    for path in paths:
        document = resources.read_json(path.with_suffix(".json"))
        kind = document.get("kind")
        assert kind in KIND_DIRECTORIES, path.relative_to(SHARED).as_posix()
        assert path.parent.name == KIND_DIRECTORIES[kind], path.relative_to(SHARED).as_posix()


def test_shared_runtime_contains_no_design_documents() -> None:
    assert not list((SHARED / "runtime").rglob("*.metta"))


def test_every_workspace_uses_lifecycle_first_resource_directories() -> None:
    allowed = {"design", "runtime", "policies", "docs"}
    for workspace in WORKSPACES.iterdir():
        if not workspace.is_dir():
            continue
        assert {path.name for path in workspace.iterdir() if path.is_dir()} <= allowed, workspace.name
        for path in (workspace / "design").rglob("*.metta") if (workspace / "design").is_dir() else []:
            document = get_filesystem_provider().read_json(path.with_suffix(".json"))
            kind = document.get("kind")
            assert kind in KIND_DIRECTORIES, path.relative_to(WORKSPACES).as_posix()
            assert path.parent.name == KIND_DIRECTORIES[kind], path.relative_to(WORKSPACES).as_posix()
