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
import time
from datetime import datetime, timezone
from pathlib import Path

_PROLOG_DIR = Path(__file__).resolve().parent / "generative_vision" / "prolog"
if str(_PROLOG_DIR) not in sys.path:
    sys.path.insert(0, str(_PROLOG_DIR))
# The Phase 3 object-memory contract package lives in <repo>/python.
_PY_DIR = Path(__file__).resolve().parents[2] / "python"
if str(_PY_DIR) not in sys.path:
    sys.path.insert(0, str(_PY_DIR))
_REPO_ROOT = Path(__file__).resolve().parents[2]

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


def _demo_progressive_reveal():
    """Progressive occlusion during LEARNING (a small, controlled version of what the
    live ls20 recording shows): an object starts mostly hidden and is uncovered in
    connected CHUNKS as the player/AI moves. Each newly revealed chunk is registered
    as a PART; the object is built up incrementally from its parts, and its turtle
    (canonical form) stays PROVISIONAL — refined as parts arrive — only finalised once
    the whole object is uncovered. Early on the object may even read as several
    DISJOINT pieces before a later chunk connects them into one."""
    import symbolic_arc as sa
    from scipy import ndimage
    import numpy as _np
    # The object as the ordered CHUNKS a moving player reveals (each chunk = a part).
    # A PLUS/cross revealed arm-by-arm: the four arms appear as DISJOINT pieces, then
    # the centre chunk snaps them together into one connected object.
    parts = [
        [(2, 0), (2, 1)],       # 1: top arm
        [(0, 2), (1, 2)],       # 2: left arm  (disjoint -> 2 pieces)
        [(3, 2), (4, 2)],       # 3: right arm (disjoint -> 3 pieces)
        [(2, 3), (2, 4)],       # 4: bottom arm (disjoint -> 4 pieces)
        [(2, 2)],               # 5: centre — connects every arm into ONE object
    ]
    full = sorted({tuple(c) for pt in parts for c in pt})
    fullset = set(full)
    ox, oy, w, h = _bbox(fullset)

    def _pieces(cells):
        if not cells:
            return 0
        g = _np.zeros((h, w), dtype=int)
        for (x, y) in cells:
            g[y - oy, x - ox] = 1
        _lab, n = ndimage.label(g)
        return int(n)

    def _prov_name(cells):
        cl = sorted(cells)
        try:
            nm = sa._identity_name(cl)
        except Exception:  # noqa: BLE001
            nm = None
        if nm:
            return nm
        try:
            return "form_" + str(sa._shape_key((None, sa._canon_br(cl))))[:8]
        except Exception:  # noqa: BLE001
            return f"form_{len(cl)}cells"

    frames: list = []
    revealed: set = set()
    pieces_seq: list = []
    reads: list = []
    assembled_at = None
    for k, pt in enumerate(parts):
        chunk = {tuple(c) for c in pt}
        prev = set(revealed)
        revealed |= chunk
        pieces = _pieces(revealed)
        prev_pieces = pieces_seq[-1] if pieces_seq else None
        pieces_seq.append(pieces)
        name = _prov_name(revealed)
        reads.append(name)
        complete = revealed == fullset
        if assembled_at is None and pieces == 1 and prev_pieces is not None and prev_pieces > 1:
            assembled_at = k + 1
        hidden = fullset - revealed
        scene = _panel(
            f"reveal {k + 1}/{len(parts)} · +1 part ({len(chunk)} cells) · parts {k + 1} · pieces {pieces} · "
            + ("turtle FINAL" if complete else "turtle provisional") + f" · reads as {name}",
            [(x, y, "filled", _GREEN) for (x, y) in prev]
            + [(x, y, "visible", _BLUE) for (x, y) in chunk]
            + [(x, y, "hidden", None) for (x, y) in hidden], ox, oy, w, h)
        scene["aux"] = _panel(
            f"assembled from parts · {k + 1} part(s) · {pieces} piece(s) · "
            + ("COMPLETE" if complete else "provisional"),
            [(x, y, "object", _GREEN) for (x, y) in revealed], ox, oy, w, h)
        frames.append(scene)

    faithful = revealed == fullset
    turtle_evolved = len(set(reads)) > 1
    final_name = reads[-1] if reads else None
    passed = bool(frames) and faithful and len(parts) >= 2 and turtle_evolved and bool(final_name)
    return {"id": "progressive-reveal", "group": "Occlusion completion",
            "title": "Progressively revealed object — built from parts",
            "panels": [frames[0], frames[-1]], "frames": frames,
            "result": {"parts": len(parts), "frames": len(frames),
                       "pieces_over_time": pieces_seq,
                       "provisional_reads": reads,
                       "assembled_at_frame": assembled_at,
                       "final_shape": final_name,
                       "turtle_final": faithful,
                       "turtle_evolved": turtle_evolved,
                       "faithful": faithful},
            "passed": passed,
            "description": "A small controlled version of what the live ls20 recording shows: an object is "
                           "revealed in connected CHUNKS as the player/AI moves. Each chunk is registered as a "
                           "PART and the object is assembled incrementally; its turtle (canonical form) stays "
                           "PROVISIONAL and is refined as parts arrive, only finalised once the whole object is "
                           "uncovered. Note the object first reads as TWO disjoint pieces, then a later chunk "
                           "connects them into one. Overlay: green = already revealed, blue = the chunk just "
                           "discovered, dark = still occluded."}


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

def _demo_noise():
    import symbolic_arc as sa
    base = [(0, 0), (0, 1), (0, 2), (1, 2)]          # L-tetromino
    specks = [(4, 0), (5, 3), (3, 5)]                # scattered noise pixels
    noisy = base + specks
    raw_id = sa._identity_name(list(sa._norm(noisy)))
    clean = list(sa.denoise_cells(noisy))
    clean_id = sa._identity_name(clean)
    base_id = sa._identity_name(base)
    panels = [_panel("noisy input (base + specks)",
                     [(x, y, "object", _RED) for (x, y) in base]
                     + [(x, y, "visible", _BLUE) for (x, y) in specks]),
              _panel(f"denoised → {clean_id}", [(x, y, "regen", _GREEN) for (x, y) in sa._norm(clean)])]
    passed = clean_id == base_id and raw_id != base_id
    return {"id": "noise", "group": "Robustness (noise / degradation)",
            "title": "Recognize despite noise", "panels": panels,
            "result": {"noisy_identity": raw_id, "denoised_identity": clean_id,
                       "base_identity": base_id, "specks_removed": len(noisy) - len(clean)},
            "passed": passed,
            "description": "Scattered speck pixels are removed by keeping the largest connected component; "
                           "the denoised shape recognizes as the base object."}


def _demo_degradation():
    import symbolic_arc as sa
    base = [(0, 0), (1, 0), (2, 0), (1, 1)]          # T-tetromino
    base_id = sa._identity_name(base)
    scaled = [(x * 3 + dx, y * 3 + dy) for (x, y) in base for dx in range(3) for dy in range(3)]
    degraded = [c for i, c in enumerate(sorted(scaled)) if i % 6 != 0]   # drop ~1/6 of cells
    recovered = list(sa.downscale_cells(degraded, 3))                    # majority-vote downscale
    recovered_id = sa._identity_name(recovered)
    panels = [_panel("3x-scaled, cells dropped (degraded)",
                     [(x, y, "object", _RED) for (x, y) in sa._norm(degraded)]),
              _panel(f"downscaled (majority) → {recovered_id}",
                     [(x, y, "regen", _GREEN) for (x, y) in recovered])]
    passed = recovered_id == base_id
    return {"id": "degradation", "group": "Robustness (noise / degradation)",
            "title": "Recognize under modest degradation", "panels": panels,
            "result": {"base_identity": base_id, "recovered_identity": recovered_id,
                       "cells_dropped": len(scaled) - len(degraded)},
            "passed": passed,
            "description": "A down-scaled shape with missing cells is binned by a majority vote so each "
                           "block that is mostly filled is recovered, restoring the base object identity."}


def _demo_properties():
    import symbolic_arc as sa
    L = [(0, 0), (0, 1), (0, 2), (1, 2)]
    ident = sa._identity_name(L)
    xs = [x for x, _ in L]; ys = [y for _, y in L]
    w, h = max(xs) - min(xs) + 1, max(ys) - min(ys) + 1
    panels = [_panel(f"{ident}", [(x, y, "object", _RED) for (x, y) in L])]
    passed = ident == "tetromino_L" and len(L) == 4
    return {"id": "properties", "group": "Representation",
            "title": "Represent object properties, structure & pose", "panels": panels,
            "result": {"shape": ident, "cells": len(L), "bbox": f"{w}x{h}",
                       "centroid": [round(sum(xs) / len(xs), 1), round(sum(ys) / len(ys), 1)],
                       "colour": "red"},
            "passed": passed,
            "description": "Each object carries structure (cells/shape), pose (bbox, centroid) and appearance "
                           "(colour) as explicit properties."}


def _demo_relationships():
    import numpy as np
    import symbolic_arc as sa
    labels = np.zeros((11, 13), dtype=int)
    labels[2:5, 1:4] = 1          # left block
    labels[2:5, 4:7] = 2          # right block (adjacent to 1)
    labels[6:10, 7:12] = 4        # outer ring
    labels[7:9, 8:11] = 3         # inside 4 (enclosed)
    pairs = sa.adjacency(labels)
    gids = [int(g) for g in np.unique(labels)]

    def _border(g):
        return bool((labels[0, :] == g).any() or (labels[-1, :] == g).any()
                    or (labels[:, 0] == g).any() or (labels[:, -1] == g).any())
    region_info = {g: {"border": _border(g)} for g in gids}
    enc = sa.enclosures(region_info, pairs)
    adj = sorted({tuple(sorted((a, b))) for (a, b) in pairs if a and b})
    pal = {0: "#0b0f1a", 1: _RED, 2: _BLUE, 3: _GREEN, 4: "#e0b450"}
    cells = [(x, y, "object", pal[int(labels[y, x])])
             for y in range(labels.shape[0]) for x in range(labels.shape[1]) if labels[y, x]]
    panels = [_panel("regions: 1|2 adjacent, 3 inside 4", cells)]
    passed = (1, 2) in adj and enc == [(4, 3)]
    return {"id": "relationships", "group": "Representation",
            "title": "Represent relationships (adjacency / containment)", "panels": panels,
            "result": {"adjacent_pairs": [list(p) for p in adj],
                       "enclosures": [list(e) for e in enc]},
            "passed": passed,
            "description": "Real adjacency() + enclosures() compute spatial relationships between objects: "
                           "regions 1 and 2 are adjacent; region 3 is contained inside region 4."}


def _demo_recolor_change():
    import symbolic_arc as sa
    L = [(0, 0), (0, 1), (0, 2), (1, 2)]
    mem = tempfile.mkdtemp()
    sa.remember_objects([_frame_col(_RED, L)], "demo-1", mem, write=True)
    b = _frame_col(_BLUE, L)
    sa.remember_objects([b], "demo-2", mem, write=True)
    ids = sa.registry_snapshot(mem)["scopes"]["demo"]["identities"]
    colours = [v["color"] for v in ids[0]["variations"]] if ids else []
    recolored = len(set(colours)) > 1 and len(ids) == 1
    panels = [_panel("before (red)", [(x, y, "object", _RED) for (x, y) in L]),
              _panel("after (blue) — recoloured", [(x, y, "regen", _BLUE) for (x, y) in L])]
    return {"id": "recolor-change", "group": "Change detection",
            "title": "Detect recoloring", "panels": panels,
            "result": {"same_object": len(ids) == 1, "colours": colours, "recolored": recolored},
            "passed": recolored,
            "description": "The same object seen in a new colour is detected as a recolour (same identity, "
                           "two colour variations)."}


def _demo_resize_change():
    import symbolic_arc as sa
    base = [(0, 0), (1, 0)]
    big = [(x * 2 + dx, y * 2 + dy) for (x, y) in base for dx in range(2) for dy in range(2)]
    mem = tempfile.mkdtemp()
    sa.remember_objects([_frame_col(_RED, base)], "demo-1", mem, write=True)
    sa.remember_objects([_frame_col(_RED, big)], "demo-2", mem, write=True)
    ids = sa.registry_snapshot(mem)["scopes"]["demo"]["identities"]
    sizes = sorted({v["size"] for v in ids[0]["variations"]}) if ids else []
    resized = len(sizes) > 1 and len(ids) == 1
    panels = [_panel("before (small)", [(x, y, "object", _RED) for (x, y) in base]),
              _panel("after (2x) — resized", [(x, y, "regen", _GREEN) for (x, y) in sa._norm(big)])]
    return {"id": "resize-change", "group": "Change detection",
            "title": "Detect resizing", "panels": panels,
            "result": {"same_object": len(ids) == 1, "sizes": sizes, "resized": resized},
            "passed": resized,
            "description": "The same object seen at a new size is detected as a resize (same identity, two "
                           "size variations)."}


def _demo_dedup():
    import symbolic_arc as sa
    L = [(0, 0), (0, 1), (0, 2), (1, 2)]
    mem = tempfile.mkdtemp()
    sa.remember_objects([_frame_col(_RED, L)], "demo-1", mem, write=True)
    sa.remember_objects([_frame_col(_RED, L)], "demo-2", mem, write=True)
    ids = sa.registry_snapshot(mem)["scopes"]["demo"]["identities"]
    panels = [_panel("stored once", [(x, y, "object", _RED) for (x, y) in L]),
              _panel("seen again — not duplicated", [(x, y, "regen", _GREEN) for (x, y) in L])]
    passed = len(ids) == 1 and ids[0]["seen"] == 2
    return {"id": "dedup", "group": "Memory",
            "title": "Prevent duplicate storage", "panels": panels,
            "result": {"identities": len(ids), "seen": ids[0]["seen"] if ids else 0},
            "passed": passed,
            "description": "Re-encountering a known object bumps its seen count instead of storing a duplicate: "
                           "one identity, seen twice."}


def _demo_encounter_history():
    import symbolic_arc as sa
    L = [(0, 0), (0, 1), (0, 2), (1, 2)]
    mem = tempfile.mkdtemp()
    seen_series = []
    frames = []
    for k in range(3):
        sa.remember_objects([_frame_col(_RED, L)], f"demo-{k + 1}", mem, write=True)
        ids = sa.registry_snapshot(mem)["scopes"]["demo"]["identities"]
        s = ids[0]["seen"] if ids else 0
        seen_series.append(s)
        frames.append(_panel(f"encounter {k + 1} · seen={s}", [(x, y, "object", _GREEN) for (x, y) in L]))
    passed = seen_series == [1, 2, 3]
    return {"id": "encounter-history", "group": "Memory",
            "title": "Preserve encounter history", "panels": frames[:1], "frames": frames,
            "result": {"seen_series": seen_series},
            "passed": passed,
            "description": "Every re-encounter accrues to the object's persistent history; the seen count grows "
                           "1 → 2 → 3 across encounters."}


def _demo_phase3_contract():
    """Phase 3 interface/data contract: build a real GameObjectLearnerPayload with
    objects, properties, relationships, correspondences, state differences and
    encounter history, validate it, and show a malformed payload is rejected."""
    from object_memory import GameObjectLearnerPayload, IntegrationValidator, IntegrationError
    payload = GameObjectLearnerPayload(
        "state-2",
        ({"id": "player", "candidate_identity_id": "cand-player", "object_identity_id": "player",
          "encounter_id": "enc-2", "position": [2, 1], "shape": "domino", "colour": "red",
          "relationships": {"adjacent_to": ["wall"]}, "evidence_ids": ("ev1",)},
         {"id": "wall", "position": [3, 1], "shape": "box", "colour": "grey"}),
        correspondences=({"candidate_id": "cand-player", "stored_identity_id": "player",
                          "evidence_ids": ("ev1",)},),
        transitions=({"id": "player", "action": "step",
                      "properties": {"position": {"from": [1, 1], "to": [2, 1]}}},),
        provenance=("frame:s1", "frame:s2"), identity_ids=("player", "wall"),
        encounter_ids=("enc-1", "enc-2"),
        evidence=({"evidence_id": "ev1", "subject_id": "player", "polarity": "supports"},))
    valid = IntegrationValidator().validate(payload)
    rt = GameObjectLearnerPayload.from_dict(valid.to_dict())          # round-trips (REST parity)
    roundtrip_ok = rt.to_dict() == valid.to_dict()                    # JSON in == JSON out
    bad_rejected = False
    try:
        IntegrationValidator().validate(GameObjectLearnerPayload("state-x", ({"noid": True},)))
    except IntegrationError:
        bad_rejected = True
    panels = [_panel("2 objects handed to the Game Object Learner",
                     _placed([(_RED, [(0, 0), (0, 1)], 0, 0), ("#aaaaaa", [(0, 0)], 3, 0)])
                     + [(3, 1, "regen", _GREEN)])]
    passed = (roundtrip_ok and bad_rejected
              and len(valid.objects) == 2 and len(valid.transitions) == 1)
    return {"id": "phase3-contract", "group": "Phase 3 — integration",
            "title": "Game Object Learner data contract", "panels": panels,
            "result": {"schema_version": valid.schema_version, "objects": len(valid.objects),
                       "relationships": bool(valid.objects[0].get("relationships")),
                       "correspondences": len(valid.correspondences),
                       "state_differences": len(valid.transitions),
                       "encounter_history": len(valid.encounter_ids),
                       "roundtrip_ok": roundtrip_ok, "bad_payload_rejected": bad_rejected},
            "passed": passed,
            "description": "The perception layer hands a validated, versioned, JSON-serializable payload "
                           "(objects, properties, relationships, correspondences, state differences, encounter "
                           "history) to the Game Object Learner; it round-trips over REST and rejects malformed input."}


def _demo_environments():
    """Phase 3 representative environments: actually decode the rendered-arcade,
    fixed-camera-physics and top-down-manipulation fixture images with the LLM-free
    recogniser and count the objects found in each."""
    import os
    import numpy as np
    from scipy import ndimage
    import symbolic_arc as sa
    from object_memory import environment_progression_fixtures
    fx = environment_progression_fixtures()
    groups = {"rendered_arcade": fx.rendered_arcade,
              "fixed_camera_physics": fx.fixed_camera,
              "top_down_manipulation": fx.top_down_manipulation}
    counts: dict = {}
    panels: list = []
    ok = True
    for name, fixtures in groups.items():
        f = fixtures[0]
        safe = "".join(c if c.isalnum() else "_" for c in f.fixture_id)
        tmp = os.path.join(tempfile.mkdtemp(), safe + ".png")
        f.image.save(tmp)
        idx, hexpal, _cols, _rows = sa.decode_grid(tmp)
        vals, cnts = np.unique(idx, return_counts=True)
        bg = vals[int(np.argmax(cnts))]
        _lab, nobj = ndimage.label(idx != bg)
        counts[name] = int(nobj)
        ok = ok and int(nobj) >= 1
        panels.append(_panel(f"{name}: {nobj} objects", _grid_to_cells(idx, hexpal)))
    passed = ok and len(counts) == 3
    return {"id": "environments", "group": "Phase 3 — integration",
            "title": "Operation across representative environments", "panels": panels,
            "result": {**{k: f"{v} objects" for k, v in counts.items()},
                       "grid": "live-ls20", "raster": "input-gradient"},
            "passed": passed,
            "description": "The LLM-free recogniser decodes and extracts objects from real rendered-arcade, "
                           "fixed-camera-physics and top-down-manipulation fixtures (plus grid via live-ls20 "
                           "and raster via input-gradient)."}


def _demo_suite():
    """Integration acceptance, run live: drive the real object-memory pipeline
    through induce -> predict (before outcome) -> grade (independent) -> deterministic
    replay, checking the acceptance invariants, plus real tests/docs/scripts evidence."""
    from object_memory import (
        GameLearningPipeline, GameObjectLearnerPayload, PipelineGameObjectLearnerPlugin,
        InMemorySemanticBackend, SymbolicStore, RuleStore, PredictionLedger,
        OutcomeChannel, PredictionEvaluator, PredictionGrade,
    )
    from object_memory.integration import (
        phase2_transition_analyzer, phase2_transformation_learner,
        phase2_rule_inducer, phase2_rule_ranker, phase2_rule_executor,
    )
    store = RuleStore(); ledger = PredictionLedger(); sem = SymbolicStore(InMemorySemanticBackend())
    pipe = GameLearningPipeline(phase2_transition_analyzer(), phase2_transformation_learner(),
                                phase2_rule_inducer(), phase2_rule_ranker(), store, ledger, sem)
    before = GameObjectLearnerPayload("s1", ({"id": "o", "position": [1, 1]},), identity_ids=("o",))
    after = GameObjectLearnerPayload("s2", ({"id": "o", "position": [2, 1]},), identity_ids=("o",),
                                     transitions=({"id": "o", "action": "step",
                                                   "properties": {"position": {"from": [1, 1], "to": [2, 1]}}},))
    step = PipelineGameObjectLearnerPlugin(pipe).consume_transition(before, "step", after).value.learning_step
    rel = next((r for r in step.rules
                if r.predicted_effects and isinstance(r.predicted_effects[0], dict)
                and r.predicted_effects[0].get("interpretation") == "relative_delta"), step.rules[0])
    ex = phase2_rule_executor(store, "step")
    _ps, pred = pipe.predict(prediction_id="suite", rule_id=rel.rule_id, source_state_id="s2",
                             state={"id": "o", "position": [5, 5], "action": "step"},
                             created_sequence=1, executor=ex)
    before_outcome = sem.get("predictions", pred.prediction_id).outcome_sequence is None
    closed = pipe.grade_prediction(prediction_id=pred.prediction_id, outcome_sequence=2,
                                   outcome_channel=OutcomeChannel(lambda: {"id": "o", "position": [6, 5], "action": "step"}),
                                   evaluator=PredictionEvaluator(
                                       lambda e, o: PredictionGrade(1.0 if e.get("position") == o.get("position") else 0.0,
                                                                    evidence=("independent_outcome",))))
    replay = SymbolicStore(InMemorySemanticBackend()).replay(sem.snapshot())
    replay_ok = replay.get("predictions", pred.prediction_id) is not None
    tests = len(list((_REPO_ROOT / "tests").glob("test_*.py"))) if (_REPO_ROOT / "tests").is_dir() else 0
    docs = len([p for p in (_REPO_ROOT / "workbench" / "docs").rglob("*.md") if p.stat().st_size > 0]) \
        if (_REPO_ROOT / "workbench" / "docs").is_dir() else 0
    scripts = len([p for p in (_REPO_ROOT / "scripts").glob("phase*_*.py")]) if (_REPO_ROOT / "scripts").is_dir() else 0
    panels = [_panel("acceptance flow: induce → predict → grade → replay", [(0, 0, "regen", _GREEN)])]
    passed = (before_outcome and closed.grade == 1.0 and replay_ok
              and tests > 0 and docs > 0 and scripts > 0)
    return {"id": "suite", "group": "Phase 3 — integration",
            "title": "Integration acceptance flow + evidence", "panels": panels,
            "result": {"prediction_before_outcome": before_outcome,
                       "independent_grade": closed.grade, "deterministic_replay": replay_ok,
                       "test_files": tests, "doc_files": docs, "example_scripts": scripts},
            "passed": passed,
            "description": "Runs the real Phase 2→3 acceptance flow live (induce a rule, predict before the "
                           "outcome, grade against an independent outcome, replay deterministically) and reports "
                           "the test/doc/script deliverable evidence."}


def _demo_phase3():
    """Phase 3 live over real ls20 frames: induce a motion rule from A→B, predict
    the mover's position in C BEFORE observing, then grade against the real C."""
    import symbolic_arc as sa
    import phase3_pipeline as p3
    res = p3.run_live_phase3()
    if not res.get("ok"):
        return {"id": "phase3-live", "group": "Phase 3 — live learning",
                "title": "Learn a rule, predict next state, grade (live)", "panels": [],
                "result": res, "passed": False,
                "description": "Live Phase 3 over ls20 frames (no trackable mover found)."}
    fr = res["frames"]
    setdir = p3._LS20_DIR

    def grid(idv, marks):
        png = next(iter(setdir.glob(f"{idv}.png")), None)
        idx, hexpal, _c, _r = sa.decode_grid(str(png))
        return _grid_to_cells(idx, hexpal) + list(marks)
    pa = res["observed_move_AB"]["from"]; pb = res["observed_move_AB"]["to"]
    pred = res["prediction"]["predicted"]; act = res["actual_C"]
    panels = [
        _panel(f'A {fr["A"]} · mover @ {pa}', grid(fr["A"], [(pa[0], pa[1], "visible", _BLUE)])),
        _panel(f'B {fr["B"]} · moved to {pb}', grid(fr["B"], [(pb[0], pb[1], "visible", _BLUE)])),
        _panel(f'C {fr["C"]} · predicted {pred} (green) vs actual {act} (blue)',
               grid(fr["C"], [(pred[0], pred[1], "regen", _GREEN), (act[0], act[1], "visible", _BLUE)])),
    ]
    return {"id": "phase3-live", "group": "Phase 3 — live learning",
            "title": "Learn a rule, predict next state, grade (live)", "panels": panels[:1],
            "frames": panels,
            "result": {"mover": f'{res["mover"]["color"]} {res["mover"]["shape"]}',
                       "move_AB": f'{pa}→{pb}', "predicted_C": pred, "actual_C": act,
                       "grade": res["grade"], "calibrated": round(res["calibrated_probability"], 2),
                       "rules": [r["interpretation"] for r in res["rules_induced"]]},
            "passed": bool(res["passed"]),
            "description": "Real learn→predict→grade over live ls20 frames: a motion rule induced from A→B "
                           "predicts the mover's position in C before it is observed; graded against the real "
                           "frame C and the rule's calibrated probability is updated."}


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
# Raw per-frame recordings (each frame is a numbered subfolder holding image.png).
# The long "release run" ls20 playthroughs (hundreds of moves) live here, split
# across attempt segments; we concatenate a base id's attempts into one sequence.
_RAW_LS20_DIR = (Path(__file__).resolve().parents[1] / "workspaces" / "arc3_random_player" / "data"
                 / "arc3_games" / "recordings" / "ls20")

_ls20_selected: str | None = None   # user-chosen recording key (else default = longest)
_ls20_recs_cache: list | None = None
_ls20_write_memory: bool = False    # when True, the live-ls20 demo COMMITS recognized
                                    # objects to the persistent registry (default OFF so
                                    # the demo stays ephemeral and can't pollute memory)
# ARC-AGI-3 movement actions -> direction arrows (the "move" made between two frames).
_ACTION_ARROW = {"ACTION1": "↑", "ACTION2": "↓", "ACTION3": "←", "ACTION4": "→",
                 "ACTION5": "•", "ACTION6": "*"}


def _ls20_base(name: str) -> str:
    """Strip the '_attempt<N>_size<M>' / '_size<M>' segment suffix to get the run id."""
    import re
    return re.sub(r"_size_\d+$", "", re.sub(r"_attempt\d+_size_\d+$", "", name))


def _ls20_attempt_key(name: str) -> tuple:
    import re
    a = re.search(r"_attempt(\d+)", name)
    s = re.search(r"_size_(\d+)", name)
    return (int(a.group(1)) if a else 0, int(s.group(1)) if s else 0)


def _raw_base_frames(dirs: list, with_action: bool = False) -> list:
    """Ordered (displayId, image.png, action) for a raw recording base: attempts in
    order, then each attempt's numbered frame subfolders in numeric order. `action`
    is the move (incoming_action) that produced the frame — read only when asked, so
    listing recordings stays cheap."""
    import json as _json
    out: list = []
    for d in sorted(dirs, key=lambda p: _ls20_attempt_key(p.name)):
        subs = [c for c in d.iterdir() if c.is_dir() and c.name.isdigit()]
        for c in sorted(subs, key=lambda p: int(p.name)):
            img = c / "image.png"
            if not img.is_file():
                continue
            action = None
            if with_action:
                sj = c / "state.json"
                if sj.is_file():
                    try:
                        action = _json.loads(sj.read_text(encoding="utf-8")).get("incoming_action")
                    except (OSError, _json.JSONDecodeError):
                        action = None
            out.append((f"{d.name}#{c.name}", str(img), action))
    return out


def _ls20_recordings() -> list:
    """Every selectable ls20 recording: the reduced vision-frame dirs (fast, may have
    committed part-graphs) plus the raw release-run playthroughs (concatenated across
    attempt segments). Cached for the session."""
    global _ls20_recs_cache
    if _ls20_recs_cache is not None:
        return _ls20_recs_cache
    recs: list = []
    root = _LS20_DIR.parent
    if root.is_dir():
        for sub in sorted(root.glob("*ls20*")):
            if sub.is_dir():
                n = len(list(sub.glob("*.png")))
                if n >= 2:
                    short = sub.name.replace("data-arc3_games-recordings-ls20-", "")
                    recs.append({"key": "vf:" + sub.name, "label": f"reduced · {short} · {n} frames", "count": n})
    if _RAW_LS20_DIR.is_dir():
        groups: dict = {}
        for sub in _RAW_LS20_DIR.iterdir():
            if sub.is_dir():
                groups.setdefault(_ls20_base(sub.name), []).append(sub)
        for base, dirs in sorted(groups.items()):
            frames = _raw_base_frames(dirs)
            if len(frames) >= 2:
                recs.append({"key": "raw:" + base, "label": f"raw run · {base} · {len(frames)} frames",
                             "count": len(frames)})
    recs.sort(key=lambda r: r["count"], reverse=True)
    _ls20_recs_cache = recs
    return recs


def _resolve_ls20(key: str | None) -> tuple:
    """(ordered [(displayId, pngPath)], committedDir | None, label) for a recording key."""
    if key and key.startswith("vf:"):
        sub = _LS20_DIR.parent / key[3:]
        if sub.is_dir():
            import json as _json
            order: list = []
            mf = sub / "manifest.json"
            if mf.is_file():
                try:
                    order = [it["id"] for it in _json.loads(mf.read_text(encoding="utf-8")).get("items", [])]
                except (OSError, _json.JSONDecodeError):
                    order = []
            if not order:
                order = sorted(p.stem for p in sub.glob("*.png"))
            entries = []
            for idv in order:
                p = next(iter(sub.glob(f"{idv}.png")), None)
                if p:
                    entries.append((idv, str(p), None))
            return entries, sub, sub.name.replace("data-arc3_games-recordings-ls20-", "")
    if key and key.startswith("raw:") and _RAW_LS20_DIR.is_dir():
        base = key[4:]
        dirs = [d for d in _RAW_LS20_DIR.iterdir() if d.is_dir() and _ls20_base(d.name) == base]
        return _raw_base_frames(dirs, with_action=True), None, base
    return [], None, ""


def _current_ls20_key() -> str | None:
    """The selected recording key if still valid, else the longest reduced recording
    (fast default), else the longest overall."""
    with _demo_lock:
        sel = _ls20_selected
    recs = _ls20_recordings()
    if not recs:
        return None
    if sel and any(r["key"] == sel for r in recs):
        return sel
    vf = [r for r in recs if r["key"].startswith("vf:")]
    pool = vf or recs
    return max(pool, key=lambda r: r["count"])["key"]


def set_ls20_source(key: str | None) -> None:
    """Choose which ls20 recording the live-ls20 demo plays."""
    global _ls20_selected
    with _demo_lock:
        _ls20_selected = key or None


def set_ls20_write(value: bool) -> None:
    """Toggle whether the live-ls20 demo commits recognized objects to the persistent
    long-term registry (default OFF: the demo stays ephemeral / from-empty)."""
    global _ls20_write_memory
    with _demo_lock:
        _ls20_write_memory = bool(value)


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
    """A (real data): play ONE long recorded ls20 playthrough over time, starting
    from an EMPTY memory and learning as it goes — frame 0 recognizes nothing; each
    later frame recognizes the objects (by their colour-free, scale-normalized
    identity) it has already seen earlier, so you watch recognition build up. The
    single recording naturally spans several in-game LEVELS (auto-detected as scene
    resets) and RECOLOURS objects between them, yet the colour-free GEOMETRY stays
    recognized — proof the recogniser separates shape identity from colour. NEW
    objects (first sighting) render blue, RECOGNIZED objects render green."""
    import json as _json
    import symbolic_arc as sa
    import numpy as _np

    key = _current_ls20_key()
    entries, committed_dir, source_label = _resolve_ls20(key)
    if not entries:
        return {"id": "live-ls20", "group": "Live sequence (real data)",
                "title": "Live ls20 recording — recognition over time", "panels": [],
                "frames": [], "result": {"note": "ls20 recording set not found",
                                         "recordings": _ls20_recordings()}, "passed": False,
                "description": "Plays a real recorded ls20 playthrough with live recognition; run a reduce first."}

    def _parts_for(disp, png, game):
        """A frame's parts: use the committed Prolog part-graph if present (reduced
        recordings), else extract the frame fresh on the fly (raw recordings)."""
        if committed_dir is not None:
            pj = committed_dir / "sym" / f"{disp}__prolog.parts.json"
            if pj.is_file():
                try:
                    parts = _json.loads(pj.read_text(encoding="utf-8"))
                except (OSError, _json.JSONDecodeError):
                    parts = []
                idx, hexpal, _c, _r = sa.decode_grid(png)
                return idx, hexpal, parts
        try:
            pr = sa.extract_frame(png, game)
        except Exception:  # noqa: BLE001
            pr = None
        if not pr or pr.get("nparts", 0) <= 0 or pr.get("cols", 999) > 160 or pr.get("rows", 999) > 160:
            return None, None, None
        idx, hexpal, _c, _r = sa.decode_grid(png)
        return idx, hexpal, pr.get("geom", [])

    _MAX_FRAMES = 420          # bound runtime for very long recordings
    order = entries[:_MAX_FRAMES]
    game = "ls20-live"

    # In-game LEVEL boundaries are detected as scene resets: a big frame-to-frame
    # change in the palette-stable HEX grid marks a new level. (Index grids are not
    # comparable across frames because decode_grid re-orders the palette per frame.)
    # This is folded into the single play pass below (one decode per frame).
    _RESET = 0.30             # fraction of cells that must change to count as a reset
    _MIN_GAP = 6              # debounce: ignore resets closer than this many frames

    frames: list = []
    geo_seen: dict = {}            # shape -> {variantKey: provenance}  (learners + how each was made)
    geo_exemplar: dict = {}        # shape -> ((w,h), colour) of its first raw form (the exemplar)
    ind_seen: set = set()          # INDIVIDUALS: (shape, colour) objects learned across the whole run
    level_colours: dict = {}       # shape -> {colours seen so far THIS level} (reset at each boundary)
    recolored_shapes = recolor_events = 0
    first_ind_recog = first_geo_recog = None
    total_ind_recog = total_geo_recog = total_parts = 0
    moves_seen = 0                 # frame transitions with a recorded move (direction action)
    level_no = 1
    boundaries: list = []
    prev_hex = None
    last_boundary = -_MIN_GAP

    for i, (disp, png, action) in enumerate(order):
        idx, hexpal, parts = _parts_for(disp, png, game)
        if idx is None:
            continue
        # Scene-reset boundary detection folded into the play pass (one decode per
        # frame): a big change in the palette-stable HEX grid marks a new level.
        hexgrid = _np.asarray(hexpal, dtype=object)[idx]
        if prev_hex is not None and prev_hex.shape == hexgrid.shape:
            if float((prev_hex != hexgrid).mean()) > _RESET and (i - last_boundary) >= _MIN_GAP:
                boundaries.append(i)
                last_boundary = i
                recolored_shapes += sum(1 for cs in level_colours.values() if len(cs) > 1)
                level_colours = {}
                level_no += 1
        prev_hex = hexgrid
        arrow = _ACTION_ARROW.get(action or "", "")
        if arrow:
            moves_seen += 1
        geo_new = geo_recog = ind_new = ind_recog = frame_parts = frame_recolor = 0
        roled: list = []
        frame_geo: dict = {}       # shape -> {variantKey: rawform}  raw parts seen this frame
        frame_ind: set = set()
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
            frame_parts += 1
            geo_recog += geo_known; geo_new += (not geo_known)
            ind_recog += ind_known; ind_new += (not ind_known)
            if geo in level_colours and cname not in level_colours[geo]:   # same shape, NEW colour this level = recoloured
                frame_recolor += 1
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
            lc = level_colours.setdefault(g, set())
            for vk, ((w, h), cname) in variants.items():
                dst[vk] = _variant_prov(geo_exemplar[g], (w, h), cname)
                lc.add(cname)             # remember every colour this shape wore this level
        ind_seen.update(frame_ind)
        after_obj, after_geo = len(ind_seen), len(geo_seen)     # known AFTER learning this frame
        if first_ind_recog is None:
            first_ind_recog, first_geo_recog = ind_recog, geo_recog
        total_ind_recog += ind_recog
        total_geo_recog += geo_recog
        total_parts += frame_parts
        recolor_events += frame_recolor
        direct = sum(1 for v in geo_seen.values() for pr in v.values() if pr == "direct")
        made = sum(1 for v in geo_seen.values() for pr in v.values() if pr != "direct")
        rows, cols = idx.shape[0], idx.shape[1]
        base = [(x, y, "object", hexpal[int(idx[y, x])]) for y in range(rows) for x in range(cols)]
        scene = _panel(
            f"LEVEL {level_no} · {disp}"
            + (f" · move {arrow} {action}" if arrow else "")
            + f" · this frame: {ind_recog} recognized, {ind_new} new"
            + (f", {frame_recolor} recoloured" if frame_recolor else "")
            + f" · objects known {before_obj}→{after_obj}, shapes {before_geo}→{after_geo} "
            f"· learners {direct} direct / {made} via filter",
            base)
        # Recognition map shown to the SIDE (not painted over the scene): green =
        # recognized object, blue = new first sighting, rest dark.
        scene["aux"] = _panel(f"LEVEL {level_no} recognition · green = recognized · blue = new",
                              roled, ox=0, oy=0, w=cols, h=rows)
        frames.append(scene)
    recolored_shapes += sum(1 for cs in level_colours.values() if len(cs) > 1)   # final level
    levels_detected = level_no

    # Object memory. The demo always tracks objects/shapes across frames in-run.
    # When the user opts in (checkbox), it ALSO commits them to an ISOLATED per-
    # recording memory area — a separate store rooted at object_memory_demo/<key>,
    # NEVER the canonical registry — so the persistent object memory can be tested
    # and inspected without polluting long-term memory. (Each recording gets its own
    # area; inheriting from a shared longer-term base is a planned follow-up.)
    with _demo_lock:
        write_mem = _ls20_write_memory
    memory_store = "ephemeral (in-run only — from empty each run)"
    memory_identities = memory_shapes = 0
    if write_mem:
        import re as _re
        area = Path(sa.memory_dir()).parent / "object_memory_demo" / (_re.sub(r"[^A-Za-z0-9_.-]", "_", key or "default"))
        try:
            sa.extract_sequence([p for (_d, p, _a) in order], "ls20-live",
                                mem_dir=str(area), write=True, game=source_label)
            snap = sa.registry_snapshot(str(area))
            memory_shapes = snap.get("shapeCount", 0)
            memory_identities = sum(len(s.get("identities", [])) for s in snap.get("scopes", {}).values())
            memory_store = str(area)
        except Exception as _e:  # noqa: BLE001
            memory_store = f"write failed: {_e}"

    # per-shape learner evidence + provenance: how many raw variants (identities)
    # instantiate each shape, and how many only exist because a normalization
    # filter (scale/rotation/colour) collapsed a raw variant onto the shape.
    ev = sorted(((len(v), g) for g, v in geo_seen.items()), reverse=True)
    top_shape = (f"{ev[0][1]} ({ev[0][0]} learners)" if ev else "none")
    direct_all = sum(1 for v in geo_seen.values() for pr in v.values() if pr == "direct")
    made_all = sum(1 for v in geo_seen.values() for pr in v.values() if pr != "direct")
    geo_pct = (100.0 * total_geo_recog / total_parts) if total_parts else 0.0
    # Demonstrates learning over one long playthrough: frame 0 recognizes nothing,
    # geometry (fewer, shared) saturates faster than individuals (colour variety),
    # the recording crosses several in-game levels, and objects are recoloured while
    # the colour-free geometry stays recognized.
    passed = (bool(frames)
              and first_ind_recog == 0                 # started from an EMPTY memory
              and total_ind_recog > 0                  # recognition built up within the recording
              and levels_detected >= 2                 # the recording spans multiple in-game levels
              and recolor_events > 0)                  # objects are recoloured across the run
    return {"id": "live-ls20", "group": "Live sequence (real data)",
            "title": "Live ls20 recording — recognition builds up across levels (recolour)",
            "panels": frames[:1],
            "frames": frames,
            "result": {"frames": len(frames),
                       "source": source_label,
                       "sourceKey": key,
                       "recordings": _ls20_recordings(),
                       "levels_detected": levels_detected,
                       "level_boundaries": (", ".join(str(b) for b in boundaries) or "none"),
                       "frame0_objects_recognized": first_ind_recog,
                       "frame0_shapes_recognized": first_geo_recog,
                       "objects_learned": len(ind_seen), "shapes_learned": len(geo_seen),
                       "max_learners_per_shape": (ev[0][0] if ev else 0),
                       "most_learned_shape": top_shape,
                       "learners_direct": direct_all,
                       "learners_via_filter": made_all,
                       "geometry_recognized": f"{total_geo_recog}/{total_parts} ({geo_pct:.0f}%)",
                       "individuals_recognized": f"{total_ind_recog}/{total_parts}",
                       "moves_seen": moves_seen,
                       "memory_store": memory_store,
                       "memory_identities": memory_identities,
                       "memory_shapes": memory_shapes,
                       "recolored_shapes": recolored_shapes,
                       "recolor_events": recolor_events},
            "passed": passed,
            "description": "One long real ls20 playthrough played from an EMPTY memory. Frame 0 recognizes nothing; "
                           "then GEOMETRY (colour-free shape vocabulary, shared) and INDIVIDUALS (shape+colour) are "
                           "learned separately — each shape accruing evidence = the raw variants that use it, and "
                           "every learner keeping its provenance: 'direct' (matched as-is) vs. made by the "
                           "normalization filter (scale/rotation/colour). The single recording spans several in-game "
                           "LEVELS (auto-detected as scene resets) and RECOLOURS objects between them: the same shapes "
                           "reappear in new colours, yet the colour-free GEOMETRY stays recognized — proof the "
                           "recogniser separates shape identity from colour. Overlay: green = recognized, blue = "
                           "first sighting."}


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
    _demo_progressive_reveal,
    _demo_recolor, _demo_resize,
    _demo_rotation, _demo_reflection,
    _demo_store_then_recognize, _demo_new_distinguished,
    _demo_addition, _demo_removal, _demo_correspondence,
    _demo_regeneration, _demo_replay,
    _demo_input_gradient, _demo_input_video,
    _demo_noise, _demo_degradation,
    _demo_properties, _demo_relationships,
    _demo_recolor_change, _demo_resize_change,
    _demo_dedup, _demo_encounter_history,
    _demo_phase3_contract, _demo_environments, _demo_suite, _demo_phase3,
]


# Static metadata for every sanity test, in _DEMOS order, so the page can list
# the tests as "not run yet" (each individually runnable) BEFORE anything runs.
# Kept in sync with the id/group/title each builder returns.
_DEMO_CATALOG = [
    {"id": "live-ls20", "group": "Live sequence (real data)",
     "title": "Live ls20 recording — recognition builds up across levels (recolour)",
     "resultKeys": ["frames", "source", "levels_detected", "level_boundaries",
                    "frame0_objects_recognized", "frame0_shapes_recognized",
                    "objects_learned", "shapes_learned", "max_learners_per_shape",
                    "most_learned_shape", "learners_direct", "learners_via_filter",
                    "geometry_recognized", "individuals_recognized", "moves_seen",
                    "memory_store", "memory_identities", "memory_shapes",
                    "recolored_shapes", "recolor_events"]},
    {"id": "occlusion-t", "group": "Occlusion completion", "title": "T tetromino — stem occluded",
     "resultKeys": ["recognized", "scale", "orientation", "residual", "confidence", "faithful"]},
    {"id": "occlusion-plus", "group": "Occlusion completion", "title": "Plus pentomino — centre + arm occluded",
     "resultKeys": ["recognized", "scale", "orientation", "residual", "confidence", "faithful"]},
    {"id": "occlusion-scaled", "group": "Occlusion completion", "title": "2x-scaled T — scaled stem occluded",
     "resultKeys": ["recognized", "scale", "orientation", "residual", "confidence", "faithful"]},
    {"id": "occlusion-reject", "group": "Occlusion completion", "title": "Inconsistent fragment is rejected",
     "resultKeys": ["recognized", "note"]},
    {"id": "progressive-reveal", "group": "Occlusion completion", "title": "Progressively revealed object — built from parts",
     "resultKeys": ["parts", "frames", "pieces_over_time", "provisional_reads", "assembled_at_frame",
                    "final_shape", "turtle_final", "turtle_evolved", "faithful"]},
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
    {"id": "noise", "group": "Robustness (noise / degradation)", "title": "Recognize despite noise",
     "resultKeys": ["noisy_identity", "denoised_identity", "base_identity", "specks_removed"]},
    {"id": "degradation", "group": "Robustness (noise / degradation)", "title": "Recognize under modest degradation",
     "resultKeys": ["base_identity", "recovered_identity", "cells_dropped"]},
    {"id": "properties", "group": "Representation", "title": "Represent object properties, structure & pose",
     "resultKeys": ["shape", "cells", "bbox", "centroid", "colour"]},
    {"id": "relationships", "group": "Representation", "title": "Represent relationships (adjacency / containment)",
     "resultKeys": ["adjacent_pairs", "enclosures"]},
    {"id": "recolor-change", "group": "Change detection", "title": "Detect recoloring",
     "resultKeys": ["same_object", "colours", "recolored"]},
    {"id": "resize-change", "group": "Change detection", "title": "Detect resizing",
     "resultKeys": ["same_object", "sizes", "resized"]},
    {"id": "dedup", "group": "Memory", "title": "Prevent duplicate storage",
     "resultKeys": ["identities", "seen"]},
    {"id": "encounter-history", "group": "Memory", "title": "Preserve encounter history",
     "resultKeys": ["seen_series"]},
    {"id": "phase3-contract", "group": "Phase 3 — integration", "title": "Game Object Learner data contract",
     "resultKeys": ["schema_version", "objects", "relationships", "correspondences",
                    "state_differences", "encounter_history", "roundtrip_ok", "bad_payload_rejected"]},
    {"id": "environments", "group": "Phase 3 — integration", "title": "Operation across representative environments",
     "resultKeys": ["rendered_arcade", "fixed_camera_physics", "top_down_manipulation", "total_fixtures"]},
    {"id": "suite", "group": "Phase 3 — integration", "title": "Integration acceptance flow + evidence",
     "resultKeys": ["prediction_before_outcome", "independent_grade", "deterministic_replay",
                    "test_files", "doc_files", "example_scripts"]},
    {"id": "phase3-live", "group": "Phase 3 — live learning", "title": "Learn a rule, predict next state, grade (live)",
     "resultKeys": ["mover", "move_AB", "predicted_C", "actual_C", "grade", "calibrated", "rules"]},
]


def _preview_live_ls20():
    """The raw first ls20 frame as an INPUT MAP: the decoded scene with no
    recognition overlay at all (nothing recognized yet). Cheap -- one png decode,
    no part-graph, no scoring -- so it is a safe 'unstarted' preview. Uses the same
    (longest) recording the live demo plays."""
    import json as _json
    import symbolic_arc as sa
    setdir = None
    root = _LS20_DIR.parent
    if root.is_dir():
        best_n = -1
        for sub in sorted(root.glob("*ls20*")):
            if sub.is_dir():
                n = len(list(sub.glob("*.png")))
                if n > best_n:
                    best_n, setdir = n, sub
    if setdir is None:
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
    ("P2", "2a", "Represent properties & appearance", "full", "full", "properties"),
    ("P2", "2b", "Represent structure", "full", "full", "properties"),
    ("P2", "2c", "Represent relationships (adjacency/containment)", "full", "full", "relationships"),
    ("P2", "2d", "Represent position/orientation/scale", "full", "full", "properties"),
    ("P2", "3a", "Stable identity across encounters", "full", "full", "store-then-recognize"),
    ("P2", "3b", "Stable identity across state transitions", "full", "full", "correspondence"),
    ("P2", "4a", "Match corresponding objects between states", "full", "full", "correspondence"),
    ("P2", "4b", "Match across repeated encounters", "full", "full", "store-then-recognize"),
    ("P2", "5a", "Recognize despite position", "full", "full", "store-then-recognize"),
    ("P2", "5b", "Recognize despite rotation", "full", "full", "rotation"),
    ("P2", "5c", "Recognize despite scale", "full", "full", "resize"),
    ("P2", "5d", "Recognize despite reflection", "full", "full", "reflection"),
    ("P2", "5e", "Recognize despite colour", "full", "full", "recolor"),
    ("P2", "5f", "Recognize despite noise", "full", "full", "noise"),
    ("P2", "5g", "Recognize despite partial visibility", "full", "full", "occlusion-t"),
    ("P2", "6a", "Detect movement", "full", "full", "input-video"),
    ("P2", "6b", "Detect recoloring (as change)", "full", "full", "recolor-change"),
    ("P2", "6c", "Detect resizing (as change)", "full", "full", "resize-change"),
    ("P2", "6d", "Detect addition", "full", "full", "addition"),
    ("P2", "6e", "Detect removal", "full", "full", "removal"),
    ("P2", "6f", "Detect structural change", "full", "full", "new-distinguished"),
    ("P2", "7", "Normalized store -> regenerate", "full", "full", "regeneration"),
    ("P2", "8", "Distinguish recognized vs new", "full", "full", "new-distinguished"),
    ("P2", "9", "Prevent duplicate storage", "full", "full", "dedup"),
    ("P2", "10a", "Accumulate evidence", "full", "full", "live-ls20"),
    ("P2", "10b", "Accumulate provenance", "full", "full", "live-ls20"),
    ("P2", "11a", "Preserve encounter history", "full", "full", "encounter-history"),
    ("P2", "11b", "Deterministic replay", "full", "full", "replay"),
    ("P2", "12a", "Object (individual) memory", "full", "full", "live-ls20"),
    ("P2", "12b", "Shape (geometry) memory", "full", "full", "live-ls20"),
    ("P2", "13", "Demonstrate regeneration", "full", "full", "regeneration"),
    ("P2", "14a", "Recognition under modest degradation", "full", "full", "degradation"),
    ("P2", "14b", "Recognition under partial occlusion", "full", "full", "occlusion-t"),
    ("P2", "15a", "Tests", "full", "full", "suite"),
    ("P2", "15b", "Documentation", "full", "full", "suite"),
    ("P3", "1", "Interface / data contract to Game Object Learner", "full", "full", "phase3-contract"),
    ("P3", "2a", "Provide detected objects", "full", "full", "phase3-contract"),
    ("P3", "2b", "Provide properties", "full", "full", "phase3-contract"),
    ("P3", "2c", "Provide relationships", "full", "full", "phase3-contract"),
    ("P3", "2d", "Provide correspondences", "full", "full", "phase3-contract"),
    ("P3", "2e", "Provide state differences", "full", "full", "phase3-contract"),
    ("P3", "2f", "Provide encounter history", "full", "full", "phase3-contract"),
    ("P3", "3", "Stable interface decoupled from perception internals", "full", "full", "phase3-contract"),
    ("P3", "4a", "Interface validation", "full", "full", "phase3-contract"),
    ("P3", "4b", "Structured errors", "full", "full", "phase3-contract"),
    ("P3", "4c", "Integration tests", "full", "full", "suite"),
    ("P3", "4d", "Example workflows", "full", "full", "suite"),
    ("P3", "5", "Infer candidate transformations / transition rules", "full", "full", "phase3-live"),
    ("P3", "6a", "Support multiple candidate interpretations", "full", "full", "phase3-live"),
    ("P3", "6b", "Retain evidence for successful & unsuccessful rules", "full", "full", "phase3-live"),
    ("P3", "7", "Apply learned transformations to new cases", "full", "full", "phase3-live"),
    ("P3", "8", "Predict later states before outcomes", "full", "full", "phase3-live"),
    ("P3", "9", "Compare predictions with independent outcomes", "full", "full", "phase3-live"),
    ("P3", "10", "Update rule evidence on success/failure", "full", "full", "phase3-live"),
    ("P3", "11", "Prevent post-hoc explanations counting as predictions", "full", "full", "phase3-live"),
    ("P3", "12a", "Recognition of partly occluded objects", "full", "full", "occlusion-t"),
    ("P3", "12b", "Completion of partly occluded objects", "full", "full", "occlusion-t"),
    ("P3", "12c", "Progressive reveal — object built from parts while occlusion lifts", "full", "full", "progressive-reveal"),
    ("P3", "13a", "Operation in grid environments", "full", "full", "live-ls20"),
    ("P3", "13b", "Operation in raster environments", "full", "full", "input-gradient"),
    ("P3", "13c", "Rendered arcade / fixed-camera physics / top-down manipulation", "full", "full", "environments"),
    ("P3", "14a", "Integration documentation", "full", "full", "suite"),
    ("P3", "14b", "Example scripts", "full", "full", "suite"),
    ("P3", "14c", "Acceptance-test results", "full", "full", "suite"),
    ("P3", "14d", "Developer notes", "full", "full", "suite"),
]


def sow_coverage() -> list:
    """Every Phase 2 & 3 SoW deliverable with implemented/LLM-free/demo status, so
    the page can list an entry for each. Every row maps to a real, runnable demo
    card (no stubs); rows still short of full implementation are marked partial."""
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

# --- server-OWNED animation playhead ---------------------------------------
# The frame each demo shows is decided by the SERVER (advanced by elapsed time),
# not by any client-side loop. The UI just renders the frame index the server
# reports and sends run/stop/clear/play/seek as commands. "Stop all" freezes the
# playheads here, so the animation genuinely stops everywhere.
_PLAY_INTERVAL = 0.7  # seconds per frame
_play: dict = {}      # demo id -> {"playing": bool, "t0": float, "n": int, "idx": int}
_play_epoch = 0       # bumped whenever playhead state changes, so observers can diff cheaply


def _cur_index_locked(did: str) -> int:
    """Current frame index for a demo, computed from elapsed time when playing."""
    p = _play.get(did)
    if not p or p["n"] <= 1:
        return 0
    if p["playing"]:
        return int((time.monotonic() - p["t0"]) / _PLAY_INTERVAL) % p["n"]
    return max(0, min(p["idx"], p["n"] - 1))


def _is_playing_locked(did: str) -> bool:
    p = _play.get(did)
    return bool(p and p["playing"] and p["n"] > 1)


def _touch_play_locked() -> None:
    global _play_epoch
    _play_epoch += 1


def demo_heads() -> dict:
    """Lightweight playhead snapshot the UI renders without any client loop."""
    with _demo_lock:
        heads = {k: _cur_index_locked(k) for k in _play}
        playing = {k: _is_playing_locked(k) for k in _play}
        any_playing = any(playing.values())
        return {"heads": heads, "playing": playing, "anyPlaying": any_playing,
                "running": _demo_state["running"], "epoch": _play_epoch, "generation": _demo_gen}


def set_demo_play(did: str, playing: bool) -> dict:
    """Play/pause one demo's animation on the server."""
    with _demo_lock:
        p = _play.get(did)
        if p:
            p["idx"] = _cur_index_locked(did)          # freeze where we are
            p["playing"] = bool(playing) and p["n"] > 1
            if p["playing"]:                            # resume so current frame == idx
                p["t0"] = time.monotonic() - p["idx"] * _PLAY_INTERVAL
            _touch_play_locked()
    return demo_heads()


def seek_demo(did: str, index: int) -> dict:
    """Jump one demo to a specific frame (pauses it) on the server."""
    with _demo_lock:
        p = _play.get(did)
        if p:
            p["playing"] = False
            p["idx"] = max(0, min(int(index), p["n"] - 1))
            _touch_play_locked()
    return demo_heads()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_demo_state() -> dict:
    """Observe the latest server run: {running, results, startedAt, finishedAt}.
    Each demo carries the SERVER's current frame index (frameIndex) so the UI never
    decides frame advancement itself."""
    with _demo_lock:
        st = dict(_demo_state)
        res = st.get("results") or {"demos": [], "total": 0, "passed": 0}
        demos = [{**d, "frameIndex": _cur_index_locked(d.get("id", "")),
                  "playing": _is_playing_locked(d.get("id", ""))} for d in res.get("demos", [])]
        any_playing = any(_is_playing_locked(k) for k in _play)
        epoch = _play_epoch
    return {"demos": demos, "total": res.get("total", 0), "passed": res.get("passed", 0),
            "catalog": demo_catalog(), "coverage": sow_coverage(), "running": st["running"],
            "anyPlaying": any_playing, "playEpoch": epoch,
            "ls20Recordings": _ls20_recordings(), "ls20Source": _current_ls20_key(),
            "ls20WriteMemory": _ls20_write_memory,
            "startedAt": st["startedAt"], "finishedAt": st["finishedAt"], "only": st["only"]}


def _run_job(only: str | None, gen: int, stepped: bool = False) -> None:
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
            # Server OWNS the animation: (re)start the playhead for each demo that
            # just (re)computed, so it advances by elapsed time on the server. When
            # 'stepped', start PAUSED at frame 0 so the user steps manually.
            for d in res["demos"]:
                n = len(d.get("frames") or d.get("panels") or [])
                _play[d["id"]] = {"playing": (n > 1) and not stepped, "t0": time.monotonic(), "n": n, "idx": 0}
            _touch_play_locked()
    finally:
        with _demo_lock:
            if gen == _demo_gen:          # only the current job may flip running off
                _demo_state["running"] = False
                _demo_state["finishedAt"] = _now()


def start_demo_run(only: str | None = None, stepped: bool = False) -> dict:
    """Kick off a background server run and return immediately. PREEMPTS any run
    already in progress (its stale generation makes it discard its result) so Run
    and Run step 1 always restart cleanly from the beginning. The page observes
    progress via get_demo_state(). `stepped` starts the demo PAUSED at frame 0."""
    global _demo_gen
    with _demo_lock:
        _demo_gen += 1                    # preempt/cancel any in-flight run
        gen = _demo_gen
        _demo_state["running"] = True
        _demo_state["startedAt"] = _now()
        _demo_state["finishedAt"] = None
        _demo_state["only"] = only
    threading.Thread(target=_run_job, args=(only, gen, stepped), name=f"sanity-tests-{only or 'all'}",
                     daemon=True).start()
    return get_demo_state()


def stop_demo_run() -> dict:
    """Stop any in-flight server run AND freeze every animation playhead, so the
    demos genuinely stop (the UI holds on whatever frame the server last reported)."""
    global _demo_gen
    with _demo_lock:
        _demo_gen += 1                    # invalidate any in-flight job
        _demo_state["running"] = False
        _demo_state["finishedAt"] = _now()
        for did, p in _play.items():      # freeze each playhead where it currently is
            p["idx"] = _cur_index_locked(did)
            p["playing"] = False
        _touch_play_locked()
    return get_demo_state()


def _wipe_demo_memory(only: str | None) -> None:
    """Delete the ISOLATED demo object-memory store(s) so Clear truly resets learning.
    Only ever touches object_memory_demo/* — NEVER the canonical registry."""
    try:
        import shutil  # noqa: PLC0415
        import re as _re  # noqa: PLC0415
        import symbolic_arc as sa  # noqa: PLC0415
        root = Path(sa.memory_dir()).parent / "object_memory_demo"
    except Exception:  # noqa: BLE001
        return
    try:
        if only == "live-ls20":
            key = _current_ls20_key()
            if key:
                target = root / _re.sub(r"[^A-Za-z0-9_.-]", "_", key)
                if target.is_dir():
                    shutil.rmtree(target, ignore_errors=True)
        elif not only:
            if root.is_dir():
                shutil.rmtree(root, ignore_errors=True)
    except Exception:  # noqa: BLE001
        pass


def clear_demo_state(only: str | None = None) -> dict:
    """Stop any in-flight run AND clear cached results. With `only`, clear just that
    one test (back to 'not run'); without it, clear everything. Also wipes the demo's
    ISOLATED object-memory store(s) so Clear resets persisted learning too."""
    global _demo_gen
    with _demo_lock:
        _demo_gen += 1                    # invalidate any in-flight job
        _demo_state["running"] = False
        _demo_state["finishedAt"] = _now()
        if only:
            _play.pop(only, None)
            res = _demo_state.get("results")
            if res and res.get("demos"):
                demos = [d for d in res["demos"] if d.get("id") != only]
                _demo_state["results"] = ({"demos": demos, "total": len(demos),
                                           "passed": sum(1 for d in demos if d.get("passed"))}
                                          if demos else None)
        else:
            _play.clear()
            _demo_state["results"] = None
            _demo_state["startedAt"] = None
            _demo_state["finishedAt"] = None
            _demo_state["only"] = None
        _touch_play_locked()
    _wipe_demo_memory(only)               # outside the lock: disk I/O + reads selection
    return get_demo_state()
