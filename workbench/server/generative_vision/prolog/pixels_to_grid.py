"""pixels_to_grid.py — turn a flat-color ARC render (PNG bitmap) back into the
underlying color grid, then emit it as JSON and as Prolog cell/3 facts that
arc_parts.pl can consume directly.

ARC frames are rendered as N*N equal square cells of one flat color each, so we
can recover the grid losslessly by detecting the cell pitch and sampling one
pixel per cell.

Usage:
    python pixels_to_grid.py FRAME.png [--prolog out.pl] [--json out.json]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from PIL import Image


def _change_positions(line_colors: list[tuple]) -> list[int]:
    """Indices where the color changes from the previous position."""
    out = []
    for i in range(1, len(line_colors)):
        if line_colors[i] != line_colors[i - 1]:
            out.append(i)
    return out


def _gcd_list(nums: list[int]) -> int:
    from math import gcd
    g = 0
    for n in nums:
        g = gcd(g, n)
    return g


def detect_pitch(px, w: int, h: int) -> int:
    """Detect the square cell size in pixels via the GCD of colour-run spans
    sampled along the middle row and column (robust to grid lines)."""
    mid_row = [px[x, h // 2] for x in range(w)]
    mid_col = [px[w // 2, y] for y in range(h)]
    spans: list[int] = []
    for line, n in ((mid_row, w), (mid_col, h)):
        bounds = [0] + _change_positions(line) + [n]
        spans += [b - a for a, b in zip(bounds, bounds[1:]) if b > a]
    if not spans:
        return 1
    pitch = _gcd_list(spans)
    return max(1, pitch)


def to_grid(img: Image.Image) -> list[list[str]]:
    im = img.convert("RGB")
    w, h = im.size
    px = im.load()
    pitch = detect_pitch(px, w, h)
    cols, rows = w // pitch, h // pitch
    grid: list[list[str]] = []
    for gy in range(rows):
        row: list[str] = []
        for gx in range(cols):
            # sample the cell centre
            cx = min(w - 1, gx * pitch + pitch // 2)
            cy = min(h - 1, gy * pitch + pitch // 2)
            r, g, b = px[cx, cy]
            row.append(f"#{r:02x}{g:02x}{b:02x}")
        grid.append(row)
    return grid


def to_prolog(grid: list[list[str]]) -> str:
    lines = [
        "% auto-generated ARC grid facts: cell(X, Y, Color).  X=col, Y=row, top-left origin.",
        ":- dynamic cell/3.",
        "",
    ]
    for y, row in enumerate(grid):
        for x, c in enumerate(row):
            lines.append(f"cell({x}, {y}, '{c}').")
    return "\n".join(lines) + "\n"


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("frame")
    ap.add_argument("--prolog")
    ap.add_argument("--json")
    args = ap.parse_args(argv)

    img = Image.open(args.frame)
    grid = to_grid(img)
    rows = len(grid)
    cols = len(grid[0]) if grid else 0
    palette = sorted({c for row in grid for c in row})
    print(f"{args.frame}: {img.size[0]}x{img.size[1]}px -> {cols}x{rows} cells, "
          f"{len(palette)} colors")
    print("palette:", ", ".join(palette))

    if args.json:
        Path(args.json).write_text(json.dumps({"cols": cols, "rows": rows, "grid": grid}), encoding="utf-8")
        print("wrote", args.json)
    if args.prolog:
        Path(args.prolog).write_text(to_prolog(grid), encoding="utf-8")
        print("wrote", args.prolog)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
