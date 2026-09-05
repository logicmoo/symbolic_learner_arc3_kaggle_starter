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
    pass/fail per demo, plus a `running` flag). Never computes and never starts a
    run on its own — the tests only run when the user presses a button (Run all or
    a single test). Until then this returns the empty 'not run yet' state."""
    import recognition_demos as rd  # lazy: pulls numpy/scipy/PIL/swipl

    return rd.get_demo_state()


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


@router.post("/recognition/demos/stop")
def recognition_demos_stop() -> dict:
    """Stop any in-flight sanity-test run (keeps the last cached results)."""
    import recognition_demos as rd

    return rd.stop_demo_run()


@router.post("/recognition/demos/clear")
def recognition_demos_clear() -> dict:
    """Stop any in-flight run and clear cached results back to the empty state."""
    import recognition_demos as rd

    return rd.clear_demo_state()
