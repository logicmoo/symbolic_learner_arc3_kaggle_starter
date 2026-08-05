from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _environment(primary: str, legacy: str) -> str:
    """Read a workbench setting while preserving the ARC3-era name."""
    return os.environ.get(primary, "").strip() or os.environ.get(legacy, "").strip()


def _resolved_path(value: str | Path, *, base: Path) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = base / path
    return path.resolve()


def _launch_cwd() -> Path:
    configured = _environment("WORLD_WORKBENCH_LAUNCH_CWD", "ARC3_LAUNCH_CWD")
    if configured:
        return _resolved_path(configured, base=Path.cwd())
    return Path.cwd().expanduser().resolve()


def _walk_up(start: Path):
    candidate = start.expanduser().resolve()
    if candidate.is_file():
        candidate = candidate.parent
    yield candidate
    yield from candidate.parents


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


def _runtime_root() -> Path | None:
    value = _environment("WORLD_WORKBENCH_HOME", "ARC3_RUNTIME_HOME")
    return _resolved_path(value, base=_launch_cwd()) if value else None


def config_root() -> Path:
    """Return the selected config directory without creating a fake source."""
    explicit_root = _environment("WORLD_WORKBENCH_CONFIG_ROOT", "ARC3_CONFIG_ROOT")
    if explicit_root:
        return _resolved_path(explicit_root, base=_launch_cwd())

    explicit_file = _environment("WORLD_WORKBENCH_LLM_CONFIG", "ARC3_LLM_CONFIG")
    if explicit_file:
        return _resolved_path(explicit_file, base=_launch_cwd()).parent

    nearest = _find_upward_file(
        _launch_cwd(),
        Path("config") / "llm_providers.json",
    )
    if nearest is not None:
        return nearest.parent

    runtime_root = _runtime_root()
    if runtime_root is not None:
        candidate = runtime_root / "config" / "llm_providers.json"
        if candidate.is_file():
            return candidate.parent.resolve()

    return (PROJECT_ROOT / "config").resolve()


def llm_config_path() -> Path:
    configured = _environment("WORLD_WORKBENCH_LLM_CONFIG", "ARC3_LLM_CONFIG")
    if configured:
        path = _resolved_path(configured, base=_launch_cwd())
    else:
        path = config_root() / "llm_providers.json"
    if not path.is_file():
        raise RuntimeError(f"LLM configuration file does not exist: {path}")
    return path.resolve()


def prompts_root() -> Path:
    """Compatibility alias for the unified configuration directory."""
    return config_root()


def environment_files_root() -> Path:
    """Compatibility alias for the unified configuration directory."""
    return config_root()


def action_trees_root() -> Path:
    explicit = _environment("WORLD_WORKBENCH_RUN_ROOT", "ARC3_TREE_ROOT")
    if explicit:
        root = _resolved_path(explicit, base=_launch_cwd())
    else:
        nearest = _find_upward_directory(_launch_cwd(), "action_trees")
        if nearest is not None:
            root = nearest
        else:
            runtime_root = _runtime_root()
            runtime_candidate = (
                runtime_root / "action_trees" if runtime_root is not None else None
            )
            if runtime_candidate is not None and runtime_candidate.is_dir():
                root = runtime_candidate.resolve()
            else:
                root = (PROJECT_ROOT / "action_trees").resolve()
    root.mkdir(parents=True, exist_ok=True)
    return root


def analysis_runs_root() -> Path:
    """Domain-neutral name for the persisted observation/action evidence tree."""
    return action_trees_root()


def prompts_path() -> Path:
    """Compatibility alias for the unified provider and prompt config."""
    return llm_config_path()


def histories_root(level_root: str | Path) -> Path:
    root = Path(level_root) / "histories"
    root.mkdir(parents=True, exist_ok=True)
    return root


def exports_root(level_root: str | Path) -> Path:
    root = Path(level_root) / "exports"
    root.mkdir(parents=True, exist_ok=True)
    return root
