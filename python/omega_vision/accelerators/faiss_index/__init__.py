"""SoW Appendix A.2 ``accelerators/faiss_index/`` / §15 — embedding recall.

DINOv2 + FAISS as a recall accelerator only (SoW §15). This is a dependency-free,
FAISS-compatible brute-force cosine index so the recall seam exists without pulling
in native FAISS. A recall accelerator ONLY (SoW A.1.4): learned embeddings cannot
mint a durable identity, decide a merge, or raise confidence.
"""

from __future__ import annotations

import math
from typing import Sequence


class FaissIndex:
    """Brute-force cosine recall index over embedding vectors (advisory only)."""

    def __init__(self, dim: int | None = None) -> None:
        self.dim = dim
        self._handles: list[str] = []
        self._vectors: list[tuple[float, ...]] = []

    def add(self, handle: str, vector: Sequence[float]) -> str:
        vec = tuple(float(x) for x in vector)
        if self.dim is None:
            self.dim = len(vec)
        elif len(vec) != self.dim:
            raise ValueError(f"expected dim {self.dim}, got {len(vec)}")
        self._handles.append(handle)
        self._vectors.append(vec)
        return handle

    def search(self, vector: Sequence[float], k: int = 1) -> tuple[tuple[str, float], ...]:
        """Return up to ``k`` ``(handle, cosine)`` pairs — a recall hint, not identity."""
        q = tuple(float(x) for x in vector)
        scored = sorted(
            ((self._cosine(q, v), h) for h, v in zip(self._handles, self._vectors)),
            reverse=True,
        )
        return tuple((h, s) for s, h in scored[:k])

    @staticmethod
    def _cosine(a: tuple[float, ...], b: tuple[float, ...]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        na = math.sqrt(sum(x * x for x in a))
        nb = math.sqrt(sum(y * y for y in b))
        return dot / (na * nb) if na and nb else 0.0

    def __len__(self) -> int:
        return len(self._handles)


__all__ = ["FaissIndex"]
