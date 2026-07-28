from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Iterable

from .models import CandidateObject


class PerceptionAdapter(ABC):
    """Domain seam; core code must not import ARC or raster assumptions."""

    @abstractmethod
    def propose_candidates(self, observation: Any) -> Iterable[CandidateObject]:
        raise NotImplementedError


class GridAdapter(PerceptionAdapter):
    """Thin adapter around an existing grid object extractor."""

    def __init__(self, extractor: Any, provider: Any) -> None:
        self.extractor = extractor
        self.provider = provider

    def propose_candidates(self, observation: Any) -> Iterable[CandidateObject]:
        for index, item in enumerate(self.extractor(observation)):
            if isinstance(item, CandidateObject):
                yield item
                continue
            yield CandidateObject(
                candidate_id=str(item.get("candidate_id", f"candidate_{index}")),
                observation_id=str(item["observation_id"]),
                domain="grid",
                provider=self.provider,
                region_ref=item.get("region_ref"),
                provenance=tuple(item.get("provenance", ())),
            )
