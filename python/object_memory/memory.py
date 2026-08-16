from __future__ import annotations

from dataclasses import replace
from hashlib import sha256
import json
from typing import Any

from .models import (
    CommittedAtom,
    EncounterRecord,
    ResidualCandidate,
    ResidualDisposition,
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

    def get(self, handle: str) -> CommittedAtom | None:
        return self._atoms.get(handle)

    def all_atoms(self) -> tuple[CommittedAtom, ...]:
        return tuple(self._atoms.values())

    def events(self) -> tuple[dict[str, Any], ...]:
        return tuple(self._events)


class SingleWriter:
    """Only mutation path for committed atoms and their evidence."""

    def __init__(self, memory: SymbolicMemory) -> None:
        self.memory = memory

    def commit(self, atom: CommittedAtom) -> CommittedAtom:
        existing = self.memory._atoms.get(atom.handle)
        if existing is not None and existing.atom_type != atom.atom_type:
            raise ValueError(f"Identity conflict for {atom.handle!r}")
        admitted = replace(atom, confidence=0.0)
        self.memory._atoms[atom.handle] = admitted
        self.memory._events.append({"event": "commit", "handle": atom.handle})
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
        return updated
