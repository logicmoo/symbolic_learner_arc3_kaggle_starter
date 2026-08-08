from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from workspace_inheritance import effective_workspace_layers, layer_source


TREE_KINDS = {
    "goals": {"goal", "goal_interpretation", "goal_variant"},
    "plans": {"plan", "plan_variant"},
    "operations": {"operation", "operation_implementation"},
    "datatypes": {"semantic_datatype", "representation_datatype", "concrete_datatype"},
    "prompts": {"prompt", "prompt_implementation"},
    "models": {"backend", "model", "profile"},
    "atomspaces": {"context", "context_variant"},
    "workflows": {"workflow"},
}


def validate_artifact_category(document: dict[str, Any]) -> None:
    if document.get("kind") != "artifact_category" or not document.get("id"):
        raise ValueError("Artifact category requires kind=artifact_category and id")
    if not isinstance(document.get("path"), str) or not document["path"].strip(" /"):
        raise ValueError("Artifact category requires a non-empty path")
    trees = document.get("trees")
    if not isinstance(trees, list) or not trees or any(tree not in TREE_KINDS for tree in trees):
        raise ValueError("Artifact category requires supported trees")
    query = document.get("query")
    kinds = query.get("kinds") if isinstance(query, dict) else None
    if not isinstance(kinds, list) or not kinds:
        raise ValueError("Artifact category query requires kinds")
    allowed = set().union(*(TREE_KINDS[tree] for tree in trees))
    incompatible = set(kinds) - allowed
    if incompatible:
        raise ValueError(f"Artifact category kinds are incompatible with trees: {sorted(incompatible)}")
    if document.get("parentMode", "user") not in {"hide", "show", "user"}:
        raise ValueError("Artifact category parentMode must be hide, show, or user")


def load_workspace_artifact_categories(workspace_root: Path) -> list[dict[str, Any]]:
    combined: dict[str, dict[str, Any]] = {}
    for layer in effective_workspace_layers(workspace_root, workspace_root.parent):
        directory = layer / "design" / "categories"
        if not directory.is_dir():
            continue
        for path in sorted(directory.glob("*.json")):
            record: dict[str, Any] = {"path": path.relative_to(layer).as_posix(), "source": layer_source(layer, workspace_root), "workspaceId": layer.name}
            try:
                document = json.loads(path.read_text(encoding="utf-8"))
                validate_artifact_category(document)
                record["document"] = document
                combined[str(document["id"])] = record
            except (OSError, json.JSONDecodeError, ValueError) as error:
                record["error"] = str(error)
                combined[record["path"]] = record
    return sorted(combined.values(), key=lambda record: str((record.get("document") or {}).get("path") or record["path"]).lower())


def _value_at(document: dict[str, Any], path: str) -> Any:
    value: Any = document
    for part in path.split("."):
        if not isinstance(value, dict):
            return None
        value = value.get(part)
    return value


def _matches_condition(value: Any, condition: Any) -> bool:
    if not isinstance(condition, dict):
        return value == condition
    if "equals" in condition and value != condition["equals"]:
        return False
    if "startsWith" in condition and not str(value or "").lower().startswith(str(condition["startsWith"]).lower()):
        return False
    if "contains" in condition:
        expected = condition["contains"]
        if isinstance(value, list):
            if not any(str(item).lower() == str(expected).lower() for item in value):
                return False
        elif str(expected).lower() not in str(value or "").lower():
            return False
    if "gte" in condition and not isinstance(value, (int, float)):
        return False
    if "gte" in condition and value < condition["gte"]:
        return False
    if "lte" in condition and not isinstance(value, (int, float)):
        return False
    if "lte" in condition and value > condition["lte"]:
        return False
    return True


def apply_artifact_categories(records: list[dict[str, Any]], categories: list[dict[str, Any]], tree: str) -> list[dict[str, Any]]:
    definitions = [record["document"] for record in categories if record.get("document") and tree in record["document"].get("trees", [])]
    result: list[dict[str, Any]] = []
    for record in records:
        updated = copy.deepcopy(record)
        document = updated.get("document")
        if not isinstance(document, dict):
            result.append(updated)
            continue
        candidate = {**document, "_resolved": updated.get("resolved") or {}}
        resolved: list[dict[str, str]] = []
        for definition in definitions:
            query = definition["query"]
            if document.get("kind") not in query["kinds"]:
                continue
            where = query.get("where") or {}
            if all(_matches_condition(_value_at(candidate, field), condition) for field, condition in where.items()):
                path = str(definition["path"]).strip(" /")
                document["categories"] = list(dict.fromkeys([*(document.get("categories") or []), path]))
                resolved.append({"id": definition["id"], "path": path, "parentMode": definition.get("parentMode", "user")})
        if resolved:
            updated["resolvedArtifactCategories"] = resolved
        result.append(updated)
    return result
