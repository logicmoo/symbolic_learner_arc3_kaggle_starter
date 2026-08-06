from __future__ import annotations

from typing import Any

from fastapi import Body, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from routes.artifacts import router as artifacts_router
from routes.workflow import router as workflow_router
from store import DATATYPE_MANIFEST, TASK_CATALOG, WorkbenchStore


app = FastAPI(title="MeTTaSymbolicLearnerWorkbench API", version="0.2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

store = WorkbenchStore()


@app.exception_handler(HTTPException)
async def http_error(_request: Request, error: HTTPException) -> JSONResponse:
    return JSONResponse(status_code=error.status_code, content={"error": str(error.detail)})

# Compatibility routes used by the earlier Tk/web demonstration.
app.include_router(workflow_router, prefix="/api")
app.include_router(artifacts_router, prefix="/api")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "MeTTaSymbolicLearnerWorkbench",
        "persistence": "sqlite",
    }


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
def command_run(
    run_id: str,
    body: dict[str, Any] = Body(default_factory=dict),
) -> dict[str, Any]:
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
    return {"tasks": store.list_tasks(limit)}


@app.get("/api/workflows")
def list_workflows() -> dict[str, Any]:
    return {
        "workflows": store.list_workflows(),
        "tasks": TASK_CATALOG,
        "datatypes": DATATYPE_MANIFEST,
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
            workflows, task = store.save_workflow(
                body["workflow"],
                str(body["originalId"]) if body.get("originalId") else None,
            )
            return {"workflows": workflows, "task": task}
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    raise HTTPException(status_code=400, detail="Invalid workflow operation")
