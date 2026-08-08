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


def test_repository_reader_repairs_mojibake_glyph_sequences() -> None:
    broken = "\u00e2\u2020\u0090 \u00e2\u201d\u0153\u00e2\u201d\u20ac\u00e2\u201d\u20ac \u00e2\u2020\u2019 \u00e2\u20ac\u0153quoted\u00e2\u20ac\u009d"
    assert repository_docs_api.repair_display_text(broken) == "← ├── → “quoted”"


def test_repository_file_endpoint_opens_linked_source_files_safely(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(repository_docs_api, "REPOSITORY_ROOT", tmp_path)
    (tmp_path / "example.py").write_text("print('open')", encoding="utf-8")
    assert repository_docs_api.read_repository_file("example.py") == {
        "path": "example.py",
        "content": "print('open')",
        "format": "source",
        "checksum": "0849a4786f3ca8f6e61d9ebfacd39c2206e11727b4b7f8d28bcc8aabe4cedbd9",
    }
    (tmp_path / ".env").write_text("SECRET=value", encoding="utf-8")
    with pytest.raises(HTTPException) as secret:
        repository_docs_api.read_repository_file(".env")
    assert secret.value.status_code == 400


def test_help_view_intercepts_repository_markdown_links() -> None:
    source = (ROOT / "workbench" / "frontend" / "src" / "components" / "HelpDocumentTabs.tsx").read_text(encoding="utf-8")
    assert "/api/repository/markdown?path=" in source
    assert "resolveMarkdownPath(document.path,href)" in source
    assert "event.preventDefault()" in source
    assert "← Back" in source


def test_repository_markdown_index_and_ui_links(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(repository_docs_api, "REPOSITORY_ROOT", tmp_path)
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "GUIDE.md").write_text("# Guide", encoding="utf-8")
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "README.md").write_text("dependency", encoding="utf-8")
    (tmp_path / "action_trees").mkdir()
    (tmp_path / "action_trees" / "README.md").write_text("runtime output", encoding="utf-8")
    payload = repository_docs_api.list_repository_markdown()
    assert [item["path"] for item in payload["documents"]] == ["docs/GUIDE.md"]

    components = ROOT / "workbench" / "frontend" / "src" / "components"
    help_source = (components / "HelpDocumentTabs.tsx").read_text(encoding="utf-8")
    docs_source = (components / "RepositoryDocsPage.tsx").read_text(encoding="utf-8")
    assert 'label:"Datatype Guide",repositoryPath:"docs/DATATYPES_MANIFEST_EXPLAINED.md"' in help_source
    assert "/api/repository/markdown-index" in docs_source
    assert "/api/repository/file?path=" in docs_source
    assert 'opened.format==="markdown"' in docs_source
    assert 'history.length>0&&<button onClick={back}>← Back</button>' in docs_source
    assert 'href={local?"#":href}' in docs_source
    assert "event.stopPropagation()" in docs_source
    assert 'refreshing?"Refreshing...":"Refresh"' in docs_source
    assert "current.checksum!==opened.checksum" in docs_source
    data_docs = (ROOT / "workbench" / "workspaces" / "shared" / "docs" / "data.md").read_text(encoding="utf-8")
    assert "[Browse Data documents](?docs=data)" in data_docs
    assert "[Browse datatype documents](?docs=datatype)" in data_docs
    assert 'new CustomEvent("workbench:open-docs"' in help_source
    page_source = (ROOT / "workbench" / "frontend" / "src" / "pages" / "FilesystemWorkbenchPage.tsx").read_text(encoding="utf-8")
    styles = (ROOT / "workbench" / "frontend" / "src" / "styles" / "workbench.css").read_text(encoding="utf-8")
    assert 'classList.toggle("docs-focused",view==="docs")' in page_source
    assert "body.docs-focused .workspace>.stages-panel" in styles
    assert "body.docs-focused .workspace>.inspector-resizer" in styles
    assert "body.docs-focused .workspace .view-tabs" in styles
