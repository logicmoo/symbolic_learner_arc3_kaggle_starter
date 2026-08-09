from __future__ import annotations

import json
import re
import traceback
from datetime import UTC, datetime
from pathlib import Path
from pathlib import PurePosixPath
from time import perf_counter
from typing import Any
from urllib.error import HTTPError
from uuid import uuid4

from fastapi import APIRouter, Body, HTTPException, Query

from operation_library import DEFAULT_WORKSPACES_ROOT, resolve_operation_implementation
from operation_resolution import materialize_workflow_step
from workflow_engine_api import engine
from resource_store import get_filesystem_provider


router = APIRouter(prefix="/workspaces", tags=["operations"])


def _workspace_root(workspace_id: str) -> Path:
    root = Path(DEFAULT_WORKSPACES_ROOT) / workspace_id
    if not get_filesystem_provider().is_dir(root):
        raise KeyError(f"workspace not found: {workspace_id}")
    return root


def _redact_secrets(value: Any, key: str = "") -> Any:
    if key and re.search(r"(?:authorization|api.?key|access.?token|secret|password)$", key, re.IGNORECASE):
        return "[REDACTED]"
    if isinstance(value, dict):
        return {str(name): _redact_secrets(item, str(name)) for name, item in value.items()}
    if isinstance(value, list):
        return [_redact_secrets(item) for item in value]
    return value


def _write_invocation_trace(
    workspace_root: Path,
    operation_id: str,
    trace: dict[str, Any],
) -> str:
    created = datetime.now(UTC)
    safe_operation = re.sub(r"[^A-Za-z0-9_.-]+", "_", operation_id).strip("._") or "operation"
    trace_id = f"{created.strftime('%Y%m%dT%H%M%S.%fZ')}_{safe_operation}_{uuid4().hex[:8]}"
    relative_path = f"runtime/logs/operation_invocations/{trace_id}.log"
    trace.update({
        "kind": "operation_invocation_trace",
        "id": trace_id,
        "createdAt": created.isoformat(),
        "logPath": relative_path,
    })
    resources = get_filesystem_provider()
    resources.write_text(
        resources.resolve(workspace_root, relative_path),
        json.dumps(_redact_secrets(trace), indent=2, ensure_ascii=False, default=str) + "\n",
    )
    return relative_path


@router.get("/{workspace_id}/operations/debug-log")
def read_operation_debug_log(
    workspace_id: str,
    path: str = Query(...),
) -> dict[str, str]:
    workspace_root = _workspace_root(workspace_id)
    logical = PurePosixPath(path)
    if logical.is_absolute() or ".." in logical.parts:
        raise HTTPException(status_code=400, detail="debug log path must stay inside the workspace")
    if logical.parts[:3] != ("runtime", "logs", "operation_invocations") or logical.suffix.lower() != ".log":
        raise HTTPException(status_code=400, detail="only operation invocation debug logs can be read here")
    resources = get_filesystem_provider()
    resolved = resources.resolve(workspace_root, logical.as_posix())
    if not resources.is_file(resolved):
        raise HTTPException(status_code=404, detail=f"debug log not found: {path}")
    return {"path": logical.as_posix(), "content": resources.read_text(resolved)}


@router.post("/{workspace_id}/operations/{operation_id}/invoke")
def invoke_operation(
    workspace_id: str,
    operation_id: str,
    body: dict[str, Any] = Body(default_factory=dict),
) -> dict[str, Any]:
    """Execute one abstract operation through a selected concrete implementation.

    This endpoint is intentionally a playground/integration surface, not a
    workflow replacement.  Inputs are literal artifact payloads supplied by
    the editor.  The workflow runtime continues to reference the abstract operation
    and uses the same resolution/materialization path.
    """
    try:
        workspace_root = _workspace_root(workspace_id)
        requested = body.get("implementationVariant")
        resolved = resolve_operation_implementation(
            workspace_root,
            operation_id,
            str(requested) if requested else None,
        )
        operation = resolved["operation"]
        implementation = resolved["implementation"]

        supplied_inputs = body.get("inputs") or {}
        if not isinstance(supplied_inputs, dict):
            raise ValueError("inputs must be a JSON object")

        missing = [name for name in (operation.get("inputs") or {}) if name not in supplied_inputs]
        if missing:
            raise ValueError(f"missing operation inputs: {', '.join(missing)}")

        step = {
            "id": "operation_playground",
            "operation": operation_id,
            "implementationVariant": implementation["id"],
            "inputs": supplied_inputs,
            "parameters": body.get("parameters") or {},
            "promptVariants": body.get("promptVariants") or {},
        }
        executable = materialize_workflow_step(
            {"id": "operation_playground", "workspaceId": workspace_id},
            step,
        )
        if executable.get("kind") == "human":
            response = {
                "operation": {
                    "id": operation["id"],
                    "label": operation.get("label") or operation["id"],
                    "inputs": operation.get("inputs") or {},
                    "outputs": operation.get("outputs") or {},
                },
                "implementation": {
                    "id": implementation["id"],
                    "label": implementation.get("label") or implementation["id"],
                    "route": implementation["implementation"],
                },
                "inputs": supplied_inputs,
                "outputs": {
                    "status": "waiting_for_input",
                    "form": executable.get("form") or {},
                },
                "elapsedMs": 0,
            }
            response["debugLogPath"] = _write_invocation_trace(workspace_root, operation_id, {
                "workspaceId": workspace_id,
                "status": "waiting_for_input",
                "operation": operation,
                "implementation": implementation,
                "invocationRequest": body,
                "materializedExecutable": executable,
                "outputs": response["outputs"],
                "elapsedMs": 0,
            })
            return response
        spec = engine.registry.get(str(executable["implementation"]))

        started = perf_counter()
        handler_inputs = dict(executable.get("inputs") or {})
        handler_parameters = dict(executable.get("parameters") or {})
        trace: dict[str, Any] = {
            "workspaceId": workspace_id,
            "status": "running",
            "operation": operation,
            "implementation": implementation,
            "invocationRequest": body,
            "materializedExecutable": {
                **executable,
                "parameters": {
                    key: value for key, value in handler_parameters.items() if not str(key).startswith("_debug")
                },
            },
            "handler": {
                "route": spec.name,
                "inputs": handler_inputs,
                "parameters": {
                    key: value for key, value in handler_parameters.items() if not str(key).startswith("_debug")
                },
            },
        }
        try:
            result = spec.handler(handler_inputs, handler_parameters)
            if not isinstance(result, dict):
                raise TypeError("operation implementation returned a non-object result")
        except Exception as error:
            elapsed_ms = round((perf_counter() - started) * 1000, 3)
            trace.update({
                "status": "failed",
                "elapsedMs": elapsed_ms,
                "providerExecution": handler_parameters.get("_debugExecution") or {},
                "error": {
                    "type": type(error).__name__,
                    "message": str(error),
                    "traceback": traceback.format_exc(),
                },
            })
            debug_log_path = _write_invocation_trace(workspace_root, operation_id, trace)
            if isinstance(error, HTTPError):
                provider_response = dict(handler_parameters.get("_debugExecution") or {}).get("response") or {}
                provider_detail = str(provider_response.get("bodyText") or error.reason)
                message = f"provider request failed with HTTP {error.code}: {provider_detail}"
                status_code = error.code
            else:
                message = str(error)
                status_code = 404 if isinstance(error, KeyError) else 400
            raise HTTPException(
                status_code=status_code,
                detail={"message": message, "debugLogPath": debug_log_path},
            ) from error
        elapsed_ms = round((perf_counter() - started) * 1000, 3)
        response = {
            "operation": {
                "id": operation["id"],
                "label": operation.get("label") or operation["id"],
                "inputs": operation.get("inputs") or {},
                "outputs": operation.get("outputs") or {},
            },
            "implementation": {
                "id": implementation["id"],
                "label": implementation.get("label") or implementation["id"],
                "route": implementation["implementation"],
            },
            "resolvedPrompts": executable.get("resolvedPrompts") or [],
            "inputs": supplied_inputs,
            "outputs": result,
            "elapsedMs": elapsed_ms,
        }
        trace.update({
            "status": "completed",
            "elapsedMs": elapsed_ms,
            "providerExecution": handler_parameters.get("_debugExecution") or {},
            "outputs": result,
        })
        response["debugLogPath"] = _write_invocation_trace(workspace_root, operation_id, trace)
        return response
    except HTTPError as error:
        try:
            provider_detail = error.read().decode("utf-8", errors="replace").strip() if error.fp else ""
        except OSError:
            provider_detail = ""
        detail = f"provider request failed with HTTP {error.code}: {provider_detail or error.reason}"
        raise HTTPException(status_code=error.code, detail=detail) from error
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except (ValueError, TypeError, RuntimeError, ImportError, AttributeError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
