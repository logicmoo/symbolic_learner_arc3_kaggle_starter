"""Phase-2 acceptance tests for the symbolic_arc recognizer line: faithful
REGENERATION from the stored form, deterministic REPLAY, and the end-to-end
RECOGNITION demo (store an object, then recognize it as the same object on a
later encounter under position / reflection / colour change, without minting a
duplicate)."""
import sys
from pathlib import Path

_SERVER = Path(__file__).resolve().parents[1] / "workbench" / "server" / "generative_vision" / "prolog"
sys.path.insert(0, str(_SERVER))

import symbolic_arc as sa  # noqa: E402


def _turtle_to_cells(turtle: dict) -> set:
    """Invert a _poly_turtle program back to unit cells (each cell is one scaled
    rectangle), so we can check a stored form regenerates its exact shape."""
    rects = [c for c in turtle.get("commands", []) if c.get("op") == "rectangle" and c.get("box")]
    if not rects:
        return set()
    # cell size = the (uniform) rectangle edge length in the 0..1000 box.
    cs = min(b["box"][2] - b["box"][0] for b in rects)
    return {(round(b["box"][0] / cs), round(b["box"][1] / cs)) for b in rects}


def _frame(color, off, cx=5, cy=5, pid="p"):
    sig = sa._shape_key((None, sa._canon_br([tuple(c) for c in off])))
    return {"metta": "", "geom": [{"id": pid, "sig": sig, "color": color,
                                   "off": [list(c) for c in off], "cx": cx, "cy": cy}]}


# --- regeneration -----------------------------------------------------------

def test_stored_form_regenerates_its_exact_shape(tmp_path):
    """Every vocabulary shape's stored turtle program regenerates its exact
    normalized cells (faithful/exact on clean discrete grids)."""
    snap = sa.registry_snapshot(str(tmp_path), include_turtles=True)
    checked = 0
    for s in snap["shapes"]:
        if s["size"] > 8 or not s.get("turtle"):
            continue
        want = {(int(x), int(y)) for x, y in s["cells"]}
        got = _turtle_to_cells(s["turtle"])
        # both are translation-normalized unit-cell sets; compare up to translation.
        def _norm(cs):
            mx = min(x for x, _ in cs); my = min(y for _, y in cs)
            return {(x - mx, y - my) for x, y in cs}
        assert _norm(got) == _norm(want), s["name"]
        checked += 1
    assert checked > 5


# --- replay / determinism ---------------------------------------------------

def test_replay_same_input_same_identity_and_form(tmp_path):
    """Same input yields the same committed identity keys and the same canonical
    form (metta) on repeated runs."""
    L = [(0, 0), (0, 1), (0, 2), (1, 2)]
    a = _frame("#c80000", L)
    b = _frame("#c80000", L)
    sa.remember_objects([a], "g-1", str(tmp_path / "A"), write=True)
    sa.remember_objects([b], "g-1", str(tmp_path / "B"), write=True)
    assert a["geom"][0]["globalId"] == b["geom"][0]["globalId"]
    assert a["metta"] == b["metta"]


def test_replay_identity_is_colour_and_position_free(tmp_path):
    """The committed identity handle is stable regardless of colour or position
    (identity rests on the normalized form, not a query-time matcher)."""
    L = [(0, 0), (0, 1), (0, 2), (1, 2)]
    a = _frame("#c80000", L, cx=5, cy=5)
    b = _frame("#0000ff", L, cx=40, cy=22)
    sa.remember_objects([a], "g-1", str(tmp_path / "A"), write=True)
    sa.remember_objects([b], "g-1", str(tmp_path / "B"), write=True)
    assert a["geom"][0]["globalId"] == b["geom"][0]["globalId"]


# --- recognition demo (store -> later recognize as same object) --------------

def test_recognition_demo_recognizes_same_object_later(tmp_path):
    """Demonstration-workflow tail: store an object, then on a later encounter
    (moved, reflected, recoloured) recognize it as the SAME object — evidence
    accrues and no duplicate is minted."""
    mem = str(tmp_path)
    L = [(0, 0), (0, 1), (0, 2), (1, 2)]
    sa.remember_objects([_frame("#c80000", L, cx=5, cy=5)], "game-1", mem, write=True)
    reflected = [(1 - x, y) for (x, y) in L]           # reflection (same free polyomino)
    later = _frame("#00a000", reflected, cx=30, cy=12)  # moved + reflected + recoloured
    sa.remember_objects([later], "game-2", mem, write=True)   # same game scope
    p = later["geom"][0]
    assert p["memNew"] is False        # recognized, not new
    assert p["memSeen"] == 2           # evidence accumulated across encounters
    ids = sa.registry_snapshot(mem)["scopes"]["game"]["identities"]
    assert len(ids) == 1               # duplicate storage prevented


def test_recognition_demo_new_object_is_distinguished(tmp_path):
    """A genuinely new structure is committed as new, distinct from the held one."""
    mem = str(tmp_path)
    L = [(0, 0), (0, 1), (0, 2), (1, 2)]                # tetromino_L
    T = [(0, 0), (1, 0), (2, 0), (1, 1)]                # tetromino_T (different shape)
    sa.remember_objects([_frame("#c80000", L)], "game-1", mem, write=True)
    fr = _frame("#c80000", T)
    sa.remember_objects([fr], "game-2", mem, write=True)
    assert fr["geom"][0]["memNew"] is True             # new structure distinguished
    ids = sa.registry_snapshot(mem)["scopes"]["game"]["identities"]
    assert len(ids) == 2
