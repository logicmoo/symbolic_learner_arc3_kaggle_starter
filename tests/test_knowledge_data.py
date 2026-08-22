from __future__ import annotations

import base64
import sys
from pathlib import Path

import pytest
from fastapi import HTTPException


ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "workbench" / "server"
sys.path.insert(0, str(SERVER))

import workspace_api  # noqa: E402


def test_binary_data_import_uses_workspace_knowledge_storage(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(workspace_api, "_resolve_workspace_without_counts", lambda _workspace_id: {"id": "demo", "root": str(tmp_path)})
    payload = workspace_api.import_workspace_data("demo", {"files": [{"name": "frame.png", "base64": base64.b64encode(b"PNG").decode()}]})

    assert payload["directory"] == "knowledge/data/imports"
    assert payload["files"][0]["path"] == "knowledge/data/imports/frame.png"
    assert (tmp_path / "knowledge" / "data" / "imports" / "frame.png").read_bytes() == b"PNG"


def test_binary_data_import_rejects_unsafe_or_runtime_destinations(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(workspace_api, "_resolve_workspace_without_counts", lambda _workspace_id: {"id": "demo", "root": str(tmp_path)})
    with pytest.raises(HTTPException) as error:
        workspace_api.import_workspace_data("demo", {"directory": "runtime/logs", "files": [{"name": "x.bin", "base64": "eA=="}]})
    assert error.value.status_code == 400


def test_binary_data_import_requires_explicit_overwrite(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(workspace_api, "_resolve_workspace_without_counts", lambda _workspace_id: {"id": "demo", "root": str(tmp_path)})
    request = {"directory": "knowledge/data/photos", "files": [{"name": "x.bin", "base64": "eA=="}]}
    workspace_api.import_workspace_data("demo", request)
    with pytest.raises(HTTPException) as error:
        workspace_api.import_workspace_data("demo", request)
    assert "enable overwrite" in str(error.value.detail)
    replaced = workspace_api.import_workspace_data("demo", {**request, "overwrite": True})
    assert replaced["files"][0]["path"] == "knowledge/data/photos/x.bin"


def test_knowledge_data_page_imports_selects_and_previews_workspace_values() -> None:
    page = (ROOT / "workbench" / "frontend" / "src" / "components" / "KnowledgeDataExplorer.tsx").read_text(encoding="utf-8")
    shell = (ROOT / "workbench" / "frontend" / "src" / "pages" / "FilesystemWorkbenchPage.tsx").read_text(encoding="utf-8")

    assert 'busy?"Importing…":"Import Data"' in page
    assert 'type="file" multiple' in page
    assert 'aria-label="Data collection name"' in page
    assert "Replace same-name files" in page
    assert "directory:`knowledge/data/${collectionId}`" in page
    assert "overwrite}" in page
    assert "/data/import`" in page
    assert "knowledge-data-preview" in page
    assert "imageSuffixes.has" in page
    assert "/asset?path=" in page
    assert '^(knowledge|data|datasets|images|inputs|examples)' in page
    assert "onChanged={refreshSnapshot}" in shell
    assert 'view === "knowledgeData"' in shell and '? "data"' in shell
    assert 'view === "data"' in shell and '? "datatypeGuide"' in shell
