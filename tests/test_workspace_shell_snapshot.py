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
