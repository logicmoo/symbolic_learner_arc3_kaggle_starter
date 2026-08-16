from __future__ import annotations

from pathlib import Path

import workspace_api


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "workbench" / "workspaces" / "generate_count_to_ten"
SHARED_ROOT = ROOT / "workbench" / "workspaces" / "shared_library_system"


def test_generate_count_to_ten_is_a_real_discoverable_generation_project(monkeypatch) -> None:
    monkeypatch.setattr(workspace_api, "_workspace_roots", lambda: [ROOT / "workbench" / "workspaces"])
    workspace_api.invalidate_workspace_discovery()
    discovered = {item["id"]: item for item in workspace_api.discover_workspaces(force=True, include_counts=False)}
    project = discovered["generate_count_to_ten"]
    assert project["workspaceType"] == "project"
    assert project["includes"] == [{"workspaceId": "shared_library_system", "includeInherited": True}]
    assert (WORKSPACE / "design" / "workflows" / "generate_count_to_ten.workflow.metta").is_file()
    assert (WORKSPACE / "design" / "prompts" / "generate_count_to_ten_english_specification.prompt.metta").is_file()


def test_count_to_ten_target_starts_empty_and_points_to_the_generator() -> None:
    workspace = workspace_api._workspace_from_directory(WORKSPACE, include_counts=False)
    local = [record for record in workspace_api._load_workflows(workspace) if record.get("workspaceId") == "generate_count_to_ten"]
    target = next(record["document"] for record in local if record["document"]["id"] == "generate_count_to_ten")
    assert target["steps"] == []
    assert target["generation"]["operation"] == "workflow.populate_from_english"
    assert target["generation"]["englishSpecificationPrompt"] == "generate_count_to_ten.english_workflow_specification"
    assert target["generation"]["operationCategories"] == ["workflow-language"]
    assert "preferredFormat" not in target["generation"]
    assert (
        WORKSPACE / "policies" / "workspace_model_selection.model_runtime_policy.metta"
    ).is_file()


def test_shared_control_structures_are_workflow_language_operations() -> None:
    for name in ("control_loops.operation.metta", "control_conditionals.operation.metta"):
        source = (SHARED_ROOT / "design" / "operations" / name).read_text(encoding="utf-8")
        assert "workflow-language" in source


def test_count_to_ten_local_resources_contain_no_game_domain_language() -> None:
    forbidden = ("game", "arc3", "played", "move", "screenshot")
    authored_roots = [WORKSPACE / "design", WORKSPACE / "docs", WORKSPACE / "policies"]
    authored_files = [WORKSPACE / "workspace.json"]
    for root in authored_roots:
        authored_files.extend(path for path in root.rglob("*") if path.is_file())
    for path in authored_files:
        source = path.read_text(encoding="utf-8").lower()
        assert not any(term in source for term in forbidden), f"game-domain term leaked into {path}"
