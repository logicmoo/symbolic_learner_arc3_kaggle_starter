from __future__ import annotations

import re
from pathlib import Path
from typing import Any

RESOURCE_KINDS = {
    "artifact-catalog",
    "backend",
    "config",
    "datatype-catalog",
    "model",
    "profile",
    "prompt",
    "task",
    "workflow",
    "workspace",
}


def resource_filename(resource_id: str, kind: str) -> str:
    """Return the canonical `<id>.<kind>.json` filename."""
    if kind not in RESOURCE_KINDS:
        raise ValueError(f"Unsupported resource kind: {kind}")
    safe_id = re.sub(r"[^A-Za-z0-9._-]+", "_", str(resource_id).strip()).strip("._") or "resource"
    suffix = f".{kind}"
    if safe_id.endswith(suffix):
        safe_id = safe_id[: -len(suffix)]
    return f"{safe_id}.{kind}.json"


def filename_kind(path: Path) -> str | None:
    if path.suffix.lower() != ".json":
        return None
    stem = path.name[:-5]
    if "." not in stem:
        return None
    kind = stem.rsplit(".", 1)[1]
    return kind if kind in RESOURCE_KINDS else None


def infer_resource_kind(path: Path, document: dict[str, Any]) -> str | None:
    declared = document.get("kind")
    if isinstance(declared, str) and declared.strip():
        return declared.strip()

    parent = path.parent.name.lower()
    if parent == "tasks":
        return "task"
    if parent == "prompts":
        return "prompt"
    if parent == "workflows":
        return "workflow"
    if parent == "models":
        if document.get("provider"):
            return "backend"
        if document.get("inherits"):
            return "model"
    if parent == "config":
        name = path.stem.lower()
        if "datatype" in name:
            return "datatype-catalog"
        if "artifact" in name:
            return "artifact-catalog"
        return "config"
    if path.name == "workspace.json" or path.name.endswith(".workspace.json"):
        return "workspace"
    return None


def canonical_resource_path(path: Path, document: dict[str, Any]) -> Path:
    kind = infer_resource_kind(path, document)
    if not kind:
        raise ValueError(f"Cannot determine JSON resource kind for {path}")
    resource_id = str(document.get("id") or document.get("title") or path.name[:-5])
    if kind == "workspace" and not document.get("id"):
        resource_id = path.parent.name
    return path.with_name(resource_filename(resource_id, kind))


def validate_kind_filename(path: Path, document: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    declared = document.get("kind")
    if not isinstance(declared, str) or not declared.strip():
        errors.append("missing kind")
        return errors
    declared = declared.strip()
    if declared not in RESOURCE_KINDS:
        errors.append(f"unsupported kind: {declared}")
    suffix_kind = filename_kind(path)
    if suffix_kind != declared:
        errors.append(f"filename must end in .{declared}.json")
    return errors
