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
