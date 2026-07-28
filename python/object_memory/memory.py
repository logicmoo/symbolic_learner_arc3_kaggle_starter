from __future__ import annotations

from dataclasses import replace
from typing import Any

from .models import CommittedAtom, ResidualCandidate, ResidualDisposition


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
