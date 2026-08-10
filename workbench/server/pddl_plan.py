from __future__ import annotations

import re
from typing import Any


_PLAN_LINE = re.compile(
    r"^\s*(?:(?P<start>\d+(?:\.\d+)?)\s*:\s*)?\((?P<body>[^()]*)\)\s*(?:\[(?P<duration>\d+(?:\.\d+)?)\])?\s*$"
)


def _identifier(value: str) -> str:
    identifier = re.sub(r"[^a-zA-Z0-9_]+", "_", value.strip()).strip("_").lower()
    if not identifier:
        raise ValueError("PDDL action name is empty")
    return identifier


def grounded_plan_to_workflow(request: dict[str, Any]) -> dict[str, Any]:
    """Convert conventional grounded PDDL planner output without saving it.

    Action names map to abstract Operation IDs. Positional PDDL arguments remain
    explicit metadata because only the domain-specific Operation knows its port
    names. Callers may supply ``actionMap`` to translate PDDL action names.
    """

    source = str(request.get("sourcePlan") or "")
    action_map = request.get("actionMap") or {}
    if not isinstance(action_map, dict):
        raise ValueError("actionMap must be an object")
    action_bindings = request.get("actionBindings") or {}
    if not isinstance(action_bindings, dict):
        raise ValueError("actionBindings must be an object")
    parsed: list[dict[str, Any]] = []
    for line_number, original in enumerate(source.splitlines(), start=1):
        line = original.split(";", 1)[0].strip()
        if not line:
            continue
        match = _PLAN_LINE.match(line)
        if not match:
            raise ValueError(f"invalid grounded plan line {line_number}: {original.strip()}")
        tokens = match.group("body").split()
        if not tokens:
            raise ValueError(f"grounded plan line {line_number} has no action")
        action = _identifier(tokens[0])
        operation = str(action_map.get(action) or action)
        parameters: dict[str, Any] = {"pddlAction": tokens[0], "pddlArguments": tokens[1:]}
        if match.group("start") is not None:
            parameters["pddlStartTime"] = float(match.group("start"))
        if match.group("duration") is not None:
            parameters["pddlDuration"] = float(match.group("duration"))
        bindings = action_bindings.get(action) or {}
        if not isinstance(bindings, dict):
            raise ValueError(f"actionBindings.{action} must be an object")
        inputs: dict[str, Any] = {}
        for port, argument_index in bindings.items():
            if not isinstance(argument_index, int) or isinstance(argument_index, bool):
                raise ValueError(f"actionBindings.{action}.{port} must be a zero-based integer argument index")
            if argument_index < 0 or argument_index >= len(tokens) - 1:
                raise ValueError(f"actionBindings.{action}.{port} refers to missing argument {argument_index + 1}")
            inputs[str(port)] = tokens[argument_index + 1]
        parsed.append({"action": action, "operation": operation, "parameters": parameters, "inputs": inputs})
    if not parsed:
        raise ValueError("sourcePlan must contain at least one grounded PDDL action")
    steps = []
    temporal = all("pddlStartTime" in item["parameters"] for item in parsed)
    previous_start: float | None = None
    previous_group: list[str] = []
    current_group: list[str] = []
    for index, item in enumerate(parsed):
        step_id = f"{item['action']}_{index + 1}"
        if temporal:
            start = float(item["parameters"]["pddlStartTime"])
            if previous_start is not None and start < previous_start:
                raise ValueError("temporal grounded plan actions must be ordered by start time")
            if previous_start is None or start != previous_start:
                previous_group = current_group
                current_group = []
                previous_start = start
            dependencies = list(previous_group)
        else:
            dependencies = [steps[-1]["id"]] if steps else []
        step = {
            "id": step_id,
            "label": " ".join([item["parameters"]["pddlAction"], *item["parameters"]["pddlArguments"]]),
            "kind": "workflow_step",
            "operation": item["operation"],
            "parameters": item["parameters"],
            "dependsOn": dependencies,
        }
        if item["inputs"]:
            step["inputs"] = item["inputs"]
        steps.append(step)
        current_group.append(step_id)
    workflow_id = _identifier(str(request.get("id") or "pddl_plan"))
    return {
        "kind": "workflow",
        "id": workflow_id,
        "label": str(request.get("label") or workflow_id.replace("_", " ").title()),
        "description": str(request.get("description") or "Executable Workflow imported from grounded PDDL planner output."),
        "inputs": request.get("inputs") if isinstance(request.get("inputs"), dict) else {},
        "outputs": request.get("outputs") if isinstance(request.get("outputs"), dict) else {},
        "steps": steps,
        "planProvenance": {
            "origin": "pddl",
            "planner": str(request.get("planner") or ""),
            "domain": str(request.get("domain") or ""),
            "problem": str(request.get("problem") or ""),
            "sourcePlan": source,
        },
    }
