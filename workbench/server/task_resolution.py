from __future__ import annotations

from pathlib import Path
from typing import Any

from prompt_library import load_workspace_prompt_records
from task_library import DEFAULT_WORKSPACES_ROOT, SHARED_WORKSPACE_ID, resolve_task_implementation


def _prompt_prefix(workspace_root: Path, prompt_ids: list[str], separator: str) -> str:
    if not prompt_ids:
        return ""
    prompts = {
        str((record.get("document") or {}).get("id")): record.get("document") or {}
        for record in load_workspace_prompt_records(workspace_root)
    }
    parts: list[str] = []
    for prompt_id in prompt_ids:
        prompt = prompts.get(prompt_id)
        if not prompt:
            raise KeyError(f"prompt not found: {prompt_id}")
        text = prompt.get("text", "")
        if isinstance(text, list):
            parts.append("\n".join(str(item) for item in text))
        else:
            parts.append(str(text))
    return separator.join(parts)


def materialize_workflow_step(workflow: dict[str, Any], step: dict[str, Any]) -> dict[str, Any]:
    """Resolve a workflow_step/task reference into an executable engine task step."""
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
    bindings = implementation.get("bindings") or {}
    parameters = {**(implementation.get("parameters") or {}), **(step.get("parameters") or {})}
    prompt_ids = [str(item) for item in bindings.get("prompts") or []]
    if prompt_ids:
        separator = str(bindings.get("separator") or "\n\n")
        parameters["promptPrefix"] = _prompt_prefix(workspace_root, prompt_ids, separator)
        parameters["promptIds"] = prompt_ids

    executable_inputs = dict(step.get("inputs") or {})
    if implementation.get("implementation") == "llm.complete" and "prompt" not in executable_inputs:
        input_binding = str(parameters.get("inputBinding") or "text")
        if input_binding in executable_inputs:
            executable_inputs = {"prompt": executable_inputs[input_binding]}

    return {
        **step,
        "kind": "task",
        "implementation": implementation["implementation"],
        "inputs": executable_inputs,
        "parameters": parameters,
        "task": task["id"],
        "implementationVariant": implementation["id"],
        "taskBindings": bindings,
        "modelSelection": implementation.get("modelSelection") or {},
    }


def materialize_workflow(workflow: dict[str, Any]) -> dict[str, Any]:
    return {
        **workflow,
        "steps": [materialize_workflow_step(workflow, step) for step in workflow.get("steps") or []],
    }
