"""SoW Appendix A.2 ``adapters/grid/`` / A.6 — the grid candidate provider.

The grid adapter is :class:`object_memory.adapters.GridAdapter`; its declarative
``candidate_provider`` name in the SoW registry (A.6) is ``GridIndividuator``.
The individuator reads clean discrete cells the engine reads directly (SoW rung 1)
and cuts a scene into per-object candidate regions by 4-connected same-colour
components. Background (value ``0``) is skipped.
"""

from __future__ import annotations

from typing import Any, Sequence

from object_memory.adapters import GridAdapter, normalize_grid_structure

from .._segment import label_components


class GridIndividuator:
    """Individuate a discrete grid into candidate objects (SoW §4 Segment)."""

    def __init__(self, background: Any = 0) -> None:
        self.background = background

    def individuate(self, grid: Sequence[Sequence[Any]]) -> tuple[dict[str, Any], ...]:
        """Return per-object regions ``{cells, color, bbox}`` (same-colour, 4-conn)."""
        regions = label_components(
            grid,
            participates=lambda v: v != self.background,
            same_region=lambda a, b: a == b,
        )
        return tuple({"cells": r["cells"], "color": r["value"], "bbox": r["bbox"]} for r in regions)

    __call__ = individuate


__all__ = ["GridAdapter", "GridIndividuator", "normalize_grid_structure"]
