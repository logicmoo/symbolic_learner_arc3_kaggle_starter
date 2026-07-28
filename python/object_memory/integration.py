from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Mapping

from .models import NormalizedResult


@dataclass(frozen=True)
class GameObjectLearnerPayload:
    state_id: str
    objects: tuple[Mapping[str, Any], ...]
    correspondences: tuple[Mapping[str, Any], ...] = ()
    transitions: tuple[Mapping[str, Any], ...] = ()
    provenance: tuple[str, ...] = ()


class GameObjectLearnerPlugin(ABC):
    """Phase 3 boundary; implementations consume normalized Phase 2 results."""

    @abstractmethod
    def consume(self, payload: GameObjectLearnerPayload) -> NormalizedResult:
        raise NotImplementedError
