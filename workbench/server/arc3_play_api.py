"""Live human-play API for ARC3 games.

Hosts real ARC3 environments inside the workbench server so a person can
enumerate games, pick one, and play it move by move in the web UI. Every
move is recorded as a B1->B2 consumable setup directory:

    <workspace>/data/<game>/level_<n>_<YYYYmmdd-HHMMSS>_<ns>/
        image.png            initial frame for this attempt/level
        state.json           initial state payload
        recording.json       ordered move manifest for this level dir
        0/  image.png state.json     first move
        1/  image.png state.json     second move
        ...

A new stamped level directory starts on every new attempt (reset) and on
every detected level transition, so parallel sessions started milliseconds
apart never collide (the ns suffix disambiguates).
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import shutil
import sys
import threading
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Body, HTTPException
from fastapi.responses import FileResponse

router = APIRouter(prefix="/arc3-play", tags=["arc3-play"])

_REPO_ROOT = Path(__file__).resolve().parents[2]
_PYTHON_ROOT = _REPO_ROOT / "python"
_THUMBNAIL_CACHE_DIR = Path(__file__).resolve().parent / "environment_thumbnails"
_THUMBNAIL_SCALE = 4

_engine_lock = threading.Lock()
_catalog_cache: tuple[float, list[dict[str, Any]]] | None = None
_CATALOG_TTL_SECONDS = 600.0

_sessions: dict[str, "PlaySession"] = {}
_sessions_lock = threading.Lock()
_savepoints_lock = threading.Lock()


def _load_savepoints(path: Path) -> list[dict[str, Any]]:
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
        return list(loaded) if isinstance(loaded, list) else []
    except (OSError, ValueError):
        return []


def _ensure_python_path() -> None:
    path = str(_PYTHON_ROOT)
    if path not in sys.path:
        sys.path.insert(0, path)


def _load_runner_module() -> Any:
    _ensure_python_path()
    try:
        import arc3_runner
    except Exception as error:  # pragma: no cover - environment-specific
        raise HTTPException(
            status_code=503,
            detail=f"ARC3 engine unavailable: {error}",
        ) from error
    return arc3_runner


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _slug(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(value).strip())
    return cleaned.strip("._") or "unknown"


def _game_slug(game_id: str) -> str:
    value = str(game_id).strip()
    match = re.fullmatch(r"([A-Za-z0-9]+)-[0-9A-Fa-f]{8}", value)
    return _slug(match.group(1) if match else value)


_RANKED_LEVEL_DIR_RE = re.compile(r"^level_(?P<level>[^_]+)_(?P<rank>\d+)$")
_DATA_ROOT_NON_GAME_DIRS = {"recordings", "importables"}


def _games_container(root: Path) -> Path:
    """The canonical home for every game's recordings: data/Recordings/<game>/.

    All NEW recordings (live play sessions and imports alike) are written
    here. Some games may still have artifacts at the older, pre-reorg
    data/<game>/ location -- see _game_dirs_for()/_all_game_dirs(), which
    read both locations so nothing already on disk is hidden from listings.
    """
    return root / "data" / "Recordings"


def _game_write_dir(root: Path, game_dir: str) -> Path:
    """Where a specific game's new recordings/savepoints are written."""
    return _games_container(root) / game_dir


def _game_dirs_for(root: Path, game_dir: str) -> list[Path]:
    """Every existing directory for one game: new location first, then legacy."""
    candidates = [_game_write_dir(root, game_dir), root / "data" / game_dir]
    seen: set[Path] = set()
    result: list[Path] = []
    for candidate in candidates:
        if candidate in seen or not candidate.is_dir():
            continue
        seen.add(candidate)
        result.append(candidate)
    return result


def _all_game_dirs(root: Path) -> list[Path]:
    """Every per-game directory under data/, new (Recordings/<game>) and
    legacy (data/<game>) locations combined, deduplicated."""
    seen: set[Path] = set()
    result: list[Path] = []
    recordings_root = _games_container(root)
    if recordings_root.is_dir():
        for path in recordings_root.iterdir():
            if path.is_dir() and path.resolve() not in seen:
                seen.add(path.resolve())
                result.append(path)
    data_root = root / "data"
    if data_root.is_dir():
        for path in data_root.iterdir():
            if (
                path.is_dir()
                and path.name.lower() not in _DATA_ROOT_NON_GAME_DIRS
                and path.resolve() not in seen
            ):
                seen.add(path.resolve())
                result.append(path)
    return result


def _next_ranked_level_dir_name(container: Path, level: str) -> str:
    """level_<level>_<NNN>, continuing from the highest existing NNN for this
    level already under container (0-padded to at least 3 digits, starting
    at 001). Unranked/legacy-named siblings (bare level_1, timestamped
    level_1_<stamp>_<ns>) are ignored -- they don't participate in or block
    this numbering."""
    level_slug = _slug(level)
    highest = 0
    if container.is_dir():
        for entry in container.iterdir():
            if not entry.is_dir():
                continue
            match = _RANKED_LEVEL_DIR_RE.fullmatch(entry.name)
            if not match or match.group("level") != level_slug:
                continue
            try:
                highest = max(highest, int(match.group("rank")))
            except ValueError:
                continue
    return f"level_{level_slug}_{highest + 1:03d}"


def _workspace_root(workspace_id: str) -> Path:
    from workspace_api import _resolve_workspace_without_counts

    try:
        workspace = _resolve_workspace_without_counts(workspace_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return Path(workspace["root"]).resolve()


def _jsonable(value: Any) -> Any:
    module = _load_runner_module()
    return module._jsonable(value)


# Mirrors Arc3B1B2PipelinePage.tsx's scanSetupStatePath bucketing exactly (same
# suffix/name rules, same result-object shape) so every recorded move already
# carries a "scan" block and is natively usable as a B1->B2 SETUP source with
# no separate manual scan pass required.
_SCAN_IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".svg"}


def _scan_setup_dir(directory: Path, root: Path) -> dict[str, Any]:
    results: dict[str, list[str]] = {
        "obj_images": [],
        "grp_images": [],
        "sub_images": [],
        "pl_files": [],
        "eng_files": [],
        "json_files": [],
        "metta_files": [],
        "prompt_files": [],
        "unknown_files": [],
    }
    if directory.is_dir():
        for entry in directory.iterdir():
            if not entry.is_file():
                continue
            suffix = entry.suffix.lower()
            name = entry.name.lower()
            try:
                candidate = entry.relative_to(root).as_posix()
            except ValueError:
                candidate = entry.as_posix()
            if suffix in _SCAN_IMAGE_SUFFIXES:
                if name.startswith("obj"):
                    results["obj_images"].append(candidate)
                elif name.startswith("grp"):
                    results["grp_images"].append(candidate)
                else:
                    results["sub_images"].append(candidate)
            elif suffix == ".pl":
                results["pl_files"].append(candidate)
            elif suffix == ".json":
                results["json_files"].append(candidate)
            elif suffix == ".metta":
                results["metta_files"].append(candidate)
            elif suffix == ".prompt":
                results["prompt_files"].append(candidate)
            elif "eng" in name:
                results["eng_files"].append(candidate)
            else:
                results["unknown_files"].append(candidate)
    for values in results.values():
        values.sort()
    try:
        path = directory.relative_to(root).as_posix()
    except ValueError:
        path = directory.as_posix()
    return {"path": path, "results": results}


class PlaySession:
    """One live ARC3 environment plus its flat 0/1/2 move recording."""

    def __init__(self, workspace_id: str, workspace_root: Path, game_id: str) -> None:
        module = _load_runner_module()
        self.id = uuid.uuid4().hex
        self.workspace_id = workspace_id
        self.workspace_root = workspace_root
        self.game_id = str(game_id)
        self.game_dir = _game_slug(self.game_id)
        self.created_at = _utc_now()
        self.lock = threading.RLock()
        self.closed = False
        self._autosave_id = uuid.uuid4().hex[:12]
        with _engine_lock:
            self.runner = module.Arc3Runner(
                game_id=self.game_id,
                render_mode=None,
                capture_terminal=True,
                tree_root=workspace_root / "runtime" / "states" / "play_action_trees",
            )
        self.level_dirs: list[Path] = []
        self.moves: list[dict[str, Any]] = []
        self._level_moves: list[dict[str, Any]] = []
        # Deterministic recipe from env creation to now: step/reset ops.
        self.replay_log: list[dict[str, Any]] = []
        self.forked_from: str | None = None
        self._last_level = self.runner.current_level_label()
        self._begin_level_dir(reason="session_start")

    # ---- recording ----------------------------------------------------

    def _frame_png(self) -> bytes:
        _ensure_python_path()
        from image_codec import frame_to_png_bytes

        return frame_to_png_bytes(self.runner.current_grid())

    def _begin_level_dir(self, reason: str) -> None:
        level = self.runner.current_level_label()
        container = _game_write_dir(self.workspace_root, self.game_dir)
        name = _next_ranked_level_dir_name(container, level)
        directory = container / name
        directory.mkdir(parents=True, exist_ok=True)
        self.level_dir = directory
        self.level_dirs.append(directory)
        self._level_moves = []
        self._last_level = level
        self._write_node(directory, incoming_action=None, action_data={}, ordinal=None)
        self._write_recording(reason=reason)

    def _write_node(
        self,
        directory: Path,
        *,
        incoming_action: str | None,
        action_data: dict[str, Any],
        ordinal: int | None,
    ) -> dict[str, Any]:
        directory.mkdir(parents=True, exist_ok=True)
        try:
            png = self._frame_png()
        except Exception:
            png = b""
        if png:
            (directory / "image.png").write_bytes(png)
        payload = {
            **self.runner._state_payload(),
            "game_id": self.game_id,
            "game_directory": self.game_dir,
            "image_hash": hashlib.sha256(png).hexdigest()[:16] if png else None,
            "incoming_action": incoming_action,
            "action_directory": str(ordinal) if ordinal is not None else None,
            "action_data": _jsonable(action_data),
            "parent_node": ".." if ordinal is not None else None,
            "action_path": [str(index) for index in range(ordinal + 1)] if ordinal is not None else [],
            "recorded_at": _utc_now(),
            "scan": _scan_setup_dir(directory, self.workspace_root),
        }
        (directory / "state.json").write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return payload

    def _write_recording(self, reason: str = "move") -> None:
        manifest = {
            "kind": "arc3_play_recording",
            "session_id": self.id,
            "game_id": self.game_id,
            "game_directory": self.game_dir,
            "level": self._last_level,
            "level_directory": self._relative(self.level_dir),
            "started_at": self.created_at,
            "updated_at": _utc_now(),
            "last_event": reason,
            "moves": self._level_moves,
        }
        (self.level_dir / "recording.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def _relative(self, path: Path) -> str:
        try:
            return path.relative_to(self.workspace_root).as_posix()
        except ValueError:
            return path.as_posix()

    # ---- gameplay -----------------------------------------------------

    def act(self, action: str, x: int | None = None, y: int | None = None) -> dict[str, Any]:
        with self.lock:
            self._require_open()
            with _engine_lock:
                self.runner.step(action, x=x, y=y)
            data = {key: value for key, value in (("x", x), ("y", y)) if value is not None}
            op: dict[str, Any] = {"op": "step", "action": str(action).upper(), "data": data}
            level = self.runner.current_level_label()
            if level != self._last_level:
                move = self._record_level_transition(action, x, y, level)
            else:
                move = self._record_move(action, x, y)
            op["directory"] = move.get("directory")
            self.replay_log.append(op)
            self._autosave()
            return move

    def _record_move(self, action: str, x: int | None, y: int | None) -> dict[str, Any]:
        ordinal = len(self._level_moves)
        directory = self.level_dir / str(ordinal)
        data = {key: value for key, value in (("x", x), ("y", y)) if value is not None}
        payload = self._write_node(
            directory,
            incoming_action=str(action).upper(),
            action_data=data,
            ordinal=ordinal,
        )
        move = {
            "index": ordinal,
            "action": str(action).upper(),
            "data": data,
            "directory": self._relative(directory),
            "state": payload.get("state"),
            "level": payload.get("level"),
            "recorded_at": payload.get("recorded_at"),
        }
        self._level_moves.append(move)
        self.moves.append(move)
        self._write_recording()
        return move

    def _record_level_transition(
        self, action: str, x: int | None, y: int | None, level: str
    ) -> dict[str, Any]:
        # The winning move is recorded in the level it finished, then a fresh
        # stamped directory begins for the newly loaded level.
        move = self._record_move(action, x, y)
        move["level_completed"] = self._last_level
        self._write_recording(reason="level_complete")
        self._begin_level_dir(reason="level_start")
        return move

    def reset(self) -> None:
        with self.lock:
            self._require_open()
            with _engine_lock:
                self.runner.reset(clear_history=True)
            self.replay_log.append({"op": "reset"})
            self._begin_level_dir(reason="new_attempt")
            self._autosave()

    def undo(self, count: int = 1) -> dict[str, Any]:
        # Artificial rewind: games are deterministic, so RESET the current
        # level, replay every recorded move except the last `count`, and
        # drop the rewound move directories so the recording position
        # points at the earlier move again.
        with self.lock:
            self._require_open()
            if not self._level_moves:
                raise ValueError("no moves to undo in this level")
            count = max(1, min(int(count), len(self._level_moves)))
            replay = list(self._level_moves[:-count])
            rewound = list(self._level_moves[-count:])
            with _engine_lock:
                self.runner.reset(clear_history=True)
                for move in replay:
                    data = move.get("data") or {}
                    self.runner.step(
                        move["action"], x=data.get("x"), y=data.get("y")
                    )
            for move in rewound:
                shutil.rmtree(
                    self.level_dir / str(move["index"]), ignore_errors=True
                )
            self._level_moves = replay
            for move in reversed(rewound):
                if self.moves and self.moves[-1] is move:
                    self.moves.pop()
                if self.replay_log and self.replay_log[-1].get("op") == "step":
                    self.replay_log.pop()
            # Verify the deterministic replay landed on the recorded frame.
            verified: bool | None = None
            try:
                png = self._frame_png()
                digest = hashlib.sha256(png).hexdigest()[:16] if png else None
                expected_dir = (
                    self.level_dir / str(replay[-1]["index"])
                    if replay
                    else self.level_dir
                )
                expected = json.loads(
                    (expected_dir / "state.json").read_text(encoding="utf-8")
                ).get("image_hash")
                verified = bool(digest and expected and digest == expected)
            except Exception:
                verified = None
            self._write_recording(reason="undo")
            self._autosave()
            return {
                "rewound": rewound,
                "count": len(rewound),
                "undone_at": _utc_now(),
                "replay_verified": verified,
            }

    def restart(self) -> None:
        # Full game restart: fresh environment back at level 1 (unlike
        # reset, which only restarts the current level).
        with self.lock:
            self._require_open()
            with _engine_lock:
                old_env = getattr(self.runner, "env", None)
                self.runner.restart_game()
                if hasattr(self.runner, "_pending_level_after_win"):
                    self.runner._pending_level_after_win = None
                close = getattr(old_env, "close", None)
                if callable(close):
                    try:
                        close()
                    except Exception:
                        pass
            self.replay_log = []
            self._begin_level_dir(reason="game_restart")
            self._autosave()

    def fork(self, label: str | None = None) -> dict[str, Any]:
        # Non-disruptive save-point: snapshot the deterministic replay
        # recipe into the game log and keep playing.
        with self.lock:
            self._require_open()
            savepoint = self._savepoint_payload(uuid.uuid4().hex[:12], label)
            self._write_savepoint(savepoint)
            return savepoint

    def _savepoint_payload(self, savepoint_id: str, label: str | None) -> dict[str, Any]:
        return {
            "id": savepoint_id,
            "kind": "arc3_play_savepoint",
            "created_at": _utc_now(),
            "label": str(label).strip() if label else None,
            "game_id": self.game_id,
            "game_directory": self.game_dir,
            "level": self._last_level,
            "level_directory": self._relative(self.level_dir),
            "move_index": len(self._level_moves) - 1 if self._level_moves else None,
            "state": self.runner.state_name(),
            "session_id": self.id,
            "replay_log": [dict(entry) for entry in self.replay_log],
        }

    def _write_savepoint(self, savepoint: dict[str, Any], replace_id: str | None = None) -> None:
        path = _game_write_dir(self.workspace_root, self.game_dir) / "savepoints.json"
        with _savepoints_lock:
            entries = _load_savepoints(path)
            if replace_id:
                entries = [entry for entry in entries if str(entry.get("id")) != replace_id]
            entries.append(savepoint)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                json.dumps(entries, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )

    def _autosave(self) -> None:
        # Rolling backup: one savepoint per session, overwritten after every
        # move so the latest position is always resumable.
        if not any(entry.get("op") == "step" for entry in self.replay_log):
            return
        savepoint = self._savepoint_payload(self._autosave_id, "auto save (latest)")
        self._write_savepoint(savepoint, replace_id=self._autosave_id)

    def replay_recipe(self, recipe: list[dict[str, Any]], forked_from: str) -> None:
        # Re-drive the session through the normal act/reset path so every
        # replayed move is recorded exactly like live play.
        for entry in recipe:
            op = str(entry.get("op") or "")
            if op == "reset":
                self.reset()
            elif op == "step":
                data = entry.get("data") or {}
                self.act(str(entry.get("action")), x=data.get("x"), y=data.get("y"))
        self.forked_from = forked_from
        with self.lock:
            self._write_recording(reason="fork_resume")

    def close(self) -> None:
        with self.lock:
            if self.closed:
                return
            self.closed = True
            self._write_recording(reason="session_closed")
            environment = getattr(self.runner, "env", None)
            close = getattr(environment, "close", None)
            if callable(close):
                try:
                    close()
                except Exception:
                    pass

    def _require_open(self) -> None:
        if self.closed:
            raise HTTPException(status_code=409, detail="play session is closed")

    # ---- snapshots ----------------------------------------------------

    def _available_actions(self) -> list[dict[str, Any]]:
        _ensure_python_path()
        from arc3_runner import action_name, is_complex_action

        observation = self.runner.current_observation
        raw_available = getattr(observation, "available_actions", None)
        available_values: set[int] | None = None
        if isinstance(raw_available, (list, tuple)) and raw_available:
            try:
                available_values = {int(item) for item in raw_available}
            except (TypeError, ValueError):
                available_values = None
        friendly = {
            "ACTION1": "UP",
            "ACTION2": "DOWN",
            "ACTION3": "LEFT",
            "ACTION4": "RIGHT",
            "ACTION5": "SPACE",
            "ACTION6": "CLICK",
            "ACTION7": "UNDO",
        }
        actions: list[dict[str, Any]] = []
        for candidate in self.runner.action_space:
            name = action_name(candidate).upper().split(".")[-1]
            if name == "RESET":
                continue
            value = getattr(candidate, "value", None)
            enabled = True
            if available_values is not None and isinstance(value, int):
                enabled = value in available_values
            actions.append(
                {
                    "id": name,
                    "label": friendly.get(name, name),
                    "complex": is_complex_action(candidate),
                    "enabled": enabled,
                }
            )
        return actions

    def snapshot(self, include_moves: bool = True) -> dict[str, Any]:
        with self.lock:
            latest_dir = (
                self.level_dir / str(len(self._level_moves) - 1)
                if self._level_moves
                else self.level_dir
            )
            frame_path = latest_dir / "image.png"
            payload: dict[str, Any] = {
                "id": self.id,
                "workspaceId": self.workspace_id,
                "gameId": self.game_id,
                "gameDirectory": self.game_dir,
                "createdAt": self.created_at,
                "closed": self.closed,
                "state": self.runner.state_name(),
                "level": self.runner.current_level_label(),
                "moveCount": len(self.moves),
                "levelMoveCount": len(self._level_moves),
                "levelDir": self._relative(self.level_dir),
                "levelDirs": [self._relative(path) for path in self.level_dirs],
                "framePath": self._relative(frame_path) if frame_path.is_file() else None,
                "forkedFrom": self.forked_from,
                "availableActions": self._available_actions(),
                "replayLog": [dict(entry) for entry in self.replay_log],
            }
            if include_moves:
                payload["moves"] = list(self.moves)
            return payload


# ---- catalog ------------------------------------------------------------


def _game_catalog(refresh: bool = False) -> list[dict[str, Any]]:
    global _catalog_cache
    now = time.monotonic()
    if not refresh and _catalog_cache and now - _catalog_cache[0] < _CATALOG_TTL_SECONDS:
        return _catalog_cache[1]
    module = _load_runner_module()
    _ensure_python_path()
    import arc_agi

    with _engine_lock:
        arcade = arc_agi.Arcade()
        games = [module.Arc3Runner.game_info(game) for game in (arcade.get_environments() or [])]
    for game in games:
        game["short_id"] = _game_slug(str(game.get("game_id") or ""))
    games.sort(key=lambda game: str(game.get("short_id") or ""))
    _catalog_cache = (now, games)
    return games


def _find_game(game_id: str) -> dict[str, Any] | None:
    catalog = _game_catalog()
    return next(
        (game for game in catalog if game.get("short_id") == game_id or game.get("game_id") == game_id),
        None,
    )


def _thumbnail_path(short_id: str) -> Path:
    safe = re.sub(r"[^A-Za-z0-9_.-]", "_", short_id) or "unknown"
    return _THUMBNAIL_CACHE_DIR / f"{safe}.png"


def _render_game_preview_png(full_game_id: str) -> bytes:
    """Instantiate the game briefly (offline, no action-tree side effects) and
    PNG-encode its initial frame -- a lightweight one-shot render, not a full
    ``Arc3Runner`` play session (which would also start writing action-tree
    state to disk for every one of the 278+ catalog games)."""
    _ensure_python_path()
    import arc_agi
    from image_codec import extract_latest_frame, frame_to_png_bytes

    with _engine_lock:
        arcade = arc_agi.Arcade(operation_mode=arc_agi.OperationMode.OFFLINE)
        env = arcade.make(full_game_id, include_frame_data=True, render_mode=None)
        if env is None:
            raise RuntimeError(f"could not create environment for {full_game_id}")
        frame = extract_latest_frame(getattr(env, "observation_space", None), env)
        return frame_to_png_bytes(frame, scale=_THUMBNAIL_SCALE)


# ---- routes -------------------------------------------------------------


@router.get("/games")
def list_games(refresh: bool = False) -> dict[str, Any]:
    return {"games": _game_catalog(refresh=refresh)}


@router.post("/games/sync")
def sync_games_from_arc_interactive() -> dict[str, Any]:
    """Notice + import any new games from a sibling ``../arc-interactive``
    checkout (if present) into the local environment_files cache, then bust
    the catalog cache so the next /games list reflects them immediately."""
    _ensure_python_path()
    from arc_interactive_sync import DEFAULT_DEST, DEFAULT_SOURCE, sync_summary

    with _engine_lock:
        summary = sync_summary(DEFAULT_SOURCE, DEFAULT_DEST)
    if summary["copied"] or not _catalog_cache:
        _game_catalog(refresh=True)
    return summary


@router.get("/games/{game_id}/preview")
def game_preview(game_id: str, refresh: bool = False) -> FileResponse:
    game = _find_game(game_id)
    if game is None:
        raise HTTPException(status_code=404, detail=f"unknown game: {game_id}")
    short_id = str(game.get("short_id") or game_id)
    full_id = str(game.get("game_id") or game_id)
    cache_path = _thumbnail_path(short_id)
    if refresh and cache_path.is_file():
        cache_path.unlink(missing_ok=True)
    if not cache_path.is_file():
        try:
            png_bytes = _render_game_preview_png(full_id)
        except HTTPException:
            raise
        except Exception as error:
            raise HTTPException(status_code=502, detail=f"could not render preview for {full_id}: {error}") from error
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_bytes(png_bytes)
    return FileResponse(cache_path, media_type="image/png")



@router.get("/sessions")
def list_sessions() -> dict[str, Any]:
    with _sessions_lock:
        sessions = list(_sessions.values())
    return {"sessions": [session.snapshot(include_moves=False) for session in sessions]}


@router.post("/sessions", status_code=201)
def create_session(body: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    workspace_id = str(body.get("workspaceId") or "").strip()
    game_id = str(body.get("gameId") or "").strip()
    savepoint_id = str(body.get("savepointId") or "").strip()
    replay_ops_raw = body.get("replayLog")
    replay_ops = [dict(op) for op in replay_ops_raw] if isinstance(replay_ops_raw, list) else []
    if not workspace_id or (not game_id and not savepoint_id):
        raise HTTPException(status_code=400, detail="workspaceId and gameId are required")
    root = _workspace_root(workspace_id)
    savepoint: dict[str, Any] | None = None
    if savepoint_id:
        savepoint = _find_savepoint(root, savepoint_id, game_dir=_game_slug(game_id) if game_id else None)
        if savepoint is None:
            raise HTTPException(status_code=404, detail=f"savepoint not found: {savepoint_id}")
        game_id = str(savepoint.get("game_id") or game_id)
    try:
        session = PlaySession(workspace_id, root, game_id)
        if savepoint is not None:
            session.replay_recipe(
                list(savepoint.get("replay_log") or []),
                forked_from=str(savepoint.get("id")),
            )
        elif replay_ops:
            # Play-from-here on a closed session: re-drive the recorded ops
            # into this fresh session (no revival of the old one needed).
            session.replay_recipe(replay_ops, forked_from=str(body.get("forkedFrom") or "history"))
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=400, detail=f"could not start game: {error}") from error
    with _sessions_lock:
        _sessions[session.id] = session
    return {"session": session.snapshot()}


@router.get("/savepoints")
def list_savepoints(workspaceId: str, gameId: str | None = None) -> dict[str, Any]:
    root = _workspace_root(workspaceId)
    entries: list[dict[str, Any]] = []
    directories = _game_dirs_for(root, _game_slug(gameId)) if gameId else _all_game_dirs(root)
    with _savepoints_lock:
        for directory in directories:
            for entry in _load_savepoints(directory / "savepoints.json"):
                summary = {key: value for key, value in entry.items() if key != "replay_log"}
                summary["move_total"] = sum(
                    1 for op in entry.get("replay_log") or [] if op.get("op") == "step"
                )
                entries.append(summary)
    entries.sort(key=lambda entry: str(entry.get("created_at") or ""), reverse=True)
    return {"savepoints": entries}


def _dedupe_key(entry: dict[str, Any]) -> str:
    imported = entry.get("imported_from")
    if imported:
        return f"import:{imported}"
    return f"log:{json.dumps(entry.get('replay_log') or [], sort_keys=True)}"


def _dedupe_savepoints_in(path: Path) -> int:
    entries = _load_savepoints(path)
    groups: dict[str, list[dict[str, Any]]] = {}
    for entry in entries:
        groups.setdefault(_dedupe_key(entry), []).append(entry)
    kept: list[dict[str, Any]] = []
    removed = 0
    for group in groups.values():
        if len(group) == 1:
            kept.append(group[0])
            continue
        # Same source recording or byte-identical replay recipe: keep the
        # newest entry (freshest label/timestamp), drop the rest.
        group.sort(key=lambda entry: str(entry.get("created_at") or ""))
        kept.append(group[-1])
        removed += len(group) - 1
    if removed:
        path.write_text(json.dumps(kept, indent=2, ensure_ascii=False), encoding="utf-8")
    return removed


@router.post("/savepoints/dedupe")
def dedupe_savepoints(workspaceId: str, gameId: str | None = None) -> dict[str, Any]:
    root = _workspace_root(workspaceId)
    directories = _game_dirs_for(root, _game_slug(gameId)) if gameId else _all_game_dirs(root)
    removed = 0
    with _savepoints_lock:
        for directory in directories:
            path = directory / "savepoints.json"
            if path.is_file():
                removed += _dedupe_savepoints_in(path)
    return {"removed": removed}


@router.get("/savepoints/{savepoint_id}")
def read_savepoint(savepoint_id: str, workspaceId: str, gameId: str | None = None) -> dict[str, Any]:
    root = _workspace_root(workspaceId)
    entry = _find_savepoint(root, savepoint_id, game_dir=_game_slug(gameId) if gameId else None)
    if entry is None:
        raise HTTPException(status_code=404, detail=f"savepoint not found: {savepoint_id}")
    return {"savepoint": entry}


@router.delete("/savepoints/{savepoint_id}")
def delete_savepoint(savepoint_id: str, workspaceId: str, gameId: str | None = None) -> dict[str, Any]:
    root = _workspace_root(workspaceId)
    directories = _game_dirs_for(root, _game_slug(gameId)) if gameId else _all_game_dirs(root)
    with _savepoints_lock:
        for directory in directories:
            path = directory / "savepoints.json"
            entries = _load_savepoints(path)
            kept = [entry for entry in entries if str(entry.get("id")) != savepoint_id]
            if len(kept) != len(entries):
                path.write_text(
                    json.dumps(kept, indent=2, ensure_ascii=False),
                    encoding="utf-8",
                )
                return {"deleted": savepoint_id}
    raise HTTPException(status_code=404, detail=f"savepoint not found: {savepoint_id}")


@router.post("/savepoints/{savepoint_id}/duplicate", status_code=201)
def duplicate_savepoint(savepoint_id: str, workspaceId: str, gameId: str | None = None) -> dict[str, Any]:
    root = _workspace_root(workspaceId)
    directories = _game_dirs_for(root, _game_slug(gameId)) if gameId else _all_game_dirs(root)
    with _savepoints_lock:
        for directory in directories:
            path = directory / "savepoints.json"
            entries = _load_savepoints(path)
            for entry in entries:
                if str(entry.get("id")) == savepoint_id:
                    copy = json.loads(json.dumps(entry))
                    copy["id"] = uuid.uuid4().hex[:12]
                    copy["created_at"] = _utc_now()
                    label = str(entry.get("label") or "").strip()
                    copy["label"] = f"{label} (copy)" if label else f"copy of {savepoint_id}"
                    entries.append(copy)
                    path.write_text(
                        json.dumps(entries, indent=2, ensure_ascii=False),
                        encoding="utf-8",
                    )
                    return {"savepoint": {key: value for key, value in copy.items() if key != "replay_log"}}
    raise HTTPException(status_code=404, detail=f"savepoint not found: {savepoint_id}")


# ---- human recording import ----------------------------------------------
#
# Official ARC-AGI-3 recordings (arcprize agents SDK / human plays) are JSONL
# files: one {"timestamp", "data": {frame, state, action_input, ...}} line per
# frame plus a final scorecard line. The importer converts one offline into
# the exact same level_*/0..k recording layout the live recorder writes, and
# registers a savepoint whose replay_log can re-drive a real session.

_RECORDING_SKIP_NAMES = {"savepoints.json", "recording.json", "state.json"}


def _sniff_recording_head(path: Path) -> str | None:
    try:
        with path.open("r", encoding="utf-8") as handle:
            head = handle.readline(131072).strip()
    except OSError:
        return None
    if not head.startswith("{") or '"action_input"' not in head or '"frame"' not in head:
        return None
    return head


def _list_recording_files(root: Path) -> list[dict[str, Any]]:
    data_root = root / "data" / "importables"
    if not data_root.is_dir():
        return []
    found: list[dict[str, Any]] = []
    for path in sorted(data_root.rglob("*.json")):
        if path.name in _RECORDING_SKIP_NAMES:
            continue
        head = _sniff_recording_head(path)
        if head is None:
            continue
        match = re.search(r'"game_id"\s*:\s*"([^"]+)"', head)
        found.append(
            {
                "path": path.relative_to(root).as_posix(),
                "name": path.name,
                "gameId": match.group(1) if match else None,
                "sizeBytes": path.stat().st_size,
                "kind": "human-jsonl",
            }
        )
    # Official agent release-runs: <game>/<timestamp>/workspace/log.txt (+ its
    # own bundled arclog.py parser), one level below data/importables/release-runs/.
    release_root = data_root / "release-runs"
    if release_root.is_dir():
        for game_dir in sorted(p for p in release_root.iterdir() if p.is_dir()):
            for run_dir in sorted(p for p in game_dir.iterdir() if p.is_dir()):
                log_path = run_dir / "workspace" / "log.txt"
                arclog_path = run_dir / "workspace" / "arclog.py"
                if not (log_path.is_file() and arclog_path.is_file()):
                    continue
                score = None
                scorecard_path = run_dir / "scorecard.json"
                if scorecard_path.is_file():
                    try:
                        score = json.loads(scorecard_path.read_text(encoding="utf-8")).get("total_actions")
                    except (OSError, json.JSONDecodeError):
                        score = None
                found.append(
                    {
                        "path": run_dir.relative_to(root).as_posix(),
                        "name": f"{game_dir.name}/{run_dir.name}",
                        "gameId": game_dir.name,
                        "sizeBytes": log_path.stat().st_size,
                        "kind": "release-run",
                        "totalActions": score,
                    }
                )
    return found


def _purge_prior_import(root: Path, game_dir: str, rel_path: str) -> int:
    """Remove level dirs + savepoints from an earlier import of the same source file.

    Makes re-importing idempotent: clicking Import again on a file that was
    already converted replaces its artifacts instead of piling up duplicates.
    Checks both the new (data/Recordings/<game>) and legacy (data/<game>)
    locations, since an earlier import may predate this fix.
    """
    removed = 0
    for game_root in _game_dirs_for(root, game_dir):
        for level_dir in sorted(game_root.glob("level_*")):
            manifest_path = level_dir / "recording.json"
            if not manifest_path.is_file():
                continue
            try:
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if manifest.get("imported_from") == rel_path:
                shutil.rmtree(level_dir, ignore_errors=True)
                removed += 1
        savepoints_path = game_root / "savepoints.json"
        with _savepoints_lock:
            entries = _load_savepoints(savepoints_path)
            kept = [entry for entry in entries if entry.get("imported_from") != rel_path]
            if len(kept) != len(entries):
                savepoints_path.write_text(
                    json.dumps(kept, indent=2, ensure_ascii=False),
                    encoding="utf-8",
                )
    return removed


def _import_recording(root: Path, rel_path: str, label: str | None) -> dict[str, Any]:
    _ensure_python_path()
    from image_codec import frame_to_png_bytes

    source = (root / rel_path).resolve()
    try:
        source.relative_to(root)
    except ValueError as error:
        raise HTTPException(status_code=400, detail="path must live inside the workspace") from error
    if not source.is_file():
        raise HTTPException(status_code=404, detail=f"recording not found: {rel_path}")

    events: list[dict[str, Any]] = []
    for line in source.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        data = row.get("data") if isinstance(row, dict) else None
        if isinstance(data, dict) and isinstance(data.get("frame"), list):
            events.append(row)
    if not events:
        raise HTTPException(status_code=400, detail="no frame events found in recording")

    first = events[0]["data"]
    game_id = str(first.get("game_id") or source.stem)
    guid = str(first.get("guid") or uuid.uuid4().hex)
    game_dir = _game_slug(game_id)
    session_tag = f"import-{guid[:12]}"
    import_label = str(label).strip() if label else f"human recording {source.stem}"
    _purge_prior_import(root, game_dir, rel_path)

    def relative(path: Path) -> str:
        return path.relative_to(root).as_posix()

    def grid_of(event: dict[str, Any]) -> Any:
        frames = event["data"].get("frame") or []
        return frames[-1] if frames else []

    level_dirs: list[Path] = []
    level_moves: list[dict[str, Any]] = []
    replay_log: list[dict[str, Any]] = []
    move_total = 0
    current_dir: Path | None = None
    current_level = "1"

    def write_node(
        directory: Path,
        event: dict[str, Any],
        incoming_action: str | None,
        action_data: dict[str, Any],
        ordinal: int | None,
        step_count: int,
    ) -> dict[str, Any]:
        directory.mkdir(parents=True, exist_ok=True)
        try:
            png = frame_to_png_bytes(grid_of(event))
        except Exception:
            png = b""
        if png:
            (directory / "image.png").write_bytes(png)
        data = event["data"]
        observation = {key: value for key, value in data.items() if key != "frame"}
        observation["frame_count"] = len(data.get("frame") or [])
        payload = {
            "state": data.get("state"),
            "level": current_level,
            "level_source": "imported_recording",
            "next_level_expected": None,
            "observation": observation,
            "step_count": step_count,
            "game_id": game_id,
            "game_directory": game_dir,
            "image_hash": hashlib.sha256(png).hexdigest()[:16] if png else None,
            "incoming_action": incoming_action,
            "action_directory": str(ordinal) if ordinal is not None else None,
            "action_data": action_data,
            "parent_node": ".." if ordinal is not None else None,
            "action_path": [str(index) for index in range(ordinal + 1)] if ordinal is not None else [],
            "recorded_at": str(event.get("timestamp") or _utc_now()),
            "scan": _scan_setup_dir(directory, root),
        }
        (directory / "state.json").write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return payload

    def write_recording(reason: str) -> None:
        if current_dir is None:
            return
        manifest = {
            "kind": "arc3_play_recording",
            "session_id": session_tag,
            "game_id": game_id,
            "game_directory": game_dir,
            "level": current_level,
            "level_directory": relative(current_dir),
            "started_at": str(events[0].get("timestamp") or _utc_now()),
            "updated_at": _utc_now(),
            "last_event": reason,
            "imported_from": rel_path,
            "moves": level_moves,
        }
        (current_dir / "recording.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def begin_level(event: dict[str, Any], reason: str, step_count: int) -> None:
        nonlocal current_dir, level_moves, current_level
        current_level = str(int(event["data"].get("levels_completed") or 0) + 1)
        container = _game_write_dir(root, game_dir)
        directory = container / _next_ranked_level_dir_name(container, current_level)
        directory.mkdir(parents=True, exist_ok=True)
        current_dir = directory
        level_dirs.append(directory)
        level_moves = []
        write_node(directory, event, None, {}, None, step_count)
        write_recording(reason)

    begin_level(events[0], "imported_start", 0)
    last_completed = int(events[0]["data"].get("levels_completed") or 0)

    for index, event in enumerate(events[1:], start=1):
        data = event["data"]
        action_input = data.get("action_input") or {}
        action_id = int(action_input.get("id") or 0)
        if action_id == 0:
            replay_log.append({"op": "reset"})
            begin_level(event, "new_attempt", index)
            last_completed = int(data.get("levels_completed") or 0)
            continue
        action = f"ACTION{action_id}"
        raw_data = action_input.get("data") or {}
        action_data = {key: int(raw_data[key]) for key in ("x", "y") if key in raw_data}
        assert current_dir is not None
        ordinal = len(level_moves)
        directory = current_dir / str(ordinal)
        payload = write_node(directory, event, action, action_data, ordinal, index)
        move = {
            "index": ordinal,
            "action": action,
            "data": action_data,
            "directory": relative(directory),
            "state": payload.get("state"),
            "level": payload.get("level"),
            "recorded_at": payload.get("recorded_at"),
        }
        level_moves.append(move)
        move_total += 1
        replay_log.append({"op": "step", "action": action, "data": action_data, "directory": move["directory"]})
        completed = int(data.get("levels_completed") or 0)
        if completed != last_completed and str(data.get("state") or "").upper() != "WIN":
            move["level_completed"] = current_level
            write_recording("level_complete")
            begin_level(event, "level_start", index)
        else:
            write_recording("move")
        last_completed = completed

    final_state = str(events[-1]["data"].get("state") or "NOT_FINISHED")
    savepoint = {
        "id": uuid.uuid4().hex[:12],
        "kind": "arc3_play_savepoint",
        "created_at": _utc_now(),
        "label": import_label,
        "game_id": game_id,
        "game_directory": game_dir,
        "level": current_level,
        "level_directory": relative(current_dir) if current_dir else None,
        "move_index": len(level_moves) - 1 if level_moves else None,
        "state": final_state,
        "session_id": session_tag,
        "imported_from": rel_path,
        "replay_log": replay_log,
    }
    savepoints_path = _game_write_dir(root, game_dir) / "savepoints.json"
    with _savepoints_lock:
        entries = _load_savepoints(savepoints_path)
        entries.append(savepoint)
        savepoints_path.parent.mkdir(parents=True, exist_ok=True)
        savepoints_path.write_text(
            json.dumps(entries, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    return {
        "imported": {
            "path": rel_path,
            "gameId": game_id,
            "gameDirectory": game_dir,
            "moveCount": move_total,
            "levelDirs": [relative(path) for path in level_dirs],
            "state": final_state,
        },
        "savepoint": {key: value for key, value in savepoint.items() if key != "replay_log"},
    }


def _parse_transcript_actions(run_dir: Path) -> list[dict[str, Any]]:
    """Flatten transcript.jsonl's invocations into one entry per planned
    action, in order. Each release-run's total planned actions across every
    invocation lines up 1:1 with its real (non-RESET) steps in log.txt, so
    this list can be walked in lockstep with arclog's Step list to attach
    the agent's own commentary/reasoning to the exact move it produced.
    """
    transcript_path = run_dir / "transcript.jsonl"
    if not transcript_path.is_file():
        return []
    flattened: list[dict[str, Any]] = []
    for line in transcript_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            invocation = json.loads(line)
        except json.JSONDecodeError:
            continue
        text = str(invocation.get("text") or "")
        marker = text.find("[ACTIONS]")
        commentary = (text[:marker] if marker >= 0 else text).strip()
        plan_entries: list[dict[str, Any]] = []
        if marker >= 0:
            try:
                plan = json.loads(text[marker + len("[ACTIONS]"):].strip())
                if isinstance(plan, dict) and isinstance(plan.get("plan"), list):
                    plan_entries = plan["plan"]
            except json.JSONDecodeError:
                plan_entries = []
        for entry in plan_entries:
            if not isinstance(entry, dict):
                continue
            flattened.append(
                {
                    "invocation": invocation.get("invocation"),
                    "commentary": commentary,
                    "action": entry.get("action"),
                    "expect": entry.get("expect"),
                    "reasoning": entry.get("reasoning"),
                }
            )
    return flattened


def _load_trace_playbook_snapshots(run_dir: Path, filename: str = "playbook.md") -> dict[int, str]:
    """Return {invocation_number: cumulative file content as of the end of
    that invocation}, reconstructed from write/edit tool-call spans in the
    run's OTel-style trace files. Trace files are sorted by their earliest
    span timestamp, which lines up with invocation order 1..N -- this is a
    persistent, cross-invocation "working memory" file the agent edits and
    recompacts over the whole run, not a per-step artifact.
    """
    traces_root = run_dir / "traces"
    if not traces_root.is_dir():
        return {}
    trace_files: list[Path] = []
    for workspace_dir in traces_root.iterdir():
        if workspace_dir.is_dir():
            trace_files.extend(workspace_dir.glob("*.jsonl"))

    def min_started_at(path: Path) -> float:
        best = float("inf")
        try:
            for line in path.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                try:
                    span = json.loads(line)
                except json.JSONDecodeError:
                    continue
                started = span.get("started_at")
                if isinstance(started, (int, float)) and started < best:
                    best = started
        except OSError:
            pass
        return best

    trace_files.sort(key=min_started_at)
    snapshots: dict[int, str] = {}
    content = ""
    for invocation_number, trace_path in enumerate(trace_files, start=1):
        changed = False
        try:
            lines = trace_path.read_text(encoding="utf-8").splitlines()
        except OSError:
            lines = []
        for line in lines:
            if not line.strip() or filename not in line:
                continue
            try:
                span = json.loads(line)
            except json.JSONDecodeError:
                continue
            attrs = span.get("attributes") or {}
            if attrs.get("gen_ai.tool.name") not in ("write", "edit"):
                continue
            raw_args = attrs.get("gen_ai.tool.call.arguments")
            args = raw_args
            if isinstance(raw_args, str):
                try:
                    args = json.loads(raw_args)
                except json.JSONDecodeError:
                    continue
            if not isinstance(args, dict) or args.get("path") != filename:
                continue
            piece = args.get("content")
            if not isinstance(piece, str):
                continue
            content = f"{content}{piece}" if args.get("append") and content else piece
            changed = True
        if changed:
            snapshots[invocation_number] = content
    return snapshots


def _import_release_run(root: Path, rel_dir: str, label: str | None) -> dict[str, Any]:
    """Import an official ARC-AGI-3 agent release-run directory.

    Shape: <run_dir>/scorecard.json, workspace/log.txt, workspace/arclog.py
    (the log parser is copied fresh into every run's own workspace, so we
    load that exact copy dynamically instead of re-implementing parsing --
    guarantees the same interpretation the agent itself used). Converts into
    our standard level_*/0..k recording layout + a resumable savepoint, same
    as the human-JSONL importer.
    """
    _ensure_python_path()
    from image_codec import frame_to_png_bytes

    run_dir = (root / rel_dir).resolve()
    try:
        run_dir.relative_to(root)
    except ValueError as error:
        raise HTTPException(status_code=400, detail="path must live inside the workspace") from error
    log_path = run_dir / "workspace" / "log.txt"
    arclog_path = run_dir / "workspace" / "arclog.py"
    if not log_path.is_file() or not arclog_path.is_file():
        raise HTTPException(status_code=404, detail=f"not a release-run directory: {rel_dir}")

    spec = importlib.util.spec_from_file_location(f"_arclog_{abs(hash(str(arclog_path)))}", arclog_path)
    if spec is None or spec.loader is None:
        raise HTTPException(status_code=400, detail=f"could not load parser at {arclog_path}")
    arclog_module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = arclog_module  # dataclass() introspects sys.modules by name
    spec.loader.exec_module(arclog_module)
    steps = arclog_module.load(str(log_path))
    if not steps:
        raise HTTPException(status_code=400, detail="no steps found in log.txt")

    scorecard: dict[str, Any] = {}
    scorecard_path = run_dir / "scorecard.json"
    if scorecard_path.is_file():
        try:
            scorecard = json.loads(scorecard_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            scorecard = {}
    envs = scorecard.get("environments") if isinstance(scorecard, dict) else None
    env_id = envs[0].get("id") if isinstance(envs, list) and envs else None
    game_id = str(env_id or run_dir.parent.name)
    game_dir = _game_slug(game_id)
    session_tag = f"release-{run_dir.parent.name}-{run_dir.name}"
    import_label = str(label).strip() if label else f"release run {run_dir.parent.name}/{run_dir.name}"
    _purge_prior_import(root, game_dir, rel_dir)

    def relative(path: Path) -> str:
        return path.relative_to(root).as_posix()

    level_dirs: list[Path] = []
    level_moves: list[dict[str, Any]] = []
    replay_log: list[dict[str, Any]] = []
    move_total = 0
    current_dir: Path | None = None
    current_level = "1"

    def write_node(directory: Path, step: Any, incoming_action: str | None, action_data: dict[str, Any], ordinal: int | None) -> dict[str, Any]:
        directory.mkdir(parents=True, exist_ok=True)
        try:
            png = frame_to_png_bytes(step.settled)
        except Exception:
            png = b""
        if png:
            (directory / "image.png").write_bytes(png)
        payload = {
            "state": step.state,
            "level": current_level,
            "level_source": "imported_release_run",
            "next_level_expected": None,
            "observation": {
                "available_actions": list(step.available),
                "levels_completed": step.levels_completed,
                "win_levels": step.win_levels,
                "log_step": step.step,
            },
            "step_count": step.step,
            "game_id": game_id,
            "game_directory": game_dir,
            "image_hash": hashlib.sha256(png).hexdigest()[:16] if png else None,
            "incoming_action": incoming_action,
            "action_directory": str(ordinal) if ordinal is not None else None,
            "action_data": action_data,
            "parent_node": ".." if ordinal is not None else None,
            "action_path": [str(index) for index in range(ordinal + 1)] if ordinal is not None else [],
            "recorded_at": _utc_now(),
            "scan": _scan_setup_dir(directory, root),
        }
        (directory / "state.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        return payload

    def write_recording(reason: str) -> None:
        if current_dir is None:
            return
        manifest = {
            "kind": "arc3_play_recording",
            "session_id": session_tag,
            "game_id": game_id,
            "game_directory": game_dir,
            "level": current_level,
            "level_directory": relative(current_dir),
            "started_at": _utc_now(),
            "updated_at": _utc_now(),
            "last_event": reason,
            "imported_from": rel_dir,
            "moves": level_moves,
        }
        (current_dir / "recording.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    def begin_level(step: Any, reason: str) -> None:
        nonlocal current_dir, level_moves, current_level
        is_first = not level_dirs
        current_level = str(int(step.levels_completed) + 1)
        container = _game_write_dir(root, game_dir)
        directory = container / _next_ranked_level_dir_name(container, current_level)
        directory.mkdir(parents=True, exist_ok=True)
        current_dir = directory
        level_dirs.append(directory)
        level_moves = []
        write_node(directory, step, None, {}, None)
        if is_first:
            prime_path = run_dir / "prime.json"
            if prime_path.is_file():
                try:
                    prime = json.loads(prime_path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    prime = {}
                description = prime.get("description") if isinstance(prime, dict) else None
                if isinstance(description, str) and description.strip():
                    vision_model = prime.get("vision_model") or "vision model"
                    (directory / "vision_prime.md").write_text(
                        f"# Opening-frame read ({vision_model})\n\n{description}\n",
                        encoding="utf-8",
                    )
        write_recording(reason)

    flattened_actions = _parse_transcript_actions(run_dir)
    playbook_snapshots = _load_trace_playbook_snapshots(run_dir)

    begin_level(steps[0], "imported_start")
    last_completed = steps[0].levels_completed

    for index, step in enumerate(steps[1:], start=1):
        action = str(step.action).upper()
        if action == "RESET":
            replay_log.append({"op": "reset"})
            begin_level(step, "new_attempt")
            last_completed = step.levels_completed
            continue
        action_data = {key: value for key, value in (("x", step.x), ("y", step.y)) if value is not None}
        assert current_dir is not None
        ordinal = len(level_moves)
        directory = current_dir / str(ordinal)
        payload = write_node(directory, step, action, action_data, ordinal)
        # Agent's own commentary/reasoning for this move (from transcript.jsonl,
        # flattened 1:1 against non-RESET steps) and, when this move is the
        # last one its invocation produced, the persistent playbook.md
        # snapshot as of that point (reconstructed from trace write/edit
        # spans) -- so stepping through the replay surfaces both as they
        # actually accrued during the run, not just a single final artifact.
        flat_index = move_total
        if flat_index < len(flattened_actions):
            entry = flattened_actions[flat_index]
            commentary_lines = [f"# Agent commentary (invocation {entry.get('invocation')})", "", entry.get("commentary") or ""]
            if entry.get("reasoning"):
                commentary_lines += ["", "## Reasoning for this action", "", str(entry["reasoning"])]
            if entry.get("expect"):
                commentary_lines += ["", "## Predicted cells (x, y, old, new)", "", json.dumps(entry["expect"])]
            (directory / "commentary.md").write_text("\n".join(commentary_lines).strip() + "\n", encoding="utf-8")
            invocation_number = entry.get("invocation")
            is_last_of_invocation = (
                flat_index + 1 >= len(flattened_actions)
                or flattened_actions[flat_index + 1].get("invocation") != invocation_number
            )
            if is_last_of_invocation and invocation_number in playbook_snapshots:
                (directory / "playbook.md").write_text(playbook_snapshots[invocation_number], encoding="utf-8")
        move = {
            "index": ordinal,
            "action": action,
            "data": action_data,
            "directory": relative(directory),
            "state": payload.get("state"),
            "level": payload.get("level"),
            "recorded_at": payload.get("recorded_at"),
        }
        level_moves.append(move)
        move_total += 1
        replay_log.append({"op": "step", "action": action, "data": action_data, "directory": move["directory"]})
        completed = step.levels_completed
        if completed != last_completed and str(step.state or "").upper() != "WIN":
            move["level_completed"] = current_level
            write_recording("level_complete")
            begin_level(step, "level_start")
        else:
            write_recording("move")
        last_completed = completed

    final_state = str(steps[-1].state or "NOT_FINISHED")
    savepoint = {
        "id": uuid.uuid4().hex[:12],
        "kind": "arc3_play_savepoint",
        "created_at": _utc_now(),
        "label": import_label,
        "game_id": game_id,
        "game_directory": game_dir,
        "level": current_level,
        "level_directory": relative(current_dir) if current_dir else None,
        "move_index": len(level_moves) - 1 if level_moves else None,
        "state": final_state,
        "session_id": session_tag,
        "imported_from": rel_dir,
        "replay_log": replay_log,
    }
    savepoints_path = _game_write_dir(root, game_dir) / "savepoints.json"
    with _savepoints_lock:
        entries = _load_savepoints(savepoints_path)
        entries.append(savepoint)
        savepoints_path.parent.mkdir(parents=True, exist_ok=True)
        savepoints_path.write_text(
            json.dumps(entries, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    return {
        "imported": {
            "path": rel_dir,
            "gameId": game_id,
            "gameDirectory": game_dir,
            "moveCount": move_total,
            "levelDirs": [relative(path) for path in level_dirs],
            "state": final_state,
        },
        "savepoint": {key: value for key, value in savepoint.items() if key != "replay_log"},
    }


@router.get("/recordings")
def list_recordings(workspaceId: str) -> dict[str, Any]:
    root = _workspace_root(workspaceId)
    return {"recordings": _list_recording_files(root)}


def _dedupe_recordings_in(root: Path, game_root: Path) -> list[str]:
    groups: dict[str, list[tuple[float, Path]]] = {}
    for level_dir in sorted(game_root.glob("level_*")):
        manifest_path = level_dir / "recording.json"
        if not manifest_path.is_file():
            continue
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        imported_from = manifest.get("imported_from")
        if not imported_from:
            continue  # never touch live-played recordings, only re-imports
        groups.setdefault(imported_from, []).append((manifest_path.stat().st_mtime, level_dir))

    removed: list[str] = []
    for entries in groups.values():
        if len(entries) <= 1:
            continue
        entries.sort(key=lambda item: item[0])
        # Sequential clustering: a new import run starts whenever the gap
        # between consecutive level dirs' last-write time exceeds 2 minutes.
        clusters: list[list[tuple[float, Path]]] = []
        for item in entries:
            if clusters and item[0] - clusters[-1][-1][0] <= 120:
                clusters[-1].append(item)
            else:
                clusters.append([item])
        clusters.sort(key=lambda cluster: cluster[-1][0])
        for cluster in clusters[:-1]:  # keep only the most recent run
            for _, path in cluster:
                shutil.rmtree(path, ignore_errors=True)
                removed.append(path.relative_to(root).as_posix())
    return removed


@router.post("/recordings/dedupe")
def dedupe_recordings(workspaceId: str, gameId: str | None = None) -> dict[str, Any]:
    root = _workspace_root(workspaceId)
    directories = _game_dirs_for(root, _game_slug(gameId)) if gameId else _all_game_dirs(root)
    removed: list[str] = []
    for directory in directories:
        if directory.is_dir():
            removed.extend(_dedupe_recordings_in(root, directory))
    return {"removed": removed, "count": len(removed)}


@router.post("/import-recording", status_code=201)
def import_recording(body: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    workspace_id = str(body.get("workspaceId") or "").strip()
    rel_path = str(body.get("path") or "").strip()
    if not workspace_id or not rel_path:
        raise HTTPException(status_code=400, detail="workspaceId and path are required")
    root = _workspace_root(workspace_id)
    label = body.get("label")
    target = root / rel_path
    if target.is_dir() and (target / "workspace" / "log.txt").is_file():
        return _import_release_run(root, rel_path, str(label) if label else None)
    return _import_recording(root, rel_path, str(label) if label else None)


def _find_savepoint(root: Path, savepoint_id: str, game_dir: str | None = None) -> dict[str, Any] | None:
    directories = _game_dirs_for(root, game_dir) if game_dir else _all_game_dirs(root)
    with _savepoints_lock:
        for directory in directories:
            for entry in _load_savepoints(directory / "savepoints.json"):
                if str(entry.get("id")) == savepoint_id:
                    return entry
    return None


def _get_session(session_id: str) -> PlaySession:
    with _sessions_lock:
        session = _sessions.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="unknown play session")
    return session


@router.get("/sessions/{session_id}")
def read_session(session_id: str) -> dict[str, Any]:
    return {"session": _get_session(session_id).snapshot()}


@router.post("/sessions/{session_id}/action")
def act(session_id: str, body: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    session = _get_session(session_id)
    action = str(body.get("action") or "").strip()
    if not action:
        raise HTTPException(status_code=400, detail="action is required")
    x = body.get("x")
    y = body.get("y")
    try:
        move = session.act(
            action,
            x=int(x) if x is not None else None,
            y=int(y) if y is not None else None,
        )
    except HTTPException:
        raise
    except (TypeError, ValueError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=400, detail=f"action failed: {error}") from error
    return {"move": move, "session": session.snapshot()}


@router.post("/sessions/{session_id}/reset")
def reset(session_id: str) -> dict[str, Any]:
    session = _get_session(session_id)
    try:
        session.reset()
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=400, detail=f"reset failed: {error}") from error
    return {"session": session.snapshot()}


@router.post("/sessions/{session_id}/undo")
def undo(session_id: str, body: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    session = _get_session(session_id)
    try:
        count = int(body.get("count") or 1)
    except (TypeError, ValueError):
        count = 1
    try:
        removed = session.undo(count=count)
    except HTTPException:
        raise
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=400, detail=f"undo failed: {error}") from error
    return {"removed": removed, "session": session.snapshot()}


@router.post("/sessions/{session_id}/fork")
def fork(session_id: str, body: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    session = _get_session(session_id)
    try:
        savepoint = session.fork(label=body.get("label"))
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=400, detail=f"fork failed: {error}") from error
    return {"savepoint": savepoint, "session": session.snapshot()}


@router.post("/sessions/{session_id}/restart")
def restart(session_id: str) -> dict[str, Any]:
    session = _get_session(session_id)
    try:
        session.restart()
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=400, detail=f"restart failed: {error}") from error
    return {"session": session.snapshot()}


@router.delete("/sessions/{session_id}")
def close_session(session_id: str) -> dict[str, Any]:
    session = _get_session(session_id)
    session.close()
    with _sessions_lock:
        _sessions.pop(session_id, None)
    return {"session": session.snapshot()}


@router.on_event("shutdown")
def _save_open_sessions_on_shutdown() -> None:
    # The dev server file-watcher reloads the process on code changes.
    # The rolling per-move autosave already keeps every session backed up,
    # so shutdown only needs to close environments cleanly.
    with _sessions_lock:
        sessions = list(_sessions.values())
    for session in sessions:
        try:
            session.close()
        except Exception:
            pass
