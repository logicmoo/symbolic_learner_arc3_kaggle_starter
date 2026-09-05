"""registry_api.py -- read-only HTTP access to the symbolic object-memory registry
for the Sprite Viewer UI. Serves the colorless SHAPE vocabulary and, per identity
SCOPE (game, shared across its levels; or `_all_games_`), the persistent
identities and placement trajectories."""
from __future__ import annotations

import sys
from pathlib import Path

from fastapi import APIRouter, Query

router = APIRouter()

_PROLOG_DIR = Path(__file__).resolve().parent / "generative_vision" / "prolog"
if str(_PROLOG_DIR) not in sys.path:
    sys.path.insert(0, str(_PROLOG_DIR))


@router.get("/registry/snapshot")
def registry_snapshot(
    includeTurtles: bool = Query(True, description="include per-shape turtle programs"),
    game: str | None = Query(None, description="filter identities to one scope (game)"),
) -> dict:
    """The entire object-memory registry: the shape vocabulary plus, per scope
    (game / `_all_games_`), its identities and placements. `game` filters to one
    scope; identity is shared per game between its levels."""
    import symbolic_arc as sa  # lazy: pulls numpy/scipy/PIL

    snap = sa.registry_snapshot(include_turtles=includeTurtles)
    snap["games"] = sorted(k for k in snap.get("scopes", {}))
    if game is not None:
        snap = dict(snap)
        snap["scopes"] = {game: snap.get("scopes", {}).get(game, {"identities": [], "placements": []})}
        snap["filteredGame"] = game
    return snap


@router.get("/recognition/demos")
def recognition_demos(only: str | None = Query(None, description="run a single demo by id")) -> dict:
    """Run the symbolic_arc Phase-2 acceptance demonstrations and return their
    visual grid panels + result + pass/fail for the Recognition Demos page."""
    import recognition_demos as rd  # lazy: pulls numpy/scipy/PIL/swipl

    return rd.run_demos(only=only)
