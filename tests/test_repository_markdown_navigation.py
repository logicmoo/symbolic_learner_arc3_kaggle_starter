from __future__ import annotations

import json
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
    opened = repository_docs_api.read_repository_file("example.py")
    assert opened["path"] == "example.py"
    assert opened["content"] == "print('open')"
    assert opened["format"] == "source"
    assert opened["checksum"] == repository_docs_api._file_revision((tmp_path / "example.py").stat())
    assert opened["contentChecksum"] == "0849a4786f3ca8f6e61d9ebfacd39c2206e11727b4b7f8d28bcc8aabe4cedbd9"
    (tmp_path / ".env").write_text("SECRET=value", encoding="utf-8")
    with pytest.raises(HTTPException) as secret:
        repository_docs_api.read_repository_file(".env")
    assert secret.value.status_code == 403


def test_repository_filesystem_index_separates_exposed_and_sensitive_files(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(repository_docs_api, "REPOSITORY_ROOT", tmp_path)
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "guide.md").write_text("# Guide", encoding="utf-8")
    (tmp_path / "runner.py").write_text("print('safe')", encoding="utf-8")
    (tmp_path / ".env").write_text("API_KEY=never-return-this", encoding="utf-8")
    (tmp_path / "client.pem").write_text("private material", encoding="utf-8")
    (tmp_path / "archive.zip").write_bytes(b"not browser safe")

    payload = repository_docs_api.list_repository_filesystem()
    assert [item["path"] for item in payload["files"]] == ["docs/guide.md", "runner.py"]
    excluded = {item["path"]: item["reason"] for item in payload["unexposed"]}
    assert "credentials" in excluded[".env"]
    assert "credentials" in excluded["client.pem"]
    assert "not approved" in excluded["archive.zip"]
    assert all("content" not in item for item in payload["unexposed"])


def test_repository_json_and_metta_files_can_be_updated(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(repository_docs_api, "REPOSITORY_ROOT", tmp_path)
    json_file = tmp_path / "config.json"
    metta_file = tmp_path / "rule.metta"
    json_file.write_text('{"before": true}', encoding="utf-8")
    metta_file.write_text("(before)", encoding="utf-8")
    updated_json = repository_docs_api.update_repository_file(repository_docs_api.RepositoryFileUpdate(content='{"after": true}'), "config.json")
    updated_metta = repository_docs_api.update_repository_file(repository_docs_api.RepositoryFileUpdate(content="(after)"), "rule.metta")
    assert json.loads(updated_json["content"]) == {"after": True}
    assert updated_metta["content"] == "(after)"
    with pytest.raises(HTTPException) as invalid:
        repository_docs_api.update_repository_file(repository_docs_api.RepositoryFileUpdate(content="{"), "config.json")
    assert invalid.value.status_code == 422


def test_repository_images_are_exposed_as_renderable_assets(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(repository_docs_api, "REPOSITORY_ROOT", tmp_path)
    image = tmp_path / "diagram.png"
    image.write_bytes(b"not-a-real-png")
    assert repository_docs_api.read_repository_file("diagram.png")["format"] == "image"
    asset = repository_docs_api.read_repository_asset("diagram.png")
    assert Path(asset.path) == image


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
    assert payload["documents"][0]["checksum"] == repository_docs_api._file_revision((tmp_path / "docs" / "GUIDE.md").stat())

    provider = repository_docs_api.get_filesystem_provider()
    original_read_text = provider.read_text
    monkeypatch.setattr(provider, "read_text", lambda _path: (_ for _ in ()).throw(AssertionError("index must not read document bodies")))
    assert repository_docs_api.list_repository_markdown()["documents"][0]["path"] == "docs/GUIDE.md"
    monkeypatch.setattr(provider, "read_text", original_read_text)

    components = ROOT / "workbench" / "frontend" / "src" / "components"
    help_source = (components / "HelpDocumentTabs.tsx").read_text(encoding="utf-8")
    docs_source = (components / "RepositoryDocsPage.tsx").read_text(encoding="utf-8")
    assert 'label:"Datatype Guide",repositoryPath:"docs/DATATYPES_MANIFEST_EXPLAINED.md"' in help_source
    assert "/api/repository/filesystem-index" in docs_source
    assert "/api/repository/file?path=" in docs_source
    assert 'opened.format==="markdown"' in docs_source
    assert 'history.length>0&&<button onClick={back}>← Back</button>' in docs_source
    assert 'href={local?"#":href}' in docs_source
    assert "event.stopPropagation()" in docs_source
    assert 'refreshing?"Refreshing...":"Refresh"' in docs_source
    assert "current.checksum!==opened.checksum" in docs_source
    assert 'initialFilter||".md|.metta|.json"' in docs_source
    assert "Contents of unexposed files never reach the browser" in docs_source
    assert "function buildFileTree" in docs_source
    assert "<FileTree node={tree}" in docs_source
    assert "repository-tree-sidebar" in docs_source
    assert 'selectPanel("tree")' in docs_source
    assert 'selectPanel("navigator")' in docs_source
    assert 'browserMode==="tree"' in docs_source
    assert "Exposed Tree" in docs_source
    assert "Exposed Navigator" in docs_source
    assert "Exposed Full Path" in docs_source
    assert "Unexposed Full Path" in docs_source
    assert "repository-full-paths" in docs_source
    assert 'method:"PUT"' in docs_source
    assert "Save to filesystem" in docs_source
    assert "Edit source" in docs_source
    assert "Rendered preview" in docs_source
    assert "@uiw/react-codemirror" in docs_source
    assert "/api/repository/asset?path=" in docs_source
    assert "Find in Tree" in docs_source
    assert "Find in Navigator" in docs_source
    assert "Find in Full Paths" in docs_source
    assert "data-repository-path" in docs_source
    assert 'split("|")' in docs_source
    assert ".md|.txt" in docs_source
    assert "File Name" in docs_source
    assert "File Size" in docs_source
    assert "Directory Name" in docs_source
    assert "Parent Name (is Directory)" in docs_source
    assert "Parent Bytes (is Directory)" in docs_source
    assert "Path Depth" in docs_source
    assert "Hide\"} .dotdirs" in docs_source
    assert "Hide\"} .dotfiles" in docs_source
    assert "isInDotDirectory" in docs_source
    assert "isDotFile" in docs_source
    assert 'useState("runtime/|venv/")' in docs_source
    assert "setHideDotDirectories]=useState(true)" in docs_source
    assert "setHideDotFiles]=useState(true)" in docs_source
    assert "Exclude repository files" in docs_source
    assert "directoryMetrics" in docs_source
    assert 'useState<"tree"|"navigator"|"paths">' in docs_source
    assert 'initialPanel==="tree"||initialPanel==="navigator"?initialPanel:"paths"' in docs_source
    assert "function FilesystemNavigator" in docs_source
    assert "filesystem-breadcrumbs" in docs_source
    assert "Parent directory" in docs_source
    assert "Close document" in docs_source
    assert "ignored_names=IGNORED_DIRECTORIES" in (SERVER / "repository_docs_api.py").read_text(encoding="utf-8")
    data_docs = (ROOT / "workbench" / "workspaces" / "shared_library_system" / "docs" / "data.md").read_text(encoding="utf-8")
    assert "[Browse Data documents](?docs=data)" in data_docs
    assert "[Browse datatype documents](?docs=datatype)" in data_docs
    assert 'new CustomEvent("workbench:open-docs"' in help_source
    page_source = (ROOT / "workbench" / "frontend" / "src" / "pages" / "FilesystemWorkbenchPage.tsx").read_text(encoding="utf-8")
    styles = (ROOT / "workbench" / "frontend" / "src" / "styles" / "workbench.css").read_text(encoding="utf-8")
    assert 'classList.toggle("docs-focused", view === "docs")' in page_source
    assert "body.docs-focused .workspace>.stages-panel" in styles
    assert "body.docs-focused .workspace>.inspector-resizer" in styles
    assert "body.docs-focused .workspace .view-tabs" in styles
    assert '.workbench[data-view="docs"] .workspace>.stages-panel' in styles
    assert '.workbench[data-view="docs"] .workspace>.resource-browser-resizer' in styles


def test_help_view_loads_only_the_active_document() -> None:
    source = (ROOT / "workbench" / "frontend" / "src" / "components" / "HelpDocumentTabs.tsx").read_text(encoding="utf-8")
    assert 'if(active==="context"||docs[active]||errors[active])return' in source
    assert "tabs.find(tab=>tab.id===active)" in source
    assert "for(const tab of docTabs)" not in source
