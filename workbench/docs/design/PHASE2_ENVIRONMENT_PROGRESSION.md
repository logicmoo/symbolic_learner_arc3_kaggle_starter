# Phase 2 Environment Progression

The deterministic progression demo verifies that broader raster environments use
the same normalized `Observation` and `CandidateObject` contracts as logical
grids. It does not introduce an environment-specific identity store.

Run:

```powershell
.\.venv\Scripts\python.exe scripts\phase2_environment_progression_demo.py `
  --output runtime\phase2_environment_progression
```

The command generates and evaluates seven fixtures:

- one rendered arcade frame containing three disconnected sprites;
- three fixed-camera frames containing a moving ball and stationary floor;
- clean, modest-noise, and partly occluded top-down manipulation scenes.

The generated `environment_progression_summary.json` records every expected and
detected object count, degradation type, per-fixture score, and the aggregate
acceptance result. Re-running the command produces the same ordered results.

Run the object-memory and Phase 3 learning demonstrations, then verify all three
summaries and generate the final evidence report:

```powershell
.\.venv\Scripts\python.exe scripts\phase2_object_memory_demo.py `
  --output runtime\phase2_object_memory_demo
.\.venv\Scripts\python.exe scripts\phase3_learning_demo.py `
  --output runtime\phase3_learning_demo
```

```powershell
.\.venv\Scripts\python.exe scripts\generate_phase2_acceptance_report.py `
  --object-memory-summary runtime\phase2_object_memory_demo\phase2_demo_summary.json `
  --environment-summary runtime\phase2_environment_progression\environment_progression_summary.json `
  --phase3-summary runtime\phase3_learning_demo\phase3_learning_summary.json `
  --test-result "513 passed" `
  --commit $(git rev-parse HEAD) `
  --output runtime\phase2_acceptance
```

The generator exits unsuccessfully if required identity, reconstruction, replay,
environment, predict-before-outcome, independent-grade, calibrated-update, test,
or commit evidence is missing. Its JSON output is suitable for automation; its
Markdown output is the corresponding human-readable audit.

These fixtures prove contract integration and deterministic baseline extraction.
They do not claim production recognition quality for arbitrary photographic or
game-engine inputs; additional perception providers can be compared with the
same benchmark and provider-ablation runners.

[← Back to top-level README](../../../README.md)
