from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from hashlib import sha256
from io import BytesIO
from math import atan2, degrees
from pathlib import Path
from typing import Any, Iterable, Mapping

from PIL import Image

from .models import ArtifactRef, CandidateObject, Observation, ProvenanceRef


class LearnedPartRoleProvider:
    """Infer semantic component roles from labeled structural examples.

    The provider deliberately learns only the label boundary. Component
    extraction and role-reference validation remain deterministic adapter
    responsibilities.
    """

    def __init__(self, examples: Iterable[Mapping[str, Any]]) -> None:
        learned: list[tuple[str, tuple[float, ...], Mapping[str, Any]]] = []
        for example in examples:
            role = str(example.get("role") or "").strip()
            cells = _normalized_cells(example.get("cells"))
            if not role or not cells:
                raise ValueError("learned part-role examples require role and cells")
            learned.append(
                (role, self._features(cells), dict(example.get("properties") or {}))
            )
        if not learned:
            raise ValueError("learned part-role provider requires labeled examples")
        self._examples = tuple(learned)

    @staticmethod
    def _features(cells: tuple[tuple[int, int], ...]) -> tuple[float, ...]:
        xs = [cell[0] for cell in cells]
        ys = [cell[1] for cell in cells]
        width = max(xs) - min(xs) + 1
        height = max(ys) - min(ys) + 1
        area = width * height
        return (
            float(len(cells)),
            float(width),
            float(height),
            len(cells) / area,
            width / height,
        )

    def infer_part_roles(
        self,
        _item: Mapping[str, Any],
        components: tuple[tuple[tuple[int, int], ...], ...],
    ) -> tuple[Mapping[str, Any], ...]:
        roles = []
        for index, component in enumerate(components):
            features = self._features(component)
            role, _example, properties = min(
                self._examples,
                key=lambda example: (
                    sum(
                        abs(current - learned) / max(1.0, abs(learned))
                        for current, learned in zip(features, example[1])
                    ),
                    example[0],
                ),
            )
            roles.append(
                {
                    "role": role,
                    "component": index,
                    "properties": {**properties, "inference": "learned_nearest_example"},
                }
            )
        return tuple(roles)


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


def _principal_orientation(
    cells: tuple[tuple[int, int], ...],
) -> float | None:
    """Return an undirected principal-axis angle, or None for symmetric shapes."""

    if len(cells) < 2:
        return None
    center_x = sum(cell[0] for cell in cells) / len(cells)
    center_y = sum(cell[1] for cell in cells) / len(cells)
    xx = sum((cell[0] - center_x) ** 2 for cell in cells)
    yy = sum((cell[1] - center_y) ** 2 for cell in cells)
    xy = sum(
        (cell[0] - center_x) * (cell[1] - center_y) for cell in cells
    )
    if abs(xx - yy) < 1e-12 and abs(xy) < 1e-12:
        return None
    return round((degrees(0.5 * atan2(2.0 * xy, xx - yy)) + 180.0) % 180.0, 6)


def _normalized_part_roles(
    value: Any,
    components: tuple[tuple[tuple[int, int], ...], ...],
) -> tuple[dict[str, Any], ...]:
    """Validate provider-supplied semantic roles against structural components."""

    if value in (None, (), []):
        return ()
    entries = (
        ({"role": role, "component": component} for role, component in value.items())
        if isinstance(value, Mapping)
        else value
    )
    normalized: list[dict[str, Any]] = []
    for entry in entries:
        if not isinstance(entry, Mapping) or not str(entry.get("role", "")).strip():
            raise ValueError("part roles require a non-empty role and component index")
        indexes = entry.get("components", entry.get("component"))
        if indexes is None:
            raise ValueError("part roles require a non-empty role and component index")
        if isinstance(indexes, (list, tuple, set)):
            component_indexes = tuple(sorted({int(item) for item in indexes}))
        else:
            component_indexes = (int(indexes),)
        if not component_indexes or any(
            index < 0 or index >= len(components) for index in component_indexes
        ):
            raise ValueError("part role references an unknown structural component")
        normalized.append(
            {
                "role": str(entry["role"]),
                "component_indices": component_indexes,
                "cells": tuple(
                    cell
                    for index in component_indexes
                    for cell in components[index]
                ),
                "properties": dict(entry.get("properties") or {}),
            }
        )
    return tuple(
        sorted(
            normalized,
            key=lambda item: (item["role"], item["component_indices"]),
        )
    )


def normalize_grid_structure(
    item: Mapping[str, Any], role_provider: Any | None = None
) -> Mapping[str, Any]:
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
    supplied_roles = (
        item.get("partRoles")
        or topology.get("part_roles")
        or topology.get("partRoles")
    )
    if not supplied_roles and role_provider is not None and normalized_components:
        supplied_roles = role_provider.infer_part_roles(item, normalized_components)
    part_roles = _normalized_part_roles(supplied_roles, normalized_components)
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
        "orientation": _principal_orientation(cells),
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
            "part_roles": part_roles,
        },
        "properties": {
            "color": item.get("colorName"),
            "shape": item.get("shape"),
            "pixel_count": item.get("pixelCount", len(cells)),
        },
        "relationships": relationships,
    }


def normalize_image_structure(
    item: Mapping[str, Any], role_provider: Any | None = None
) -> Mapping[str, Any]:
    """Preserve provider raster semantics in the shared normalized contract."""

    bounds = tuple(int(value) for value in item.get("bounds") or item.get("bbox") or ())
    origin_x, origin_y = bounds[:2] if len(bounds) >= 2 else (0, 0)
    cells = _normalized_cells(item.get("cells") or item.get("maskCells"))
    contour = _normalized_cells(
        item.get("contour")
        or (item.get("geometry") or {}).get("boundaryCells")
        or cells
    )

    def relative(group: tuple[tuple[int, int], ...]) -> tuple[tuple[int, int], ...]:
        return tuple((x - origin_x, y - origin_y) for x, y in group)

    components = _connected_components(cells) if cells else ()
    supplied_topology = (
        dict(item.get("topology") or {})
        if isinstance(item.get("topology"), Mapping)
        else {}
    )
    topology_part_roles = supplied_topology.pop("part_roles", None)
    topology_part_roles_camel = supplied_topology.pop("partRoles", None)
    supplied_part_roles = (
        item.get("partRoles") or topology_part_roles or topology_part_roles_camel
    )
    width = bounds[2] - origin_x if len(bounds) >= 4 else None
    height = bounds[3] - origin_y if len(bounds) >= 4 else None
    orientation = item.get("orientation")
    if orientation is None:
        orientation = _principal_orientation(cells or contour)
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
    normalized_components = tuple(relative(component) for component in components)
    if not supplied_part_roles and role_provider is not None and normalized_components:
        supplied_part_roles = role_provider.infer_part_roles(item, normalized_components)
    part_roles = _normalized_part_roles(
        supplied_part_roles,
        normalized_components,
    )
    topology = {
        **supplied_topology,
        "connected_components": supplied_topology.get(
            "connected_components", len(components) if cells else None
        ),
        "components": normalized_components,
        "compound": len(components) > 1,
        "compound_parts": normalized_components if len(components) > 1 else (),
        "part_roles": part_roles,
    }
    return {
        "geometry": {
            "bounds": bounds,
            "width": width,
            "height": height,
            "cells": relative(cells),
            "boundary_cells": relative(contour),
        },
        "topology": topology,
        "properties": dict(item.get("properties") or {}),
        "relationships": relationships,
        "orientation": None if orientation is None else float(orientation),
        "scale": tuple(
            item.get("scale")
            or ((width, height) if width is not None and height is not None else ())
        ),
        "appearance": dict(item.get("appearance") or item.get("properties") or {}),
    }


def _raster_spatial_relationships(
    objects: tuple[tuple[str, tuple[int, ...]], ...],
) -> dict[str, tuple[dict[str, str], ...]]:
    """Infer conservative pairwise relations from non-rotated raster bounds."""

    relations: dict[str, set[tuple[str, str]]] = {
        object_id: set() for object_id, _bounds in objects
    }
    for index, (left_id, left) in enumerate(objects):
        if len(left) < 4:
            continue
        lx1, ly1, lx2, ly2 = left[:4]
        for right_id, right in objects[index + 1:]:
            if len(right) < 4:
                continue
            rx1, ry1, rx2, ry2 = right[:4]
            if lx2 <= rx1:
                relations[left_id].add((right_id, "left_of"))
                relations[right_id].add((left_id, "right_of"))
            elif rx2 <= lx1:
                relations[left_id].add((right_id, "right_of"))
                relations[right_id].add((left_id, "left_of"))
            if ly2 <= ry1:
                relations[left_id].add((right_id, "above"))
                relations[right_id].add((left_id, "below"))
            elif ry2 <= ly1:
                relations[left_id].add((right_id, "below"))
                relations[right_id].add((left_id, "above"))
            left_contains = lx1 <= rx1 and ly1 <= ry1 and lx2 >= rx2 and ly2 >= ry2
            right_contains = rx1 <= lx1 and ry1 <= ly1 and rx2 >= lx2 and ry2 >= ly2
            if left_contains and left != right:
                relations[left_id].add((right_id, "contains"))
                relations[right_id].add((left_id, "inside"))
            elif right_contains and left != right:
                relations[left_id].add((right_id, "inside"))
                relations[right_id].add((left_id, "contains"))
            elif max(lx1, rx1) < min(lx2, rx2) and max(ly1, ry1) < min(ly2, ry2):
                relations[left_id].add((right_id, "overlaps"))
                relations[right_id].add((left_id, "overlaps"))
    return {
        object_id: tuple(
            {"target": target, "relation": relation}
            for target, relation in sorted(values, key=lambda value: (value[1], value[0]))
        )
        for object_id, values in relations.items()
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

    def __init__(self, extractor: Any, provider: Any, role_provider: Any | None = None) -> None:
        self.extractor = extractor
        self.provider = provider
        self.role_provider = role_provider
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
                "normalizedStructure": normalize_grid_structure(item, self.role_provider),
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

    def __init__(self, extractor: Any, provider: Any, role_provider: Any | None = None) -> None:
        self.extractor = extractor
        self.provider = provider
        self.role_provider = role_provider
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
        bounded_objects: list[tuple[str, tuple[int, ...]]] = []
        for index, item in enumerate(extracted["objects"]):
            if not isinstance(item, Mapping):
                raise TypeError("image extractor object entries must be mappings")
            candidate_id = str(
                item.get("candidate_id") or item.get("id") or f"candidate_{index}"
            )
            details[candidate_id] = {
                **item,
                "normalizedStructure": normalize_image_structure(item, self.role_provider),
            }
            bounded_objects.append(
                (
                    candidate_id,
                    tuple(int(value) for value in item.get("bounds") or item.get("bbox") or ()),
                )
            )
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
        inferred_relationships = _raster_spatial_relationships(tuple(bounded_objects))
        for candidate_id, inferred in inferred_relationships.items():
            structure = dict(details[candidate_id]["normalizedStructure"])
            combined = {
                (str(item["target"]), str(item["relation"]))
                for item in (*structure.get("relationships", ()), *inferred)
            }
            structure["relationships"] = tuple(
                {"target": target, "relation": relation}
                for target, relation in sorted(combined, key=lambda value: (value[1], value[0]))
            )
            details[candidate_id] = {**details[candidate_id], "normalizedStructure": structure}
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
