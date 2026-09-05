"""Shared 4-connectivity labelling for the SoW candidate providers.

Connected components and contours handle clean sprites and grids (SoW §4
Segment). Pure-python and deterministic so identical input yields identical
candidates (SoW §13 Determinism); no numpy/OpenCV dependency at import time.
"""

from __future__ import annotations

from typing import Any, Callable, Sequence

Cell = tuple[int, int]


def _rows(grid: Any) -> list[list[Any]]:
    return [list(row) for row in grid]


def _neighbours(x: int, y: int):
    yield x - 1, y
    yield x + 1, y
    yield x, y - 1
    yield x, y + 1


def label_components(
    grid: Sequence[Sequence[Any]],
    *,
    participates: Callable[[Any], bool],
    same_region: Callable[[Any, Any], bool],
) -> list[dict[str, Any]]:
    """Return 4-connected components as ``{cells, value, bbox}`` dicts.

    ``participates(v)`` decides whether a cell is foreground; ``same_region(a, b)``
    decides whether two adjacent foreground cells belong to the same component.
    """
    rows = _rows(grid)
    height = len(rows)
    width = len(rows[0]) if height else 0
    seen: set[Cell] = set()
    out: list[dict[str, Any]] = []
    for sy in range(height):
        for sx in range(width):
            if (sx, sy) in seen:
                continue
            value = rows[sy][sx]
            if not participates(value):
                continue
            stack = [(sx, sy)]
            seen.add((sx, sy))
            cells: list[Cell] = []
            while stack:
                x, y = stack.pop()
                cells.append((x, y))
                for nx, ny in _neighbours(x, y):
                    if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in seen:
                        nv = rows[ny][nx]
                        if participates(nv) and same_region(value, nv):
                            seen.add((nx, ny))
                            stack.append((nx, ny))
            cells.sort()
            xs = [c[0] for c in cells]
            ys = [c[1] for c in cells]
            out.append({
                "cells": tuple(cells),
                "value": value,
                "bbox": (min(xs), min(ys), max(xs), max(ys)),
            })
    # deterministic order: by position then size
    out.sort(key=lambda r: (r["bbox"][1], r["bbox"][0], -len(r["cells"])))
    return out


__all__ = ["label_components"]
