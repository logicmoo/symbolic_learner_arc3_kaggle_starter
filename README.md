# Symbolic Learner ARC3 Kaggle Starter

This repository combines the delivered ARC3 debugger and extensible inspection framework, the protected ARC-AGI-3 Kaggle workflow, and the connected architecture for later object memory, learning, and prediction.

## Documentation

- [Native Windows setup and troubleshooting](README_WINDOWS.md) — administrator long-path setup, Python and virtual-environment installation, batch launchers, line endings, SWI-Prolog, PyCharm, UNC paths, and native Kaggle commands.
- [LLM providers, prompt sections, and comparison transcripts](config/README.md) — switch providers, compose provider-specific prompts, compare runs, and restore historical artifacts.
- [ARC3 debugger guide](DEBUGGER.md) — debugger controls, action trees, pluggable GPT/Prolog analysis, Turtle mock display, web UI, replay, and provider evidence.
- [ARC Prize 2026 local-development and Kaggle guide](KAGGLE.md) — setup, local play, notebook generation, submission, accelerators, and troubleshooting.
- [Architecture](SOW_PHASE_ARCHITECTURE.md) — large technical overview with phase boundaries, classes, modules, data contracts, ownership rules, per-object Turtle programs, learning, and prediction.
- [Active implementation TODO](TODO.md) — Phase 1 maintenance plus the concrete Phase 2 and Phase 3 work we need to execute next.
- [SOW deliverables checklist](SOW_DELIVERABLES.md) — delivered Phase 1 debugger outcomes and partial/open Phase 2 and Phase 3 outcomes with evidence links.
- [Clickable repository file tree](FILE_TREE.md) — links to maintained files with descriptions of their responsibilities.

The three project-planning documents deliberately have different scopes and link to one another:

```text
SOW_PHASE_ARCHITECTURE.md  → how the debugger, object memory, and learner are designed
TODO.md                    → what we are actively implementing
SOW_DELIVERABLES.md        → what is delivered and what remains to be checked off
```

## Project phase boundaries

- **Phase 1 is delivered:** the ARC3 debugger records rendered observations, actions, history, replay paths, provider calls, `object_registry.pl`, node READMEs, transcripts, Turtle mocks, objects, differences, similarities, candidate rules, critiques, and confidence outputs. These are inspectable provider artifacts; the debugger does not claim to implement their final semantic algorithms.
- **Phase 2 implements object semantics:** repeatable perception, persistent identities, correspondence, positive and negative recognition evidence, calibrated confidence, symbolic memory, and one regenerating Turtle program per recognized grid object using movement, rotation, pen state, and pen width rather than box filling.
- **Phase 3 implements learning and prediction:** competing transformations and rules, assumptions, critiques, probabilities, pre-outcome predictions, independent grades, evidence updates, and optional action recommendations written back through the debugger evidence surface.

## Layered code and resource discovery

ARC3 does not assume that code, configuration, and generated action trees share one global root. Startup records the launch directory, resolves each resource independently, and enters the code checkout only for imports and legacy relative-script behavior.

### Code/runtime checkout

The Python code root is resolved in this order:

1. `ARC3_RUNTIME_HOME`, when explicitly set to a valid checkout.
2. The nearest valid project root found while walking upward from the launch directory.
3. The project root inferred from the running script/code location.

An invalid explicit `ARC3_RUNTIME_HOME` is an error because it claims to select the code checkout.

### LLM provider and prompt configuration

The selected `config/llm_providers.json` is resolved independently:

1. `ARC3_LLM_CONFIG`.
2. `ARC3_CONFIG_ROOT/llm_providers.json`.
3. The nearest `config/llm_providers.json` found while walking upward from the launch directory.
4. `ARC3_RUNTIME_HOME/config/llm_providers.json`, when present.
5. The config beside the running script/code checkout.

This allows an experiment workspace to supply its own provider list and prompt sections while running code from another checkout.

### Action-tree output

The writable action-tree root is resolved independently:

1. `ARC3_TREE_ROOT`.
2. The nearest existing `action_trees/` found while walking upward from the launch directory.
3. `ARC3_RUNTIME_HOME/action_trees/`, when present.
4. The action-tree directory beside the running script/code checkout.
5. A newly created `action_trees/` beside the selected code root when none exists.

Launching from a workspace that already contains `./action_trees/` keeps generated state, transcripts, and `.pl` artifacts in that workspace.

### Environment files and startup report

The nearest launch-directory `.env` is loaded first, followed by distinct runtime/script checkout `.env` files. Loading uses `override=False`, so shell and IDE variables still win. The resolved paths are exported through `ARC3_LAUNCH_CWD`, `ARC3_RUNTIME_HOME`, `ARC3_LLM_CONFIG`, `ARC3_CONFIG_ROOT`, and `ARC3_TREE_ROOT`.

At startup ARC3 prints:

```text
ARC3 resolved paths
  Launch directory: ...
  Code/runtime root: ...
  Environment files: ...
  LLM config source: ...
  Action-tree output: ...
```

Set `ARC3_SHOW_PATHS=0` to suppress this report.

Examples:

```bash
cd /path/to/experiment-workspace
python /path/to/symbolic_learner_arc3_kaggle_starter/scripts/interactive_runner.py ls20

ARC3_RUNTIME_HOME=/path/to/symbolic_learner_arc3_kaggle_starter \
python /another/path/to/scripts/interactive_runner.py ls20
```

## Install

Python 3.12 or newer is required.

Native Windows users should first follow [README_WINDOWS.md](README_WINDOWS.md), then run:

```bat
scripts\setup_windows.bat
```

For debugger, web UI, notebooks, and tests:

```bash
python -m pip install -e ".[debugger,notebooks,test]"
```

The compatibility requirements file installs the same bundle:

```bash
python -m pip install -r requirements.txt
```

For every optional dependency, including Kaggle tooling:

```bash
python -m pip install -e ".[all]"
```

The protected Kaggle workflow still uses [KAGGLE.md](KAGGLE.md) and the existing Makefile targets. On native Windows, use the direct commands in [README_WINDOWS.md](README_WINDOWS.md).

## Runnable Python entry points and demonstrations

These commands may be run from the repository root or another directory. Each script resolves code and data resources through layered discovery before importing project modules.

### Interactive terminal debugger

```bash
python scripts/interactive_runner.py ls20
```

On native Windows:

```bat
scripts\interactive_runner.bat ls20
```

Press `g` repeatedly to cycle configured OpenAI/ChatGPT, Claude, Unsloth Studio, or custom providers. Providers and reusable prompt blocks share [`config/llm_providers.json`](config/llm_providers.json); each provider selects the ordered `prompt_text` sections it receives.

Press `2`, `3`, or `4` for demo, deep, or extreme analysis. Each LLM request creates a uniquely named Markdown transcript containing a restorable artifact snapshot followed by the full debugging interaction. The normal `.pl` files remain the mutable latest view.

Press `1` in LLM mode to list historical transcripts for the current node, restore an older completed run into the individual `.pl` files, or open the unified provider/prompt configuration. The node `README.md` identifies the active transcript, links historical runs, and embeds the latest artifacts. Press `p` for Prolog mode.

The provider-generated object, difference, similarity, Turtle, rule, critique, and confidence artifacts demonstrate the debugger’s pluggable inspection surface. Later phases implement and validate their semantic and predictive quality.

### Browser terminal

```bash
python scripts/run_webui.py --game ls20
```

Open `http://127.0.0.1:8765/`.

### SWI-Prolog-controlled ARC3 demonstration

```bash
python scripts/prolog_controlled_runner.py
```

### Minimal direct ARC3 smoke demos

```bash
python scripts/re_play.py
python scripts/my_play.py
python scripts/me_play.py
python scripts/he_play.py
```

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

### Slim the vendored framework

```bash
python scripts/slim_framework.py
```

### Run Python tests

```bash
pytest -q
```

### Open notebooks

```bash
jupyter lab
```

Use `notebooks/arc3_debugger.ipynb` for the guided debugger and `notebooks/arc3_runner.ipynb` for lower-level scripting.

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

See [FILE_TREE.md](FILE_TREE.md) for each module’s purpose.

## Protected Kaggle entry points

Do not rename or repurpose:

- [`agent/my_agent.py`](agent/my_agent.py)
- [`scripts/play_local.py`](scripts/play_local.py)
- [`scripts/build_notebook.py`](scripts/build_notebook.py)
- [`notebooks/submission.ipynb`](notebooks/submission.ipynb)
- [`Makefile`](Makefile)
