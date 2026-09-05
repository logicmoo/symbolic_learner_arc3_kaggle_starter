"""SoW Appendix A.2 ``accelerators/`` — recall accelerators only (SoW §15, A.1.4).

Off-the-shelf recall tiers: perceptual hashing, vector tracing, and a
FAISS-compatible embedding index. None may mint a durable identity, decide a
merge, or raise confidence — they only accelerate recall.
"""

from .faiss_index import FaissIndex
from .perceptual_hash import PerceptualHash
from .sketchformer import SketchformerEmbedding
from .vector_trace import VectorTraceIndex

__all__ = ["PerceptualHash", "VectorTraceIndex", "FaissIndex", "SketchformerEmbedding"]
