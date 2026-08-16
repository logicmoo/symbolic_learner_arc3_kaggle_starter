from object_memory import (
    CommittedAtom,
    IdentityDecision,
    MergeDecision,
    SingleWriter,
    SplitDecision,
    SymbolicMemory,
)


def test_merge_is_explicit_evidence_preserving_and_reversible() -> None:
    memory = SymbolicMemory()
    writer = SingleWriter(memory)
    writer.commit(CommittedAtom("red-1", "object", {"color": "red"}, provenance=("node-1",)))
    writer.commit(CommittedAtom("red-2", "object", {"color": "red"}, provenance=("node-2",)))
    decision = MergeDecision.create(
        identity_ids=("red-1", "red-2"),
        resulting_identity_id="red-1",
        status=IdentityDecision.ACCEPTED,
        evidence_ids=("evidence-same-shape",),
    )

    merged = writer.merge_identities(
        decision,
        CommittedAtom("red-1", "object", {"color": "red", "encounters": 2}),
    )

    assert merged.lifecycle_state == "active"
    assert {"node-1", "node-2", decision.decision_id, "evidence-same-shape"} <= set(merged.provenance)
    assert memory.get("red-2").lifecycle_state == "demoted"  # type: ignore[union-attr]
    assert writer.merge_identities(decision, merged) == merged

    writer.reverse_identity_decision(decision.decision_id, "evidence-false-merge")
    assert memory.get("red-1").lifecycle_state == "active"  # type: ignore[union-attr]
    assert memory.get("red-2").lifecycle_state == "active"  # type: ignore[union-attr]
    assert "evidence-false-merge" in memory.get("red-2").provenance  # type: ignore[union-attr]


def test_split_tombstones_new_children_when_reversed() -> None:
    memory = SymbolicMemory()
    writer = SingleWriter(memory)
    writer.commit(CommittedAtom("compound", "object", {"parts": 2}, provenance=("node-4",)))
    decision = SplitDecision.create(
        source_identity_id="compound",
        resulting_identity_ids=("part-a", "part-b"),
        status=IdentityDecision.ACCEPTED,
        evidence_ids=("evidence-disconnected",),
    )

    parts = writer.split_identity(
        decision,
        (
            CommittedAtom("part-a", "object", {"part": "a"}),
            CommittedAtom("part-b", "object", {"part": "b"}),
        ),
    )

    assert all(item.lifecycle_state == "active" for item in parts)
    assert memory.get("compound").lifecycle_state == "demoted"  # type: ignore[union-attr]
    writer.reverse_identity_decision(decision.decision_id, "evidence-false-split")
    assert memory.get("compound").lifecycle_state == "active"  # type: ignore[union-attr]
    assert memory.get("part-a").lifecycle_state == "tombstoned"  # type: ignore[union-attr]
    assert memory.get("part-b").lifecycle_state == "tombstoned"  # type: ignore[union-attr]


def test_demote_and_tombstone_are_distinct_lifecycle_states() -> None:
    memory = SymbolicMemory()
    writer = SingleWriter(memory)
    writer.commit(CommittedAtom("candidate", "object", {}))

    assert writer.demote("candidate", "weak-evidence").lifecycle_state == "demoted"
    assert writer.tombstone("candidate", "invalidated").lifecycle_state == "tombstoned"
