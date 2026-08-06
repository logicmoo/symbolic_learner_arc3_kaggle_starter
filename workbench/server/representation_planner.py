from __future__ import annotations

import heapq
from pathlib import Path
from typing import Any

from task_library import DEFAULT_WORKSPACES_ROOT, load_workspace_task_records


def conversion_edges(workspace_root: Path, *, workspaces_root: Path = DEFAULT_WORKSPACES_ROOT) -> list[dict[str, Any]]:
    edges: list[dict[str, Any]] = []
    for record in load_workspace_task_records(workspace_root, workspaces_root=workspaces_root):
        document = record.get("document") or {}
        conversion = document.get("conversion")
        if not isinstance(conversion, dict):
            continue
        datatype = str(conversion.get("datatype") or "")
        source = str(conversion.get("from") or "")
        target = str(conversion.get("to") or "")
        if not datatype or not source or not target:
            continue
        planning = document.get("planning") if isinstance(document.get("planning"), dict) else {}
        cost = float((planning or {}).get("cost", 1.0))
        edges.append({
            "taskId": str(document.get("id")),
            "label": str(document.get("label") or document.get("id")),
            "datatype": datatype,
            "from": source,
            "to": target,
            "cost": cost,
            "lossy": bool((planning or {}).get("lossy", False)),
            "expectedAccuracy": (planning or {}).get("expectedAccuracy"),
            "source": record.get("source"),
            "path": record.get("path"),
        })
    return sorted(edges, key=lambda edge: (edge["datatype"], edge["from"], edge["to"], edge["taskId"]))


def plan_representation_conversion(
    workspace_root: Path,
    datatype: str,
    source_representation: str,
    target_representation: str,
    *,
    workspaces_root: Path = DEFAULT_WORKSPACES_ROOT,
) -> dict[str, Any]:
    if source_representation == target_representation:
        return {
            "datatype": datatype,
            "from": source_representation,
            "to": target_representation,
            "cost": 0.0,
            "steps": [],
        }

    edges = [edge for edge in conversion_edges(workspace_root, workspaces_root=workspaces_root) if edge["datatype"] == datatype]
    adjacency: dict[str, list[dict[str, Any]]] = {}
    for edge in edges:
        adjacency.setdefault(edge["from"], []).append(edge)

    queue: list[tuple[float, str, tuple[dict[str, Any], ...]]] = [(0.0, source_representation, ())]
    best: dict[str, float] = {source_representation: 0.0}
    while queue:
        cost, current, path = heapq.heappop(queue)
        if current == target_representation:
            return {
                "datatype": datatype,
                "from": source_representation,
                "to": target_representation,
                "cost": cost,
                "steps": list(path),
            }
        if cost > best.get(current, float("inf")):
            continue
        for edge in adjacency.get(current, []):
            next_cost = cost + float(edge["cost"])
            target = str(edge["to"])
            if next_cost >= best.get(target, float("inf")):
                continue
            best[target] = next_cost
            heapq.heappush(queue, (next_cost, target, path + (edge,)))

    raise KeyError(f"no representation conversion path for {datatype}: {source_representation} -> {target_representation}")
