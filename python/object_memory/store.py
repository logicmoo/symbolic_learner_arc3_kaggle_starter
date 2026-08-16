from __future__ import annotations

from collections import defaultdict
from typing import Any, Protocol

from .memory import EncounterLog
from .models import (
    ArtifactRef,
    CommittedAtom,
    EncounterRecord,
    EvidenceRecord,
    MatchProposal,
    Observation,
    RecognitionAccount,
    TurtleProgramRef,
)


class SemanticStoreBackend(Protocol):
    """Minimal exact-record boundary implemented by Prolog or AtomSpace stores."""

    def write_once(self, namespace: str, record_id: str, value: Any) -> Any: ...

    def get(self, namespace: str, record_id: str) -> Any | None: ...

    def values(self, namespace: str) -> tuple[Any, ...]: ...


class InMemorySemanticBackend:
    """Deterministic reference backend used by tests and local composition."""

    def __init__(self) -> None:
        self._records: dict[str, dict[str, Any]] = defaultdict(dict)

    def write_once(self, namespace: str, record_id: str, value: Any) -> Any:
        existing = self._records[namespace].get(record_id)
        if existing is not None:
            if existing != value:
                raise ValueError(f"Semantic identity conflict for {namespace}/{record_id}")
            return existing
        self._records[namespace][record_id] = value
        return value

    def get(self, namespace: str, record_id: str) -> Any | None:
        return self._records.get(namespace, {}).get(record_id)

    def values(self, namespace: str) -> tuple[Any, ...]:
        return tuple(self._records.get(namespace, {}).values())


class ArtifactIndex:
    """Exact artifact lookup by stable ID and semantic artifact type."""

    def __init__(self) -> None:
        self._artifacts: dict[str, ArtifactRef] = {}
        self._by_type: dict[str, list[str]] = defaultdict(list)

    def register(self, artifact: ArtifactRef) -> ArtifactRef:
        existing = self._artifacts.get(artifact.artifact_id)
        if existing is not None:
            if existing != artifact:
                raise ValueError(f"Artifact identity conflict for {artifact.artifact_id!r}")
            return existing
        self._artifacts[artifact.artifact_id] = artifact
        self._by_type[artifact.artifact_type].append(artifact.artifact_id)
        return artifact

    def get(self, artifact_id: str) -> ArtifactRef | None:
        return self._artifacts.get(artifact_id)

    def by_type(self, artifact_type: str) -> tuple[ArtifactRef, ...]:
        return tuple(self._artifacts[item] for item in self._by_type.get(artifact_type, ()))


class SymbolicStore:
    """Backend-neutral facade for exact Phase 2 semantic records.

    Similarity indexes may propose identifiers to query here, but only exact
    stable identifiers address or commit records through this boundary.
    """

    def __init__(self, backend: SemanticStoreBackend) -> None:
        self.backend = backend
        self.encounters = EncounterLog()
        self.artifacts = ArtifactIndex()

    def put_observation(self, value: Observation) -> Observation:
        for artifact in value.artifacts:
            self.put_artifact(artifact)
        return self.backend.write_once("observations", value.observation_id, value)

    def put_encounter(self, value: EncounterRecord) -> EncounterRecord:
        stored = self.backend.write_once("encounters", value.encounter_id, value)
        self.encounters.append(stored)
        for artifact in value.reconstruction_artifacts:
            self.put_artifact(artifact)
        for turtle in value.turtle_programs:
            self.put_turtle(turtle)
        return stored

    def put_recognition(self, value: RecognitionAccount) -> RecognitionAccount:
        return self.backend.write_once("recognition_accounts", value.account_id, value)

    def put_match_proposal(self, value: MatchProposal) -> MatchProposal:
        return self.backend.write_once("match_proposals", value.proposal_id, value)

    def put_evidence(self, value: EvidenceRecord) -> EvidenceRecord:
        return self.backend.write_once("evidence", value.evidence_id, value)

    def put_artifact(self, value: ArtifactRef) -> ArtifactRef:
        stored = self.backend.write_once("artifacts", value.artifact_id, value)
        self.artifacts.register(stored)
        return stored

    def put_turtle(self, value: TurtleProgramRef) -> TurtleProgramRef:
        self.put_artifact(value.artifact)
        return self.backend.write_once(
            "turtle_programs", value.artifact.artifact_id, value
        )

    def put_atom(self, value: CommittedAtom) -> CommittedAtom:
        return self.backend.write_once("atoms", value.handle, value)

    def get(self, namespace: str, record_id: str) -> Any | None:
        return self.backend.get(namespace, record_id)

    def values(self, namespace: str) -> tuple[Any, ...]:
        return self.backend.values(namespace)
