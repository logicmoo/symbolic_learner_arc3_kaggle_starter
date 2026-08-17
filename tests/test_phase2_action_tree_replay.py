import json
from pathlib import Path

import pytest

from object_memory import (
    ActionTreeSemanticReplay,
    InMemorySemanticBackend,
    SemanticRecordCodec,
    SymbolicStore,
)


def test_action_tree_replay_ignores_nonsemantic_artifacts(tmp_path: Path) -> None:
    node = tmp_path / "node"
    node.mkdir()
    (node / "semantic_records.json").write_text(
        json.dumps(
            {
                "records": [
                    {
                        "record_type": "future_record",
                        "record_id": "future-1",
                        "artifact": "missing.future.json",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    store = ActionTreeSemanticReplay().replay(
        tmp_path, SymbolicStore(InMemorySemanticBackend())
    )

    assert all(not values for values in store.snapshot().values())


def test_semantic_record_codec_rejects_unknown_types() -> None:
    with pytest.raises(ValueError, match="unsupported semantic record type"):
        SemanticRecordCodec.decode("future_record", {})


def test_action_tree_replay_rejects_missing_encounter_predecessors(tmp_path: Path) -> None:
    node = tmp_path / "node"
    node.mkdir()
    artifact = node / "encounter.json"
    artifact.write_text(
        json.dumps(
            {
                "encounter_id": "encounter-child",
                "observation_id": "observation",
                "action_tree_node": "node",
                "previous_encounter_id": "missing-parent",
            }
        ),
        encoding="utf-8",
    )
    (node / "semantic_records.json").write_text(
        json.dumps(
            {
                "records": [
                    {
                        "record_type": "encounter",
                        "record_id": "encounter-child",
                        "artifact": "encounter.json",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="missing or cyclic predecessors"):
        ActionTreeSemanticReplay().replay(
            tmp_path, SymbolicStore(InMemorySemanticBackend())
        )
