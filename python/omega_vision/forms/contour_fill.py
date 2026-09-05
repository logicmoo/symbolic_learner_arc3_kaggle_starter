"""SoW Appendix A.2 ``forms/contour_fill.py`` / A.8 task 8 — the raster form.

Raster -> a contour/fill program (SoW §5). This is one of the SoW-laid-out
classes that had no prior home, so a compact, deterministic implementation lives
here. It is intentionally small: it fulfils the :class:`GenerativeForm` contract
(A.3) over a normalized set of filled cells per colour, so the same kernel serves
raster sprites by swapping the form language, not the core.

A ``ContourFillForm`` holds a *fill program*: one layer per colour, each layer a
set of integer ``(x, y)`` cells. Canonicalization translates to the origin and
orders layers and cells deterministically, so identical shapes hash identically
across machines (SoW §13 Determinism).
"""

from __future__ import annotations

from typing import Any, Iterable, Mapping

from object_memory.forms import FitResult, GenerativeForm

Cell = tuple[int, int]
Layer = tuple[str, tuple[Cell, ...]]


def _as_layers(program: Any) -> tuple[Layer, ...]:
    """Coerce assorted inputs into ``((colour, (cells...)), ...)``.

    Accepts a mapping ``{colour: iterable_of_cells}``, an iterable of
    ``(colour, cells)`` pairs, or an iterable of ``(x, y)`` cells (single
    default-coloured layer).
    """
    if isinstance(program, Mapping):
        items: Iterable[tuple[Any, Any]] = program.items()
    else:
        seq = list(program or [])
        if seq and isinstance(seq[0], (tuple, list)) and len(seq[0]) == 2 \
                and all(isinstance(v, (int, float)) for v in seq[0]):
            # a bare iterable of (x, y) cells -> one default layer
            items = [("_", seq)]
        else:
            items = seq  # already (colour, cells) pairs
    layers: list[Layer] = []
    for colour, cells in items:
        norm = tuple(sorted((int(x), int(y)) for x, y in cells))
        if norm:
            layers.append((str(colour), norm))
    return tuple(layers)


class ContourFillForm(GenerativeForm):
    """A raster contour/fill ``GenerativeForm`` over normalized filled cells."""

    def __init__(self, program: Any) -> None:
        self._layers = _as_layers(program)

    # -- SoW A.3: canonicalize / render / fit_instance / distance ----------
    def canonicalize(self) -> str:
        """Translate to the origin and order layers/cells deterministically."""
        cells = [c for _, layer in self._layers for c in layer]
        ox = min((x for x, _ in cells), default=0)
        oy = min((y for _, y in cells), default=0)
        norm = tuple(
            (colour, tuple(sorted((x - ox, y - oy) for x, y in layer)))
            for colour, layer in self._layers
        )
        norm = tuple(sorted(norm, key=lambda l: (-len(l[1]), l[0])))
        return ";".join(
            colour + ":" + ",".join(f"{x}_{y}" for x, y in layer)
            for colour, layer in norm
        )

    def render(self, params: dict[str, Any] | None = None) -> dict[Cell, str]:
        """Rasterize to ``{(x, y): colour}`` after an optional integer offset."""
        dx, dy = (params or {}).get("offset", (0, 0))
        grid: dict[Cell, str] = {}
        for colour, layer in self._layers:
            for x, y in layer:
                grid[(x + int(dx), y + int(dy))] = colour
        return grid

    def fit_instance(self, candidate: Any) -> FitResult:
        """Fit the integer translation that best overlaps ``candidate``."""
        other = candidate if isinstance(candidate, ContourFillForm) else ContourFillForm(candidate)
        mine = self._occupied()
        theirs = other._occupied()
        if not mine or not theirs:
            return FitResult(parameters={"offset": (0, 0)}, residual=float(len(mine ^ theirs)))
        # centroid alignment is the cheapest good offset (SoW §7 cheapest account)
        cx = round(sum(x for x, _ in theirs) / len(theirs) - sum(x for x, _ in mine) / len(mine))
        cy = round(sum(y for _, y in theirs) / len(theirs) - sum(y for _, y in mine) / len(mine))
        shifted = {(x + cx, y + cy) for x, y in mine}
        residual = float(len(shifted ^ theirs))
        return FitResult(parameters={"offset": (cx, cy)}, residual=residual)

    def distance(self, other: GenerativeForm) -> float:
        """1 - IoU over occupied cells of the two canonical forms (colour-free)."""
        if not isinstance(other, ContourFillForm):
            return 1.0
        a = self._canon_cells()
        b = other._canon_cells()
        if not a and not b:
            return 0.0
        inter = len(a & b)
        union = len(a | b)
        return 1.0 - (inter / union if union else 0.0)

    # -- SoW A.3 extensions: code_length / residual / complete -------------
    def code_length(self) -> float:
        """Description length = cells + per-layer parameter bits (SoW §5)."""
        return float(sum(len(layer) for _, layer in self._layers) + len(self._layers))

    def residual(self, candidate: Any, params: dict[str, Any] | None = None) -> float:
        """Explicit, measurable residual: cells the fitted account leaves uncovered."""
        return self.fit_instance(candidate).residual

    def complete(self, partial_evidence: Any = None) -> tuple["ContourFillForm", ...]:
        """Generative completion (SoW §8): mirror across the bbox vertical axis."""
        cells = self._occupied()
        if not cells:
            return (ContourFillForm(()),)
        max_x = max(x for x, _ in cells)
        min_x = min(x for x, _ in cells)
        span = max_x + min_x
        completed = {(span - x, y) for x, y in cells} | cells
        # keep the first layer's colour for the mirrored fill
        colour = self._layers[0][0] if self._layers else "_"
        return (ContourFillForm({colour: tuple(sorted(completed))}),)

    # -- helpers -----------------------------------------------------------
    @property
    def layers(self) -> tuple[Layer, ...]:
        return self._layers

    def _occupied(self) -> set[Cell]:
        return {c for _, layer in self._layers for c in layer}

    def _canon_cells(self) -> set[Cell]:
        cells = self._occupied()
        if not cells:
            return set()
        ox = min(x for x, _ in cells)
        oy = min(y for _, y in cells)
        return {(x - ox, y - oy) for x, y in cells}


__all__ = ["ContourFillForm"]
