# Symbolic Learner ARC3 Kaggle Starter

This repository combines the delivered ARC3 debugger, the protected ARC-AGI-3 Kaggle workflow, and the connected object-memory and game-learning architecture.

## Documentation

- [ARC3 debugger guide](DEBUGGER.md) — debugger controls, action trees, GPT/Prolog analysis, Turtle reconstruction, web UI, and replay.
- [ARC Prize 2026 local-development and Kaggle guide](KAGGLE.md) — setup, local play, notebook generation, submission, accelerators, and troubleshooting.
- [SoW phase architecture](SOW_PHASE_ARCHITECTURE.md) — mapping of existing and connected code to Phases 1–3.
- [Implementation TODO](TODO.md) — reconciled status, remaining coding work, cross-language mapping, and acceptance tasks.
- [Clickable repository file tree](FILE_TREE.md) — links to maintained files with descriptions of their responsibilities.

## Install debugger dependencies

```bash
pip install -r requirements.txt
```

For the protected Kaggle workflow, use the setup instructions in [KAGGLE.md](KAGGLE.md).

## Runnable Python entry points and demonstrations

Run these commands from the repository root.

### Interactive terminal debugger

```bash
python scripts/interactive_runner.py ls20
```

### Browser terminal exposing the same debugger

```bash
python scripts/run_webui.py --game ls20
```

Then open `http://127.0.0.1:8765/`.

### SWI-Prolog-controlled ARC3 demonstration

```bash
python scripts/prolog_controlled_runner.py
```

This uses `python/swipl_bridge.py` and `prolog/arc3_agent.pl`.

### Protected local Kaggle-compatible agent run

```bash
python scripts/play_local.py --game ls20 --max-steps 200
```

Equivalent Makefile command:

```bash
make play-local GAME=ls20 STEPS=200
```

### Build the protected Kaggle submission notebook

```bash
python scripts/build_notebook.py
```

Equivalent Makefile command:

```bash
make notebook
```

### Slim the vendored ARC-AGI-3 Agents framework

```bash
python scripts/slim_framework.py
```

Normally this is run by `make setup`.

### Run Python contract and documentation tests

```bash
pytest -q tests/test_object_memory_contracts.py tests/test_documentation_links.py
```

### Open the notebooks

```bash
jupyter lab
```

Use `notebooks/arc3_debugger.ipynb` for the guided debugger and `notebooks/arc3_runner.ipynb` for lower-level scripted use.

## Runnable Prolog demonstrations and checks

### Turtle DSL tests

```bash
swipl -q -s prolog/test_turtle_dsl.pl -g run_tests,halt
```

### Object-memory and connected Phase 3 tests

```bash
swipl -q -s prolog/test_object_memory.pl -g run_tests,halt
```

### Load the action-selection controller

```bash
swipl -q -g "use_module('prolog/arc3_agent.pl'),halt"
```

### Load the connected Game Object Learner pipeline

```bash
swipl -q -g "use_module('prolog/game_object_learner_api.pl'),halt"
```

The remaining `.pl` files are library modules exercised through these two test suites and the Python-controlled Prolog demonstration. See [FILE_TREE.md](FILE_TREE.md) for each module’s purpose.

## Protected Kaggle entry points

Do not rename or repurpose:

- [`agent/my_agent.py`](agent/my_agent.py)
- [`scripts/play_local.py`](scripts/play_local.py)
- [`scripts/build_notebook.py`](scripts/build_notebook.py)
- [`notebooks/submission.ipynb`](notebooks/submission.ipynb)
- [`Makefile`](Makefile)
