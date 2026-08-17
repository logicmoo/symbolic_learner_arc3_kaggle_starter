from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Any, Mapping


NODE_PROLOG_FILES = (
    "objects.pl",
    "differences.pl",
    "similarities.pl",
    "turtle_from_image.pl",
    "turtle_from_diff.pl",
    "rules.pl",
)


def _required_path(value: Any, label: str) -> Path:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"ARC3 artifact bundle requires {label!r}")
    return Path(text).expanduser().resolve()


def _load_check(path: Path, swipl: str | None) -> dict[str, Any]:
    if not path.is_file():
        return {"path": str(path), "exists": False, "nonempty": False, "loadChecked": False}
    result: dict[str, Any] = {
        "path": str(path),
        "exists": True,
        "nonempty": path.stat().st_size > 0,
        "loadChecked": False,
    }
    if not swipl:
        return result
    try:
        completed = subprocess.run(
            [swipl, "-q", "-s", str(path), "-g", "halt"],
            cwd=path.parent,
            capture_output=True,
            text=True,
            check=False,
            timeout=20,
        )
    except subprocess.TimeoutExpired:
        result.update({"loadChecked": True, "loadValid": False, "error": "SWI-Prolog load check timed out"})
        return result
    result.update({
        "loadChecked": True,
        "loadValid": completed.returncode == 0,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    })
    return result


def collect_prolog_evidence(bundle: Mapping[str, Any]) -> dict[str, Any]:
    """Return an inspectable ARC3 Prolog bundle without making an LLM call."""

    if not isinstance(bundle, Mapping):
        raise TypeError("bundle must be an ArtifactBundle object")
    node_root = _required_path(bundle.get("node"), "node")
    registry_path = _required_path(bundle.get("registry"), "registry")
    paths = (registry_path, *(node_root / name for name in NODE_PROLOG_FILES))
    swipl = shutil.which("swipl")
    checks = [_load_check(path, swipl) for path in paths]
    artifacts = {
        path.name: {
            "path": str(path),
            "text": path.read_text(encoding="utf-8") if path.is_file() else "",
        }
        for path in paths
    }
    resolved_bundle = {
        **dict(bundle),
        "node": str(node_root),
        "registry": str(registry_path),
        "prologArtifacts": artifacts,
    }
    validation = {
        "valid": all(check["exists"] and check["nonempty"] and check.get("loadValid", True) for check in checks),
        "provider": "python.callable",
        "llmCalled": False,
        "swipl": swipl,
        "checks": checks,
    }
    return {"bundle": resolved_bundle, "validation": validation}
