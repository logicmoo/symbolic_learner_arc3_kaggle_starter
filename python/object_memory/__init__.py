"""Shared object-memory contracts for PROLOG, GPT, and PYTHON backends.

The package supplements the existing ARC3 debugger. It does not replace
Arc3Runner, ActionTreeStore, GptArcAnalyzer, SWIPrologBridge, or the generated
Prolog artifact contracts.
"""

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
from .prediction import PredictionLedger
from .providers import ArtifactProvider, GptArtifactProvider, PrologProvider, PythonProvider

__all__ = [
    "ArtifactProvider",
    "CandidateObject",
    "CommittedAtom",
    "ExecutionMode",
    "GptArtifactProvider",
    "NormalizedResult",
    "PredictionLedger",
    "PredictionRecord",
    "PrologProvider",
    "PythonProvider",
    "ResidualCandidate",
    "ResidualDisposition",
    "ResidualGate",
    "SingleWriter",
    "SymbolicMemory",
    "TransitionRule",
]
