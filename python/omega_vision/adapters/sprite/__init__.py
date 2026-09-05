"""SoW Appendix A.2 ``adapters/sprite/`` / A.6 — the raster candidate provider.

The raster adapters are :class:`object_memory.adapters.ImageAdapter`,
:class:`object_memory.sprite.SpriteAdapter`, and
:class:`object_memory.adapters.SimpleVideoAdapter`. The SoW registry (A.6) names the
raster ``candidate_provider`` ``RasterSegmenter``; the contractor's existing contour
provider is :class:`object_memory.sprite.AlphaContourProvider`.

``RasterSegmenter`` cuts a raster into whole-object regions by 4-connected
non-background pixels (SoW §4 Segment). It produces an explicit region so the gate
can read a residual; it does not decide identity.
"""

from __future__ import annotations

from typing import Any, Sequence

from object_memory.adapters import ImageAdapter, SimpleVideoAdapter
from object_memory.sprite import AlphaContourProvider, SpriteAdapter

from .._segment import label_components


class RasterSegmenter:
    """Segment a raster grid into connected non-background object regions."""

    def __init__(self, background: Any = None) -> None:
        self.background = background

    def _is_background(self, value: Any) -> bool:
        if self.background is not None:
            return value == self.background
        if isinstance(value, (tuple, list)) and len(value) == 4:
            return value[3] == 0  # RGBA transparency
        return value in (0, None, (0, 0, 0), (0, 0, 0, 0))

    def segment(self, pixels: Sequence[Sequence[Any]]) -> tuple[dict[str, Any], ...]:
        """Return object regions ``{cells, colors, bbox}`` (whole connected sprites)."""
        rows = [list(r) for r in pixels]
        regions = label_components(
            rows,
            participates=lambda v: not self._is_background(v),
            same_region=lambda a, b: True,
        )
        out: list[dict[str, Any]] = []
        for r in regions:
            colors = {(x, y): rows[y][x] for (x, y) in r["cells"]}
            out.append({"cells": r["cells"], "colors": colors, "bbox": r["bbox"]})
        return tuple(out)

    __call__ = segment


__all__ = [
    "SpriteAdapter",
    "ImageAdapter",
    "SimpleVideoAdapter",
    "AlphaContourProvider",
    "RasterSegmenter",
]
