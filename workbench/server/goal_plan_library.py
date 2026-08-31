from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from operation_library import DEFAULT_WORKSPACES_ROOT, SHARED_WORKSPACE_ID
from resource_relationships import relationship_ids
from workspace_inheritance import effective_workspace_layers, layer_source
from resource_store import get_filesystem_provider


FAMILIES = {
    "goal": (("design/goals", "design/goal_interpretations", "design/goal_variants", "goals", "goal_interpretations", "goal_variants"), {"goal", "goal_interpretation", "goal_variant"}),
    "plan": (("design/planning_strategies", "design/planning_strategy_variants", "design/plans", "design/plan_variants", "planning_strategies", "planning_strategy_variants", "plans", "plan_variants"), {"planning_strategy", "planning_strategy_variant", "plan", "plan_variant"}),
    "context": (("design/atomspaces", "design/atomspace_variants", "contexts", "context_variants"), {"atomspace", "context", "context_variant"}),
}

BASE_KINDS = {"goal": "goal", "plan": "planning_strategy", "context": "atomspace"}


def _validate(value: Any, path: Path, kinds: set[str], base_kind: str) -> dict[str, Any]:
    if not isinstance(value, dict) or value.get("kind") not in kinds:
        raise ValueError(f"Resource must declare one of {sorted(kinds)}: {path}")
    if not str(value.get("id") or "").strip():
        raise ValueError(f"Resource requires id: {path}")
    declared_kind = str(value["kind"])
    if declared_kind.endswith(("_variant", "_interpretation")) and not relationship_ids(value.get("implements")):
        raise ValueError(f"Variant requires implements: {path}")
    value["kind"] = base_kind
    return value


def _records(root: Path, directories: tuple[str, ...], kinds: set[str], base_kind: str, source: str, workspace_id: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    paths = get_filesystem_provider().glob(root, directories)
    for path in sorted(paths, key=lambda item: item.name.lower()):
        try:
            documents = get_filesystem_provider().read_json_documents(path)
        except (OSError, json.JSONDecodeError, ValueError) as error:
            records.append({"path": path.relative_to(root).as_posix(), "source": source, "workspaceId": workspace_id, "error": str(error)})
            continue
        for resource_index, value in enumerate(documents):
            record: dict[str, Any] = {"path": path.relative_to(root).as_posix(), "source": source, "workspaceId": workspace_id, "resourceIndex": resource_index}
            try:
                record["document"] = _validate(value, path, kinds, base_kind)
            except ValueError as error:
                record["error"] = str(error)
            records.append(record)
    return records


def load_workspace_symbolic_records(workspace_root: Path, family: str, *, workspaces_root: Path = DEFAULT_WORKSPACES_ROOT) -> list[dict[str, Any]]:
    directories, kinds = FAMILIES[family]
    base_kind = BASE_KINDS[family]
    effective: dict[str, dict[str, Any]] = {}
    for layer in effective_workspace_layers(workspace_root, workspaces_root):
        for record in _records(layer, directories, kinds, base_kind, layer_source(layer, workspace_root), layer.name):
            document = record.get("document") or {}
            effective[str(document.get("id") or record["path"])] = record
    return sorted(effective.values(), key=lambda record: str((record.get("document") or {}).get("label") or record["path"]).lower())


def symbolic_hierarchy(records: list[dict[str, Any]], parent_kind: str) -> dict[str, Any]:
    parents = [record for record in records if not relationship_ids((record.get("document") or {}).get("implements"))]
    variants = [record for record in records if relationship_ids((record.get("document") or {}).get("implements"))]
    by_parent: dict[str, list[dict[str, Any]]] = {}
    for record in variants:
        for parent in relationship_ids(record["document"].get("implements")):
            by_parent.setdefault(parent, []).append(record)
    return {"specifications": parents, "variants": variants, "implementedByResource": by_parent}
