from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_WORKSPACES_ROOT = REPOSITORY_ROOT / "workbench" / "workspaces"
SHARED_WORKSPACE_ID = "shared"


def read_task_file(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Invalid task definition {path}: {error}") from error
    if not isinstance(value, dict):
        raise ValueError(f"Task definition must be a JSON object: {path}")
    declared_kind = value.get("kind")
    if declared_kind not in (None, "task"):
        raise ValueError(f"Task definition must declare kind='task': {path}")
    value.setdefault("kind", "task")
    if not str(value.get("id") or "").strip():
        raise ValueError(f"Task definition requires id: {path}")
    if not str(value.get("implementation") or "").strip():
        raise ValueError(f"Task definition requires implementation: {path}")
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
            "convention": "canonical" if path.name.endswith(".task.json") else "legacy-filename",
        }
        try:
            record["document"] = read_task_file(path)
        except ValueError as error:
            record["error"] = str(error)
        records.append(record)
    return records


def load_shared_task_records(workspaces_root: Path = DEFAULT_WORKSPACES_ROOT) -> list[dict[str, Any]]:
    shared_root = workspaces_root / SHARED_WORKSPACE_ID
    return _task_records(shared_root, "shared", SHARED_WORKSPACE_ID)


def load_workspace_task_records(
    workspace_root: Path,
    *,
    workspaces_root: Path = DEFAULT_WORKSPACES_ROOT,
) -> list[dict[str, Any]]:
    """Return shared tasks plus workspace-specific overrides by task ID."""
    combined: dict[str, dict[str, Any]] = {}
    for record in load_shared_task_records(workspaces_root):
        document = record.get("document") or {}
        key = str(document.get("id") or record["path"])
        combined[key] = record

    workspace_id = workspace_root.name
    if workspace_id != SHARED_WORKSPACE_ID:
        for record in _task_records(workspace_root, "workspace", workspace_id):
            document = record.get("document") or {}
            key = str(document.get("id") or record["path"])
            combined[key] = record

    return sorted(
        combined.values(),
        key=lambda item: str((item.get("document") or {}).get("label") or item["path"]).lower(),
    )


def load_shared_task_documents(workspaces_root: Path = DEFAULT_WORKSPACES_ROOT) -> list[dict[str, Any]]:
    return [record["document"] for record in load_shared_task_records(workspaces_root) if "document" in record]


def load_effective_task_documents(
    workspace_root: Path,
    *,
    workspaces_root: Path = DEFAULT_WORKSPACES_ROOT,
) -> list[dict[str, Any]]:
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
        result.append(
            {
                "id": document["id"],
                "label": document.get("label") or document["id"],
                "ports": f"{left} → {right}",
                "routes": str(document.get("implementation") or ""),
                "definition": document,
                "source": "workbench/workspaces/shared/tasks",
            }
        )
    return sorted(result, key=lambda item: str(item["label"]).lower())
