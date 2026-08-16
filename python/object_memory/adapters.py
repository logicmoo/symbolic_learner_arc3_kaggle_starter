from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from .models import ArtifactRef, CandidateObject, Observation, ProvenanceRef


@dataclass(frozen=True)
class GridPerceptionBatch:
    observation: Observation
    candidates: tuple[CandidateObject, ...]
    extractor_details: Mapping[str, Mapping[str, Any]]


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
        self._details: dict[str, Mapping[str, Any]] = {}

    def normalize(
        self,
        *,
        observation_id: str,
        grid: Any,
        action_tree_node: str,
        artifact_uri: str,
    ) -> GridPerceptionBatch:
        """Wrap the established extractor result in Phase 2 contracts."""

        extracted = self.extractor(grid)
        if not isinstance(extracted, Mapping) or not isinstance(
            extracted.get("objects"), list
        ):
            raise TypeError("grid extractor must return a mapping with an objects list")
        provenance = ProvenanceRef(
            source_id=observation_id,
            provider=str(extracted.get("source", "grid_extractor")),
            action_tree_node=action_tree_node,
            sequence=None,
            metadata={"algorithm": extracted.get("algorithm")},
        )
        artifact = ArtifactRef.create(
            artifact_type="logical_grid",
            uri=artifact_uri,
            content_hash=(
                f"sha256:{extracted['sha256']}" if extracted.get("sha256") else None
            ),
            media_type="application/json",
            provenance=(provenance,),
        )
        candidates: list[CandidateObject] = []
        details: dict[str, Mapping[str, Any]] = {}
        for index, item in enumerate(extracted["objects"]):
            if not isinstance(item, Mapping):
                raise TypeError("grid extractor object entries must be mappings")
            candidate_id = str(item.get("candidate_id") or item.get("id") or f"candidate_{index}")
            details[candidate_id] = item
            candidates.append(
                CandidateObject(
                    candidate_id=candidate_id,
                    observation_id=observation_id,
                    domain="grid",
                    provider=self.provider,
                    region_ref=f"{artifact_uri}#objects/{candidate_id}",
                    provenance=(
                        provenance.source_id,
                        provenance.provider,
                        action_tree_node,
                    ),
                )
            )
        self._details.update(details)
        observation = Observation.create(
            source_modality="logical_grid",
            artifacts=(artifact,),
            dimensions=(int(extracted["height"]), int(extracted["width"])),
            coordinate_contract="(x, y) integer cells; origin top-left; 4-connected components",
            candidate_object_ids=tuple(item.candidate_id for item in candidates),
            action_tree_node=action_tree_node,
            provenance=(provenance,),
        )
        return GridPerceptionBatch(observation, tuple(candidates), details)

    def candidate_detail(self, candidate_id: str) -> Mapping[str, Any]:
        return self._details[candidate_id]

    def propose_candidates(self, observation: Any) -> Iterable[CandidateObject]:
        if isinstance(observation, Mapping) and "grid" in observation:
            yield from self.normalize(
                observation_id=str(observation["observation_id"]),
                grid=observation["grid"],
                action_tree_node=str(observation["action_tree_node"]),
                artifact_uri=str(observation["artifact_uri"]),
            ).candidates
            return
        extracted = self.extractor(observation)
        for index, item in enumerate(extracted):
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
