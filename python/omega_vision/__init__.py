"""``omega_vision`` — the SoW Appendix A.2 package layout for
*Image Perception to Recognizable Memory* (v1.9).

This package **lays out the SoW-named surface only**. The implementations live
elsewhere — chiefly in :mod:`object_memory` (the deterministic core, forms,
adapters, store, recognition, learning, and benchmarks) — and are re-exported here
under the exact names and module layout the SoW prescribes (Appendix A.2/A.3/A.4/A.6).

The only net-new code here is (a) compact implementations for SoW-laid-out names
that had no prior home (the raster :class:`~omega_vision.forms.contour_fill.ContourFillForm`,
the ``GridIndividuator`` / ``RasterSegmenter`` candidate providers, the recall
accelerators, and the ``GridMetrics`` / ``RasterMetrics`` scorers), (b) importable
§16 future stubs, and (c) a factory method or two (:func:`new_memory`,
:func:`new_writer`, :func:`build_store`, :func:`process_observation`) that belong to
the SoW entry layer.

See :doc:`docs/PROGRAMMERS_GUIDE.md <PROGRAMMERS_GUIDE>` for the class-by-class map
back to the SoW sections.
"""

from __future__ import annotations

from typing import Any

# --- forms (SoW §5, A.3) ---------------------------------------------------
from .forms import (
    CellLogoForm,
    ContourFillForm,
    FitResult,
    GenerativeForm,
    LayeredStrokeForm,
    PartGraph3DForm,
)

# --- deterministic core (SoW §3.1, §9, §10, A.1/A.2) -----------------------
from .core import (
    AcceptanceReport,
    ArtifactIndex,
    AtomStore,
    EncounterLog,
    GameLearningPipeline,
    GridMetrics,
    IdentityMerge,
    InMemorySemanticBackend,
    OutcomeChannel,
    PerceptionBenchmarkRunner,
    PredictionEvaluator,
    PredictionLedger,
    ProviderAblationRunner,
    RasterMetrics,
    RecognitionBenchmarkRunner,
    RecognitionCalibrator,
    RegistryCorrespondenceAuthority,
    ResidualAnalyzer,
    ResidualGate,
    RuleExecutor,
    RuleInducer,
    RuleRanker,
    RuleStore,
    SingleWriter,
    SymbolicMemory,
    SymbolicStore,
    TransformationLearner,
    TransitionAnalyzer,
)

# --- core data types (SoW A.4) ---------------------------------------------
from .core.schemas import (
    CandidateObject,
    CommittedAtom,
    Observation,
    PredictionRecord,
    RecognitionAccount,
    ResidualCandidate,
    ResidualDisposition,
    TransitionRule,
)

# --- adapters (SoW §6, A.6) ------------------------------------------------
from .adapters import (
    GridAdapter,
    GridIndividuator,
    ImageAdapter,
    PerceptionAdapter,
    RasterSegmenter,
    SimpleVideoAdapter,
    SpriteAdapter,
)

# --- accelerators (SoW §15, A.1.4) -----------------------------------------
from .accelerators import FaissIndex, PerceptualHash, VectorTraceIndex


# --- factory methods that belong to the SoW entry layer --------------------
def new_memory() -> SymbolicMemory:
    """Create an empty Atomspace-layer store (SoW §9)."""
    return SymbolicMemory()


def new_writer(memory: SymbolicMemory | None = None) -> SingleWriter:
    """Create the single writer over a (new or given) Atomspace store (SoW A.1.1)."""
    return SingleWriter(memory or SymbolicMemory())


def build_store(backend: Any | None = None) -> SymbolicStore:
    """Build the backend-neutral semantic record store (SoW §9)."""
    return SymbolicStore(backend or InMemorySemanticBackend())


def process_observation(
    observation: Any,
    adapter: Any,
    *,
    store: Any | None = None,
    writer: Any | None = None,  # noqa: ARG001 - reserved for the commit phase
    rules: Any | None = None,   # noqa: ARG001 - reserved for the rule phase
    planner: Any | None = None,
) -> dict[str, Any]:
    """Run the SoW §4/A.5 front of the kernel loop for one observation.

    Segments the observation into candidates through the domain adapter (the only
    domain-aware step, SoW §3.2) and records the observation in the store when one
    is provided. The commit, prediction-grading, and rule phases are performed by
    :class:`~object_memory.memory.SingleWriter`,
    :class:`~object_memory.prediction.PredictionLedger`, and
    :class:`~object_memory.learning.GameLearningPipeline`; ``planner`` is a SoW §16
    future seam and is intentionally unused.
    """
    candidates = tuple(adapter.propose_candidates(observation))
    if store is not None and hasattr(store, "put_observation"):
        try:
            store.put_observation(observation)
        except Exception:  # noqa: BLE001 - non-Observation inputs are tolerated
            pass
    return {"observation": observation, "candidates": candidates, "planner": planner}


__all__ = [
    # forms
    "GenerativeForm", "FitResult", "CellLogoForm", "ContourFillForm",
    "LayeredStrokeForm", "PartGraph3DForm",
    # core
    "SingleWriter", "AtomStore", "SymbolicMemory", "SymbolicStore", "ArtifactIndex",
    "InMemorySemanticBackend", "EncounterLog", "ResidualGate", "ResidualAnalyzer",
    "IdentityMerge", "RegistryCorrespondenceAuthority", "PredictionLedger", "RuleStore",
    "TransitionAnalyzer", "TransformationLearner", "RuleInducer", "RuleRanker",
    "RuleExecutor", "GameLearningPipeline", "PredictionEvaluator", "OutcomeChannel",
    "RecognitionCalibrator", "AcceptanceReport", "PerceptionBenchmarkRunner",
    "RecognitionBenchmarkRunner", "ProviderAblationRunner", "GridMetrics", "RasterMetrics",
    # data types (A.4)
    "Observation", "CandidateObject", "RecognitionAccount", "ResidualCandidate",
    "CommittedAtom", "TransitionRule", "PredictionRecord", "ResidualDisposition",
    # adapters
    "PerceptionAdapter", "GridAdapter", "GridIndividuator", "SpriteAdapter",
    "ImageAdapter", "SimpleVideoAdapter", "RasterSegmenter",
    # accelerators
    "PerceptualHash", "VectorTraceIndex", "FaissIndex",
    # factories
    "new_memory", "new_writer", "build_store", "process_observation",
]
