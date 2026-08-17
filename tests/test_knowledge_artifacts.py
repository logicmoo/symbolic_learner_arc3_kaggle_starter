from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_knowledge_artifacts_are_separate_from_the_active_run_explorer() -> None:
    page = (ROOT / "workbench" / "frontend" / "src" / "pages" / "FilesystemWorkbenchPage.tsx").read_text(encoding="utf-8")
    explorer = (ROOT / "workbench" / "frontend" / "src" / "components" / "KnowledgeArtifactExplorer.tsx").read_text(encoding="utf-8")
    compact = "".join(page.split())

    assert 'label:"Artifacts",view:"knowledgeArtifacts"' in compact
    assert 'view==="knowledgeArtifacts"&&(<KnowledgeArtifactExplorer' in compact
    assert 'view === "artifacts" && (' in page
    assert "run.artifacts.map" in page
    assert "PERSISTENT TYPED OUTPUTS" in explorer
    assert "The Workflow Artifact Explorer remains scoped to the active run" in explorer
    assert "artifacts?|outputs?" in explorer
    assert "/asset?path=" in explorer
