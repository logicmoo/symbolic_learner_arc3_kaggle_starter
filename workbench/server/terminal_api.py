"""First-class workbench Terminal: a cross-platform PTY bridged to the browser.

Exposes a WebSocket that spawns an interactive shell under a real pseudo-terminal
(ConPTY via pywinpty on Windows, ptyprocess on POSIX) and relays bytes to and
from an xterm.js terminal in the frontend. Loopback-only, like the other local
control surfaces.

Supported shells:
  * Windows: cmd, powershell (or pwsh), and bash via WSL (wsl.exe).
  * POSIX:   bash, sh, zsh, pwsh (whichever are installed).
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import os
import shutil
import threading
from pathlib import Path
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

try:  # Cross-platform PTY backend.
    if os.name == "nt":
        from winpty import PtyProcess  # type: ignore  # pywinpty (Windows ConPTY)
    else:
        from ptyprocess import PtyProcessUnicode as PtyProcess  # type: ignore  # POSIX pty
    _PTY_IMPORT_ERROR = ""
except Exception as error:  # noqa: BLE001 - the feature degrades with a clear message
    PtyProcess = None  # type: ignore
    _PTY_IMPORT_ERROR = str(error)


router = APIRouter(tags=["terminal"])

# Default working directory for a new shell: the repository root, so the terminal
# opens where the code lives. (server -> workbench -> repo root.)
_REPO_ROOT = Path(__file__).resolve().parents[2]

_MAX_COLS, _MAX_ROWS = 500, 200


def _shell_specs() -> dict[str, list[str]]:
    if os.name == "nt":
        return {
            "cmd": ["cmd.exe"],
            "powershell": ["powershell.exe", "-NoLogo"],
            "pwsh": ["pwsh.exe", "-NoLogo"],
            "bash": ["wsl.exe"],
            "wsl": ["wsl.exe"],
        }
    return {
        "bash": ["bash"],
        "sh": ["sh"],
        "zsh": ["zsh"],
        "pwsh": ["pwsh"],
    }


def _resolve_shell(kind: str) -> list[str] | None:
    """Resolve a shell kind to an executable argv, or None when unavailable."""

    specs = _shell_specs()
    default = "cmd" if os.name == "nt" else "bash"
    argv = list(specs.get((kind or "").strip().lower() or default, specs.get(default, [])))
    if not argv:
        return None
    exe = argv[0]
    resolved = exe if os.path.isabs(exe) and os.path.exists(exe) else shutil.which(exe)
    if not resolved:
        return None
    argv[0] = resolved
    return argv


def _available_shells() -> list[str]:
    order = ["cmd", "powershell", "pwsh", "bash"] if os.name == "nt" else ["bash", "zsh", "sh", "pwsh"]
    seen: list[str] = []
    for kind in order:
        if kind in seen:
            continue
        if _resolve_shell(kind):
            seen.append(kind)
    return seen


def _resolve_cwd(raw: str | None) -> str:
    if raw:
        candidate = Path(raw)
        if candidate.is_dir():
            return str(candidate)
    return str(_REPO_ROOT if _REPO_ROOT.is_dir() else Path.home())


@router.get("/terminal/shells")
def list_shells() -> dict[str, Any]:
    """Which shells this host can open, plus PTY availability."""

    shells = _available_shells()
    return {
        "shells": shells,
        "default": shells[0] if shells else "",
        "os": os.name,
        "ptyAvailable": PtyProcess is not None,
        "ptyError": _PTY_IMPORT_ERROR,
        "defaultCwd": _resolve_cwd(None),
    }


def _is_loopback(host: str | None) -> bool:
    return host in {"127.0.0.1", "::1", "localhost", None}


@router.websocket("/terminal/ws")
async def terminal_ws(ws: WebSocket) -> None:
    await ws.accept()
    if not _is_loopback(ws.client.host if ws.client else None):
        await ws.close(code=1008)
        return
    if PtyProcess is None:
        with contextlib.suppress(Exception):
            await ws.send_text(f"\r\n[terminal] PTY backend unavailable: {_PTY_IMPORT_ERROR}\r\n")
            await ws.close()
        return

    params = ws.query_params
    argv = _resolve_shell(params.get("shell") or "")
    if not argv:
        with contextlib.suppress(Exception):
            await ws.send_text(f"\r\n[terminal] shell not available: {params.get('shell')!r}\r\n")
            await ws.close()
        return

    def _clamp(value: str | None, fallback: int, hi: int) -> int:
        try:
            return max(1, min(hi, int(value or fallback)))
        except (TypeError, ValueError):
            return fallback

    cols = _clamp(params.get("cols"), 100, _MAX_COLS)
    rows = _clamp(params.get("rows"), 30, _MAX_ROWS)
    cwd = _resolve_cwd(params.get("cwd"))

    try:
        proc = PtyProcess.spawn(argv, cwd=cwd, env=dict(os.environ), dimensions=(rows, cols))
    except Exception as error:  # noqa: BLE001
        with contextlib.suppress(Exception):
            await ws.send_text(f"\r\n[terminal] failed to start shell: {error}\r\n")
            await ws.close()
        return

    loop = asyncio.get_running_loop()
    outq: asyncio.Queue = asyncio.Queue()

    def reader() -> None:
        while True:
            try:
                data = proc.read(65536)
            except EOFError:
                break
            except Exception:  # noqa: BLE001 - closed pipe / terminated
                break
            if data:
                loop.call_soon_threadsafe(outq.put_nowait, data)
        loop.call_soon_threadsafe(outq.put_nowait, None)

    threading.Thread(target=reader, daemon=True).start()

    async def sender() -> None:
        while True:
            data = await outq.get()
            if data is None:
                break
            with contextlib.suppress(Exception):
                await ws.send_text(data)
        with contextlib.suppress(Exception):
            await ws.send_text("\r\n[shell exited]\r\n")
        with contextlib.suppress(Exception):
            await ws.close()

    send_task = loop.create_task(sender())
    try:
        while True:
            message = await ws.receive_text()
            control: Any = None
            with contextlib.suppress(Exception):
                control = json.loads(message)
            if isinstance(control, dict) and control.get("t") == "i":
                with contextlib.suppress(Exception):
                    proc.write(control.get("d", ""))
            elif isinstance(control, dict) and control.get("t") == "r":
                with contextlib.suppress(Exception):
                    proc.setwinsize(_clamp(str(control.get("r")), rows, _MAX_ROWS),
                                    _clamp(str(control.get("c")), cols, _MAX_COLS))
            else:
                with contextlib.suppress(Exception):
                    proc.write(message)
    except WebSocketDisconnect:
        pass
    finally:
        with contextlib.suppress(Exception):
            proc.terminate(force=True)
        send_task.cancel()
