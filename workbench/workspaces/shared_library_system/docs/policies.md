[← Back to documentation contents](contents.md)

# Policies

Policies are filesystem-backed MeTTa resources that control runtime eligibility, health interpretation, testing, and other workbench decisions without rewriting the resources they govern.

Policy resources may remain under `policies/`, where policy definitions, observations, jobs, events, and benchmark results form a related operational family. A policy alternative uses the same `kind` as its parent and declares that relationship through `parents`; there are no separate variant kinds or variant directories.

## Model policy

- `model_policy` defines the shared runtime and benchmarking rules.
- `vendor_policy` and `model_policy_entry` preserve explicit wanted, runtime, and benchmark intent.
- Backends and models are eligible by default until a persisted policy disables them.
- Workspace policy overrides inherit shared policy and affect only that workspace.
- Health observations and ping events are evidence. They never silently rewrite user intent.

The effective state shown by **Model Policy** is calculated from resource enablement, inherited vendor/model intent, observed health, and policy rules. Use the page's filesystem load/save actions to inspect or persist those decisions.

## Benchmark policy

A `benchmark_policy` declares cases, Model Presets, Prompt Profiles, required capabilities, metrics, and repetitions. Running one creates durable benchmark jobs and results; it does not alter the benchmark definition or model policy.

Use the separate **Benchmarks** page for preflight, compatibility matrices, execution, and performance history.

[Open Benchmarks documentation](benchmarks.md)
