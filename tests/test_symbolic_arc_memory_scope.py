"""Cross-encounter object-memory tests for the symbolic_arc recognizer (Phase 2
gaps #1/#3/#6): identity is recognized across a game's LEVELS, kept separate
across GAMES by default, and shareable across games on request."""
import sys
from pathlib import Path

_SERVER = Path(__file__).resolve().parents[1] / "workbench" / "server" / "generative_vision" / "prolog"
sys.path.insert(0, str(_SERVER))

import symbolic_arc as sa  # noqa: E402

_OFF = [(0, 0), (1, 0), (0, 1), (1, 1)]  # tetromino_O
_SIG = sa._shape_key((None, sa._canon_br(_OFF)))


def _frame():
    return {"metta": "", "geom": [{"id": "part_red_1", "sig": _SIG, "color": "#c80000",
                                    "off": [list(c) for c in _OFF], "cx": 5, "cy": 5}]}


def _seen(mem, char, **kw):
    sa.remember_objects([_frame()], char, str(mem), **kw)
    snap = sa.registry_snapshot(str(mem))
    scope = sa.identity_scope(kw.get("game") or sa._game_of(char), kw.get("cross_game"))
    ids = snap["scopes"].get(scope, {}).get("identities", [])
    return ids[0]["seen"] if ids else 0


def test_game_key_derivation():
    assert sa._game_of("ls20-saved_001") == "ls20"
    assert sa._game_of("ls20-saved_002") == "ls20"
    assert sa._game_of("sonic_level_3") == "sonic"


def test_identity_recognized_across_levels_of_a_game(tmp_path):
    assert _seen(tmp_path, "ls20-saved_001") == 1     # first level: new
    assert _seen(tmp_path, "ls20-saved_002") == 2     # next level, same game: recognized


def test_identity_separate_across_games_by_default(tmp_path):
    _seen(tmp_path, "ls20-saved_001")
    assert _seen(tmp_path, "sonic-saved_001") == 1    # different game: its own scope
    snap = sa.registry_snapshot(str(tmp_path))
    assert {"ls20", "sonic"} <= set(snap["scopes"])


def test_cross_game_option_shares_one_scope(tmp_path):
    assert _seen(tmp_path, "ls20-saved_001", cross_game=True) == 1
    assert _seen(tmp_path, "sonic-saved_001", cross_game=True) == 2  # shared _all_games_
    snap = sa.registry_snapshot(str(tmp_path))
    assert "_all_games_" in snap["scopes"]


def test_registry_snapshot_has_shape_vocabulary(tmp_path):
    _seen(tmp_path, "ls20-saved_001")
    snap = sa.registry_snapshot(str(tmp_path))
    assert snap["shapeCount"] > 500
    names = {s["name"] for s in snap["shapes"]}
    assert {"tetromino_O", "empty_box", "empty_rectangle"} <= names


def _scope_seen(mem, char, **kw):
    snap = sa.registry_snapshot(str(mem))
    scope = sa.identity_scope(kw.get("game") or sa._game_of(char), kw.get("cross_game"))
    ids = snap["scopes"].get(scope, {}).get("identities", [])
    return ids[0]["seen"] if ids else 0


def test_recognize_only_does_not_create_identities(tmp_path):
    # A recognize-only pass against an empty scope must NOT mint anything.
    fr = _frame()
    sa.recognize_objects([fr], "ls20-saved_001", str(tmp_path))
    assert _scope_seen(tmp_path, "ls20-saved_001") == 0
    p = fr["geom"][0]
    assert p.get("memNew") is True and p.get("memSeen") == 0
    assert "(memory" in fr["metta"]


def test_recognize_only_reports_prior_commit_without_bumping(tmp_path):
    # Commit once (write=True), then recognize-only twice: the stored count is
    # reported (seen 1, not new) and never incremented.
    assert _seen(tmp_path, "ls20-saved_001") == 1
    for _ in range(2):
        fr = _frame()
        sa.recognize_objects([fr], "ls20-saved_002", str(tmp_path))  # same game scope
        p = fr["geom"][0]
        assert p.get("memNew") is False and p.get("memSeen") == 1
    assert _scope_seen(tmp_path, "ls20-saved_001") == 1  # store unchanged


def test_commit_accumulates_across_encounters(tmp_path):
    assert _seen(tmp_path, "ls20-saved_001") == 1
    assert _seen(tmp_path, "ls20-saved_002") == 2
    assert _seen(tmp_path, "ls20-saved_003") == 3


def _frame_col(color, off):
    sig = sa._shape_key((None, sa._canon_br([tuple(c) for c in off])))
    return {"metta": "", "geom": [{"id": "p", "sig": sig, "color": color,
                                   "off": [list(c) for c in off], "cx": 5, "cy": 5}]}


def test_recolor_is_the_same_object(tmp_path):
    # Option A: colour is an occurrence attribute, so a recoloured shape is the
    # SAME object (identity = shapename), not a new identity.
    sa.remember_objects([_frame_col("#c80000", _OFF)], "ls20-saved_001", str(tmp_path), write=True)
    sa.remember_objects([_frame_col("#0000ff", _OFF)], "ls20-saved_002", str(tmp_path), write=True)
    ids = sa.registry_snapshot(str(tmp_path))["scopes"]["ls20"]["identities"]
    assert len(ids) == 1                       # recolour did NOT mint a new object
    assert ids[0]["seen"] == 2
    assert len({v["color"] for v in ids[0]["variations"]}) == 2  # both colours bound


def test_resize_is_the_same_object(tmp_path):
    base = [(0, 0), (1, 0)]                                     # domino
    big = [(0, 0), (1, 0), (2, 0), (3, 0), (0, 1), (1, 1), (2, 1), (3, 1)]  # 2x-scaled domino
    sa.remember_objects([_frame_col("#c80000", base)], "g-1", str(tmp_path), write=True)
    sa.remember_objects([_frame_col("#c80000", big)], "g-2", str(tmp_path), write=True)
    ids = sa.registry_snapshot(str(tmp_path))["scopes"]["g"]["identities"]
    assert len(ids) == 1                       # resize did NOT mint a new object
    assert ids[0]["seen"] == 2
    assert {v["size"] for v in ids[0]["variations"]} == {2, 8}  # size is an occurrence attribute


def test_identity_is_scale_and_colour_normalized_name():
    assert sa._identity_name([(0, 0), (1, 0)]) == "domino"
    assert sa._identity_name([(0, 0), (1, 0), (2, 0), (3, 0), (0, 1), (1, 1), (2, 1), (3, 1)]) == "domino"
    assert sa._identity_name([(0, 0), (1, 0), (0, 1), (1, 1)]) == "monomino"  # 2x2 solid = scaled monomino
