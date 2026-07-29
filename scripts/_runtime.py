from __future__ import annotations

import os
import sys
from pathlib import Path

_PROJECT_MARKERS = ("pyproject.toml", "README.md")


def _find_project_root(start: Path) -> Path | None:
    """Return the nearest parent that looks like the ARC3 project root."""
    candidate = start.expanduser().resolve()
    if candidate.is_file():
        candidate = candidate.parent

    for directory in (candidate, *candidate.parents):
        if all((directory / marker).is_file() for marker in _PROJECT_MARKERS):
            return directory
    return None


def configure_runtime_home(script_file: str | Path) -> Path:
    """Resolve and enter the runtime home used by every runnable script.

    Resolution order:

    1. ``ARC3_RUNTIME_HOME`` when explicitly configured.
    2. The current working directory, including its parent directories.
    3. The repository root inferred from the script location.

    An explicitly configured but invalid ``ARC3_RUNTIME_HOME`` is an error rather
    than a reason to silently run against another checkout.
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

    os.environ["ARC3_RUNTIME_HOME"] = str(project_root)
    os.chdir(project_root)

    for import_root in (project_root, project_root / "python"):
        value = str(import_root)
        if value not in sys.path:
            sys.path.insert(0, value)

    return project_root
