from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Body, HTTPException

from workflow_engine import WorkflowEngine

router = APIRouter(prefix='/engine', tags=['workflow-engine'])
_db = Path(os.getenv('WORKFLOW_ENGINE_DB', Path(__file__).resolve().parents[1] / 'data' / 'workflow_engine.db'))
engine = WorkflowEngine(_db)


def _http(error: Exception) -> HTTPException:
    return HTTPException(status_code=400 if isinstance(error, ValueError) else 404, detail=str(error))


@router.get('/implementations')
def implementations() -> dict[str, Any]:
    return {'implementations': engine.registry.describe()}


@router.get('/workflows')
def workflows() -> dict[str, Any]:
    return {'workflows': engine.list_workflows()}


@router.post('/workflows', status_code=201)
def save_workflow(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    try:
        return {'workflow': engine.save_workflow(body)}
    except (ValueError, KeyError) as error:
        raise _http(error) from error


@router.post('/workflows/validate')
def validate_workflow(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    errors = engine.validate(body)
    return {'valid': not errors, 'errors': errors}


@router.get('/workflows/{workflow_id}')
def get_workflow(workflow_id: str, version: int | None = None) -> dict[str, Any]:
    try:
        return {'workflow': engine.get_workflow(workflow_id, version)}
    except KeyError as error:
        raise _http(error) from error


@router.post('/runs', status_code=201)
def start_run(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    try:
        return {'run': engine.start(str(body['workflowId']), body.get('inputs') or {}, body.get('version'))}
    except (ValueError, KeyError) as error:
        raise _http(error) from error


@router.get('/runs/{run_id}')
def get_run(run_id: str) -> dict[str, Any]:
    try:
        return {'run': engine.get_run(run_id)}
    except KeyError as error:
        raise _http(error) from error


@router.post('/runs/{run_id}/commands')
def command_run(run_id: str, body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    try:
        return {'run': engine.command(run_id, str(body['command']))}
    except (ValueError, KeyError) as error:
        raise _http(error) from error


@router.post('/runs/{run_id}/steps/{step_id}/input')
def submit_input(run_id: str, step_id: str, body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    try:
        return {'run': engine.submit_human_input(run_id, step_id, body)}
    except (ValueError, KeyError) as error:
        raise _http(error) from error
