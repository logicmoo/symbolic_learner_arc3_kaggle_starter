from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from PIL import Image

from .adapters import ImageAdapter


def _components(cells: set[tuple[int, int]]) -> tuple[tuple[tuple[int, int], ...], ...]:
    remaining = set(cells)
    result = []
    while remaining:
        pending = [min(remaining)]
        remaining.remove(pending[0])
        component = set()
        while pending:
            cell = pending.pop()
            component.add(cell)
            x, y = cell
            for neighbor in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    pending.append(neighbor)
        result.append(tuple(sorted(component)))
    return tuple(sorted(result, key=lambda item: item[0]))


class AlphaContourProvider:
    """Extract transparent sprites and exact pixel-boundary vector contours."""

    def __call__(self, image: Image.Image) -> Mapping[str, Any]:
        rgba = image.convert("RGBA")
        visible = {
            (x, y)
            for y in range(rgba.height)
            for x in range(rgba.width)
            if rgba.getpixel((x, y))[3] > 0
        }
        objects = []
        for index, component in enumerate(_components(visible)):
            component_set = set(component)
            boundary = tuple(
                cell
                for cell in component
                if any(
                    neighbor not in component_set
                    for neighbor in (
                        (cell[0] - 1, cell[1]),
                        (cell[0] + 1, cell[1]),
                        (cell[0], cell[1] - 1),
                        (cell[0], cell[1] + 1),
                    )
                )
            )
            xs = [cell[0] for cell in component]
            ys = [cell[1] for cell in component]
            colors = sorted({rgba.getpixel(cell)[:3] for cell in component})
            objects.append(
                {
                    "id": f"sprite_{index}",
                    "bounds": [min(xs), min(ys), max(xs) + 1, max(ys) + 1],
                    "properties": {
                        "colors": [list(color) for color in colors],
                        "pixel_count": len(component),
                    },
                    "topology": {"connected_components": 1},
                    "contour": [list(cell) for cell in boundary],
                    "vector": {
                        "kind": "pixel_boundary",
                        "points": [list(cell) for cell in boundary],
                    },
                }
            )
        return {
            "source": "alpha_contour_provider",
            "algorithm": "4-connected-alpha-components",
            "objects": objects,
        }


class SpriteAdapter(ImageAdapter):
    """Image adapter preconfigured for transparent sprite sheets."""

    def __init__(self, provider: Any, extractor: Any | None = None) -> None:
        super().__init__(extractor or AlphaContourProvider(), provider)
