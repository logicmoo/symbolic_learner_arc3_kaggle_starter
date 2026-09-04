"""symbolic_arc.py — the "Prolog line" of the ARC reduce pipeline.

For a flat-color ARC frame it does, deterministically and WITHOUT any LLM:
  1. decode the PNG back to its exact color grid (auto cell-pitch),
  2. label connected same-color regions + derive pixel TOPOLOGY (adjacency,
     enclosure, border) — no bounding boxes,
  3. run SWI-Prolog (arc_group.pl) to do the grouping (containment + object
     instances),
  4. emit the SAME artifacts the LLM line produces: a MeTTa part-graph and a
     per-part turtle geometry sidecar (parts.json), so both render identically
     in the reduce UI.

bbox is never used for grouping; a part's shape is the exact region, drawn as
merged horizontal-run rectangles.
"""
from __future__ import annotations

import json
import subprocess
import tempfile
from math import gcd
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

STRUCT4 = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]])
_HERE = Path(__file__).resolve().parent
GROUP_PL = _HERE / "arc_group.pl"


def _detect_pitch(arr: np.ndarray) -> int:
    """Square cell size in px, via GCD of colour-run spans on the mid row/col."""
    h, w, _ = arr.shape
    spans: list[int] = []
    for line, n in ((arr[h // 2, :, :], w), (arr[:, w // 2, :], h)):
        bounds = [0]
        for i in range(1, n):
            if not np.array_equal(line[i], line[i - 1]):
                bounds.append(i)
        bounds.append(n)
        spans += [b - a for a, b in zip(bounds, bounds[1:]) if b > a]
    g = 0
    for s in spans:
        g = gcd(g, s)
    return max(1, g)


def decode_grid(path: str) -> tuple[np.ndarray, int, int]:
    """Return (idx grid rows x cols of int color-ids, cols, rows) + palette."""
    im = Image.open(path).convert("RGB")
    arr = np.asarray(im)
    pitch = _detect_pitch(arr)
    h, w, _ = arr.shape
    cols, rows = w // pitch, h // pitch
    # sample the centre of each cell
    ys = (np.arange(rows) * pitch + pitch // 2).clip(0, h - 1)
    xs = (np.arange(cols) * pitch + pitch // 2).clip(0, w - 1)
    cells = arr[np.ix_(ys, xs)]                       # rows x cols x 3
    flat = cells.reshape(-1, 3)
    palette, inv = np.unique(flat, axis=0, return_inverse=True)
    idx = inv.reshape(rows, cols)
    hexpal = [f"#{r:02x}{g:02x}{b:02x}" for r, g, b in palette]
    return idx, hexpal, cols, rows


def label_regions(idx: np.ndarray):
    rows, cols = idx.shape
    labels = np.zeros((rows, cols), dtype=np.int32)
    info: dict[int, dict] = {}
    nxt = 1
    for ci in np.unique(idx):
        lab, n = ndimage.label(idx == ci, structure=STRUCT4)
        for comp in range(1, n + 1):
            sel = lab == comp
            gid = nxt
            nxt += 1
            labels[sel] = gid
            ys, xs = np.where(sel)
            info[gid] = {
                "color_id": int(ci),
                "area": int(xs.size),
                "cx": int(round(xs.mean())),
                "cy": int(round(ys.mean())),
                "border": bool(xs.min() == 0 or ys.min() == 0 or xs.max() == cols - 1 or ys.max() == rows - 1),
                "cells": sel,
            }
    return labels, info


def adjacency(labels: np.ndarray) -> set[tuple[int, int]]:
    pairs: set[tuple[int, int]] = set()
    for A, B in ((labels[:, :-1], labels[:, 1:]), (labels[:-1, :], labels[1:, :])):
        d = A != B
        if not d.any():
            continue
        u = np.stack([A[d], B[d]], axis=1)
        u.sort(axis=1)
        for a, b in np.unique(u, axis=0):
            pairs.add((int(a), int(b)))
    return pairs


def region_turtle(cells: np.ndarray, cols: int, rows: int, color: str) -> dict:
    """Exact region shape as merged horizontal-run rectangles in 0..1000."""
    sx, sy = 1000.0 / cols, 1000.0 / rows
    cmds = []
    for y in range(rows):
        row = cells[y]
        x = 0
        while x < cols:
            if row[x]:
                x0 = x
                while x < cols and row[x]:
                    x += 1
                cmds.append({"op": "rectangle",
                             "box": [round(x0 * sx), round(y * sy), round(x * sx), round((y + 1) * sy)],
                             "fill": color, "outline": color})
            else:
                x += 1
    return {"version": 1, "background": "transparent", "penColor": color, "penWidth": 2, "commands": cmds}


def _run_prolog(region_info, pairs, enclos, cols, rows) -> tuple[list[tuple[str, str]], dict[str, str]]:
    """Write facts, run swipl arc_group.pl, parse pof/obj lines."""
    lines = [":- dynamic region/4.", ":- dynamic adjacent/2.", ":- dynamic encloses/2.",
             ":- dynamic border/1.", ":- dynamic img_size/2.", f"img_size({cols},{rows})."]
    for gid, i in region_info.items():
        lines.append(f"region(r{gid}, '{i['hex']}', {i['area']}, centroid({i['cx']},{i['cy']})).")
        if i["border"]:
            lines.append(f"border(r{gid}).")
    for a, b in sorted(pairs):
        lines.append(f"adjacent(r{a}, r{b}).")
    for o, i in enclos:
        lines.append(f"encloses(r{o}, r{i}).")
    with tempfile.NamedTemporaryFile("w", suffix=".pl", delete=False, encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
        facts = f.name
    try:
        out = subprocess.run(
            ["swipl", "-q", "-g",
             f"consult('{GROUP_PL.as_posix()}'), consult('{Path(facts).as_posix()}'), emit",
             "-t", "halt"],
            capture_output=True, text=True, timeout=60).stdout
    finally:
        Path(facts).unlink(missing_ok=True)
    pof: list[tuple[str, str]] = []
    obj: dict[str, str] = {}
    for ln in out.splitlines():
        p = ln.split()
        if len(p) == 3 and p[0] == "pof":
            pof.append((p[1], p[2]))
        elif len(p) == 3 and p[0] == "obj":
            obj[p[2]] = "obj" + p[1]
    return pof, obj


def enclosures(region_info, pairs) -> list[tuple[int, int]]:
    from collections import defaultdict
    neigh = defaultdict(set)
    for a, b in pairs:
        neigh[a].add(b)
        neigh[b].add(a)
    out = []
    for gid, i in region_info.items():
        if i["border"]:
            continue
        ns = neigh.get(gid, set())
        if len(ns) == 1:
            out.append((next(iter(ns)), gid))
    return out


def extract_frame(png_path: str, char: str) -> dict:
    idx, hexpal, cols, rows = decode_grid(png_path)
    labels, info = label_regions(idx)
    for gid, i in info.items():
        i["hex"] = hexpal[i["color_id"]]
    pairs = adjacency(labels)
    enclos = enclosures(info, pairs)
    pof, obj = _run_prolog(info, pairs, enclos, cols, rows)

    # metta + parts.json in the SAME schema as the LLM line
    groups = sorted(set(obj.values()))
    mlines = [f"; symbolic (prolog) part-graph for {char}  ({len(info)} parts)",
              f"(character {char})"]
    geom = []
    for gid, i in info.items():
        rid = f"r{gid}"
        lbl = i["hex"]
        mlines.append(f'(part {char} {rid} (label "{lbl}") (color {i["hex"]}))')
        geom.append({"id": rid, "label": lbl, "color": i["hex"],
                     "partOf": obj.get(rid, ""),
                     "turtle": region_turtle(i["cells"], cols, rows, i["hex"])})
    for g in groups:
        mlines.append(f"(group {char} {g})")
    for rid, g in obj.items():
        mlines.append(f"(partOf {char} {rid} {g})")
    for inner, outer in pof:
        mlines.append(f"(inside {char} {inner} {outer})")
    metta = "\n".join(mlines) + "\n"
    return {"metta": metta, "geom": geom, "nparts": len(info),
            "nrels": len(pof) + len(obj), "cols": cols, "rows": rows,
            "ngroups": len(groups)}


if __name__ == "__main__":
    import sys
    r = extract_frame(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "frame")
    print(f"parts={r['nparts']} groups={r['ngroups']} rels={r['nrels']} grid={r['cols']}x{r['rows']}")
    print(r["metta"][:600])
