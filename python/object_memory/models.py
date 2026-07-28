from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping


class ExecutionMode(str, Enum):
    PROLOG = "PROLOG"
    GPT = "GPT"
    PYTHON = "PYTHON"


class ResidualDisposition(str, Enum):
    ABSORBED = "absorbed"
    PROVISIONAL = "provisional"
    COMMIT_REQUEST = "commit_request"


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


@dataclass(frozen=True)
class CommittedAtom:
    handle: str
    atom_type: str
    payload: Mapping[str, Any]
    confidence: float = 0.0
    provenance: tuple[str, ...] = ()
    lifecycle_state: str = "active"


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
