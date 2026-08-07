from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi import HTTPException

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "workbench" / "server"
sys.path.insert(0, str(SERVER))

import repository_docs_api  # noqa: E402


def test_repository_markdown_endpoint_reads_only_markdown(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(repository_docs_api, "REPOSITORY_ROOT", tmp_path)
    (tmp_path / "README.md").write_text("# Repository", encoding="utf-8")
    assert repository_docs_api.read_repository_markdown("README.md") == {"path": "README.md", "content": "# Repository"}
    with pytest.raises(HTTPException) as outside:
        repository_docs_api.read_repository_markdown("../README.md")
    assert outside.value.status_code == 400
    with pytest.raises(HTTPException) as non_markdown:
        repository_docs_api.read_repository_markdown("settings.json")
    assert non_markdown.value.status_code == 400


def test_help_view_intercepts_repository_markdown_links() -> None:
    source = (ROOT / "workbench" / "frontend" / "src" / "components" / "HelpDocumentTabs.tsx").read_text(encoding="utf-8")
    assert "/api/repository/markdown?path=" in source
    assert "resolveMarkdownPath(document.path,href)" in source
    assert "event.preventDefault()" in source
    assert "← Back" in source
