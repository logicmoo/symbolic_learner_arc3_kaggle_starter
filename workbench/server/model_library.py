from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from task_library import DEFAULT_WORKSPACES_ROOT

SHARED_WORKSPACE_ID = "shared"


def read_model_file(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Invalid model definition {path}: {error}") from error
    if not isinstance(value, dict):
        raise ValueError(f"Model definition must be a JSON object: {path}")
    if value.get("kind") != "model":
        raise ValueError(f"Model definition must declare kind='model': {path}")
    if not str(value.get("id") or "").strip():
        raise ValueError(f"Model definition requires id: {path}")
    if not str(value.get("backend") or "").strip():
        raise ValueError(f"Model definition requires backend: {path}")
    if not str(value.get("model") or "").strip():
        raise ValueError(f"Model definition requires model: {path}")
    return value


def _model_records(workspace_root: Path, source: str, workspace_id: str) -> list[dict[str, Any]]:
    directory = workspace_root / "models"
    if not directory.is_dir():
        return []
    records: list[dict[str, Any]] = []
    for path in sorted(directory.glob("*.json"), key=lambda item: item.name.lower()):
        record: dict[str, Any] = {
            "path": path.relative_to(workspace_root).as_posix(),
            "source": source,
            "workspaceId": workspace_id,
        }
        try:
            record["document"] = read_model_file(path)
        except ValueError as error:
            record["error"] = str(error)
        records.append(record)
    return records


def load_shared_model_records(workspaces_root: Path = DEFAULT_WORKSPACES_ROOT) -> list[dict[str, Any]]:
    return _model_records(workspaces_root / SHARED_WORKSPACE_ID, "shared", SHARED_WORKSPACE_ID)


def load_workspace_model_records(
    workspace_root: Path,
    *,
    workspaces_root: Path = DEFAULT_WORKSPACES_ROOT,
) -> list[dict[str, Any]]:
    """Merge shared models with workspace-specific overrides by model ID."""
    combined: dict[str, dict[str, Any]] = {}
    for record in load_shared_model_records(workspaces_root):
        document = record.get("document") or {}
        combined[str(document.get("id") or record["path"])] = record

    workspace_id = workspace_root.name
    if workspace_id != SHARED_WORKSPACE_ID:
        for record in _model_records(workspace_root, "workspace", workspace_id):
            document = record.get("document") or {}
            combined[str(document.get("id") or record["path"])] = record

    return sorted(
        combined.values(),
        key=lambda item: str((item.get("document") or {}).get("label") or item["path"]).lower(),
    )


def load_effective_model_documents(workspace_root: Path) -> list[dict[str, Any]]:
    return [record["document"] for record in load_workspace_model_records(workspace_root) if "document" in record]
