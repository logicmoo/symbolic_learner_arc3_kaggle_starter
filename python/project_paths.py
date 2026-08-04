from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def config_root() -> Path:
    root = Path(os.environ.get("ARC3_CONFIG_ROOT") or PROJECT_ROOT / "config")
    root = root.expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    return root


def llm_config_path() -> Path:
    configured = os.environ.get("ARC3_LLM_CONFIG", "").strip()
    if configured:
        return Path(configured).expanduser().resolve()
    return config_root() / "llm_providers.json"


def prompts_root() -> Path:
    """Compatibility alias for the unified configuration directory."""
    return config_root()


def environment_files_root() -> Path:
    """Compatibility alias for the unified configuration directory."""
    return config_root()


def action_trees_root() -> Path:
    root = Path(os.environ.get("ARC3_TREE_ROOT") or PROJECT_ROOT / "action_trees")
    root = root.expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    return root


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
