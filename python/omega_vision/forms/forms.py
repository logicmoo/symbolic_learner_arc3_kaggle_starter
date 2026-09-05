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
    """Canonical Turtle/LOGO generative form over the existing DSL program."""

    domain = "grid"

    def __init__(
        self,
        program: str,
        renderer: Any | None = None,
        swi_bridge: Any | None = None,
    ) -> None:
        self.program = "\n".join(line.rstrip() for line in program.splitlines()).strip()
        if renderer is not None and swi_bridge is not None:
            raise ValueError("supply renderer or swi_bridge, not both")
        self.renderer = renderer or (
            swi_bridge.execute_turtle if swi_bridge is not None else None
        )

    def canonicalize(self) -> str:
        return self.program

    def render(self, params: dict[str, Any] | None = None) -> Any:
        if self.renderer is None:
            return self.program
        return self.renderer(self.program, params or {})

    def fit_instance(self, candidate: Any) -> FitResult:
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
        if not isinstance(other, GenerativeForm):
            return 1.0
        if self.renderer is None or other.renderer is None:
            return 0.0 if self.canonicalize() == other.canonicalize() else 1.0
        left = self._cell_set(self.render())
        right = self._cell_set(other.render())
        union = left | right
        return len(left ^ right) / len(union) if union else 0.0

    def description_length(self) -> int:
        return len(self.canonicalize().encode("utf-8"))

    @staticmethod
    def _cell_set(value: Any) -> set[tuple[int, int]]:
        cells = value.get("cells", ()) if isinstance(value, dict) else value
        if not isinstance(cells, (list, tuple, set)):
            raise TypeError("cell candidate must be a collection or mapping with cells")
        return {(int(cell[0]), int(cell[1])) for cell in cells}
