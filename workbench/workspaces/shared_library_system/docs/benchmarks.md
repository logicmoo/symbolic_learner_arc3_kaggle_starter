[← Back to top-level README](../../../../README.md) · [Documentation contents](contents.md)

# Benchmarks

The Benchmarks page is a focused projection of the same filesystem registry used by Model Policy. It contains no separate browser-only catalog and does not generate sample results.

## Benchmark dimensions

Each benchmark combines:

- one enabled `benchmark_policy`;
- its declared Model Presets;
- optional Prompt Profiles; and
- models whose effective benchmark policy and required capabilities permit execution.

Preflight explains why a run is blocked. The compatibility matrix distinguishes enabled and compatible, enabled but limited, disabled, and incompatible combinations before any provider call is made.

## Running and inspecting results

**Run Benchmark** queues a durable job through the backend. Completed measurements are persisted as benchmark-result resources and remain available after reload or restart. The history surface can show every chronological result, the latest result per model/preset/profile series, or an average per series, and can filter by model, Model Preset, Prompt Profile, and metric.

Health checks and benchmark runs are intentionally separate. A ping observes availability; a benchmark executes declared cases and records measurements. Neither operation silently changes wanted/runtime/benchmark intent.

Use **Manage Models & Presets** when a policy references a missing execution dimension. Use **Model Policy** when no models are effectively benchmark-enabled.
