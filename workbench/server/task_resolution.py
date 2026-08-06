from __future__ import annotations

from pathlib import Path
from typing import Any

from task_library import DEFAULT_WORKSPACES_ROOT, SHARED_WORKSPACE_ID, resolve_task_implementation


def materialize_workflow_step(workflow: dict[str, Any], step: dict[str, Any]) -> dict[str, Any]:
    """Resolve a workflow_step/task reference into an executable engine task step.

    Workflows point at abstract task IDs. The task chooses allowed implementation
    variants, and the workflow may optionally request one with
    `implementationVariant`. If omitted, the task's default implementation wins.
    """
    task_id = step.get("task")
    if not task_id:
        return step
    workspace_id = str(workflow.get("workspaceId") or SHARED_WORKSPACE_ID)
    workspace_root = Path(DEFAULT_WORKSPACES_ROOT) / workspace_id
    resolved = resolve_task_implementation(
        workspace_root,
        str(task_id),
        str(step.get("implementationVariant")) if step.get("implementationVariant") else None,
    )
    task = resolved["task"]
    implementation = resolved["implementation"]
    return {
        **step,
        "kind": "task",
        "implementation": implementation["implementation"],
        "parameters": {**(implementation.get("parameters") or {}), **(step.get("parameters") or {})},
        "task": task["id"],
        "implementationVariant": implementation["id"],
        "taskBindings": implementation.get("bindings") or {},
        "modelSelection": implementation.get("modelSelection") or {},
    }


def materialize_workflow(workflow: dict[str, Any]) -> dict[str, Any]:
    return {
        **workflow,
        "steps": [materialize_workflow_step(workflow, step) for step in workflow.get("steps") or []],
    }
