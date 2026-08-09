from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Body, HTTPException

from policy_library import POLICY_KINDS, effective_model_registry, load_workspace_policy_records
from backend_library import load_workspace_backend_records
from model_policy_ping import run_ping_job, write_policy_resource
from model_benchmark import run_benchmark
from model_library import resolve_model_records
from model_discovery import discover_backend_models, import_discovered_models, reconcile_discovered_models, remove_missing_models
from model_benchmark import call_model
from workspace_api import _resolve_workspace, invalidate_workspace_discovery
from resource_store import get_filesystem_provider

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


def _run_ping_job_safely(root: Path, job: dict[str, Any], models: list[dict[str, Any]], backends: list[dict[str, Any]], slow_latency_ms: float) -> None:
    try:
        run_ping_job(root, job, models, backends, slow_latency_ms=slow_latency_ms)
    except Exception as error:
        write_policy_resource(root, {
            **job,
            "kind": "model_ping_job",
            "status": "failed",
            "completedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "targetCount": len(models),
            "failureCount": len(models),
            "error": str(error),
        })


def _run_benchmark_safely(root: Path, policy: dict[str, Any], models: list[dict[str, Any]], profiles: list[dict[str, Any]], job_id: str) -> None:
    try:
        run_benchmark(root, policy, models, profiles, job_id=job_id)
    except Exception as error:
        completed_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        write_policy_resource(root, {
            "kind": "benchmark_job",
            "id": job_id,
            "benchmarkPolicyId": policy.get("id"),
            "status": "failed",
            "createdAt": completed_at,
            "completedAt": completed_at,
            "modelCount": len(models),
            "profileCount": len(profiles),
            "caseCount": len(policy.get("cases") or []),
            "error": str(error),
        })

@router.get("/{workspace_id}/model-policy")
def model_policy_registry(workspace_id: str) -> dict[str, Any]:
    try:
        workspace = _resolve_workspace(workspace_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    records = load_workspace_policy_records(Path(workspace["root"]))
    root = Path(workspace["root"])
    return {"workspace": workspace, "resources": records, "registry": _effective_registry(root, records)}


@router.post("/{workspace_id}/models/{model_id}/example-invoke")
def invoke_model_example(workspace_id: str, model_id: str, request: dict[str, Any] = Body(...)) -> dict[str, Any]:
    try: workspace = _resolve_workspace(workspace_id)
    except KeyError as error: raise HTTPException(status_code=404, detail=str(error)) from error
    record = next((item for item in resolve_model_records(Path(workspace["root"])) if (item.get("document") or {}).get("id") == model_id), None)
    if not record or not (record.get("resolved") or {}).get("enabled"): raise HTTPException(status_code=404, detail=f"enabled model/profile not found: {model_id}")
    prompt = str((request.get("arguments") or {}).get("prompt") or request.get("prompt") or "")
    if not prompt: raise HTTPException(status_code=400, detail="example argument prompt is required")
    try: result = call_model({"id": model_id, "modelId": (record.get("resolved") or {}).get("model")}, {**record, "_workspaceRoot": workspace["root"]}, prompt, int(request.get("timeoutSeconds") or 120))
    except Exception as error: raise HTTPException(status_code=400, detail=str(error)) from error
    return {"modelId": model_id, **result}


@router.get("/{workspace_id}/models/discover/{backend_id}")
def discover_models(workspace_id: str, backend_id: str) -> dict[str, Any]:
    try: workspace = _resolve_workspace(workspace_id)
    except KeyError as error: raise HTTPException(status_code=404, detail=str(error)) from error
    backend = next((record.get("document") for record in load_workspace_backend_records(Path(workspace["root"]))
                    if (record.get("document") or {}).get("id") == backend_id), None)
    if not backend: raise HTTPException(status_code=404, detail=f"backend not found: {backend_id}")
    try: models = discover_backend_models(backend, workspace_root=Path(workspace["root"]))
    except Exception as error: raise HTTPException(status_code=502, detail=str(error)) from error
    shared_workspace = _resolve_workspace("shared")
    return {"workspace": workspace, "backend": backend, "models": reconcile_discovered_models(Path(shared_workspace["root"]), backend, models)}


@router.post("/{workspace_id}/models/import/{backend_id}", status_code=201)
def import_models(workspace_id: str, backend_id: str, request: dict[str, Any] = Body(...)) -> dict[str, Any]:
    try: workspace = _resolve_workspace(workspace_id); shared_workspace = _resolve_workspace("shared")
    except KeyError as error: raise HTTPException(status_code=404, detail=str(error)) from error
    backend = next((record.get("document") for record in load_workspace_backend_records(Path(shared_workspace["root"]))
                    if (record.get("document") or {}).get("id") == backend_id), None)
    if not backend: raise HTTPException(status_code=404, detail=f"shared backend not found: {backend_id}")
    models = request.get("models")
    if not isinstance(models, list): raise HTTPException(status_code=400, detail="models must be a list")
    if request.get("overwrite", True) is not True: raise HTTPException(status_code=400, detail="model imports require overwrite=true")
    imported = import_discovered_models(Path(shared_workspace["root"]), backend, models)
    invalidate_workspace_discovery()
    return {"workspace": workspace, "targetWorkspace": shared_workspace, "backendId": backend_id, "models": imported}


@router.post("/{workspace_id}/models/remove-missing/{backend_id}")
def remove_missing(workspace_id: str, backend_id: str, request: dict[str, Any] = Body(...)) -> dict[str, Any]:
    try: workspace = _resolve_workspace(workspace_id); shared_workspace = _resolve_workspace("shared")
    except KeyError as error: raise HTTPException(status_code=404, detail=str(error)) from error
    backend = next((record.get("document") for record in load_workspace_backend_records(Path(shared_workspace["root"]))
                    if (record.get("document") or {}).get("id") == backend_id), None)
    if not backend: raise HTTPException(status_code=404, detail=f"shared backend not found: {backend_id}")
    resource_ids = request.get("resourceIds")
    if not isinstance(resource_ids, list): raise HTTPException(status_code=400, detail="resourceIds must be a list")
    removed = remove_missing_models(Path(shared_workspace["root"]), backend, [str(value) for value in resource_ids])
    invalidate_workspace_discovery()
    return {"workspace": workspace, "targetWorkspace": shared_workspace, "backendId": backend_id, "removed": removed}

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
    resources = get_filesystem_provider()
    resources.make_directory(directory)
    target = directory / f"{resource_id}.{kind}.json"
    temporary = target.with_suffix(target.suffix + ".tmp")
    resources.write_json(temporary, document)
    resources.replace(temporary, target)
    return {"workspace": workspace, "path": target.relative_to(Path(workspace["root"])).as_posix(), "document": document}


@router.post("/{workspace_id}/model-policy/ping", status_code=202)
def execute_model_policy_ping(workspace_id: str, background_tasks: BackgroundTasks, request: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
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
    queued = {**job, "status": "queued", "targetCount": len(models)}
    write_policy_resource(root, queued)
    background_tasks.add_task(_run_ping_job_safely, root, job, models, backends, float(rules.get("slowLatencyMs", 5000)))
    return {"workspace": workspace, "job": queued, "results": []}


@router.post("/{workspace_id}/model-policy/benchmarks/{policy_id}/run", status_code=202)
def execute_model_benchmark(workspace_id: str, policy_id: str, background_tasks: BackgroundTasks) -> dict[str, Any]:
    try: workspace = _resolve_workspace(workspace_id)
    except KeyError as error: raise HTTPException(status_code=404, detail=str(error)) from error
    root=Path(workspace["root"]);records=load_workspace_policy_records(root);registry=_effective_registry(root,records);policy=next((item for item in registry["benchmarkPolicies"] if item.get("id")==policy_id),None)
    if not policy: raise HTTPException(status_code=404,detail=f"benchmark policy not found: {policy_id}")
    models=[item for item in registry["models"] if item["effective"]["benchmark"]]; resolved=resolve_model_records(root); profile_ids=set(policy.get("promptProfiles") or []);profiles=[record for record in resolved if (record.get("document") or {}).get("id") in profile_ids and (record.get("resolved") or {}).get("enabled")]
    cases = policy.get("cases")
    if not isinstance(cases, list) or not cases: raise HTTPException(status_code=400,detail="benchmark policy requires at least one declared case")
    job_id=f"benchmark_{policy['id']}_{uuid4().hex[:10]}";queued={"kind":"benchmark_job","id":job_id,"benchmarkPolicyId":policy["id"],"status":"queued","createdAt":datetime.now(timezone.utc).isoformat().replace("+00:00","Z"),"modelCount":len(models),"profileCount":len(profiles),"caseCount":len(cases)}
    write_policy_resource(root,queued)
    background_tasks.add_task(_run_benchmark_safely, root, policy, models, profiles, job_id)
    return {"workspace":workspace,"job":queued,"results":[]}
