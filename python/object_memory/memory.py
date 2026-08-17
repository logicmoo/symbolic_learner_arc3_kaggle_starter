from __future__ import annotations

from dataclasses import replace
from hashlib import sha256
import json
from typing import Any, Callable

from .models import (
    CommittedAtom,
    ConfidenceHistoryRecord,
    EncounterRecord,
    EvidencePolarity,
    EvidenceRecord,
    IdentityDecision,
    IdentityMemoryCheckpoint,
    MergeDecision,
    ResidualCandidate,
    ResidualDisposition,
    SplitDecision,
)


class EncounterLog:
    """Append-only semantic encounters with deterministic, idempotent replay.

    Phase 1 remains the owner of action-tree history. This log only records the
    Phase 2 semantic encounters linked to those immutable node references.
    """

    def __init__(self) -> None:
        self._ordered: list[EncounterRecord] = []
        self._by_id: dict[str, EncounterRecord] = {}

    def append(self, encounter: EncounterRecord) -> EncounterRecord:
        existing = self._by_id.get(encounter.encounter_id)
        if existing is not None:
            if existing != encounter:
                raise ValueError(
                    f"Encounter identity conflict for {encounter.encounter_id!r}"
                )
            return existing
        if (
            encounter.previous_encounter_id is not None
            and encounter.previous_encounter_id not in self._by_id
        ):
            raise ValueError(
                "previous encounter must already exist in this append-only log: "
                f"{encounter.previous_encounter_id!r}"
            )
        self._ordered.append(encounter)
        self._by_id[encounter.encounter_id] = encounter
        return encounter

    def get(self, encounter_id: str) -> EncounterRecord | None:
        return self._by_id.get(encounter_id)

    def records(self) -> tuple[EncounterRecord, ...]:
        return tuple(self._ordered)

    def for_object(self, object_identity_id: str) -> tuple[EncounterRecord, ...]:
        return tuple(
            record
            for record in self._ordered
            if record.object_identity_id == object_identity_id
        )

    def replay(self, encounters: tuple[EncounterRecord, ...]) -> "EncounterLog":
        for encounter in encounters:
            self.append(encounter)
        return self

    def deterministic_hash(self) -> str:
        encoded = json.dumps(
            [record.encounter_id for record in self._ordered],
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")
        return sha256(encoded).hexdigest()


class ResidualGate:
    """Deterministic admission policy; thresholds remain configuration choices."""

    def evaluate(self, residual: ResidualCandidate) -> ResidualDisposition:
        if residual.disposition is ResidualDisposition.ABSORBED:
            return residual.disposition
        if residual.structured and (
            residual.recurrence_count > 1 or residual.prediction_gain > 0.0
        ):
            return ResidualDisposition.COMMIT_REQUEST
        return ResidualDisposition.PROVISIONAL


class SymbolicMemory:
    """Small in-memory reference store; durable stores may implement this API."""

    def __init__(self) -> None:
        self._atoms: dict[str, CommittedAtom] = {}
        self._events: list[dict[str, Any]] = []
        self._evidence: dict[str, dict[str, EvidenceRecord]] = {}
        self._identity_decisions: dict[str, MergeDecision | SplitDecision] = {}
        self._decision_snapshots: dict[str, dict[str, CommittedAtom | None]] = {}
        self._confidence_history: list[ConfidenceHistoryRecord] = []
        self._checkpoints: list[IdentityMemoryCheckpoint] = []

    def get(self, handle: str) -> CommittedAtom | None:
        return self._atoms.get(handle)

    def all_atoms(self) -> tuple[CommittedAtom, ...]:
        return tuple(self._atoms.values())

    def events(self) -> tuple[dict[str, Any], ...]:
        return tuple(self._events)

    def evidence_for(self, handle: str) -> tuple[EvidenceRecord, ...]:
        return tuple(
            self._evidence.get(handle, {})[evidence_id]
            for evidence_id in sorted(self._evidence.get(handle, {}))
        )

    def identity_decision(self, decision_id: str) -> MergeDecision | SplitDecision | None:
        return self._identity_decisions.get(decision_id)

    def confidence_history(self, handle: str) -> tuple[ConfidenceHistoryRecord, ...]:
        return tuple(item for item in self._confidence_history if item.handle == handle)

    def checkpoints(self) -> tuple[IdentityMemoryCheckpoint, ...]:
        return tuple(self._checkpoints)

    def restore(self, checkpoint: IdentityMemoryCheckpoint) -> "SymbolicMemory":
        """Restore an exact writer state from one durable checkpoint."""

        self._atoms = {item.handle: item for item in checkpoint.atoms}
        self._evidence = {}
        for item in checkpoint.evidence:
            self._evidence.setdefault(item.subject_id, {})[item.evidence_id] = item
        self._identity_decisions = {
            item.decision_id: item
            for item in (*checkpoint.merge_decisions, *checkpoint.split_decisions)
        }
        self._decision_snapshots = {
            decision_id: dict(snapshot)
            for decision_id, snapshot in checkpoint.decision_snapshots.items()
        }
        self._confidence_history = list(checkpoint.confidence_history)
        self._checkpoints = [checkpoint]
        self._events = [
            {
                "event": "durable_reload",
                "checkpoint_id": checkpoint.checkpoint_id,
                "source_event": checkpoint.event,
            }
        ]
        return self


class SingleWriter:
    """Only mutation path for committed atoms and their evidence."""

    def __init__(
        self,
        memory: SymbolicMemory,
        checkpoint_sink: Callable[[IdentityMemoryCheckpoint], Any] | None = None,
    ) -> None:
        self.memory = memory
        self.checkpoint_sink = checkpoint_sink

    def _checkpoint(self, event: str, reference_id: str | None = None) -> None:
        decisions = tuple(self.memory._identity_decisions.values())
        sequence = (
            self.memory._checkpoints[-1].sequence + 1
            if self.memory._checkpoints
            else 0
        )
        checkpoint = IdentityMemoryCheckpoint.create(
            sequence=sequence,
            event=event,
            reference_id=reference_id,
            atoms=tuple(self.memory._atoms[key] for key in sorted(self.memory._atoms)),
            evidence=tuple(
                values[key]
                for handle in sorted(self.memory._evidence)
                for values in (self.memory._evidence[handle],)
                for key in sorted(values)
            ),
            merge_decisions=tuple(
                item for item in decisions if isinstance(item, MergeDecision)
            ),
            split_decisions=tuple(
                item for item in decisions if isinstance(item, SplitDecision)
            ),
            decision_snapshots={
                decision_id: dict(snapshot)
                for decision_id, snapshot in self.memory._decision_snapshots.items()
            },
            confidence_history=tuple(self.memory._confidence_history),
        )
        self.memory._checkpoints.append(checkpoint)
        if self.checkpoint_sink is not None:
            self.checkpoint_sink(checkpoint)

    def _record_confidence(
        self,
        atom: CommittedAtom,
        event: str,
        reference_id: str | None = None,
    ) -> None:
        self.memory._confidence_history.append(
            ConfidenceHistoryRecord(
                sequence=len(self.memory._confidence_history),
                handle=atom.handle,
                confidence=atom.confidence,
                lifecycle_state=atom.lifecycle_state,
                event=event,
                reference_id=reference_id,
            )
        )

    def commit(self, atom: CommittedAtom) -> CommittedAtom:
        existing = self.memory._atoms.get(atom.handle)
        if existing is not None:
            if existing.atom_type != atom.atom_type or existing.payload != atom.payload:
                raise ValueError(f"Identity conflict for {atom.handle!r}")
            return existing
        admitted = replace(atom, confidence=0.0)
        self.memory._atoms[atom.handle] = admitted
        self.memory._events.append({"event": "commit", "handle": atom.handle})
        self._record_confidence(admitted, "commit")
        self._checkpoint("commit", atom.handle)
        return admitted

    def commit_residual(
        self,
        residual: ResidualCandidate,
        atom: CommittedAtom,
        gate: ResidualGate,
    ) -> CommittedAtom:
        """Commit only a residual that the configured gate admits."""
        disposition = gate.evaluate(residual)
        if disposition is not ResidualDisposition.COMMIT_REQUEST:
            raise ValueError(
                f"Residual {residual.residual_id!r} is {disposition.value}, not commit_request"
            )
        committed = self.commit(atom)
        self.memory._events.append(
            {
                "event": "residual_commit",
                "residual_id": residual.residual_id,
                "handle": atom.handle,
            }
        )
        return committed

    def accrue_evidence(self, handle: str, confidence: float, evidence: str) -> CommittedAtom:
        """Compatibility path for legacy callers with pre-calibrated evidence."""
        if not 0.0 <= confidence < 1.0:
            raise ValueError("confidence must be in [0, 1)")
        atom = self.memory._atoms[handle]
        updated = replace(
            atom,
            confidence=confidence,
            provenance=(*atom.provenance, evidence),
        )
        self.memory._atoms[handle] = updated
        self.memory._events.append({"event": "evidence", "handle": handle, "evidence": evidence})
        self._record_confidence(updated, "legacy_evidence", evidence)
        self._checkpoint("legacy_evidence", evidence)
        return updated

    def apply_evidence(self, handle: str, evidence: EvidenceRecord) -> CommittedAtom:
        """Derive calibrated confidence from attributable signed evidence."""

        if evidence.subject_id != handle:
            raise ValueError(
                f"Evidence subject {evidence.subject_id!r} does not match {handle!r}"
            )
        atom = self.memory._atoms[handle]
        records = self.memory._evidence.setdefault(handle, {})
        existing = records.get(evidence.evidence_id)
        if existing is not None and existing != evidence:
            raise ValueError(f"Evidence identity conflict for {evidence.evidence_id!r}")
        if existing is not None:
            return atom
        prior_evidence_ids = set(records)
        records[evidence.evidence_id] = evidence
        support = sum(
            item.weight
            for item in records.values()
            if item.polarity is EvidencePolarity.SUPPORTS
        )
        contradiction = sum(
            item.weight
            for item in records.values()
            if item.polarity is EvidencePolarity.CONTRADICTS
        )
        confidence = support / (support + contradiction + 1.0)
        evidence_ids = tuple(sorted(records))
        base_provenance = tuple(
            item for item in atom.provenance if item not in prior_evidence_ids
        )
        updated = replace(
            atom,
            confidence=confidence,
            provenance=(*base_provenance, *evidence_ids),
        )
        self.memory._atoms[handle] = updated
        self.memory._events.append(
            {
                "event": "evidence_calibrated",
                "handle": handle,
                "evidence_id": evidence.evidence_id,
                "polarity": evidence.polarity.value,
                "support_weight": support,
                "contradiction_weight": contradiction,
                "confidence": confidence,
            }
        )
        self._record_confidence(updated, "evidence_calibrated", evidence.evidence_id)
        self._checkpoint("evidence_calibrated", evidence.evidence_id)
        return updated

    def tombstone(self, handle: str, reason: str) -> CommittedAtom:
        atom = self.memory._atoms[handle]
        updated = replace(
            atom,
            lifecycle_state="tombstoned",
            provenance=(*atom.provenance, reason),
        )
        self.memory._atoms[handle] = updated
        self.memory._events.append({"event": "tombstone", "handle": handle, "reason": reason})
        self._record_confidence(updated, "tombstone", reason)
        self._checkpoint("tombstone", handle)
        return updated

    def demote(
        self, handle: str, reason: str, *, checkpoint: bool = True
    ) -> CommittedAtom:
        atom = self.memory._atoms[handle]
        updated = replace(
            atom,
            lifecycle_state="demoted",
            provenance=(*atom.provenance, reason),
        )
        self.memory._atoms[handle] = updated
        self.memory._events.append({"event": "demote", "handle": handle, "reason": reason})
        self._record_confidence(updated, "demote", reason)
        if checkpoint:
            self._checkpoint("demote", handle)
        return updated

    def merge_identities(
        self,
        decision: MergeDecision,
        resulting_atom: CommittedAtom,
    ) -> CommittedAtom:
        if decision.status is not IdentityDecision.ACCEPTED:
            raise ValueError("merge decision must be accepted before application")
        if resulting_atom.handle != decision.resulting_identity_id:
            raise ValueError("resulting atom does not match merge decision")
        existing_decision = self.memory._identity_decisions.get(decision.decision_id)
        if existing_decision is not None:
            if existing_decision != decision:
                raise ValueError(f"Identity decision conflict for {decision.decision_id!r}")
            return self.memory._atoms[decision.resulting_identity_id]
        sources = [self.memory._atoms[item] for item in decision.identity_ids]
        if len({item.atom_type for item in sources}) != 1:
            raise ValueError("merged identities must have the same atom type")
        if resulting_atom.atom_type != sources[0].atom_type:
            raise ValueError("merge result must preserve the source atom type")
        snapshot = {
            handle: self.memory._atoms.get(handle)
            for handle in {*decision.identity_ids, decision.resulting_identity_id}
        }
        self.memory._decision_snapshots[decision.decision_id] = snapshot
        provenance = tuple(
            dict.fromkeys(
                (
                    *(item for source in sources for item in source.provenance),
                    *resulting_atom.provenance,
                    decision.decision_id,
                    *decision.evidence_ids,
                )
            )
        )
        prior_result = self.memory._atoms.get(decision.resulting_identity_id)
        confidence = prior_result.confidence if prior_result is not None else 0.0
        merged = replace(
            resulting_atom,
            confidence=confidence,
            provenance=provenance,
            lifecycle_state="active",
        )
        self.memory._atoms[merged.handle] = merged
        self._record_confidence(merged, "merge_result", decision.decision_id)
        for handle in decision.identity_ids:
            if handle != merged.handle:
                self.demote(handle, decision.decision_id, checkpoint=False)
        self.memory._identity_decisions[decision.decision_id] = decision
        self.memory._events.append(
            {
                "event": "merge",
                "decision_id": decision.decision_id,
                "sources": decision.identity_ids,
                "result": merged.handle,
            }
        )
        self._checkpoint("merge", decision.decision_id)
        return merged

    def split_identity(
        self,
        decision: SplitDecision,
        resulting_atoms: tuple[CommittedAtom, ...],
    ) -> tuple[CommittedAtom, ...]:
        if decision.status is not IdentityDecision.ACCEPTED:
            raise ValueError("split decision must be accepted before application")
        if tuple(item.handle for item in resulting_atoms) != decision.resulting_identity_ids:
            raise ValueError("split atoms must match the decision result order")
        existing_decision = self.memory._identity_decisions.get(decision.decision_id)
        if existing_decision is not None:
            if existing_decision != decision:
                raise ValueError(f"Identity decision conflict for {decision.decision_id!r}")
            return tuple(self.memory._atoms[item] for item in decision.resulting_identity_ids)
        source = self.memory._atoms[decision.source_identity_id]
        if any(item.atom_type != source.atom_type for item in resulting_atoms):
            raise ValueError("split results must preserve the source atom type")
        snapshot = {
            handle: self.memory._atoms.get(handle)
            for handle in {decision.source_identity_id, *decision.resulting_identity_ids}
        }
        self.memory._decision_snapshots[decision.decision_id] = snapshot
        stored: list[CommittedAtom] = []
        for item in resulting_atoms:
            admitted = replace(
                item,
                confidence=0.0,
                provenance=tuple(
                    dict.fromkeys(
                        (
                            *source.provenance,
                            *item.provenance,
                            decision.decision_id,
                            *decision.evidence_ids,
                        )
                    )
                ),
                lifecycle_state="active",
            )
            self.memory._atoms[item.handle] = admitted
            self._record_confidence(admitted, "split_result", decision.decision_id)
            stored.append(admitted)
        self.demote(source.handle, decision.decision_id, checkpoint=False)
        self.memory._identity_decisions[decision.decision_id] = decision
        self.memory._events.append(
            {
                "event": "split",
                "decision_id": decision.decision_id,
                "source": source.handle,
                "results": decision.resulting_identity_ids,
            }
        )
        self._checkpoint("split", decision.decision_id)
        return tuple(stored)

    def reverse_identity_decision(self, decision_id: str, reason: str) -> None:
        decision = self.memory._identity_decisions[decision_id]
        snapshot = self.memory._decision_snapshots[decision_id]
        for handle, prior in snapshot.items():
            if prior is None:
                current = self.memory._atoms.get(handle)
                if current is not None:
                    self.memory._atoms[handle] = replace(
                        current,
                        lifecycle_state="tombstoned",
                        provenance=(*current.provenance, reason),
                    )
            else:
                self.memory._atoms[handle] = replace(
                    prior,
                    provenance=(*prior.provenance, reason),
                )
            restored = self.memory._atoms.get(handle)
            if restored is not None:
                self._record_confidence(restored, "identity_decision_reversed", decision_id)
        self.memory._events.append(
            {"event": "identity_decision_reversed", "decision_id": decision_id, "reason": reason}
        )
        self._checkpoint("identity_decision_reversed", decision_id)
