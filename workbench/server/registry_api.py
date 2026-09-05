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
_PY_DIR = Path(__file__).resolve().parents[2] / "python"
if str(_PY_DIR) not in sys.path:
    sys.path.insert(0, str(_PY_DIR))


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
def recognition_demos_clear(payload: dict | None = Body(default=None)) -> dict:
    """Stop any in-flight run and clear cached results. With {"only": id}, clear
    just that one test back to its 'not run' state; otherwise clear everything."""
    import recognition_demos as rd

    only = None
    if isinstance(payload, dict) and payload.get("only"):
        only = str(payload["only"]).strip()
    return rd.clear_demo_state(only)


@router.get("/recognition/phase3")
def recognition_phase3() -> dict:
    """OBSERVE the latest Phase 3 live-learning run: a real transition rule induced
    from the recogniser's frames, a prediction recorded before its outcome, and the
    independent grade. Never starts a run on its own."""
    import phase3_pipeline as p3

    return p3.get_state()


@router.post("/recognition/phase3/run")
def recognition_phase3_run() -> dict:
    """Run the Phase 3 pipeline on the SERVER over live ls20 frames: feed the real
    recogniser encounters into GameObjectLearnerPayload -> learn -> predict -> grade."""
    import phase3_pipeline as p3

    return p3.start_run()


@router.post("/recognition/phase3/clear")
def recognition_phase3_clear() -> dict:
    """Stop any in-flight Phase 3 run and clear its cached result."""
    import phase3_pipeline as p3

    return p3.clear_state()


@router.post("/phase3/contract/validate")
def phase3_contract_validate(payload: dict = Body(...)) -> dict:
    """REST access to the object-memory data contract: accept a GameObjectLearnerPayload
    as JSON, validate it, and return the normalized payload (or a structured error).
    The SAME dataclasses are usable via local import; this proves REST parity."""
    from object_memory import GameObjectLearnerPayload, IntegrationValidator, IntegrationError

    try:
        parsed = GameObjectLearnerPayload.from_dict(payload)
        valid = IntegrationValidator().validate(parsed)
        return {"ok": True, "payload": valid.to_dict()}
    except IntegrationError as err:
        return {"ok": False, "error": str(err)}
    except Exception as err:  # noqa: BLE001 - malformed input -> structured error
        return {"ok": False, "error": f"{type(err).__name__}: {err}"}


@router.post("/phase3/learn")
def phase3_learn(payload: dict | None = Body(default=None)) -> dict:
    """REST access to the Phase 3 learning pipeline: POST {before, action, after}
    GameObjectLearnerPayload dicts and get the induced rules back as JSON. Runs the
    same GameLearningPipeline used by local import."""
    from object_memory import (
        GameObjectLearnerPayload, PipelineGameObjectLearnerPlugin, GameLearningPipeline,
        RuleStore, PredictionLedger, InMemorySemanticBackend, SymbolicStore,
    )
    from object_memory.integration import (
        phase2_transition_analyzer, phase2_transformation_learner,
        phase2_rule_inducer, phase2_rule_ranker,
    )

    if not isinstance(payload, dict) or "before" not in payload or "after" not in payload:
        return {"ok": False, "error": "expected {before, action, after}"}
    try:
        before = GameObjectLearnerPayload.from_dict(payload["before"])
        after = GameObjectLearnerPayload.from_dict(payload["after"])
        pipe = GameLearningPipeline(
            phase2_transition_analyzer(), phase2_transformation_learner(),
            phase2_rule_inducer(), phase2_rule_ranker(),
            RuleStore(), PredictionLedger(), SymbolicStore(InMemorySemanticBackend()))
        step = PipelineGameObjectLearnerPlugin(pipe).consume_transition(
            before, payload.get("action", "step"), after).value.learning_step
        return {"ok": True,
                "rules": [{"id": r.rule_id,
                           "interpretation": (r.predicted_effects[0].get("interpretation")
                                              if r.predicted_effects and isinstance(r.predicted_effects[0], dict) else None),
                           "bootstrap_probability": r.bootstrap_probability}
                          for r in step.rules],
                "candidates": [c.candidate_id for c in step.candidates]}
    except Exception as err:  # noqa: BLE001
        return {"ok": False, "error": f"{type(err).__name__}: {err}"}
