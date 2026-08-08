from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from resource_store import get_filesystem_provider

Probe = Callable[[dict[str, Any], dict[str, Any] | None, int], dict[str, Any]]

def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def _safe_id(value: object) -> str:
    result = re.sub(r"[^a-zA-Z0-9._-]+", "_", str(value or "")).strip("._")
    if not result: raise ValueError("resource id is required")
    return result

def write_policy_resource(root: Path, document: dict[str, Any]) -> Path:
    resources = get_filesystem_provider()
    directory = root / "policies"; resources.make_directory(directory)
    target = directory / f"{_safe_id(document.get('id'))}.{document['kind']}.json"
    temporary = target.with_suffix(target.suffix + ".tmp")
    resources.write_json(temporary, document); resources.replace(temporary, target)
    return target

def probe_model(model: dict[str, Any], backend: dict[str, Any] | None, timeout_ms: int) -> dict[str, Any]:
    started = time.perf_counter(); configuration = (backend or {}).get("configuration") or {}; base_url = str(configuration.get("baseUrl") or "").rstrip("/")
    if not base_url: return {"status": "unknown", "latencyMs": 0, "error": "vendor backend has no HTTP endpoint"}
    key_name = str(configuration.get("apiKeyEnvironmentVariable") or configuration.get("apiKeyEnvironment") or ""); api_key = os.environ.get(key_name, "") if key_name else ""
    if key_name and not api_key and not base_url.startswith(("http://127.0.0.1", "http://localhost")): return {"status": "authentication_error", "latencyMs": 0, "error": f"environment variable {key_name} is not set"}
    headers = {"Accept": "application/json", "User-Agent": "MeTTaSymbolicLearnerWorkbench/0.6"}
    if api_key:
        if str(configuration.get("adapter")) == "anthropic_messages": headers.update({"x-api-key": api_key, "anthropic-version": "2023-06-01"})
        else: headers["Authorization"] = f"Bearer {api_key}"
    request = urllib.request.Request(f"{base_url}/models", headers=headers, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=max(0.1, timeout_ms / 1000)) as response: response.read(2048)
        return {"status": "online", "latencyMs": round((time.perf_counter() - started) * 1000, 1)}
    except urllib.error.HTTPError as error:
        status = "authentication_error" if error.code in {401, 403} else "rate_limited" if error.code == 429 else "error"
        return {"status": status, "latencyMs": round((time.perf_counter() - started) * 1000, 1), "error": f"HTTP {error.code}"}
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        return {"status": "offline", "latencyMs": round((time.perf_counter() - started) * 1000, 1), "error": str(error)}

def run_ping_job(workspace_root: Path, job: dict[str, Any], models: list[dict[str, Any]], backends: list[dict[str, Any]], *, slow_latency_ms: float = 5000, probe: Probe = probe_model, deduplicate_vendor_probes: bool | None = None) -> dict[str, Any]:
    job = {**job, "kind": "model_ping_job", "status": "running", "startedAt": _now()}; write_policy_resource(workspace_root, job)
    backend_by_id = {str(item.get("id")): item for item in backends if item.get("id")}; timeout_ms = max(100, int(job.get("timeoutMs") or 15000)); concurrency = max(1, min(32, int(job.get("concurrency") or 4))); results: list[dict[str, Any]] = []
    def execute(model: dict[str, Any]) -> dict[str, Any]:
        observed = probe(model, backend_by_id.get(str(model.get("vendorId") or "")), timeout_ms); latency = observed.get("latencyMs")
        if observed.get("status") == "online" and isinstance(latency, (int, float)) and latency > slow_latency_ms: observed["status"] = "slow"
        return observed
    if deduplicate_vendor_probes is None: deduplicate_vendor_probes = probe is probe_model
    groups: list[list[dict[str, Any]]]
    if deduplicate_vendor_probes:
        grouped: dict[str, list[dict[str, Any]]] = {}
        for model in models: grouped.setdefault(str(model.get("vendorId") or model.get("id")), []).append(model)
        groups = list(grouped.values())
    else: groups = [[model] for model in models]
    with ThreadPoolExecutor(max_workers=concurrency, thread_name_prefix="model-policy-ping") as executor:
        futures = {executor.submit(execute, group[0]): group for group in groups}
        for future in as_completed(futures):
            group = futures[future]
            try: observed = future.result()
            except Exception as error: observed = {"status": "error", "latencyMs": 0, "error": str(error)}
            for model in group:
                stamp = _now(); suffix = _safe_id(model.get("id"))
                health = {"kind": "model_health_observation", "id": f"{job['id']}:health:{suffix}", "modelPolicyEntryId": model.get("id"), "vendorId": model.get("vendorId"), "status": observed.get("status", "error"), "latencyMs": observed.get("latencyMs", 0), "observedAt": stamp, "jobId": job["id"]}
                if observed.get("error"): health["error"] = str(observed["error"])
                event = {"kind": "model_ping_event", "id": f"{job['id']}:event:{suffix}", "jobId": job["id"], "modelPolicyEntryId": model.get("id"), "status": "succeeded" if health["status"] in {"online", "slow"} else "failed", "healthStatus": health["status"], "latencyMs": health["latencyMs"], "createdAt": stamp}
                if health.get("error"): event["error"] = health["error"]
                write_policy_resource(workspace_root, health); write_policy_resource(workspace_root, event); results.append({"event": event, "health": health})
    failures = sum(item["event"]["status"] == "failed" for item in results)
    completed = {**job, "status": "completed_with_errors" if failures else "completed", "completedAt": _now(), "targetCount": len(models), "failureCount": failures}; write_policy_resource(workspace_root, completed)
    return {"job": completed, "results": results}
