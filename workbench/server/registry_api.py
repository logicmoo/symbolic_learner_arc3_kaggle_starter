"""registry_api.py -- read-only HTTP access to the symbolic object-memory registry
for the Sprite Viewer UI. Serves the colorless SHAPE vocabulary and, per identity
SCOPE (game, shared across its levels; or `_all_games_`), the persistent
identities and placement trajectories."""
from __future__ import annotations

import sys
from pathlib import Path

from fastapi import APIRouter, Body, Query

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
def recognition_demos() -> dict:
    """OBSERVE the latest server-run sanity tests (visual grid panels + result +
    pass/fail per demo, plus a `running` flag). Does not compute — if nothing has
    run yet it kicks off one background server run and returns the empty/running
    state for the page to poll."""
    import recognition_demos as rd  # lazy: pulls numpy/scipy/PIL/swipl

    st = rd.get_demo_state()
    if st.get("results") is None and not st.get("running") and not st.get("demos"):
        rd.start_demo_run(None)
        st = rd.get_demo_state()
    return st


@router.post("/recognition/demos/run")
def recognition_demos_run(payload: dict | None = Body(default=None)) -> dict:
    """Ask the SERVER to (re)run the sanity tests in the background. Returns the
    running state immediately; the page observes results via GET. `only` reruns a
    single test by id."""
    import recognition_demos as rd

    only = None
    if isinstance(payload, dict) and payload.get("only"):
        only = str(payload["only"]).strip()
    return rd.start_demo_run(only)
