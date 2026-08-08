from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from operation_library import DEFAULT_WORKSPACES_ROOT, SHARED_WORKSPACE_ID
from resource_relationships import relationship_ids
from workspace_inheritance import effective_workspace_layers, layer_source


FAMILIES = {
    "goal": ("goals", {"goal", "goal_interpretation", "goal_variant"}),
    "plan": ("plans", {"plan", "plan_variant"}),
    "context": ("contexts", {"context", "context_variant"}),
}


def _read(path: Path, kinds: set[str]) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Invalid symbolic resource {path}: {error}") from error
    if not isinstance(value, dict) or value.get("kind") not in kinds:
        raise ValueError(f"Resource must declare one of {sorted(kinds)}: {path}")
    if not str(value.get("id") or "").strip():
        raise ValueError(f"Resource requires id: {path}")
    if value["kind"] not in {"goal", "plan", "context"} and not relationship_ids(value.get("parents")):
        raise ValueError(f"Variant requires parents: {path}")
    return value


def _records(root: Path, directory: str, kinds: set[str], source: str, workspace_id: str) -> list[dict[str, Any]]:
    resource_dir = root / directory
    if not resource_dir.is_dir():
        return []
    records: list[dict[str, Any]] = []
    for path in sorted(resource_dir.glob("*.json"), key=lambda item: item.name.lower()):
        record: dict[str, Any] = {"path": path.relative_to(root).as_posix(), "source": source, "workspaceId": workspace_id}
        try:
            record["document"] = _read(path, kinds)
        except ValueError as error:
            record["error"] = str(error)
        records.append(record)
    return records


def load_workspace_symbolic_records(workspace_root: Path, family: str, *, workspaces_root: Path = DEFAULT_WORKSPACES_ROOT) -> list[dict[str, Any]]:
    directory, kinds = FAMILIES[family]
    effective: dict[str, dict[str, Any]] = {}
    for layer in effective_workspace_layers(workspace_root, workspaces_root):
        for record in _records(layer, directory, kinds, layer_source(layer, workspace_root), layer.name):
            document = record.get("document") or {}
            effective[str(document.get("id") or record["path"])] = record
    return sorted(effective.values(), key=lambda record: str((record.get("document") or {}).get("label") or record["path"]).lower())


def symbolic_hierarchy(records: list[dict[str, Any]], parent_kind: str) -> dict[str, Any]:
    parents = [record for record in records if (record.get("document") or {}).get("kind") == parent_kind]
    variants = [record for record in records if (record.get("document") or {}).get("kind") != parent_kind]
    by_parent: dict[str, list[dict[str, Any]]] = {}
    for record in variants:
        for parent in relationship_ids(record["document"].get("parents")):
            by_parent.setdefault(parent, []).append(record)
    return {"specifications": parents, "variants": variants, "variantsBySpecification": by_parent}
