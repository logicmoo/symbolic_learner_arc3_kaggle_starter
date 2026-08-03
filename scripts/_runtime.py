from __future__ import annotations

import contextlib
import io
import os
import sys
import time
from pathlib import Path

_PROJECT_MARKERS = ("pyproject.toml", "README.md")
_DEBUGGER_ATTEMPTED = False
_DEBUGGER_ATTACHED = False


def _find_project_root(start: Path) -> Path | None:
    """Return the nearest parent that looks like the ARC3 project root."""
    candidate = start.expanduser().resolve()
    if candidate.is_file():
        candidate = candidate.parent

    for directory in (candidate, *candidate.parents):
        if all((directory / marker).is_file() for marker in _PROJECT_MARKERS):
            return directory
    return None


def _env_bool(name: str, default: bool) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on", "y"}:
        return True
    if normalized in {"0", "false", "no", "off", "n"}:
        return False
    raise RuntimeError(f"{name} must be a boolean value, not {value!r}")


def _load_project_environment(project_root: Path) -> None:
    """Load project-root .env values without replacing the caller's shell."""
    env_path = project_root / ".env"
    if not env_path.is_file():
        return

    try:
        from dotenv import load_dotenv
    except ImportError as error:
        raise RuntimeError(
            f"{env_path} exists but python-dotenv is not installed. "
            "Reinstall the project dependencies before launching ARC3."
        ) from error

    load_dotenv(dotenv_path=env_path, override=False)


def hook_debugger(
    host: str = "localhost",
    port: int = 5678,
    suspend: bool = True,
    timeout: float = 7.0,
    retry_interval: float = 1.0,
    wait_for_user_if_not_started: bool = False,
) -> bool:
    """Attach to a listening PyCharm debug server using the shared behavior."""
    try:
        import pydevd_pycharm
    except ImportError:
        print("PyCharm debugger support is not installed.")
        print("Install it with:")
        print("  python -m pip install pydevd-pycharm")
        return False

    while True:
        print()
        print(
            f"Looking for the PyCharm debugger at "
            f"{host}:{port} for up to {timeout:g} seconds..."
        )

        deadline = time.monotonic() + timeout
        last_error: BaseException | None = None

        while time.monotonic() < deadline:
            try:
                suppressed_output = io.StringIO()
                with contextlib.redirect_stderr(suppressed_output):
                    pydevd_pycharm.settrace(
                        host=host,
                        port=port,
                        suspend=suspend,
                        stdout_to_server=False,
                        stderr_to_server=False,
                    )

                print(f"PyCharm debugger attached at {host}:{port}.")
                return True
            except (ConnectionError, OSError) as error:
                last_error = error
                remaining = deadline - time.monotonic()
                if remaining > 0:
                    time.sleep(min(retry_interval, remaining))

        print()
        print(f"No PyCharm debugger was found at {host}:{port}.")
        if last_error is not None:
            print(f"Reason: {last_error}")

        if not wait_for_user_if_not_started:
            print("Continuing without the PyCharm debugger.")
            return False

        while True:
            try:
                response = input(
                    "[Enter/C] Continue  [T] Try again  "
                    "[Q] Quit  [port] Try another port: "
                ).strip().lower()
            except EOFError:
                print()
                print("Continuing without the PyCharm debugger.")
                return False
            except KeyboardInterrupt:
                print()
                print("Exiting.")
                raise SystemExit(130)

            if response in {"", "c", "continue"}:
                print("Continuing without the PyCharm debugger.")
                return False
            if response in {"q", "quit", "exit"}:
                print("Exiting.")
                raise SystemExit(1)
            if response in {"t", "try", "retry"}:
                break

            try:
                new_port = int(response)
            except ValueError:
                print(
                    "Enter C to continue, T to retry, Q to quit, "
                    "or a port number."
                )
                continue

            if not 1 <= new_port <= 65535:
                print("The port must be between 1 and 65535.")
                continue

            port = new_port
            print(f"Changed the debugger port to {port}.")
            break


def configure_pycharm_debugger() -> bool:
    """Run the shared PyCharm attach attempt once for the current process."""
    global _DEBUGGER_ATTEMPTED, _DEBUGGER_ATTACHED

    if _DEBUGGER_ATTEMPTED:
        return _DEBUGGER_ATTACHED

    _DEBUGGER_ATTEMPTED = True

    default_enabled = "pytest" not in sys.modules
    if not _env_bool("ARC3_PYCHARM_DEBUG", default_enabled):
        return False

    host = os.environ.get("ARC3_PYCHARM_HOST", "localhost")
    try:
        port = int(os.environ.get("ARC3_PYCHARM_PORT", "5678"))
        timeout = float(os.environ.get("ARC3_PYCHARM_TIMEOUT", "7"))
        retry_interval = float(os.environ.get("ARC3_PYCHARM_RETRY_INTERVAL", "1"))
    except ValueError as error:
        raise RuntimeError("Invalid numeric PyCharm debugger environment setting") from error

    if not 1 <= port <= 65535:
        raise RuntimeError("ARC3_PYCHARM_PORT must be between 1 and 65535")
    if timeout < 0:
        raise RuntimeError("ARC3_PYCHARM_TIMEOUT must be non-negative")
    if retry_interval <= 0:
        raise RuntimeError("ARC3_PYCHARM_RETRY_INTERVAL must be positive")

    _DEBUGGER_ATTACHED = hook_debugger(
        host=host,
        port=port,
        suspend=_env_bool("ARC3_PYCHARM_SUSPEND", True),
        timeout=timeout,
        retry_interval=retry_interval,
        wait_for_user_if_not_started=_env_bool("ARC3_PYCHARM_WAIT", False),
    )
    return _DEBUGGER_ATTACHED


def configure_runtime_home(script_file: str | Path) -> Path:
    """Resolve the project root, load .env, enter it, and configure debugging.

    Runtime-home resolution order:

    1. ``ARC3_RUNTIME_HOME`` when explicitly configured by the caller.
    2. The current working directory, including its parent directories.
    3. The repository root inferred from the script location.

    Once the root is known, project-root ``.env`` values are loaded with
    ``override=False``. Explicit shell and IDE variables therefore take
    precedence. The PyCharm attach attempt runs after environment loading.
    """
    configured = os.environ.get("ARC3_RUNTIME_HOME")
    if configured:
        project_root = _find_project_root(Path(configured))
        if project_root is None:
            raise RuntimeError(
                "ARC3_RUNTIME_HOME does not point inside a valid project root: "
                f"{configured!r}"
            )
    else:
        project_root = _find_project_root(Path.cwd())
        if project_root is None:
            project_root = _find_project_root(Path(script_file))
        if project_root is None:
            raise RuntimeError(
                f"Unable to locate the ARC3 project root from {script_file!r}"
            )

    _load_project_environment(project_root)
    os.environ["ARC3_RUNTIME_HOME"] = str(project_root)
    os.chdir(project_root)

    for import_root in (project_root, project_root / "python"):
        value = str(import_root)
        if value not in sys.path:
            sys.path.insert(0, value)

    configure_pycharm_debugger()
    return project_root
