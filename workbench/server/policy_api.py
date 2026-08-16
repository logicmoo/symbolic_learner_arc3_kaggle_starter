from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Body, HTTPException, Query

from policy_library import POLICY_KINDS, effective_model_registry, load_workspace_policy_records
from backend_library import backend_matches, load_workspace_backend_records
from model_policy_ping import run_ping_job, write_policy_resource
from model_benchmark import run_benchmark
from model_library import resolve_model_records
from prompt_library import load_workspace_prompt_profile_records, resolve_prompt_profile
from model_discovery import discover_backend_models, import_discovered_models, reconcile_discovered_models, remove_missing_models
from operation_resolution import _model_execution_parameters
from workflow_providers import _llm_complete
from workspace_api import _resolve_workspace, invalidate_workspace_discovery
from resource_store import get_filesystem_provider
from invocation_trace import list_invocation_traces, read_invocation_trace, write_invocation_trace

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


def _run_benchmark_safely(root: Path, policy: dict[str, Any], models: list[dict[str, Any]], presets: list[dict[str, Any]], job_id: str) -> None:
    try:
        run_benchmark(root, policy, models, presets, job_id=job_id)
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
            "presetCount": len(presets),
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
    registry = _effective_registry(root, records)
    registry["promptProfiles"] = [
        record["document"] for record in load_workspace_prompt_profile_records(root)
        if isinstance(record.get("document"), dict)
    ]
    return {"workspace": workspace, "resources": records, "registry": registry}


@router.post("/{workspace_id}/models/{model_id}/invoke")
@router.post("/{workspace_id}/models/{model_id}/example-invoke")
def invoke_model_example(workspace_id: str, model_id: str, request: dict[str, Any] = Body(...)) -> dict[str, Any]:
    try: workspace = _resolve_workspace(workspace_id)
    except KeyError as error: raise HTTPException(status_code=404, detail=str(error)) from error
    record = next((item for item in resolve_model_records(Path(workspace["root"])) if (item.get("document") or {}).get("id") == model_id), None)
    if not record or not (record.get("resolved") or {}).get("enabled"): raise HTTPException(status_code=404, detail=f"enabled model/profile not found: {model_id}")
    prompt = str((request.get("arguments") or {}).get("prompt") or request.get("prompt") or "")
    if not prompt: raise HTTPException(status_code=400, detail="example argument prompt is required")
    image = str(request.get("image") or "").strip()
    if image and not image.startswith(("data:image/", "https://", "http://")): raise HTTPException(status_code=400, detail="image must be an image data URL or HTTP(S) URL")
    image_summary = None if not image else {"source": "data_url" if image.startswith("data:") else "url", "mediaType": image[5:].split(";", 1)[0] if image.startswith("data:") else None, "length": len(image)}
    trace = {"workspaceId": workspace_id, "modelId": model_id, "status": "running", "prompt": prompt, "image": image_summary, "timeoutSeconds": int(request.get("timeoutSeconds") or 120), "resource": record.get("document"), "resolved": record.get("resolved")}
    parameters = _model_execution_parameters(Path(workspace["root"]), {"models": [model_id], "strategy": "single"})
    parameters["timeoutSeconds"] = trace["timeoutSeconds"]
    debug_execution: dict[str, Any] = {}
    parameters["_debugExecution"] = debug_execution
    inputs = {"prompt": prompt, **({"image": image} if image else {})}
    started = datetime.now(timezone.utc)
    try:
        provider_result = _llm_complete(inputs, parameters)
        response_payload = provider_result.get("response") if isinstance(provider_result, dict) else None
        usage = response_payload.get("usage") if isinstance(response_payload, dict) and isinstance(response_payload.get("usage"), dict) else {}
        result = {
            "text": str(provider_result.get("text") or ""),
            "latencyMs": round((datetime.now(timezone.utc) - started).total_seconds() * 1000, 2),
            "inputTokens": usage.get("prompt_tokens", usage.get("input_tokens", 0)),
            "outputTokens": usage.get("completion_tokens", usage.get("output_tokens", 0)),
            "responseId": response_payload.get("id") if isinstance(response_payload, dict) else None,
            "backendId": parameters.get("backendId"),
            "response": response_payload,
            "debugExecution": parameters.get("_debugExecution"),
        }
    except Exception as error:
        debug_log_path = write_invocation_trace(Path(workspace["root"]), "model", model_id, "model_invocation_trace", {**trace, "status": "failed", "error": str(error)})
        raise HTTPException(status_code=400, detail={"message": str(error), "debugLogPath": debug_log_path}) from error
    response = {"modelId": model_id, **result}
    response["debugLogPath"] = write_invocation_trace(Path(workspace["root"]), "model", model_id, "model_invocation_trace", {**trace, "status": "completed", "response": result})
    return response


@router.get("/{workspace_id}/models/debug-log")
def read_model_debug_log(workspace_id: str, path: str = Query(...)) -> dict[str, str]:
    try: workspace = _resolve_workspace(workspace_id)
    except KeyError as error: raise HTTPException(status_code=404, detail=str(error)) from error
    try: return {"path": path, "content": read_invocation_trace(Path(workspace["root"]), "model", path)}
    except ValueError as error: raise HTTPException(status_code=400, detail=str(error)) from error
    except FileNotFoundError as error: raise HTTPException(status_code=404, detail=f"debug log not found: {path}") from error


@router.get("/{workspace_id}/models/invocations")
def list_model_invocations(workspace_id: str, limit: int = Query(200, ge=1, le=1000)) -> dict[str, Any]:
    try: workspace = _resolve_workspace(workspace_id)
    except KeyError as error: raise HTTPException(status_code=404, detail=str(error)) from error
    return {"workspaceId": workspace_id, "family": "model", "invocations": list_invocation_traces(Path(workspace["root"]), "model", limit)}


@router.get("/{workspace_id}/models/discover/{backend_id}")
def discover_models(workspace_id: str, backend_id: str) -> dict[str, Any]:
    try: workspace = _resolve_workspace(workspace_id)
    except KeyError as error: raise HTTPException(status_code=404, detail=str(error)) from error
    backend = next((record.get("document") for record in load_workspace_backend_records(Path(workspace["root"]))
                    if backend_matches(record.get("document") or {}, backend_id)), None)
    if not backend: raise HTTPException(status_code=404, detail=f"backend not found: {backend_id}")
    try: models = discover_backend_models(backend, workspace_root=Path(workspace["root"]))
    except Exception as error: raise HTTPException(status_code=502, detail=str(error)) from error
    shared_workspace = _resolve_workspace("shared_library_system")
    return {"workspace": workspace, "backend": backend, "models": reconcile_discovered_models(Path(shared_workspace["root"]), backend, models)}


@router.post("/{workspace_id}/models/import/{backend_id}", status_code=201)
def import_models(workspace_id: str, backend_id: str, request: dict[str, Any] = Body(...)) -> dict[str, Any]:
    try: workspace = _resolve_workspace(workspace_id); shared_workspace = _resolve_workspace("shared_library_system")
    except KeyError as error: raise HTTPException(status_code=404, detail=str(error)) from error
    backend = next((record.get("document") for record in load_workspace_backend_records(Path(shared_workspace["root"]))
                    if backend_matches(record.get("document") or {}, backend_id)), None)
    if not backend: raise HTTPException(status_code=404, detail=f"shared backend not found: {backend_id}")
    models = request.get("models")
    if not isinstance(models, list): raise HTTPException(status_code=400, detail="models must be a list")
    if request.get("overwrite", True) is not True: raise HTTPException(status_code=400, detail="model imports require overwrite=true")
    imported = import_discovered_models(Path(shared_workspace["root"]), backend, models)
    invalidate_workspace_discovery()
    return {"workspace": workspace, "targetWorkspace": shared_workspace, "backendId": backend_id, "models": imported}


@router.post("/{workspace_id}/models/remove-missing/{backend_id}")
def remove_missing(workspace_id: str, backend_id: str, request: dict[str, Any] = Body(...)) -> dict[str, Any]:
    try: workspace = _resolve_workspace(workspace_id); shared_workspace = _resolve_workspace("shared_library_system")
    except KeyError as error: raise HTTPException(status_code=404, detail=str(error)) from error
    backend = next((record.get("document") for record in load_workspace_backend_records(Path(shared_workspace["root"]))
                    if backend_matches(record.get("document") or {}, backend_id)), None)
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
    models=[item for item in registry["models"] if item["effective"]["benchmark"]]; resolved=resolve_model_records(root); preset_ids=set(map(str, policy.get("modelPresets") or []));presets=[record for record in resolved if (record.get("document") or {}).get("id") in preset_ids and (record.get("resolved") or {}).get("enabled")]
    cases = policy.get("cases")
    if not isinstance(cases, list) or not cases: raise HTTPException(status_code=400,detail="benchmark policy requires at least one declared case")
    if not models: raise HTTPException(status_code=409,detail="benchmark policy has no effectively benchmark-enabled models; ping eligible models and review vendor/model benchmark policy")
    resolved_preset_ids={(record.get("document") or {}).get("id") for record in presets}
    missing_presets=sorted(preset_ids-resolved_preset_ids)
    if not preset_ids: raise HTTPException(status_code=400,detail="benchmark policy requires at least one modelPresets entry")
    if missing_presets: raise HTTPException(status_code=400,detail=f"benchmark policy references unavailable or disabled model presets: {', '.join(missing_presets)}")
    prompt_profile_ids=list(map(str, policy.get("promptProfiles") or []))
    missing_prompt_profiles=[]
    for prompt_profile_id in prompt_profile_ids:
        try: resolve_prompt_profile(root, prompt_profile_id)
        except (KeyError, ValueError): missing_prompt_profiles.append(prompt_profile_id)
    if missing_prompt_profiles: raise HTTPException(status_code=400,detail=f"benchmark policy references unavailable or disabled Prompt Profiles: {', '.join(missing_prompt_profiles)}")
    job_id=f"benchmark_{policy['id']}_{uuid4().hex[:10]}";queued={"kind":"benchmark_job","id":job_id,"benchmarkPolicyId":policy["id"],"status":"queued","createdAt":datetime.now(timezone.utc).isoformat().replace("+00:00","Z"),"modelCount":len(models),"presetCount":len(presets),"promptProfileCount":len(policy.get("promptProfiles") or []),"caseCount":len(cases)}
    write_policy_resource(root,queued)
    background_tasks.add_task(_run_benchmark_safely, root, policy, models, presets, job_id)
    return {"workspace":workspace,"job":queued,"results":[]}
