# Repository File Tree and Responsibilities

This tree documents the active architecture. It distinguishes existing Phase 1
code from the supplementary Phase 2/3 contracts added without duplicating the
working debugger or Kaggle workflow.

```text
.
├── README.md
│   Main ARC3 debugger documentation and operating instructions.
├── docs/
│   ├── FILE_TREE.md
│   │   This annotated directory tree.
│   └── SOW_PHASE_ARCHITECTURE.md
│       Mapping from existing code to the three SoW phases and execution modes.
├── agent/
│   └── my_agent.py
│       Protected Kaggle agent entry point. Kept unchanged.
├── notebooks/
│   └── submission.ipynb
│       Protected generated Kaggle submission notebook. Kept unchanged.
├── scripts/
│   ├── build_notebook.py
│   │   Protected notebook builder. Kept unchanged.
│   └── play_local.py
│       Protected local Kaggle-compatible runner. Kept unchanged.
├── examples/
│   ├── interactive_runner.py
│   │   Existing full terminal debugger used by the web UI.
│   └── prolog_controlled_runner.py
│       Existing executable demonstration of SWI-Prolog action selection.
├── python/
│   ├── arc3_runner.py
│   │   Existing Phase 1 environment, history, replay, and action-tree coordinator.
│   ├── action_tree.py
│   │   Existing deterministic filesystem state/action tree and object registry.
│   ├── gpt_bridge.py
│   │   Existing combined GPT artifact generator and cache integration.
│   ├── swipl_bridge.py
│   │   Existing subprocess bridge to SWI-Prolog.
│   └── object_memory/
│       ├── __init__.py
│       │   Public imports for the shared SoW contracts.
│       ├── models.py
│       │   Backend-neutral records: CandidateObject, ResidualCandidate,
│       │   CommittedAtom, TransitionRule, PredictionRecord, NormalizedResult.
│       ├── providers.py
│       │   One provider contract with PROLOG, GPT, and PYTHON implementations.
│       ├── forms.py
│       │   GenerativeForm interface and CellLogoForm facade over Turtle programs.
│       ├── adapters.py
│       │   PerceptionAdapter and thin GridAdapter around existing extractors.
│       ├── memory.py
│       │   ResidualGate, SymbolicMemory reference store, and SingleWriter.
│       ├── prediction.py
│       │   PredictionLedger with prediction-before-outcome enforcement.
│       └── integration.py
│           GameObjectLearnerPlugin and normalized Phase 3 handoff payload.
├── prolog/
│   ├── arc3_agent.pl
│   │   Existing SWI-Prolog action-selection skeleton.
│   ├── turtle_dsl.pl
│   │   Existing authoritative Turtle execution semantics.
│   ├── object_memory_contract.pl
│   │   Canonical Prolog records and normalized candidate access predicates.
│   ├── generative_form.pl
│   │   Reuses turtle_dsl.pl for grid rendering; no duplicate drawing engine.
│   ├── residual_gate.pl
│   │   Symbolic residual disposition and admission decision.
│   ├── single_writer.pl
│   │   Sole Prolog mutation path for committed atoms and evidence.
│   └── prediction_ledger.pl
│       Durable predictions and prediction-before-outcome grading checks.
└── tests/
    └── test_object_memory_contracts.py
        Focused provider, zero-confidence, residual, prediction, and Kaggle-path tests.
```

## Why the runners were not moved

`examples/interactive_runner.py` remains the sole debugger implementation because
`webui/server.py` launches it directly and the existing README documents that
command. Moving it now would require coordinated launcher and documentation
migration. A future move to `scripts/interactive_runner.py` should keep one real
implementation and, only if still required, a thin deprecated forwarding script.

`examples/prolog_controlled_runner.py` is likewise retained until all references
are checked. No duplicate implementation was added under `scripts/`.
