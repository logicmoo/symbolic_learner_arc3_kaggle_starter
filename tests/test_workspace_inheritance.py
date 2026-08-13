from __future__ import annotations

import json
from pathlib import Path

import pytest

from backend_library import load_workspace_backend_records
from datatype_library import load_workspace_datatype_records
from goal_plan_library import load_workspace_symbolic_records
from model_library import resolve_model_records
from operation_library import load_workspace_operation_records
from policy_library import load_workspace_policy_records
from prompt_library import load_workspace_prompt_records
from workspace_api import _load_workflows, _normalize_include_specs
from workspace_inheritance import effective_workspace_layers


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def make_layers(tmp_path: Path, *, transitive: bool) -> tuple[Path, Path]:
    for workspace_id in ("shared_library_system", "base", "middle", "current"):
        (tmp_path / workspace_id).mkdir()
    write_json(tmp_path / "middle" / "workspace.json", {"kind": "workspace", "includes": [{"workspaceId": "base", "includeInherited": True}]})
    write_json(tmp_path / "current" / "workspace.json", {"kind": "workspace", "includes": [{"workspaceId": "shared_library_system", "includeInherited": True}, {"workspaceId": "middle", "includeInherited": transitive}]})
    return tmp_path / "current", tmp_path


def test_transitive_inheritance_is_explicit_and_ordered(tmp_path: Path) -> None:
    current, root = make_layers(tmp_path, transitive=False)
    assert [item.name for item in effective_workspace_layers(current, root)] == ["shared_library_system", "middle", "current"]
    write_json(current / "workspace.json", {"kind": "workspace", "includes": [{"workspaceId": "shared_library_system", "includeInherited": True}, {"workspaceId": "middle", "includeInherited": True}]})
    assert [item.name for item in effective_workspace_layers(current, root)] == ["shared_library_system", "base", "middle", "current"]


def test_shared_is_default_but_can_be_removed(tmp_path: Path) -> None:
    shared = tmp_path / "shared_library_system"; current = tmp_path / "current"
    shared.mkdir(); current.mkdir()
    assert [item.name for item in effective_workspace_layers(current, tmp_path)] == ["shared_library_system", "current"]
    write_json(current / "workspace.json", {"kind": "workspace", "includes": []})
    assert [item.name for item in effective_workspace_layers(current, tmp_path)] == ["current"]


def test_every_resource_family_uses_the_same_included_layers(tmp_path: Path) -> None:
    current, root = make_layers(tmp_path, transitive=True)
    base = root / "base"
    write_json(base / "operations" / "included.operation.json", {"kind": "operation", "id": "included_operation"})
    write_json(base / "datatypes" / "included.semantic_datatype.json", {"kind": "semantic_datatype", "id": "included_datatype"})
    write_json(base / "prompts" / "included.prompt.json", {"kind": "prompt", "id": "included_prompt"})
    write_json(base / "goals" / "included.goal.json", {"kind": "goal", "id": "included_goal"})
    write_json(base / "policies" / "included.vendor_policy.json", {"kind": "vendor_policy", "id": "included_policy"})
    write_json(base / "models" / "included.backend.json", {"kind": "backend", "id": "included_backend", "provider": "test"})
    write_json(base / "models" / "included.model.json", {"kind": "model", "id": "included_model", "inherits": "included_backend"})
    write_json(base / "workflows" / "included.workflow.json", {"kind": "workflow", "id": "included_workflow", "steps": []})

    checks = [
        (load_workspace_operation_records(current, workspaces_root=root), "included_operation"),
        (load_workspace_datatype_records(current, workspaces_root=root), "included_datatype"),
        (load_workspace_prompt_records(current, workspaces_root=root), "included_prompt"),
        (load_workspace_symbolic_records(current, "goal", workspaces_root=root), "included_goal"),
        (load_workspace_policy_records(current, workspaces_root=root), "included_policy"),
        (load_workspace_backend_records(current, workspaces_root=root), "included_backend"),
        (resolve_model_records(current, workspaces_root=root), "included_model"),
        (_load_workflows({"root": str(current)}), "included_workflow"),
    ]
    for records, expected_id in checks:
        record = next(item for item in records if (item.get("document") or {}).get("id") == expected_id)
        assert record["source"] == "included"
        assert record["workspaceId"] == "base"


def test_current_workspace_overrides_included_resource_id(tmp_path: Path) -> None:
    current, root = make_layers(tmp_path, transitive=True)
    write_json(root / "base" / "operations" / "same.operation.json", {"kind": "operation", "id": "same", "label": "Base"})
    write_json(current / "operations" / "same.operation.json", {"kind": "operation", "id": "same", "label": "Current"})
    records = load_workspace_operation_records(current, workspaces_root=root)
    record = next(item for item in records if item["document"]["id"] == "same")
    assert record["document"]["label"] == "Current"
    assert record["source"] == "workspace"


def test_settings_validation_rejects_cycles(tmp_path: Path, monkeypatch) -> None:
    current, root = make_layers(tmp_path, transitive=True)
    monkeypatch.setattr("workspace_api.discover_workspaces", lambda: [{"id": item.name, "root": str(item), "label": item.name} for item in root.iterdir() if item.is_dir()])
    workspace = {"id": "base", "root": str(root / "base"), "label": "Base"}
    with pytest.raises(ValueError, match="cycle"):
        _normalize_include_specs(workspace, [{"workspaceId": "current", "includeInherited": True}])


def test_active_workflow_editor_opens_inherited_documents_from_snapshot() -> None:
    source = (Path(__file__).resolve().parents[1] / "workbench" / "frontend" / "src" / "pages" / "FilesystemWorkbenchPage.tsx").read_text(encoding="utf-8")
    assert 'row.workspaceId!==workspace.id' in source
    assert 'setWorkflowSource(JSON.stringify(inherited.document,null,2))' in source
