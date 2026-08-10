from __future__ import annotations

import re
from pathlib import Path
from typing import Any

KIND_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")
KNOWN_RESOURCE_KINDS = {
    "artifact_category",
    "artifact_catalog",
    "backend",
    "config",
    "data",
    "semantic_datatype",
    "representation_datatype",
    "concrete_datatype",
    "manifest",
    "model",
    "model_health_observation",
    "model_ping_event",
    "model_ping_job",
    "model_policy",
    "model_policy_entry",
    "model_policy_variant",
    "goal",
    "goal_interpretation",
    "goal_variant",
    "plan",
    "plan_variant",
    "planning_strategy",
    "planning_strategy_variant",
    "context",
    "context_variant",
    "profile",
    "prompt",
    "prompt_profile",
    "prompt_implementation",
    "schema",
    "benchmark_policy",
    "benchmark_result",
    "operation",
    "operation_implementation",
    "atomspace",
    "workflow",
    "workflow_step",
    "workspace",
    "vendor_policy",
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
    if parent in {"operations", "operation_implementations"}:
        return "operation"
    if parent in {"prompts", "prompt_implementations"}:
        return "prompt"
    if parent == "workflows":
        return "workflow"
    if parent in {"goals", "goal_interpretations", "goal_variants"}:
        return "goal"
    if parent in {"planning_strategies", "planning_strategy_variants"}:
        return "planning_strategy"
    if parent in {"plans", "plan_variants"}:
        return "planning_strategy"
    if parent in {"contexts", "context_variants", "atomspaces", "atomspace_variants"}:
        return "atomspace"
    if parent in {"datatypes", "semantic_datatypes"}:
        return "semantic_datatype"
    if parent in {"representations", "representation_datatypes"}:
        return "representation_datatype"
    if parent == "concrete_datatypes":
        return "concrete_datatype"
    if parent in {"backends", "models", "profiles"}:
        if document.get("provider"):
            return "backend"
        if document.get("inherits") or document.get("parents"):
            return "model"
        return "model"
    if parent == "config":
        if "datatype" in name:
            return "config"
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
