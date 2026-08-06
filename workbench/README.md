# MeTTaSymbolicLearnerWorkbench

A working React + FastAPI demo of the ARC3 symbolic-learning workbench UI.

## Included

- Ten-stage workflow rail with live statuses
- ARC grid with semantic object hover and selection
- Stable object identities across image, Turtle, and Prolog views
- Relative Turtle DSL examples using `fwd/1`, `rot/1`, `penup`, and `pendown`
- Prolog facts and query mockup
- Rule-induction and comparison views
- Artifact inspector with relationships and provenance
- Minimal FastAPI workflow and artifact endpoints

## Run on Linux/macOS

```bash
chmod +x run_demo.sh
./run_demo.sh
```

## Run on Windows

Double-click:

```text
run_demo.bat
```

Then open `http://localhost:5173`.

API documentation is available at `http://localhost:8000/docs`.

## Production build

```bash
cd frontend
npm install
npm run build
```

## API routes

```text
GET  /api/health
GET  /api/artifacts/{artifact_id}
POST /api/sessions/{session_id}/steps/{step_id}/run
POST /api/sessions/{session_id}/reset
```
