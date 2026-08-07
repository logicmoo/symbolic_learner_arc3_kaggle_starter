from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from operation_library import DEFAULT_WORKSPACES_ROOT, SHARED_WORKSPACE_ID
from resource_relationships import relationship_ids

POLICY_KINDS = {"model_policy", "model_policy_variant", "vendor_policy", "model_policy_entry", "model_health_observation", "model_ping_job", "model_ping_event", "benchmark_policy", "benchmark_result"}
POLICY_STATES = {"on", "auto", "off"}
UNHEALTHY_STATUSES = {"offline", "error", "ratelimited", "rate_limited", "unknown"}

def _records(root: Path, source: str, workspace_id: str) -> list[dict[str, Any]]:
    directory = root / "policies"
    if not directory.is_dir(): return []
    result: list[dict[str, Any]] = []
    for path in sorted(directory.glob("*.json"), key=lambda value: value.name.lower()):
        record: dict[str, Any] = {"path": path.relative_to(root).as_posix(), "source": source, "workspaceId": workspace_id}
        try:
            document = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(document, dict) or document.get("kind") not in POLICY_KINDS or not document.get("id"): raise ValueError("Policy resource requires an id and supported kind")
            record["document"] = document
        except (OSError, json.JSONDecodeError, ValueError) as error: record["error"] = str(error)
        result.append(record)
    return result

def load_workspace_policy_records(workspace_root: Path, *, workspaces_root: Path = DEFAULT_WORKSPACES_ROOT) -> list[dict[str, Any]]:
    combined: dict[str, dict[str, Any]] = {}
    for record in _records(workspaces_root / SHARED_WORKSPACE_ID, "shared", SHARED_WORKSPACE_ID):
        document = record.get("document") or {}; combined[str(document.get("id") or record["path"])] = record
    if workspace_root.name != SHARED_WORKSPACE_ID:
        for record in _records(workspace_root, "workspace", workspace_root.name):
            document = record.get("document") or {}; combined[str(document.get("id") or record["path"])] = record
    return sorted(combined.values(), key=lambda record: str((record.get("document") or {}).get("label") or record["path"]).lower())

def policy_hierarchy(records: list[dict[str, Any]]) -> dict[str, Any]:
    roots: list[dict[str, Any]] = []; variants: list[dict[str, Any]] = []; children: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        document = record.get("document") or {}; parents = relationship_ids(document.get("parents"))
        if document.get("kind") == "model_policy_variant" and parents:
            variants.append(record)
            for parent in parents: children.setdefault(parent, []).append(record)
        else: roots.append(record)
    return {"roots": roots, "variants": variants, "variantsByParent": children}

def _documents(records: list[dict[str, Any]], kind: str) -> list[dict[str, Any]]:
    return [record["document"] for record in records if (record.get("document") or {}).get("kind") == kind]

def _state(document: dict[str, Any] | None, name: str, default: str = "auto") -> str:
    value = str(((document or {}).get("policy") or {}).get(name, default)).lower()
    return value if value in POLICY_STATES else default

def _latest_health(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for observation in _documents(records, "model_health_observation"):
        target = str(observation.get("modelPolicyEntryId") or observation.get("vendorId") or "")
        if target and str(observation.get("observedAt") or "") >= str(result.get(target, {}).get("observedAt") or ""):
            result[target] = observation
    return result

def effective_model_registry(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Resolve persisted intent and latest health without mutating either source."""
    policies = _documents(records, "model_policy")
    active_policy = next((item for item in policies if item.get("enabled", True)), policies[0] if policies else {})
    rules = active_policy.get("rules") if isinstance(active_policy.get("rules"), dict) else {}
    vendors = {str(item.get("vendorId")): item for item in _documents(records, "vendor_policy") if item.get("vendorId")}
    health = _latest_health(records)
    models: list[dict[str, Any]] = []
    for model in _documents(records, "model_policy_entry"):
        vendor = vendors.get(str(model.get("vendorId")))
        observation = health.get(str(model.get("id"))) or {}
        status = str(observation.get("status") or "unknown").lower()
        latency = observation.get("latencyMs")
        failure_rate = observation.get("failureRate")
        reasons: list[str] = []
        wanted = model.get("enabled", True) and (vendor is None or vendor.get("enabled", True)) and _state(model, "wanted") != "off" and _state(vendor, "wanted") != "off"
        if not wanted: reasons.append("disabled by wanted policy")
        unhealthy = status in UNHEALTHY_STATUSES
        if rules.get("excludeSlowFromRuntime", True) and (status == "slow" or isinstance(latency, (int, float)) and latency > rules.get("slowLatencyMs", 5000)):
            unhealthy = True; reasons.append("latency threshold exceeded")
        if isinstance(failure_rate, (int, float)) and failure_rate > rules.get("maxFailureRate", 0.2):
            unhealthy = True; reasons.append("failure rate threshold exceeded")
        if status in UNHEALTHY_STATUSES: reasons.append(f"health is {status}")
        runtime_requested = wanted and _state(model, "runtime") != "off" and _state(vendor, "runtime") != "off"
        benchmark_requested = wanted and _state(model, "benchmark") != "off" and _state(vendor, "benchmark") != "off"
        runtime = runtime_requested and (not rules.get("requireHealthyModel", True) or not unhealthy)
        benchmark = benchmark_requested and (not rules.get("requireHealthyModel", True) or not unhealthy)
        effective_state = lambda requested, enabled: "enabled" if enabled else "temporarily_disabled" if requested else "disabled"
        models.append({**model, "health": observation or {"status": "unknown"}, "effective": {
            "runtime": runtime, "benchmark": benchmark,
            "runtimeState": effective_state(runtime_requested, runtime),
            "benchmarkState": effective_state(benchmark_requested, benchmark),
            "reasons": list(dict.fromkeys(reasons)),
        }})
    return {"policy": active_policy or None, "vendors": list(vendors.values()), "models": models,
            "benchmarkPolicies": _documents(records, "benchmark_policy"), "pingJobs": _documents(records, "model_ping_job"),
            "pingEvents": _documents(records, "model_ping_event"), "healthObservations": _documents(records, "model_health_observation")}
