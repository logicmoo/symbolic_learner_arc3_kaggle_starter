from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from hashlib import sha256
from typing import Any


DEFAULT_GRID: list[list[int]] = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 1, 0, 2, 0, 0],
    [0, 1, 0, 1, 0, 2, 0, 0],
    [0, 1, 1, 1, 0, 2, 2, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
]

COLOR_NAMES = {
    0: "black",
    1: "blue",
    2: "red",
    3: "green",
    4: "yellow",
    5: "gray",
    6: "magenta",
    7: "orange",
    8: "cyan",
    9: "brown",
}


@dataclass(frozen=True)
class Component:
    object_id: str
    color: int
    cells: tuple[tuple[int, int], ...]

    @property
    def min_x(self) -> int:
        return min(x for x, _ in self.cells)

    @property
    def max_x(self) -> int:
        return max(x for x, _ in self.cells)

    @property
    def min_y(self) -> int:
        return min(y for _, y in self.cells)

    @property
    def max_y(self) -> int:
        return max(y for _, y in self.cells)

    @property
    def width(self) -> int:
        return self.max_x - self.min_x + 1

    @property
    def height(self) -> int:
        return self.max_y - self.min_y + 1


def _validate_grid(value: Any) -> list[list[int]]:
    if value is None:
        return [row[:] for row in DEFAULT_GRID]
    if not isinstance(value, list) or not value:
        raise ValueError("grid must be a non-empty array of rows")
    width = None
    result: list[list[int]] = []
    for row in value:
        if not isinstance(row, list) or not row:
            raise ValueError("every grid row must be a non-empty array")
        if width is None:
            width = len(row)
        elif len(row) != width:
            raise ValueError("all grid rows must have the same width")
        parsed: list[int] = []
        for cell in row:
            if not isinstance(cell, int) or not 0 <= cell <= 9:
                raise ValueError("grid cells must be integers from 0 through 9")
            parsed.append(cell)
        result.append(parsed)
    if len(result) > 64 or (width or 0) > 64:
        raise ValueError("demo grid may not exceed 64x64")
    return result


def _components(grid: list[list[int]]) -> list[Component]:
    height = len(grid)
    width = len(grid[0])
    seen: set[tuple[int, int]] = set()
    found: list[Component] = []
    color_counts: dict[int, int] = {}

    for y in range(height):
        for x in range(width):
            color = grid[y][x]
            if color == 0 or (x, y) in seen:
                continue
            queue = deque([(x, y)])
            seen.add((x, y))
            cells: list[tuple[int, int]] = []
            while queue:
                cx, cy = queue.popleft()
                cells.append((cx, cy))
                for nx, ny in ((cx - 1, cy), (cx + 1, cy), (cx, cy - 1), (cx, cy + 1)):
                    if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in seen and grid[ny][nx] == color:
                        seen.add((nx, ny))
                        queue.append((nx, ny))
            color_counts[color] = color_counts.get(color, 0) + 1
            ordinal = color_counts[color]
            name = COLOR_NAMES.get(color, f"color_{color}")
            found.append(Component(f"obj_{name}_{ordinal}", color, tuple(sorted(cells, key=lambda p: (p[1], p[0])))))
    return found


def _shape(component: Component) -> str:
    occupied = set(component.cells)
    area = component.width * component.height
    count = len(component.cells)
    if count == area:
        return "rectangle" if component.width != component.height else "square"
    border = {
        (x, y)
        for y in range(component.min_y, component.max_y + 1)
        for x in range(component.min_x, component.max_x + 1)
        if x in (component.min_x, component.max_x) or y in (component.min_y, component.max_y)
    }
    if component.width >= 3 and component.height >= 3 and occupied == border:
        return "hollow_rectangle" if component.width != component.height else "hollow_square"
    if component.width == 1:
        return "vertical_line"
    if component.height == 1:
        return "horizontal_line"
    endpoints = 0
    for x, y in occupied:
        degree = sum((x + dx, y + dy) in occupied for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)))
        if degree == 1:
            endpoints += 1
    if endpoints == 2 and count == component.width + component.height - 1:
        return "angle"
    return "irregular"


def _turtle(component: Component) -> str:
    cells = set(component.cells)
    lines = [f"object({component.object_id}).", f"turtle({component.object_id}, ["]
    first = True
    for y in range(component.min_y, component.max_y + 1):
        runs: list[tuple[int, int]] = []
        start = None
        for x in range(component.min_x, component.max_x + 2):
            if (x, y) in cells and start is None:
                start = x
            if start is not None and (x, y) not in cells:
                runs.append((start, x - 1))
                start = None
        for start_x, end_x in runs:
            if not first:
                lines[-1] += ","
            lines.extend([
                "    penup,",
                f"    set_pos({start_x}, {y}),",
                f"    setcolor({COLOR_NAMES.get(component.color, component.color)}),",
                "    pendown,",
                f"    fwd({end_x - start_x})",
            ])
            first = False
    lines.append("]).")
    return "\n".join(lines)


def analyze_grid(value: Any = None) -> dict[str, Any]:
    grid = _validate_grid(value)
    components = _components(grid)
    objects: list[dict[str, Any]] = []
    prolog_lines: list[str] = []

    for component in components:
        shape = _shape(component)
        color_name = COLOR_NAMES.get(component.color, f"color_{component.color}")
        bounds = [component.min_x, component.min_y, component.width, component.height]
        facts = [
            f"object({component.object_id}).",
            f"color({component.object_id}, {color_name}).",
            f"shape({component.object_id}, {shape}).",
            f"bounds({component.object_id}, {bounds[0]}, {bounds[1]}, {bounds[2]}, {bounds[3]}).",
            f"pixel_count({component.object_id}, {len(component.cells)}).",
        ]
        prolog_lines.extend(facts)
        objects.append({
            "id": component.object_id,
            "name": component.object_id.replace("obj_", "").replace("_", " ").title(),
            "color": component.color,
            "colorName": color_name,
            "cells": [list(cell) for cell in component.cells],
            "bounds": bounds,
            "shape": shape,
            "pixelCount": len(component.cells),
            "facts": "\n".join(facts),
            "turtleProgram": _turtle(component),
        })

    reconstruction = [[0 for _ in row] for row in grid]
    for obj in objects:
        for x, y in obj["cells"]:
            reconstruction[y][x] = obj["color"]
    differences = [
        [x, y, grid[y][x], reconstruction[y][x]]
        for y in range(len(grid))
        for x in range(len(grid[0]))
        if grid[y][x] != reconstruction[y][x]
    ]
    digest = sha256(bytes(cell for row in grid for cell in row)).hexdigest()

    return {
        "source": "backend.runtime.analyze_grid",
        "algorithm": "4-connected component extraction + symbolic feature derivation + exact reconstruction",
        "grid": grid,
        "width": len(grid[0]),
        "height": len(grid),
        "sha256": digest,
        "objects": objects,
        "objectCount": len(objects),
        "prologFacts": "\n".join(prolog_lines),
        "reconstruction": reconstruction,
        "differenceCount": len(differences),
        "differences": differences,
        "exactMatch": not differences,
    }
