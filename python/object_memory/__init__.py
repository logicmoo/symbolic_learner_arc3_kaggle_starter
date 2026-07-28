"""Shared object-memory contracts for PROLOG, GPT, and PYTHON backends.

The package supplements the existing ARC3 debugger. It does not replace
Arc3Runner, ActionTreeStore, GptArcAnalyzer, SWIPrologBridge, or the generated
Prolog artifact contracts.
"""

from .adapters import GridAdapter, PerceptionAdapter
from .forms import CellLogoForm, FitResult, GenerativeForm
from .integration import (
    GameObjectLearnerPayload,
    GameObjectLearnerPlugin,
    GameObjectLearnerResult,
    GameObjectLearnerSchema,
    IntegrationError,
    IntegrationValidator,
    PipelineGameObjectLearnerPlugin,
)
from .learning import (
    GameLearningPipeline,
    LearningStepResult,
    OutcomeChannel,
    PredictionEvaluator,
    PredictionGrade,
    RuleEvidence,
    RuleExecutor,
    RuleInducer,
    RuleRanker,
    RuleRivalSet,
    TransformationCandidate,
    TransformationLearner,
    TransitionAnalyzer,
    TransitionRecord,
)
from .models import (
    CandidateObject,
    CommittedAtom,
    ExecutionMode,
    NormalizedResult,
    PredictionRecord,
    ResidualCandidate,
    ResidualDisposition,
    TransitionRule,
)
from .memory import ResidualGate, SingleWriter, SymbolicMemory
from .prediction import PredictionLedger, RuleStore
from .providers import ArtifactProvider, GptArtifactProvider, PrologProvider, PythonProvider

__all__ = [
    "ArtifactProvider",
    "CandidateObject",
    "CellLogoForm",
    "CommittedAtom",
    "ExecutionMode",
    "FitResult",
    "GameLearningPipeline",
    "GameObjectLearnerPayload",
    "GameObjectLearnerPlugin",
    "GameObjectLearnerResult",
    "GameObjectLearnerSchema",
    "GenerativeForm",
    "GptArtifactProvider",
    "GridAdapter",
    "IntegrationError",
    "IntegrationValidator",
    "LearningStepResult",
    "NormalizedResult",
    "OutcomeChannel",
    "PerceptionAdapter",
    "PipelineGameObjectLearnerPlugin",
    "PredictionEvaluator",
    "PredictionGrade",
    "PredictionLedger",
    "PredictionRecord",
    "PrologProvider",
    "PythonProvider",
    "ResidualCandidate",
    "ResidualDisposition",
    "ResidualGate",
    "RuleEvidence",
    "RuleExecutor",
    "RuleInducer",
    "RuleRanker",
    "RuleRivalSet",
    "RuleStore",
    "SingleWriter",
    "SymbolicMemory",
    "TransformationCandidate",
    "TransformationLearner",
    "TransitionAnalyzer",
    "TransitionRecord",
    "TransitionRule",
]
