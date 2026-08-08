from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SHARED_WORKSPACE_ID = "shared"


def workspace_metadata_path(root: Path) -> Path:
    named = root / f"{root.name}.workspace.json"
    return named if named.is_file() else root / "workspace.json"


def read_workspace_metadata(root: Path) -> dict[str, Any]:
    path = workspace_metadata_path(root)
    if not path.is_file():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def declared_include_specs(root: Path) -> list[dict[str, Any]]:
    raw = read_workspace_metadata(root).get("includes") or []
    if not isinstance(raw, list):
        return []
    result: list[dict[str, Any]] = []
    for value in raw:
        if isinstance(value, dict):
            workspace_id = str(value.get("workspaceId") or value.get("id") or "").strip()
            include_inherited = value.get("includeInherited", True) is not False
        else:
            workspace_id = str(value).strip()
            include_inherited = True
        if workspace_id and workspace_id != SHARED_WORKSPACE_ID and not any(item["workspaceId"] == workspace_id for item in result):
            result.append({"workspaceId": workspace_id, "includeInherited": include_inherited})
    return result


def declared_includes(root: Path) -> list[str]:
    return [item["workspaceId"] for item in declared_include_specs(root)]


def effective_workspace_layers(workspace_root: Path, workspaces_root: Path) -> list[Path]:
    """Return lowest-to-highest precedence roots, with Shared always first."""
    workspace_root = workspace_root.resolve()
    workspaces_root = workspaces_root.resolve()
    if workspace_root.name == SHARED_WORKSPACE_ID:
        return [workspace_root]
    result: list[Path] = []
    visiting: list[str] = []

    def visit(root: Path, include_inherited: bool = True) -> None:
        workspace_id = root.name
        if workspace_id in visiting:
            raise ValueError(f"Workspace inclusion cycle: {' -> '.join((*visiting, workspace_id))}")
        if any(existing.name == workspace_id for existing in result):
            return
        if not root.is_dir():
            raise ValueError(f"Included workspace does not exist: {workspace_id}")
        visiting.append(workspace_id)
        if include_inherited:
            for spec in declared_include_specs(root):
                included_id = spec["workspaceId"]
                if included_id == workspace_root.name:
                    raise ValueError(f"Workspace inclusion cycle: {workspace_root.name} -> {workspace_id} -> {included_id}")
                visit(workspaces_root / included_id, spec["includeInherited"])
        visiting.pop()
        result.append(root)

    shared_root = workspaces_root / SHARED_WORKSPACE_ID
    if shared_root.is_dir():
        visit(shared_root)
    for spec in declared_include_specs(workspace_root):
        visit(workspaces_root / spec["workspaceId"], spec["includeInherited"])
    visit(workspace_root)
    return result


def layer_source(layer: Path, workspace_root: Path) -> str:
    if layer.name == SHARED_WORKSPACE_ID:
        return "shared"
    if layer.resolve() == workspace_root.resolve():
        return "workspace"
    return "included"
