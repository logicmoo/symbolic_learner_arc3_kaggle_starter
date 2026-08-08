from __future__ import annotations

from pathlib import Path
from typing import Any

from backend_library import load_workspace_backend_records
from model_library import resolve_model_records
from prompt_library import resolve_prompt_implementation
from operation_library import DEFAULT_WORKSPACES_ROOT, SHARED_WORKSPACE_ID, resolve_operation_implementation


def _prompt_prefix(
    workspace_root: Path,
    prompt_ids: list[str],
    separator: str,
    prompt_variants: dict[str, str] | None = None,
) -> tuple[str, list[dict[str, Any]]]:
    """Resolve abstract prompt IDs to concrete prompt implementations.

    Operation implementations bind semantic prompt IDs.  At execution time each
    prompt resolves through its own preferredChild, optionally
    overridden by the caller (for example by the Operation Playground).  This keeps
    operations independent of GPT/Claude/text-only/multimodal prompt variants.
    """
    if not prompt_ids:
        return "", []

    overrides = prompt_variants or {}
    parts: list[str] = []
    resolved_prompts: list[dict[str, Any]] = []
    for prompt_id in prompt_ids:
        resolved = resolve_prompt_implementation(
            workspace_root,
            prompt_id,
            overrides.get(prompt_id),
        )
        implementation = resolved["implementation"]
        text = implementation.get("text", "")
        if isinstance(text, list):
            parts.append("\n".join(str(item) for item in text))
        else:
            parts.append(str(text))
        resolved_prompts.append(
            {
                "promptId": prompt_id,
                "implementationId": str(implementation.get("id") or prompt_id),
                "inline": bool(resolved.get("inline", False)),
                "targets": list(implementation.get("targets") or []),
                "version": implementation.get("version"),
            }
        )
    return separator.join(parts), resolved_prompts


def _implementation_parameters(implementation: dict[str, Any], step: dict[str, Any]) -> dict[str, Any]:
    parameters = dict(implementation.get("parameters") or {})
    route = str(implementation.get("implementation") or "")

    if route == "python.callable" and isinstance(implementation.get("python"), dict):
        parameters.setdefault("source", dict(implementation["python"]))

    if route == "prolog.source" and isinstance(implementation.get("prolog"), dict):
        prolog = dict(implementation["prolog"])
        parameters.setdefault("executable", prolog.get("engine") or "swipl")
        parameters.setdefault("predicate", prolog.get("predicate"))
        source_code = prolog.get("source_code")
        if isinstance(source_code, list):
            source_code = "\n".join(str(line) for line in source_code)
        parameters.setdefault("sourceCode", source_code)

    return {**parameters, **(step.get("parameters") or {})}


def _model_execution_parameters(
    workspace_root: Path,
    model_selection: dict[str, Any],
) -> dict[str, Any]:
    """Resolve an operation's selected model into provider call parameters.

    A selection may name a model resource from the effective model library or
    use a provider-qualified remote model name such as ``openrouter/free``.
    The latter deliberately works without requiring a generated model catalog.
    """
    selected_models = model_selection.get("models") or []
    if not isinstance(selected_models, list) or not selected_models:
        return {}
    selected_id = str(selected_models[0]).strip()
    if not selected_id:
        return {}

    resolved_model: dict[str, Any] | None = None
    for record in resolve_model_records(workspace_root):
        document = record.get("document") or {}
        if str(document.get("id") or "") == selected_id and not record.get("error"):
            resolved_model = record.get("resolved") or {}
            break

    backend: dict[str, Any] | None = None
    configuration: dict[str, Any] = {}
    defaults: dict[str, Any] = {}
    remote_model = selected_id
    if resolved_model:
        backend = resolved_model.get("backend") or {}
        configuration = dict(resolved_model.get("configuration") or {})
        defaults = dict(resolved_model.get("defaults") or {})
        remote_model = str(resolved_model.get("model") or selected_id)
    else:
        provider_hint = selected_id.split("/", 1)[0]
        for record in load_workspace_backend_records(workspace_root):
            candidate = record.get("document") or {}
            if provider_hint in {
                str(candidate.get("id") or ""),
                str(candidate.get("provider") or ""),
            }:
                backend = candidate
                configuration = dict(candidate.get("configuration") or {})
                defaults = dict(candidate.get("modelDefaults") or {})
                break

    if not backend:
        return {"model": remote_model}

    parameters = {
        **defaults,
        "model": remote_model,
        "backendId": str(backend.get("id") or ""),
        "baseUrl": configuration.get("baseUrl"),
        "baseUrlEnvironmentVariable": configuration.get("baseUrlEnvironmentVariable"),
        "legacyBaseUrlEnvironmentVariable": configuration.get("legacyBaseUrlEnvironmentVariable"),
        "apiKeyEnv": configuration.get("apiKeyEnvironmentVariable")
        or configuration.get("apiKeyEnvironment"),
        "timeoutSeconds": configuration.get("timeoutSeconds"),
    }
    return {key: value for key, value in parameters.items() if value is not None}


def materialize_workflow_step(workflow: dict[str, Any], step: dict[str, Any]) -> dict[str, Any]:
    """Resolve a workflow_step/operation reference into an executable engine operation step."""
    operation_id = step.get("operation")
    if not operation_id:
        return step
    workspace_id = str(workflow.get("workspaceId") or SHARED_WORKSPACE_ID)
    workspace_root = Path(DEFAULT_WORKSPACES_ROOT) / workspace_id
    resolved = resolve_operation_implementation(
        workspace_root,
        str(operation_id),
        str(step.get("implementationVariant")) if step.get("implementationVariant") else None,
    )
    operation = resolved["operation"]
    implementation = resolved["implementation"]
    bindings = implementation.get("bindings") or {}
    model_selection = implementation.get("modelSelection") or {}
    parameters = {
        **_model_execution_parameters(workspace_root, model_selection),
        **dict(operation.get("parameters") or {}),
        **_implementation_parameters(implementation, step),
    }
    prompt_ids = [str(item) for item in bindings.get("prompts") or []]
    resolved_prompts: list[dict[str, Any]] = []
    if prompt_ids:
        separator = str(bindings.get("separator") or "\n\n")
        prompt_variants = {
            str(key): str(value)
            for key, value in dict(step.get("promptVariants") or {}).items()
            if value
        }
        prompt_prefix, resolved_prompts = _prompt_prefix(
            workspace_root,
            prompt_ids,
            separator,
            prompt_variants,
        )
        parameters["promptPrefix"] = prompt_prefix
        parameters["promptIds"] = prompt_ids
        parameters["resolvedPrompts"] = resolved_prompts

    executable_inputs = dict(step.get("inputs") or {})
    route = str(implementation.get("implementation") or "")
    capability = str(parameters.get("capability") or bindings.get("capability") or "")
    if route == "system.workbench" and capability == "input.request":
        output_binding = str(parameters.get("outputBinding") or "value")
        datatype = str(parameters.get("datatype") or (operation.get("outputs") or {}).get(output_binding) or "Any")
        return {
            **step,
            "kind": "human",
            "operation": operation["id"],
            "implementation": route,
            "implementationVariant": implementation["id"],
            "parameters": parameters,
            "form": {
                output_binding: {
                    "type": datatype,
                    "label": str(parameters.get("label") or output_binding),
                    "prompt": str(parameters.get("prompt") or "Enter a value"),
                    "required": bool(parameters.get("required", True)),
                }
            },
            "outputs": {output_binding: output_binding},
            "resolvedPrompts": resolved_prompts,
        }
    if implementation.get("implementation") == "llm.complete" and "prompt" not in executable_inputs:
        input_binding = str(parameters.get("inputBinding") or "text")
        if input_binding in executable_inputs:
            executable_inputs = {"prompt": executable_inputs[input_binding]}

    return {
        **step,
        "kind": "operation",
        "implementation": implementation["implementation"],
        "inputs": executable_inputs,
        "parameters": parameters,
        "operation": operation["id"],
        "implementationVariant": implementation["id"],
        "operationBindings": bindings,
        "modelSelection": model_selection,
        "resolvedPrompts": resolved_prompts,
    }


def materialize_workflow(workflow: dict[str, Any]) -> dict[str, Any]:
    return {
        **workflow,
        "steps": [materialize_workflow_step(workflow, step) for step in workflow.get("steps") or []],
    }
