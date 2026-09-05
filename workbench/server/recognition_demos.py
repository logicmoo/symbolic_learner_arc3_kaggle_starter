"""recognition_demos.py -- runnable, visual demonstrations of the symbolic_arc
Phase-2 acceptance behaviours (SOW Exhibit A Phase 2), for the workbench
"Recognition Demos" page. Each demo runs the REAL recognizer functions and
returns grid panels (cells with a role: visible / hidden / filled / object /
regen) plus a result and a pass/fail, so the page can render and re-run them.

Memory demos use a throwaway temp store so they are isolated and never touch the
canonical registry.
"""
from __future__ import annotations

import sys
import tempfile
import threading
from datetime import datetime, timezone
from pathlib import Path

_PROLOG_DIR = Path(__file__).resolve().parent / "generative_vision" / "prolog"
if str(_PROLOG_DIR) not in sys.path:
    sys.path.insert(0, str(_PROLOG_DIR))

_BLUE = "#7c9cff"
_RED = "#e0483f"
_GREEN = "#8bd450"


def _panel(label, roled, ox=None, oy=None, w=None, h=None):
    """A grid panel from (x, y, role[, color]) cells, translated to a shared origin.
    role in {visible, hidden, filled, object, regen, background}."""
    cells = [(int(c[0]), int(c[1]), c[2], (c[3] if len(c) > 3 else None)) for c in roled]
    xs = [c[0] for c in cells] or [0]
    ys = [c[1] for c in cells] or [0]
    ox = min(xs) if ox is None else ox
    oy = min(ys) if oy is None else oy
    w = (max(xs) - ox + 1) if w is None else w
    h = (max(ys) - oy + 1) if h is None else h
    return {"label": label, "w": int(w), "h": int(h),
            "cells": [{"x": x - ox, "y": y - oy, "role": r, "color": col} for (x, y, r, col) in cells]}


def _bbox(*cellsets):
    pts = [p for cs in cellsets for p in cs]
    xs = [p[0] for p in pts] or [0]
    ys = [p[1] for p in pts] or [0]
    return min(xs), min(ys), max(xs) - min(xs) + 1, max(ys) - min(ys) + 1


# --- occlusion completion ---------------------------------------------------

def _occlusion_demo(did, title, full, hidden, candidate):
    import symbolic_arc as sa
    full_s = {tuple(c) for c in full}
    hid_s = {tuple(c) for c in hidden}
    frag = sorted(full_s - hid_s)
    cand = {tuple(sa._canon_key(candidate)): sa._name_of_cells(candidate)} if candidate else None
    r = sa.complete_occluded(frag, sorted(hid_s), candidates=cand)
    ox, oy, w, h = _bbox(full_s, hid_s)
    before = _panel("occluded view", [(x, y, "visible", _BLUE) for (x, y) in frag]
                    + [(x, y, "hidden", None) for (x, y) in hid_s], ox, oy, w, h)
    frames = [before]
    if r:
        # Animate the real completion: reveal each filled cell one at a time, in
        # the order the recognizer returned them, until the object is whole.
        filled = [tuple(c) for c in r["filled"]]
        shown: list = []
        for i, cell in enumerate(filled):
            shown.append(cell)
            rest = [c for c in hid_s if c not in set(shown)]
            frames.append(_panel(f"completing {i + 1}/{len(filled)}",
                                 [(x, y, "visible", _BLUE) for (x, y) in r["visible"]]
                                 + [(x, y, "filled", _GREEN) for (x, y) in shown]
                                 + [(x, y, "hidden", None) for (x, y) in rest], ox, oy, w, h))
        after = _panel(f"completed → {r['name']}",
                       [(x, y, "visible", _BLUE) for (x, y) in r["visible"]]
                       + [(x, y, "filled", _GREEN) for (x, y) in r["filled"]], ox, oy, w, h)
        frames.append(after)
        faithful = {tuple(c) for c in r["cells"]} == {tuple(c) for c in sa._norm(list(full_s))}
        result = {"recognized": r["name"], "scale": r["scale"], "orientation": r["orientation"],
                  "residual": r["residual"], "confidence": r["confidence"], "faithful": faithful}
        passed = bool(faithful and r["residual"] == len(hid_s & full_s))
        panels = [before, after]
    else:
        result = {"recognized": None, "note": "no consistent completion -> re-categorize as new"}
        passed = candidate is None or not (hid_s & full_s)  # reject-case demo expects None
        panels = [before]
    return {"id": did, "group": "Occlusion completion", "title": title, "panels": panels,
            "frames": frames, "result": result, "passed": passed,
            "description": "Hypothesize the held form from the visible fragment, run it forward to "
                           "fill the hidden cells, accept only when every filled cell lies under the occluder."}


def _demo_occlusion_reject():
    import symbolic_arc as sa
    T = [(0, 0), (1, 0), (2, 0), (1, 1)]
    frag = [(0, 0), (1, 0), (2, 0)]
    r = sa.complete_occluded(frag, [(9, 9)], candidates={tuple(sa._canon_key(T)): "tetromino_T"})
    ox, oy, w, h = _bbox(set(map(tuple, frag)), {(9, 9)})
    before = _panel("occluded view (occluder elsewhere)",
                    [(x, y, "visible", _BLUE) for (x, y) in frag] + [(9, 9, "hidden", None)], ox, oy, w, h)
    return {"id": "occlusion-reject", "group": "Occlusion completion",
            "title": "Inconsistent fragment is rejected", "panels": [before],
            "result": {"recognized": r["name"] if r else None,
                       "note": "rejected (no lock) -> re-categorized as new"},
            "passed": r is None,
            "description": "The cell the form needs is not under the occluder, so no completion is accepted."}


# --- identity (recolor / resize) --------------------------------------------

def _frame_col(color, off, cx=5, cy=5):
    import symbolic_arc as sa
    sig = sa._shape_key((None, sa._canon_br([tuple(c) for c in off])))
    return {"metta": "", "geom": [{"id": "p", "sig": sig, "color": color,
                                   "off": [list(c) for c in off], "cx": cx, "cy": cy}]}


def _demo_recolor():
    import symbolic_arc as sa
    mem = tempfile.mkdtemp()
    L = [(0, 0), (0, 1), (0, 2), (1, 2)]
    sa.remember_objects([_frame_col(_RED, L)], "demo-1", mem, write=True)
    b = _frame_col(_BLUE, L)
    sa.remember_objects([b], "demo-2", mem, write=True)
    ids = sa.registry_snapshot(mem)["scopes"]["demo"]["identities"]
    ox, oy, w, h = _bbox(set(map(tuple, L)))
    panels = [_panel("encounter 1 (red)", [(x, y, "object", _RED) for (x, y) in L], ox, oy, w, h),
              _panel("encounter 2 (blue)", [(x, y, "object", _BLUE) for (x, y) in L], ox, oy, w, h)]
    passed = len(ids) == 1 and ids[0]["seen"] == 2 and b["geom"][0]["memNew"] is False
    return {"id": "recolor", "group": "Identity (recolor / resize)",
            "title": "Recolour is the same object", "panels": panels,
            "result": {"object": ids[0]["name"] if ids else None, "seen": ids[0]["seen"] if ids else 0,
                       "colours": [v["color"] for v in ids[0]["variations"]] if ids else [],
                       "recognized_not_new": bool(ids) and b["geom"][0]["memNew"] is False,
                       "identities": len(ids)},
            "passed": passed,
            "description": "Colour is an occurrence attribute; a recoloured shape recognizes as the same object."}


def _demo_resize():
    import symbolic_arc as sa
    mem = tempfile.mkdtemp()
    base = [(0, 0), (1, 0)]
    big = [(0, 0), (1, 0), (2, 0), (3, 0), (0, 1), (1, 1), (2, 1), (3, 1)]
    sa.remember_objects([_frame_col(_RED, base)], "demo-1", mem, write=True)
    b = _frame_col(_RED, big)
    sa.remember_objects([b], "demo-2", mem, write=True)
    ids = sa.registry_snapshot(mem)["scopes"]["demo"]["identities"]
    panels = [_panel("small (domino)", [(x, y, "object", _RED) for (x, y) in base]),
              _panel("2x-scaled", [(x, y, "object", _RED) for (x, y) in big])]
    passed = len(ids) == 1 and ids[0]["seen"] == 2 and {v["size"] for v in ids[0]["variations"]} == {2, 8}
    return {"id": "resize", "group": "Identity (recolor / resize)",
            "title": "Resize is the same object", "panels": panels,
            "result": {"object": ids[0]["name"] if ids else None, "seen": ids[0]["seen"] if ids else 0,
                       "sizes": sorted({v["size"] for v in ids[0]["variations"]}) if ids else [],
                       "identities": len(ids)},
            "passed": passed,
            "description": "Size is an occurrence attribute; a 2x-scaled shape recognizes as the same object."}


# --- recognition (store -> recognize / new distinguished) --------------------

def _demo_store_then_recognize():
    import symbolic_arc as sa
    mem = tempfile.mkdtemp()
    L = [(0, 0), (0, 1), (0, 2), (1, 2)]
    sa.remember_objects([_frame_col(_RED, L)], "demo-1", mem, write=True)
    reflected = [(1 - x, y) for (x, y) in L]
    later = _frame_col(_GREEN, reflected, cx=30)
    sa.remember_objects([later], "demo-2", mem, write=True)
    p = later["geom"][0]
    ids = sa.registry_snapshot(mem)["scopes"]["demo"]["identities"]
    panels = [_panel("stored (encounter 1)", [(x, y, "object", _RED) for (x, y) in L]),
              _panel("later: moved+reflected+recoloured", [(x, y, "object", _GREEN) for (x, y) in sa._norm(reflected)])]
    passed = p["memNew"] is False and p["memSeen"] == 2 and len(ids) == 1
    return {"id": "store-then-recognize", "group": "Recognition",
            "title": "Store, then recognize the same object later", "panels": panels,
            "result": {"recognized_not_new": p["memNew"] is False, "seen": p["memSeen"],
                       "identities": len(ids)},
            "passed": passed,
            "description": "A later encounter (moved, reflected, recoloured) recognizes as the same object; "
                           "evidence accrues and no duplicate is stored."}


def _demo_new_distinguished():
    import symbolic_arc as sa
    mem = tempfile.mkdtemp()
    L = [(0, 0), (0, 1), (0, 2), (1, 2)]
    T = [(0, 0), (1, 0), (2, 0), (1, 1)]
    sa.remember_objects([_frame_col(_RED, L)], "demo-1", mem, write=True)
    fr = _frame_col(_RED, T)
    sa.remember_objects([fr], "demo-2", mem, write=True)
    ids = sa.registry_snapshot(mem)["scopes"]["demo"]["identities"]
    panels = [_panel("held object", [(x, y, "object", _RED) for (x, y) in L]),
              _panel("new structure", [(x, y, "object", _GREEN) for (x, y) in sa._norm(T)])]
    passed = fr["geom"][0]["memNew"] is True and len(ids) == 2
    return {"id": "new-distinguished", "group": "Recognition",
            "title": "A genuinely new structure is distinguished", "panels": panels,
            "result": {"is_new": fr["geom"][0]["memNew"], "identities": len(ids)},
            "passed": passed,
            "description": "A different shape is committed as a new object, not merged into the held one."}


# --- regeneration -----------------------------------------------------------

def _demo_regeneration():
    import symbolic_arc as sa
    snap = sa.registry_snapshot(tempfile.mkdtemp(), include_turtles=True)
    shp = next((s for s in snap["shapes"] if s["name"] == "pentomino_V"), None) or snap["shapes"][0]
    want = {(int(x), int(y)) for x, y in shp["cells"]}
    rects = [c for c in shp["turtle"]["commands"] if c.get("op") == "rectangle"]
    cs = min(b["box"][2] - b["box"][0] for b in rects)
    got = {(round(b["box"][0] / cs), round(b["box"][1] / cs)) for b in rects}

    def _n(cs_):
        mx = min(x for x, _ in cs_); my = min(y for _, y in cs_)
        return {(x - mx, y - my) for x, y in cs_}
    faithful = _n(got) == _n(want)
    # Animate the turtle replaying its program: reveal one rectangle (cell) per
    # frame in the real command order, so the shape is drawn stroke by stroke.
    ow = max(x for x, _ in got) - min(x for x, _ in got) + 1
    oh = max(y for _, y in got) - min(y for _, y in got) + 1
    oxg = min(x for x, _ in got); oyg = min(y for _, y in got)
    seq = [(round(b["box"][0] / cs), round(b["box"][1] / cs)) for b in rects]
    frames = []
    drawn: list = []
    for i, cell in enumerate(seq):
        drawn.append(cell)
        frames.append(_panel(f"drawing {i + 1}/{len(seq)}",
                             [(x, y, "regen", _GREEN) for (x, y) in drawn], oxg, oyg, ow, oh))
    panels = [_panel("stored shape", [(x, y, "object", _BLUE) for (x, y) in want]),
              _panel("regenerated from turtle", [(x, y, "regen", _GREEN) for (x, y) in got])]
    return {"id": "regeneration", "group": "Regeneration",
            "title": f"Regenerate {shp['name']} from its stored form", "panels": panels,
            "frames": frames or panels,
            "result": {"shape": shp["name"], "faithful": faithful},
            "passed": faithful,
            "description": "The stored turtle program replays to the exact normalized cells (faithful on grids)."}


# --- replay / determinism ---------------------------------------------------

def _demo_replay():
    import symbolic_arc as sa
    L = [(0, 0), (0, 1), (0, 2), (1, 2)]
    a = _frame_col(_RED, L)
    b = _frame_col(_RED, L)
    sa.remember_objects([a], "demo", tempfile.mkdtemp(), write=True)
    sa.remember_objects([b], "demo", tempfile.mkdtemp(), write=True)
    same_id = a["geom"][0]["globalId"] == b["geom"][0]["globalId"]
    same_form = a["metta"] == b["metta"]
    panels = [_panel("run A", [(x, y, "object", _RED) for (x, y) in L]),
              _panel("run B", [(x, y, "object", _RED) for (x, y) in L])]
    return {"id": "replay", "group": "Replay / determinism",
            "title": "Same input -> same identity + canonical form", "panels": panels,
            "result": {"same_identity": same_id, "same_form": same_form,
                       "handle": a["geom"][0]["globalId"]},
            "passed": bool(same_id and same_form),
            "description": "Identity rests on the normalized form, so a replay yields the same handle and metta."}


# --- input breadth (grid / raster / video) ----------------------------------

def _grid_to_cells(idx, hexpal):
    out = []
    for y in range(idx.shape[0]):
        for x in range(idx.shape[1]):
            out.append((x, y, "object", hexpal[int(idx[y, x])]))
    return out


def _demo_input_gradient():
    import numpy as np
    import symbolic_arc as sa
    from PIL import Image
    y, x = np.mgrid[0:128, 0:128]
    gr = np.stack([x * 2 % 256, y * 2 % 256, (x + y) % 256], axis=-1).astype(np.uint8)
    p = Path(tempfile.mkdtemp()) / "g.png"
    Image.fromarray(gr).save(p)
    idx, hexpal, cols, rows = sa.decode_grid(str(p))
    panels = [_panel("decoded grid (quantized + downscaled)", _grid_to_cells(idx, hexpal))]
    passed = max(cols, rows) <= 64 and 1 < len(hexpal) <= 16
    return {"id": "input-gradient", "group": "Input breadth",
            "title": "Raster gradient -> small flat grid", "panels": panels,
            "result": {"cols": cols, "rows": rows, "colours": len(hexpal)},
            "passed": passed,
            "description": "A smooth-gradient raster (thousands of colours) is median-cut quantized and "
                           "downscaled into the flat grid the recognizer expects."}


def _demo_input_video():
    import numpy as np
    import symbolic_arc as sa
    from PIL import Image
    d = Path(tempfile.mkdtemp())
    frames = []
    for i in range(4):
        g = np.full((48, 96, 3), 12, np.uint8)
        g[16:32, 8 + i * 16:24 + i * 16] = (220, 30, 30)
        fp = d / f"v{i}.png"
        Image.fromarray(g).save(fp)
        frames.append(str(fp))
    mem = str(d / "mem")
    seq = sa.extract_sequence(frames, "clip", mem_dir=mem, write=True)
    block_color = sa._cname("#dc1e1e")
    ids = sa.registry_snapshot(mem)["scopes"].get("clip", {}).get("identities", [])
    block = [o for o in ids if any(v["color"] == block_color for v in o.get("variations", []))]
    panels = []
    for i, fr in enumerate(frames):
        idx, hexpal, _c, _r = sa.decode_grid(fr)
        panels.append(_panel(f"frame {i+1}", _grid_to_cells(idx, hexpal)))
    passed = len(seq) == 4 and len(block) == 1 and block[0]["seen"] == 1
    return {"id": "input-video", "group": "Input breadth",
            "title": "Simple video: a block tracked as one object", "panels": panels,
            "result": {"frames": len(seq), "block_object": block[0]["name"] if block else None,
                       "block_identities": len(block)},
            "passed": passed,
            "description": "A block moving across 4 frames is extracted every frame and tracked as ONE "
                           "committed object, not re-minted per frame."}


_LS20_DIR = (Path(__file__).resolve().parents[1] / "workspaces" / "arc3_random_player" / "data"
             / "vision_frames" / "arc_recordings" / "data-arc3_games-recordings-ls20-saved_001")


def _demo_live_ls20_sequence():
    """A (real data): play the actual recorded ls20 frames over time, starting from
    an EMPTY memory and learning as it goes — frame 0 recognizes nothing; each
    later frame recognizes the objects (by their colour-free, scale-normalized
    identity) it has already seen earlier in the sequence, so you watch recognition
    build up over time. Object cells are drawn from each frame's real part-graph:
    NEW objects (first sighting) render blue, RECOGNIZED objects render green."""
    import json as _json
    import symbolic_arc as sa
    setdir = _LS20_DIR
    if not setdir.is_dir():
        return {"id": "live-ls20", "group": "Live sequence (real data)",
                "title": "Live ls20 recording — recognition over time", "panels": [],
                "frames": [], "result": {"note": "ls20 recording set not found"}, "passed": False,
                "description": "Plays the real recorded ls20 frames with live recognition; run a reduce first."}
    mf_path = setdir / "manifest.json"
    order = []
    if mf_path.is_file():
        try:
            order = [it["id"] for it in _json.loads(mf_path.read_text(encoding="utf-8")).get("items", [])]
        except (OSError, _json.JSONDecodeError):
            order = []
    if not order:
        order = sorted(p.stem for p in setdir.glob("*.png"))
    sym = setdir / "sym"
    frames = []
    geo_seen: dict = {}            # GEOMETRY shape -> set of identities using it (evidence/learners)
    ind_seen: set = set()          # INDIVIDUALS: (shape, colour) objects learned
    total_ind_recog = 0
    first_ind_recog = first_geo_recog = None
    for idv in order[:28]:
        png = next(iter(setdir.glob(f"{idv}.png")), None)
        if not png:
            continue
        idx, hexpal, _c, _r = sa.decode_grid(str(png))
        geo_new = geo_recog = ind_new = ind_recog = 0
        roled: list = []
        frame_geo: dict = {}       # shape -> identities using it in this frame (evidence)
        frame_ind: set = set()
        pj = sym / f"{idv}__prolog.parts.json"
        parts = []
        if pj.is_file():
            try:
                parts = _json.loads(pj.read_text(encoding="utf-8"))
            except (OSError, _json.JSONDecodeError):
                parts = []
        for p in parts:
            off = p.get("off") or []
            if not off:
                continue
            geo = sa._identity_name(off) or ("shape_" + str(p.get("sig")))   # geometry
            ind = (geo, sa._cname(p.get("color", "")))                        # individual
            geo_known = geo in geo_seen        # recognized only if seen in a PRIOR frame
            ind_known = ind in ind_seen
            geo_recog += geo_known; geo_new += (not geo_known)
            ind_recog += ind_known; ind_new += (not ind_known)
            frame_geo.setdefault(geo, set()).add(ind); frame_ind.add(ind)
            # overlay coloured by INDIVIDUAL recognition: green recognized, blue new
            cx, cy = p.get("cx", 0), p.get("cy", 0)
            oxs = [c[0] for c in off]; oys = [c[1] for c in off]
            bx = int(round(cx - (max(oxs) + min(oxs)) / 2.0))
            by = int(round(cy - (max(oys) + min(oys)) / 2.0))
            role, col = ("regen", _GREEN) if ind_known else ("visible", _BLUE)
            for (dx, dy) in off:
                roled.append((bx + dx, by + dy, role, col))
        for g, inds in frame_geo.items():     # learn AFTER scoring: accrue evidence per shape
            geo_seen.setdefault(g, set()).update(inds)
        ind_seen |= frame_ind
        if first_ind_recog is None:
            first_ind_recog, first_geo_recog = ind_recog, geo_recog
        total_ind_recog += ind_recog
        ev = [len(v) for v in geo_seen.values()]
        max_ev = max(ev) if ev else 0
        base = [(x, y, "object", hexpal[int(idx[y, x])]) for y in range(idx.shape[0]) for x in range(idx.shape[1])]
        frames.append(_panel(
            f"{idv} · objects {ind_recog} rec / {ind_new} new · shapes {geo_recog} rec / {geo_new} new "
            f"· learned {len(ind_seen)} obj, {len(geo_seen)} shapes (up to {max_ev} identities/shape)",
            base + roled))

    # --- one frame of LEVEL 2 (same game): cross-level transfer. The geometry
    # (and many individuals) learned in level 1 are recognized immediately, so
    # the level-2 frame arrives mostly green rather than all-new. It has no
    # committed part-graph, so extract it fresh on the fly.
    lvl2_geo = lvl2_ind = lvl2_total = 0
    lvl2dir = _LS20_DIR.parent / "data-arc3_games-recordings-ls20-saved_002"
    if lvl2dir.is_dir():
        l2png = next(iter(sorted(lvl2dir.glob("*.png"))), None)
        if l2png is not None:
            try:
                pr = sa.extract_frame(str(l2png), "ls20-saved_002")
            except Exception:  # noqa: BLE001
                pr = None
            if pr and pr.get("nparts", 0) > 0 and pr["cols"] <= 160 and pr["rows"] <= 160:
                idx2, hexpal2, _c2, _r2 = sa.decode_grid(str(l2png))
                roled2: list = []
                for p in pr.get("geom", []):
                    off = p.get("off") or []
                    if not off:
                        continue
                    geo = sa._identity_name(off) or ("shape_" + str(p.get("sig")))
                    ind = (geo, sa._cname(p.get("color", "")))
                    geo_known = geo in geo_seen
                    ind_known = ind in ind_seen
                    lvl2_total += 1
                    lvl2_geo += geo_known
                    lvl2_ind += ind_known
                    cx, cy = p.get("cx", 0), p.get("cy", 0)
                    oxs = [c[0] for c in off]; oys = [c[1] for c in off]
                    bx = int(round(cx - (max(oxs) + min(oxs)) / 2.0))
                    by = int(round(cy - (max(oys) + min(oys)) / 2.0))
                    role, col = ("regen", _GREEN) if ind_known else ("visible", _BLUE)
                    for (dx, dy) in off:
                        roled2.append((bx + dx, by + dy, role, col))
                base2 = [(x, y, "object", hexpal2[int(idx2[y, x])])
                         for y in range(idx2.shape[0]) for x in range(idx2.shape[1])]
                frames.append(_panel(
                    f"LEVEL 2 (saved_002) frame 1 · objects {lvl2_ind}/{lvl2_total} recognized "
                    f"· shapes {lvl2_geo}/{lvl2_total} — carried over from level 1", base2 + roled2))

    # demonstrates learning: the first frame recognizes nothing (empty memory),
    # geometry (fewer, shared) saturates faster than individuals (colour variety),
    # and the level-2 frame is mostly recognized on arrival (cross-level transfer).
    # per-shape learner evidence: how many distinct identities instantiate each shape
    ev = sorted(((len(v), g) for g, v in geo_seen.items()), reverse=True)
    top_shape = (f"{ev[0][1]} ({ev[0][0]} identities)" if ev else "none")
    passed = bool(frames) and first_ind_recog == 0 and total_ind_recog > 0
    return {"id": "live-ls20", "group": "Live sequence (real data)",
            "title": "Live ls20 recording — recognition builds up, transfers to level 2", "panels": frames[:1],
            "frames": frames,
            "result": {"frames": len(frames), "frame0_objects_recognized": first_ind_recog,
                       "frame0_shapes_recognized": first_geo_recog,
                       "objects_learned": len(ind_seen), "shapes_learned": len(geo_seen),
                       "max_identities_per_shape": (ev[0][0] if ev else 0),
                       "most_learned_shape": top_shape,
                       "level2_objects_recognized": f"{lvl2_ind}/{lvl2_total}",
                       "level2_shapes_recognized": f"{lvl2_geo}/{lvl2_total}"},
            "passed": passed,
            "description": "The real recorded ls20 frames played from an EMPTY memory. Two things are learned "
                           "separately: GEOMETRY (colour-free shape vocabulary, shared) and INDIVIDUALS "
                           "(shape+colour, per game). Each shape accrues evidence = the identities that use it, "
                           "so a well-learned shape has many identity learners. Frame 0 recognizes nothing; "
                           "geometry saturates faster than individuals; the final LEVEL 2 frame is mostly "
                           "recognized on arrival (cross-level transfer). Overlay: green = recognized, "
                           "blue = first sighting."}


_DEMOS = [
    _demo_live_ls20_sequence,
    lambda: _occlusion_demo("occlusion-t", "T tetromino — stem occluded",
                            [(0, 0), (1, 0), (2, 0), (1, 1)], [(1, 1)], [(0, 0), (1, 0), (2, 0), (1, 1)]),
    lambda: _occlusion_demo("occlusion-plus", "Plus pentomino — centre + arm occluded",
                            [(1, 0), (0, 1), (1, 1), (2, 1), (1, 2)], [(1, 1), (1, 0)],
                            [(1, 0), (0, 1), (1, 1), (2, 1), (1, 2)]),
    lambda: _occlusion_demo("occlusion-scaled", "2x-scaled T — scaled stem occluded",
                            [(x * 2 + dx, y * 2 + dy) for (x, y) in [(0, 0), (1, 0), (2, 0), (1, 1)]
                             for dx in range(2) for dy in range(2)],
                            [(2, 2), (3, 2), (2, 3), (3, 3)], [(0, 0), (1, 0), (2, 0), (1, 1)]),
    _demo_occlusion_reject,
    _demo_recolor, _demo_resize,
    _demo_store_then_recognize, _demo_new_distinguished,
    _demo_regeneration, _demo_replay,
    _demo_input_gradient, _demo_input_video,
]


def run_demos(only: str | None = None) -> dict:
    """Run all demos (or one by id) and return their visual results + pass/fail."""
    out = []
    for make in _DEMOS:
        try:
            demo = make()
            demo.setdefault("frames", demo.get("panels") or [])  # animate: default to panels
        except Exception as err:  # noqa: BLE001 - surface a failed demo, don't crash the page
            out.append({"id": "error", "group": "Error", "title": str(err),
                        "panels": [], "frames": [], "result": {"error": str(err)}, "passed": False})
            continue
        if only and demo.get("id") != only:
            continue
        out.append(demo)
    return {"demos": out, "total": len(out), "passed": sum(1 for d in out if d.get("passed"))}


# --- server-owned background runs (the UI only OBSERVES) ---------------------
# The sanity tests run on the SERVER in a background thread; the page polls the
# cached results and animates them. The UI never computes.
_demo_state: dict = {"running": False, "results": None, "startedAt": None,
                     "finishedAt": None, "only": None}
_demo_lock = threading.Lock()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_demo_state() -> dict:
    """Observe the latest server run: {running, results, startedAt, finishedAt}."""
    with _demo_lock:
        st = dict(_demo_state)
    res = st.get("results") or {"demos": [], "total": 0, "passed": 0}
    return {**res, "running": st["running"], "startedAt": st["startedAt"],
            "finishedAt": st["finishedAt"], "only": st["only"]}


def _run_job(only: str | None) -> None:
    try:
        res = run_demos(only=only)
        with _demo_lock:
            prev = (_demo_state.get("results") or {}).get("demos", [])
            if only and prev:
                fresh = res["demos"][0] if res["demos"] else None
                demos = [(fresh if fresh and d["id"] == only else d) for d in prev]
                if fresh and all(d["id"] != only for d in prev):
                    demos.append(fresh)
            else:
                demos = res["demos"]
            _demo_state["results"] = {"demos": demos, "total": len(demos),
                                      "passed": sum(1 for d in demos if d.get("passed"))}
    finally:
        with _demo_lock:
            _demo_state["running"] = False
            _demo_state["finishedAt"] = _now()


def start_demo_run(only: str | None = None) -> dict:
    """Kick off a background server run (no-op if one is already running) and
    return immediately. The page observes progress via get_demo_state()."""
    with _demo_lock:
        if _demo_state["running"]:
            return get_demo_state()
        _demo_state["running"] = True
        _demo_state["startedAt"] = _now()
        _demo_state["finishedAt"] = None
        _demo_state["only"] = only
    threading.Thread(target=_run_job, args=(only,), name=f"sanity-tests-{only or 'all'}",
                     daemon=True).start()
    return get_demo_state()
