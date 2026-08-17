from pathlib import Path

import pytest

from action_tree import ActionTreeStore
from object_memory import (
    CommittedAtom,
    EvidencePolarity,
    EvidenceRecord,
    InstanceMatcher,
    InstanceParameters,
    ProvenanceRef,
    RegistryCorrespondenceAuthority,
    SingleWriter,
    SymbolicMemory,
)


def _fixture(tmp_path: Path):
    store = ActionTreeStore(tmp_path / "tree", "game", 1)
    node = store.create_initial(b"png", {"state": "active"})
    node.objects_path.write_text(
        "new_object_identity(red_ball, object, 'red ball').\n",
        encoding="utf-8",
    )
    store.update_registry_from_objects(node)
    memory = SymbolicMemory()
    writer = SingleWriter(memory)
    writer.commit(CommittedAtom("red_ball", "object", {}))
    instance = InstanceParameters(
        position=(1.0, 2.0),
        appearance={"color": "red", "shape": "circle"},
        supported_transformations=("translation",),
    )
    proposals = InstanceMatcher().proposals(
        candidate_id="candidate-red",
        current=instance,
        stored={"red_ball": instance},
    )
    return store, writer, proposals


def test_registry_authority_requires_evidence_even_for_perfect_similarity(tmp_path: Path) -> None:
    store, writer, proposals = _fixture(tmp_path)
    authority = RegistryCorrespondenceAuthority(writer, store)

    assert proposals[0].similarity == 1.0
    with pytest.raises(ValueError, match="requires attributable evidence"):
        authority.accept(
            candidate_id="candidate-red",
            selected_identity_id="red_ball",
            proposals=proposals,
            evidence=(),
            encounter_id="encounter-1",
            decision_id="decision-1",
            decision_source="single_writer",
        )


def test_registry_authority_calibrates_accounts_and_records_prolog_history(tmp_path: Path) -> None:
    store, writer, proposals = _fixture(tmp_path)
    authority = RegistryCorrespondenceAuthority(writer, store)
    evidence = EvidenceRecord.create(
        subject_id="red_ball",
        polarity=EvidencePolarity.SUPPORTS,
        source=ProvenanceRef("encounter-1", "grid_matcher"),
        weight=3.0,
        detail={"matched": ["color", "shape"]},
    )

    account = authority.accept(
        candidate_id="candidate-red",
        selected_identity_id="red_ball",
        proposals=proposals,
        evidence=(evidence,),
        encounter_id="encounter-1",
        decision_id="decision-1",
        decision_source="single_writer",
    )
    authority.reverse(
        identity_id="red_ball",
        encounter_id="encounter-2",
        decision_id="decision-1",
        evidence_ids=("evidence-false-match",),
    )

    assert account.stored_identity_id == "red_ball"
    assert account.calibrated_confidence == pytest.approx(0.75)
    assert account.supporting_evidence_ids == (evidence.evidence_id,)
    history = store.semantic_identity_decisions_path.read_text(encoding="utf-8")
    assert "accepted" in history and "reversed" in history
    assert evidence.evidence_id in history


def test_registry_authority_records_explicit_rejection_without_calibration(tmp_path: Path) -> None:
    store, writer, proposals = _fixture(tmp_path)
    authority = RegistryCorrespondenceAuthority(writer, store)

    account = authority.reject(
        candidate_id="candidate-red",
        selected_identity_id="red_ball",
        proposals=proposals,
        encounter_id="encounter-1",
        decision_id="decision-reject-1",
        decision_source="explicit_registry_rejection",
    )

    assert account.stored_identity_id is None
    assert account.decision_source == "explicit_registry_rejection"
    assert writer.memory.evidence_for("red_ball") == ()
    history = store.semantic_identity_decisions_path.read_text(encoding="utf-8")
    assert "decision-reject-1" in history
    assert "rejected" in history
