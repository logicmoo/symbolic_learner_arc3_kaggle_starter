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


def _region_rects(cells: np.ndarray, cols: int, rows: int, color: str) -> list[dict]:
    """Fallback: exact region shape as merged horizontal-run rectangles."""
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
    return cmds


def _trace_outline(cellset: set, cols: int, rows: int) -> list[list[tuple[int, int]]]:
    """Find the object's outline: stitch the boundary edges between the object
    and everything else into closed rectilinear loops (region kept on the right,
    y-down). Returns loops as ordered corner-point lists."""
    edges: dict[tuple[int, int], tuple[int, int]] = {}
    for (x, y) in cellset:
        if (x, y - 1) not in cellset:
            edges[(x, y)] = (x + 1, y)
        if (x + 1, y) not in cellset:
            edges[(x + 1, y)] = (x + 1, y + 1)
        if (x, y + 1) not in cellset:
            edges[(x + 1, y + 1)] = (x, y + 1)
        if (x - 1, y) not in cellset:
            edges[(x, y + 1)] = (x, y)
    loops: list[list[tuple[int, int]]] = []
    used: set = set()
    for start in list(edges.keys()):
        if start in used or start not in edges:
            continue
        loop = [start]
        cur = start
        ok = True
        for _ in range(len(edges) + 4):
            used.add(cur)
            nxt = edges.get(cur)
            if nxt is None:
                ok = False
                break
            if nxt == start:
                break
            loop.append(nxt)
            cur = nxt
        else:
            ok = False
        if ok and len(loop) >= 4:
            loops.append(loop)
    return loops


def _simplify(loop: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Drop collinear midpoints from a rectilinear loop."""
    n = len(loop)
    out = []
    for i in range(n):
        a, b, c = loop[i - 1], loop[i], loop[(i + 1) % n]
        if (b[0] - a[0]) * (c[1] - b[1]) != (b[1] - a[1]) * (c[0] - b[0]):
            out.append(b)
    return out or loop


def region_turtle(cells: np.ndarray, cols: int, rows: int, color: str) -> dict:
    """Turtle program that REDRAWS the object's outline.

    Thick blobs: trace the boundary and stroke a filled polygon with a ~1-cell
    brush. Thin blobs (outline pixels close together): collapse to a single
    polyline stroked with a wider brush = the blob's thickness.
    Falls back to run-rectangles for degenerate shapes."""
    sx, sy = 1000.0 / cols, 1000.0 / rows
    ys, xs = np.where(cells)
    if xs.size == 0:
        return {"version": 1, "background": "transparent", "penColor": color, "penWidth": 2, "commands": []}
    minx, maxx, miny, maxy = int(xs.min()), int(xs.max()), int(ys.min()), int(ys.max())
    wcell, hcell = maxx - minx + 1, maxy - miny + 1
    brush = max(2, round(min(sx, sy)))

    # thin object -> one wide-brush stroke down its length
    if min(wcell, hcell) <= 2:
        pts: list[list[int]] = []
        if wcell >= hcell:
            for cx in range(minx, maxx + 1):
                col = ys[xs == cx]
                if col.size:
                    pts.append([round((cx + 0.5) * sx), round((float(col.mean()) + 0.5) * sy)])
            thickness = max(brush, round(hcell * sy))
        else:
            for cy in range(miny, maxy + 1):
                rowx = xs[ys == cy]
                if rowx.size:
                    pts.append([round((float(rowx.mean()) + 0.5) * sx), round((cy + 0.5) * sy)])
            thickness = max(brush, round(wcell * sx))
        if len(pts) >= 2:
            return {"version": 1, "background": "transparent", "penColor": color, "penWidth": int(thickness),
                    "commands": [{"op": "move", "x": pts[0][0], "y": pts[0][1]},
                                 {"op": "polyline", "points": pts, "outline": color}]}
        if len(pts) == 1:
            return {"version": 1, "background": "transparent", "penColor": color, "penWidth": 2,
                    "commands": [{"op": "dot", "x": pts[0][0], "y": pts[0][1], "radius": max(brush, round(min(sx, sy))), "color": color}]}

    # thick object -> traced outline polygon, stroked with a ~1-cell brush
    cmds: list[dict] = []
    try:
        cellset = set(zip(xs.tolist(), ys.tolist()))
        loops = _trace_outline(cellset, cols, rows)
        loops.sort(key=lambda lp: (max(p[0] for p in lp) - min(p[0] for p in lp))
                   * (max(p[1] for p in lp) - min(p[1] for p in lp)), reverse=True)
        if loops:
            pts2 = [[round(px * sx), round(py * sy)] for (px, py) in _simplify(loops[0])]
            if len(pts2) >= 3:
                cmds = [{"op": "move", "x": pts2[0][0], "y": pts2[0][1]},
                        {"op": "polygon", "points": pts2, "fill": color, "outline": color}]
    except Exception:  # noqa: BLE001
        cmds = []
    if not cmds:
        cmds = _region_rects(cells, cols, rows, color)
    return {"version": 1, "background": "transparent", "penColor": color, "penWidth": brush, "commands": cmds}


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


from color_names import nearest_name as _color_name


def _shape_sig(cells: np.ndarray, hexs: str) -> tuple:
    """Translation-invariant signature of a blob: its color + the set of cell
    offsets from its top-left. Same shape+color that merely translated between
    frames shares this signature."""
    ys, xs = np.where(cells)
    if xs.size == 0:
        return (hexs, ())
    minx, miny = int(xs.min()), int(ys.min())
    return (hexs, tuple(sorted(zip((xs - minx).tolist(), (ys - miny).tolist()))))


def _motion(info_a: dict, info_b: dict) -> dict:
    """Match A-regions to B-regions by (color, exact shape); return
    {gidA: (dx, dy)} centroid displacement (common fate)."""
    from collections import defaultdict
    bysig: dict = defaultdict(list)
    for _g, b in info_b.items():
        bysig[b["sig"]].append(b)
    used: set = set()
    disp: dict = {}
    for g, i in info_a.items():
        cands = [b for b in bysig.get(i["sig"], []) if id(b) not in used]
        if not cands:
            continue
        best = min(cands, key=lambda b: (b["cx"] - i["cx"]) ** 2 + (b["cy"] - i["cy"]) ** 2)
        used.add(id(best))
        disp[g] = (best["cx"] - i["cx"], best["cy"] - i["cy"])
    return disp


def extract_frame(png_path: str, char: str, partner_path: str | None = None) -> dict:
    idx, hexpal, cols, rows = decode_grid(png_path)
    labels, info = label_regions(idx)
    for gid, i in info.items():
        i["hex"] = hexpal[i["color_id"]]
        i["sig"] = _shape_sig(i["cells"], i["hex"])
    pairs = adjacency(labels)
    enclos = enclosures(info, pairs)
    pof, obj = _run_prolog(info, pairs, enclos, cols, rows)

    # common-fate grouping: parts that translate by the same vector between the
    # two frames are one moving object.
    move_group: dict = {}
    if partner_path:
        try:
            idx_b, pal_b, _cb, _rb = decode_grid(partner_path)
            _lb, info_b = label_regions(idx_b)
            for _g, b in info_b.items():
                b["hex"] = pal_b[b["color_id"]]
                b["sig"] = _shape_sig(b["cells"], b["hex"])
            for gid, d in _motion(info, info_b).items():
                if d != (0, 0):
                    move_group[f"r{gid}"] = f"move_{d[0]}_{d[1]}"
        except Exception:  # noqa: BLE001
            move_group = {}

    # every part gets a partOf group: its adjacency-cluster object, else (a
    # background/large blob) its own group -> full coverage like the LLM line.
    # Members are named part_<name_color> (e.g. part_limegreen_1); the internal
    # r<gid> ids are only used for the swipl facts and translated here.
    # draw big blobs first so nested / detail blobs render on top
    order = sorted(info.items(), key=lambda kv: -kv[1]["area"])
    mlines = [f"; symbolic (prolog) part-graph for {char}  ({len(info)} parts)",
              f"(character {char})"]
    geom = []
    partof_all: dict[str, str] = {}
    pid_of: dict[str, str] = {}
    raw_of: dict[str, str] = {}
    color_n: dict[str, int] = {}
    for gid, i in order:
        rid = f"r{gid}"
        cname = _color_name(i["hex"])
        color_n[cname] = color_n.get(cname, 0) + 1
        lbl = f"{cname}_{color_n[cname]}"
        pid = f"part_{lbl}"
        pid_of[rid] = pid
        # common fate first: parts that moved by the same vector are one object;
        # else the adjacency cluster; else a singleton.
        raw_of[pid] = move_group.get(rid) or obj.get(rid) or f"g{gid}"
        mlines.append(f'(part {char} {pid} (label "{lbl}") (color {i["hex"]}))')
        geom.append({"id": pid, "label": lbl, "color": i["hex"],
                     "partOf": "",
                     "turtle": region_turtle(i["cells"], cols, rows, i["hex"])})
    # unify every group id (adjacency clusters + singletons) to obj_N, numbered
    # in first-seen (big-first) order.
    raw_order: list[str] = []
    for g in raw_of.values():
        if g not in raw_order:
            raw_order.append(g)
    gmap = {g: f"obj_{k}" for k, g in enumerate(raw_order, 1)}
    partof_all = {pid: gmap[g] for pid, g in raw_of.items()}
    for e in geom:
        e["partOf"] = partof_all[e["id"]]
    groups = [gmap[g] for g in raw_order]
    for g in groups:
        mlines.append(f"(group {char} {g})")
    for pid, g in partof_all.items():
        mlines.append(f"(partOf {char} {pid} {g})")
    for inner, outer in pof:
        mlines.append(f"(inside {char} {pid_of.get(inner, inner)} {pid_of.get(outer, outer)})")
    metta = "\n".join(mlines) + "\n"
    return {"metta": metta, "geom": geom, "nparts": len(info),
            "nrels": len(pof) + len(obj), "cols": cols, "rows": rows,
            "ngroups": len(groups)}


if __name__ == "__main__":
    import sys
    r = extract_frame(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "frame")
    print(f"parts={r['nparts']} groups={r['ngroups']} rels={r['nrels']} grid={r['cols']}x{r['rows']}")
    print(r["metta"][:600])
