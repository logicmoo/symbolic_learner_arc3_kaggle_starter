from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class FitResult:
    parameters: dict[str, Any]
    residual: float


class GenerativeForm(ABC):
    """Typed facade for existing Turtle/LOGO and later raster forms."""

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
    def distance(self, other: "GenerativeForm") -> float:
        raise NotImplementedError


class CellLogoForm(GenerativeForm):
    """Compatibility facade over the existing canonical Turtle DSL program."""

    domain = "grid"

    def __init__(self, program: str, renderer: Any | None = None) -> None:
        self.program = "\n".join(line.rstrip() for line in program.splitlines()).strip()
        self.renderer = renderer

    def canonicalize(self) -> str:
        return self.program

    def render(self, params: dict[str, Any] | None = None) -> Any:
        if self.renderer is None:
            return self.program
        return self.renderer(self.program, params or {})

    def fit_instance(self, candidate: Any) -> FitResult:
        return FitResult(parameters={}, residual=0.0 if candidate == self.program else 1.0)

    def distance(self, other: GenerativeForm) -> float:
        return 0.0 if self.canonicalize() == other.canonicalize() else 1.0
