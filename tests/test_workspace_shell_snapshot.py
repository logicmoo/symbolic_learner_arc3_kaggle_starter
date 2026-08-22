from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "workbench" / "server"
if str(SERVER) not in sys.path:
    sys.path.insert(0, str(SERVER))

import workspace_api


def test_shell_snapshot_skips_editor_specific_catalogs(tmp_path: Path, monkeypatch) -> None:
    workspace = {"id": "test", "label": "Test", "root": str(tmp_path)}
    monkeypatch.setattr(workspace_api, "_resolve_workspace_without_counts", lambda _workspace_id: workspace)
    monkeypatch.setattr(workspace_api, "_load_workflows", lambda _workspace: [])
    monkeypatch.setattr(workspace_api, "_load_workflow_pages", lambda _workspace: [])
    monkeypatch.setattr(workspace_api, "_load_symbolic_family", lambda _workspace, _family: [])

    def unexpected(_workspace):
        raise AssertionError("shell snapshot loaded an editor-specific catalog")

    for name in (
        "_load_operations",
        "_load_operation_implementations",
        "_load_datatypes",
        "_load_representations",
        "_load_concrete_datatypes",
        "_load_backends",
        "_load_backend_library",
        "_load_models",
        "_load_model_library",
        "_load_prompts",
        "_load_prompt_library",
        "_load_artifact_categories",
    ):
        monkeypatch.setattr(workspace_api, name, unexpected)

    payload = workspace_api.workspace_snapshot("test", "shell")
    assert set(payload) == {"workspace", "workflows", "workflowPages", "goals", "plans", "contexts", "files"}


def test_workflow_pages_are_effective_inherited_filesystem_resources() -> None:
    records = workspace_api._load_workflow_pages(
        workspace_api._resolve_workspace("arc3_random_player"),
    )
    by_id = {record["document"]["id"]: record for record in records}

    assert by_id["workbench.generate_workflow"]["source"] == "shared"
    assert by_id["workbench.generate_workflow"]["workspaceId"] == "shared_library_system"
    assert by_id["workbench.generate_workflow"]["document"]["label"] == "Generate Workflow"
    assert by_id["workbench.generate_workflow"]["document"]["menuPlacement"] == "first"
    assert by_id["workbench.generate_workflow"]["document"]["layout"]["kind"] == "three_column_accordion"
    assert by_id["arc3.visual_sequencing"]["source"] == "workspace"
    assert by_id["arc3.visual_sequencing"]["document"]["label"] == "Visual Sequencing"
    assert by_id["arc3.visual_sequencing"]["document"]["menuPlacement"] == "middle"


def test_workflow_page_files_are_enumerated_in_menu_placement_order(tmp_path: Path) -> None:
    directory = tmp_path / "design" / "workflow_pages"
    directory.mkdir(parents=True)

    def page(page_id: str, label: str, placement: str, order: int) -> dict[str, object]:
        return {
            "kind": "workflow_page",
            "id": page_id,
            "label": label,
            "menuPlacement": placement,
            "order": order,
            "routeView": "englishWorkflow",
            "renderer": "english_workflow",
            "layout": {
                "kind": "three_column_accordion",
                "columns": [
                    {"id": "left", "label": "LEFT", "members": []},
                    {"id": "center", "label": "CENTER", "members": []},
                    {"id": "right", "label": "RIGHT", "members": []},
                ],
            },
        }

    for page_id, label, placement, order in (
        ("last", "Last", "last", 1),
        ("middle_b", "Middle B", "middle", 20),
        ("first", "First", "first", 500),
        ("middle_a", "Middle A", "middle", 10),
    ):
        (directory / f"{page_id}.workflow_page.json").write_text(
            json.dumps(page(page_id, label, placement, order)),
            encoding="utf-8",
        )

    records = workspace_api._load_workflow_pages(
        {"id": "test", "label": "Test", "root": str(tmp_path)},
    )

    assert [record["document"]["id"] for record in records] == [
        "first",
        "middle_a",
        "middle_b",
        "last",
    ]


def test_three_column_page_source_requires_its_own_json_inspector() -> None:
    document = {
        "kind": "workflow_page",
        "id": "test.page",
        "label": "Test Page",
        "routeView": "testPage",
        "renderer": "test_page",
        "layout": {
            "kind": "three_column_accordion",
            "columns": [
                {"id": "left", "label": "LEFT", "members": []},
                {"id": "center", "label": "CENTER", "members": []},
                {"id": "right", "label": "RIGHT", "members": []},
            ],
        },
    }

    with pytest.raises(ValueError, match="ResourceSourceEditor"):
        workspace_api._validate_workflow_page_definition(document, "test.page")

    document["layout"]["columns"][2]["members"].append({
        "id": "page_source",
        "component": "ResourceSourceEditor",
        "resource": {"kind": "workflow_page", "id": "test.page"},
    })
    assert workspace_api._validate_workflow_page_definition(document, "test.page") is document


def test_active_ui_requests_shell_snapshot() -> None:
    source = (ROOT / "workbench" / "frontend" / "src" / "pages" / "FilesystemWorkbenchPage.tsx").read_text(encoding="utf-8")
    assert source.count("/snapshot?scope=shell") == 3


def test_workspace_chooser_exposes_resource_counting_toggle_state() -> None:
    source = (ROOT / "workbench" / "frontend" / "src" / "pages" / "FilesystemWorkbenchPage.tsx").read_text(encoding="utf-8")
    assert "WORKSPACE_RESOURCE_COUNTING_STORAGE_KEY" in source
    assert "workbench.workspaceResourceCountingEnabled" in source
    assert "WORKSPACE RESOURCE COUNTING DISABLED" in source
    assert "worker pool" in source


def test_workflow_catalog_does_not_require_an_english_description(tmp_path: Path) -> None:
    workflow_directory = tmp_path / "design" / "workflows"
    workflow_directory.mkdir(parents=True)
    (workflow_directory / "catalog_only.workflow.json").write_text(
        '{"kind":"workflow","id":"catalog_only","label":"Catalog Only","steps":[]}',
        encoding="utf-8",
    )

    records = workspace_api._load_workflows(
        {"id": "test", "label": "Test", "root": str(tmp_path)},
    )

    assert [record["document"]["id"] for record in records] == ["catalog_only"]
    assert "generation" not in records[0]["document"]


def test_workspace_discovery_reuses_summary_until_refresh(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path / "demo"
    root.mkdir()
    calls: list[Path] = []
    monkeypatch.setattr(workspace_api, "_workspace_roots", lambda: [tmp_path])
    monkeypatch.setattr(workspace_api, "_workspace_from_directory", lambda path, **_kwargs: calls.append(path) or {"id": path.name, "label": path.name, "root": str(path)})
    workspace_api.invalidate_workspace_discovery()

    assert workspace_api.discover_workspaces()[0]["id"] == "demo"
    assert workspace_api.discover_workspaces()[0]["id"] == "demo"
    assert len(calls) == 1
    workspace_api.discover_workspaces(force=True)
    assert len(calls) == 2


def test_lightweight_workspace_chooser_skips_catalog_resolution(tmp_path: Path, monkeypatch) -> None:
    (tmp_path / "workspace.json").write_text('{"label":"Demo"}', encoding="utf-8")

    def unexpected(*_args, **_kwargs):
        raise AssertionError("workspace chooser resolved a resource catalog")

    for name in (
        "load_workspace_backend_records", "resolve_model_records", "load_workspace_prompt_records",
        "load_workspace_operation_records", "load_workspace_operation_implementation_records",
        "load_workspace_datatype_records", "load_workspace_representation_records",
        "load_workspace_concrete_datatype_records", "load_workspace_symbolic_records",
    ):
        monkeypatch.setattr(workspace_api, name, unexpected)

    summary = workspace_api._workspace_from_directory(tmp_path, include_counts=False)
    assert summary["label"] == "Demo"
    assert summary["countsAvailable"] is False


def test_direct_workspace_file_resolution_skips_catalog_counts(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path / "demo"
    root.mkdir()
    calls: list[bool] = []
    monkeypatch.setattr(workspace_api, "_workspace_roots", lambda: [tmp_path])
    original = workspace_api._workspace_from_directory

    def capture(path: Path, *, include_counts: bool = True):
        calls.append(include_counts)
        return original(path, include_counts=include_counts)

    monkeypatch.setattr(workspace_api, "_workspace_from_directory", capture)
    resolved = workspace_api._resolve_workspace_without_counts("demo")
    assert resolved["root"] == str(root.resolve())
    assert calls == [False]


def test_workspace_file_endpoint_uses_lightweight_resolution() -> None:
    source = (ROOT / "workbench" / "server" / "workspace_api.py").read_text(encoding="utf-8")
    endpoint = source.split("def read_workspace_file", 1)[1].split("@router.get", 1)[0]
    assert "_resolve_workspace_without_counts(workspace_id)" in endpoint
    assert "_resolve_workspace(workspace_id)" not in endpoint


def test_shell_snapshot_endpoint_uses_lightweight_resolution() -> None:
    source = (ROOT / "workbench" / "server" / "workspace_api.py").read_text(encoding="utf-8")
    endpoint = source.split("def workspace_snapshot", 1)[1].split("def _collect_shell_files", 1)[0]
    assert "_resolve_workspace_without_counts(workspace_id)" in endpoint
    assert "_resolve_workspace(workspace_id)" not in endpoint


def test_collect_shell_files_filters_by_suffix_respects_limit_and_ignores_dirs(tmp_path: Path) -> None:
    (tmp_path / "state.json").write_text("{}", encoding="utf-8")
    (tmp_path / "notes.md").write_text("hi", encoding="utf-8")
    (tmp_path / "image.png").write_bytes(b"\x89PNG")
    ignored = tmp_path / "node_modules"
    ignored.mkdir()
    (ignored / "ignored.json").write_text("{}", encoding="utf-8")

    files = workspace_api._collect_shell_files(tmp_path, limit=2000)
    paths = {record["path"] for record in files}
    assert paths == {"state.json", "notes.md"}

    limited = workspace_api._collect_shell_files(tmp_path, limit=1)
    assert len(limited) == 1
