# MeTTaSymbolicLearnerWorkbench local web demo

This directory contains the complete locally runnable workbench: a React/Vite
web interface and a FastAPI event backend with SQLite persistence.

## Run it on Windows

After pulling `main`, run this from the repository root:

```text
run_workbench.bat
```

`workbench\run_demo.bat` is the underlying launcher and can also be run
directly.

The launcher performs first-run setup, starts the API and web development
servers in separate command windows, waits until they are ready, and opens:

```text
http://127.0.0.1:5173/
```

You do not need to deploy anything. Changes under `workbench\frontend\src`
refresh in the browser through Vite. Changes under `workbench\server` restart
the FastAPI backend through Uvicorn. Close the two server windows when done.

Requirements:

- Python 3.12 or newer on `PATH`
- Node.js 22 or newer, including `npm`, on `PATH`

The first launch installs dependencies and therefore takes longer. Later
launches reuse `workbench\.venv` and `workbench\frontend\node_modules`.

## What is included

- Seven-stage ARC3 apprenticeship demonstration
- Human-action pause with keyboard and on-screen controls
- Durable workflow-design and workflow-execution tasks
- Ordered backend events, versioned artifacts, and provenance
- Topology and chronology spline modes
- Visible loop-back arcs for repeated task steps
- Hover previews and pinned event inspection
- Workflow library, structured editor, and raw JSON editor
- Typed task and datatype catalogs
- Nested-workflow validation and cycle detection
- Artifact, evidence, LLM, validation, and setup views
- SQLite state in `workbench/data/workbench.db`

The Python, SWI-Prolog, LLM, Turtle, and ARC3 execution engines remain adapter
boundaries. The local server implements the shared command/event contract and
persists the demonstrator's workflows, tasks, runs, artifacts, and history.

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
useful for tests or experiments.

## Main API routes

```text
GET  /api/health
POST /api/runs
GET  /api/runs/{run_id}
POST /api/runs/{run_id}/commands
GET  /api/runs/{run_id}/events?after={cursor}
GET  /api/tasks
GET  /api/workflows
POST /api/workflows
```
