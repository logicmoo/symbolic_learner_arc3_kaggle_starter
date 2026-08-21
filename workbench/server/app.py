from __future__ import annotations

from typing import Any

from fastapi import Body, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from arc3_play_api import router as arc3_play_router
from datatype_api import router as datatype_router
from goal_run_api import router as goal_run_router
from mailbox_api import router as mailbox_router
from prompt_api import router as prompt_router
from routes.artifacts import router as artifacts_router
from routes.workflow import router as workflow_router
from runtime import analyze_grid
from store import DATATYPE_MANIFEST, WorkbenchStore
from operation_api import router as operation_router
from operation_library import legacy_catalog_view, load_shared_operation_documents
from model_policy_todo_api import router as model_policy_todo_router
from policy_api import router as policy_router
from repository_docs_api import router as repository_docs_router
from system_control_api import INSTANCE_ID, router as system_control_router
from service_monitor_api import router as service_monitor_router, schedule_startup_reconciliation
from workflow_engine_api import router as workflow_engine_router
from workflow_runner_todo_api import router as workflow_runner_todo_router
from workspace_api import router as workspace_router


app = FastAPI(title="MeTTaSymbolicLearnerWorkbench API", version="0.6.2")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
store = WorkbenchStore()


@app.on_event("startup")
def reconcile_managed_services_after_api_restart() -> None:
    schedule_startup_reconciliation()


@app.exception_handler(HTTPException)
async def http_error(_request: Request, error: HTTPException) -> JSONResponse:
    detail = error.detail if isinstance(error.detail, (dict, list)) else str(error.detail)
    return JSONResponse(status_code=error.status_code, content={"error": detail})


app.include_router(workflow_router, prefix="/api")
app.include_router(artifacts_router, prefix="/api")
app.include_router(workflow_engine_router, prefix="/api")
app.include_router(workflow_runner_todo_router, prefix="/api")
app.include_router(workspace_router, prefix="/api")
app.include_router(arc3_play_router, prefix="/api")
app.include_router(datatype_router, prefix="/api")
app.include_router(goal_run_router, prefix="/api")
app.include_router(mailbox_router, prefix="/api")
app.include_router(prompt_router, prefix="/api")
app.include_router(operation_router, prefix="/api")
app.include_router(model_policy_todo_router, prefix="/api")
app.include_router(policy_router, prefix="/api")
app.include_router(repository_docs_router, prefix="/api")
app.include_router(system_control_router, prefix="/api")
app.include_router(service_monitor_router, prefix="/api")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "MeTTaSymbolicLearnerWorkbench",
        "persistence": "sqlite",
        "workflowEngine": "durable-typed-runtime",
        "workspaces": "filesystem",
        "operationCatalog": "filesystem-invokable",
        "datatypeCatalog": "filesystem",
        "representationCatalog": "filesystem",
        "promptCatalog": "filesystem-hierarchical",
        "instanceId": INSTANCE_ID,
    }


@app.post("/api/analyze")
def analyze(body: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    try:
        return {"analysis": analyze_grid(body.get("grid"))}
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.post("/api/runs", status_code=201)
def create_run(body: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    try:
        return {
            "run": store.create_run(
                workflow_id=str(body.get("workflowId") or "arc3_human_observation"),
                world_id=str(body.get("worldId") or "ls20"),
                parent_task_id=body.get("parentTaskId"),
            )
        }
    except (KeyError, ValueError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.get("/api/runs/{run_id}")
def get_run(run_id: str) -> dict[str, Any]:
    try:
        return {"run": store.get_run(run_id)}
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@app.post("/api/runs/{run_id}/commands")
def command_run(run_id: str, body: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    command = str(body.get("command") or "")
    if not command:
        raise HTTPException(status_code=400, detail="command is required")
    try:
        return {
            "run": store.command_run(
                run_id,
                command,
                body.get("input") if isinstance(body.get("input"), dict) else {},
            )
        }
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.get("/api/runs/{run_id}/events")
def get_events(run_id: str, after: int = Query(default=0, ge=0)) -> dict[str, Any]:
    try:
        events = store.get_events(run_id, after)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return {"events": events, "cursor": events[-1]["id"] if events else after}


@app.get("/api/tasks")
def list_tasks(limit: int = Query(default=20, ge=1, le=200)) -> dict[str, Any]:
    """List thread/job tasks; executable artifacts use the operations API."""
    return {"tasks": store.list_tasks(limit)}


@app.get("/api/workflows")
def list_workflows() -> dict[str, Any]:
    """Compatibility endpoint for the retired mock-workbench client.

    Operation metadata is derived from default/operations on every request. The active
    workspace desktop should use /api/workspaces/{id}/snapshot instead.
    """
    shared_operations = load_shared_operation_documents()
    return {
        "workflows": store.list_workflows(),
        "operations": legacy_catalog_view(shared_operations),
        "datatypes": DATATYPE_MANIFEST,
        "deprecated": True,
        "replacement": "/api/workspaces/{workspace_id}/snapshot",
    }


@app.post("/api/workflows")
def mutate_workflow(body: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    operation = body.get("operation")
    try:
        if operation == "new":
            return {"workflows": store.create_workflow(False)}
        if operation == "example":
            return {"workflows": store.create_workflow(True)}
        if operation == "delete" and body.get("id"):
            return {"workflows": store.delete_workflow(str(body["id"]))}
        if operation == "validate":
            workflow = body.get("workflow")
            return {"validation": store.validate_workflows(workflow if isinstance(workflow, dict) else None)}
        if operation == "save" and isinstance(body.get("workflow"), dict):
            workflows, operation = store.save_workflow(
                body["workflow"],
                str(body["originalId"]) if body.get("originalId") else None,
            )
            return {"workflows": workflows, "operation": operation}
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    raise HTTPException(status_code=400, detail="Invalid workflow operation")
