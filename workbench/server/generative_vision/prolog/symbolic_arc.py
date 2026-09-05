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
        out[g] = {"d": (dx, dy), "tf": tf, "key": key}
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


def extract_frame(png_path: str, char: str, partner_path: str | None = None) -> dict:
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
    if partner_path:
        edge_action = _read_incoming_action(partner_path)
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
    for rid, (dx, dy, tf) in motion.items():
        pid = pid_of.get(rid)
        if pid and ((dx, dy) != (0, 0) or tf != "identity"):
            mlines.append(f"(moved {char} {pid} {dx} {dy} {tf})")
    for g in disappeared:
        pid = pid_of.get(f"r{g}")
        if pid:
            mlines.append(f"(disappeared {char} {pid})")
    for hexc, cx, cy in appeared:
        mlines.append(f"(appeared {char} {hexc} {cx} {cy})")
    # spatial event links: a mover whose DESTINATION lands on a vanished cell
    # likely caused it (interacted); on a newborn cell -> revealed it. This
    # grounds induction so temporally-coincident but far-apart events (e.g. a
    # rotation across the map) are not spuriously linked.
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
        for hexc, ax, ay in appeared:
            if _near(destx, desty, ax, ay):
                mlines.append(f"(revealed {char} {mp} {hexc} {ax} {ay})")
    metta = "\n".join(mlines) + "\n"
    return {"metta": metta, "geom": geom, "nparts": len(info),
            "nrels": len(pof) + len(obj), "cols": cols, "rows": rows,
            "ngroups": len(groups)}


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
