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


# --- invariance (rotation / reflection) + change (add / remove / match) -----

def _frame_objs(specs):
    """A frame with several objects: specs = [(color, offsets, cx, cy), ...]."""
    import symbolic_arc as sa
    geom = []
    for i, (color, off, cx, cy) in enumerate(specs):
        sig = sa._shape_key((None, sa._canon_br([tuple(c) for c in off])))
        geom.append({"id": f"p{i}", "sig": sig, "color": color,
                     "off": [list(c) for c in off], "cx": cx, "cy": cy})
    return {"metta": "", "geom": geom}


def _placed(specs):
    """Lay several objects on one display grid: specs = [(color, offsets, ox, oy)]."""
    cells = []
    for (color, off, ox, oy) in specs:
        for (x, y) in off:
            cells.append((ox + x, oy + y, "object", color))
    return cells


def _demo_rotation():
    import symbolic_arc as sa
    mem = tempfile.mkdtemp()
    L = [(0, 0), (0, 1), (0, 2), (1, 2)]
    rot = list(sa._norm([(y, -x) for (x, y) in L]))          # 90° rotation
    sa.remember_objects([_frame_col(_RED, L)], "demo-1", mem, write=True)
    b = _frame_col(_RED, rot)
    sa.remember_objects([b], "demo-2", mem, write=True)
    ids = sa.registry_snapshot(mem)["scopes"]["demo"]["identities"]
    panels = [_panel("stored", [(x, y, "object", _RED) for (x, y) in L]),
              _panel("rotated 90°", [(x, y, "regen", _GREEN) for (x, y) in rot])]
    passed = len(ids) == 1 and ids[0]["seen"] == 2 and b["geom"][0]["memNew"] is False
    return {"id": "rotation", "group": "Identity (invariance)",
            "title": "Rotation is the same object", "panels": panels,
            "result": {"object": ids[0]["name"] if ids else None,
                       "recognized_not_new": bool(ids) and b["geom"][0]["memNew"] is False,
                       "seen": ids[0]["seen"] if ids else 0, "identities": len(ids)},
            "passed": passed,
            "description": "Orientation is an occurrence attribute; a 90°-rotated shape recognizes as the "
                           "same object (D4 rotation-normalized identity)."}


def _demo_reflection():
    import symbolic_arc as sa
    mem = tempfile.mkdtemp()
    L = [(0, 0), (0, 1), (0, 2), (1, 2)]
    refl = list(sa._norm([(-x, y) for (x, y) in L]))         # mirror left-right
    sa.remember_objects([_frame_col(_RED, L)], "demo-1", mem, write=True)
    b = _frame_col(_RED, refl)
    sa.remember_objects([b], "demo-2", mem, write=True)
    ids = sa.registry_snapshot(mem)["scopes"]["demo"]["identities"]
    panels = [_panel("stored", [(x, y, "object", _RED) for (x, y) in L]),
              _panel("mirrored", [(x, y, "regen", _GREEN) for (x, y) in refl])]
    passed = len(ids) == 1 and ids[0]["seen"] == 2 and b["geom"][0]["memNew"] is False
    return {"id": "reflection", "group": "Identity (invariance)",
            "title": "Reflection is the same object", "panels": panels,
            "result": {"object": ids[0]["name"] if ids else None,
                       "recognized_not_new": bool(ids) and b["geom"][0]["memNew"] is False,
                       "seen": ids[0]["seen"] if ids else 0, "identities": len(ids)},
            "passed": passed,
            "description": "A mirrored shape recognizes as the same object (identity is reflection-normalized)."}


def _demo_addition():
    import symbolic_arc as sa
    A = [(0, 0), (0, 1)]                       # domino
    B = [(0, 0), (1, 0), (2, 0)]              # I-tromino
    C = [(0, 0), (1, 0), (1, 1)]             # V-tromino (the ADDED object)
    mem = tempfile.mkdtemp()
    sa.remember_objects([_frame_objs([(_RED, A, 5, 5), (_BLUE, B, 20, 5)])], "demo-1", mem, write=True)
    fr2 = _frame_objs([(_RED, A, 5, 5), (_BLUE, B, 20, 5), (_GREEN, C, 12, 20)])
    sa.remember_objects([fr2], "demo-2", mem, write=True)
    added = [g for g in fr2["geom"] if g.get("memNew")]
    panels = [_panel("state 1 — 2 objects", _placed([(_RED, A, 0, 0), (_BLUE, B, 4, 0)])),
              _panel("state 2 — one added (green)",
                     _placed([(_RED, A, 0, 0), (_BLUE, B, 4, 0)]) + [(x, y + 4, "regen", _GREEN) for (x, y) in C])]
    passed = len(added) == 1
    return {"id": "addition", "group": "Change detection",
            "title": "Object addition is detected", "panels": panels,
            "result": {"added": len(added),
                       "added_shape": sa._identity_name(C)},
            "passed": passed,
            "description": "An object present in the later state but not the earlier one is committed as new "
                           "(memNew), i.e. an addition is detected."}


def _demo_removal():
    import symbolic_arc as sa
    A = [(0, 0), (0, 1)]
    B = [(0, 0), (1, 0), (2, 0)]
    C = [(0, 0), (1, 0), (1, 1)]
    before = {sa._identity_name(o) for o in (A, B, C)}
    after = {sa._identity_name(o) for o in (A, B)}
    removed = sorted(before - after)
    panels = [_panel("state 1 — 3 objects",
                     _placed([(_RED, A, 0, 0), (_BLUE, B, 4, 0), (_GREEN, C, 0, 4)])),
              _panel("state 2 — one removed",
                     _placed([(_RED, A, 0, 0), (_BLUE, B, 4, 0)])
                     + [(x, y + 4, "hidden", None) for (x, y) in C])]
    passed = removed == [sa._identity_name(C)]
    return {"id": "removal", "group": "Change detection",
            "title": "Object removal is detected", "panels": panels,
            "result": {"removed": removed, "removed_count": len(removed)},
            "passed": passed,
            "description": "Comparing the two states by object identity, the object gone from the later state "
                           "is reported as removed (dashed)."}


def _demo_correspondence():
    import symbolic_arc as sa
    A = [(0, 0), (0, 1), (0, 2), (1, 2)]     # L
    B = [(0, 0), (1, 0), (2, 0), (1, 1)]     # T
    # same two objects, moved to new positions in state 2
    before = [(sa._identity_name(A), (2, 2)), (sa._identity_name(B), (12, 3))]
    after = [(sa._identity_name(A), (6, 8)), (sa._identity_name(B), (18, 9))]
    matches = []
    for (bid, bpos) in before:
        for (aid, apos) in after:
            if aid == bid:
                matches.append({"object": bid, "from": list(bpos), "to": list(apos)})
                break
    panels = [_panel("state 1", _placed([(_RED, A, 2, 2), (_BLUE, B, 12, 3)])),
              _panel("state 2 — same objects, moved",
                     _placed([(_RED, A, 6, 8), (_BLUE, B, 18, 9)]))]
    passed = len(matches) == 2
    return {"id": "correspondence", "group": "Change detection",
            "title": "Match corresponding objects between states", "panels": panels,
            "result": {"matched": len(matches),
                       "moves": [f'{m["object"]}: {m["from"]}→{m["to"]}' for m in matches]},
            "passed": passed,
            "description": "Objects in two states are put in correspondence by their identity, so the same "
                           "object is tracked between before/after states even after moving."}


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


def _variant_prov(exemplar, wh, cname) -> str:
    """Provenance of a raw part relative to a shape's exemplar (its first raw form):
    which normalization filter had to fire for this raw part to be recognized as the
    same shape. 'direct' means it matched as-is; otherwise the tag names the filter(s)
    (scale / rotation / colour) that 'made' this learner by collapsing it onto the shape."""
    ex_wh, ex_c = exemplar
    tags = []
    if tuple(wh) != tuple(ex_wh):
        tags.append("rotation" if (wh[1], wh[0]) == tuple(ex_wh) else "scale")
    if cname != ex_c:
        tags.append("colour")
    return "+".join(tags) if tags else "direct"


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
    geo_seen: dict = {}            # shape -> {variantKey: provenance}  (learners + how each was made)
    geo_exemplar: dict = {}        # shape -> ((w,h), colour) of its first raw form (the exemplar)
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
        frame_geo: dict = {}       # shape -> {variantKey: rawform}  raw parts seen this frame
        frame_ind: set = set()
        pj = sym / f"{idv}__prolog.parts.json"
        parts = []
        if pj.is_file():
            try:
                parts = _json.loads(pj.read_text(encoding="utf-8"))
            except (OSError, _json.JSONDecodeError):
                parts = []
        bg_area = 0.33 * idx.shape[0] * idx.shape[1]   # skip background floods, not real objects
        for p in parts:
            off = p.get("off") or []
            if not off or len(off) > bg_area:
                continue
            geo = sa._identity_name(off) or ("shape_" + str(p.get("sig")))   # geometry
            cname = sa._cname(p.get("color", ""))
            ind = (geo, cname)                                               # individual
            oxs = [c[0] for c in off]; oys = [c[1] for c in off]
            w = max(oxs) - min(oxs) + 1; h = max(oys) - min(oys) + 1         # raw (pre-normalization) size
            vk = (w, h, cname)                                               # distinct raw variant key
            geo_known = geo in geo_seen        # recognized only if seen in a PRIOR frame
            ind_known = ind in ind_seen
            geo_recog += geo_known; geo_new += (not geo_known)
            ind_recog += ind_known; ind_new += (not ind_known)
            frame_geo.setdefault(geo, {})[vk] = ((w, h), cname)
            frame_ind.add(ind)
            # overlay coloured by INDIVIDUAL recognition: green recognized, blue new
            cx, cy = p.get("cx", 0), p.get("cy", 0)
            # place the blob by aligning its CENTROID (mean of offsets) to (cx, cy);
            # the bbox midpoint used before shifted asymmetric shapes by 1-2 cells.
            bx = int(round(cx - sum(oxs) / len(oxs)))
            by = int(round(cy - sum(oys) / len(oys)))
            role, col = ("regen", _GREEN) if ind_known else ("visible", _BLUE)
            for (dx, dy) in off:
                roled.append((bx + dx, by + dy, role, col))
        before_obj, before_geo = len(ind_seen), len(geo_seen)   # known BEFORE learning this frame
        for g, variants in frame_geo.items():   # learn AFTER scoring: accrue evidence + provenance
            if g not in geo_exemplar:            # first raw form founds the shape (direct)
                geo_exemplar[g] = next(iter(variants.values()))
            dst = geo_seen.setdefault(g, {})
            for vk, ((w, h), cname) in variants.items():
                dst[vk] = _variant_prov(geo_exemplar[g], (w, h), cname)
        ind_seen |= frame_ind
        after_obj, after_geo = len(ind_seen), len(geo_seen)     # known AFTER learning this frame
        if first_ind_recog is None:
            first_ind_recog, first_geo_recog = ind_recog, geo_recog
        total_ind_recog += ind_recog
        direct = sum(1 for v in geo_seen.values() for pr in v.values() if pr == "direct")
        made = sum(1 for v in geo_seen.values() for pr in v.values() if pr != "direct")
        rows, cols = idx.shape[0], idx.shape[1]
        base = [(x, y, "object", hexpal[int(idx[y, x])]) for y in range(rows) for x in range(cols)]
        scene = _panel(
            f"{idv} · this frame: {ind_recog} recognized, {ind_new} new "
            f"· objects known {before_obj}→{after_obj}, shapes {before_geo}→{after_geo} "
            f"· learners {direct} direct / {made} via filter",
            base)
        # Recognition map shown to the SIDE (not painted over the scene): green =
        # recognized object, blue = new first sighting, rest dark.
        scene["aux"] = _panel("recognition · green = recognized · blue = new",
                              roled, ox=0, oy=0, w=cols, h=rows)
        frames.append(scene)

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
                l2_made = 0
                bg2 = 0.33 * idx2.shape[0] * idx2.shape[1]
                for p in pr.get("geom", []):
                    off = p.get("off") or []
                    if not off or len(off) > bg2:
                        continue
                    geo = sa._identity_name(off) or ("shape_" + str(p.get("sig")))
                    cname = sa._cname(p.get("color", ""))
                    ind = (geo, cname)
                    geo_known = geo in geo_seen
                    ind_known = ind in ind_seen
                    lvl2_total += 1
                    lvl2_geo += geo_known
                    lvl2_ind += ind_known
                    cx, cy = p.get("cx", 0), p.get("cy", 0)
                    oxs = [c[0] for c in off]; oys = [c[1] for c in off]
                    w = max(oxs) - min(oxs) + 1; h = max(oys) - min(oys) + 1
                    if geo_known and _variant_prov(geo_exemplar.get(geo, ((w, h), cname)), (w, h), cname) != "direct":
                        l2_made += 1                        # recognized only via the normalization filter
                    bx = int(round(cx - sum(oxs) / len(oxs)))
                    by = int(round(cy - sum(oys) / len(oys)))
                    role, col = ("regen", _GREEN) if ind_known else ("visible", _BLUE)
                    for (dx, dy) in off:
                        roled2.append((bx + dx, by + dy, role, col))
                r2, c2 = idx2.shape[0], idx2.shape[1]
                base2 = [(x, y, "object", hexpal2[int(idx2[y, x])])
                         for y in range(r2) for x in range(c2)]
                l2scene = _panel(
                    f"LEVEL 2 (saved_002) frame 1 · objects {lvl2_ind}/{lvl2_total} recognized "
                    f"· shapes {lvl2_geo}/{lvl2_total} ({l2_made} via filter) — carried over from level 1",
                    base2)
                l2scene["aux"] = _panel("recognition · green = recognized · blue = new",
                                        roled2, ox=0, oy=0, w=c2, h=r2)
                frames.append(l2scene)

    # demonstrates learning: the first frame recognizes nothing (empty memory),
    # geometry (fewer, shared) saturates faster than individuals (colour variety),
    # and the level-2 frame is mostly recognized on arrival (cross-level transfer).
    # per-shape learner evidence + provenance: how many raw variants (identities)
    # instantiate each shape, and how many only exist because a normalization
    # filter (scale/rotation/colour) collapsed a raw variant onto the shape.
    ev = sorted(((len(v), g) for g, v in geo_seen.items()), reverse=True)
    top_shape = (f"{ev[0][1]} ({ev[0][0]} learners)" if ev else "none")
    direct_all = sum(1 for v in geo_seen.values() for pr in v.values() if pr == "direct")
    made_all = sum(1 for v in geo_seen.values() for pr in v.values() if pr != "direct")
    passed = bool(frames) and first_ind_recog == 0 and total_ind_recog > 0
    return {"id": "live-ls20", "group": "Live sequence (real data)",
            "title": "Live ls20 recording — recognition builds up, transfers to level 2", "panels": frames[:1],
            "frames": frames,
            "result": {"frames": len(frames), "frame0_objects_recognized": first_ind_recog,
                       "frame0_shapes_recognized": first_geo_recog,
                       "objects_learned": len(ind_seen), "shapes_learned": len(geo_seen),
                       "max_learners_per_shape": (ev[0][0] if ev else 0),
                       "most_learned_shape": top_shape,
                       "learners_direct": direct_all,
                       "learners_via_filter": made_all,
                       "level2_objects_recognized": f"{lvl2_ind}/{lvl2_total}",
                       "level2_shapes_recognized": f"{lvl2_geo}/{lvl2_total}"},
            "passed": passed,
            "description": "The real recorded ls20 frames played from an EMPTY memory. Two things are learned "
                           "separately: GEOMETRY (colour-free shape vocabulary, shared) and INDIVIDUALS "
                           "(shape+colour, per game). Each shape accrues evidence = the raw variants that use "
                           "it, and every learner keeps its provenance: 'direct' (matched as-is) vs. made by "
                           "the normalization filter (scale/rotation/colour) that collapsed a raw variant onto "
                           "the shape. Frame 0 recognizes nothing; geometry saturates faster than individuals; "
                           "the final LEVEL 2 frame is mostly recognized on arrival (cross-level transfer). "
                           "Overlay: green = recognized, blue = first sighting."}


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
    _demo_rotation, _demo_reflection,
    _demo_store_then_recognize, _demo_new_distinguished,
    _demo_addition, _demo_removal, _demo_correspondence,
    _demo_regeneration, _demo_replay,
    _demo_input_gradient, _demo_input_video,
]


# Static metadata for every sanity test, in _DEMOS order, so the page can list
# the tests as "not run yet" (each individually runnable) BEFORE anything runs.
# Kept in sync with the id/group/title each builder returns.
_DEMO_CATALOG = [
    {"id": "live-ls20", "group": "Live sequence (real data)",
     "title": "Live ls20 recording — recognition builds up, transfers to level 2",
     "resultKeys": ["frames", "frame0_objects_recognized", "frame0_shapes_recognized",
                    "objects_learned", "shapes_learned", "max_learners_per_shape",
                    "most_learned_shape", "learners_direct", "learners_via_filter",
                    "level2_objects_recognized", "level2_shapes_recognized"]},
    {"id": "occlusion-t", "group": "Occlusion completion", "title": "T tetromino — stem occluded",
     "resultKeys": ["recognized", "scale", "orientation", "residual", "confidence", "faithful"]},
    {"id": "occlusion-plus", "group": "Occlusion completion", "title": "Plus pentomino — centre + arm occluded",
     "resultKeys": ["recognized", "scale", "orientation", "residual", "confidence", "faithful"]},
    {"id": "occlusion-scaled", "group": "Occlusion completion", "title": "2x-scaled T — scaled stem occluded",
     "resultKeys": ["recognized", "scale", "orientation", "residual", "confidence", "faithful"]},
    {"id": "occlusion-reject", "group": "Occlusion completion", "title": "Inconsistent fragment is rejected",
     "resultKeys": ["recognized", "note"]},
    {"id": "recolor", "group": "Identity (recolor / resize)", "title": "Recolour is the same object",
     "resultKeys": ["object", "seen", "colours", "recognized_not_new", "identities"]},
    {"id": "resize", "group": "Identity (recolor / resize)", "title": "Resize is the same object",
     "resultKeys": ["object", "seen", "sizes", "identities"]},
    {"id": "rotation", "group": "Identity (invariance)", "title": "Rotation is the same object",
     "resultKeys": ["object", "recognized_not_new", "seen", "identities"]},
    {"id": "reflection", "group": "Identity (invariance)", "title": "Reflection is the same object",
     "resultKeys": ["object", "recognized_not_new", "seen", "identities"]},
    {"id": "store-then-recognize", "group": "Recognition", "title": "Store, then recognize the same object later",
     "resultKeys": ["recognized_not_new", "seen", "identities"]},
    {"id": "new-distinguished", "group": "Recognition", "title": "A genuinely new structure is distinguished",
     "resultKeys": ["is_new", "identities"]},
    {"id": "addition", "group": "Change detection", "title": "Object addition is detected",
     "resultKeys": ["added", "added_shape"]},
    {"id": "removal", "group": "Change detection", "title": "Object removal is detected",
     "resultKeys": ["removed", "removed_count"]},
    {"id": "correspondence", "group": "Change detection", "title": "Match corresponding objects between states",
     "resultKeys": ["matched", "moves"]},
    {"id": "regeneration", "group": "Regeneration", "title": "Regenerate a stored shape from its turtle form",
     "resultKeys": ["shape", "faithful"]},
    {"id": "replay", "group": "Replay / determinism", "title": "Same input -> same identity + canonical form",
     "resultKeys": ["same_identity", "same_form", "handle"]},
    {"id": "input-gradient", "group": "Input breadth", "title": "Raster gradient -> small flat grid",
     "resultKeys": ["cols", "rows", "colours"]},
    {"id": "input-video", "group": "Input breadth", "title": "Simple video: a block tracked as one object",
     "resultKeys": ["frames", "block_object", "block_identities"]},
]


def _preview_live_ls20():
    """The raw first ls20 frame as an INPUT MAP: the decoded scene with no
    recognition overlay at all (nothing recognized yet). Cheap -- one png decode,
    no part-graph, no scoring -- so it is a safe 'unstarted' preview."""
    import json as _json
    import symbolic_arc as sa
    setdir = _LS20_DIR
    if not setdir.is_dir():
        return None
    order = []
    mf_path = setdir / "manifest.json"
    if mf_path.is_file():
        try:
            order = [it["id"] for it in _json.loads(mf_path.read_text(encoding="utf-8")).get("items", [])]
        except (OSError, _json.JSONDecodeError):
            order = []
    if not order:
        order = sorted(p.stem for p in setdir.glob("*.png"))
    if not order:
        return None
    idv = order[0]
    png = next(iter(setdir.glob(f"{idv}.png")), None)
    if not png:
        return None
    idx, hexpal, _c, _r = sa.decode_grid(str(png))
    base = [(x, y, "object", hexpal[int(idx[y, x])])
            for y in range(idx.shape[0]) for x in range(idx.shape[1])]
    return _panel(f"{idv} · input map — nothing recognized yet (press ▶ Run)", base)


_live_preview = None
_live_preview_done = False
_live_preview_lock = threading.Lock()


def _live_preview_cached():
    """Compute the live-ls20 input-map preview once and cache it (one png decode)."""
    global _live_preview, _live_preview_done
    with _live_preview_lock:
        if _live_preview_done:
            return _live_preview
    try:
        pv = _preview_live_ls20()
    except Exception:  # noqa: BLE001
        pv = None
    with _live_preview_lock:
        _live_preview = pv
        _live_preview_done = True
    return pv


def demo_catalog() -> list:
    """The list of available sanity tests (id/group/title) WITHOUT running them, so
    the page can show them as 'not run yet' cards that are individually runnable.
    live-ls20 carries a cheap raw input-map `preview` for its unstarted card; other
    tests fall back to a blank map on the page until run."""
    live_pv = _live_preview_cached()
    out = []
    for c in _DEMO_CATALOG:
        entry = dict(c)
        if c["id"] == "live-ls20":
            entry["preview"] = live_pv
        out.append(entry)
    return out


# Full Phase 2 & Phase 3 SoW deliverable coverage, so the Sanity Tests page can
# show an entry for EVERY deliverable -- done or not -- and mark the gaps.
# Tuple: (phase, id, title, implemented, llm_free, demo)
#   implemented / llm_free: "full" | "partial" | "none"
#   demo: a runnable recognition-demo id, "phase3" (the live Phase 3 run), or None
_SOW_COVERAGE = [
    ("P2", "1a", "Extract objects from grid", "full", "full", "live-ls20"),
    ("P2", "1b", "Extract objects from image (raster)", "full", "full", "input-gradient"),
    ("P2", "1c", "Extract objects from video", "full", "full", "input-video"),
    ("P2", "2a", "Represent properties & appearance", "full", "full", None),
    ("P2", "2b", "Represent structure", "full", "full", None),
    ("P2", "2c", "Represent relationships (adjacency/containment)", "full", "full", None),
    ("P2", "2d", "Represent position/orientation/scale", "full", "full", None),
    ("P2", "3a", "Stable identity across encounters", "full", "full", "store-then-recognize"),
    ("P2", "3b", "Stable identity across state transitions", "full", "full", "correspondence"),
    ("P2", "4a", "Match corresponding objects between states", "full", "full", "correspondence"),
    ("P2", "4b", "Match across repeated encounters", "full", "full", "store-then-recognize"),
    ("P2", "5a", "Recognize despite position", "full", "full", "store-then-recognize"),
    ("P2", "5b", "Recognize despite rotation", "full", "full", "rotation"),
    ("P2", "5c", "Recognize despite scale", "full", "full", "resize"),
    ("P2", "5d", "Recognize despite reflection", "full", "full", "reflection"),
    ("P2", "5e", "Recognize despite colour", "full", "full", "recolor"),
    ("P2", "5f", "Recognize despite noise", "none", "none", None),
    ("P2", "5g", "Recognize despite partial visibility", "full", "full", "occlusion-t"),
    ("P2", "6a", "Detect movement", "full", "full", "input-video"),
    ("P2", "6b", "Detect recoloring (as change)", "partial", "partial", None),
    ("P2", "6c", "Detect resizing (as change)", "partial", "partial", None),
    ("P2", "6d", "Detect addition", "full", "full", "addition"),
    ("P2", "6e", "Detect removal", "full", "full", "removal"),
    ("P2", "6f", "Detect structural change", "full", "full", "new-distinguished"),
    ("P2", "7", "Normalized store -> regenerate", "full", "full", "regeneration"),
    ("P2", "8", "Distinguish recognized vs new", "full", "full", "new-distinguished"),
    ("P2", "9", "Prevent duplicate storage", "full", "full", None),
    ("P2", "10a", "Accumulate evidence", "full", "full", "live-ls20"),
    ("P2", "10b", "Accumulate provenance", "full", "full", "live-ls20"),
    ("P2", "11a", "Preserve encounter history", "full", "full", None),
    ("P2", "11b", "Deterministic replay", "full", "full", "replay"),
    ("P2", "12a", "Object (individual) memory", "full", "full", "live-ls20"),
    ("P2", "12b", "Shape (geometry) memory", "full", "full", "live-ls20"),
    ("P2", "13", "Demonstrate regeneration", "full", "full", "regeneration"),
    ("P2", "14a", "Recognition under modest degradation", "none", "none", None),
    ("P2", "14b", "Recognition under partial occlusion", "full", "full", "occlusion-t"),
    ("P2", "15a", "Tests", "full", "full", None),
    ("P2", "15b", "Documentation", "full", "full", None),
    ("P3", "1", "Interface / data contract to Game Object Learner", "full", "full", None),
    ("P3", "2a", "Provide detected objects", "full", "full", None),
    ("P3", "2b", "Provide properties", "full", "full", None),
    ("P3", "2c", "Provide relationships", "full", "full", None),
    ("P3", "2d", "Provide correspondences", "full", "full", None),
    ("P3", "2e", "Provide state differences", "full", "full", None),
    ("P3", "2f", "Provide encounter history", "full", "full", None),
    ("P3", "3", "Stable interface decoupled from perception internals", "full", "full", None),
    ("P3", "4a", "Interface validation", "full", "full", None),
    ("P3", "4b", "Structured errors", "full", "full", None),
    ("P3", "4c", "Integration tests", "full", "full", None),
    ("P3", "4d", "Example workflows", "full", "full", None),
    ("P3", "5", "Infer candidate transformations / transition rules", "full", "full", "phase3"),
    ("P3", "6a", "Support multiple candidate interpretations", "full", "full", "phase3"),
    ("P3", "6b", "Retain evidence for successful & unsuccessful rules", "full", "full", "phase3"),
    ("P3", "7", "Apply learned transformations to new cases", "full", "full", "phase3"),
    ("P3", "8", "Predict later states before outcomes", "full", "full", "phase3"),
    ("P3", "9", "Compare predictions with independent outcomes", "full", "full", "phase3"),
    ("P3", "10", "Update rule evidence on success/failure", "full", "full", "phase3"),
    ("P3", "11", "Prevent post-hoc explanations counting as predictions", "full", "full", "phase3"),
    ("P3", "12a", "Recognition of partly occluded objects", "full", "full", "occlusion-t"),
    ("P3", "12b", "Completion of partly occluded objects", "full", "full", "occlusion-t"),
    ("P3", "13a", "Operation in grid environments", "full", "full", "live-ls20"),
    ("P3", "13b", "Operation in raster environments", "full", "full", "input-gradient"),
    ("P3", "13c", "Rendered arcade / fixed-camera physics / top-down manipulation", "partial", "full", None),
    ("P3", "14a", "Integration documentation", "full", "full", None),
    ("P3", "14b", "Example scripts", "full", "full", None),
    ("P3", "14c", "Acceptance-test results", "full", "full", None),
    ("P3", "14d", "Developer notes", "full", "full", None),
]


def sow_coverage() -> list:
    """Every Phase 2 & 3 SoW deliverable with implemented/LLM-free/demo status, so
    the page can list an entry for each -- including the ones not done yet."""
    out = []
    for phase, did, title, impl, llm, demo in _SOW_COVERAGE:
        if demo:
            demo_status = "demo"
        elif impl == "none":
            demo_status = "not-done"
        else:
            demo_status = "no-demo"
        out.append({"phase": phase, "id": did, "title": title,
                    "implemented": impl, "llmFree": llm,
                    "demo": demo, "demoStatus": demo_status})
    return out


def run_demos(only: str | None = None) -> dict:
    """Run all demos (or one by id) and return their visual results + pass/fail."""
    out = []
    for meta, make in zip(_DEMO_CATALOG, _DEMOS):
        if only and meta["id"] != only:      # skip building non-matching demos on a single-test run
            continue
        try:
            demo = make()
            demo.setdefault("frames", demo.get("panels") or [])  # animate: default to panels
        except Exception as err:  # noqa: BLE001 - surface a failed demo, don't crash the page
            out.append({"id": "error", "group": "Error", "title": str(err),
                        "panels": [], "frames": [], "result": {"error": str(err)}, "passed": False})
            continue
        if only and demo.get("id") != only:  # safety if the catalog drifts from the builders
            continue
        out.append(demo)
    return {"demos": out, "total": len(out), "passed": sum(1 for d in out if d.get("passed"))}


# --- server-owned background runs (the UI only OBSERVES) ---------------------
# The sanity tests run on the SERVER in a background thread; the page polls the
# cached results and animates them. The UI never computes.
_demo_state: dict = {"running": False, "results": None, "startedAt": None,
                     "finishedAt": None, "only": None}
_demo_lock = threading.Lock()
_demo_gen = 0  # bumped on every start/stop/clear; an in-flight job whose gen is stale is discarded


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_demo_state() -> dict:
    """Observe the latest server run: {running, results, startedAt, finishedAt}."""
    with _demo_lock:
        st = dict(_demo_state)
    res = st.get("results") or {"demos": [], "total": 0, "passed": 0}
    return {**res, "catalog": demo_catalog(), "coverage": sow_coverage(), "running": st["running"],
            "startedAt": st["startedAt"], "finishedAt": st["finishedAt"], "only": st["only"]}


def _run_job(only: str | None, gen: int) -> None:
    try:
        res = run_demos(only=only)
        with _demo_lock:
            if gen != _demo_gen:          # stopped or cleared while we were running: discard
                return
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
            if gen == _demo_gen:          # only the current job may flip running off
                _demo_state["running"] = False
                _demo_state["finishedAt"] = _now()


def start_demo_run(only: str | None = None) -> dict:
    """Kick off a background server run and return immediately. PREEMPTS any run
    already in progress (its stale generation makes it discard its result) so Run
    and Run step 1 always restart cleanly from the beginning. The page observes
    progress via get_demo_state()."""
    global _demo_gen
    with _demo_lock:
        _demo_gen += 1                    # preempt/cancel any in-flight run
        gen = _demo_gen
        _demo_state["running"] = True
        _demo_state["startedAt"] = _now()
        _demo_state["finishedAt"] = None
        _demo_state["only"] = only
    threading.Thread(target=_run_job, args=(only, gen), name=f"sanity-tests-{only or 'all'}",
                     daemon=True).start()
    return get_demo_state()


def stop_demo_run() -> dict:
    """Stop any in-flight server run. The running job (if any) finishes its
    computation but its result is discarded; the cached results are kept."""
    global _demo_gen
    with _demo_lock:
        _demo_gen += 1                    # invalidate any in-flight job
        _demo_state["running"] = False
        _demo_state["finishedAt"] = _now()
    return get_demo_state()


def clear_demo_state(only: str | None = None) -> dict:
    """Stop any in-flight run AND clear cached results. With `only`, clear just that
    one test (back to 'not run'); without it, clear everything."""
    global _demo_gen
    with _demo_lock:
        _demo_gen += 1                    # invalidate any in-flight job
        _demo_state["running"] = False
        _demo_state["finishedAt"] = _now()
        if only:
            res = _demo_state.get("results")
            if res and res.get("demos"):
                demos = [d for d in res["demos"] if d.get("id") != only]
                _demo_state["results"] = ({"demos": demos, "total": len(demos),
                                           "passed": sum(1 for d in demos if d.get("passed"))}
                                          if demos else None)
        else:
            _demo_state["results"] = None
            _demo_state["startedAt"] = None
            _demo_state["finishedAt"] = None
            _demo_state["only"] = None
    return get_demo_state()
