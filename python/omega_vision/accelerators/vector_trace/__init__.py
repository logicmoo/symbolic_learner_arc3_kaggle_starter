"""SoW Appendix A.2 ``accelerators/vector_trace/`` / §15 — vector-trace recall.

Vector tracing renders raster into the canonical program (SoW §15); this index
keeps traced forms keyed by handle and returns the nearest by shape distance. A
recall accelerator ONLY (SoW A.1.4): it never decides identity.
"""

from __future__ import annotations

from typing import Any


class VectorTraceIndex:
    """Handle -> traced ``GenerativeForm`` recall index by shape distance."""

    def __init__(self) -> None:
        self._forms: dict[str, Any] = {}

    def add(self, handle: str, form: Any) -> str:
        self._forms[handle] = form
        return handle

    def query(self, form: Any, k: int = 1) -> tuple[str, ...]:
        """Return up to ``k`` nearest committed handles (advisory recall only)."""
        def dist(other: Any) -> float:
            try:
                return float(form.distance(other))
            except Exception:  # noqa: BLE001 - incomparable form -> far away
                return 1.0

        scored = sorted(((dist(f), h) for h, f in self._forms.items()))
        return tuple(h for _, h in scored[:k])

    def __len__(self) -> int:
        return len(self._forms)


__all__ = ["VectorTraceIndex"]
