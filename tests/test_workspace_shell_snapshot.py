from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "workbench" / "server"
if str(SERVER) not in sys.path:
    sys.path.insert(0, str(SERVER))

import workspace_api


def test_shell_snapshot_skips_editor_specific_catalogs(tmp_path: Path, monkeypatch) -> None:
    workspace = {"id": "test", "label": "Test", "root": str(tmp_path)}
    monkeypatch.setattr(workspace_api, "_resolve_workspace", lambda _workspace_id: workspace)
    monkeypatch.setattr(workspace_api, "_load_workflows", lambda _workspace: [])
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
    assert set(payload) == {"workspace", "workflows", "goals", "plans", "contexts", "files"}


def test_active_ui_requests_shell_snapshot() -> None:
    source = (ROOT / "workbench" / "frontend" / "src" / "pages" / "FilesystemWorkbenchPage.tsx").read_text(encoding="utf-8")
    assert source.count("/snapshot?scope=shell") == 2


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
