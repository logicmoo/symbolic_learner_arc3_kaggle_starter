"""SoW Appendix A.2 ``core/`` — the deterministic kernel (identity, evidence,
residual gating, rule records, prediction checking, and the encounter log).

The kernel owns integrity; every open-world stage sits behind a typed contract and
is replaceable one at a time (SoW §3.2). These names re-export the primary
implementations in :mod:`object_memory`.
"""

from .atom_store import (
    ArtifactIndex,
    AtomStore,
    InMemorySemanticBackend,
    SemanticStoreBackend,
    SymbolicMemory,
    SymbolicStore,
)
from .encounter_log import EncounterLog
from .evaluation import (
    AcceptanceReport,
    GridMetrics,
    OutcomeChannel,
    PerceptionBenchmarkRunner,
    PredictionEvaluator,
    ProviderAblationRunner,
    RasterMetrics,
    RecognitionBenchmarkRunner,
    RecognitionCalibrator,
    build_acceptance_report,
)
from .identity_merge import (
    IdentityDecision,
    IdentityMerge,
    MergeDecision,
    RegistryCorrespondenceAuthority,
    SplitDecision,
)
from .prediction_ledger import PredictionLedger, PredictionRecord, RuleStore
from .residual_gate import ResidualAnalyzer, ResidualCandidate, ResidualDisposition, ResidualGate
from .rule_induction import (
    GameLearningPipeline,
    RuleExecutor,
    RuleInducer,
    RuleRanker,
    TransformationLearner,
    TransitionAnalyzer,
)
from .schemas import (
    CandidateObject,
    CommittedAtom,
    Observation,
    RecognitionAccount,
    TransitionRule,
)
from .single_writer import SingleWriter

__all__ = [
    "SingleWriter",
    "AtomStore",
    "SymbolicMemory",
    "SymbolicStore",
    "ArtifactIndex",
    "InMemorySemanticBackend",
    "SemanticStoreBackend",
    "EncounterLog",
    "ResidualGate",
    "ResidualAnalyzer",
    "ResidualCandidate",
    "ResidualDisposition",
    "IdentityMerge",
    "MergeDecision",
    "SplitDecision",
    "IdentityDecision",
    "RegistryCorrespondenceAuthority",
    "PredictionLedger",
    "RuleStore",
    "PredictionRecord",
    "TransitionAnalyzer",
    "TransformationLearner",
    "RuleInducer",
    "RuleRanker",
    "RuleExecutor",
    "GameLearningPipeline",
    "PredictionEvaluator",
    "OutcomeChannel",
    "RecognitionCalibrator",
    "AcceptanceReport",
    "build_acceptance_report",
    "PerceptionBenchmarkRunner",
    "RecognitionBenchmarkRunner",
    "ProviderAblationRunner",
    "GridMetrics",
    "RasterMetrics",
    "Observation",
    "CandidateObject",
    "RecognitionAccount",
    "CommittedAtom",
    "TransitionRule",
]
