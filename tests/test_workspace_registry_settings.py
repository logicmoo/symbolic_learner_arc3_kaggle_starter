import json
from pathlib import Path

import service_monitor_api
import workspace_api


def write_workspace(root: Path, workspace_id: str, **metadata: object) -> Path:
    path = root / workspace_id
    path.mkdir()
    (path / "workspace.json").write_text(json.dumps({"kind": "workspace", "id": workspace_id, "label": workspace_id, "includes": [], **metadata}), encoding="utf-8")
    return path


def test_hidden_workspaces_are_administered_but_not_offered_by_chooser(tmp_path: Path, monkeypatch) -> None:
    write_workspace(tmp_path, "visible")
    write_workspace(tmp_path, "hidden", hidden=True, workspaceType="library")
    monkeypatch.setattr(workspace_api, "_workspace_roots", lambda: [tmp_path])
    workspace_api.invalidate_workspace_discovery()
    assert [item["id"] for item in workspace_api.list_workspaces(refresh=True, detailed=False)["workspaces"]] == ["visible"]
    detailed = {item["id"]: item for item in workspace_api.list_workspaces(refresh=True, detailed=True)["workspaces"]}
    assert detailed["hidden"]["hidden"] is True
    assert detailed["hidden"]["workspaceType"] == "library"


def test_workspace_registry_settings_preserve_inclusions(tmp_path: Path, monkeypatch) -> None:
    root = write_workspace(tmp_path, "demo", includes=[])
    monkeypatch.setattr(workspace_api, "_workspace_roots", lambda: [tmp_path])
    workspace_api.invalidate_workspace_discovery()
    result = workspace_api.update_workspace_settings("demo", {"workspaceType": "library", "hidden": True})
    assert result["workspace"]["workspaceType"] == "library"
    assert result["workspace"]["hidden"] is True
    metadata = workspace_api.read_workspace_metadata(root)
    assert metadata["includes"] == []


def test_workspace_registry_source_editor_reads_and_preserves_full_document(tmp_path: Path, monkeypatch) -> None:
    root = write_workspace(tmp_path, "demo", includes=[], customField={"owner": "agent"})
    operations = root / "design" / "operations"
    operations.mkdir(parents=True)
    (operations / "demo.operation.metta").write_text("((kind operation) (id demo))", encoding="utf-8")
    monkeypatch.setattr(workspace_api, "_workspace_roots", lambda: [tmp_path])
    workspace_api.invalidate_workspace_discovery()
    loaded = workspace_api.get_workspace_settings("demo")
    assert loaded["document"]["customField"] == {"owner": "agent"}
    document = {**loaded["document"], "label": "Edited", "hidden": True}
    saved = workspace_api.update_workspace_settings("demo", {"document": document})
    assert saved["document"]["customField"] == {"owner": "agent"}
    assert workspace_api.read_workspace_metadata(root)["label"] == "Edited"
    assert loaded["workspace"]["fileCount"] == 2
    assert loaded["workspace"]["diskUsageBytes"] > 0
    assert loaded["workspace"]["resourceCounts"]["operations"] == 1


def test_workspace_registry_source_editor_rejects_id_change(tmp_path: Path, monkeypatch) -> None:
    write_workspace(tmp_path, "demo", includes=[])
    monkeypatch.setattr(workspace_api, "_workspace_roots", lambda: [tmp_path])
    workspace_api.invalidate_workspace_discovery()
    try:
        workspace_api.update_workspace_settings("demo", {"document": {"kind": "workspace", "id": "other"}})
    except workspace_api.HTTPException as error:
        assert error.status_code == 400
        assert "id cannot be changed" in str(error.detail)
    else:
        raise AssertionError("workspace id change should fail")


def test_settings_resource_counts_exclude_inherited_resources(tmp_path: Path, monkeypatch) -> None:
    parent = write_workspace(tmp_path, "parent", includes=[])
    operations = parent / "design" / "operations"
    operations.mkdir(parents=True)
    (operations / "parent.operation.metta").write_text("((kind operation) (id parent_op))", encoding="utf-8")
    write_workspace(tmp_path, "child", includes=[{"workspaceId": "parent", "includeInherited": True}])
    child = tmp_path / "child"
    assert workspace_api._local_resource_counts(parent)["operations"] == 1
    assert workspace_api._local_resource_counts(child).get("operations", 0) == 0
    monkeypatch.setattr(workspace_api, "_workspace_roots", lambda: [tmp_path])
    workspace_api.invalidate_workspace_discovery()
    discovered = {item["id"]: item for item in workspace_api.discover_workspaces(force=True, include_counts=False)}
    assert discovered["parent"]["usedByProjectCount"] == 1
    assert discovered["parent"]["usedByProjects"] == ["child"]
    assert discovered["child"]["usedByProjectCount"] == 0
    assert discovered["child"]["consumedProjectCount"] == 1
    assert discovered["child"]["consumedProjects"] == ["parent"]
    assert discovered["parent"]["consumedProjectCount"] == 0


def test_workspace_chooser_breakdowns_include_local_inherited_and_overridden(tmp_path: Path, monkeypatch) -> None:
    parent = write_workspace(tmp_path, "parent", includes=[])
    child = write_workspace(
        tmp_path,
        "child",
        includes=[{"workspaceId": "parent", "includeInherited": True}],
    )
    parent_operations = parent / "design" / "operations"
    parent_operations.mkdir(parents=True)
    (parent_operations / "shared.operation.metta").write_text(
        "((kind operation) (id shared_operation))",
        encoding="utf-8",
    )
    (parent_operations / "parent_only.operation.metta").write_text(
        "((kind operation) (id parent_only_operation))",
        encoding="utf-8",
    )
    child_operations = child / "design" / "operations"
    child_operations.mkdir(parents=True)
    (child_operations / "shared_override.operation.metta").write_text(
        "((kind operation) (id shared_operation))",
        encoding="utf-8",
    )
    for name in (
        "load_workspace_backend_records",
        "resolve_model_records",
        "load_workspace_prompt_records",
        "load_workspace_operation_records",
        "load_workspace_operation_implementation_records",
        "load_workspace_datatype_records",
        "load_workspace_representation_records",
        "load_workspace_concrete_datatype_records",
        "load_workspace_symbolic_records",
    ):
        monkeypatch.setattr(workspace_api, name, lambda *_args, **_kwargs: [])
    monkeypatch.setattr(workspace_api, "_workspace_roots", lambda: [tmp_path])
    workspace_api.invalidate_workspace_discovery()

    detailed = {
        item["id"]: item
        for item in workspace_api.list_workspaces(refresh=True, detailed=True)[
            "workspaces"
        ]
    }
    counts = detailed["child"]["resourceCountBreakdowns"]["operations"]
    assert counts["total"] == 2
    assert counts["local"] == 1
    assert counts["inherited"] == 1
    assert counts["overridden"] == 1


def test_startup_policy_exposes_start_and_window_visibility(tmp_path: Path, monkeypatch) -> None:
    policy_path = tmp_path / "workbench_startup.json"
    policy_path.write_text(json.dumps({"services": {"clawrouter": {"start": False, "hidden": True}}}), encoding="utf-8")
    monkeypatch.setattr(service_monitor_api, "STARTUP_POLICY_PATH", policy_path)
    monkeypatch.setattr(service_monitor_api, "LEGACY_STARTUP_POLICY_PATH", tmp_path / "missing.json")
    policy = service_monitor_api._startup_policy()
    assert policy["clawrouter"] == {"start": False, "hiddenWindow": True, "hideFromProcessViewer": False}
    assert policy["workbench-api"]["start"] is True


def test_startup_policy_writes_physical_metta_resource(tmp_path: Path, monkeypatch) -> None:
    logical_path = tmp_path / "workbench_startup.workbench_startup_policy.json"
    monkeypatch.setattr(service_monitor_api, "STARTUP_POLICY_PATH", logical_path)
    monkeypatch.setattr(service_monitor_api, "LEGACY_STARTUP_POLICY_PATH", tmp_path / "missing.json")
    service_monitor_api.get_filesystem_provider().write_json(logical_path, {
        "kind": "workbench_startup_policy", "id": "workbench_startup",
        "services": {"omniroute": {"start": False, "hidden": True}},
    })
    assert logical_path.with_suffix(".metta").is_file()
    assert service_monitor_api._startup_policy()["omniroute"] == {"start": False, "hiddenWindow": True, "hideFromProcessViewer": False}


def test_startup_policy_document_is_editor_ready(monkeypatch) -> None:
    monkeypatch.setattr(service_monitor_api, "_read_policy_resource", lambda: {})
    document = service_monitor_api._startup_policy_document()
    assert document["kind"] == "workbench_startup_policy"
    assert document["id"] == "workbench_startup"
    assert document["services"]["omniroute"]["start"] is True
    assert document["services"]["omniroute"] == {"start": True, "hiddenWindow": False, "hideFromProcessViewer": False}


def test_policy_can_add_a_new_managed_process_without_code(monkeypatch) -> None:
    monkeypatch.setattr(service_monitor_api, "_read_managed_service_resources", lambda: {"demo": {
        "label": "Demo server", "description": "Configured in MeTTa", "port": 9123,
        "healthPath": "/health", "launcher": "scripts/demo.cmd", "workingDirectory": "scripts",
        "commandPatterns": ["demo-server"], "controllable": True,
        "allowKill": False, "allowRelaunch": True,
    }})
    definition = next(item for item in service_monitor_api._definitions(8000) if item.id == "demo")
    assert definition.port == 9123
    assert definition.launcher == service_monitor_api.ROOT / "scripts" / "demo.cmd"
    assert definition.working_directory == service_monitor_api.ROOT / "scripts"
    assert definition.allow_kill is False
    assert definition.allow_relaunch is True


def test_each_managed_service_is_an_independent_resource() -> None:
    configured = service_monitor_api._read_managed_service_resources()
    assert set(configured) >= {"workbench-api", "workbench-web", "mailbox_server", "clawrouter", "omniroute", "freerouter"}
    assert all(document["kind"] == "managed_service" for document in configured.values())
    assert all(document["singleton"] is True for document in configured.values())
    assert configured["mailbox_server"]["defaultStartup"] == {"start": True, "hiddenWindow": False}
    assert configured["omniroute"]["defaultStartup"] == {"start": True, "hiddenWindow": False}
    policy = service_monitor_api._read_policy_resource()
    assert set(policy["services"]["omniroute"]) == {"start", "hiddenWindow", "hideFromProcessViewer"}


def test_settings_ui_embeds_synchronized_startup_policy_source_editor() -> None:
    source = (Path(__file__).parents[1] / "workbench" / "frontend" / "src" / "components" / "WorkspaceSettingsPanel.tsx").read_text(encoding="utf-8")
    assert "<ResourceSourceEditor" in source
    assert 'label="Edit start, window visibility, and Process Viewer overrides"' in source
    assert "changeStartupPolicy" in source
    assert "startupPolicyValid" in source
    assert "RegistryWorkspaceSourceEditor" in source
    assert "Edit workspace MeTTa / JSON" in source
    assert "Save workspace metadata" in source
    assert "workspace-disk-summary" in source
    assert "workspace-resource-counts" in source
    assert "workspace-project-usage" in source
    assert "WORKSPACE RESOURCE COUNTING" in source
    assert "workspaceResourceCountingEnabled" in source
    assert "worker pool" in source


def test_workspace_chooser_has_enumerate_resource_counts_button() -> None:
    source = (Path(__file__).parents[1] / "workbench" / "frontend" / "src" / "pages" / "FilesystemWorkbenchPage.tsx").read_text(encoding="utf-8")
    assert "workspace-count-actions" in source
    assert "workspace-count-enumerate" in source
    assert "Enumerate resource counts" in source
    assert "Recount resource counts" in source
    assert "setWorkspaceResourceCountingEnabled(true)" in source
    assert '/workbench/workspaces?detailed=true' in source


def test_workspace_chooser_enumerate_button_is_styled() -> None:
    source = (Path(__file__).parents[1] / "workbench" / "frontend" / "src" / "styles" / "workspace_backed.css").read_text(encoding="utf-8")
    assert ".workspace-count-actions" in source
    assert ".workspace-count-enumerate" in source
