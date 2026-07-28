# ARC3 Debugger and Kaggle Operating Guide

This file preserves the complete operational material that previously lived in the top-level README. The active top-level README is now a documentation hub.

For the current architecture and implementation status, see:

- [Documentation index](README.md)
- [SoW phase architecture](SOW_PHASE_ARCHITECTURE.md)
- [Implementation backlog](IMPLEMENTATION_BACKLOG.md)
- [Clickable file tree](FILE_TREE.md)

## ARC3 debugger operating guide

The debugger opens real ARC3 games and levels, captures frames after each action, records deterministic action branches, generates symbolic Prolog artifacts, refreshes GitHub-friendly state-node READMEs, and reuses cached analysis.

### Shared roots

```text
prompts/
└── gpt_prompts.json

action_trees/
└── <game>/
    └── level_<n>/
        ├── histories/
        ├── exports/
        └── ... state and action branches ...
```

Override them with `ARC3_PROMPTS_ROOT` and `ARC3_TREE_ROOT` when needed.

### Terminal controls

```text
Game actions
  Up/Down/Left/Right  ACTION1..ACTION4
  Space               ACTION5
  c                   coordinate ACTION6
  Ctrl-Z              ACTION7 / undo

Selection
  Shift+Left/Right    previous/next game
  Shift+Up/Down       previous/next level

Recorded history
  Ctrl+Left/Right     previous/next step
  Ctrl+Up/Down        first/latest step

Reset and execution
  r                   reset current level
  R                   restart current game
  Enter               redraw current stored frame
  v                   replay
  w                   save history
  e                   export state
  x                   pause/resume
  .                   single queued step
  q                   quit
```

### GPT and Prolog modes

```text
g  GPT mode
p  Prolog mode
```

In GPT mode, `(2)`, `(3)`, and `(4)` run the same combined artifact pipeline at increasing depth. The normal demonstration path is `(g)` then `(2)`.

The combined pipeline captures or reuses `image.png`, ensures parent/current object context, produces or reuses `objects.pl`, `differences.pl`, `similarities.pl`, `turtle_from_image.pl`, `turtle_from_diff.pl`, and `rules.pl`, updates the level-wide `object_registry.pl`, and refreshes current and parent READMEs.

### Friendly identity policy

The level-wide `object_registry.pl` is authoritative. Friendly names such as `blue_player`, `red_goal`, or `left_wall` are reused across the whole level and every action-tree branch. Opaque numbered IDs are rejected or repaired. Node-local `objects.pl` files contain state-specific facts and reference the shared registry instead of repeating identities.

### Action-tree layout

```text
action_trees/
└── ls20/
    └── level_1/
        ├── README.md
        ├── image.png
        ├── state.json
        ├── object_registry.pl
        ├── objects.pl
        ├── LEFT/
        │   ├── README.md
        │   ├── image.png
        │   ├── state.json
        │   ├── objects.pl
        │   ├── differences.pl
        │   ├── similarities.pl
        │   ├── turtle_from_image.pl
        │   ├── turtle_from_diff.pl
        │   └── rules.pl
        └── UP/
            └── ...
```

The level directory itself is the initial state. Each action directory is the resulting state. Coordinate actions include coordinates in the directory name.

### Turtle vocabulary

```prolog
penup.
pendown.
set_pos(X, Y).
setcolor(Color).
pen_width(Width).  % 1..4 logical cells
fwd(Distance).
rot(Degrees).
set_cell.
```

Generated programs favor motion and turns over direct block placement. Filled areas are represented by scan-line strokes, using `pen_width/1` where exact.

### Browser terminal

Run:

```powershell
pip install -r requirements.txt
python run_webui.py --game ls20
```

Then open `http://127.0.0.1:8765/`.

For non-loopback binding, set an access token:

```powershell
$env:ARC3_WEB_TOKEN="choose-a-long-random-token"
python run_webui.py --host 0.0.0.0 --port 8765 --game ls20
```

The browser launches the same `examples/interactive_runner.py` through PTY/ConPTY; it is not a second debugger implementation.

### Requirements and launch

```bash
pip install -r requirements.txt
python examples/interactive_runner.py ls20
```

For GPT mode:

```powershell
$env:OPENAI_API_KEY="your-api-key"
$env:ARC3_GPT_MODEL="gpt-5.6"
```

## Kaggle operating guide

The protected Kaggle workflow keeps local development and the generated submission notebook in lock-step:

```text
agent/my_agent.py
    -> make play-local
    -> make notebook / make submit
    -> notebooks/submission.ipynb
```

### Prerequisites

- Python 3.12
- git
- a Kaggle account with the ARC-AGI-3 competition rules accepted
- a project-local token at `.kaggle/access_token`

### Quick start

```bash
git clone https://github.com/logicmoo/symbolic_learner_arc3_kaggle_starter.git
cd symbolic_learner_arc3_kaggle_starter
mkdir -p .kaggle
echo "KGAT_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" > .kaggle/access_token
chmod 600 .kaggle/access_token
make setup
make play-local
make submit
make status
```

When the Kaggle run is complete, open the kernel page and deliberately select **Submit to Competition** using the generated `submission.parquet`.

### Protected source files

- [`../agent/my_agent.py`](../agent/my_agent.py) — agent implementation and required `MyAgent` contract.
- [`../scripts/play_local.py`](../scripts/play_local.py) — local game runner.
- [`../scripts/build_notebook.py`](../scripts/build_notebook.py) — notebook generator.
- [`../notebooks/submission.ipynb`](../notebooks/submission.ipynb) — generated submission artifact.
- [`../notebooks/kernel-metadata.json`](../notebooks/kernel-metadata.json) — Kaggle kernel identity and accelerator metadata.
- [`../Makefile`](../Makefile) — supported workflow commands.

### Make commands

| Command | Purpose |
|---|---|
| `make setup` | Create the venv, install dependencies, and clone the official framework |
| `make play-local` | Run the agent locally against all available games |
| `make play-local GAME=ls20` | Run one game |
| `make verify-local` | Short local smoke test |
| `make list-games` | List available game IDs |
| `make pull-sample` | Download the official sample notebook |
| `make notebook` | Generate the Kaggle notebook without uploading |
| `make submit` | Generate and upload the notebook |
| `make status` | Check the latest Kaggle run |
| `make clean` | Remove generated local artifacts |

### Accelerator selection

Edit `ACCELERATOR` near the top of `scripts/build_notebook.py` and choose `cpu`, `t4`, `p100`, or `rtx6000`. The T4 setting is the default.

### Troubleshooting

- If Python 3.12 is missing, install it before `make setup`.
- If Kaggle reports unauthorized, replace `.kaggle/access_token` with a valid token.
- If local game creation fails, confirm Internet access for the first download; game sources are cached afterward.
- A zero score is expected from the starter random policy until `agent/my_agent.py` is improved.
