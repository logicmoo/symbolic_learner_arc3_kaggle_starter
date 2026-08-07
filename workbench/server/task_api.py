from __future__ import annotations

from pathlib import Path
from time import perf_counter
from typing import Any

from fastapi import APIRouter, Body, HTTPException

from task_library import DEFAULT_WORKSPACES_ROOT, resolve_task_implementation
from task_resolution import materialize_workflow_step
from workflow_engine_api import engine


router = APIRouter(prefix="/workspaces", tags=["tasks"])


def _workspace_root(workspace_id: str) -> Path:
    root = Path(DEFAULT_WORKSPACES_ROOT) / workspace_id
    if not root.is_dir():
        raise KeyError(f"workspace not found: {workspace_id}")
    return root


@router.post("/{workspace_id}/tasks/{task_id}/invoke")
def invoke_task(
    workspace_id: str,
    task_id: str,
    body: dict[str, Any] = Body(default_factory=dict),
) -> dict[str, Any]:
    """Execute one abstract task through a selected concrete implementation.

    This endpoint is intentionally a playground/integration surface, not a
    workflow replacement.  Inputs are literal artifact payloads supplied by
    the editor.  The workflow runtime continues to reference the abstract task
    and uses the same resolution/materialization path.
    """
    try:
        workspace_root = _workspace_root(workspace_id)
        requested = body.get("implementationVariant")
        resolved = resolve_task_implementation(
            workspace_root,
            task_id,
            str(requested) if requested else None,
        )
        task = resolved["task"]
        implementation = resolved["implementation"]

        supplied_inputs = body.get("inputs") or {}
        if not isinstance(supplied_inputs, dict):
            raise ValueError("inputs must be a JSON object")

        missing = [name for name in (task.get("inputs") or {}) if name not in supplied_inputs]
        if missing:
            raise ValueError(f"missing task inputs: {', '.join(missing)}")

        step = {
            "id": "task_playground",
            "task": task_id,
            "implementationVariant": implementation["id"],
            "inputs": supplied_inputs,
            "parameters": body.get("parameters") or {},
            "promptVariants": body.get("promptVariants") or {},
        }
        executable = materialize_workflow_step(
            {"id": "task_playground", "workspaceId": workspace_id},
            step,
        )
        spec = engine.registry.get(str(executable["implementation"]))

        started = perf_counter()
        result = spec.handler(
            dict(executable.get("inputs") or {}),
            dict(executable.get("parameters") or {}),
        )
        elapsed_ms = round((perf_counter() - started) * 1000, 3)
        if not isinstance(result, dict):
            raise TypeError("task implementation returned a non-object result")

        return {
            "task": {
                "id": task["id"],
                "label": task.get("label") or task["id"],
                "inputs": task.get("inputs") or {},
                "outputs": task.get("outputs") or {},
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
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except (ValueError, TypeError, RuntimeError, ImportError, AttributeError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
