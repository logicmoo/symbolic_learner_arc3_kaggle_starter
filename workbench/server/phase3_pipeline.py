"""phase3_pipeline.py -- wire the LIVE symbolic recogniser's real encounters into
the Phase 3 object-memory learning stack (python/omega_vision), exposed to the
workbench via the registry API.

This is the missing integration: until now the Phase 3 classes
(GameLearningPipeline, RuleInducer, RuleExecutor, PredictionLedger, ...) were only
driven by scripts and tests. Here we take real consecutive frames from the ls20
recording, extract objects with the LLM-free recogniser (symbolic_arc), turn the
before/after states into GameObjectLearnerPayload handoffs, and run the real
phase2_* domain pipeline: induce competing transition rules from an observed move,
predict the NEXT state before it is observed, then grade that prediction against
the independently observed later frame and update the rule's calibrated evidence.
"""
from __future__ import annotations

import json as _json
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path

_HERE = Path(__file__).resolve()
_PROLOG_DIR = _HERE.parent / "generative_vision" / "prolog"
if str(_PROLOG_DIR) not in sys.path:
    sys.path.insert(0, str(_PROLOG_DIR))
# The Phase 3 package lives in <repo>/python/omega_vision.
_REPO_ROOT = _HERE.parents[2]
_PY_DIR = _REPO_ROOT / "python"
if str(_PY_DIR) not in sys.path:
    sys.path.insert(0, str(_PY_DIR))

_LS20_DIR = (_HERE.parents[1] / "workspaces" / "arc3_random_player" / "data"
             / "vision_frames" / "arc_recordings"
             / "data-arc3_games-recordings-ls20-saved_001")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _frame_ids(setdir: Path) -> list:
    mf = setdir / "manifest.json"
    order = []
    if mf.is_file():
        try:
            order = [it["id"] for it in _json.loads(mf.read_text(encoding="utf-8")).get("items", [])]
        except (OSError, _json.JSONDecodeError):
            order = []
    if not order:
        order = sorted(p.stem for p in setdir.glob("*.png"))
    return order


def _frame_objects(setdir: Path, idv: str) -> list:
    """Real objects in one frame via the LLM-free recogniser: identity (colour-free
    scale/rotation-normalised shape name), colour, and centroid position. Skips the
    background flood."""
    import symbolic_arc as sa
    png = next(iter(setdir.glob(f"{idv}.png")), None)
    if not png:
        return []
    idx, _hexpal, _cols, _rows = sa.decode_grid(str(png))
    bg = 0.33 * idx.shape[0] * idx.shape[1]
    pj = setdir / "sym" / f"{idv}__prolog.parts.json"
    parts = []
    if pj.is_file():
        try:
            parts = _json.loads(pj.read_text(encoding="utf-8"))
        except (OSError, _json.JSONDecodeError):
            parts = []
    objs = []
    for p in parts:
        off = p.get("off") or []
        if not off or len(off) > bg:
            continue
        geo = sa._identity_name(off) or ("shape_" + str(p.get("sig")))
        objs.append({"identity": geo, "color": sa._cname(p.get("color", "")),
                     "position": [int(p.get("cx", 0)), int(p.get("cy", 0))]})
    return objs


def _match(obj: dict, pool: list) -> tuple | None:
    """Nearest object in `pool` sharing identity+colour (greedy correspondence)."""
    best = None
    bd = 1e18
    for j, c in pool:
        if c["identity"] != obj["identity"] or c["color"] != obj["color"]:
            continue
        d = (c["position"][0] - obj["position"][0]) ** 2 + (c["position"][1] - obj["position"][1]) ** 2
        if d < bd:
            bd, best = d, (j, c, d)
    return best


def _pick_mover(a_objs: list, b_objs: list) -> dict | None:
    """The single object with the largest real displacement between two frames."""
    pool = list(enumerate(b_objs))
    best = None
    bd = 0.0
    used = set()
    for oa in a_objs:
        m = _match(oa, [(j, c) for (j, c) in pool if j not in used])
        if not m:
            continue
        j, cb, d = m
        if d > bd:
            bd, best = d, {"a": oa, "b": cb, "j": j}
    if not best or bd <= 0:
        return None
    return best


def run_live_phase3(n_probe: int = 12) -> dict:
    """Drive the real Phase 3 pipeline from live ls20 frames:
    learn a motion rule from frame A->B, predict the mover's position in frame C
    BEFORE looking, then grade against the actually-observed frame C."""
    from omega_vision import (
        GameLearningPipeline, GameObjectLearnerPayload, PipelineGameObjectLearnerPlugin,
        InMemorySemanticBackend, SymbolicStore, RuleStore, PredictionLedger,
        OutcomeChannel, PredictionEvaluator, PredictionGrade,
    )
    from omega_vision.runtime.integration import (
        phase2_transition_analyzer, phase2_transformation_learner,
        phase2_rule_inducer, phase2_rule_ranker, phase2_rule_executor,
    )

    setdir = _LS20_DIR
    if not setdir.is_dir():
        return {"ok": False, "note": "ls20 recording set not found", "steps": []}
    order = _frame_ids(setdir)

    # find three consecutive frames A,B,C where one object clearly moves A->B and
    # that same object can be tracked into C (so we can grade the prediction).
    chosen = None
    for k in range(min(n_probe, max(len(order) - 2, 0))):
        a, b, c = order[k], order[k + 1], order[k + 2]
        ao, bo, co = _frame_objects(setdir, a), _frame_objects(setdir, b), _frame_objects(setdir, c)
        mv = _pick_mover(ao, bo)
        if not mv:
            continue
        cont = _match(mv["b"], list(enumerate(co)))
        if not cont:
            continue
        chosen = {"a": a, "b": b, "c": c, "ao": ao, "bo": bo, "co": co,
                  "mover": mv, "cmatch": cont[1]}
        break
    if not chosen:
        return {"ok": False, "note": "no trackable moving object in the first frames",
                "frames_scanned": min(n_probe, len(order))}

    mover = chosen["mover"]
    pos_a = mover["a"]["position"]
    pos_b = mover["b"]["position"]
    pos_c = chosen["cmatch"]["position"]
    ident = mover["a"]["identity"]
    color = mover["a"]["color"]

    # --- build real Phase 2 -> Phase 3 handoffs (GameObjectLearnerPayload) --------
    before = GameObjectLearnerPayload(
        f"ls20:{chosen['a']}",
        ({"id": "mover", "position": pos_a, "shape": ident, "color": color},),
        identity_ids=("mover",), provenance=(f"frame:{chosen['a']}",))
    after = GameObjectLearnerPayload(
        f"ls20:{chosen['b']}",
        ({"id": "mover", "position": pos_b, "shape": ident, "color": color},),
        identity_ids=("mover",), provenance=(f"frame:{chosen['b']}",),
        transitions=({"id": "mover", "action": "step",
                      "properties": {"position": {"from": pos_a, "to": pos_b}}},))

    store = RuleStore()
    ledger = PredictionLedger()
    sem = SymbolicStore(InMemorySemanticBackend())
    pipeline = GameLearningPipeline(
        phase2_transition_analyzer(), phase2_transformation_learner(),
        phase2_rule_inducer(), phase2_rule_ranker(), store, ledger, sem)

    step = PipelineGameObjectLearnerPlugin(pipeline).consume_transition(before, "step", after).value.learning_step
    rules = step.rules
    # prefer the generalising relative-delta rule so the motion transfers to a new
    # position; fall back to the first induced rule.
    rel = next((r for r in rules
                if (r.predicted_effects and isinstance(r.predicted_effects[0], dict)
                    and r.predicted_effects[0].get("interpretation") == "relative_delta")), None)
    chosen_rule = rel or (rules[0] if rules else None)
    if chosen_rule is None:
        return {"ok": False, "note": "no rule induced from the observed move"}

    # --- predict frame C's position BEFORE observing it --------------------------
    executor = phase2_rule_executor(store, "step")
    predicted_state, prediction = pipeline.predict(
        prediction_id=f"ls20-{chosen['b']}-{chosen['c']}",
        rule_id=chosen_rule.rule_id,
        source_state_id=f"ls20:{chosen['b']}",
        state={"id": "mover", "position": pos_b, "shape": ident, "color": color, "action": "step"},
        created_sequence=1,
        executor=executor)
    predicted_pos = predicted_state.get("position") if isinstance(predicted_state, dict) else None
    recorded_before_outcome = sem.get("predictions", prediction.prediction_id).outcome_sequence is None

    # --- grade against the independently observed frame C ------------------------
    observed_state = {"id": "mover", "position": pos_c, "shape": ident, "color": color, "action": "step"}

    def _grade(expected, observed):
        ep = expected.get("position") if isinstance(expected, dict) else None
        op = observed.get("position") if isinstance(observed, dict) else None
        return PredictionGrade(1.0 if ep == op else 0.0, evidence=("independent_outcome",))

    closed = pipeline.grade_prediction(
        prediction_id=prediction.prediction_id, outcome_sequence=2,
        outcome_channel=OutcomeChannel(lambda: observed_state),
        evaluator=PredictionEvaluator(_grade))
    refined = store.get(chosen_rule.rule_id)

    passed = bool(recorded_before_outcome and predicted_pos == pos_c)
    return {
        "ok": True,
        "passed": passed,
        "frames": {"A": chosen["a"], "B": chosen["b"], "C": chosen["c"]},
        "mover": {"shape": ident, "color": color},
        "observed_move_AB": {"from": pos_a, "to": pos_b,
                             "delta": [pos_b[0] - pos_a[0], pos_b[1] - pos_a[1]]},
        "rules_induced": [
            {"id": r.rule_id[:16],
             "interpretation": (r.predicted_effects[0].get("interpretation")
                                if r.predicted_effects and isinstance(r.predicted_effects[0], dict) else None),
             "bootstrap": r.bootstrap_probability}
            for r in rules],
        "chosen_rule": chosen_rule.rule_id[:16],
        "prediction": {"for_frame": chosen["c"], "from": pos_b, "predicted": predicted_pos,
                       "recorded_before_outcome": recorded_before_outcome},
        "actual_C": pos_c,
        "grade": closed.grade,
        "calibrated_probability": refined.calibrated_probability,
        "probability_source": refined.probability_source,
        "startedAt": _now(),
    }


# --- server-owned run state (the UI only OBSERVES, like the Sanity Tests) -------
_state: dict = {"running": False, "result": None, "startedAt": None, "finishedAt": None}
_lock = threading.Lock()
_gen = 0


def get_state() -> dict:
    with _lock:
        st = dict(_state)
    return {"running": st["running"], "result": st["result"],
            "startedAt": st["startedAt"], "finishedAt": st["finishedAt"]}


def _job(gen: int) -> None:
    try:
        res = run_live_phase3()
        with _lock:
            if gen == _gen:
                _state["result"] = res
    except Exception as err:  # noqa: BLE001 - surface failures to the page
        with _lock:
            if gen == _gen:
                _state["result"] = {"ok": False, "note": f"error: {err}"}
    finally:
        with _lock:
            if gen == _gen:
                _state["running"] = False
                _state["finishedAt"] = _now()


def start_run() -> dict:
    global _gen
    with _lock:
        _gen += 1
        gen = _gen
        _state["running"] = True
        _state["startedAt"] = _now()
        _state["finishedAt"] = None
    threading.Thread(target=_job, args=(gen,), name="phase3-live", daemon=True).start()
    return get_state()


def clear_state() -> dict:
    global _gen
    with _lock:
        _gen += 1
        _state["running"] = False
        _state["result"] = None
        _state["startedAt"] = None
        _state["finishedAt"] = None
    return get_state()
