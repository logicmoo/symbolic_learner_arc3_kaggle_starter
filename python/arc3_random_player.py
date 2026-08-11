from __future__ import annotations

import copy
import hashlib
import json
import random
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from collection_operations import curate_gallery_resource


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _game_record(game: Any) -> dict[str, Any]:
    game_id = str(getattr(game, "game_id", "")).split("-", 1)[0]
    return {
        "game_id": game_id,
        "server_game_id": str(getattr(game, "game_id", game_id)),
        "title": str(getattr(game, "title", game_id)),
        "tags": list(getattr(game, "tags", []) or []),
    }


def discover_games(arcade: Any | None = None) -> list[dict[str, Any]]:
    """Ask the ARC service for the current environment catalog."""
    if arcade is None:
        import arc_agi

        arcade = arc_agi.Arcade()
    return sorted(
        (_game_record(game) for game in (arcade.get_environments() or [])),
        key=lambda game: game["game_id"],
    )


def build_game_preview_gallery(
    games: Sequence[Mapping[str, Any]],
    workspace_root: str | Path,
    runner_factory: Callable[..., Any] | None = None,
) -> dict[str, Any]:
    """Build a human- and AI-inspectable gallery from every game's first frame."""
    if runner_factory is None:
        from arc3_runner import Arc3Runner

        runner_factory = Arc3Runner
    tree_root = Path(workspace_root) / "runtime" / "states" / "preview_action_trees"
    enriched: list[dict[str, Any]] = []
    for game in games:
        record = dict(game)
        runner = runner_factory(
            game_id=str(record["game_id"]),
            render_mode=None,
            capture_terminal=True,
            tree_root=tree_root,
        )
        try:
            record["preview"] = _frame_snapshot(runner)
        finally:
            environment = getattr(runner, "env", None)
            close = getattr(environment, "close", None)
            if callable(close):
                close()
        enriched.append(record)
    gallery = curate_gallery_resource(
        enriched,
        label="Game Preview Gallery",
        title_field="title",
        image_field="frame_path",
    )
    return {**gallery, "kind": "game_preview_gallery", "games": enriched}


def enrich_game_previews(
    games: Sequence[Mapping[str, Any]],
    workspace_root: str | Path,
    runner_factory: Callable[..., Any] | None = None,
) -> list[dict[str, Any]]:
    """Compatibility wrapper for callers that still expect only the game list."""
    return build_game_preview_gallery(games, workspace_root, runner_factory)["games"]


def select_game(
    games: Sequence[Mapping[str, Any]],
    previous_game_id: str | None = None,
    seed: int | None = None,
) -> dict[str, Any]:
    if not games:
        raise ValueError("ARC returned no games")
    choices = [dict(game) for game in games]
    alternatives = [game for game in choices if game.get("game_id") != previous_game_id]
    return random.Random(seed).choice(alternatives or choices)


def choose_action(
    action_table: Sequence[Mapping[str, Any]],
    memory: Mapping[str, Any] | None = None,
    game_id: str | None = None,
    state: str | None = None,
    seed: int | None = None,
    current_image: Any | None = None,
) -> dict[str, Any]:
    del current_image  # Reserved for prompt-backed and future vision implementations.
    actions = [dict(action) for action in action_table]
    if not actions:
        raise ValueError("ARC environment exposes no legal actions")
    reset = next((action for action in actions if action.get("name") == "RESET"), None)
    if state in {"NOT_PLAYED", "GAME_OVER"} and reset:
        selected = reset
    else:
        candidates = [action for action in actions if action.get("name") != "RESET"] or actions
        learned = dict((memory or {}).get("games", {}).get(game_id or "", {}).get("actions", {}))
        weights = []
        for action in candidates:
            stats = dict(learned.get(str(action.get("name")), {}))
            good = int(stats.get("good", 0))
            bad = int(stats.get("bad", 0))
            weights.append(max(0.15, (good + 1.0) / (bad + 1.0)))
        selected = random.Random(seed).choices(candidates, weights=weights, k=1)[0]
    payload: dict[str, int] = {}
    if selected.get("complex"):
        rng = random.Random(seed)
        payload = {"x": rng.randint(0, 63), "y": rng.randint(0, 63)}
    return {
        "index": selected.get("index"),
        "action": selected.get("name"),
        "data": payload,
        "strategy": "learned_weighted_random",
    }


def assess_transition(
    before: Mapping[str, Any],
    after: Mapping[str, Any],
) -> dict[str, Any]:
    previous_level = int(before.get("level") or 1)
    current_level = int(after.get("level") or previous_level)
    frame_changed = before.get("frame_sha256") != after.get("frame_sha256")
    state = str(after.get("state") or "")
    if state == "WIN" or current_level > previous_level:
        rating, reason = "good", "won or advanced a level"
    elif state == "GAME_OVER":
        rating, reason = "bad", "ended the attempt"
    elif not frame_changed:
        rating, reason = "bad", "did not change the visible state"
    else:
        rating, reason = "neutral", "changed the state without decisive progress"
    return {
        "rating": rating,
        "reason": reason,
        "frame_changed": frame_changed,
        "state_before": before.get("state"),
        "state_after": after.get("state"),
        "level_before": previous_level,
        "level_after": current_level,
    }


def update_learning_memory(
    memory: Mapping[str, Any] | None,
    game_id: str,
    action: str,
    assessment: Mapping[str, Any],
) -> dict[str, Any]:
    updated = copy.deepcopy(dict(memory or {}))
    updated.setdefault("version", 1)
    updated["updated_at"] = _utc_now()
    game = updated.setdefault("games", {}).setdefault(game_id, {"actions": {}})
    stats = game["actions"].setdefault(action, {"good": 0, "bad": 0, "neutral": 0})
    rating = str(assessment.get("rating") or "neutral")
    stats[rating if rating in stats else "neutral"] += 1
    stats["last_reason"] = str(assessment.get("reason") or "")
    stats["last_seen_at"] = updated["updated_at"]
    game["attempts"] = int(game.get("attempts", 0)) + 1
    return updated


def should_rotate(
    started_monotonic: float,
    duration_seconds: float = 600.0,
    now_monotonic: float | None = None,
) -> bool:
    now = time.monotonic() if now_monotonic is None else now_monotonic
    return now - started_monotonic >= duration_seconds


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + f".{uuid.uuid4().hex}.tmp")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temporary.replace(path)


def _append_jsonl(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(dict(value), ensure_ascii=False) + "\n")


def load_learning_memory(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {"version": 1, "games": {}}
    return value if isinstance(value, dict) else {"version": 1, "games": {}}


def _frame_snapshot(runner: Any) -> dict[str, Any]:
    node = getattr(runner, "current_node", None)
    image_path = Path(node.image_path) if node is not None else None
    digest = hashlib.sha256(image_path.read_bytes()).hexdigest() if image_path and image_path.is_file() else None
    return {
        "captured_at": _utc_now(),
        "state": runner.state_name(),
        "level": runner.current_level_label(),
        "frame_path": str(image_path) if image_path else None,
        "frame_sha256": digest,
    }


def capture_observation(
    frame_path: str | None,
    state: str | None,
    level: int | str = 1,
) -> dict[str, Any]:
    path = Path(frame_path) if frame_path else None
    digest = hashlib.sha256(path.read_bytes()).hexdigest() if path and path.is_file() else None
    return {
        "captured_at": _utc_now(),
        "state": state,
        "level": int(level),
        "frame_path": str(path) if path else None,
        "frame_sha256": digest,
    }


def execute_action(runner: Any, proposal: Mapping[str, Any]) -> dict[str, Any]:
    """Apply one proposed action and return the resulting observable state."""
    runner.step(str(proposal["action"]), data=dict(proposal.get("data") or {}))
    return _frame_snapshot(runner)


class RandomArc3Player:
    """Rotate through real ARC3 games and retain action-outcome evidence."""

    def __init__(
        self,
        workspace_root: str | Path,
        *,
        seconds_per_game: float = 600.0,
        seed: int | None = None,
        runner_factory: Callable[..., Any] | None = None,
        arcade: Any | None = None,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.workspace_root = Path(workspace_root).resolve()
        self.seconds_per_game = seconds_per_game
        self.rng = random.Random(seed)
        self.arcade = arcade
        self.clock = clock
        if runner_factory is None:
            from arc3_runner import Arc3Runner

            runner_factory = Arc3Runner
        self.runner_factory = runner_factory
        self.memory_path = self.workspace_root / "runtime" / "contexts" / "action_learning_memory.json"

    def run(self, *, max_games: int | None = None, max_steps_per_game: int | None = None) -> list[dict[str, Any]]:
        games = discover_games(self.arcade)
        catalog_path = self.workspace_root / "runtime" / "states" / "arc3_game_catalog.json"
        _write_json(catalog_path, {"fetched_at": _utc_now(), "games": games})
        summaries: list[dict[str, Any]] = []
        previous_game_id: str | None = None
        while max_games is None or len(summaries) < max_games:
            chosen = select_game(games, previous_game_id, self.rng.randrange(2**32))
            summary = self._play_game(chosen, max_steps=max_steps_per_game)
            summaries.append(summary)
            previous_game_id = chosen["game_id"]
        return summaries

    def _play_game(self, game: Mapping[str, Any], *, max_steps: int | None) -> dict[str, Any]:
        session_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "-" + uuid.uuid4().hex[:8]
        game_id = str(game["game_id"])
        session_root = self.workspace_root / "runtime" / "goal-runs" / session_id
        events_path = self.workspace_root / "runtime" / "events" / f"{session_id}.events.jsonl"
        runner = self.runner_factory(
            game_id=game_id,
            render_mode=None,
            capture_terminal=True,
            tree_root=self.workspace_root / "runtime" / "states" / "action_trees",
        )
        started = self.clock()
        memory = load_learning_memory(self.memory_path)
        steps = 0
        ratings = {"good": 0, "bad": 0, "neutral": 0}
        _append_jsonl(events_path, {"type": "game_selected", "at": _utc_now(), "game": dict(game)})
        while not should_rotate(started, self.seconds_per_game, self.clock()):
            before = _frame_snapshot(runner)
            proposal = choose_action(
                runner.action_table(), memory, game_id, before["state"], self.rng.randrange(2**32)
            )
            runner.step(proposal["action"], data=proposal["data"])
            after = _frame_snapshot(runner)
            assessment = assess_transition(before, after)
            memory = update_learning_memory(memory, game_id, str(proposal["action"]), assessment)
            _write_json(self.memory_path, memory)
            event = {
                "type": "action_assessed",
                "at": _utc_now(),
                "game_id": game_id,
                "step": steps,
                "proposal": proposal,
                "before": before,
                "after": after,
                "assessment": assessment,
            }
            _append_jsonl(events_path, event)
            steps += 1
            ratings[assessment["rating"]] += 1
            if max_steps is not None and steps >= max_steps:
                break
        history_path = session_root / "arc3_history.json"
        runner.save_history(history_path)
        summary = {
            "kind": "goal_run",
            "id": session_id,
            "goalId": "arc3_random_player.learn_by_playing",
            "game": dict(game),
            "started_monotonic": started,
            "duration_seconds": self.clock() - started,
            "steps": steps,
            "ratings": ratings,
            "history": str(history_path),
            "events": str(events_path),
            "memory": str(self.memory_path),
            "completed_at": _utc_now(),
        }
        _write_json(session_root / "summary.json", summary)
        return summary


def run_random_arc3_session(
    workspace_root: str = "workbench/workspaces/arc3_random_player",
    seconds_per_game: float = 600.0,
    max_games: int | None = 1,
    seed: int | None = None,
) -> list[dict[str, Any]]:
    return RandomArc3Player(
        workspace_root,
        seconds_per_game=seconds_per_game,
        seed=seed,
    ).run(max_games=max_games)
