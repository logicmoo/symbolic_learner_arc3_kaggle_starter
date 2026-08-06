# MeTTaSymbolicLearnerWorkbench local web workbench

This directory contains the complete locally runnable workbench: a React/Vite
web interface and a FastAPI event backend with SQLite persistence.

## Run it on Windows

After pulling `main`, run this from the repository root:

```text
run_workbench.bat
```

`workbench\run_demo.bat` is the underlying launcher and can also be run
directly.

The Windows launcher accepts optional network arguments:

```text
run_workbench.bat [bind_ip] [web_port] [api_port]
```

With no arguments it preserves the original addresses:

```text
Web: http://127.0.0.1:5173/
API: http://127.0.0.1:8000/
```

If a non-default web port is supplied and `api_port` is omitted, the API port
is automatically the next port. For example, this starts a second independent
server pair on web port 5200 and API port 5201:

```text
run_workbench.bat 127.0.0.1 5200
```

A third argument explicitly chooses the API port:

```text
run_workbench.bat 127.0.0.1 5300 8300
```

To listen on all IPv4 interfaces while still opening the local browser through
`127.0.0.1`, use:

```text
run_workbench.bat 0.0.0.0 5400
```

Each invocation gives its API and web command windows port-specific titles,
and Vite's `/api` proxy is pointed at the FastAPI instance started by that same
invocation. This allows several workbench instances to run from one checkout
at the same time as long as their selected ports do not overlap.

The launcher performs first-run setup, starts the API and web development
servers in separate command windows, waits until they are ready, and opens the
selected web address.

You do not need to deploy anything. Changes under `workbench\frontend\src`
refresh in the browser through Vite. Changes under `workbench\server` restart
the FastAPI backend through Uvicorn. Close the two server windows for an
instance when done.

Requirements:

- Python 3.12 or newer on `PATH`
- Node.js 22 or newer, including `npm`, on `PATH`

The first launch installs dependencies and therefore takes longer. Later
launches reuse `workbench\.venv` and `workbench\frontend\node_modules`.

## What is included

- Filesystem-enumerated workspaces and an editable shared library workspace
- Seven-stage ARC3 apprenticeship workflow
- Human-action pause with keyboard and on-screen controls
- Durable workflow-design and workflow-execution tasks
- Ordered backend events, versioned artifacts, and provenance
- Topology and chronology views
- Workflow library, structured editor, and raw JSON editor
- Shared and workspace-specific task definitions
- First-class abstract datatypes and concrete datatype representations
- Representation-conversion tasks and cost-based conversion path planning
- Shared and workspace-specific backend/model definitions
- Nested-workflow validation and cycle detection
- Artifact, evidence, LLM, validation, and setup views
- SQLite state in `workbench/data/workbench.db`

The Python, SWI-Prolog, LLM, Turtle, and ARC3 execution engines remain adapter
boundaries. The local server implements the shared command/event contract and
persists workflows, tasks, runs, artifacts, and history.

## Datatypes and representations

The workbench treats the semantic datatype and its concrete representation as
separate first-class resources. For example, `image` is an abstract datatype,
while bitmap, SVG, LOGO/Turtle, scene graph, object list, natural-language
description, and latent embedding are representations of that same meaning.

Shared resources are stored as one JSON file per definition:

```text
workbench/workspaces/shared/datatypes/
workbench/workspaces/shared/representations/
```

A normal workspace inherits these definitions and can override a shared
resource by defining the same resource ID locally. Conversion tasks are normal
abstract tasks with a `conversion` contract, so the planner can find paths such
as:

```text
bitmap -> scene_graph -> logo_program
bitmap -> object_list -> logo_program
natural_language -> scene_graph
```

PNG, JPEG, and BMP are modeled as encodings of the bitmap representation rather
than as different semantic datatypes.

The design and resource schemas are described in
`workbench/docs/DATA_REPRESENTATIONS.md`.

## Run it on Linux or macOS

```bash
cd workbench
chmod +x run_demo.sh
./run_demo.sh
```

Then open `http://127.0.0.1:5173/`. API documentation is available at
`http://127.0.0.1:8000/docs`.

## Manual development commands

Backend:

```bash
cd workbench/server
../.venv/bin/python -m uvicorn app:app --reload --port 8000
```

Frontend:

```bash
cd workbench/frontend
npm run dev
```

Production frontend check:

```bash
cd workbench/frontend
npm run build
```

Set `WORKBENCH_DB` to an alternate SQLite path when an isolated database is
useful for tests or experiments. Multiple launcher instances use the same
default database unless you start them with different `WORKBENCH_DB`
environment values.

## Main API routes

```text
GET  /api/health
GET  /api/workspaces/{workspace_id}/snapshot
GET  /api/workspaces/{workspace_id}/tasks
GET  /api/workspaces/{workspace_id}/datatypes
GET  /api/workspaces/{workspace_id}/representations
GET  /api/workspaces/{workspace_id}/representation-graph
GET  /api/workspaces/{workspace_id}/datatypes/{datatype_id}/resolve
GET  /api/workspaces/{workspace_id}/datatypes/{datatype_id}/plan?source=bitmap&target=logo_program
POST /api/runs
GET  /api/runs/{run_id}
POST /api/runs/{run_id}/commands
GET  /api/runs/{run_id}/events?after={cursor}
GET  /api/tasks
GET  /api/workflows
POST /api/workflows
```
