[← Back to top-level README](README.md)

# ARC3 Debugger

The debugger opens real ARC3 games and levels, captures a rendered frame after each state change, records deterministic action branches, creates GitHub-browsable state nodes, and supports shared GPT-, Prolog-, and Python-backed symbolic analysis.

## Shared prompt and action-tree roots

```text
prompts/
└── gpt_prompts.json

action_trees/
└── <game>/
    └── level_<n>/
        ├── histories/
        ├── exports/
        ├── README.md
        ├── image.png
        ├── state.json
        └── ... action branches ...
```

Override these roots when needed:

```bash
ARC3_PROMPTS_ROOT=/path/to/prompts
ARC3_TREE_ROOT=/path/to/action_trees
```

## Runtime architecture

```text
Notebook, terminal, or browser UI
        ↓
Arc3Runner
        ↓
arc_agi.Arcade environment
        ↓
state/history/action-tree storage
        ↓
GPT artifacts or SWI-Prolog providers
```

The debugger does not implement a separate game engine. The ARC3 toolkit environment is authoritative.

## Start the terminal debugger

From the repository root:

```bash
python scripts/interactive_runner.py ls20
```

The first positional argument is the initial game ID. The default is `ls20`.

## Controls

### Game actions

```text
Up arrow       ACTION1
Down arrow     ACTION2
Left arrow     ACTION3
Right arrow    ACTION4
Space          ACTION5
c              ACTION6 coordinate action
Ctrl-Z         ACTION7 / undo
```

### Game and level navigation

```text
Shift+Left     previous game
Shift+Right    next game
Shift+Up       previous level
Shift+Down     next level
```

### Recorded-history navigation

```text
Ctrl+Left      previous recorded step
Ctrl+Right     next recorded step
Ctrl+Up        first recorded step
Ctrl+Down      latest recorded step
```

### Reset and restart

```text
r              reset current level
R              restart current game from level 1
```

### Information

```text
L              list games and levels
l              show current game and level
a              list legal actions
h              show history
s              show scorecard
?              reprint controls
```

### Replay, execution, and files

```text
Enter          redraw current frame
v              replay recorded actions
w              save history
e              export current state
x              pause or resume
.              run one queued debugger step
q              quit
```

## GPT and Prolog modes

Select a symbolic-analysis mode first:

```text
g              GPT mode
p              Prolog mode
```

Then press a number from 1 through 6.

### GPT mode

```text
1  inspect or edit GPT prompts
2  demo combined analysis
3  deep combined analysis
4  extreme combined analysis
5  recompute turtle_from_diff.pl
6  recompute similarities.pl
```

Commands 2, 3, and 4 use the same combined artifact contract at different image-detail, reasoning, and output-token levels.

### Combined GPT pipeline

The normal `(g)` then `(2)` path:

1. Captures or reuses `image.png`.
2. Resolves the parent state.
3. Generates or reuses `objects.pl` for current and parent states.
4. Generates or reuses `differences.pl`.
5. Generates or reuses `similarities.pl`.
6. Generates or reuses `turtle_from_image.pl`.
7. Generates or reuses `turtle_from_diff.pl` when a parent exists.
8. Generates or reuses `rules.pl`.
9. Updates the level-wide `object_registry.pl`.
10. Refreshes the current and parent node READMEs.

Existing nonempty artifacts are reused unless regeneration is forced.

### Prolog mode

The Prolog menu uses the same state tree and artifact contracts:

```text
1  inspect Prolog description context
2  full state analysis to shared .pl artifacts
3  recompute differences.pl
4  recompute turtle_from_image.pl
5  recompute turtle_from_diff.pl
6  recompute similarities.pl
```

The deterministic Prolog implementations are being connected incrementally. The shared contracts and provider interfaces are documented in [SOW_PHASE_ARCHITECTURE.md](SOW_PHASE_ARCHITECTURE.md) and [TODO.md](TODO.md).

## Friendly persistent object identities

Opaque numbered identifiers such as `obj_1` or `shape_2` are rejected. The first analyzed state introduces friendly identities, for example:

```prolog
object_identity(blue_player, player, 'blue player').
object_identity(red_goal, goal, 'red goal').
object_identity(left_wall, wall, 'left boundary wall').
```

The level-wide generated `object_registry.pl` is authoritative:

- names are reused across the level and all action branches;
- state-local `objects.pl` files do not repeat the identity database;
- genuinely new objects may add new friendly declarations;
- older caches are normalized against the registry;
- embeddings or similarity may propose a match but do not commit identity.

## Action-tree layout

The level directory is the root state. Every action directory is the resulting state:

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
        └── SELECT_x_12_y_31/
            └── ...
```

The directory path is the action path. Coordinate actions include their coordinates so distinct selections do not collide.

## Generated state artifacts

- `README.md` — navigation, image, metadata, child links, and collapsible artifact text.
- `image.png` — authoritative captured visual frame.
- `state.json` — game, level, action, parent, hash, and observation metadata.
- `object_registry.pl` — level-wide friendly identity authority.
- `objects.pl` — facts specific to one state.
- `differences.pl` — parent/current symbolic delta.
- `similarities.pl` — object correspondences and matching evidence.
- `turtle_from_image.pl` — Turtle reconstruction of the current state.
- `turtle_from_diff.pl` — Turtle transformation from parent to current state.
- `rules.pl` — candidate rules and evidence from the branch context.

Creating a child action branch refreshes both the child README and its parent README so GitHub navigation stays current.

## Turtle DSL

The canonical motion-oriented vocabulary is:

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

Generated programs should trace geometry with `fwd/1` and `rot/1`, using `set_pos/2` only to establish or restart a stroke. Filled regions are represented with scan-line strokes rather than opaque rectangle commands.

Run Turtle tests:

```bash
swipl -q -s prolog/test_turtle_dsl.pl -g run_tests,halt
```

## SWI-Prolog-controlled demonstration

```bash
python scripts/prolog_controlled_runner.py
```

This calls `python/swipl_bridge.py`, loads `prolog/arc3_agent.pl`, asks Prolog for an action, and applies it through `Arc3Runner`.

## Browser terminal

The browser interface launches the same script used by the terminal debugger:

```text
xterm.js
    ⇅ WebSocket
FastAPI PTY server
    ⇅
scripts/interactive_runner.py
    ↓
Arc3Runner
```

Start it:

```bash
python run_webui.py --game ls20
```

Open:

```text
http://127.0.0.1:8765/
```

Each browser connection gets an isolated debugger process. Saved action-tree files remain after the tab closes.

### Terminal dimensions

Defaults can be changed with:

```bash
ARC3_WEB_COLS=320
ARC3_WEB_ROWS=100
```

### Non-loopback binding

Binding outside localhost requires a token:

```bash
ARC3_WEB_TOKEN=choose-a-long-random-token \
python run_webui.py --host 0.0.0.0 --port 8765 --game ls20
```

Do not expose an unrestricted terminal, Prolog execution endpoint, API keys, or private files without authentication and HTTPS.

## Notebooks

Launch:

```bash
jupyter lab
```

- `notebooks/arc3_debugger.ipynb` — guided debugger workflow.
- `notebooks/arc3_runner.ipynb` — lower-level scripting and API exploration.

Both use `Arc3Runner`, the same action tree, the same identity registry, and the same combined GPT artifacts.

## Replay and level-transition safety

A `WIN` result is stored in the level that was actually won. The debugger does not assume a next level has loaded until the toolkit exposes a changed level identifier or a genuine post-win/reset state. This prevents winning frames from being written into the next level’s initial state or identity registry.

Replay uses the recorded action sequence and verifies deterministic branch reuse. Histories and exports are stored beneath the active level’s actual `histories/` and `exports/` paths, including Windows/UNC fallback directory names.

## Windows and UNC path handling

If a requested action-tree path is blocked by an unusable filesystem entry, the conflicting entry is preserved and a sibling path such as `level_1.dir` is used. The actual chosen path is returned to callers and used for subsequent histories, exports, and child branches.

## Prompt files

Editable GPT prompts live in `prompts/gpt_prompts.json`. Prompts may be stored as arrays of physical lines so Git diffs remain readable; the loader joins and normalizes them at runtime.

[← Back to top-level README](README.md)
