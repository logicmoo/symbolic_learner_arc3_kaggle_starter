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
import hashlib
import itertools
import os
import subprocess
import tempfile
import time
from math import gcd
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

STRUCT4 = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]])
_HERE = Path(__file__).resolve().parent
GROUP_PL = _HERE / "arc_group.pl"
MEM_PL = _HERE / "object_memory.pl"


def _repo_root() -> Path:
    """Walk up to the repository root (dir holding .git / workbench)."""
    p = _HERE
    for _ in range(8):
        if (p / ".git").exists() or (p / "workbench").is_dir():
            return p
        p = p.parent
    return _HERE.parents[4]


def memory_dir() -> Path:
    """Canonical on-disk object-memory DATA DIRECTORY. Global across games and
    sessions by default (so an object seen in one game/level can be recognized in
    another); override with $OBJECT_MEMORY_DIR. Created on demand. The persistent
    Prolog store lives here and is db_attach-ed (read) before every operation."""
    env = os.environ.get("OBJECT_MEMORY_DIR")
    d = Path(env) if env else (_repo_root() / "data" / "object_memory")
    d.mkdir(parents=True, exist_ok=True)
    return d


def memory_db_path() -> str:
    """Path to the persistent object-memory DB file inside the data directory."""
    return str(memory_dir() / "object_memory.db.pl")


def _shape_key(sig) -> str:
    """Stable short hash of a part's D4-canonical shape (color-independent), used
    as the persistent-memory key so the same shape is recognized across runs."""
    canon = sig[1] if isinstance(sig, tuple) and len(sig) > 1 else sig
    return hashlib.sha1(repr(canon).encode("utf-8")).hexdigest()[:12]


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


def _canon(loop: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Rotate a loop to start at its top-left-most vertex so identical shapes
    yield the same vertex sequence — two translated copies then differ ONLY in
    their x,y coordinates."""
    if not loop:
        return loop
    k = min(range(len(loop)), key=lambda i: (loop[i][1], loop[i][0]))
    return loop[k:] + loop[:k]


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

# dihedral group D4 (the 8 flips/rotations) as integer (x, y) maps.
_D4 = (
    ("identity", lambda x, y: (x, y)),
    ("rot90", lambda x, y: (y, -x)),
    ("rot180", lambda x, y: (-x, -y)),
    ("rot270", lambda x, y: (-y, x)),
    ("flip_h", lambda x, y: (-x, y)),
    ("flip_v", lambda x, y: (x, -y)),
    ("transpose", lambda x, y: (y, x)),
    ("anti_transpose", lambda x, y: (-y, -x)),
)


def _offsets(cells: np.ndarray) -> tuple:
    """Cell offsets from the blob's top-left (translation-normalized)."""
    ys, xs = np.where(cells)
    if xs.size == 0:
        return ()
    minx, miny = int(xs.min()), int(ys.min())
    return tuple(sorted(zip((xs - minx).tolist(), (ys - miny).tolist())))


def _norm(offs) -> frozenset:
    if not offs:
        return frozenset()
    mnx = min(o[0] for o in offs)
    mny = min(o[1] for o in offs)
    return frozenset((o[0] - mnx, o[1] - mny) for o in offs)


def _canon_key(offs) -> tuple:
    """Shape key invariant under all 8 flips/rotations (smallest variant)."""
    best = None
    for _n, f in _D4:
        t = tuple(sorted(_norm([f(x, y) for x, y in offs])))
        if best is None or t < best:
            best = t
    return best or ()


def _transform_between(off_a, off_b) -> str:
    """The D4 transform that maps shape A onto shape B (else 'deformed')."""
    nb = _norm(off_b)
    for name, f in _D4:
        if _norm([f(x, y) for x, y in off_a]) == nb:
            return name
    return "deformed"


def _shape_sig(cells: np.ndarray, hexs: str) -> tuple:
    """Color + D4-canonical shape: same up to flip / rotation / translation."""
    return (hexs, _canon_key(_offsets(cells)))


def _motion(info_a: dict, info_b: dict):
    """Match A-regions to B-regions by (color, D4-canonical shape) as a rigid
    motion. Returns (out, used_b): out[gidA] = {"d": (dx,dy), "tf": name,
    "key": (kx,ky)}, and used_b = the set of matched B gids (so the caller can
    tell what appeared/disappeared)."""
    from collections import defaultdict
    fmap = dict(_D4)
    bysig: dict = defaultdict(list)
    for gb, b in info_b.items():
        bysig[b["sig"]].append((gb, b))
    used: set = set()
    out: dict = {}
    for g, i in info_a.items():
        cands = [(gb, b) for (gb, b) in bysig.get(i["sig"], []) if gb not in used]
        if not cands:
            continue
        gb, best = min(cands, key=lambda t: (t[1]["cx"] - i["cx"]) ** 2 + (t[1]["cy"] - i["cy"]) ** 2)
        used.add(gb)
        tf = _transform_between(i["off"], best["off"])
        dx, dy = best["cx"] - i["cx"], best["cy"] - i["cy"]
        f = fmap.get(tf)
        if f:
            fx, fy = f(i["cx"], i["cy"])
            key = (best["cx"] - fx, best["cy"] - fy)
        else:
            key = (dx, dy)
        out[g] = {"d": (dx, dy), "tf": tf, "key": key, "to": gb}
    return out, used


# ARC-AGI-3 action ids -> friendly labels (authoritative map mirrored from
# arc3_play_api.py) so the imported provenance edge reads "frame_0 + LEFT = frame_1".
ARC_ACTION_LABELS = {
    "ACTION1": "UP", "ACTION2": "DOWN", "ACTION3": "LEFT", "ACTION4": "RIGHT",
    "ACTION5": "SPACE", "ACTION6": "CLICK", "ACTION7": "UNDO",
}


def _read_incoming_action(png_path: str) -> str:
    """The ARC action that produced this frame, from the provenance sidecar that
    is imported alongside the image (``<frame>.provenance.json`` -> source
    .incomingAction). Returns "" when there is no sidecar/field."""
    try:
        p = Path(png_path)
        sidecar = p.with_name(p.stem + ".provenance.json")
        if not sidecar.is_file():
            return ""
        pj = json.loads(sidecar.read_text(encoding="utf-8"))
        return str((pj.get("source") or {}).get("incomingAction") or "")
    except (OSError, json.JSONDecodeError, ValueError):
        return ""


def extract_frame(png_path: str, char: str, partner_path: str | None = None,
                  carry: dict | None = None) -> dict:
    idx, hexpal, cols, rows = decode_grid(png_path)
    labels, info = label_regions(idx)
    for gid, i in info.items():
        i["hex"] = hexpal[i["color_id"]]
        i["off"] = _offsets(i["cells"])
        i["sig"] = _shape_sig(i["cells"], i["hex"])
    pairs = adjacency(labels)
    enclos = enclosures(info, pairs)
    pof, obj = _run_prolog(info, pairs, enclos, cols, rows)

    # common-fate grouping across the two frames: parts sharing the same rigid
    # motion (displacement + flip/rotation) are one object; unmatched parts are
    # appear/disappear events (e.g. a switch toggling).
    move_group: dict = {}
    motion: dict = {}
    disappeared: list = []   # A gids gone in B
    appeared: list = []      # (hex, cx, cy) new in B
    edge_action: str = ""    # ARC action on the outgoing edge (from partner's provenance)
    induce_ms: int | None = None  # wall time of the cross-frame induction (frame B)
    if partner_path:
        edge_action = _read_incoming_action(partner_path)
        _t_ind = time.monotonic()
        try:
            idx_b, pal_b, _cb, _rb = decode_grid(partner_path)
            _lb, info_b = label_regions(idx_b)
            for _g, b in info_b.items():
                b["hex"] = pal_b[b["color_id"]]
                b["off"] = _offsets(b["cells"])
                b["sig"] = _shape_sig(b["cells"], b["hex"])
            mres, used_b = _motion(info, info_b)
            for gid, mo in mres.items():
                dx, dy = mo["d"]
                tf = mo["tf"]
                kx, ky = mo["key"]
                motion[f"r{gid}"] = (dx, dy, tf)
                if (dx, dy) != (0, 0) or tf != "identity":
                    # group by the RIGID transform (shared across an object's
                    # parts even when they rotate/flip), not raw displacement.
                    move_group[f"r{gid}"] = f"move_{kx}_{ky}_{tf}"
            disappeared = [g for g in info if g not in mres]
            appeared = [(info_b[gb]["hex"], info_b[gb]["cx"], info_b[gb]["cy"])
                        for gb in info_b if gb not in used_b]
        except Exception:  # noqa: BLE001
            move_group, motion, disappeared, appeared = {}, {}, [], []
        induce_ms = int((time.monotonic() - _t_ind) * 1000)

    # every part gets a partOf group: its adjacency-cluster object, else (a
    # background/large blob) its own group -> full coverage like the LLM line.
    # Members are named part_<name_color> (e.g. part_limegreen_1); the internal
    # r<gid> ids are only used for the swipl facts and translated here.
    # draw big blobs first so nested / detail blobs render on top
    order = sorted(info.items(), key=lambda kv: -kv[1]["area"])
    mlines = [f"; symbolic (prolog) part-graph for {char}  ({len(info)} parts)",
              f"(character {char})"]
    # provenance edge imported with the image: this frame + ACTION = next frame.
    if partner_path and edge_action:
        this_stem = Path(png_path).stem
        partner_stem = Path(partner_path).stem
        edge_label = ARC_ACTION_LABELS.get(edge_action.upper(), edge_action)
        mlines.append(f"; provenance: {this_stem} + {edge_label} = {partner_stem}  ({edge_action})")
        mlines.append(f"(transition {char} {this_stem} {edge_label} {partner_stem})")
        if induce_ms is not None:
            mlines.append(f"; induce-ms {induce_ms}")
    geom = []
    partof_all: dict[str, str] = {}
    pid_of: dict[str, str] = {}
    raw_of: dict[str, str] = {}
    color_n: dict[str, int] = {}
    cur_pid_by_gid: dict[int, str] = {}
    # persistent per-color counter (carry) vs fresh per-frame (no carry).
    name_state = carry["name_state"] if carry is not None else color_n
    # carry identity forward: match THIS frame's regions back to the previous
    # frame's, so a matched part keeps its name/id across steps (like the LLM
    # line's consolidated names) instead of being renumbered every frame.
    back_map: dict[int, str] = {}
    if carry is not None and carry.get("prev_info"):
        try:
            bmres, _bu = _motion(carry["prev_info"], info)
            for pg, mo in bmres.items():
                cg = mo.get("to")
                if cg is not None and pg in carry["prev_pid"]:
                    back_map[cg] = carry["prev_pid"][pg]
        except Exception:  # noqa: BLE001
            back_map = {}
    # gap re-identification: a region that does NOT match the previous frame but
    # matches a recently-vanished identity (same D4 shape, nearest cell) reclaims
    # that id, so identity survives short occlusions (vanish -> return) and object
    # permanence can be resolved.
    reclaim: dict[int, str] = {}
    recent = carry.get("recent") if carry is not None else None
    if recent:
        used_recent: set = set()
        for gid, i in order:
            if gid in back_map:
                continue
            best_pid = None
            best_d = None
            for pid, r in recent.items():
                if pid in used_recent or r.get("sig") != i.get("sig"):
                    continue
                d = (r["cx"] - i["cx"]) ** 2 + (r["cy"] - i["cy"]) ** 2
                if best_d is None or d < best_d:
                    best_d = d
                    best_pid = pid
            if best_pid is not None:
                reclaim[gid] = best_pid
                used_recent.add(best_pid)
    for gid, i in order:
        rid = f"r{gid}"
        if gid in back_map:
            pid = back_map[gid]
            lbl = pid[5:] if pid.startswith("part_") else pid
        elif gid in reclaim:
            pid = reclaim[gid]
            lbl = pid[5:] if pid.startswith("part_") else pid
        else:
            cname = _color_name(i["hex"])
            name_state[cname] = name_state.get(cname, 0) + 1
            lbl = f"{cname}_{name_state[cname]}"
            pid = f"part_{lbl}"
        pid_of[rid] = pid
        cur_pid_by_gid[gid] = pid
        # common fate first: parts that moved by the same vector are one object;
        # else the adjacency cluster; else a singleton.
        raw_of[pid] = move_group.get(rid) or obj.get(rid) or f"g{gid}"
        mlines.append(f'(part {char} {pid} (label "{lbl}") (color {i["hex"]}))')
        _off = list(i.get("off") or [])
        # Two shrinkings run for EVERY shape (their output is small): a large thing
        # may collapse onto a small / named shape. Only the expensive per-cell reps
        # (16 orientations, directed turtle, start points) are capped to small
        # glyph-scale shapes; large regions keep their full-size outline turtle.
        _small = 0 < len(_off) <= _MAX_REP_CELLS
        _sq = _collapse_runs(_off) if _off else []
        _asp = _aspect_cells(_off) if _off else []
        _sq_small = 0 < len(_sq) <= _MAX_REP_CELLS
        _asp_small = 0 < len(_asp) <= _MAX_REP_CELLS
        _starts = sorted((tuple(c) for c in _off), key=lambda c: (c[1], c[0])) if _small else []
        _start = _starts[0] if _starts else None
        _order = _bfs_order(_off, _start) if _start else []
        _head = _dir_name(_order[0], _order[1]) if len(_order) >= 2 else "none"
        geom.append({"id": pid, "label": lbl, "color": i["hex"],
                     "partOf": "", "cx": i["cx"], "cy": i["cy"],
                     "sig": _shape_key(i.get("sig")),
                     "off": _off,
                     "sigSquared": _shape_key((None, _canon_key(_sq))) if _sq else "",
                     "sigAspect": _shape_key((None, _canon_key(_asp))) if _asp else "",
                     "sigDiag": _shape_key((None, _canon_key(_rot45(_off)))) if _small else "",
                     "squaredName": _name_of_cells(_sq) if _sq else "",
                     "aspectName": _name_of_cells(_asp) if _asp else "",
                     "startPoint": list(_start) if _start else None,
                     "startPoints": [list(s) for s in _starts],
                     "heading": _head,
                     "orientations": _orientations(_off) if _small else [],
                     "turtle": region_turtle(i["cells"], cols, rows, i["hex"]),
                     "turtleSquared": _poly_turtle(_sq, i["hex"]) if _sq_small else None,
                     "turtleAspect": _poly_turtle(_asp, i["hex"]) if _asp_small else None,
                     "turtleDirected": _poly_turtle(_order, i["hex"]) if _order else None})
    # unify every group id (adjacency clusters + singletons) to obj_N. With
    # carry, a group whose members were mostly carried forward reuses the
    # previous frame's obj id (stable object identity); otherwise a new
    # persistent obj id is minted.
    raw_order: list[str] = []
    for g in raw_of.values():
        if g not in raw_order:
            raw_order.append(g)
    if carry is not None:
        from collections import Counter
        prev_group = carry.get("prev_group") or {}
        members: dict[str, list[str]] = {}
        for pid, g in raw_of.items():
            members.setdefault(g, []).append(pid)
        used_obj: set = set()
        gstate = int(carry.get("group_state") or 0)
        gmap = {}
        for g in raw_order:
            votes = Counter(prev_group[pid] for pid in members.get(g, []) if pid in prev_group)
            chosen = None
            for oid, _c in votes.most_common():
                if oid not in used_obj:
                    chosen = oid
                    break
            if chosen is None:
                gstate += 1
                chosen = f"obj_{gstate}"
            used_obj.add(chosen)
            gmap[g] = chosen
        carry["group_state"] = gstate
    else:
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
    for rid, (dx, dy, tf) in motion.items():
        pid = pid_of.get(rid)
        if pid and ((dx, dy) != (0, 0) or tf != "identity"):
            mlines.append(f"(moved {char} {pid} {dx} {dy} {tf})")
    # In sequence mode the permanence of a vanished/appeared part cannot be known
    # from a single transition (occluded vs gone vs consumed vs transformed), so
    # extract_sequence resolves it across later frames. Only emit the raw
    # disappeared/appeared here for standalone (no-carry) calls.
    if carry is None:
        for g in disappeared:
            pid = pid_of.get(f"r{g}")
            if pid:
                mlines.append(f"(disappeared {char} {pid})")
        for hexc, cx, cy in appeared:
            mlines.append(f"(appeared {char} {_color_name(hexc)} {cx} {cy})")
    # spatial interaction: a mover whose DESTINATION lands on a vanished cell
    # likely caused it (interacted) -> disambiguates consumed_or_taken vs gone.
    interacted_pairs: list = []

    def _near(ax: int, ay: int, bx: int, by: int, tol: int = 2) -> bool:
        return abs(ax - bx) <= tol and abs(ay - by) <= tol
    for rid, (dx, dy, tf) in motion.items():
        mp = pid_of.get(rid)
        gid = int(rid[1:]) if rid[1:].isdigit() else None
        if not mp or gid not in info or ((dx, dy) == (0, 0) and tf == "identity"):
            continue
        destx, desty = info[gid]["cx"] + dx, info[gid]["cy"] + dy
        for g in disappeared:
            if _near(destx, desty, info[g]["cx"], info[g]["cy"]):
                dp = pid_of.get(f"r{g}")
                if dp:
                    mlines.append(f"(interacted {char} {mp} {dp})")
                    interacted_pairs.append((mp, dp))
    metta = "\n".join(mlines) + "\n"
    # thread identity forward + maintain the recent-vanished buffer for gaps.
    if carry is not None:
        rec = carry.get("recent") or {}
        for pid in set(reclaim.values()):
            rec.pop(pid, None)
        for pid in list(rec):
            rec[pid]["age"] = rec[pid].get("age", 0) + 1
            if rec[pid]["age"] > _ID_RETENTION:
                rec.pop(pid, None)
        carried = set(cur_pid_by_gid.values())
        for pgid, ppid in (carry.get("prev_pid") or {}).items():
            if ppid not in carried:
                pr = (carry.get("prev_info") or {}).get(pgid)
                if pr is not None:
                    rec[ppid] = {"sig": pr.get("sig"), "cx": pr.get("cx"), "cy": pr.get("cy"), "age": 1}
        carry["recent"] = rec
        carry["prev_info"] = info
        carry["prev_pid"] = cur_pid_by_gid
        carry["prev_group"] = partof_all
    return {"metta": metta, "geom": geom, "nparts": len(info),
            "nrels": len(pof) + len(obj), "cols": cols, "rows": rows,
            "ngroups": len(groups), "induceMs": induce_ms,
            "interacted": interacted_pairs}


# Object-permanence tuning. DEFAULT_OCCLUSION_HORIZON is how many following
# frames a vanished part may stay missing before it is committed to a verdict
# (occluded if it returns within the horizon, else gone/consumed). It is the
# baked backend default; the UI can preview other horizons live. _ID_RETENTION
# is how long an identity is kept for gap re-identification -- kept generously
# larger than the default so the live slider can look further than the bake.
DEFAULT_OCCLUSION_HORIZON = 4
_ID_RETENTION = 30
# Minimum confidence floor for evidence-based verdicts (gone / consumed_or_taken
# / new): even with no look-ahead left at a clip boundary, a verdict keeps a weak
# base-rate prior rather than reading a misleading exact 0.00.
_CONF_FLOOR = 0.1


def extract_sequence(frame_paths: list[str], char: str,
                     horizon: int = DEFAULT_OCCLUSION_HORIZON,
                     mem_db: str | None = None) -> list[dict]:
    """Run extract_frame over an ordered list of frames, threading part/object
    identity forward (stable ids, gap re-identified across occlusions), resolve
    object permanence across the whole sequence, and (when mem_db is given)
    recognize each distinct object against the persistent GLOBAL Prolog memory so
    objects recur across encounters keep one identity."""
    carry: dict = {"prev_info": None, "prev_pid": {}, "name_state": {},
                   "prev_group": {}, "group_state": 0, "recent": {}}
    out: list[dict] = []
    for k, fp in enumerate(frame_paths):
        partner = frame_paths[k + 1] if k + 1 < len(frame_paths) else None
        out.append(extract_frame(fp, char, partner, carry=carry))
    _classify_permanence(out, char, horizon)
    if mem_db:
        remember_objects(out, char, mem_db)
    return out


# Canonical polyomino shape library used to INITIALIZE the persistent global
# memory. The small free polyominoes are enumerated generatively (monomino ..
# hexomino); the well-known orders keep their letter names (Wikipedia:
# Tetromino, Pentomino, Polyomino), larger ones get generic order-indexed names.
_MONOMINO = {"monomino": [(0, 0)]}
_DOMINO = {"domino": [(0, 0), (1, 0)]}
_TROMINOES = {
    "tromino_I": [(0, 0), (1, 0), (2, 0)],
    "tromino_L": [(0, 0), (1, 0), (0, 1)],
}
_TETROMINOES = {
    "tetromino_I": [(0, 0), (1, 0), (2, 0), (3, 0)],
    "tetromino_O": [(0, 0), (1, 0), (0, 1), (1, 1)],
    "tetromino_T": [(0, 0), (1, 0), (2, 0), (1, 1)],
    "tetromino_S": [(1, 0), (2, 0), (0, 1), (1, 1)],
    "tetromino_L": [(0, 0), (0, 1), (0, 2), (1, 2)],
}
_PENTOMINOES = {
    "pentomino_F": [(1, 0), (2, 0), (0, 1), (1, 1), (1, 2)],
    "pentomino_I": [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)],
    "pentomino_L": [(0, 0), (0, 1), (0, 2), (0, 3), (1, 3)],
    "pentomino_N": [(1, 0), (1, 1), (0, 2), (1, 2), (0, 3)],
    "pentomino_P": [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2)],
    "pentomino_T": [(0, 0), (1, 0), (2, 0), (1, 1), (1, 2)],
    "pentomino_U": [(0, 0), (2, 0), (0, 1), (1, 1), (2, 1)],
    "pentomino_V": [(0, 0), (0, 1), (0, 2), (1, 2), (2, 2)],
    "pentomino_W": [(0, 0), (0, 1), (1, 1), (1, 2), (2, 2)],
    "pentomino_X": [(1, 0), (0, 1), (1, 1), (2, 1), (1, 2)],
    "pentomino_Y": [(1, 0), (0, 1), (1, 1), (1, 2), (1, 3)],
    "pentomino_Z": [(0, 0), (1, 0), (1, 1), (1, 2), (2, 2)],
}
_MAX_POLY_ORDER = 8  # seed monomino..octomino (1,1,2,5,12,35,108,369 = 533 free shapes)
_MAX_REP_CELLS = 64  # cap for per-object polyomino reps: small glyph-scale shapes only
_SEED_FACTS_CACHE: "list | None" = None
# key -> (composed_piece_names | None, box_cut_descriptor). Populated by
# _seed_shape_facts so remember_objects can emit compositional / box facts.
_SHAPE_DESCRIPTORS: "dict | None" = None


def _gen_free_polyominoes(max_n: int) -> dict:
    """Enumerate free polyominoes (unique up to translation + all 8 flips/
    rotations) for orders 1..max_n by growing from the monomino and canonicalizing
    with _canon_key. Returns {n: [canonical (x,y) cell tuple, ...]}."""
    out: dict[int, list] = {1: [_canon_key([(0, 0)])]}
    for n in range(2, max_n + 1):
        nxt: set = set()
        for ck in out[n - 1]:
            cells = set(ck)
            cand: set = set()
            for (x, y) in cells:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    q = (x + dx, y + dy)
                    if q not in cells:
                        cand.add(q)
            for q in cand:
                nxt.add(_canon_key(list(cells | {q})))
        out[n] = list(nxt)
    return out


def _poly_turtle(cells: list, hexc: str = "#7c9cff") -> dict:
    """A unit-cell turtle program for a polyomino, scaled into the 0..1000 box."""
    xs = [c[0] for c in cells]
    ys = [c[1] for c in cells]
    span = max(max(xs) + 1, max(ys) + 1)
    cs = 1000.0 / span
    cmds: list = [{"op": "move", "x": round((xs[0] + 0.5) * cs), "y": round((ys[0] + 0.5) * cs)}]
    for (x, y) in cells:
        cmds.append({"op": "rectangle",
                     "box": [round(x * cs), round(y * cs), round((x + 1) * cs), round((y + 1) * cs)],
                     "fill": hexc, "outline": hexc})
    return {"version": 1, "background": "transparent", "penColor": hexc, "penWidth": 4, "commands": cmds}


def _collapse_runs(offs) -> list:
    """Shrink a shape maximally by collapsing every maximal run of identical
    adjacent rows AND columns to a single line. Holes are preserved and shrink
    the same way (an interior empty run collapses just like a solid run): a solid
    W x H rectangle -> 1x1; a 5x5 ring with a 3x3 hole -> a 3x3 ring with a 1x1
    hole. Returns a list of unit (x, y) cells."""
    cells = set(map(tuple, offs))
    if not cells:
        return []
    w = max(x for x, _ in cells) + 1
    h = max(y for _, y in cells) + 1
    rows = [tuple((x, y) in cells for x in range(w)) for y in range(h)]
    keep_y = [y for y in range(h) if y == 0 or rows[y] != rows[y - 1]]
    grid = [rows[y] for y in keep_y]
    cols = [tuple(row[x] for row in grid) for x in range(w)]
    keep_x = [x for x in range(w) if x == 0 or cols[x] != cols[x - 1]]
    out = []
    for ny, y in enumerate(keep_y):
        for nx, x in enumerate(keep_x):
            if rows[y][x]:
                out.append((nx, ny))
    return out


def _aspect_cells(offs) -> list:
    """Aspect-minimal form: a SOLID rectangle keeps only which side is longer,
    shrunk so longer = shorter + 1 (landscape -> 2x1, portrait -> 1x2, square ->
    1x1); any shape with a hole or non-rectangular structure keeps its
    hole-preserving collapsed form (same as _collapse_runs)."""
    cells = set(map(tuple, offs))
    if not cells:
        return []
    w = max(x for x, _ in cells) + 1
    h = max(y for _, y in cells) + 1
    if len(cells) == w * h:  # solid rectangle
        if w > h:
            return [(0, 0), (1, 0)]
        if h > w:
            return [(0, 0), (0, 1)]
        return [(0, 0)]
    return _collapse_runs(offs)


_DIRS4 = (("N", 0, -1), ("W", -1, 0), ("E", 1, 0), ("S", 0, 1))


def _bfs_order(offs, start) -> list:
    """Deterministic traversal order of a shape's cells starting at `start`
    (breadth-first, neighbours visited N,W,E,S). Drawing cells in this order makes
    the turtle DIRECTED: a different start cell yields a different command order,
    hence a distinct directed turtle program."""
    cs = {tuple(c) for c in offs}
    start = tuple(start)
    order = [start]
    seen = {start}
    head = 0
    while head < len(order):
        x, y = order[head]
        head += 1
        for _nm, dx, dy in _DIRS4:
            q = (x + dx, y + dy)
            if q in cs and q not in seen:
                seen.add(q)
                order.append(q)
    for c in offs:  # append any cells unreachable by 4-adjacency (safety)
        if tuple(c) not in seen:
            order.append(tuple(c))
    return order


def _dir_name(a, b) -> str:
    """Compass heading (E/W/S/N) from cell a to adjacent cell b, else 'none'."""
    d = (b[0] - a[0], b[1] - a[1])
    return {(1, 0): "E", (-1, 0): "W", (0, 1): "S", (0, -1): "N"}.get(d, "none")


def _rot45(offs) -> list:
    """The shape rotated 45 degrees, kept on the integer grid via the rotate-45 +
    scale-sqrt(2) lattice map (x, y) -> (x - y, x + y). A grid -imino at 45 deg
    appears as diagonally-touching cells: a domino -> {(0,0),(1,1)} (corner pair),
    an L-tromino -> a diagonal chevron. Returns normalized unit (x, y) cells."""
    rot = [(x - y, x + y) for x, y in (tuple(c) for c in offs)]
    return sorted(_norm(rot))


def _orientations(offs) -> list:
    """The full set of 16 orientations of a shape: 8 rotational directions at
    45-degree steps (0/45/.../315) x {normal, flipped}. Rotations combine the 4
    axis-aligned D4 rotations with the rot45 lattice form; flip mirrors each.
    Returns [{deg, flip, cells}] sorted by (deg, flip); cells normalized unit
    (x, y). Symmetric shapes yield duplicate cell sets across slots (e.g. a
    monomino is identical in all 16) -- the slots are kept, identity still lives
    in the D4-invariant `sig`."""
    base = [tuple(c) for c in offs]
    diag = _rot45(base)
    fm = dict(_D4)
    rots = [
        (0, base), (90, [fm["rot90"](x, y) for x, y in base]),
        (180, [fm["rot180"](x, y) for x, y in base]), (270, [fm["rot270"](x, y) for x, y in base]),
        (45, diag), (135, [fm["rot90"](x, y) for x, y in diag]),
        (225, [fm["rot180"](x, y) for x, y in diag]), (315, [fm["rot270"](x, y) for x, y in diag]),
    ]
    out = []
    for deg, cells in rots:
        out.append({"deg": deg, "flip": False, "cells": [[x, y] for x, y in sorted(_norm(cells))]})
        flipped = [fm["flip_h"](x, y) for x, y in cells]
        out.append({"deg": deg, "flip": True, "cells": [[x, y] for x, y in sorted(_norm(flipped))]})
    out.sort(key=lambda d: (d["deg"], d["flip"]))
    return out


def _connected(cells) -> bool:
    """True if the set of (x, y) cells is edge-connected (4-neighbourhood)."""
    cells = set(cells)
    if not cells:
        return False
    seen: set = set()
    stack = [next(iter(cells))]
    while stack:
        x, y = stack.pop()
        if (x, y) in seen:
            continue
        seen.add((x, y))
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + dx, y + dy)
            if q in cells and q not in seen:
                stack.append(q)
    return len(seen) == len(cells)


def _decompose_named(ck, named: dict, name_size: dict, memo: dict):
    """Decompose a polyomino (canonical cell tuple `ck`) into NAMED sub-polyominoes
    (orders 1..5 are all named). Returns a sorted tuple of piece names, preferring
    the fewest pieces, then the largest smallest-piece, then lexicographic order.
    Every connected polyomino resolves (worst case: peel a monomino), so the
    result is never None. Memoized by canonical key (names are D4-invariant)."""
    if ck in named:
        return (named[ck],)
    if ck in memo:
        return memo[ck]
    cells = list(ck)
    n = len(cells)
    best = None
    best_key = None
    memo[ck] = None  # guard against re-entrancy on the same key
    for k in range(min(5, n - 1), 0, -1):
        if n - k > 5 and best is not None and len(best) <= 2:
            break  # a single named remainder is impossible here; 2 pieces already found
        for combo in itertools.combinations(cells, k):
            a = set(combo)
            b = set(cells) - a
            ka = _canon_key(a)
            if ka not in named or not _connected(a) or not _connected(b):
                continue
            sub = _decompose_named(_canon_key(b), named, name_size, memo)
            if sub is None:
                continue
            cand = tuple(sorted((named[ka],) + sub))
            sizes = [name_size[x] for x in cand]
            key = (len(cand), -min(sizes), cand)
            if best_key is None or key < best_key:
                best_key = key
                best = cand
    memo[ck] = best
    return best


def _box_cut_name(ck) -> str:
    """Universal fallback descriptor: the shape's bounding box (H x W) minus the
    cells that are cut out of it. A solid rectangle is `box_HxW`; otherwise
    `box_HxW_cut_N_at_rYcX_...` listing the removed cells in row-major order.
    Canonical (the D4-canonical orientation) so it is unique per free shape."""
    xs = [c[0] for c in ck]
    ys = [c[1] for c in ck]
    w = max(xs) + 1
    h = max(ys) + 1
    filled = set(ck)
    cuts = [(x, y) for y in range(h) for x in range(w) if (x, y) not in filled]
    if not cuts:
        return f"box_{h}x{w}"
    pos = "_".join(f"r{y}c{x}" for (x, y) in cuts)
    return f"box_{h}x{w}_cut_{len(cuts)}_at_{pos}"


_NAMED_LOOKUP: "dict | None" = None


def _named_lookup() -> dict:
    """Memoized {D4-canonical key: letter name} for the classically named small
    polyominoes (monomino .. pentomino)."""
    global _NAMED_LOOKUP
    if _NAMED_LOOKUP is None:
        _NAMED_LOOKUP = {}
        for nm, cells in {**_MONOMINO, **_DOMINO, **_TROMINOES,
                          **_TETROMINOES, **_PENTOMINOES}.items():
            _NAMED_LOOKUP[_canon_key(cells)] = nm
    return _NAMED_LOOKUP


def _name_of_cells(cells) -> str:
    """Name of a cell set: its letter name if it is a classic small polyomino,
    otherwise its universal box-cut descriptor. Used to see whether a shrunk large
    shape 'gets lucky' and collapses onto a named thing."""
    if not cells:
        return ""
    ck = _canon_key(cells)
    return _named_lookup().get(ck) or _box_cut_name(ck)


def _shape_recurred(sigs) -> bool:
    """True if a shape returns after changing away from it (A .. B .. A): a
    meaningful shape recurrence along a tracked instance's trajectory."""
    seen: set = set()
    prev = None
    for s in sigs:
        if s != prev and s in seen:
            return True
        seen.add(s)
        prev = s
    return False


_ORIENT_CACHE: dict = {}


def _distinct_orientations(ck):
    """A shape's distinct grid placements under the 8 D4 operations (rotations +
    reflections). Returns (count, {rep_transform_name: normalized_form}). Symmetry
    collapses the 8 operations onto fewer placements: a square -> 1, a domino or
    straight bar -> 2, a fully asymmetric polyomino -> 8. The representative for
    each placement is the first D4 transform (in _D4 order) that produces it."""
    ck = tuple(ck)
    if ck in _ORIENT_CACHE:
        return _ORIENT_CACHE[ck]
    reps: dict = {}
    for nm, f in _D4:
        form = tuple(sorted(_norm([f(x, y) for x, y in ck])))
        reps.setdefault(form, nm)
    res = (len(reps), {v: k for k, v in reps.items()})
    _ORIENT_CACHE[ck] = res
    return res


def _seed_shape_facts() -> list[str]:
    """Prolog shape/3 facts seeding the global memory with the free polyominoes
    (monomino..octomino) as named turtle programs (canonical key + name + turtle).
    Orders 1-5 keep their letter names; larger shapes get a unique, canonical
    `box_HxW[_cut_N_at_...]` descriptor as their name, plus a *composition* into
    smaller NAMED pieces (e.g. tetromino_O+tetromino_S) recorded as a relationship
    in _SHAPE_DESCRIPTORS. Memoized: the enumeration is computed once per process."""
    global _SEED_FACTS_CACHE, _SHAPE_DESCRIPTORS
    if _SEED_FACTS_CACHE is not None:
        return _SEED_FACTS_CACHE
    named: dict = {}
    name_size: dict = {}
    for nm, cells in {**_MONOMINO, **_DOMINO, **_TROMINOES, **_TETROMINOES, **_PENTOMINOES}.items():
        named[_canon_key(cells)] = nm
        name_size[nm] = len(cells)
    facts: list[str] = []
    descriptors: dict = {}
    seen: set = set()
    memo: dict = {}
    for n, shapes in _gen_free_polyominoes(_MAX_POLY_ORDER).items():
        for ck in sorted(shapes):
            key = _shape_key((None, ck))
            if key in seen:
                continue
            seen.add(key)
            composed = None
            box = _box_cut_name(ck)
            if ck in named:
                name = named[ck]
            else:
                # unique canonical name = the box-cut descriptor; the decomposition
                # into named pieces is recorded as a relationship, not the name.
                composed = _decompose_named(ck, named, name_size, memo)
                name = box
            descriptors[key] = (composed, box, ck)
            turtle = json.dumps(_poly_turtle(list(ck)), separators=(",", ":"))
            turtle = turtle.replace("\\", "\\\\").replace("'", "\\'")
            facts.append(f"shape('{key}', '{name}', '{turtle}').")
            # shape-vocabulary variants (just shapes, no identity): the two shrinks
            # and the 45-degree diagonal form map back to this -imino name, so a
            # rescaled / diagonally-placed object is recognized as the same shape.
            for kind, vcells in (("squared", _collapse_runs(ck)),
                                 ("aspect", _aspect_cells(ck)),
                                 ("diag45", _rot45(ck))):
                if not vcells:
                    continue
                vkey = _shape_key((None, _canon_key(vcells)))
                if vkey == key:
                    continue  # variant coincides with the full shape; nothing to add
                facts.append(f"variant('{vkey}', '{name}', '{kind}', '{key}').")
    _SEED_FACTS_CACHE = facts
    _SHAPE_DESCRIPTORS = descriptors
    return facts


def remember_objects(results: list[dict], char: str, mem_db: str) -> None:
    """Recognize every distinct object (shape signature + color) of this
    sequence against the persistent global Prolog memory (object_memory.pl),
    minting an identity the first time and bumping the encounter count on
    recognition. Annotates each part with globalId / memSeen / memNew and emits a
    `(memory ...)` fact per part into each frame's metta."""
    # distinct (sig, color) across the whole sequence = the objects of this
    # encounter; plus each tracked instance's move-to-move (x, y, shape) trajectory
    # (glyph-scale objects only), so placement is remembered and a later similar
    # shape can be recognized as a meaningful recurrence.
    distinct: dict[tuple[str, str], str] = {}
    traj: dict[str, list] = {}
    traj_gid: dict[str, str] = {}
    traj_last: dict[str, int] = {}
    for fi, r in enumerate(results):
        for p in r.get("geom", []):
            sg = p.get("sig")
            col = _cname(p.get("color", ""))
            if not sg:
                continue
            distinct[(sg, col)] = ""
            iid = p.get("id")
            if iid and 0 < len(p.get("off") or []) <= _MAX_REP_CELLS:
                traj.setdefault(iid, []).append((p.get("cx", 0), p.get("cy", 0), sg))
                traj_gid.setdefault(iid, f"gobj_{col}_{sg}")
                traj_last[iid] = fi
    if not distinct:
        return
    facts = [f"db('{Path(mem_db).as_posix()}').", f"when_stamp('{char}')."]
    facts.extend(_seed_shape_facts())
    for (sg, col) in distinct:
        facts.append(f"sig('{sg}', '{col}').")
    for iid, pts in traj.items():
        points = ";".join(f"{x},{y},{s}" for (x, y, s) in pts)
        facts.append(f"place('{char}', '{iid}', '{traj_gid[iid]}', '{points}', {len(pts)}).")
    Path(mem_db).parent.mkdir(parents=True, exist_ok=True)
    info: dict[tuple[str, str], tuple[str, int, bool, str]] = {}
    with tempfile.NamedTemporaryFile("w", suffix=".pl", delete=False, encoding="utf-8") as f:
        f.write("\n".join(facts) + "\n")
        fpath = f.name
    try:
        out = subprocess.run(
            ["swipl", "-q", "-g",
             f"consult('{MEM_PL.as_posix()}'), consult('{Path(fpath).as_posix()}'), run_memory",
             "-t", "halt"],
            capture_output=True, text=True, timeout=60).stdout
    except Exception:  # noqa: BLE001
        return
    finally:
        Path(fpath).unlink(missing_ok=True)
    for ln in out.splitlines():
        p = ln.split()
        if len(p) == 7 and p[0] == "mem":
            _mem, gid, key, col, seen, new, sname = p
            try:
                info[(key, col)] = (gid, int(seen), new == "t", sname)
            except ValueError:
                continue
    # per-instance placement summary, emitted into the frame where the instance is
    # last seen: how many moves it was tracked, how many distinct shapes it took
    # (morph), and whether a shape recurred (a meaningful A..B..A return).
    place_lines: dict[int, list[str]] = {}
    for iid, pts in traj.items():
        sigs = [s for (_x, _y, s) in pts]
        nshapes = len(set(sigs))
        fi = traj_last.get(iid, len(results) - 1)
        gid = traj_gid.get(iid, "")
        acc = place_lines.setdefault(fi, [])
        acc.append(f"(placement {char} {iid} {gid} (moves {len(pts)}) (shapes {nshapes}))")
        if nshapes > 1:
            acc.append(f"(morph {char} {iid} {nshapes})")
        if _shape_recurred(sigs):
            acc.append(f"(shape-recurs {char} {iid})")
    for fi, r in enumerate(results):
        lines: list[str] = []
        for p in r.get("geom", []):
            k = (p.get("sig"), _cname(p.get("color", "")))
            if k in info:
                gid, seen, new, sname = info[k]
                p["globalId"] = gid
                p["memSeen"] = seen
                p["memNew"] = new
                lines.append(f"(memory {char} {p['id']} {gid} (seen {seen}) (new {'t' if new else 'f'}))")
                if sname and sname != "-":
                    p["shapeName"] = sname
                    lines.append(f"(shape {char} {p['id']} {sname})")
                desc = (_SHAPE_DESCRIPTORS or {}).get(p.get("sig"))
                if desc:
                    composed, box, canon = desc
                    if composed:
                        p["composedOf"] = list(composed)
                        lines.append(f"(composed {char} {p['id']} " + " ".join(composed) + ")")
                    if box:
                        p["boxName"] = box
                        lines.append(f"(box {char} {p['id']} {box})")
                    off = p.get("off")
                    if canon and off and sname and sname != "-":
                        ori = _transform_between(list(canon), [tuple(o) for o in off])
                        if ori and ori != "deformed":
                            n_vis, _ = _distinct_orientations(canon)  # visually distinct
                            n_dir = len(_D4)  # 8 directional slots (turtle is directional)
                            p["orientation"] = ori
                            p["orientCount"] = n_dir
                            p["orientVisual"] = n_vis
                            lines.append(
                                f"(oriented {char} {p['id']} {sname} {ori} {n_dir} {n_vis})")
                    sp = p.get("startPoint")
                    if sp and sname and sname != "-":
                        nsp = len(p.get("startPoints") or [])
                        lines.append(
                            f"(start-point {char} {p['id']} {sp[0]} {sp[1]} "
                            f"{p.get('heading', 'none')} {nsp})")
        lines.extend(place_lines.get(fi, []))
        if lines:
            r["metta"] = r["metta"].rstrip("\n") + "\n" + "\n".join(lines) + "\n"


def _classify_permanence(results: list[dict], char: str,
                         horizon: int = DEFAULT_OCCLUSION_HORIZON) -> None:
    """Resolve each per-transition disappearance/appearance using the sequence
    (the truth is only knowable after processing later frames, up to `horizon`
    frames of patience; horizon <= 0 waits for the whole sequence):
      disappeared -> occluded (id returns within horizon) | transformed
                     (co-located new shape) | consumed_or_taken (mover on its
                     cell, never returns) | gone (unexplained, never returns)
      appeared    -> no-longer-occluded (id seen within horizon back) | transformed | new
    and appends the resolved facts to each frame's metta."""
    n = len(results)
    cells: list[dict] = []
    idsets: list[set] = []
    for r in results:
        m = {p["id"]: (p.get("cx", 0), p.get("cy", 0)) for p in r.get("geom", [])}
        cells.append(m)
        idsets.append(set(m.keys()))

    def after(pid: str, i: int) -> bool:
        hi = n if horizon <= 0 else min(n, i + 1 + horizon)
        return any(pid in idsets[j] for j in range(i + 1, hi))

    def before(pid: str, i: int) -> bool:
        lo = 0 if horizon <= 0 else max(0, i - horizon)
        return any(pid in idsets[j] for j in range(lo, i))

    for i in range(n - 1):
        disappeared = idsets[i] - idsets[i + 1]
        appeared = idsets[i + 1] - idsets[i]
        inter_targets = {t for (_m, t) in results[i].get("interacted", [])}
        # confidence = fraction of the horizon window we actually got to observe.
        # A "gone" is only as trustworthy as how many later frames we watched
        # without a return (forward); a "new" as how many prior frames we watched
        # without it existing (backward). Observed verdicts (occluded / back) = 1.
        rem_fwd = (n - 1) - (i + 1)
        req_fwd = horizon if horizon > 0 else rem_fwd
        conf_fwd = round(max(_CONF_FLOOR, min(req_fwd, rem_fwd) / req_fwd), 2) if req_fwd > 0 else _CONF_FLOOR
        rem_bwd = i + 1
        req_bwd = horizon if horizon > 0 else rem_bwd
        conf_bwd = round(max(_CONF_FLOOR, min(req_bwd, rem_bwd) / req_bwd), 2) if req_bwd > 0 else _CONF_FLOOR
        # transformed: pair a vanishing part (that never returns) with a co-located
        # appearing part (never seen before) -> same thing changed form.
        used_app: set = set()
        trans: list = []
        for x in disappeared:
            if after(x, i):
                continue
            xc = cells[i].get(x)
            best = None
            best_d = None
            for y in appeared:
                if y in used_app or before(y, i + 1):
                    continue
                yc = cells[i + 1].get(y)
                if xc and yc:
                    d = (xc[0] - yc[0]) ** 2 + (xc[1] - yc[1]) ** 2
                    if d <= 9 and (best_d is None or d < best_d):
                        best_d = d
                        best = y
            if best is not None:
                used_app.add(best)
                trans.append((x, best, best_d or 0))
        trans_from = {x for x, _y, _d in trans}
        lines: list[str] = []
        for x, y, d in trans:
            conf_t = round(max(0.5, 1.0 - (d ** 0.5) / 3.0), 2)
            lines.append(f"(transformed {char} {x} {y} {conf_t})")
        for x in disappeared:
            if x in trans_from:
                continue
            if after(x, i):
                lines.append(f"(occluded {char} {x} 1.0)")
            elif x in inter_targets:
                lines.append(f"(consumed_or_taken {char} {x} {conf_fwd})")
            else:
                lines.append(f"(gone {char} {x} {conf_fwd})")
        for y in appeared:
            if y in used_app:
                continue
            if before(y, i + 1):
                lines.append(f"(no-longer-occluded {char} {y} 1.0)")
            else:
                lines.append(f"(new {char} {y} {conf_bwd})")
        if lines:
            results[i]["metta"] = results[i]["metta"].rstrip("\n") + "\n" + "\n".join(lines) + "\n"


def _pid_color(pid: str) -> str:
    """Color name embedded in a part id: part_darkred_2 -> darkred."""
    import re as _re
    s = pid[5:] if pid.startswith("part_") else pid
    return _re.sub(r"_\d+$", "", s)


def induce_sequence_rules(metta_texts: list[str]) -> str:
    """Aggregate grounded interacted/revealed links across a whole frame
    sequence into candidate rules, ranked by how often they recur (support).
    Spurious one-off co-occurrences stay low-support; real mechanics rise."""
    from collections import Counter
    inter: Counter = Counter()
    reveal: Counter = Counter()
    for txt in metta_texts:
        for ln in txt.splitlines():
            p = ln.strip().rstrip(")").split()
            if len(p) >= 4 and p[0] == "(interacted":
                inter[(_pid_color(p[2]), _pid_color(p[3]))] += 1
            elif len(p) >= 4 and p[0] == "(revealed":
                tc = _color_name(p[3]) if p[3].startswith("#") else p[3]
                reveal[(_pid_color(p[2]), tc)] += 1
    lines = ["; induced sequence rules - grounded co-occurrences across the sequence",
             f"; {sum(inter.values())} interactions, {sum(reveal.values())} reveals"]
    for (mc, tc), n in inter.most_common():
        lines.append(f"(rule-candidate moved-onto {mc} {tc} disappears (support {n}))")
    for (mc, tc), n in reveal.most_common():
        lines.append(f"(rule-candidate moved-onto {mc} {tc} reveals (support {n}))")
    return "\n".join(lines) + "\n"


def _cname(color: str) -> str:
    """Normalize a color (hex or word) to a stable name."""
    return _color_name(color) if color.startswith("#") else color.lower()


def _turtle_centroid(t: dict):
    xs: list = []
    ys: list = []
    for c in (t or {}).get("commands", []):
        box = c.get("box")
        if isinstance(box, list) and len(box) == 4:
            xs += [box[0], box[2]]
            ys += [box[1], box[3]]
        for p in c.get("points", []) or []:
            if len(p) == 2:
                xs.append(p[0])
                ys.append(p[1])
        if "x" in c and "y" in c:
            xs.append(c["x"])
            ys.append(c["y"])
    if not xs:
        return None
    return (sum(xs) / len(xs), sum(ys) / len(ys))


def frames_from_parts(parts_lists: list) -> list:
    """Turn a sequence of parts.json lists (from EITHER the prolog or the LLM
    line) into per-frame [{color, cx, cy}] using each part's turtle centroid."""
    frames = []
    for parts in parts_lists:
        fr = []
        for p in parts or []:
            ce = _turtle_centroid(p.get("turtle") or {})
            if ce is None:
                continue
            fr.append({"color": p.get("color", ""), "cx": ce[0], "cy": ce[1]})
        frames.append(fr)
    return frames


def induce_from_frames(frames: list, move_min: int = 8, near: int = 60) -> str:
    """Source-agnostic rule induction over a sequence of per-frame parts
    (color + centroid, in 0..1000). Matches parts across consecutive frames by
    color + nearest centroid, finds movers whose destination lands on a
    vanished/newborn part, and aggregates those grounded links into
    support-ranked Prolog rule candidates. Works on prolog OR LLM parts."""
    from collections import Counter, defaultdict
    inter: Counter = Counter()
    reveal: Counter = Counter()
    for a, b in zip(frames, frames[1:]):
        byc: dict = defaultdict(list)
        for j, pb in enumerate(b):
            byc[pb["color"]].append(j)
        used: set = set()
        matched: dict = {}
        for i, pa in enumerate(a):
            cands = [j for j in byc.get(pa["color"], []) if j not in used]
            if not cands:
                continue
            j = min(cands, key=lambda j: (b[j]["cx"] - pa["cx"]) ** 2 + (b[j]["cy"] - pa["cy"]) ** 2)
            used.add(j)
            matched[i] = j
        disappeared = [i for i in range(len(a)) if i not in matched]
        appeared = [j for j in range(len(b)) if j not in used]
        for i, j in matched.items():
            dx, dy = b[j]["cx"] - a[i]["cx"], b[j]["cy"] - a[i]["cy"]
            if abs(dx) < move_min and abs(dy) < move_min:
                continue
            dxp, dyp = b[j]["cx"], b[j]["cy"]
            for di in disappeared:
                if abs(dxp - a[di]["cx"]) <= near and abs(dyp - a[di]["cy"]) <= near:
                    inter[(_cname(a[i]["color"]), _cname(a[di]["color"]))] += 1
            for aj in appeared:
                if abs(dxp - b[aj]["cx"]) <= near and abs(dyp - b[aj]["cy"]) <= near:
                    reveal[(_cname(a[i]["color"]), _cname(b[aj]["color"]))] += 1
    lines = ["; induced sequence rules - grounded co-occurrences across the sequence",
             f"; {sum(inter.values())} interactions, {sum(reveal.values())} reveals"]
    for (mc, tc), n in inter.most_common():
        lines.append(f"(rule-candidate moved-onto {mc} {tc} disappears (support {n}))")
    for (mc, tc), n in reveal.most_common():
        lines.append(f"(rule-candidate moved-onto {mc} {tc} reveals (support {n}))")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    import sys
    r = extract_frame(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "frame")
    print(f"parts={r['nparts']} groups={r['ngroups']} rels={r['nrels']} grid={r['cols']}x{r['rows']}")
    print(r["metta"][:600])
