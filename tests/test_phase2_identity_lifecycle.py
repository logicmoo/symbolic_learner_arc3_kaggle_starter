from object_memory import (
    AtomSpaceSemanticBackend,
    CommittedAtom,
    IdentityDecision,
    MergeDecision,
    SingleWriter,
    SplitDecision,
    SymbolicStore,
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


def test_atomspace_checkpoint_restores_and_reverses_merge_after_reload(tmp_path) -> None:
    path = tmp_path / "identity-memory.metta"
    first_store = SymbolicStore(AtomSpaceSemanticBackend(path=path))
    first_memory = SymbolicMemory()
    writer = SingleWriter(first_memory, first_store.put_identity_checkpoint)
    writer.commit(CommittedAtom("left", "object", {"part": "left"}))
    writer.commit(CommittedAtom("right", "object", {"part": "right"}))
    decision = MergeDecision.create(
        identity_ids=("left", "right"),
        resulting_identity_id="whole",
        status=IdentityDecision.ACCEPTED,
        evidence_ids=("same-object",),
    )
    writer.merge_identities(
        decision,
        CommittedAtom("whole", "object", {"parts": ["left", "right"]}),
    )

    second_store = SymbolicStore(AtomSpaceSemanticBackend(path=path))
    restored = second_store.restore_identity_memory()
    assert restored.get("whole").lifecycle_state == "active"  # type: ignore[union-attr]
    assert restored.get("left").lifecycle_state == "demoted"  # type: ignore[union-attr]
    assert restored.identity_decision(decision.decision_id) == decision

    resumed = SingleWriter(restored, second_store.put_identity_checkpoint)
    resumed.reverse_identity_decision(decision.decision_id, "human-review")

    final_store = SymbolicStore(AtomSpaceSemanticBackend(path=path))
    final_memory = final_store.restore_identity_memory()
    assert final_memory.get("left").lifecycle_state == "active"  # type: ignore[union-attr]
    assert final_memory.get("right").lifecycle_state == "active"  # type: ignore[union-attr]
    assert final_memory.get("whole").lifecycle_state == "tombstoned"  # type: ignore[union-attr]
    assert final_memory.checkpoints()[-1].event == "identity_decision_reversed"


def test_atomspace_checkpoint_restores_and_reverses_split_after_reload(tmp_path) -> None:
    path = tmp_path / "split-memory.metta"
    store = SymbolicStore(AtomSpaceSemanticBackend(path=path))
    memory = SymbolicMemory()
    writer = SingleWriter(memory, store.put_identity_checkpoint)
    writer.commit(CommittedAtom("compound", "object", {"parts": 2}))
    decision = SplitDecision.create(
        source_identity_id="compound",
        resulting_identity_ids=("part-a", "part-b"),
        status=IdentityDecision.ACCEPTED,
        evidence_ids=("disconnected",),
    )
    writer.split_identity(
        decision,
        (
            CommittedAtom("part-a", "object", {"part": "a"}),
            CommittedAtom("part-b", "object", {"part": "b"}),
        ),
    )

    reloaded_store = SymbolicStore(AtomSpaceSemanticBackend(path=path))
    reloaded = reloaded_store.restore_identity_memory()
    assert reloaded.get("compound").lifecycle_state == "demoted"  # type: ignore[union-attr]
    assert reloaded.get("part-a").lifecycle_state == "active"  # type: ignore[union-attr]
    resumed = SingleWriter(reloaded, reloaded_store.put_identity_checkpoint)
    resumed.reverse_identity_decision(decision.decision_id, "human-review")

    final = SymbolicStore(AtomSpaceSemanticBackend(path=path)).restore_identity_memory()
    assert final.get("compound").lifecycle_state == "active"  # type: ignore[union-attr]
    assert final.get("part-a").lifecycle_state == "tombstoned"  # type: ignore[union-attr]
    assert final.get("part-b").lifecycle_state == "tombstoned"  # type: ignore[union-attr]
