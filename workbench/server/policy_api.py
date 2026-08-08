from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Body, HTTPException

from policy_library import POLICY_KINDS, effective_model_registry, load_workspace_policy_records
from backend_library import load_workspace_backend_records
from model_policy_ping import run_ping_job
from model_benchmark import run_benchmark
from model_library import resolve_model_records
from model_discovery import discover_backend_models, import_discovered_models
from workspace_api import _resolve_workspace

router = APIRouter(prefix="/workspaces", tags=["model-policy"])
WRITABLE_OBSERVATION_KINDS = {"model_health_observation", "model_ping_job", "model_ping_event", "benchmark_result"}


def _effective_registry(root: Path, records: list[dict[str, Any]]) -> dict[str, Any]:
    backends = [
        record["document"] for record in load_workspace_backend_records(root)
        if isinstance(record.get("document"), dict)
    ]
    return effective_model_registry(records, backends, resolve_model_records(root))

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
    root = Path(workspace["root"])
    return {"workspace": workspace, "resources": records, "registry": _effective_registry(root, records)}


@router.get("/{workspace_id}/models/discover/{backend_id}")
def discover_models(workspace_id: str, backend_id: str) -> dict[str, Any]:
    try: workspace = _resolve_workspace(workspace_id)
    except KeyError as error: raise HTTPException(status_code=404, detail=str(error)) from error
    backend = next((record.get("document") for record in load_workspace_backend_records(Path(workspace["root"]))
                    if (record.get("document") or {}).get("id") == backend_id), None)
    if not backend: raise HTTPException(status_code=404, detail=f"backend not found: {backend_id}")
    try: models = discover_backend_models(backend)
    except Exception as error: raise HTTPException(status_code=502, detail=str(error)) from error
    return {"workspace": workspace, "backend": backend, "models": models}


@router.post("/{workspace_id}/models/import/{backend_id}", status_code=201)
def import_models(workspace_id: str, backend_id: str, request: dict[str, Any] = Body(...)) -> dict[str, Any]:
    try: workspace = _resolve_workspace(workspace_id); shared_workspace = _resolve_workspace("shared")
    except KeyError as error: raise HTTPException(status_code=404, detail=str(error)) from error
    backend = next((record.get("document") for record in load_workspace_backend_records(Path(shared_workspace["root"]))
                    if (record.get("document") or {}).get("id") == backend_id), None)
    if not backend: raise HTTPException(status_code=404, detail=f"shared backend not found: {backend_id}")
    models = request.get("models")
    if not isinstance(models, list): raise HTTPException(status_code=400, detail="models must be a list")
    imported = import_discovered_models(Path(shared_workspace["root"]), backend, models)
    return {"workspace": workspace, "targetWorkspace": shared_workspace, "backendId": backend_id, "models": imported}

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


@router.post("/{workspace_id}/model-policy/ping", status_code=201)
def execute_model_policy_ping(workspace_id: str, request: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    try: workspace = _resolve_workspace(workspace_id)
    except KeyError as error: raise HTTPException(status_code=404, detail=str(error)) from error
    root = Path(workspace["root"]); records = load_workspace_policy_records(root); registry = _effective_registry(root, records)
    scope = str(request.get("scope") or "all").lower()
    if scope not in {"all", "on", "auto", "off", "selected"}: raise HTTPException(status_code=400, detail="scope must be all, on, auto, off, or selected")
    models = registry["models"]
    if scope == "selected":
        targets = {str(value) for value in request.get("targets", [])}
        models = [model for model in models if str(model.get("id")) in targets]
    elif scope != "all": models = [model for model in models if str((model.get("policy") or {}).get("wanted") or "auto").lower() == scope]
    job_id = f"ping_{scope}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}_{uuid4().hex[:8]}"
    job = {"kind": "model_ping_job", "id": job_id, "label": f"Ping {scope}", "scope": scope, "targets": [model.get("id") for model in models], "concurrency": request.get("concurrency", 4), "timeoutMs": request.get("timeoutMs", 15000), "continueOnError": True, "createdAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")}
    rules = (registry.get("policy") or {}).get("rules") or {}; backend_records = load_workspace_backend_records(root); backends = [record["document"] for record in backend_records if record.get("document")]
    result = run_ping_job(root, job, models, backends, slow_latency_ms=float(rules.get("slowLatencyMs", 5000)))
    return {"workspace": workspace, **result}


@router.post("/{workspace_id}/model-policy/benchmarks/{policy_id}/run", status_code=201)
def execute_model_benchmark(workspace_id: str, policy_id: str) -> dict[str, Any]:
    try: workspace = _resolve_workspace(workspace_id)
    except KeyError as error: raise HTTPException(status_code=404, detail=str(error)) from error
    root=Path(workspace["root"]);records=load_workspace_policy_records(root);registry=_effective_registry(root,records);policy=next((item for item in registry["benchmarkPolicies"] if item.get("id")==policy_id),None)
    if not policy: raise HTTPException(status_code=404,detail=f"benchmark policy not found: {policy_id}")
    models=[item for item in registry["models"] if item["effective"]["benchmark"]]; resolved=resolve_model_records(root); profile_ids=set(policy.get("promptProfiles") or []);profiles=[record for record in resolved if (record.get("document") or {}).get("id") in profile_ids and (record.get("resolved") or {}).get("enabled")]
    try: result=run_benchmark(root,policy,models,profiles)
    except ValueError as error: raise HTTPException(status_code=400,detail=str(error)) from error
    return {"workspace":workspace,**result}
