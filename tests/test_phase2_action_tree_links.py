import json
from pathlib import Path

import pytest

from action_tree import ActionTreeStore
from object_memory import (
    EvidencePolarity,
    EvidenceRecord,
    InMemorySemanticBackend,
    PredictionGradeRecord,
    PredictionRecord,
    ProvenanceRef,
    SymbolicStore,
)


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


def test_action_tree_materializes_prediction_grade_and_evidence_history(
    tmp_path: Path,
) -> None:
    tree = ActionTreeStore(tmp_path / "tree", "game", 1)
    node = tree.create_initial(b"png", {"state": "active"})
    semantic = SymbolicStore(InMemorySemanticBackend())
    prediction = semantic.put_prediction(
        PredictionRecord(
            "prediction-1",
            "rule-1",
            "state-before",
            ({"effect": "move-right"},),
            10,
        )
    )
    evidence = semantic.put_evidence(
        EvidenceRecord.create(
            subject_id="rule-1",
            polarity=EvidencePolarity.SUPPORTS,
            source=ProvenanceRef.create(
                source_id="prediction-1",
                provider="prediction_evaluator",
                sequence=11,
            ),
            detail={"expected": "move-right", "observed": "move-right"},
            created_sequence=11,
        )
    )
    semantic.put_prediction_grade(
        PredictionGradeRecord(
            prediction_id=prediction.prediction_id,
            rule_id=prediction.rule_id,
            outcome_sequence=11,
            outcome={"effect": "move-right"},
            grade=1.0,
            evidence=("independent_outcome",),
            evidence_record_ids=(evidence.evidence_id,),
            prior_probability=None,
            calibrated_probability=2.0 / 3.0,
        )
    )

    manifest_path = tree.link_prediction_history(
        node, semantic, prediction.prediction_id
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert {item["record_type"] for item in manifest["records"]} == {
        "prediction",
        "prediction_grade",
        "evidence",
    }
    readme = node.readme_path.read_text(encoding="utf-8")
    assert "predicted before outcome at sequence `10`" in readme
    assert "outcome fields remain empty" in readme
    assert "independently observed outcome at sequence `11`" in readme
    assert "`None` → `0.6666666666666666`" in readme
    assert "1 evidence update(s)" in readme

    with pytest.raises(KeyError, match="Unknown persisted prediction"):
        tree.link_prediction_history(node, semantic, "prediction-missing")
