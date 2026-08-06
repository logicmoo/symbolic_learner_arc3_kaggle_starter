from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from task_library import DEFAULT_WORKSPACES_ROOT

SHARED_WORKSPACE_ID = "shared"
PROMPT_DIRECTORY = "prompts"


def read_prompt_file(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Invalid prompt definition {path}: {error}") from error
    if not isinstance(value, dict):
        raise ValueError(f"Prompt definition must be a JSON object: {path}")
    if value.get("kind") != "prompt":
        raise ValueError(f"Prompt definition must declare kind='prompt': {path}")
    if not str(value.get("id") or "").strip():
        raise ValueError(f"Prompt definition requires id: {path}")
    text = value.get("text")
    if not isinstance(text, (str, list)):
        raise ValueError(f"Prompt definition requires text as a string or list of strings: {path}")
    if isinstance(text, list) and not all(isinstance(item, str) for item in text):
        raise ValueError(f"Prompt text list must contain only strings: {path}")
    return value


def _prompt_records(workspace_root: Path, source: str, workspace_id: str) -> list[dict[str, Any]]:
    directory = workspace_root / PROMPT_DIRECTORY
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
            record["document"] = read_prompt_file(path)
        except ValueError as error:
            record["error"] = str(error)
        records.append(record)
    return records


def load_shared_prompt_records(workspaces_root: Path = DEFAULT_WORKSPACES_ROOT) -> list[dict[str, Any]]:
    return _prompt_records(workspaces_root / SHARED_WORKSPACE_ID, "shared", SHARED_WORKSPACE_ID)


def load_workspace_local_prompt_records(workspace_root: Path) -> list[dict[str, Any]]:
    if workspace_root.name == SHARED_WORKSPACE_ID:
        return []
    return _prompt_records(workspace_root, "workspace", workspace_root.name)


def load_workspace_prompt_records(
    workspace_root: Path,
    *,
    workspaces_root: Path = DEFAULT_WORKSPACES_ROOT,
) -> list[dict[str, Any]]:
    combined: dict[str, dict[str, Any]] = {}
    for record in load_shared_prompt_records(workspaces_root):
        document = record.get("document") or {}
        combined[str(document.get("id") or record["path"])] = record
    for record in load_workspace_local_prompt_records(workspace_root):
        document = record.get("document") or {}
        combined[str(document.get("id") or record["path"])] = record
    return sorted(
        combined.values(),
        key=lambda item: str((item.get("document") or {}).get("label") or item["path"]).lower(),
    )


def load_prompt_library_records(
    workspace_root: Path,
    *,
    workspaces_root: Path = DEFAULT_WORKSPACES_ROOT,
) -> dict[str, list[dict[str, Any]]]:
    return {
        "shared": load_shared_prompt_records(workspaces_root),
        "workspace": load_workspace_local_prompt_records(workspace_root),
        "effective": load_workspace_prompt_records(workspace_root, workspaces_root=workspaces_root),
    }
