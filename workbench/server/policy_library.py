from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from operation_library import DEFAULT_WORKSPACES_ROOT, SHARED_WORKSPACE_ID
from resource_relationships import relationship_ids

POLICY_KINDS = {"model_policy", "model_policy_variant", "vendor_policy", "model_policy_entry", "model_health_observation", "model_ping_job", "model_ping_event", "benchmark_policy", "benchmark_result"}

def _records(root: Path, source: str, workspace_id: str) -> list[dict[str, Any]]:
    directory = root / "policies"
    if not directory.is_dir(): return []
    result: list[dict[str, Any]] = []
    for path in sorted(directory.glob("*.json"), key=lambda value: value.name.lower()):
        record: dict[str, Any] = {"path": path.relative_to(root).as_posix(), "source": source, "workspaceId": workspace_id}
        try:
            document = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(document, dict) or document.get("kind") not in POLICY_KINDS or not document.get("id"): raise ValueError("Policy resource requires an id and supported kind")
            record["document"] = document
        except (OSError, json.JSONDecodeError, ValueError) as error: record["error"] = str(error)
        result.append(record)
    return result

def load_workspace_policy_records(workspace_root: Path, *, workspaces_root: Path = DEFAULT_WORKSPACES_ROOT) -> list[dict[str, Any]]:
    combined: dict[str, dict[str, Any]] = {}
    for record in _records(workspaces_root / SHARED_WORKSPACE_ID, "shared", SHARED_WORKSPACE_ID):
        document = record.get("document") or {}; combined[str(document.get("id") or record["path"])] = record
    if workspace_root.name != SHARED_WORKSPACE_ID:
        for record in _records(workspace_root, "workspace", workspace_root.name):
            document = record.get("document") or {}; combined[str(document.get("id") or record["path"])] = record
    return sorted(combined.values(), key=lambda record: str((record.get("document") or {}).get("label") or record["path"]).lower())

def policy_hierarchy(records: list[dict[str, Any]]) -> dict[str, Any]:
    roots: list[dict[str, Any]] = []; variants: list[dict[str, Any]] = []; children: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        document = record.get("document") or {}; parents = relationship_ids(document.get("parents"))
        if document.get("kind") == "model_policy_variant" and parents:
            variants.append(record)
            for parent in parents: children.setdefault(parent, []).append(record)
        else: roots.append(record)
    return {"roots": roots, "variants": variants, "variantsByParent": children}
