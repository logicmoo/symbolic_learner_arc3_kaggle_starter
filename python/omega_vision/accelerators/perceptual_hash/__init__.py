"""SoW Appendix A.2 ``accelerators/perceptual_hash/`` / §15 — coarse re-recognition.

Perceptual hashing for a coarse re-recognition tier (SoW §15). A recall
accelerator ONLY (SoW A.1.4): it may propose a coarse match but can never mint a
durable identity, decide a merge, or raise confidence.
"""

from __future__ import annotations

from typing import Sequence


class PerceptualHash:
    """Average-hash over a normalized bitmap; Hamming distance for recall."""

    def __init__(self, size: int = 8) -> None:
        self.size = size

    def hash(self, bitmap: Sequence[Sequence[float]]) -> int:
        rows = [list(r) for r in bitmap]
        height = len(rows)
        width = len(rows[0]) if height else 0
        if not height or not width:
            return 0
        vals: list[float] = []
        for by in range(self.size):
            for bx in range(self.size):
                y0 = by * height // self.size
                y1 = max(y0 + 1, (by + 1) * height // self.size)
                x0 = bx * width // self.size
                x1 = max(x0 + 1, (bx + 1) * width // self.size)
                block = [float(rows[y][x]) for y in range(y0, y1) for x in range(x0, x1)]
                vals.append(sum(block) / len(block))
        mean = sum(vals) / len(vals)
        bits = 0
        for i, v in enumerate(vals):
            if v >= mean:
                bits |= 1 << i
        return bits

    @staticmethod
    def distance(a: int, b: int) -> int:
        """Hamming distance between two hashes (lower = more similar)."""
        return bin(a ^ b).count("1")


__all__ = ["PerceptualHash"]
