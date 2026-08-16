from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ACTIVE_PAGE = ROOT / "workbench" / "frontend" / "src" / "pages" / "FilesystemWorkbenchPage.tsx"


def test_artifact_explorer_uses_durable_engine_artifact_fields():
    source = ACTIVE_PAGE.read_text(encoding="utf-8")
    compact = "".join(source.split())

    assert "payload?:unknown" in compact
    assert "contentHash?:string" in compact
    assert "provenance?:Record<string,unknown>" in compact
    assert "selectedArtifact.payload" in source
    assert "selectedArtifact.contentHash" in source
    assert "selectedArtifact.provenance" in source
    assert "item.stepId" in source
    assert "item.producer" not in source
    assert "selectedArtifact.value" not in source
