[← Back to top-level README](README.md)

# ARC Prize 2026 — Local Dev Starter

This repository includes a protected local-development and Kaggle submission workflow for ARC-AGI-3. The notebook is generated from `agent/my_agent.py`; do not maintain a second agent implementation inside the notebook.

## Requirements

- Python 3.12
- git
- A Kaggle account with the ARC Prize 2026 competition rules accepted
- A Kaggle API token stored in `.kaggle/access_token`

The local token path is intentionally project-specific and is ignored by git.

## Quick start

```bash
# 1. Create the project-local Kaggle token file.
mkdir -p .kaggle
printf '%s\n' 'KGAT_your_token_here' > .kaggle/access_token
chmod 600 .kaggle/access_token

# 2. Create the virtual environment, install dependencies,
#    and clone the ARC-AGI-3 Agents framework.
make setup

# 3. Run the protected agent locally.
make play-local GAME=ls20 STEPS=200

# 4. Build the generated notebook without uploading.
make notebook

# 5. Build and upload the notebook to Kaggle.
make submit

# 6. Check the Kaggle kernel status.
make status
```

When the Kaggle kernel run completes, open it on Kaggle and select **Submit to Competition** using the generated `submission.parquet` output.

## Protected Kaggle surface

Do not rename, move, repurpose, or break:

- `agent/my_agent.py`
- `scripts/play_local.py`
- `scripts/build_notebook.py`
- `notebooks/submission.ipynb`
- `notebooks/kernel-metadata.json`
- existing Kaggle-related Makefile commands
- imports, paths, and packaging rules required by the Kaggle workflow

## The agent source

`agent/my_agent.py` defines `MyAgent`, which must continue to satisfy the ARC-AGI-3 Agents framework contract:

```python
class MyAgent(Agent):
    def is_done(self, frames, latest_frame) -> bool:
        ...

    def choose_action(self, frames, latest_frame) -> GameAction:
        ...
```

The starter implementation is a valid random baseline. Replace its action-selection strategy without changing the protected class name or notebook packaging contract.

Run the agent locally through:

```bash
python scripts/play_local.py --game ls20 --max-steps 200
```

or:

```bash
make play-local GAME=ls20 STEPS=200
```

## Local runner behavior

`scripts/play_local.py`:

1. Loads `agent/my_agent.py` dynamically.
2. Uses the vendored ARC-AGI-3 Agents framework.
3. Opens real ARC3 environments through `arc_agi.Arcade`.
4. Runs one selected game, a comma-separated game list, or all available games.
5. Prints per-game state, completed levels, action counts, and the aggregate scorecard.

Examples:

```bash
python scripts/play_local.py --list
python scripts/play_local.py --game ls20 --max-steps 50
python scripts/play_local.py --game ls20,vc33 --max-steps 50
```

## Makefile commands

| Command | Responsibility |
|---|---|
| `make setup` | Create `.venv`, install ARC/Kaggle dependencies, clone the framework, and slim framework imports. |
| `make play-local` | Run `MyAgent` locally against all games. |
| `make play-local GAME=ls20` | Run one selected game. |
| `make verify-local` | Smoke-test selected games with a reduced action limit. |
| `make list-games` | List available ARC3 environments. |
| `make pull-sample` | Download the official reference notebook. |
| `make notebook` | Generate `notebooks/submission.ipynb` from `agent/my_agent.py`. |
| `make submit` | Generate and upload the notebook to Kaggle. |
| `make status` | Check the latest Kaggle kernel status. |
| `make clean` | Remove generated local artifacts. |

## Notebook generation

Run directly:

```bash
python scripts/build_notebook.py
```

or:

```bash
make notebook
```

The builder creates `notebooks/submission.ipynb` with the competition pattern:

1. Install the competition-provided offline wheels.
2. Write the current `agent/my_agent.py` into the Kaggle working directory.
3. On competition rerun, copy and configure the ARC-AGI-3 Agents framework.
4. Register `MyAgent` and run the framework against the gateway.
5. During ordinary notebook commit validation, emit a placeholder `submission.parquet` so the save-and-run step succeeds.

`notebooks/submission.ipynb` is generated output and should not be edited by hand.

## Kaggle kernel metadata

`notebooks/kernel-metadata.json` contains the Kaggle kernel ID and accelerator settings. Confirm that its `id` uses the intended Kaggle account and slug before running `make submit`.

## Accelerator selection

`scripts/build_notebook.py` defines:

```python
ACCELERATOR = "t4"
```

Supported values currently include:

| Value | Hardware | Typical use |
|---|---|---|
| `cpu` | No GPU | Symbolic or lightweight agents. |
| `t4` | Nvidia T4 | Default accelerated configuration. |
| `p100` | Nvidia P100 | Larger single-GPU workloads. |
| `rtx6000` | Nvidia RTX 6000 | Heavy ARC-AGI-3 workloads; use carefully. |

Rebuild the notebook after changing the accelerator.

## Framework slimming

The upstream agent package may eagerly import optional LLM frameworks. The repository keeps the Kaggle environment lightweight by running:

```bash
python scripts/slim_framework.py
```

This is normally invoked automatically by `make setup`.

## Submission flow

Kaggle code competitions effectively run the notebook in two stages:

```text
make submit
    ↓
Kaggle save-and-run validation
    ↓
make status reports completion
    ↓
Submit to Competition
    ↓
competition rerun against hidden games
```

A completed notebook run is not yet a leaderboard submission. The final **Submit to Competition** action selects the produced `submission.parquet`.

## Project paths used by the Kaggle workflow

```text
agent/
└── my_agent.py

scripts/
├── play_local.py
├── build_notebook.py
└── slim_framework.py

notebooks/
├── kernel-metadata.json
└── submission.ipynb

vendor/
└── ARC-AGI-3-Agents/     generated by setup; gitignored

.kaggle/
└── access_token          local credential; gitignored
```

The debugger scripts also live in `scripts/`, but they do not replace or alter the protected Kaggle entry points.

## Troubleshooting

### `python3.12` is unavailable

Install Python 3.12 and ensure the `PYTHON` Makefile variable points to it.

### `.kaggle/access_token` is missing

Create the file as one line containing the current Kaggle token. Do not commit it.

### Kaggle returns `401 Unauthorized`

Replace the token with a newly generated token from Kaggle settings, then retry.

### `make submit` rejects the kernel metadata

Inspect `notebooks/kernel-metadata.json` and confirm the kernel ID belongs to the intended Kaggle account.

### Local game creation fails

The first local run may need network access to obtain game assets. Once cached, subsequent runs use the local environment files.

### Local score is zero

The starter agent is intentionally a valid but weak baseline. A zero score does not imply that notebook construction or submission plumbing is broken.

### Framework directory is missing

Run:

```bash
make setup
```

The setup target clones the framework into `vendor/ARC-AGI-3-Agents`.

## Relationship to the debugger

The Kaggle workflow and debugger share repository code but have separate responsibilities:

- [DEBUGGER.md](DEBUGGER.md) documents interactive exploration, action trees, GPT/Prolog artifacts, replay, and the browser terminal.
- This file documents protected local-agent execution, notebook generation, and Kaggle submission.

[← Back to top-level README](README.md)
