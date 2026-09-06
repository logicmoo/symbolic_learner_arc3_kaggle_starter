from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class FitResult:
    parameters: dict[str, Any]
    residual: float


class AbstractGenerativeForm(ABC):
    """Abstract typed contract for a generative form (Turtle/LOGO and later raster)."""

    domain: str

    @abstractmethod
    def canonicalize(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def render(self, params: dict[str, Any] | None = None) -> Any:
        raise NotImplementedError

    @abstractmethod
    def fit_instance(self, candidate: Any) -> FitResult:
        raise NotImplementedError

    @abstractmethod
    def distance(self, other: "AbstractGenerativeForm") -> float:
        raise NotImplementedError


class GenerativeForm(AbstractGenerativeForm):
    """Canonical Turtle/LOGO generative form over the existing DSL program.

    ``GenerativeForm`` can also act as a delegating holder: pass ``delegate``
    (an instance of any :class:`AbstractGenerativeForm` subclass, e.g.
    :class:`~omega_vision.forms.contour_fill.ContourFillForm`) and every
    contract method forwards to that instance instead of the built-in
    grid/Turtle implementation. The wrapper then reports the delegate's
    ``domain``.
    """

    domain = "grid"

    def __init__(
        self,
        program: str = "",
        renderer: Any | None = None,
        swi_bridge: Any | None = None,
        delegate: "AbstractGenerativeForm | None" = None,
    ) -> None:
        if delegate is not None and not isinstance(delegate, AbstractGenerativeForm):
            raise TypeError("delegate must be an AbstractGenerativeForm instance")
        self.delegate = delegate
        self.program = "\n".join(line.rstrip() for line in program.splitlines()).strip()
        if renderer is not None and swi_bridge is not None:
            raise ValueError("supply renderer or swi_bridge, not both")
        self.renderer = renderer or (
            swi_bridge.execute_turtle if swi_bridge is not None else None
        )
        if delegate is not None:
            self.domain = delegate.domain

    def canonicalize(self) -> str:
        if self.delegate is not None:
            return self.delegate.canonicalize()
        return self.program

    def render(self, params: dict[str, Any] | None = None) -> Any:
        if self.delegate is not None:
            return self.delegate.render(params)
        if self.renderer is None:
            return self.program
        return self.renderer(self.program, params or {})

    def fit_instance(self, candidate: Any) -> FitResult:
        if self.delegate is not None:
            return self.delegate.fit_instance(candidate)
        expected = self._cell_set(candidate)
        actual = self._cell_set(self.render())
        union = expected | actual
        residual = len(expected ^ actual) / len(union) if union else 0.0
        return FitResult(
            parameters={
                "expected_cells": len(expected),
                "rendered_cells": len(actual),
                "description_length": self.description_length(),
            },
            residual=residual,
        )

    def distance(self, other: AbstractGenerativeForm) -> float:
        if self.delegate is not None:
            inner = other.delegate if isinstance(other, GenerativeForm) and other.delegate is not None else other
            return self.delegate.distance(inner)
        if not isinstance(other, GenerativeForm):
            return 1.0
        if self.renderer is None or other.renderer is None:
            return 0.0 if self.canonicalize() == other.canonicalize() else 1.0
        left = self._cell_set(self.render())
        right = self._cell_set(other.render())
        union = left | right
        return len(left ^ right) / len(union) if union else 0.0

    def description_length(self) -> int:
        if self.delegate is not None:
            length = getattr(self.delegate, "description_length", None) or getattr(
                self.delegate, "code_length", None
            )
            if callable(length):
                return int(length())
            return len(self.delegate.canonicalize().encode("utf-8"))
        return len(self.canonicalize().encode("utf-8"))

    @staticmethod
    def _cell_set(value: Any) -> set[tuple[int, int]]:
        cells = value.get("cells", ()) if isinstance(value, dict) else value
        if not isinstance(cells, (list, tuple, set)):
            raise TypeError("cell candidate must be a collection or mapping with cells")
        return {(int(cell[0]), int(cell[1])) for cell in cells}


# SoW A.3 name for the grid/Turtle form (importable alias).
CellLogoForm = GenerativeForm

__all__ = ["AbstractGenerativeForm", "CellLogoForm", "FitResult", "GenerativeForm"]
