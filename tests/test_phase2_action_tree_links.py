import json
from pathlib import Path

import pytest

from action_tree import ActionTreeStore


def test_action_tree_links_semantic_records_without_embedding_them_in_state(tmp_path: Path) -> None:
    store = ActionTreeStore(tmp_path / "tree", "game-12345678", 1)
    node = store.create_initial(b"png", {"state": "active"})
    artifact = tmp_path / "semantic" / "encounter-1.json"
    artifact.parent.mkdir()
    artifact.write_text('{"encounter_id":"encounter-1"}\n', encoding="utf-8")

    manifest = store.link_semantic_record(
        node,
        record_type="encounter",
        record_id="encounter-1",
        artifact_path=artifact,
        schema_version="2.0.0",
        deterministic_hash="abc123",
    )
    store.link_semantic_record(
        node,
        record_type="encounter",
        record_id="encounter-1",
        artifact_path=artifact,
        schema_version="2.0.0",
        deterministic_hash="abc123",
    )

    payload = json.loads(manifest.read_text(encoding="utf-8"))
    assert len(payload["records"]) == 1
    assert "encounter-1" not in node.state_path.read_text(encoding="utf-8")
    readme = node.readme_path.read_text(encoding="utf-8")
    assert "## Semantic records" in readme
    assert "**encounter** `encounter-1`" in readme
    assert "[open record]" in readme


def test_action_tree_rejects_conflicting_semantic_record_links(tmp_path: Path) -> None:
    store = ActionTreeStore(tmp_path / "tree", "game", 1)
    node = store.create_initial(b"png", {"state": "active"})
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    first.write_text("{}", encoding="utf-8")
    second.write_text("{}", encoding="utf-8")
    values = dict(
        record_type="observation",
        record_id="observation-1",
        schema_version="2.0.0",
        deterministic_hash="hash-1",
    )

    store.link_semantic_record(node, artifact_path=first, **values)
    with pytest.raises(RuntimeError, match="link conflict"):
        store.link_semantic_record(node, artifact_path=second, **values)
