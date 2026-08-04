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
_PATHS_REPORTED = False


def _resolved_path(value: str | Path, *, base: Path | None = None) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = (base or Path.cwd()) / path
    return path.resolve()


def _walk_up(start: Path):
    candidate = start.expanduser().resolve()
    if candidate.is_file():
        candidate = candidate.parent
    yield candidate
    yield from candidate.parents


def _find_project_root(start: Path) -> Path | None:
    """Return the nearest parent that looks like the ARC3 code checkout."""
    for directory in _walk_up(start):
        if all((directory / marker).is_file() for marker in _PROJECT_MARKERS):
            return directory
    return None


def _find_upward_file(start: Path, relative: str | Path) -> Path | None:
    relative_path = Path(relative)
    for directory in _walk_up(start):
        candidate = directory / relative_path
        if candidate.is_file():
            return candidate.resolve()
    return None


def _find_upward_directory(start: Path, name: str) -> Path | None:
    for directory in _walk_up(start):
        if directory.name.lower() == name.lower() and directory.is_dir():
            return directory.resolve()
        candidate = directory / name
        if candidate.is_dir():
            return candidate.resolve()
    return None


def _unique_paths(paths):
    seen: set[Path] = set()
    for path in paths:
        if path is None:
            continue
        resolved = Path(path).resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        yield resolved


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


def _load_environment_files(paths) -> tuple[Path, ...]:
    """Load nearest/user-local .env files first without replacing shell values."""
    existing = tuple(path for path in _unique_paths(paths) if path.is_file())
    if not existing:
        return ()

    try:
        from dotenv import load_dotenv
    except ImportError as error:
        joined = ", ".join(str(path) for path in existing)
        raise RuntimeError(
            f"Environment file(s) exist but python-dotenv is not installed: {joined}. "
            "Reinstall the project dependencies before launching ARC3."
        ) from error

    for path in existing:
        load_dotenv(dotenv_path=path, override=False)
    return existing


def _resolve_code_root(
    *,
    launch_cwd: Path,
    script_file: Path,
    script_root: Path | None,
) -> tuple[Path, str]:
    configured = os.environ.get("ARC3_RUNTIME_HOME", "").strip()
    if configured:
        configured_path = _resolved_path(configured, base=launch_cwd)
        root = _find_project_root(configured_path)
        if root is None:
            raise RuntimeError(
                "ARC3_RUNTIME_HOME does not point inside a valid project root: "
                f"{configured!r}"
            )
        return root, "ARC3_RUNTIME_HOME"

    cwd_root = _find_project_root(launch_cwd)
    if cwd_root is not None:
        return cwd_root, "launch directory search"
    if script_root is not None:
        return script_root, "script/code location"
    raise RuntimeError(f"Unable to locate the ARC3 code root from {script_file!r}")


def _resolve_llm_config(
    *,
    launch_cwd: Path,
    configured_root: Path | None,
    script_root: Path | None,
    code_root: Path,
) -> tuple[Path, str]:
    explicit_file = os.environ.get("ARC3_LLM_CONFIG", "").strip()
    if explicit_file:
        path = _resolved_path(explicit_file, base=launch_cwd)
        if not path.is_file():
            raise RuntimeError(f"ARC3_LLM_CONFIG does not exist: {path}")
        return path, "ARC3_LLM_CONFIG"

    explicit_root = os.environ.get("ARC3_CONFIG_ROOT", "").strip()
    if explicit_root:
        root = _resolved_path(explicit_root, base=launch_cwd)
        path = root / "llm_providers.json"
        if not path.is_file():
            raise RuntimeError(
                "ARC3_CONFIG_ROOT does not contain llm_providers.json: "
                f"{root}"
            )
        return path.resolve(), "ARC3_CONFIG_ROOT"

    nearest = _find_upward_file(launch_cwd, Path("config") / "llm_providers.json")
    if nearest is not None:
        return nearest, "launch directory config search"

    candidates = (
        (configured_root, "ARC3_RUNTIME_HOME/config"),
        (script_root, "script/code config"),
        (code_root, "code-root config"),
    )
    for root, source in candidates:
        if root is None:
            continue
        path = root / "config" / "llm_providers.json"
        if path.is_file():
            return path.resolve(), source

    raise RuntimeError(
        "Unable to locate config/llm_providers.json from the launch directory, "
        "ARC3_RUNTIME_HOME, or script/code checkout"
    )


def _resolve_action_trees(
    *,
    launch_cwd: Path,
    configured_root: Path | None,
    script_root: Path | None,
    code_root: Path,
) -> tuple[Path, str]:
    explicit = os.environ.get("ARC3_TREE_ROOT", "").strip()
    if explicit:
        root = _resolved_path(explicit, base=launch_cwd)
        root.mkdir(parents=True, exist_ok=True)
        return root, "ARC3_TREE_ROOT"

    nearest = _find_upward_directory(launch_cwd, "action_trees")
    if nearest is not None:
        return nearest, "launch directory action_trees search"

    candidates = (
        (configured_root, "ARC3_RUNTIME_HOME/action_trees"),
        (script_root, "script/code action_trees"),
        (code_root, "code-root action_trees"),
    )
    for root, source in candidates:
        if root is None:
            continue
        path = root / "action_trees"
        if path.is_dir():
            return path.resolve(), source

    # No existing tree was found. Keep the historical default beside the code
    # checkout instead of silently creating a new tree in an arbitrary subdir.
    fallback = code_root / "action_trees"
    fallback.mkdir(parents=True, exist_ok=True)
    return fallback.resolve(), "created at code root"


def _report_runtime_paths(
    *,
    launch_cwd: Path,
    code_root: Path,
    code_source: str,
    config_path: Path,
    config_source: str,
    tree_root: Path,
    tree_source: str,
    env_files: tuple[Path, ...],
) -> None:
    global _PATHS_REPORTED
    if _PATHS_REPORTED:
        return
    _PATHS_REPORTED = True

    default_enabled = "pytest" not in sys.modules
    if not _env_bool("ARC3_SHOW_PATHS", default_enabled):
        return

    print("\nARC3 resolved paths")
    print(f"  Launch directory: {launch_cwd}")
    print(f"  Code/runtime root: {code_root}  [{code_source}]")
    if env_files:
        print("  Environment files:")
        for path in env_files:
            print(f"    - {path}")
    else:
        print("  Environment files: none")
    print(f"  LLM config source: {config_path}  [{config_source}]")
    print(f"  Action-tree output: {tree_root}  [{tree_source}]")


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
                print("The port must be between 1 and 65535")
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
    """Resolve code and data resources independently, then configure imports.

    Resource discovery is intentionally layered rather than tied to one global
    root. For each resource, explicit environment variables win; otherwise the
    nearest matching resource found while walking upward from the directory in
    which ARC3 was launched wins. ARC3_RUNTIME_HOME and the script/code checkout
    are fallbacks when the launch workspace does not provide that resource.
    """
    launch_cwd = Path.cwd().expanduser().resolve()
    script_path = _resolved_path(script_file, base=launch_cwd)
    script_root = _find_project_root(script_path)

    initial_runtime = os.environ.get("ARC3_RUNTIME_HOME", "").strip()
    initial_runtime_root = (
        _find_project_root(_resolved_path(initial_runtime, base=launch_cwd))
        if initial_runtime
        else None
    )

    launch_env = _find_upward_file(launch_cwd, ".env")
    runtime_env = (
        initial_runtime_root / ".env" if initial_runtime_root is not None else None
    )
    script_env = script_root / ".env" if script_root is not None else None
    env_files = _load_environment_files((launch_env, runtime_env, script_env))

    code_root, code_source = _resolve_code_root(
        launch_cwd=launch_cwd,
        script_file=script_path,
        script_root=script_root,
    )
    configured_root = None
    configured_value = os.environ.get("ARC3_RUNTIME_HOME", "").strip()
    if configured_value:
        configured_root = _find_project_root(
            _resolved_path(configured_value, base=launch_cwd)
        )

    code_env = code_root / ".env"
    if code_env.is_file() and code_env.resolve() not in set(env_files):
        env_files = env_files + _load_environment_files((code_env,))

    config_path, config_source = _resolve_llm_config(
        launch_cwd=launch_cwd,
        configured_root=configured_root,
        script_root=script_root,
        code_root=code_root,
    )
    tree_root, tree_source = _resolve_action_trees(
        launch_cwd=launch_cwd,
        configured_root=configured_root,
        script_root=script_root,
        code_root=code_root,
    )

    os.environ["ARC3_LAUNCH_CWD"] = str(launch_cwd)
    os.environ["ARC3_RUNTIME_HOME"] = str(code_root)
    os.environ["ARC3_CODE_ROOT"] = str(code_root)
    os.environ["ARC3_CONFIG_ROOT"] = str(config_path.parent)
    os.environ["ARC3_LLM_CONFIG"] = str(config_path)
    os.environ["ARC3_TREE_ROOT"] = str(tree_root)
    os.environ["ARC3_CONFIG_SOURCE"] = config_source
    os.environ["ARC3_TREE_SOURCE"] = tree_source
    os.environ["ARC3_ENV_FILES"] = os.pathsep.join(str(path) for path in env_files)

    # Preserve historical script behavior for relative imports, while resource
    # paths remain pinned to the launch workspace discovered above.
    os.chdir(code_root)
    for import_root in (code_root, code_root / "python"):
        value = str(import_root)
        if value not in sys.path:
            sys.path.insert(0, value)

    _report_runtime_paths(
        launch_cwd=launch_cwd,
        code_root=code_root,
        code_source=code_source,
        config_path=config_path,
        config_source=config_source,
        tree_root=tree_root,
        tree_source=tree_source,
        env_files=env_files,
    )
    configure_pycharm_debugger()
    return code_root
