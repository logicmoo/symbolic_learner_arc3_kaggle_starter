from __future__ import annotations

import asyncio
import os
import re
from typing import Any

import httpx
import websockets
from fastapi import Body, FastAPI, HTTPException, Query, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

from arc3_play_api import router as arc3_play_router
from registry_api import router as registry_router
from video_import_api import router as video_import_router
from datatype_api import router as datatype_router
from goal_run_api import router as goal_run_router
from jobs_api import router as jobs_router
from mailbox_api_lib import router as mailbox_router
from prompt_api import router as prompt_router
from routes.artifacts import router as artifacts_router
from routes.workflow import router as workflow_router
from runtime import analyze_grid
from store import DATATYPE_MANIFEST, WorkbenchStore
from operation_api import router as operation_router
from operation_library import legacy_catalog_view, load_shared_operation_documents
from model_policy_todo_api import router as model_policy_todo_router
from policy_api import router as policy_router
from plugin_api import install_plugins, router as plugin_router
from repository_docs_api import router as repository_docs_router
from system_control_api import INSTANCE_ID, router as system_control_router
from service_monitor_api import router as service_monitor_router, schedule_startup_reconciliation
from terminal_api import router as terminal_router
from workflow_engine_api import router as workflow_engine_router
from workflow_runner_todo_api import router as workflow_runner_todo_router
from workspace_api import router as workspace_router


app = FastAPI(title="MeTTaSymbolicLearnerWorkbench API", version="0.6.2")
DEFAULT_WEB_URL = "http://127.0.0.1:5173/"
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


@app.on_event("startup")
def autostart_sanity_tests() -> None:
    """Run the Sanity Tests on the SERVER automatically at startup, and refresh
    them periodically, so the page always observes a live run without anyone
    pressing Run all. The heavy import + runs happen on a background thread so
    server startup is never blocked."""
    import threading
    import time

    def _boot() -> None:
        try:
            import recognition_demos as rd  # heavy: numpy/scipy/PIL/swipl
        except Exception:  # noqa: BLE001
            return
        while True:
            try:
                rd.start_demo_run()  # background; no-op if a run is already going
            except Exception:  # noqa: BLE001
                pass
            time.sleep(900)  # keep results fresh (e.g. after a reduce)

    threading.Thread(target=_boot, name="sanity-tests-autostart", daemon=True).start()


@app.exception_handler(HTTPException)
async def http_error(_request: Request, error: HTTPException) -> JSONResponse:
    detail = error.detail if isinstance(error.detail, (dict, list)) else str(error.detail)
    return JSONResponse(status_code=error.status_code, content={"error": detail})


app.include_router(workflow_router, prefix="/workbench")
app.include_router(artifacts_router, prefix="/workbench")
app.include_router(workflow_engine_router, prefix="/workbench")
app.include_router(workflow_runner_todo_router, prefix="/workbench")
app.include_router(workspace_router, prefix="/workbench")
app.include_router(arc3_play_router, prefix="/workbench")
app.include_router(registry_router, prefix="/workbench")
app.include_router(video_import_router, prefix="/workbench")
app.include_router(datatype_router, prefix="/workbench")
app.include_router(goal_run_router, prefix="/workbench")
app.include_router(jobs_router, prefix="/workbench")
app.include_router(mailbox_router, prefix="/workbench")
app.include_router(prompt_router, prefix="/workbench")
app.include_router(operation_router, prefix="/workbench")
app.include_router(model_policy_todo_router, prefix="/workbench")
app.include_router(policy_router, prefix="/workbench")
app.include_router(repository_docs_router, prefix="/workbench")
app.include_router(system_control_router, prefix="/workbench")
app.include_router(service_monitor_router, prefix="/workbench")
app.include_router(terminal_router, prefix="/workbench")
app.include_router(plugin_router, prefix="/workbench")
install_plugins(app)


@app.get("/workbench/health")
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


@app.get("/workbench/whoami")
def whoami(request: Request) -> dict[str, Any]:
    """Identify the calling connection for client-side log naming.

    Websocket log names are `<server location> ⇄ <agent>@<ip>#<connection>`;
    the browser cannot see its own address, so this echoes what the server
    sees (through the Vite proxy this is the proxy's loopback address, which
    still identifies the machine).
    """

    client = request.client
    forwarded = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
    return {
        "ip": forwarded or (client.host if client else "unknown"),
        "port": client.port if client else None,
        "userAgent": request.headers.get("user-agent", ""),
    }


@app.get("/workbench/endpoints")
def list_endpoints() -> dict[str, Any]:
    """Full listing of every registered non-plugin route, method-by-method.

    Built from FastAPI's own OpenAPI schema (which already correctly flattens
    every ``include_router`` call, including the newer FastAPI versions'
    ``_IncludedRouter`` wrapper) rather than walking ``app.routes`` by hand.
    Diagnostic/introspection routes (``/docs``, ``/openapi.json``, the web
    interface relay itself) are intentionally excluded via
    ``include_in_schema=False`` on those routes, so this mirrors exactly what
    a consumer would consider "the API" -- not internal plumbing.
    """

    schema = app.openapi()
    endpoints = [
        {"path": path, "methods": sorted(method.upper() for method in (operations or {}) if method != "parameters")}
        for path, operations in sorted((schema.get("paths") or {}).items())
    ]
    return {"count": len(endpoints), "endpoints": endpoints}


@app.post("/workbench/analyze")
def analyze(body: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    try:
        return {"analysis": analyze_grid(body.get("grid"))}
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.post("/workbench/runs", status_code=201)
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


@app.get("/workbench/runs/{run_id}")
def get_run(run_id: str) -> dict[str, Any]:
    try:
        return {"run": store.get_run(run_id)}
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@app.post("/workbench/runs/{run_id}/commands")
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


@app.get("/workbench/runs/{run_id}/events")
def get_events(run_id: str, after: int = Query(default=0, ge=0)) -> dict[str, Any]:
    try:
        events = store.get_events(run_id, after)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return {"events": events, "cursor": events[-1]["id"] if events else after}


@app.get("/workbench/tasks")
def list_tasks(limit: int = Query(default=20, ge=1, le=200)) -> dict[str, Any]:
    """List thread/job tasks; executable artifacts use the operations API."""
    return {"tasks": store.list_tasks(limit)}


@app.get("/workbench/workflows")
def list_workflows() -> dict[str, Any]:
    """Compatibility endpoint for the retired mock-workbench client.

    Operation metadata is derived from default/operations on every request. The active
    workspace desktop should use /workbench/workspaces/{id}/snapshot instead.
    """
    shared_operations = load_shared_operation_documents()
    return {
        "workflows": store.list_workflows(),
        "operations": legacy_catalog_view(shared_operations),
        "datatypes": DATATYPE_MANIFEST,
        "deprecated": True,
        "replacement": "/workbench/workspaces/{workspace_id}/snapshot",
    }


@app.post("/workbench/workflows")
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


# --------------------------------------------------------------------------
# Web interface relay: registered LAST so every explicit route above (and
# every plugin route mounted by install_plugins()) is tried first. Anything
# still unmatched is genuinely the web interface's own territory (its app
# shell, module graph, and assets), so it is RELAYED here -- not redirected
# -- to the Vite dev server. A redirect would 302 the browser over to the
# web port, defeating the point of opening the API port at all; relaying
# instead makes the API port serve the exact same app, byte for byte, so the
# two ports are indistinguishable to a browser (no second origin, so no CORS
# concerns either). This mirrors, in the opposite direction, the catch-all
# `API_FALLBACK` proxy rule in frontend/vite.config.ts that sends anything
# the web port does not own to the API.
# --------------------------------------------------------------------------
_HOP_BY_HOP_HEADERS = {
    "connection", "keep-alive", "proxy-authenticate", "proxy-authorization",
    "te", "trailers", "transfer-encoding", "upgrade",
}
# Mirrors frontend/vite.config.ts's own VITE_OWNED allowlist -- the paths Vite
# genuinely serves itself (its app shell, module graph, and assets). Relaying
# is restricted to exactly this set: a request the API doesn't recognize AND
# Vite wouldn't recognize as its own either (a stale/renamed/typo'd endpoint,
# for example a stale `/workbench-old/health`) must 404 here, not relay blindly --
# Vite's OWN dev proxy (`API_FALLBACK` in vite.config.ts) sends anything IT
# doesn't own back to the API, so an over-broad relay here would ping-pong
# forever between the two ports for exactly the paths neither side owns.
_WEB_OWNED_RE = re.compile(
    r"^$|^@vite|^@id|^@fs|^@react-refresh|^__vite|^src/|^node_modules/|^assets/|^index\.html$|^favicon\.ico$"
)


def _is_web_owned(full_path: str, *, has_query: bool) -> bool:
    # Vite tags virtually all of its own module-loading requests with a query
    # string (cache-busting/import versioning), so a query string is treated
    # the same way vite.config.ts's own `\?` VITE_OWNED entry treats it.
    return has_query or bool(_WEB_OWNED_RE.match(full_path))


def _web_origin() -> str:
    """The Vite dev/preview server's origin, no trailing slash."""

    configured = os.environ.get("WORKBENCH_WEB_URL") or DEFAULT_WEB_URL
    return configured.rstrip("/")


def _filtered_headers(headers: Any, *, websocket: bool = False) -> dict[str, str]:
    ignored = _HOP_BY_HOP_HEADERS | {"host", "content-length"}
    if websocket:
        ignored |= {
            "sec-websocket-accept", "sec-websocket-extensions", "sec-websocket-key",
            "sec-websocket-protocol", "sec-websocket-version",
        }
    return {name: value for name, value in headers if name.lower() not in ignored}


async def _relay_to_web(request: Request, full_path: str = "") -> Response:
    if not _is_web_owned(full_path, has_query=bool(request.url.query)):
        raise HTTPException(status_code=404, detail="Not Found")
    target = f"{_web_origin()}/{full_path.lstrip('/')}" if full_path else f"{_web_origin()}/"
    if request.url.query:
        target = f"{target}?{request.url.query}"
    body = await request.body()
    async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
        try:
            upstream_response = await client.request(
                request.method, target, content=body, headers=_filtered_headers(request.headers.items()),
            )
        except httpx.HTTPError as error:
            raise HTTPException(status_code=502, detail=f"Web interface unreachable: {error}") from error
    return Response(
        content=upstream_response.content,
        status_code=upstream_response.status_code,
        headers=_filtered_headers(upstream_response.headers.multi_items()),
        media_type=upstream_response.headers.get("content-type"),
    )


async def _relay_web_websocket(websocket: WebSocket, full_path: str = "") -> None:
    """Relay a client WebSocket (Vite's HMR client) to the Vite dev server."""

    if not _is_web_owned(full_path, has_query=bool(websocket.url.query)):
        await websocket.close(code=1008)
        return
    path = f"/{full_path.lstrip('/')}" if full_path else "/"
    query = f"?{websocket.url.query}" if websocket.url.query else ""
    web_origin = _web_origin()
    ws_url = ("wss://" if web_origin.startswith("https://") else "ws://") + web_origin.split("://", 1)[1] + path + query
    requested_protocols = [
        value.strip() for value in websocket.headers.get("sec-websocket-protocol", "").split(",") if value.strip()
    ]
    try:
        async with websockets.connect(
            ws_url,
            additional_headers=_filtered_headers(websocket.headers.items(), websocket=True),
            subprotocols=requested_protocols or None,
            max_size=None,
        ) as upstream:
            await websocket.accept(subprotocol=upstream.subprotocol)

            async def client_to_upstream() -> None:
                while True:
                    message = await websocket.receive()
                    if message["type"] == "websocket.disconnect":
                        await upstream.close()
                        return
                    if message.get("bytes") is not None:
                        await upstream.send(message["bytes"])
                    elif message.get("text") is not None:
                        await upstream.send(message["text"])

            async def upstream_to_client() -> None:
                async for message in upstream:
                    if isinstance(message, bytes):
                        await websocket.send_bytes(message)
                    else:
                        await websocket.send_text(message)

            tasks = [asyncio.create_task(client_to_upstream()), asyncio.create_task(upstream_to_client())]
            done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            for task in pending:
                task.cancel()
            for task in done:
                task.result()
    except (WebSocketDisconnect, websockets.ConnectionClosed):
        return
    except Exception:  # noqa: BLE001 - any relay failure closes the client cleanly
        if websocket.client_state.name != "DISCONNECTED":
            await websocket.close(code=1011)


_RELAY_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"]
app.add_api_route("/", _relay_to_web, methods=_RELAY_METHODS, include_in_schema=False)
app.add_api_route("/{full_path:path}", _relay_to_web, methods=_RELAY_METHODS, include_in_schema=False)
app.add_api_websocket_route("/", _relay_web_websocket)
app.add_api_websocket_route("/{full_path:path}", _relay_web_websocket)
