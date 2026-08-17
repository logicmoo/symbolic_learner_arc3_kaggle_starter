from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from hashlib import sha256
from io import BytesIO
from pathlib import Path
from typing import Any, Iterable, Mapping

from PIL import Image

from .models import ArtifactRef, CandidateObject, Observation, ProvenanceRef


def _normalized_cells(value: Any) -> tuple[tuple[int, int], ...]:
    cells = value if isinstance(value, (list, tuple, set)) else ()
    return tuple(sorted({(int(cell[0]), int(cell[1])) for cell in cells}))


def _connected_components(
    cells: tuple[tuple[int, int], ...],
) -> tuple[tuple[tuple[int, int], ...], ...]:
    remaining = set(cells)
    components: list[tuple[tuple[int, int], ...]] = []
    while remaining:
        pending = [min(remaining)]
        remaining.remove(pending[0])
        component: set[tuple[int, int]] = set()
        while pending:
            cell = pending.pop()
            component.add(cell)
            x, y = cell
            for neighbor in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    pending.append(neighbor)
        components.append(tuple(sorted(component)))
    return tuple(sorted(components, key=lambda item: (item[0], len(item))))


def _axis_runs(
    cells: tuple[tuple[int, int], ...], *, horizontal: bool
) -> tuple[tuple[tuple[int, int], ...], ...]:
    groups: dict[int, list[int]] = {}
    for x, y in cells:
        fixed, varying = (y, x) if horizontal else (x, y)
        groups.setdefault(fixed, []).append(varying)
    runs: list[tuple[tuple[int, int], ...]] = []
    for fixed, values in sorted(groups.items()):
        current: list[int] = []
        for value in sorted(set(values)):
            if current and value != current[-1] + 1:
                if len(current) >= 2:
                    runs.append(
                        tuple(
                            (item, fixed) if horizontal else (fixed, item)
                            for item in current
                        )
                    )
                current = []
            current.append(value)
        if len(current) >= 2:
            runs.append(
                tuple(
                    (item, fixed) if horizontal else (fixed, item)
                    for item in current
                )
            )
    return tuple(runs)


def normalize_grid_structure(item: Mapping[str, Any]) -> Mapping[str, Any]:
    """Normalize extractor-specific grid structure into one semantic contract."""

    cells = _normalized_cells(item.get("cells"))
    components = _connected_components(cells)
    bounds = tuple(int(value) for value in item.get("bounds") or (0, 0, 0, 0))
    origin_x, origin_y = bounds[:2]

    def relative(group):
        return tuple((x - origin_x, y - origin_y) for x, y in group)

    topology = item.get("topology") if isinstance(item.get("topology"), Mapping) else {}
    holes = tuple(relative(_normalized_cells(hole)) for hole in topology.get("holes") or ())
    normalized_components = tuple(relative(component) for component in components)
    relationships = tuple(
        {
            "target": str(value.get("target")),
            "relation": str(value.get("relation")),
        }
        for value in sorted(
            (item.get("relationships") or ()),
            key=lambda value: (str(value.get("relation")), str(value.get("target"))),
        )
        if isinstance(value, Mapping)
    )
    geometry = item.get("geometry") if isinstance(item.get("geometry"), Mapping) else {}
    return {
        "geometry": {
            "cells": relative(cells),
            "width": geometry.get("width", bounds[2] if len(bounds) > 2 else 0),
            "height": geometry.get("height", bounds[3] if len(bounds) > 3 else 0),
            "boundary_cells": relative(
                _normalized_cells(geometry.get("boundaryCells") or cells)
            ),
            "horizontal_bars": tuple(
                relative(run) for run in _axis_runs(cells, horizontal=True)
            ),
            "vertical_bars": tuple(
                relative(run) for run in _axis_runs(cells, horizontal=False)
            ),
            "line_thickness": item.get("lineThickness"),
        },
        "topology": {
            "connected_components": len(components),
            "components": normalized_components,
            "hole_count": len(holes),
            "holes": holes,
            "enclosures": holes,
            "compound": len(components) > 1,
            "compound_parts": normalized_components if len(components) > 1 else (),
        },
        "properties": {
            "color": item.get("colorName"),
            "shape": item.get("shape"),
            "pixel_count": item.get("pixelCount", len(cells)),
        },
        "relationships": relationships,
    }


@dataclass(frozen=True)
class GridPerceptionBatch:
    observation: Observation
    candidates: tuple[CandidateObject, ...]
    extractor_details: Mapping[str, Mapping[str, Any]]


@dataclass(frozen=True)
class MediaPerceptionBatch:
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
            details[candidate_id] = {
                **item,
                "normalizedStructure": normalize_grid_structure(item),
            }
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


def _load_image(value: Any) -> tuple[Image.Image, bytes | None, str | None]:
    if isinstance(value, Image.Image):
        return value.copy(), None, value.format
    if isinstance(value, (bytes, bytearray)):
        payload = bytes(value)
        with Image.open(BytesIO(payload)) as source:
            return source.copy(), payload, source.format
    path = Path(value)
    payload = path.read_bytes()
    with Image.open(BytesIO(payload)) as source:
        return source.copy(), payload, source.format


class ImageAdapter(PerceptionAdapter):
    """Normalize raster extractor output without prescribing segmentation."""

    def __init__(self, extractor: Any, provider: Any) -> None:
        self.extractor = extractor
        self.provider = provider
        self._details: dict[str, Mapping[str, Any]] = {}

    def normalize(
        self,
        *,
        observation_id: str,
        image: Any,
        action_tree_node: str,
        artifact_uri: str,
        sequence: int | None = None,
    ) -> MediaPerceptionBatch:
        raster, payload, image_format = _load_image(image)
        extracted = self.extractor(raster)
        if not isinstance(extracted, Mapping) or not isinstance(
            extracted.get("objects"), list
        ):
            raise TypeError("image extractor must return a mapping with an objects list")
        provider_name = str(extracted.get("source", "image_extractor"))
        provenance = ProvenanceRef(
            source_id=observation_id,
            provider=provider_name,
            action_tree_node=action_tree_node,
            sequence=sequence,
            metadata={"algorithm": extracted.get("algorithm")},
        )
        digest = extracted.get("sha256") or (
            sha256(payload).hexdigest() if payload is not None else None
        )
        artifact = ArtifactRef.create(
            artifact_type="raster_image",
            uri=artifact_uri,
            content_hash=f"sha256:{digest}" if digest else None,
            media_type=Image.MIME.get(image_format or "", "image/png"),
            provenance=(provenance,),
        )
        candidates: list[CandidateObject] = []
        details: dict[str, Mapping[str, Any]] = {}
        for index, item in enumerate(extracted["objects"]):
            if not isinstance(item, Mapping):
                raise TypeError("image extractor object entries must be mappings")
            candidate_id = str(
                item.get("candidate_id") or item.get("id") or f"candidate_{index}"
            )
            bounds = tuple(item.get("bounds") or item.get("bbox") or ())
            details[candidate_id] = {
                **item,
                "normalizedStructure": {
                    "geometry": {"bounds": bounds},
                    "properties": dict(item.get("properties") or {}),
                    "relationships": tuple(item.get("relationships") or ()),
                    "topology": dict(item.get("topology") or {}),
                },
            }
            candidates.append(
                CandidateObject(
                    candidate_id=candidate_id,
                    observation_id=observation_id,
                    domain="image",
                    provider=self.provider,
                    region_ref=f"{artifact_uri}#objects/{candidate_id}",
                    provenance=(observation_id, provider_name, action_tree_node),
                )
            )
        self._details.update(details)
        observation = Observation.create(
            source_modality="raster_image",
            artifacts=(artifact,),
            dimensions=(raster.height, raster.width, len(raster.getbands())),
            coordinate_contract="(x, y) pixel coordinates; origin top-left",
            candidate_object_ids=tuple(item.candidate_id for item in candidates),
            action_tree_node=action_tree_node,
            provenance=(provenance,),
        )
        return MediaPerceptionBatch(observation, tuple(candidates), details)

    def candidate_detail(self, candidate_id: str) -> Mapping[str, Any]:
        return self._details[candidate_id]

    def propose_candidates(self, observation: Any) -> Iterable[CandidateObject]:
        if not isinstance(observation, Mapping) or "image" not in observation:
            raise TypeError("image observation must contain an image")
        yield from self.normalize(
            observation_id=str(observation["observation_id"]),
            image=observation["image"],
            action_tree_node=str(observation["action_tree_node"]),
            artifact_uri=str(observation["artifact_uri"]),
            sequence=observation.get("sequence"),
        ).candidates


class SimpleVideoAdapter(PerceptionAdapter):
    """Adapt an ordered iterable of decoded frames through an ImageAdapter."""

    def __init__(self, image_adapter: ImageAdapter) -> None:
        self.image_adapter = image_adapter

    def normalize(
        self,
        *,
        observation_id: str,
        frames: Iterable[Any],
        action_tree_node: str,
        artifact_uri: str,
    ) -> tuple[MediaPerceptionBatch, ...]:
        batches = []
        for sequence, frame in enumerate(frames):
            batches.append(
                self.image_adapter.normalize(
                    observation_id=f"{observation_id}:frame:{sequence}",
                    image=frame,
                    action_tree_node=action_tree_node,
                    artifact_uri=f"{artifact_uri}#frame={sequence}",
                    sequence=sequence,
                )
            )
        return tuple(batches)

    def propose_candidates(self, observation: Any) -> Iterable[CandidateObject]:
        if not isinstance(observation, Mapping) or "frames" not in observation:
            raise TypeError("video observation must contain decoded frames")
        for batch in self.normalize(
            observation_id=str(observation["observation_id"]),
            frames=observation["frames"],
            action_tree_node=str(observation["action_tree_node"]),
            artifact_uri=str(observation["artifact_uri"]),
        ):
            yield from batch.candidates
