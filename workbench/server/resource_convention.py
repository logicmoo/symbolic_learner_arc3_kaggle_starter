from __future__ import annotations

import re
from pathlib import Path
from typing import Any

KIND_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")
KNOWN_RESOURCE_KINDS = {
    "artifact_catalog",
    "backend",
    "config",
    "data",
    "datatype",
    "datatype_catalog",
    "datatype_representation",
    "manifest",
    "model",
    "goal",
    "goal_interpretation",
    "goal_variant",
    "plan",
    "plan_variant",
    "profile",
    "prompt",
    "prompt_implementation",
    "schema",
    "operation",
    "operation_implementation",
    "workflow",
    "workflow_step",
    "workspace",
}


def normalize_kind(kind: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "_", str(kind).strip().lower()).strip("_")
    if not value or not KIND_PATTERN.fullmatch(value):
        raise ValueError(f"Invalid resource kind: {kind!r}")
    return value


def resource_filename(resource_id: str, kind: str) -> str:
    """Return the canonical `<id>.<kind>.json` filename."""
    kind = normalize_kind(kind)
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
    candidate = stem.rsplit(".", 1)[1].lower()
    return candidate if KIND_PATTERN.fullmatch(candidate) else None


def infer_resource_kind(path: Path, document: dict[str, Any]) -> str:
    declared = document.get("kind")
    if isinstance(declared, str) and declared.strip():
        return normalize_kind(declared)

    parent = path.parent.name.lower()
    name = path.stem.lower()
    if parent == "operations":
        return "operation_implementation" if document.get("implements") else "operation"
    if parent == "prompts":
        return "prompt_implementation" if document.get("implements") else "prompt"
    if parent == "workflows":
        return "workflow"
    if parent == "goals":
        return "goal_variant" if document.get("implements") else "goal"
    if parent == "plans":
        return "plan_variant" if document.get("implements") else "plan"
    if parent == "datatypes":
        return "datatype"
    if parent == "representations":
        return "datatype_representation"
    if parent == "models":
        if document.get("provider"):
            return "backend"
        if document.get("inherits"):
            return "profile" if any(token in name for token in ("light", "deep", "extreme", "profile")) else "model"
        return "model"
    if parent == "config":
        if "datatype" in name:
            return "datatype_catalog"
        if "artifact" in name:
            return "artifact_catalog"
        if "schema" in name:
            return "schema"
        if "manifest" in name:
            return "manifest"
        return "config"
    if path.name == "workspace.json" or path.name.endswith(".workspace.json"):
        return "workspace"
    if "manifest" in name:
        return "manifest"
    if "schema" in name:
        return "schema"
    return "data"


def _base_name_without_kind(path: Path) -> str:
    stem = path.name[:-5] if path.name.lower().endswith(".json") else path.stem
    suffix_kind = filename_kind(path)
    if suffix_kind:
        return stem[: -(len(suffix_kind) + 1)]
    return stem


def canonical_resource_path(path: Path, document: dict[str, Any]) -> Path:
    kind = infer_resource_kind(path, document)
    resource_id = str(document.get("id") or _base_name_without_kind(path))
    if kind == "workspace" and not document.get("id"):
        resource_id = path.parent.name
    return path.with_name(resource_filename(resource_id, kind))


def validate_kind_filename(path: Path, document: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    declared = document.get("kind")
    if not isinstance(declared, str) or not declared.strip():
        errors.append("missing kind")
        return errors
    try:
        declared = normalize_kind(declared)
    except ValueError as error:
        errors.append(str(error))
        return errors
    suffix_kind = filename_kind(path)
    if suffix_kind != declared:
        errors.append(f"filename must end in .{declared}.json")
    return errors
