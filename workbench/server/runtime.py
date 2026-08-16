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


def _hole_regions(component: Component) -> list[list[tuple[int, int]]]:
    occupied = set(component.cells)
    empty = {
        (x, y)
        for y in range(component.min_y, component.max_y + 1)
        for x in range(component.min_x, component.max_x + 1)
        if (x, y) not in occupied
    }
    outside: set[tuple[int, int]] = set()
    queue = deque(
        cell
        for cell in empty
        if cell[0] in (component.min_x, component.max_x)
        or cell[1] in (component.min_y, component.max_y)
    )
    outside.update(queue)
    while queue:
        x, y = queue.popleft()
        for neighbor in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if neighbor in empty and neighbor not in outside:
                outside.add(neighbor)
                queue.append(neighbor)
    remaining = empty - outside
    regions: list[list[tuple[int, int]]] = []
    while remaining:
        start = min(remaining, key=lambda item: (item[1], item[0]))
        region: list[tuple[int, int]] = []
        queue = deque([start])
        remaining.remove(start)
        while queue:
            cell = queue.popleft()
            region.append(cell)
            x, y = cell
            for neighbor in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    queue.append(neighbor)
        regions.append(sorted(region, key=lambda item: (item[1], item[0])))
    return regions


def _boundary_cells(component: Component) -> list[tuple[int, int]]:
    occupied = set(component.cells)
    return [
        cell
        for cell in component.cells
        if any(
            (cell[0] + dx, cell[1] + dy) not in occupied
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1))
        )
    ]


def _relationships(left: Component, right: Component) -> list[str]:
    result: list[str] = []
    if left.max_x < right.min_x:
        result.append("left_of")
    if left.min_x > right.max_x:
        result.append("right_of")
    if left.max_y < right.min_y:
        result.append("above")
    if left.min_y > right.max_y:
        result.append("below")
    horizontal_gap = max(right.min_x - left.max_x - 1, left.min_x - right.max_x - 1, 0)
    vertical_gap = max(right.min_y - left.max_y - 1, left.min_y - right.max_y - 1, 0)
    if horizontal_gap == 0 and vertical_gap == 0:
        result.append("adjacent_bounds")
    return result


def _turtle(component: Component) -> str:
    cells = set(component.cells)
    lines = [f"object({component.object_id}).", f"turtle({component.object_id}, ["]
    filled_rectangle = len(cells) == component.width * component.height
    if filled_rectangle and component.width <= 4 and component.height >= component.width:
        center_x = component.min_x + component.width // 2
        lines.extend([
            "    penup,",
            f"    set_pos({center_x}, {component.min_y}),",
            f"    setcolor({COLOR_NAMES.get(component.color, component.color)}),",
            f"    pen_width({component.width}),",
            "    rot(90),",
            "    pendown,",
            "    set_cell,",
            f"    fwd({component.height - 1})",
            "]).",
        ])
        return "\n".join(lines)
    if filled_rectangle and component.height <= 4:
        center_y = component.min_y + component.height // 2
        lines.extend([
            "    penup,",
            f"    set_pos({component.min_x}, {center_y}),",
            f"    setcolor({COLOR_NAMES.get(component.color, component.color)}),",
            f"    pen_width({component.height}),",
            "    pendown,",
            "    set_cell,",
            f"    fwd({component.width - 1})",
            "]).",
        ])
        return "\n".join(lines)
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
                "    pen_width(1),",
                "    set_cell,",
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
        holes = _hole_regions(component)
        boundary = _boundary_cells(component)
        filled_rectangle = len(component.cells) == component.width * component.height
        line_thickness = (
            min(component.width, component.height) if filled_rectangle else 1
        )
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
            "geometry": {
                "minX": component.min_x,
                "minY": component.min_y,
                "maxX": component.max_x,
                "maxY": component.max_y,
                "width": component.width,
                "height": component.height,
                "boundaryCells": [list(cell) for cell in boundary],
            },
            "topology": {
                "connectedComponents": 1,
                "holeCount": len(holes),
                "holes": [[list(cell) for cell in region] for region in holes],
            },
            "lineThickness": line_thickness,
            "relationships": [],
            "facts": "\n".join(facts),
            "turtleProgram": _turtle(component),
        })

    by_id = {component.object_id: component for component in components}
    for obj in objects:
        source_component = by_id[obj["id"]]
        obj["relationships"] = [
            {"target": target.object_id, "relation": relation}
            for target in components
            if target.object_id != source_component.object_id
            for relation in _relationships(source_component, target)
        ]

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
