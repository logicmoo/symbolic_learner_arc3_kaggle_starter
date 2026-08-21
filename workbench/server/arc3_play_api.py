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
import json
import re
import sys
import threading
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Body, HTTPException

router = APIRouter(prefix="/arc3-play", tags=["arc3-play"])

_REPO_ROOT = Path(__file__).resolve().parents[2]
_PYTHON_ROOT = _REPO_ROOT / "python"

_engine_lock = threading.Lock()
_catalog_cache: tuple[float, list[dict[str, Any]]] | None = None
_CATALOG_TTL_SECONDS = 600.0

_sessions: dict[str, "PlaySession"] = {}
_sessions_lock = threading.Lock()


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


def _stamped_level_dir_name(level: str) -> str:
    now = datetime.now(timezone.utc)
    stamp = now.strftime("%Y%m%d-%H%M%S")
    return f"level_{_slug(level)}_{stamp}_{time.time_ns()}"


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
        self._last_level = self.runner.current_level_label()
        self._begin_level_dir(reason="session_start")

    # ---- recording ----------------------------------------------------

    def _frame_png(self) -> bytes:
        _ensure_python_path()
        from image_codec import frame_to_png_bytes

        return frame_to_png_bytes(self.runner.current_grid())

    def _begin_level_dir(self, reason: str) -> None:
        level = self.runner.current_level_label()
        name = _stamped_level_dir_name(level)
        directory = self.workspace_root / "data" / self.game_dir / name
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
            level = self.runner.current_level_label()
            if level != self._last_level:
                move = self._record_level_transition(action, x, y, level)
            else:
                move = self._record_move(action, x, y)
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
            self._begin_level_dir(reason="new_attempt")

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
            "ACTION6": "SELECT",
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
                "availableActions": self._available_actions(),
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


# ---- routes -------------------------------------------------------------


@router.get("/games")
def list_games(refresh: bool = False) -> dict[str, Any]:
    return {"games": _game_catalog(refresh=refresh)}


@router.get("/sessions")
def list_sessions() -> dict[str, Any]:
    with _sessions_lock:
        sessions = list(_sessions.values())
    return {"sessions": [session.snapshot(include_moves=False) for session in sessions]}


@router.post("/sessions", status_code=201)
def create_session(body: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    workspace_id = str(body.get("workspaceId") or "").strip()
    game_id = str(body.get("gameId") or "").strip()
    if not workspace_id or not game_id:
        raise HTTPException(status_code=400, detail="workspaceId and gameId are required")
    root = _workspace_root(workspace_id)
    try:
        session = PlaySession(workspace_id, root, game_id)
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=400, detail=f"could not start game: {error}") from error
    with _sessions_lock:
        _sessions[session.id] = session
    return {"session": session.snapshot()}


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


@router.delete("/sessions/{session_id}")
def close_session(session_id: str) -> dict[str, Any]:
    session = _get_session(session_id)
    session.close()
    with _sessions_lock:
        _sessions.pop(session_id, None)
    return {"session": session.snapshot()}
