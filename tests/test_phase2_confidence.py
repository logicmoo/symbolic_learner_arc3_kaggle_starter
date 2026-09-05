import pytest

from omega_vision import (
    CommittedAtom,
    EvidencePolarity,
    EvidenceRecord,
    ProvenanceRef,
    SingleWriter,
    SymbolicMemory,
)


def _evidence(name: str, polarity: EvidencePolarity, weight: float) -> EvidenceRecord:
    return EvidenceRecord.create(
        subject_id="object-ball",
        polarity=polarity,
        source=ProvenanceRef(name, "recognizer"),
        weight=weight,
        detail={"source": name},
    )


def test_confidence_is_derived_from_positive_and_negative_evidence() -> None:
    memory = SymbolicMemory()
    writer = SingleWriter(memory)
    writer.commit(CommittedAtom("object-ball", "object", {}))
    supporting = _evidence("match-1", EvidencePolarity.SUPPORTS, 3.0)
    contradicting = _evidence("mismatch-1", EvidencePolarity.CONTRADICTS, 1.0)

    assert writer.apply_evidence("object-ball", supporting).confidence == pytest.approx(0.75)
    updated = writer.apply_evidence("object-ball", contradicting)

    assert updated.confidence == pytest.approx(0.6)
    assert updated.provenance == tuple(sorted((supporting.evidence_id, contradicting.evidence_id)))
    assert memory.evidence_for("object-ball") == tuple(
        sorted((supporting, contradicting), key=lambda item: item.evidence_id)
    )


def test_confidence_is_reproducible_regardless_of_evidence_arrival_order() -> None:
    evidence = (
        _evidence("match-1", EvidencePolarity.SUPPORTS, 2.0),
        _evidence("match-2", EvidencePolarity.SUPPORTS, 1.0),
        _evidence("mismatch", EvidencePolarity.CONTRADICTS, 0.5),
    )

    def replay(order: tuple[EvidenceRecord, ...]) -> tuple[float, tuple[str, ...]]:
        memory = SymbolicMemory()
        writer = SingleWriter(memory)
        writer.commit(CommittedAtom("object-ball", "object", {}))
        for item in order:
            writer.apply_evidence("object-ball", item)
        atom = memory.get("object-ball")
        assert atom is not None
        return atom.confidence, atom.provenance

    assert replay(evidence) == replay(tuple(reversed(evidence)))


def test_calibrated_evidence_is_idempotent_and_subject_checked() -> None:
    memory = SymbolicMemory()
    writer = SingleWriter(memory)
    writer.commit(CommittedAtom("object-ball", "object", {}))
    supporting = _evidence("match", EvidencePolarity.SUPPORTS, 1.0)

    first = writer.apply_evidence("object-ball", supporting)
    second = writer.apply_evidence("object-ball", supporting)
    assert first == second
    wrong_subject = EvidenceRecord.create(
        subject_id="object-cube",
        polarity=EvidencePolarity.SUPPORTS,
        source=ProvenanceRef("match", "recognizer"),
    )
    with pytest.raises(ValueError, match="does not match"):
        writer.apply_evidence("object-ball", wrong_subject)
