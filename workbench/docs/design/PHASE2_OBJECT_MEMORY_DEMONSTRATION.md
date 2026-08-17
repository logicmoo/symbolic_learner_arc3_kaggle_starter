# Phase 2 Object-Memory Demonstration

[Back to repository README](../../../README.md)

This deterministic demonstration exercises the complete Phase 2 path without
an LLM or network service. It uses the established grid extractor, the real
SWI-Prolog Turtle renderer, the action-tree registry, signed correspondence
evidence, the single identity writer, and exact semantic-record replay.

## Run it

From the repository root:

```powershell
.\.venv\Scripts\python.exe scripts\phase2_object_memory_demo.py `
  --output runtime\phase2_object_memory_demo
```

The command prints a machine-readable summary and writes
`runtime/phase2_object_memory_demo/phase2_demo_summary.json`. Its action tree
is under `runtime/phase2_object_memory_demo/action_trees/phase2_demo/level_1/`.
Open that directory's `README.md` to inspect links to every exact observation,
encounter, proposal, account, evidence record, object change, and Turtle source.

## What it proves

1. A logical grid is normalized into observations and object candidates.
2. Each candidate receives a movement-based Turtle program and is regenerated
   through SWI-Prolog; fit and residual evidence are persisted.
3. A friendly registry identity is offered for explicit authorization. The
   `SingleWriter` admits it at zero confidence and calibrates it only from
   attributable signed evidence.
4. A second grid translates the blue hollow object. Correspondence and
   before/after comparison persist a `moved` object-change record.
5. The later encounter resolves to the same durable `known_shape` identity.
6. A fresh `SymbolicStore` is rebuilt exclusively from linked
   `semantic_records.json` manifests. Its encounter hash and summary demonstrate
   deterministic replay after process restart.

## Regression evidence

`tests/test_phase2_object_memory_demo.py` runs the same workflow and requires
two observations, four encounters, four exact Turtle reconstructions, two
resolved recognition accounts, a moved-object record, and a 64-character
deterministic replay hash.
