from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from resource_relationships import points_to, relationship_ids


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_WORKSPACES_ROOT = REPOSITORY_ROOT / "workbench" / "workspaces"
SHARED_WORKSPACE_ID = "shared"
OPERATION_KINDS = {"operation", "operation_implementation"}


def read_operation_file(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Invalid operation definition {path}: {error}") from error
    if not isinstance(value, dict):
        raise ValueError(f"Operation definition must be a JSON object: {path}")
    raw_kind = str(value.get("kind") or "operation")
    kind = raw_kind.replace("-", "_")
    if kind not in OPERATION_KINDS:
        raise ValueError(f"Operation definition must declare kind='operation' or kind='operation_implementation': {path}")
    value["kind"] = kind
    if not str(value.get("id") or "").strip():
        raise ValueError(f"Operation definition requires id: {path}")
    if kind == "operation_implementation":
        if not relationship_ids(value.get("parents")):
            raise ValueError(f"Operation implementation requires parents: {path}")
        if not str(value.get("implementation") or "").strip():
            raise ValueError(f"Operation implementation requires implementation: {path}")
    return value


def _operation_records(workspace_root: Path, source: str, workspace_id: str) -> list[dict[str, Any]]:
    operation_dir = workspace_root / "operations"
    if not operation_dir.is_dir():
        return []
    records: list[dict[str, Any]] = []
    for path in sorted(operation_dir.glob("*.json"), key=lambda item: item.name.lower()):
        record: dict[str, Any] = {
            "path": path.relative_to(workspace_root).as_posix(),
            "source": source,
            "workspaceId": workspace_id,
        }
        try:
            document = read_operation_file(path)
            record["document"] = document
            expected = f".{document['kind']}.json"
            record["convention"] = "canonical" if path.name.endswith(expected) else "legacy-filename"
        except ValueError as error:
            record["error"] = str(error)
        records.append(record)
    return records


def load_shared_operation_resource_records(workspaces_root: Path = DEFAULT_WORKSPACES_ROOT) -> list[dict[str, Any]]:
    return _operation_records(workspaces_root / SHARED_WORKSPACE_ID, "shared", SHARED_WORKSPACE_ID)


def load_workspace_local_operation_resource_records(workspace_root: Path) -> list[dict[str, Any]]:
    if workspace_root.name == SHARED_WORKSPACE_ID:
        return []
    return _operation_records(workspace_root, "workspace", workspace_root.name)


def _effective_resources(workspace_root: Path, *, workspaces_root: Path = DEFAULT_WORKSPACES_ROOT) -> list[dict[str, Any]]:
    combined: dict[str, dict[str, Any]] = {}
    for record in load_shared_operation_resource_records(workspaces_root):
        document = record.get("document") or {}
        combined[str(document.get("id") or record["path"])] = record
    for record in load_workspace_local_operation_resource_records(workspace_root):
        document = record.get("document") or {}
        combined[str(document.get("id") or record["path"])] = record
    return sorted(combined.values(), key=lambda item: str((item.get("document") or {}).get("label") or item["path"]).lower())


def load_shared_operation_records(workspaces_root: Path = DEFAULT_WORKSPACES_ROOT) -> list[dict[str, Any]]:
    return [r for r in load_shared_operation_resource_records(workspaces_root) if (r.get("document") or {}).get("kind") == "operation"]


def load_shared_operation_implementation_records(workspaces_root: Path = DEFAULT_WORKSPACES_ROOT) -> list[dict[str, Any]]:
    return [r for r in load_shared_operation_resource_records(workspaces_root) if (r.get("document") or {}).get("kind") == "operation_implementation"]


def load_workspace_operation_records(workspace_root: Path, *, workspaces_root: Path = DEFAULT_WORKSPACES_ROOT) -> list[dict[str, Any]]:
    return [r for r in _effective_resources(workspace_root, workspaces_root=workspaces_root) if (r.get("document") or {}).get("kind") == "operation"]


def load_workspace_operation_implementation_records(workspace_root: Path, *, workspaces_root: Path = DEFAULT_WORKSPACES_ROOT) -> list[dict[str, Any]]:
    return [r for r in _effective_resources(workspace_root, workspaces_root=workspaces_root) if (r.get("document") or {}).get("kind") == "operation_implementation"]


def resolve_operation_implementation(workspace_root: Path, operation_id: str, requested: str | None = None, *, workspaces_root: Path = DEFAULT_WORKSPACES_ROOT) -> dict[str, Any]:
    operations = {str((r.get("document") or {}).get("id")): r for r in load_workspace_operation_records(workspace_root, workspaces_root=workspaces_root)}
    implementations = {str((r.get("document") or {}).get("id")): r for r in load_workspace_operation_implementation_records(workspace_root, workspaces_root=workspaces_root)}
    operation_record = operations.get(operation_id)
    if not operation_record:
        raise KeyError(f"operation not found: {operation_id}")
    operation = operation_record["document"]
    variants = relationship_ids(operation.get("children"))
    chosen = requested or operation.get("preferredChild") or (variants[0] if variants else None)
    if not chosen:
        raise ValueError(f"operation has no implementation variant: {operation_id}")
    if variants and chosen not in variants:
        raise ValueError(f"implementation {chosen} is not allowed by operation {operation_id}")
    record = implementations.get(str(chosen))
    if not record:
        raise KeyError(f"operation implementation not found: {chosen}")
    implementation = record["document"]
    if not points_to(implementation, "parents", operation_id):
        raise ValueError(f"implementation {chosen} does not implement {operation_id}")
    return {"operation": operation, "operationRecord": operation_record, "implementation": implementation, "implementationRecord": record}


def load_shared_operation_documents(workspaces_root: Path = DEFAULT_WORKSPACES_ROOT) -> list[dict[str, Any]]:
    return [record["document"] for record in load_shared_operation_records(workspaces_root) if "document" in record]


def load_effective_operation_documents(workspace_root: Path, *, workspaces_root: Path = DEFAULT_WORKSPACES_ROOT) -> list[dict[str, Any]]:
    return [record["document"] for record in load_workspace_operation_records(workspace_root, workspaces_root=workspaces_root) if "document" in record]


def operation_ids(documents: Iterable[dict[str, Any]]) -> set[str]:
    return {str(document["id"]) for document in documents if document.get("id")}


def legacy_catalog_view(documents: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for document in documents:
        inputs = document.get("inputs") or {}
        outputs = document.get("outputs") or {}
        left = " + ".join(inputs) or "∅"
        right = " + ".join(outputs) or "∅"
        routes = str(document.get("preferredChild") or document.get("implementation") or "")
        result.append({"id": document["id"], "label": document.get("label") or document["id"], "ports": f"{left} → {right}", "routes": routes, "definition": document, "source": "workbench/workspaces/shared/operations"})
    return sorted(result, key=lambda item: str(item["label"]).lower())
