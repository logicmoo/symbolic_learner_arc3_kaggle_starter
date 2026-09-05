"""SoW Appendix A.2 ``core/schemas.py`` — the typed records (A.4).

Every field the kernel validates and schema-checks. Implemented in
:mod:`object_memory.models`; re-exported here under the SoW layout.
"""

from object_memory.models import (
    ActionRecommendation,
    ArtifactRef,
    CandidateObject,
    CommittedAtom,
    ConfidenceHistoryRecord,
    EncounterRecord,
    EvidencePolarity,
    EvidenceRecord,
    ExecutionMode,
    IdentityDecision,
    IdentityMemoryCheckpoint,
    InstanceParameters,
    MatchProposal,
    MergeDecision,
    NormalizedResult,
    Observation,
    ObjectChange,
    PredictionGradeRecord,
    PredictionRecord,
    ProvenanceRef,
    RecognitionAccount,
    ResidualCandidate,
    ResidualDisposition,
    SplitDecision,
    TransitionRule,
    TurtleProgramRef,
    deterministic_identifier,
)

# SoW A.4 names the seven core data types explicitly:
CORE_DATA_TYPES = (
    "Observation",
    "CandidateObject",
    "RecognitionAccount",
    "ResidualCandidate",
    "CommittedAtom",
    "TransitionRule",
    "PredictionRecord",
)

__all__ = [
    "Observation",
    "CandidateObject",
    "RecognitionAccount",
    "ResidualCandidate",
    "CommittedAtom",
    "TransitionRule",
    "PredictionRecord",
    "InstanceParameters",
    "EvidenceRecord",
    "MatchProposal",
    "MergeDecision",
    "SplitDecision",
    "ProvenanceRef",
    "ArtifactRef",
    "TurtleProgramRef",
    "EncounterRecord",
    "ObjectChange",
    "ActionRecommendation",
    "PredictionGradeRecord",
    "ConfidenceHistoryRecord",
    "IdentityMemoryCheckpoint",
    "NormalizedResult",
    "ResidualDisposition",
    "IdentityDecision",
    "ExecutionMode",
    "EvidencePolarity",
    "deterministic_identifier",
    "CORE_DATA_TYPES",
]
