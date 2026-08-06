from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_WORKSPACES_ROOT = REPOSITORY_ROOT / "workbench" / "workspaces"
SHARED_WORKSPACE_ID = "shared"
TASK_KINDS = {"task", "task_implementation"}


def read_task_file(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Invalid task definition {path}: {error}") from error
    if not isinstance(value, dict):
        raise ValueError(f"Task definition must be a JSON object: {path}")
    raw_kind = str(value.get("kind") or "task")
    kind = raw_kind.replace("-", "_")
    if kind not in TASK_KINDS:
        raise ValueError(f"Task definition must declare kind='task' or kind='task_implementation': {path}")
    value["kind"] = kind
    if not str(value.get("id") or "").strip():
        raise ValueError(f"Task definition requires id: {path}")
    if kind == "task_implementation":
        if not str(value.get("implements") or "").strip():
            raise ValueError(f"Task implementation requires implements: {path}")
        if not str(value.get("implementation") or "").strip():
            raise ValueError(f"Task implementation requires implementation: {path}")
    return value


def _task_records(workspace_root: Path, source: str, workspace_id: str) -> list[dict[str, Any]]:
    task_dir = workspace_root / "tasks"
    if not task_dir.is_dir():
        return []
    records: list[dict[str, Any]] = []
    for path in sorted(task_dir.glob("*.json"), key=lambda item: item.name.lower()):
        record: dict[str, Any] = {
            "path": path.relative_to(workspace_root).as_posix(),
            "source": source,
            "workspaceId": workspace_id,
        }
        try:
            document = read_task_file(path)
            record["document"] = document
            expected = f".{document['kind']}.json"
            record["convention"] = "canonical" if path.name.endswith(expected) else "legacy-filename"
        except ValueError as error:
            record["error"] = str(error)
        records.append(record)
    return records


def load_shared_task_resource_records(workspaces_root: Path = DEFAULT_WORKSPACES_ROOT) -> list[dict[str, Any]]:
    return _task_records(workspaces_root / SHARED_WORKSPACE_ID, "shared", SHARED_WORKSPACE_ID)


def load_workspace_local_task_resource_records(workspace_root: Path) -> list[dict[str, Any]]:
    if workspace_root.name == SHARED_WORKSPACE_ID:
        return []
    return _task_records(workspace_root, "workspace", workspace_root.name)


def _effective_resources(workspace_root: Path, *, workspaces_root: Path = DEFAULT_WORKSPACES_ROOT) -> list[dict[str, Any]]:
    combined: dict[str, dict[str, Any]] = {}
    for record in load_shared_task_resource_records(workspaces_root):
        document = record.get("document") or {}
        combined[str(document.get("id") or record["path"])] = record
    for record in load_workspace_local_task_resource_records(workspace_root):
        document = record.get("document") or {}
        combined[str(document.get("id") or record["path"])] = record
    return sorted(combined.values(), key=lambda item: str((item.get("document") or {}).get("label") or item["path"]).lower())


def load_shared_task_records(workspaces_root: Path = DEFAULT_WORKSPACES_ROOT) -> list[dict[str, Any]]:
    return [r for r in load_shared_task_resource_records(workspaces_root) if (r.get("document") or {}).get("kind") == "task"]


def load_shared_task_implementation_records(workspaces_root: Path = DEFAULT_WORKSPACES_ROOT) -> list[dict[str, Any]]:
    return [r for r in load_shared_task_resource_records(workspaces_root) if (r.get("document") or {}).get("kind") == "task_implementation"]


def load_workspace_task_records(workspace_root: Path, *, workspaces_root: Path = DEFAULT_WORKSPACES_ROOT) -> list[dict[str, Any]]:
    return [r for r in _effective_resources(workspace_root, workspaces_root=workspaces_root) if (r.get("document") or {}).get("kind") == "task"]


def load_workspace_task_implementation_records(workspace_root: Path, *, workspaces_root: Path = DEFAULT_WORKSPACES_ROOT) -> list[dict[str, Any]]:
    return [r for r in _effective_resources(workspace_root, workspaces_root=workspaces_root) if (r.get("document") or {}).get("kind") == "task_implementation"]


def resolve_task_implementation(workspace_root: Path, task_id: str, requested: str | None = None, *, workspaces_root: Path = DEFAULT_WORKSPACES_ROOT) -> dict[str, Any]:
    tasks = {str((r.get("document") or {}).get("id")): r for r in load_workspace_task_records(workspace_root, workspaces_root=workspaces_root)}
    implementations = {str((r.get("document") or {}).get("id")): r for r in load_workspace_task_implementation_records(workspace_root, workspaces_root=workspaces_root)}
    task_record = tasks.get(task_id)
    if not task_record:
        raise KeyError(f"task not found: {task_id}")
    task = task_record["document"]
    selection = task.get("implementationSelection") or {}
    variants = [str(v) for v in selection.get("variants") or []]
    chosen = requested or selection.get("default") or (variants[0] if variants else None)
    if not chosen:
        raise ValueError(f"task has no implementation variant: {task_id}")
    if variants and chosen not in variants:
        raise ValueError(f"implementation {chosen} is not allowed by task {task_id}")
    record = implementations.get(str(chosen))
    if not record:
        raise KeyError(f"task implementation not found: {chosen}")
    implementation = record["document"]
    if implementation.get("implements") != task_id:
        raise ValueError(f"implementation {chosen} does not implement {task_id}")
    return {"task": task, "taskRecord": task_record, "implementation": implementation, "implementationRecord": record}


def load_shared_task_documents(workspaces_root: Path = DEFAULT_WORKSPACES_ROOT) -> list[dict[str, Any]]:
    return [record["document"] for record in load_shared_task_records(workspaces_root) if "document" in record]


def load_effective_task_documents(workspace_root: Path, *, workspaces_root: Path = DEFAULT_WORKSPACES_ROOT) -> list[dict[str, Any]]:
    return [record["document"] for record in load_workspace_task_records(workspace_root, workspaces_root=workspaces_root) if "document" in record]


def task_ids(documents: Iterable[dict[str, Any]]) -> set[str]:
    return {str(document["id"]) for document in documents if document.get("id")}


def legacy_catalog_view(documents: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for document in documents:
        inputs = document.get("inputs") or {}
        outputs = document.get("outputs") or {}
        left = " + ".join(inputs) or "∅"
        right = " + ".join(outputs) or "∅"
        selection = document.get("implementationSelection") or {}
        routes = str(selection.get("default") or document.get("implementation") or "")
        result.append({"id": document["id"], "label": document.get("label") or document["id"], "ports": f"{left} → {right}", "routes": routes, "definition": document, "source": "workbench/workspaces/shared/tasks"})
    return sorted(result, key=lambda item: str(item["label"]).lower())
