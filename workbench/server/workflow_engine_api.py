from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Body, HTTPException, Query

from advanced_workflow_engine import AdvancedWorkflowEngine
from workflow_providers import probe_capabilities, register_real_providers

router = APIRouter(prefix='/engine', tags=['workflow-engine'])
_db = Path(os.getenv('WORKFLOW_ENGINE_DB', Path(__file__).resolve().parents[1] / 'data' / 'workflow_engine.db'))
engine = AdvancedWorkflowEngine(_db)
register_real_providers(engine.registry)


def _http(error: Exception) -> HTTPException:
    return HTTPException(status_code=400 if isinstance(error, (ValueError, TypeError)) else 404, detail=str(error))


@router.get('/capabilities')
def capabilities() -> dict[str, Any]:
    return {'capabilities': probe_capabilities(engine.registry)}


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
        engine.refresh_children(run_id)
        return {'run': engine.get_run(run_id)}
    except KeyError as error:
        raise _http(error) from error


@router.get('/runs/{run_id}/events')
def get_events(run_id: str, after: int = Query(default=0, ge=0)) -> dict[str, Any]:
    try:
        run = engine.get_run(run_id)
        events = [event for event in run['events'] if event['id'] > after]
        return {'events': events, 'cursor': events[-1]['id'] if events else after}
    except KeyError as error:
        raise _http(error) from error


@router.get('/runs/{run_id}/logs')
def get_logs(run_id: str, step_id: str | None = None) -> dict[str, Any]:
    try:
        logs = engine.get_run(run_id)['logs']
        if step_id:
            logs = [entry for entry in logs if entry['stepId'] == step_id]
        return {'logs': logs}
    except KeyError as error:
        raise _http(error) from error


@router.post('/runs/{run_id}/commands')
def command_run(run_id: str, body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    command = str(body.get('command') or '')
    try:
        if command == 'replay':
            return {'run': engine.replay(run_id)}
        if command == 'advance':
            engine.advance(run_id)
            return {'run': engine.get_run(run_id)}
        return {'run': engine.command(run_id, command)}
    except (ValueError, KeyError) as error:
        raise _http(error) from error


@router.post('/runs/{run_id}/steps/{step_id}/input')
def submit_input(run_id: str, step_id: str, body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    try:
        return {'run': engine.submit_human_input(run_id, step_id, body)}
    except (ValueError, KeyError) as error:
        raise _http(error) from error
