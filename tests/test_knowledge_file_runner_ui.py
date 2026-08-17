from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPONENTS = ROOT / "workbench" / "frontend" / "src" / "components"


def test_data_and_artifact_explorers_use_the_workspace_file_runner() -> None:
    data = (COMPONENTS / "KnowledgeDataExplorer.tsx").read_text(encoding="utf-8")
    artifacts = (COMPONENTS / "KnowledgeArtifactExplorer.tsx").read_text(encoding="utf-8")

    assert 'resourceKind="data"' in data
    assert 'resourceKind="artifact"' in artifacts
    assert "WorkspaceFileRunner" in data
    assert "WorkspaceFileRunner" in artifacts


def test_workspace_file_runner_loads_assets_through_the_workspace_api() -> None:
    source = (COMPONENTS / "WorkspaceFileRunner.tsx").read_text(encoding="utf-8")

    assert "/api/workspaces/" in source
    assert "/asset?path=" in source
    assert "ResourceExecutionPlayground" in source
    assert '"data_inspect"' in source
    assert '"artifact_inspect"' in source
    assert "data-url" in source


def test_universal_runner_separates_default_and_selected_operations() -> None:
    source = (COMPONENTS / "ResourceExecutionPlayground.tsx").read_text(encoding="utf-8")
    compact = "".join(source.split())

    assert "constdefaultOperation=operations[0]?.id" in compact
    assert "run(defaultOperation)" in source
    assert "run(selectedOperation)" in source
    assert "setSelectedOperation(current=>compatible.some" in compact
