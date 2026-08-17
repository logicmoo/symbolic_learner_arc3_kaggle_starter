from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from enum import Enum
from hashlib import sha256
import json
from typing import Any, Mapping


PHASE2_SCHEMA_VERSION = "2.0.0"


def _canonical_value(value: Any) -> Any:
    """Return a JSON-safe, order-stable value for semantic record identity."""

    if is_dataclass(value):
        return _canonical_value(asdict(value))
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Mapping):
        return {
            str(key): _canonical_value(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    if isinstance(value, (tuple, list)):
        return [_canonical_value(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    raise TypeError(f"semantic identity cannot contain {type(value).__name__}")


def deterministic_identifier(record_type: str, identity: Mapping[str, Any]) -> str:
    """Create a reproducible identifier from the record's immutable identity."""

    canonical = json.dumps(
        _canonical_value(identity),
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return f"{record_type}-{sha256(canonical).hexdigest()[:24]}"


class ExecutionMode(str, Enum):
    PROLOG = "PROLOG"
    GPT = "GPT"
    PYTHON = "PYTHON"


class ResidualDisposition(str, Enum):
    ABSORBED = "absorbed"
    PROVISIONAL = "provisional"
    COMMIT_REQUEST = "commit_request"


class EvidencePolarity(str, Enum):
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"


class IdentityDecision(str, Enum):
    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    REVERSED = "reversed"


@dataclass(frozen=True)
class ProvenanceRef:
    source_id: str
    provider: str
    action_tree_node: str | None = None
    artifact_id: str | None = None
    sequence: int | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)
    schema_version: str = PHASE2_SCHEMA_VERSION

    @classmethod
    def create(cls, *, source_id: str, provider: str, **values: Any) -> "ProvenanceRef":
        return cls(source_id=source_id, provider=provider, **values)


@dataclass(frozen=True)
class ArtifactRef:
    artifact_id: str
    artifact_type: str
    uri: str
    content_hash: str | None = None
    media_type: str | None = None
    provenance: tuple[ProvenanceRef, ...] = ()
    schema_version: str = PHASE2_SCHEMA_VERSION

    @classmethod
    def create(
        cls,
        *,
        artifact_type: str,
        uri: str,
        content_hash: str | None = None,
        **values: Any,
    ) -> "ArtifactRef":
        identity = {
            "artifact_type": artifact_type,
            "uri": uri,
            "content_hash": content_hash,
        }
        return cls(
            artifact_id=deterministic_identifier("artifact", identity),
            artifact_type=artifact_type,
            uri=uri,
            content_hash=content_hash,
            **values,
        )


@dataclass(frozen=True)
class TurtleProgramRef:
    artifact: ArtifactRef
    language: str = "turtle_dsl"
    entrypoint: str | None = None
    fit_score: float | None = None
    distance: float | None = None
    residual_score: float | None = None
    description_length: float | None = None
    schema_version: str = PHASE2_SCHEMA_VERSION


@dataclass(frozen=True)
class InstanceParameters:
    position: tuple[float, ...] = ()
    orientation: float | str | None = None
    scale: tuple[float, ...] = (1.0,)
    appearance: Mapping[str, Any] = field(default_factory=dict)
    supported_transformations: tuple[str, ...] = ()
    reflection: str | None = None
    visibility: float = 1.0
    noise_score: float = 0.0
    geometry: Mapping[str, Any] = field(default_factory=dict)
    topology: Mapping[str, Any] = field(default_factory=dict)
    relationships: tuple[Mapping[str, Any], ...] = ()
    schema_version: str = PHASE2_SCHEMA_VERSION


@dataclass(frozen=True)
class EvidenceRecord:
    evidence_id: str
    subject_id: str
    polarity: EvidencePolarity
    source: ProvenanceRef
    weight: float = 1.0
    detail: Mapping[str, Any] = field(default_factory=dict)
    created_sequence: int = 0
    schema_version: str = PHASE2_SCHEMA_VERSION

    @classmethod
    def create(
        cls,
        *,
        subject_id: str,
        polarity: EvidencePolarity,
        source: ProvenanceRef,
        weight: float = 1.0,
        detail: Mapping[str, Any] | None = None,
        created_sequence: int = 0,
    ) -> "EvidenceRecord":
        identity = {
            "subject_id": subject_id,
            "polarity": polarity,
            "source": source,
            "detail": detail or {},
            "created_sequence": created_sequence,
        }
        return cls(
            deterministic_identifier("evidence", identity),
            subject_id,
            polarity,
            source,
            weight,
            detail or {},
            created_sequence,
        )


@dataclass(frozen=True)
class Observation:
    observation_id: str
    source_modality: str
    artifacts: tuple[ArtifactRef, ...] = ()
    dimensions: tuple[int, ...] = ()
    coordinate_contract: str = ""
    candidate_object_ids: tuple[str, ...] = ()
    action_tree_node: str | None = None
    provenance: tuple[ProvenanceRef, ...] = ()
    schema_version: str = PHASE2_SCHEMA_VERSION

    @classmethod
    def create(
        cls,
        *,
        source_modality: str,
        artifacts: tuple[ArtifactRef, ...] = (),
        dimensions: tuple[int, ...] = (),
        coordinate_contract: str = "",
        candidate_object_ids: tuple[str, ...] = (),
        action_tree_node: str | None = None,
        provenance: tuple[ProvenanceRef, ...] = (),
    ) -> "Observation":
        identity = {
            "source_modality": source_modality,
            "artifacts": tuple(item.artifact_id for item in artifacts),
            "dimensions": dimensions,
            "coordinate_contract": coordinate_contract,
            "action_tree_node": action_tree_node,
        }
        return cls(
            deterministic_identifier("observation", identity),
            source_modality,
            artifacts,
            dimensions,
            coordinate_contract,
            candidate_object_ids,
            action_tree_node,
            provenance,
        )


@dataclass(frozen=True)
class MatchProposal:
    proposal_id: str
    candidate_id: str
    stored_identity_id: str
    matched_properties: tuple[str, ...] = ()
    changed_properties: Mapping[str, Any] = field(default_factory=dict)
    allowed_transformations: tuple[str, ...] = ()
    similarity: float | None = None
    evidence_ids: tuple[str, ...] = ()
    provenance: tuple[ProvenanceRef, ...] = ()
    schema_version: str = PHASE2_SCHEMA_VERSION

    @classmethod
    def create(
        cls, *, candidate_id: str, stored_identity_id: str, **values: Any
    ) -> "MatchProposal":
        identity = {
            "candidate_id": candidate_id,
            "stored_identity_id": stored_identity_id,
            "matched_properties": values.get("matched_properties", ()),
            "changed_properties": values.get("changed_properties", {}),
        }
        return cls(
            proposal_id=deterministic_identifier("match-proposal", identity),
            candidate_id=candidate_id,
            stored_identity_id=stored_identity_id,
            **values,
        )


@dataclass(frozen=True)
class MergeDecision:
    decision_id: str
    identity_ids: tuple[str, ...]
    resulting_identity_id: str
    status: IdentityDecision
    evidence_ids: tuple[str, ...] = ()
    provenance: tuple[ProvenanceRef, ...] = ()
    schema_version: str = PHASE2_SCHEMA_VERSION

    @classmethod
    def create(
        cls,
        *,
        identity_ids: tuple[str, ...],
        resulting_identity_id: str,
        status: IdentityDecision,
        **values: Any,
    ) -> "MergeDecision":
        identity = {
            "identity_ids": tuple(sorted(identity_ids)),
            "resulting_identity_id": resulting_identity_id,
            "status": status,
        }
        return cls(
            decision_id=deterministic_identifier("merge-decision", identity),
            identity_ids=identity_ids,
            resulting_identity_id=resulting_identity_id,
            status=status,
            **values,
        )


@dataclass(frozen=True)
class SplitDecision:
    decision_id: str
    source_identity_id: str
    resulting_identity_ids: tuple[str, ...]
    status: IdentityDecision
    evidence_ids: tuple[str, ...] = ()
    provenance: tuple[ProvenanceRef, ...] = ()
    schema_version: str = PHASE2_SCHEMA_VERSION

    @classmethod
    def create(
        cls,
        *,
        source_identity_id: str,
        resulting_identity_ids: tuple[str, ...],
        status: IdentityDecision,
        **values: Any,
    ) -> "SplitDecision":
        identity = {
            "source_identity_id": source_identity_id,
            "resulting_identity_ids": tuple(sorted(resulting_identity_ids)),
            "status": status,
        }
        return cls(
            decision_id=deterministic_identifier("split-decision", identity),
            source_identity_id=source_identity_id,
            resulting_identity_ids=resulting_identity_ids,
            status=status,
            **values,
        )


@dataclass(frozen=True)
class RecognitionAccount:
    account_id: str
    candidate_id: str
    stored_identity_id: str | None
    matched_properties: tuple[str, ...] = ()
    changed_properties: Mapping[str, Any] = field(default_factory=dict)
    allowed_transformations: tuple[str, ...] = ()
    turtle_reconstruction_fit: float | None = None
    residual_score: float | None = None
    supporting_evidence_ids: tuple[str, ...] = ()
    contradicting_evidence_ids: tuple[str, ...] = ()
    rival_proposal_ids: tuple[str, ...] = ()
    calibrated_confidence: float = 0.0
    decision_source: str = "unresolved"
    provenance: tuple[ProvenanceRef, ...] = ()
    schema_version: str = PHASE2_SCHEMA_VERSION

    @classmethod
    def create(
        cls,
        *,
        candidate_id: str,
        stored_identity_id: str | None,
        **values: Any,
    ) -> "RecognitionAccount":
        identity = {
            "candidate_id": candidate_id,
            "stored_identity_id": stored_identity_id,
            "supporting_evidence_ids": values.get("supporting_evidence_ids", ()),
            "contradicting_evidence_ids": values.get("contradicting_evidence_ids", ()),
            "rival_proposal_ids": values.get("rival_proposal_ids", ()),
            "decision_source": values.get("decision_source", "unresolved"),
        }
        return cls(
            account_id=deterministic_identifier("recognition-account", identity),
            candidate_id=candidate_id,
            stored_identity_id=stored_identity_id,
            **values,
        )


@dataclass(frozen=True)
class ObjectChange:
    change_id: str
    kind: str
    before_identity_ids: tuple[str, ...] = ()
    after_candidate_ids: tuple[str, ...] = ()
    properties: Mapping[str, Any] = field(default_factory=dict)
    evidence_ids: tuple[str, ...] = ()
    provenance: tuple[ProvenanceRef, ...] = ()
    schema_version: str = PHASE2_SCHEMA_VERSION

    @classmethod
    def create(
        cls,
        *,
        kind: str,
        before_identity_ids: tuple[str, ...] = (),
        after_candidate_ids: tuple[str, ...] = (),
        properties: Mapping[str, Any] | None = None,
        evidence_ids: tuple[str, ...] = (),
        provenance: tuple[ProvenanceRef, ...] = (),
    ) -> "ObjectChange":
        identity = {
            "kind": kind,
            "before_identity_ids": tuple(sorted(before_identity_ids)),
            "after_candidate_ids": tuple(sorted(after_candidate_ids)),
            "properties": properties or {},
        }
        return cls(
            change_id=deterministic_identifier("object-change", identity),
            kind=kind,
            before_identity_ids=before_identity_ids,
            after_candidate_ids=after_candidate_ids,
            properties=properties or {},
            evidence_ids=evidence_ids,
            provenance=provenance,
        )


@dataclass(frozen=True)
class EncounterRecord:
    encounter_id: str
    observation_id: str
    action_tree_node: str
    object_identity_id: str | None = None
    candidate_identity_id: str | None = None
    instance: InstanceParameters = field(default_factory=InstanceParameters)
    matched_properties: tuple[str, ...] = ()
    changed_properties: Mapping[str, Any] = field(default_factory=dict)
    turtle_programs: tuple[TurtleProgramRef, ...] = ()
    reconstruction_artifacts: tuple[ArtifactRef, ...] = ()
    residual_ids: tuple[str, ...] = ()
    confidence: float = 0.0
    evidence_ids: tuple[str, ...] = ()
    previous_encounter_id: str | None = None
    next_encounter_id: str | None = None
    provenance: tuple[ProvenanceRef, ...] = ()
    deterministic_hash: str = ""
    schema_version: str = PHASE2_SCHEMA_VERSION

    @classmethod
    def create(
        cls,
        *,
        observation_id: str,
        action_tree_node: str,
        object_identity_id: str | None = None,
        candidate_identity_id: str | None = None,
        instance: InstanceParameters | None = None,
        provenance: tuple[ProvenanceRef, ...] = (),
        **changes: Any,
    ) -> "EncounterRecord":
        identity = {
            "observation_id": observation_id,
            "action_tree_node": action_tree_node,
            "object_identity_id": object_identity_id,
            "candidate_identity_id": candidate_identity_id,
            "instance": instance or InstanceParameters(),
        }
        digest = deterministic_identifier("encounter", identity)
        return cls(
            encounter_id=digest,
            observation_id=observation_id,
            action_tree_node=action_tree_node,
            object_identity_id=object_identity_id,
            candidate_identity_id=candidate_identity_id,
            instance=instance or InstanceParameters(),
            provenance=provenance,
            deterministic_hash=digest.split("-", 1)[1],
            **changes,
        )


@dataclass(frozen=True)
class NormalizedResult:
    """Backend-neutral return shape used by all providers."""

    value: Any
    mode: ExecutionMode
    source_refs: tuple[str, ...] = ()
    evidence: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CandidateObject:
    candidate_id: str
    observation_id: str
    domain: str
    provider: "ArtifactProviderProtocol"
    region_ref: str | None = None
    provenance: tuple[str, ...] = ()

    def part(self, name: str) -> NormalizedResult:
        return self.provider.get_candidate_part(self, name)


@dataclass(frozen=True)
class ResidualCandidate:
    residual_id: str
    source_candidate_id: str
    disposition: ResidualDisposition
    residual_length: float
    structured: bool = False
    recurrence_count: int = 0
    prediction_gain: float = 0.0
    provenance: tuple[str, ...] = ()

    @classmethod
    def create(
        cls,
        *,
        source_candidate_id: str,
        disposition: ResidualDisposition,
        residual_length: float,
        provenance: tuple[str, ...] = (),
        **values: Any,
    ) -> "ResidualCandidate":
        identity = {
            "source_candidate_id": source_candidate_id,
            "residual_length": residual_length,
            "provenance": provenance,
        }
        return cls(
            residual_id=deterministic_identifier("residual", identity),
            source_candidate_id=source_candidate_id,
            disposition=disposition,
            residual_length=residual_length,
            provenance=provenance,
            **values,
        )


@dataclass(frozen=True)
class CommittedAtom:
    handle: str
    atom_type: str
    payload: Mapping[str, Any]
    confidence: float = 0.0
    provenance: tuple[str, ...] = ()
    lifecycle_state: str = "active"


@dataclass(frozen=True)
class ConfidenceHistoryRecord:
    sequence: int
    handle: str
    confidence: float
    lifecycle_state: str
    event: str
    reference_id: str | None = None


@dataclass(frozen=True)
class TransitionRule:
    rule_id: str
    preconditions: tuple[Any, ...]
    action_or_event: Any
    predicted_effects: tuple[Any, ...]
    provenance: tuple[str, ...] = ()


@dataclass(frozen=True)
class PredictionRecord:
    prediction_id: str
    rule_id: str
    source_state_id: str
    predicted_effects: tuple[Any, ...]
    created_sequence: int
    outcome_sequence: int | None = None
    outcome: Any = None
    grade: float | None = None


class ArtifactProviderProtocol:
    def get_candidate_part(self, candidate: CandidateObject, name: str) -> NormalizedResult:
        raise NotImplementedError
