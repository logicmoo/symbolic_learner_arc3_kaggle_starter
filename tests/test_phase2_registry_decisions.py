from pathlib import Path
import subprocess

import pytest

from action_tree import ActionTreeStore


def _store_with_identity(tmp_path: Path) -> tuple[ActionTreeStore, object]:
    store = ActionTreeStore(tmp_path / "tree", "game", 1)
    node = store.create_initial(b"png", {"state": "active"})
    node.objects_path.write_text(
        "new_object_identity(red_ball, object, 'red ball').\n",
        encoding="utf-8",
    )
    store.update_registry_from_objects(node)
    return store, node


def test_semantic_decisions_extend_friendly_registry_with_append_only_provenance(tmp_path: Path) -> None:
    store, node = _store_with_identity(tmp_path)
    values = dict(
        identity_id="red_ball",
        encounter_id="encounter-1",
        decision_id="decision-1",
        evidence_ids=("evidence-shape", "evidence-color"),
    )

    path = store.record_semantic_identity_decision(status="accepted", **values)
    store.record_semantic_identity_decision(status="accepted", **values)
    store.record_semantic_identity_decision(status="reversed", **values)

    source = path.read_text(encoding="utf-8")
    assert source.count("semantic_identity_decision(red_ball") == 2
    assert "accepted" in source and "reversed" in source
    assert '"evidence-shape"' in source
    registry = store.object_registry_path.read_text(encoding="utf-8")
    assert ":- ensure_loaded('semantic_identity_decisions.pl')." in registry
    assert "object_identity(red_ball, object, 'red ball')." in registry
    store.refresh_readme(node)
    readme = node.readme_path.read_text(encoding="utf-8")
    assert "## Identity registry provenance" in readme
    assert "**Canonical identities:** `1`" in readme
    assert "**Semantic decision history:** `2`" in readme
    assert "`red_ball` → `accepted`" in readme
    assert "encounter `encounter-1` via decision `decision-1`" in readme
    result = subprocess.run(
        [
            "swipl",
            "-q",
            "-s",
            str(store.object_registry_path),
            "-g",
            "findall(Status, semantic_identity_decision(red_ball,_,_,Status,_), Statuses), length(Statuses,2)",
            "-t",
            "halt",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def test_semantic_decision_rejects_unknown_or_opaque_candidate_identity(tmp_path: Path) -> None:
    store, _node = _store_with_identity(tmp_path)

    with pytest.raises(ValueError, match="not in object_registry"):
        store.record_semantic_identity_decision(
            identity_id="obj_red_1",
            encounter_id="encounter-1",
            decision_id="decision-1",
            status="accepted",
        )
