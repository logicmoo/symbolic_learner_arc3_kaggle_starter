from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter, Body, HTTPException, Query

from goal_plan_library import load_workspace_symbolic_records
from workflow_engine_api import engine
from workspace_api import _load_workflows, _resolve_workspace


router = APIRouter(prefix="/goal-runs", tags=["goal-runs"])


def _documents(root: Path, family: str) -> dict[str, dict[str, Any]]:
    return {
        str(record["document"]["id"]): record["document"]
        for record in load_workspace_symbolic_records(root, family)
        if isinstance(record.get("document"), dict) and record["document"].get("id")
    }


def _select_variant(
    documents: dict[str, dict[str, Any]], parent_id: str, requested_id: str | None
) -> dict[str, Any]:
    parent = documents.get(parent_id)
    if not parent:
        raise ValueError(f"resource not found: {parent_id}")
    variant_id = requested_id or parent.get("preferredChild")
    if not variant_id:
        children = parent.get("children") or []
        variant_id = children[0] if children else None
    variant = documents.get(str(variant_id or ""))
    if not variant or parent_id not in (variant.get("parents") or []):
        raise ValueError(f"valid variant required for {parent_id}")
    return variant


def _workflow_document(workspace: dict[str, Any], workflow_id: str) -> dict[str, Any]:
    for record in _load_workflows(workspace):
        document = record.get("document")
        if isinstance(document, dict) and document.get("id") == workflow_id:
            return document
    raise ValueError(f"workflow not found in workspace: {workflow_id}")


@router.get("")
def list_goal_runs(
    workspace_id: str | None = None, limit: int = Query(default=100, ge=1, le=500)
) -> dict[str, Any]:
    return {"goalRuns": engine.list_goal_runs(workspace_id, limit)}


@router.get("/{goal_run_id}")
def get_goal_run(goal_run_id: str) -> dict[str, Any]:
    try:
        return {"goalRun": engine.get_goal_run(goal_run_id)}
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.post("", status_code=201)
def start_goal_run(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    try:
        workspace_id = str(body.get("workspaceId") or "")
        goal_id = str(body.get("goalId") or "")
        plan_id = str(body.get("planId") or "")
        if not workspace_id or not goal_id or not plan_id:
            raise ValueError("workspaceId, goalId, and planId are required")
        workspace = _resolve_workspace(workspace_id)
        root = Path(workspace["root"])
        goals = _documents(root, "goal")
        plans = _documents(root, "plan")
        contexts = _documents(root, "context")
        goal_variant = _select_variant(goals, goal_id, body.get("goalVariantId"))
        plan = plans.get(plan_id)
        if not plan or goal_id not in (plan.get("goals") or []):
            raise ValueError(f"planning strategy {plan_id} does not pursue goal {goal_id}")
        plan_variant = _select_variant(plans, plan_id, body.get("planVariantId"))
        context_id = str(body.get("contextId") or "") or None
        context_variant = None
        if context_id:
            context = contexts.get(context_id)
            if not context or context.get("kind") not in {"atomspace", "context"}:
                raise ValueError(f"context not found: {context_id}")
            context_variant = _select_variant(contexts, context_id, body.get("contextVariantId"))
        workflow_id = str(plan_variant.get("workflow") or "")
        if not workflow_id:
            raise ValueError(f"planning strategy variant has no workflow/plan: {plan_variant['id']}")
        try:
            workflow = engine.get_workflow(workflow_id)
        except KeyError:
            workflow = engine.save_workflow(_workflow_document(workspace, workflow_id))
        workflow_run = engine.start(
            workflow_id, body.get("inputs") or {}, workflow.get("version"), workspace_id=workspace_id,
        )
        goal_run = engine.create_goal_run(
            workspace_id,
            goal_id,
            str(goal_variant["id"]),
            plan_id,
            str(plan_variant["id"]),
            context_id,
            str(context_variant["id"]) if context_variant else None,
            str(workflow_run["id"]),
        )
        return {"goalRun": goal_run}
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except (TypeError, ValueError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
