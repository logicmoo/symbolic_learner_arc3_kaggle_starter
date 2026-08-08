from __future__ import annotations

from pathlib import Path
from time import perf_counter
from typing import Any
from urllib.error import HTTPError

from fastapi import APIRouter, Body, HTTPException

from operation_library import DEFAULT_WORKSPACES_ROOT, resolve_operation_implementation
from operation_resolution import materialize_workflow_step
from workflow_engine_api import engine


router = APIRouter(prefix="/workspaces", tags=["operations"])


def _workspace_root(workspace_id: str) -> Path:
    root = Path(DEFAULT_WORKSPACES_ROOT) / workspace_id
    if not root.is_dir():
        raise KeyError(f"workspace not found: {workspace_id}")
    return root


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
            return {
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
        spec = engine.registry.get(str(executable["implementation"]))

        started = perf_counter()
        result = spec.handler(
            dict(executable.get("inputs") or {}),
            dict(executable.get("parameters") or {}),
        )
        elapsed_ms = round((perf_counter() - started) * 1000, 3)
        if not isinstance(result, dict):
            raise TypeError("operation implementation returned a non-object result")

        return {
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
