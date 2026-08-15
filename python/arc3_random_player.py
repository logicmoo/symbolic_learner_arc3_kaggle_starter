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
from collection_operations import random_list_element


_RUNNER_SESSIONS: dict[str, Any] = {}


def _selected_game_record(game: Mapping[str, Any] | str) -> dict[str, Any]:
    if isinstance(game, str):
        name = game.strip()
        if not name:
            raise ValueError("A game name or ID is required")
        return {"game_id": name, "title": name, "tags": []}
    return dict(game)


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
    """Capture first frames and return one human- and AI-viewable gallery."""
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


def curate_viewable_gallery(
    games: Sequence[Mapping[str, Any]] | None = None,
    workspace_root: str | Path | None = None,
    game: Mapping[str, Any] | str | None = None,
    session: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Curate either available-game previews or one selected-game screenshot."""
    if session is None:
        if games is None or workspace_root is None:
            raise ValueError("games and workspace_root are required for the available-games gallery")
        return build_game_preview_gallery(games, workspace_root)
    if game is None:
        raise ValueError("game is required for the selected-game gallery")
    record = _selected_game_record(game)
    record["frame_path"] = session.get("initial_screenshot") or session.get("frame_path")
    record["preview"] = dict(session)
    gallery = curate_gallery_resource(
        [record],
        label="Selected Game Gallery",
        title_field="title",
        image_field="frame_path",
    )
    return {**gallery, "kind": "game_preview_gallery", "games": [record]}


def enrich_game_previews(
    games: Sequence[Mapping[str, Any]],
    workspace_root: str | Path,
    runner_factory: Callable[..., Any] | None = None,
) -> list[dict[str, Any]]:
    """Compatibility wrapper for callers that still expect only the game list."""
    return build_game_preview_gallery(games, workspace_root, runner_factory)["games"]


def initialize_played_games() -> list[str]:
    """Start a workflow run with no ARC games marked as played."""
    return []


def filter_unplayed_games(
    games: Sequence[Mapping[str, Any]],
    played_games: Sequence[str] | None = None,
) -> list[dict[str, Any]]:
    """Exclude played IDs, starting a fresh cycle only after all games were seen."""
    choices = [dict(game) for game in games]
    played = {str(game_id) for game_id in played_games or []}
    unplayed = [game for game in choices if str(game.get("game_id") or "") not in played]
    return unplayed or choices


def remember_played_game(
    played_games: Sequence[str] | None,
    game: Mapping[str, Any] | str,
) -> list[str]:
    """Append the selected game ID once while preserving selection order."""
    game_id = str(_selected_game_record(game)["game_id"])
    result = [str(item) for item in played_games or []]
    if game_id not in result:
        result.append(game_id)
    return result


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


def select_random_game(
    games: Sequence[Mapping[str, Any]],
    previous_game_id: str | None = None,
    seed: int | None = None,
) -> dict[str, Any]:
    """Implement semantic game selection by delegating to Random List Element."""
    choices = [dict(game) for game in games]
    alternatives = [game for game in choices if game.get("game_id") != previous_game_id]
    return dict(random_list_element(alternatives or choices, seed))


def query_game_metta(
    game: Mapping[str, Any] | str,
    workspace_root: str | Path,
) -> dict[str, Any]:
    """Find existing MeTTa resources that mention the selected game metadata."""
    game = _selected_game_record(game)
    root = Path(workspace_root).resolve()
    terms = {
        str(game.get("game_id") or "").lower(),
        str(game.get("server_game_id") or "").lower(),
        str(game.get("title") or "").lower(),
        *(str(tag).lower() for tag in game.get("tags") or []),
    } - {""}
    matches: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*.metta")):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        matched_terms = sorted(term for term in terms if term in text.lower())
        if matched_terms:
            matches.append({
                "path": path.relative_to(root).as_posix(),
                "matched_terms": matched_terms,
                "source": text,
            })
    atoms = [
        ["game", str(game.get("game_id") or "")],
        ["title", str(game.get("title") or game.get("game_id") or "")],
        *(["tag", str(tag)] for tag in game.get("tags") or []),
        *(["metta_source", item["path"]] for item in matches),
        *(["metta_source_text", item["source"]] for item in matches),
    ]
    return {"game": dict(game), "query_terms": sorted(terms), "matches": matches, "atoms": atoms}


def _metta_string(value: Any) -> str:
    return json.dumps(str(value), ensure_ascii=False)


def populate_game_atomspace(
    game: Mapping[str, Any] | str,
    knowledge: Mapping[str, Any],
    workspace_root: str | Path,
) -> dict[str, Any]:
    """Persist selected-game knowledge into its default runtime AtomSpace."""
    game = _selected_game_record(game)
    game_id = str(game.get("game_id") or "unknown")
    path = Path(workspace_root).resolve() / "runtime" / "contexts" / "games" / f"{game_id}.default.atomspace.metta"
    atoms = list(knowledge.get("atoms") or [])
    atom_lines = "\n".join(
        f"      ({_metta_string(atom[0])} {_metta_string(atom[1])})"
        for atom in atoms
        if isinstance(atom, (list, tuple)) and len(atom) >= 2
    )
    source = (
        "(\n"
        "  (kind atomspace)\n"
        f"  (id {_metta_string(f'arc3.game.{game_id}.default')})\n"
        f"  (label {_metta_string(f'{game_id} Default Game AtomSpace')})\n"
        f"  (gameId {_metta_string(game_id)})\n"
        "  (role runtime_context)\n"
        "  (atoms ([]\n"
        f"{atom_lines}\n"
        "  ))\n"
        ")\n"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(source, encoding="utf-8")
    return {
        "kind": "atomspace",
        "id": f"arc3.game.{game_id}.default",
        "game_id": game_id,
        "path": str(path),
        "atoms": atoms,
        "source_matches": len(knowledge.get("matches") or []),
    }


def start_selected_game(
    game: Mapping[str, Any] | str,
    workspace_root: str | Path,
    runner_factory: Callable[..., Any] | None = None,
) -> dict[str, Any]:
    """Start the selected game and return a durable handle plus initial state."""
    game = _selected_game_record(game)
    if runner_factory is None:
        from arc3_runner import Arc3Runner

        runner_factory = Arc3Runner
    game_id = str(game["game_id"])
    runner = runner_factory(
        game_id=game_id,
        render_mode=None,
        capture_terminal=True,
        tree_root=Path(workspace_root).resolve() / "runtime" / "states" / "action_trees",
    )
    handle = uuid.uuid4().hex
    _RUNNER_SESSIONS[handle] = runner
    return {
        "handle": handle,
        "workspace_root": str(Path(workspace_root).resolve()),
        "game": dict(game),
        **_frame_snapshot(runner),
    }


def load_game_metta_data(
    game: Mapping[str, Any] | str,
    workspace_root: str | Path,
    runner_factory: Callable[..., Any] | None = None,
) -> dict[str, Any]:
    """Load selected-game knowledge and return a ready-to-run live session."""
    game_record = _selected_game_record(game)
    knowledge = query_game_metta(game_record, workspace_root)
    atomspace = populate_game_atomspace(game_record, knowledge, workspace_root)
    session = start_selected_game(game_record, workspace_root, runner_factory)
    controls = enumerate_game_controls(session)
    loaded = {
        **session,
        "game": game_record,
        "game_id": game_record["game_id"],
        "knowledge": knowledge,
        "atomspace": atomspace,
        "controls": controls,
        "initial_screenshot": session.get("frame_path"),
    }
    return {**loaded, "session": loaded}


def initialize_selected_game(session: Mapping[str, Any]) -> dict[str, Any]:
    """Initialize the episode and capture its first frame without making a move."""
    runner = _RUNNER_SESSIONS.get(str(session.get("handle") or ""))
    if runner is None:
        raise ValueError("ARC game session is unavailable or expired")
    runner.reset(clear_history=True)
    initial_state = {**dict(session), **_frame_snapshot(runner)}
    initial_state["initial_screenshot"] = initial_state.get("frame_path")
    return {
        "session": initial_state,
        "result": {
            **initial_state,
            "initialized": True,
            "moves_made": 0,
            "message": "Game initialized; no move has been made",
        },
        "initial_screenshot": initial_state.get("frame_path"),
    }


def reset_selected_game(
    session: Mapping[str, Any],
    target: str = "level",
) -> dict[str, Any]:
    """Reset the current level or restart the selected game from its beginning."""
    runner = _RUNNER_SESSIONS.get(str(session.get("handle") or ""))
    if runner is None:
        raise ValueError("ARC game session is unavailable or expired")
    requested_target = str(target or "level").strip().lower()
    normalized_target = "level" if requested_target == "checkpoint" else requested_target
    if normalized_target == "level":
        runner.reset(clear_history=False)
        message = "Current level restored to its last saved checkpoint"
    elif normalized_target == "game":
        runner.open()
        runner.reset(clear_history=True)
        message = "Entire game restarted from its first level"
    else:
        raise ValueError("Reset target must be 'level'/'checkpoint' or 'game'")
    reset_state = {**dict(session), **_frame_snapshot(runner)}
    return {
        "session": reset_state,
        "result": {
            **reset_state,
            "reset_executed": True,
            "reset_target": normalized_target,
            "requested_target": requested_target,
            "message": message,
        },
        "reset_screenshot": reset_state.get("frame_path"),
    }


def enumerate_game_controls(session: Mapping[str, Any]) -> list[dict[str, Any]]:
    runner = _RUNNER_SESSIONS.get(str(session.get("handle") or ""))
    if runner is None:
        raise ValueError("ARC game session is unavailable or expired")
    return runner.action_table()


def choose_action(
    action_table: Sequence[Mapping[str, Any]],
    memory: Mapping[str, Any] | None = None,
    game_id: str | None = None,
    state: str | None = None,
    seed: int | None = None,
    current_image: Any | None = None,
    excluded_actions: Sequence[str] | None = None,
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
        excluded = {str(action) for action in (excluded_actions or [])}
        alternatives = [action for action in candidates if str(action.get("name")) not in excluded]
        if alternatives:
            candidates = alternatives
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
    game: Mapping[str, Any] | str | None = None,
) -> dict[str, Any]:
    path = Path(frame_path) if frame_path else None
    digest = hashlib.sha256(path.read_bytes()).hexdigest() if path and path.is_file() else None
    return {
        "captured_at": _utc_now(),
        "game": _selected_game_record(game) if game is not None else {},
        "state": state,
        "level": int(level),
        "frame_path": str(path) if path else None,
        "frame_sha256": digest,
    }


def execute_action(session: Any, proposal: Mapping[str, Any]) -> dict[str, Any]:
    """Apply one proposed action and return the resulting observable state."""
    runner = session
    if isinstance(session, Mapping):
        handle = str(session.get("handle") or "")
        runner = _RUNNER_SESSIONS.get(handle)
        if runner is None:
            raise ValueError("ARC game session is unavailable or expired")
    runner.step(str(proposal["action"]), data=dict(proposal.get("data") or {}))
    return _frame_snapshot(runner)


def pick_random_move_and_execute(
    session: Mapping[str, Any],
    controls: Sequence[Mapping[str, Any]],
    game: Mapping[str, Any] | str,
    memory: Mapping[str, Any] | None = None,
    seed: int | None = None,
    move_limit: int | None = None,
) -> dict[str, Any]:
    """Choose one legal move from the declared controls and execute it."""
    game_record = _selected_game_record(game)
    runner = _RUNNER_SESSIONS.get(str(session.get("handle") or ""))
    if runner is None:
        raise ValueError("ARC game session is unavailable or expired")
    moves_made = len(getattr(runner, "records", []) or [])
    if move_limit is not None:
        limit = int(move_limit)
        if limit < 0:
            raise ValueError("move_limit must be zero or greater")
        if moves_made >= limit:
            current = _frame_snapshot(runner)
            replay_gallery = _build_replay_gallery(session, runner)
            return {
                "session": {**dict(session), **current},
                "before": capture_observation(current.get("frame_path"), current.get("state"), current.get("level", 1), game),
                "proposal": None,
                "result": {**current, "move_executed": False, "move_limit_reached": True, "move_limit": limit, "moves_made": moves_made},
                "next_screenshot": current.get("frame_path"),
                "replay_gallery": replay_gallery,
                "animated_replay": replay_gallery.get("animation"),
            }
    current = _frame_snapshot(runner)
    before = capture_observation(
        current.get("frame_path"),
        current.get("state"),
        current.get("level", 1),
        game_record,
    )
    proposal = choose_action(
        controls,
        memory,
        str(game_record["game_id"]),
        str(before.get("state") or ""),
        seed,
        before.get("frame_path"),
    )
    result = execute_action(session, proposal)
    next_session = {**dict(session), **result}
    replay_gallery = _build_replay_gallery(next_session, runner)
    return {
        "session": next_session,
        "before": before,
        "proposal": proposal,
        "result": {**result, "move_executed": True, "move_limit_reached": False, "move_limit": move_limit, "moves_made": moves_made + 1},
        "next_screenshot": result.get("frame_path"),
        "replay_gallery": replay_gallery,
        "animated_replay": replay_gallery.get("animation"),
    }


def _build_replay_gallery(session: Mapping[str, Any], runner: Any) -> dict[str, Any]:
    """Build chronological stills and a GIF from the live runner history."""
    initial_path = session.get("initial_screenshot") or session.get("frame_path")
    items: list[dict[str, Any]] = []
    if initial_path:
        items.append({
            "title": "Initial frame — 0 moves",
            "description": "Playable game state before the first move.",
            "frame_path": str(initial_path),
            "move": 0,
        })
    for index, record in enumerate(getattr(runner, "records", []) or [], start=1):
        frame_path = getattr(record, "frame_path", None)
        action = getattr(record, "action", None)
        if isinstance(record, Mapping):
            frame_path = record.get("frame_path") or frame_path
            action = record.get("action") or action
        if frame_path:
            items.append({
                "title": f"Move {index} — {action or 'action'}",
                "description": f"State captured immediately after move {index}.",
                "frame_path": str(frame_path),
                "move": index,
                "action": action,
            })
    gallery = curate_gallery_resource(items, label="ARC Game Step-by-Step Replay")
    workspace_root = Path(str(session.get("workspace_root") or ".")).resolve()
    replay_dir = workspace_root / "runtime" / "artifacts" / "arc3_replays" / str(session.get("handle") or "session")
    replay_dir.mkdir(parents=True, exist_ok=True)
    animation_path = replay_dir / "replay.gif"
    image_paths = [Path(str(item["frame_path"])) for item in items if Path(str(item["frame_path"])).is_file()]
    if image_paths:
        from PIL import Image

        frames = [Image.open(path).convert("RGBA") for path in image_paths]
        frames[0].save(
            animation_path,
            save_all=True,
            append_images=frames[1:],
            duration=650,
            loop=0,
            disposal=2,
        )
        for frame in frames:
            frame.close()
    return {
        **gallery,
        "kind": "arc_replay_gallery",
        "animation": str(animation_path) if animation_path.is_file() else None,
        "move_count": len(getattr(runner, "records", []) or []),
    }


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
        played_games: list[str] = []
        game_limit = len(games) if max_games is None else min(int(max_games), len(games))
        while len(summaries) < game_limit:
            available = filter_unplayed_games(games, played_games)
            chosen = select_random_game(available, seed=self.rng.randrange(2**32))
            summary = self._play_game(chosen, max_steps=max_steps_per_game)
            summaries.append(summary)
            played_games = remember_played_game(played_games, chosen)
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
        ineffective_actions: set[str] = set()
        _append_jsonl(events_path, {"type": "game_selected", "at": _utc_now(), "game": dict(game)})
        while not should_rotate(started, self.seconds_per_game, self.clock()):
            before = _frame_snapshot(runner)
            proposal = choose_action(
                runner.action_table(),
                memory,
                game_id,
                before["state"],
                self.rng.randrange(2**32),
                excluded_actions=ineffective_actions,
            )
            runner.step(proposal["action"], data=proposal["data"])
            after = _frame_snapshot(runner)
            assessment = assess_transition(before, after)
            if assessment["frame_changed"]:
                ineffective_actions.clear()
            else:
                ineffective_actions.add(str(proposal["action"]))
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
    max_games: int | None = None,
    move_limit: int | None = 10,
    seed: int | None = None,
    mode: str = "automatic",
) -> list[dict[str, Any]]:
    normalized_mode = str(mode or "automatic").strip().lower()
    if normalized_mode == "interactive":
        return []
    if normalized_mode != "automatic":
        raise ValueError("mode must be 'interactive' or 'automatic'")
    normalized_seconds = 600.0 if seconds_per_game is None else float(seconds_per_game)
    normalized_move_limit = 10 if move_limit is None else int(move_limit)
    if normalized_seconds < 0:
        raise ValueError("seconds_per_game must be zero or greater")
    if normalized_move_limit < 0:
        raise ValueError("move_limit must be zero or greater")
    return RandomArc3Player(
        workspace_root,
        seconds_per_game=normalized_seconds,
        seed=seed,
    ).run(max_games=max_games, max_steps_per_game=normalized_move_limit)
