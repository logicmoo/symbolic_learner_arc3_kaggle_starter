import pytest

from object_memory import (
    CommittedAtom,
    EvidencePolarity,
    EvidenceRecord,
    IdentityDecision,
    MergeDecision,
    InMemorySemanticBackend,
    ProvenanceRef,
    SingleWriter,
    SymbolicMemory,
    SymbolicStore,
)


def test_repeat_commit_preserves_existing_identity_confidence_and_history() -> None:
    memory = SymbolicMemory()
    writer = SingleWriter(memory)
    writer.commit(CommittedAtom("red_ball", "object", {"color": "red"}))
    evidence = EvidenceRecord.create(
        subject_id="red_ball",
        polarity=EvidencePolarity.SUPPORTS,
        source=ProvenanceRef("encounter", "fixture"),
        weight=3.0,
    )
    supported = writer.apply_evidence("red_ball", evidence)

    repeated = writer.commit(
        CommittedAtom("red_ball", "object", {"color": "red"}, confidence=0.99)
    )

    assert repeated is supported
    assert repeated.confidence == pytest.approx(0.75)
    assert [item.event for item in memory.confidence_history("red_ball")] == [
        "commit",
        "evidence_calibrated",
    ]
    with pytest.raises(ValueError, match="Identity conflict"):
        writer.commit(CommittedAtom("red_ball", "object", {"color": "blue"}))


def test_confidence_history_survives_lifecycle_and_reversal() -> None:
    memory = SymbolicMemory()
    writer = SingleWriter(memory)
    writer.commit(CommittedAtom("red_one", "object", {"color": "red"}))
    writer.commit(CommittedAtom("red_two", "object", {"color": "red"}))
    decision = MergeDecision.create(
        identity_ids=("red_one", "red_two"),
        resulting_identity_id="red_ball",
        status=IdentityDecision.ACCEPTED,
        evidence_ids=("merge-evidence",),
    )

    writer.merge_identities(
        decision,
        CommittedAtom("red_ball", "object", {"color": "red"}),
    )
    writer.tombstone("red_ball", "superseded")
    writer.reverse_identity_decision(decision.decision_id, "reviewed")

    assert [(item.event, item.lifecycle_state) for item in memory.confidence_history("red_ball")] == [
        ("merge_result", "active"),
        ("tombstone", "tombstoned"),
        ("identity_decision_reversed", "tombstoned"),
    ]
    assert memory.confidence_history("red_one")[-1].event == "identity_decision_reversed"
    assert memory.confidence_history("red_one")[-1].lifecycle_state == "active"

    store = SymbolicStore(InMemorySemanticBackend())
    for handle in ("red_one", "red_two", "red_ball"):
        for record in memory.confidence_history(handle):
            store.put_confidence_history(record)
    replayed = SymbolicStore(InMemorySemanticBackend()).replay(store.snapshot())
    assert replayed.values("confidence_history") == store.values("confidence_history")
