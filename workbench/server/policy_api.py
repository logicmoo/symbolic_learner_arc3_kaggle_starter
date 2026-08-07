from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Body, HTTPException

from policy_library import POLICY_KINDS, effective_model_registry, load_workspace_policy_records
from workspace_api import _resolve_workspace

router = APIRouter(prefix="/workspaces", tags=["model-policy"])
WRITABLE_OBSERVATION_KINDS = {"model_health_observation", "model_ping_job", "model_ping_event", "benchmark_result"}

def _safe_id(value: object) -> str:
    result = re.sub(r"[^a-zA-Z0-9._-]+", "_", str(value or "")).strip("._")
    if not result: raise ValueError("resource id is required")
    return result

@router.get("/{workspace_id}/model-policy")
def model_policy_registry(workspace_id: str) -> dict[str, Any]:
    try:
        workspace = _resolve_workspace(workspace_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    records = load_workspace_policy_records(Path(workspace["root"]))
    return {"workspace": workspace, "resources": records, "registry": effective_model_registry(records)}

@router.post("/{workspace_id}/model-policy/observations", status_code=201)
def record_model_policy_observation(workspace_id: str, document: dict[str, Any] = Body(...)) -> dict[str, Any]:
    kind = str(document.get("kind") or "")
    if kind not in WRITABLE_OBSERVATION_KINDS or kind not in POLICY_KINDS:
        raise HTTPException(status_code=400, detail="kind must be a health observation, ping job/event, or benchmark result")
    try:
        workspace = _resolve_workspace(workspace_id)
        resource_id = _safe_id(document.get("id"))
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    directory = Path(workspace["root"]) / "policies"
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / f"{resource_id}.{kind}.json"
    temporary = target.with_suffix(target.suffix + ".tmp")
    temporary.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    temporary.replace(target)
    return {"workspace": workspace, "path": target.relative_to(Path(workspace["root"])).as_posix(), "document": document}
