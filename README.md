# Symbolic Learner ARC3 Kaggle Starter

This repository combines the delivered ARC3 debugger, the protected ARC-AGI-3 Kaggle workflow, and the connected object-memory and game-learning architecture.

## Documentation

- [Native Windows setup and troubleshooting](README_WINDOWS.md) — administrator long-path setup, Python and virtual-environment installation, batch launchers, line endings, SWI-Prolog, PyCharm, UNC paths, and native Kaggle commands.
- [LLM providers, prompt sections, and comparison transcripts](config/README.md) — switch providers, compose provider-specific prompts, compare runs, and restore historical artifacts.
- [ARC3 debugger guide](DEBUGGER.md) — debugger controls, action trees, GPT/Prolog analysis, Turtle reconstruction, web UI, and replay.
- [ARC Prize 2026 local-development and Kaggle guide](KAGGLE.md) — setup, local play, notebook generation, submission, accelerators, and troubleshooting.
- [SoW phase architecture](SOW_PHASE_ARCHITECTURE.md) — mapping of existing and connected code to Phases 1–3.
- [Implementation TODO](TODO.md) — reconciled status, remaining coding work, cross-language mapping, and acceptance tasks.
- [Clickable repository file tree](FILE_TREE.md) — links to maintained files with descriptions of their responsibilities.

## Layered code and resource discovery

ARC3 no longer assumes that code, configuration, and generated action trees must all share one global root. Startup records the directory from which the command was launched, resolves each resource independently, then enters the code checkout only for imports and legacy relative-script behavior.

### Code/runtime checkout

The Python code root is resolved in this order:

1. `ARC3_RUNTIME_HOME`, when explicitly set to a valid checkout.
2. The nearest valid project root found while walking upward from the launch directory.
3. The project root inferred from the running script/code location.

An invalid explicit `ARC3_RUNTIME_HOME` remains an error because it claims to select the code checkout.

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

Thus launching from a workspace that already contains `./action_trees/` keeps all generated state, transcripts, and `.pl` artifacts in that workspace.

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
# Run code from one checkout while using config/action_trees discovered from cwd.
cd /path/to/experiment-workspace
python /path/to/symbolic_learner_arc3_kaggle_starter/scripts/interactive_runner.py ls20

# Explicitly select only the code checkout; cwd resources still win when present.
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

The protected Kaggle workflow still uses the setup instructions in [KAGGLE.md](KAGGLE.md) and the existing Makefile targets. On native Windows, use the direct commands documented in [README_WINDOWS.md](README_WINDOWS.md) because the Makefile is POSIX-oriented.

## Runnable Python entry points and demonstrations

These commands may be run from the repository root or from another directory. Each script resolves code and data resources through the layered discovery above before importing project modules.

### Interactive terminal debugger

```bash
python scripts/interactive_runner.py ls20
```

On native Windows after setup:

```bat
scripts\interactive_runner.bat ls20
```

The debugger has one shared artifact pipeline and a configurable LLM provider list. Press `g` repeatedly to cycle through OpenAI/ChatGPT, Claude, Unsloth Studio, or custom providers. Providers and reusable prompt blocks share one file, [`config/llm_providers.json`](config/llm_providers.json); each provider selects the ordered `prompt_text` sections it receives.

Press `2`, `3`, or `4` for the demo, deep, or extreme profile. Every actual LLM request creates a uniquely named Markdown transcript containing a restorable artifact snapshot followed by the full debugging interaction. The normal `.pl` files remain the mutable latest view.

Press `1` in LLM mode to list historical transcripts for the current node, restore an older completed run back into the individual `.pl` files, or open the unified provider/prompt configuration for editing. The node `README.md` identifies the active completed transcript, links all historical runs, and embeds the latest mutable artifacts. Press `p` for Prolog mode. See [config/README.md](config/README.md).

Generated nodes also record the active provider selection in `llm_provider.json`.

### Browser terminal exposing the same debugger

```bash
python scripts/run_webui.py --game ls20
```

Then open `http://127.0.0.1:8765/`.

The browser terminal launches the same interactive runner and therefore uses the same provider cycling, composable prompts, transcript cache, and restore behavior.

### SWI-Prolog-controlled ARC3 demonstration

```bash
python scripts/prolog_controlled_runner.py
```

This uses `python/swipl_bridge.py` and `prolog/arc3_agent.pl`.

### Minimal direct ARC3 smoke demos

Print the action space, take one `ACTION1`, and show the scorecard:

```bash
python scripts/re_play.py
```

Take ten `ACTION1` steps and show the scorecard:

```bash
python scripts/my_play.py
```

Run up to 100 random actions with terminal rendering:

```bash
python scripts/me_play.py
```

Run up to 100 random actions with human rendering:

```bash
python scripts/he_play.py
```

These four scripts exercise the ARC3 client directly. They intentionally do not use the debugger or object-memory orchestration.

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

Normally this is run by `make setup` or `scripts\setup_windows.bat`.

### Run Python tests

```bash
pytest -q
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

The remaining `.pl` files are library modules exercised through these two test suites and the Python-controlled Prolog demonstration. See [FILE_TREE.md](FILE_TREE.md) for each module's purpose.

## Protected Kaggle entry points

Do not rename or repurpose:

- [`agent/my_agent.py`](agent/my_agent.py)
- [`scripts/play_local.py`](scripts/play_local.py)
- [`scripts/build_notebook.py`](scripts/build_notebook.py)
- [`notebooks/submission.ipynb`](notebooks/submission.ipynb)
- [`Makefile`](Makefile)
