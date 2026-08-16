from __future__ import annotations

from pathlib import Path
from typing import Any

from resource_store import get_filesystem_provider


ROOT = Path(__file__).resolve().parents[2]
WORKSPACES_ROOT = ROOT / "workbench" / "workspaces"
SYSTEM_POLICY_PATH = (
    WORKSPACES_ROOT
    / "shared_library_system"
    / "policies"
    / "workbench_model_selection.model_runtime_policy.json"
)
WORKSPACE_POLICY_FILENAME = "workspace_model_selection.model_runtime_policy.json"


def _read_document(path: Path) -> dict[str, Any]:
    resources = get_filesystem_provider()
    if not resources.is_file(path):
        return {}
    try:
        document = resources.read_json(path)
    except (OSError, ValueError):
        return {}
    return document if isinstance(document, dict) else {}


def system_model_selection() -> dict[str, Any]:
    document = _read_document(SYSTEM_POLICY_PATH)
    pervasive = document.get("pervasive", document.get("alwaysUseModel")) is True
    return {
        **document,
        "kind": "model_runtime_policy",
        "id": "workbench_model_selection",
        "label": str(document.get("label") or "Workbench Model Selection"),
        "fallbackModelId": str(document.get("fallbackModelId") or ""),
        "pervasive": pervasive,
    }


def workspace_policy_path(workspace_root: Path) -> Path:
    return workspace_root / "policies" / WORKSPACE_POLICY_FILENAME


def workspace_model_selection(workspace_root: Path) -> dict[str, Any]:
    document = _read_document(workspace_policy_path(workspace_root))
    return {
        **document,
        "kind": "workspace_model_runtime_policy",
        "id": "workspace_model_selection",
        "label": str(document.get("label") or "Workspace Model Selection"),
        "overrideModelId": str(document.get("overrideModelId") or ""),
    }


def write_system_model_selection(document: dict[str, Any]) -> dict[str, Any]:
    pervasive = document.get("pervasive", document.get("alwaysUseModel")) is True
    normalized = {
        **document,
        "kind": "model_runtime_policy",
        "id": "workbench_model_selection",
        "label": str(document.get("label") or "Workbench Model Selection"),
        "fallbackModelId": str(document.get("fallbackModelId") or ""),
        "pervasive": pervasive,
    }
    normalized.pop("alwaysUseModel", None)
    resources = get_filesystem_provider()
    resources.make_directory(SYSTEM_POLICY_PATH.parent)
    resources.write_json(SYSTEM_POLICY_PATH, normalized)
    return normalized


def write_workspace_model_selection(
    workspace_root: Path,
    document: dict[str, Any],
) -> dict[str, Any]:
    normalized = {
        **document,
        "kind": "workspace_model_runtime_policy",
        "id": "workspace_model_selection",
        "label": str(document.get("label") or "Workspace Model Selection"),
        "overrideModelId": str(document.get("overrideModelId") or ""),
    }
    path = workspace_policy_path(workspace_root)
    resources = get_filesystem_provider()
    resources.make_directory(path.parent)
    resources.write_json(path, normalized)
    return normalized


def effective_model_selection(
    workspace_root: Path,
    requested_selection: dict[str, Any] | None,
) -> tuple[dict[str, Any], str]:
    """Apply workspace and system model precedence to an operation selection."""
    requested = requested_selection if isinstance(requested_selection, dict) else {}
    workspace_policy = workspace_model_selection(workspace_root)
    workspace_override = str(workspace_policy.get("overrideModelId") or "").strip()
    if workspace_override:
        return {"models": [workspace_override], "strategy": "workspace_override"}, "workspace_override"

    system_policy = system_model_selection()
    fallback = str(system_policy.get("fallbackModelId") or "").strip()
    if fallback and system_policy.get("pervasive") is True:
        return {"models": [fallback], "strategy": "system_forced"}, "system_forced"

    selected_models = requested.get("models") or []
    if isinstance(selected_models, list) and any(str(item).strip() for item in selected_models):
        return requested, "operation"

    if fallback:
        return {"models": [fallback], "strategy": "system_fallback"}, "system_fallback"
    return requested, "unresolved"
