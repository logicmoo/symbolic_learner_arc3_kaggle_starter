from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
WORKSPACES_ROOT = Path(os.getenv("WORKBENCH_WORKSPACES_ROOT", REPOSITORY_ROOT / "workbench" / "workspaces")).resolve()
SHARED_WORKSPACE = WORKSPACES_ROOT / "shared"


def _read_json(path: Path, default: Any) -> Any:
    if not path.is_file():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def load_datatype_manifest() -> list[dict[str, Any]]:
    data = _read_json(SHARED_WORKSPACE / "config" / "datatypes.json", {})
    value = data.get("datatypes", []) if isinstance(data, dict) else []
    return value if isinstance(value, list) else []


def load_artifact_specs() -> dict[str, tuple[str, str, str, float]]:
    data = _read_json(SHARED_WORKSPACE / "config" / "artifact_specs.json", {})
    raw = data.get("artifacts", {}) if isinstance(data, dict) else {}
    result: dict[str, tuple[str, str, str, float]] = {}
    if not isinstance(raw, dict):
        return result
    for name, spec in raw.items():
        if not isinstance(spec, dict):
            continue
        result[str(name)] = (
            str(spec.get("type") or "Artifact"),
            str(spec.get("producer") or "unknown"),
            str(spec.get("display") or name),
            float(spec.get("confidence", 1.0)),
        )
    return result


def load_shared_operations() -> list[dict[str, Any]]:
    operations: list[dict[str, Any]] = []
    directory = SHARED_WORKSPACE / "operations"
    if not directory.is_dir():
        return operations
    for path in sorted(directory.glob("*.json")):
        value = _read_json(path, None)
        if isinstance(value, dict):
            operations.append(value)
    return operations


def load_workspace_workflows() -> list[dict[str, Any]]:
    workflows: dict[str, dict[str, Any]] = {}
    if not WORKSPACES_ROOT.is_dir():
        return []
    for workspace in sorted(WORKSPACES_ROOT.iterdir(), key=lambda item: item.name.lower()):
        directory = workspace / "workflows"
        if not directory.is_dir():
            continue
        for path in sorted(directory.glob("*.json")):
            value = _read_json(path, None)
            if isinstance(value, dict) and value.get("id"):
                workflows[str(value["id"])] = value
    return list(workflows.values())


def operation_catalog_for_legacy_api() -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for operation in load_shared_operations():
        inputs = operation.get("inputs") or {}
        outputs = operation.get("outputs") or {}
        result.append({
            "id": operation.get("id"),
            "label": operation.get("label"),
            "ports": f"{', '.join(inputs)} → {', '.join(outputs)}",
            "routes": operation.get("implementation"),
            "source": "workbench/workspaces/shared/design/operations",
        })
    return result


def apply_to_legacy_store(store_module: Any) -> None:
    store_module.OPERATION_CATALOG = operation_catalog_for_legacy_api()
    store_module.DATATYPE_MANIFEST = load_datatype_manifest()
    artifact_specs = load_artifact_specs()
    if artifact_specs:
        store_module.ARTIFACT_SPECS = artifact_specs
    workflows = load_workspace_workflows()
    if workflows:
        store_module.STARTER_WORKFLOWS = workflows
        typed = next((item for item in workflows if item.get("id") == "example_typed_artifact_review"), None)
        if typed is not None:
            store_module.TYPED_EXAMPLE = typed
