from __future__ import annotations

import json
import os
import re
import urllib.request
from pathlib import Path
from typing import Any, Callable
from resource_store import get_filesystem_provider
from resource_relationships import (
    depends_on_resource,
    implements_resource,
    inherits_from_resource,
    relationship_ids,
    synchronize_resource_backlinks,
)
from workspace_credentials import resolve_workspace_credential


def _enabled_modalities(value: Any) -> set[str]:
    if isinstance(value, dict):
        return {
            str(name).lower()
            for name, declaration in value.items()
            if declaration is True
            or (isinstance(declaration, dict) and declaration.get("enabled") is True)
        }
    if isinstance(value, (list, tuple, set)):
        return {str(item).lower() for item in value}
    return set()


def _headers(backend: dict[str, Any], workspace_root: Path | None = None) -> dict[str, str]:
    configuration = backend.get("configuration") or {}
    headers = {"Accept": "application/json", "User-Agent": "MeTTaSymbolicLearnerWorkbench/0.6"}
    environment_name = str(configuration.get("apiKeyEnvironmentVariable") or configuration.get("apiKeyEnvironment") or "")
    api_key = resolve_workspace_credential(workspace_root, environment_name) if environment_name else ""
    if api_key:
        if configuration.get("adapter") == "anthropic_messages":
            headers.update({"x-api-key": api_key, "anthropic-version": "2023-06-01"})
        else:
            headers["Authorization"] = f"Bearer {api_key}"
    return headers


def _capabilities(row: dict[str, Any], backend: dict[str, Any], model_id: str) -> dict[str, bool]:
    architecture = row.get("architecture") if isinstance(row.get("architecture"), dict) else {}
    inputs = _enabled_modalities(architecture.get("input_modalities") or row.get("input_modalities") or [])
    outputs = _enabled_modalities(architecture.get("output_modalities") or row.get("output_modalities") or [])
    parameters = {str(value).lower() for value in row.get("supported_parameters") or []}
    declared = row.get("capabilities") if isinstance(row.get("capabilities"), dict) else {}
    supports = declared.get("supports") if isinstance(declared.get("supports"), dict) else {}
    capability_limits = declared.get("limits") if isinstance(declared.get("limits"), dict) else {}
    task_capabilities = row.get("task_capabilities") if isinstance(row.get("task_capabilities"), dict) else {}
    output_modalities = row.get("output_modalities") if isinstance(row.get("output_modalities"), dict) else {}
    image_task = task_capabilities.get("image_output")
    image_modality = output_modalities.get("image")
    name = model_id.lower()
    base_url = str((backend.get("configuration") or {}).get("baseUrl") or "")
    vision = "image" in inputs or "vision" in name or supports.get("vision") is True or bool(capability_limits.get("vision"))
    image_output = (
        "image" in outputs
        or supports.get("image_output") is True
        or image_task is True
        or (isinstance(image_task, dict) and image_task.get("enabled") is True)
        or image_modality is True
        or (isinstance(image_modality, dict) and image_modality.get("enabled") is True)
    )
    audio = "audio" in inputs | outputs or any(token in name for token in ("audio", "realtime", "transcribe", "tts", "whisper"))
    tools = bool(parameters & {"tools", "tool_choice"}) or supports.get("tool_calls") is True
    json_mode = bool(parameters & {"response_format", "structured_outputs"}) or supports.get("structured_outputs") is True
    return {
        "audio": audio,
        "code": any(token in name for token in ("code", "coder", "codex")),
        "functionCalling": tools,
        "json": json_mode,
        "jsonMode": json_mode,
        "imageGeneration": image_output,
        "imageOutput": image_output,
        "local": base_url.startswith(("http://127.0.0.1", "http://localhost")),
        "multimodal": len(inputs | outputs) > 1 or vision or audio,
        "reasoning": bool(parameters & {"reasoning", "include_reasoning"}) or bool(supports.get("reasoning_effort") or supports.get("reasoningEffort")) or any(token in name for token in ("reason", "thinking", "deep-research", "o1", "o3", "o4")),
        "text": not inputs or "text" in inputs or "messages" in parameters,
        "tools": tools,
        "vision": vision,
    }


def _backing_model_properties(
    base_url: str,
    *,
    headers: dict[str, str],
    timeout_seconds: float,
    opener: Callable[..., Any],
) -> dict[str, dict[str, Any]]:
    origin = re.sub(r"/v1/?$", "", base_url.rstrip("/"))
    request = urllib.request.Request(
        f"{origin}/emullm/admin/copilots/models",
        headers=headers,
        method="GET",
    )
    try:
        with opener(request, timeout=timeout_seconds) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (OSError, ValueError, json.JSONDecodeError):
        return {}
    rows = payload.get("models") if isinstance(payload, dict) else None
    if not isinstance(rows, list):
        return {}
    return {
        str(row.get("id")): row
        for row in rows
        if isinstance(row, dict) and str(row.get("id") or "")
    }


def discover_backend_models(backend: dict[str, Any], *, timeout_seconds: float = 20,
                            opener: Callable[..., Any] = urllib.request.urlopen,
                            workspace_root: Path | None = None) -> list[dict[str, Any]]:
    configuration = backend.get("configuration") or {}
    base_url = str(configuration.get("baseUrl") or "").rstrip("/")
    if not base_url:
        raise ValueError("backend has no configuration.baseUrl")
    url = f"{base_url}/models"
    request = urllib.request.Request(url, headers=_headers(backend, workspace_root), method="GET")
    with opener(request, timeout=timeout_seconds) as response:
        payload = json.loads(response.read().decode("utf-8"))
    rows = payload.get("data") if isinstance(payload, dict) else payload
    if not isinstance(rows, list) and isinstance(payload, dict):
        rows = payload.get("models")
    if not isinstance(rows, list):
        raise ValueError("backend /models response has no data or models list")
    backing_properties: dict[str, dict[str, Any]] = {}
    if any(isinstance(row, dict) and row.get("backing_model") for row in rows):
        backing_properties = _backing_model_properties(
            base_url,
            headers=_headers(backend, workspace_root),
            timeout_seconds=timeout_seconds,
            opener=opener,
        )
    discovered: dict[str, dict[str, Any]] = {}
    for row in rows:
        if isinstance(row, str):
            model_id, label, metadata = row, row, {"id": row}
        elif isinstance(row, dict):
            model_id = str(row.get("id") or row.get("name") or row.get("model") or "")
            label = str(row.get("display_name") or row.get("displayName") or row.get("name") or model_id)
            metadata = row
        else:
            continue
        if model_id:
            backing_model = str(metadata.get("backing_model") or "")
            backing_metadata = backing_properties.get(backing_model, {})
            enriched_metadata = {
                **backing_metadata,
                **metadata,
                **({"backingModelMetadata": backing_metadata} if backing_metadata else {}),
            }
            top_provider = enriched_metadata.get("top_provider") if isinstance(enriched_metadata.get("top_provider"), dict) else {}
            backing_capabilities = backing_metadata.get("capabilities") if isinstance(backing_metadata.get("capabilities"), dict) else {}
            backing_limits = backing_capabilities.get("limits") if isinstance(backing_capabilities.get("limits"), dict) else {}
            discovered[model_id] = {
                "id": model_id, "label": label,
                "capabilities": _capabilities(enriched_metadata, backend, model_id),
                "limits": {
                    "contextWindow": enriched_metadata.get("context_length") or backing_limits.get("max_context_window_tokens"),
                    "maxOutputTokens": top_provider.get("max_completion_tokens") or backing_limits.get("max_output_tokens"),
                },
                "pricing": enriched_metadata.get("pricing") if isinstance(enriched_metadata.get("pricing"), dict) else {},
                "properties": {**enriched_metadata, "ownedBy": enriched_metadata.get("owned_by") or enriched_metadata.get("ownedBy")},
                "providerMetadata": enriched_metadata,
            }
    return sorted(discovered.values(), key=lambda row: row["id"].lower())


def discovered_model_document(backend: dict[str, Any], row: dict[str, Any]) -> dict[str, Any] | None:
    remote_id = str(row.get("id") or "").strip()
    if not remote_id:
        return None
    resource_id = re.sub(r"[^a-zA-Z0-9._-]+", "_", f"{backend['id']}-{remote_id}").strip("._").lower()
    return {"kind": "model", "id": resource_id, "label": str(row.get("label") or remote_id),
            "description": f"Discovered from {backend.get('label') or backend['id']}.",
            "implements": implements_resource(str(backend["id"])),
            "inheritsFrom": inherits_from_resource(str(backend["id"])),
            "dependsOn": depends_on_resource(str(backend["id"])),
            "model": remote_id, "enabled": True,
            "capabilities": row.get("capabilities") or {}, "limits": row.get("limits") or {},
            "pricing": row.get("pricing") or {}, "properties": row.get("properties") or {},
            "providerMetadata": row.get("providerMetadata") or {},
            "discovery": {"managed": True, "backendId": backend["id"], "remoteModelId": remote_id}}


def reconcile_discovered_models(root: Path, backend: dict[str, Any], models: list[dict[str, Any]]) -> list[dict[str, Any]]:
    directory = root / "design" / "models"; existing_by_remote: dict[str, dict[str, Any]] = {}
    resources = get_filesystem_provider()
    if resources.is_dir(directory):
        for path in resources.glob(root, ("design/models",), "*.model.json"):
            try: documents = resources.read_json_documents(path)
            except (OSError, json.JSONDecodeError, ValueError): continue
            for document in documents:
                if not isinstance(document, dict): continue
                discovery = document.get("discovery") or {}; legacy = str(document.get("description") or "").startswith("Discovered from ")
                if backend.get("id") in relationship_ids(document.get("implements")) and (discovery.get("managed") is True or legacy):
                    existing_by_remote[str(document.get("model") or "")] = document
    rows: list[dict[str, Any]] = []
    discovered_ids: set[str] = set()
    for row in models:
        document = discovered_model_document(backend, row)
        if not document: continue
        remote_id = str(document["model"]); discovered_ids.add(remote_id); existing = existing_by_remote.get(remote_id)
        status = "new" if existing is None else "unchanged" if existing == document else "changed"
        rows.append({**row, "resourceId": document["id"], "status": status})
    for remote_id, document in existing_by_remote.items():
        if remote_id not in discovered_ids:
            rows.append({"id": remote_id, "resourceId": document.get("id"), "label": document.get("label") or remote_id, "status": "missing"})
    return sorted(rows, key=lambda row: (str(row.get("status")) == "missing", str(row.get("id")).lower()))


def import_discovered_models(root: Path, backend: dict[str, Any], models: list[dict[str, Any]]) -> list[dict[str, Any]]:
    directory = root / "design" / "models"
    resources = get_filesystem_provider()
    resources.make_directory(directory)
    imported: list[dict[str, Any]] = []
    for row in models:
        document = discovered_model_document(backend, row)
        if not document:
            continue
        resource_id = str(document["id"])
        target = directory / f"{resource_id}.model.json"
        previous = resources.read_json(target) if resources.is_file(target) else None
        previous_document = previous if isinstance(previous, dict) else None
        temporary = target.with_suffix(target.suffix + ".tmp")
        resources.write_json(temporary, document)
        resources.replace(temporary, target)
        synchronize_resource_backlinks(
            root,
            document,
            previous_document,
            resources,
        )
        imported.append(document)
    return imported


def remove_missing_models(root: Path, backend: dict[str, Any], resource_ids: list[str]) -> list[str]:
    directory = (root / "design" / "models").resolve(); removed: list[str] = []
    for resource_id in resource_ids:
        safe_id = re.sub(r"[^a-zA-Z0-9._-]+", "_", str(resource_id)).strip("._").lower()
        target = (directory / f"{safe_id}.model.json").resolve()
        resources = get_filesystem_provider()
        if target.parent != directory or not resources.is_file(target): continue
        try: document = resources.read_json(target)
        except (OSError, json.JSONDecodeError): continue
        discovery = document.get("discovery") or {}; legacy = str(document.get("description") or "").startswith("Discovered from ")
        if backend.get("id") not in relationship_ids(document.get("implements")) or not (discovery.get("managed") is True or legacy): continue
        synchronize_resource_backlinks(
            root,
            {**document, "implements": {}, "inheritsFrom": {}, "dependsOn": {}},
            document,
            resources,
        )
        resources.delete(target); removed.append(safe_id)
    return removed
