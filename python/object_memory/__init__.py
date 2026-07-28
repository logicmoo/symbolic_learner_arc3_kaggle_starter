"""Shared object-memory contracts for PROLOG, GPT, and PYTHON backends.

The package supplements the existing ARC3 debugger. It does not replace
Arc3Runner, ActionTreeStore, GptArcAnalyzer, SWIPrologBridge, or the generated
Prolog artifact contracts.
"""

from .adapters import GridAdapter, PerceptionAdapter
from .forms import CellLogoForm, FitResult, GenerativeForm
from .integration import GameObjectLearnerPayload, GameObjectLearnerPlugin
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
    "GameObjectLearnerPayload",
    "GameObjectLearnerPlugin",
    "GenerativeForm",
    "GptArtifactProvider",
    "GridAdapter",
    "NormalizedResult",
    "PerceptionAdapter",
    "PredictionLedger",
    "PredictionRecord",
    "PrologProvider",
    "PythonProvider",
    "ResidualCandidate",
    "ResidualDisposition",
    "ResidualGate",
    "RuleStore",
    "SingleWriter",
    "SymbolicMemory",
    "TransitionRule",
]
