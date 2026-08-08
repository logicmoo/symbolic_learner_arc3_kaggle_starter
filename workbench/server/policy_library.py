from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from operation_library import DEFAULT_WORKSPACES_ROOT, SHARED_WORKSPACE_ID
from resource_relationships import relationship_ids
from workspace_inheritance import effective_workspace_layers, layer_source
from resource_store import get_filesystem_provider

POLICY_KINDS = {"model_policy", "model_policy_variant", "vendor_policy", "model_policy_entry", "model_health_observation", "model_ping_job", "model_ping_event", "benchmark_policy", "benchmark_job", "benchmark_result"}
POLICY_STATES = {"on", "auto", "off"}
UNHEALTHY_STATUSES = {"offline", "error", "ratelimited", "rate_limited", "unknown"}

def _records(root: Path, source: str, workspace_id: str) -> list[dict[str, Any]]:
    directory = root / "policies"
    resources = get_filesystem_provider()
    if not resources.is_dir(directory): return []
    result: list[dict[str, Any]] = []
    for path in resources.glob(root, ("policies",)):
        try:
            documents = resources.read_json_documents(path)
        except (OSError, json.JSONDecodeError, ValueError) as error:
            result.append({"path": path.relative_to(root).as_posix(), "source": source, "workspaceId": workspace_id, "error": str(error)})
            continue
        for resource_index, document in enumerate(documents):
            if not isinstance(document, dict) or document.get("kind") not in POLICY_KINDS:
                continue
            record: dict[str, Any] = {"path": path.relative_to(root).as_posix(), "source": source, "workspaceId": workspace_id, "resourceIndex": resource_index}
            if not document.get("id"): record["error"] = "Policy resource requires an id and supported kind"
            else: record["document"] = document
            result.append(record)
    return result

def load_workspace_policy_records(workspace_root: Path, *, workspaces_root: Path = DEFAULT_WORKSPACES_ROOT) -> list[dict[str, Any]]:
    combined: dict[str, dict[str, Any]] = {}
    for layer in effective_workspace_layers(workspace_root, workspaces_root):
        for record in _records(layer, layer_source(layer, workspace_root), layer.name):
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

def _capability_map(document: dict[str, Any], documents_by_id: dict[str, dict[str, Any]]) -> dict[str, bool]:
    current = document
    visited: set[str] = set()
    while current and str(current.get("id") or "") not in visited:
        visited.add(str(current.get("id") or ""))
        values = current.get("capabilities")
        if isinstance(values, list):
            return {str(value): True for value in values}
        if isinstance(values, dict):
            return {str(key): bool(value) for key, value in values.items()}
        current = documents_by_id.get(str(current.get("inherits") or ""), {})
    return {}


def effective_model_registry(
    records: list[dict[str, Any]],
    backend_catalog: list[dict[str, Any]] | None = None,
    model_catalog: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Resolve persisted intent and latest health without mutating either source."""
    policies = _documents(records, "model_policy")
    active_policy = next((item for item in policies if item.get("enabled", True)), policies[0] if policies else {})
    rules = active_policy.get("rules") if isinstance(active_policy.get("rules"), dict) else {}
    persisted_vendors = {str(item.get("vendorId")): item for item in _documents(records, "vendor_policy") if item.get("vendorId")}
    vendors: dict[str, dict[str, Any]] = {}
    for backend in backend_catalog or []:
        vendor_id = str(backend.get("id") or backend.get("provider") or "")
        if not vendor_id:
            continue
        generated = {
            "kind": "vendor_policy", "id": f"{vendor_id}_policy", "vendorId": vendor_id,
            "label": backend.get("label") or vendor_id, "description": backend.get("description") or "",
            "enabled": backend.get("enabled", True), "catalogResourceId": backend.get("id"),
            "policy": {"wanted": "on", "runtime": "auto", "benchmark": "auto"},
            "properties": {"catalogKind": "backend", "provider": backend.get("provider")},
        }
        override = persisted_vendors.get(vendor_id) or {}
        vendors[vendor_id] = {**generated, **override, "policy": {**generated["policy"], **(override.get("policy") or {})}}
    for vendor_id, document in persisted_vendors.items():
        vendors.setdefault(vendor_id, document)
    health = _latest_health(records)
    persisted_models = _documents(records, "model_policy_entry")
    persisted_by_resource = {str(item.get("modelResourceId")): item for item in persisted_models if item.get("modelResourceId")}
    persisted_by_id = {str(item.get("id")): item for item in persisted_models if item.get("id")}
    catalog_documents = {
        str((record.get("document") or {}).get("id")): record.get("document") or {}
        for record in model_catalog or [] if (record.get("document") or {}).get("id")
    }
    model_documents: list[dict[str, Any]] = []
    catalog_policy_ids: set[str] = set()
    for record in model_catalog or []:
        document = record.get("document") or {}; resolved = record.get("resolved") or {}
        resource_id = str(document.get("id") or ""); vendor_id = str(resolved.get("backendId") or "")
        if not resource_id or not vendor_id:
            continue
        override = persisted_by_resource.get(resource_id)
        generated_id = f"{vendor_id}:{resource_id}"
        if not override:
            override = persisted_by_id.get(generated_id)
        policy_id = str((override or {}).get("id") or generated_id)
        generated = {
            "kind": "model_policy_entry", "id": policy_id, "vendorId": vendor_id,
            "modelId": resolved.get("model") or document.get("model") or resource_id,
            "modelResourceId": resource_id, "name": document.get("label") or resource_id,
            "description": document.get("description") or "", "enabled": resolved.get("enabled", document.get("enabled", True)),
            "policy": {"wanted": "on", "runtime": "auto", "benchmark": "auto"},
            "capabilities": _capability_map(document, catalog_documents),
            "limits": {**(document.get("limits") or {}), **{key: value for key, value in (resolved.get("defaults") or {}).items() if key in {"maxOutputTokens", "timeoutSeconds"}}},
            "pricing": document.get("pricing") or {},
            "properties": {**(document.get("properties") or {}), "catalogKind": document.get("kind"), "inheritance": resolved.get("inheritance") or []},
            "providerMetadata": document.get("providerMetadata") or {},
        }
        merged = {**generated, **(override or {}), "policy": {**generated["policy"], **((override or {}).get("policy") or {})},
                  "_policyOverrideFields": list(((override or {}).get("policy") or {}).keys())}
        model_documents.append(merged); catalog_policy_ids.add(policy_id)
    model_documents.extend({**item, "_policyOverrideFields": list((item.get("policy") or {}).keys())}
                           for item in persisted_models if str(item.get("id")) not in catalog_policy_ids)
    models: list[dict[str, Any]] = []
    for model in model_documents:
        vendor = vendors.get(str(model.get("vendorId")))
        override_fields = set(model.pop("_policyOverrideFields", ()))
        observation = health.get(str(model.get("id"))) or {}
        status = str(observation.get("status") or "unknown").lower()
        latency = observation.get("latencyMs")
        failure_rate = observation.get("failureRate")
        reasons: list[str] = []
        def requested(name: str) -> bool:
            model_state = _state(model, name)
            if name in override_fields and model_state != "auto":
                return model_state == "on"
            return model_state != "off" and _state(vendor, name) != "off"
        wanted = model.get("enabled", True) and (vendor is None or vendor.get("enabled", True)) and requested("wanted")
        if not wanted: reasons.append("disabled by wanted policy")
        unhealthy = status in UNHEALTHY_STATUSES
        if rules.get("excludeSlowFromRuntime", True) and (status == "slow" or isinstance(latency, (int, float)) and latency > rules.get("slowLatencyMs", 5000)):
            unhealthy = True; reasons.append("latency threshold exceeded")
        if isinstance(failure_rate, (int, float)) and failure_rate > rules.get("maxFailureRate", 0.2):
            unhealthy = True; reasons.append("failure rate threshold exceeded")
        if status in UNHEALTHY_STATUSES: reasons.append(f"health is {status}")
        runtime_requested = wanted and requested("runtime")
        benchmark_requested = wanted and requested("benchmark")
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
