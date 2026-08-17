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

These fixtures prove contract integration and deterministic baseline extraction.
They do not claim production recognition quality for arbitrary photographic or
game-engine inputs; additional perception providers can be compared with the
same benchmark and provider-ablation runners.

[← Back to top-level README](../../../README.md)
