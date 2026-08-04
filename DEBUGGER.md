[← Back to top-level README](README.md)

# ARC3 Debugger

The debugger opens real ARC3 games and levels, captures a rendered frame after each state change, records deterministic action branches, creates GitHub-browsable state nodes, and supports shared LLM-, Prolog-, and Python-backed symbolic analysis.

## Unified configuration and action-tree roots

```text
config/
├── README.md
└── llm_providers.json   # llm_providers + reusable prompt_text sections

action_trees/
└── <game>/
    └── level_<n>/
        ├── histories/
        ├── exports/
        ├── README.md
        ├── image.png
        ├── state.json
        └── ... state and action branches ...
```

Override these locations when needed:

```bash
ARC3_CONFIG_ROOT=/path/to/config
ARC3_LLM_CONFIG=/path/to/config/llm_providers.json
ARC3_TREE_ROOT=/path/to/action_trees
```

There is no separate `prompts/` directory. Each provider in the unified JSON selects an ordered list of named `prompt_text` sections.

## Runtime architecture

```text
Notebook, terminal, or browser UI
        ↓
Arc3Runner + multi-LLM extension
        ↓
arc_agi.Arcade environment
        ↓
state/history/action-tree storage
        ↓
LLM Markdown transcript cache + latest .pl artifacts
        ↓
SWI-Prolog and downstream symbolic providers
```

The debugger does not implement a separate game engine. The ARC3 toolkit environment remains authoritative.

## Start the terminal debugger

```bash
python scripts/interactive_runner.py ls20
```

On native Windows:

```bat
scripts\interactive_runner.bat ls20
```

The positional argument is the initial game ID. The default is `ls20`.

## Start the browser debugger

```bash
python scripts/run_webui.py --game ls20
```

Open:

```text
http://127.0.0.1:8765/
```

Each browser connection starts an isolated `scripts/interactive_runner.py` process. Saved action-tree files and transcripts remain after the browser tab closes.

### Browser dimensions

```bash
ARC3_WEB_COLS=320
ARC3_WEB_ROWS=100
python scripts/run_webui.py --game ls20
```

### Non-loopback binding

Binding outside localhost requires a token:

```bash
ARC3_WEB_TOKEN=choose-a-long-random-token \
python scripts/run_webui.py --host 0.0.0.0 --port 8765 --game ls20
```

Do not expose an unrestricted terminal, Prolog execution endpoint, API keys, or private files without authentication and HTTPS.

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

## LLM and Prolog modes

Select a symbolic-analysis mode first:

```text
g              LLM mode; repeated presses cycle configured providers
p              Prolog mode
```

Then press a number from 1 through 6.

### LLM mode

```text
1  choose/restore cached transcripts, or edit unified LLM config
2  demo combined analysis
3  deep combined analysis
4  extreme combined analysis
5  recompute turtle_from_diff.pl
6  recompute similarities.pl
```

Commands 2, 3, and 4 use one artifact pipeline at different image-detail, reasoning, and output-token levels. The selected provider determines which named `prompt_text` sections are assembled. For example, a provider can omit the `transitions` section while retaining object extraction, Turtle reconstruction, and rule analysis.

### Combined LLM pipeline

The normal `(g)` then `(2)` path:

1. Captures or reuses `image.png`.
2. Resolves the parent state.
3. Assembles the active provider's ordered `prompt_text` sections.
4. Sends one multimodal request through the selected provider/adapter.
5. Records the exact request, images, timing, token settings, provider metadata, and raw response in one Markdown transcript.
6. Parses strict JSON or performs deterministic local repair.
7. Uses at most one text-only repair call when the bundle remains incomplete.
8. Writes or refreshes `object_registry.pl`, `objects.pl`, differences, similarities, Turtle programs, and rules as the mutable latest view.
9. Finalizes the Markdown transcript with copies of those generated artifacts at its top.
10. Updates `llm_provider.json`.
11. Refreshes the current and parent node READMEs.

Existing nonempty artifacts may be reused unless regeneration is forced. A completed transcript is the immutable historical cache object; individual `.pl` files are the latest active view.

### Restore an earlier LLM run

Press `(g)` then `(1)`. The chooser lists all transcripts for the current state. Selecting a completed transcript:

1. extracts its embedded Prolog artifact sections;
2. rewrites the individual latest `.pl` files;
3. rewrites `llm_provider.json` with restored provenance;
4. marks that transcript active;
5. regenerates `README.md` so the embedded latest artifacts and active transcript link agree.

Failed or incomplete runs remain available as debug-only transcripts but cannot become the active artifact snapshot. Enter `E` in the same chooser to edit `config/llm_providers.json`.

### Prolog mode

```text
1  inspect Prolog description context
2  full state analysis to shared .pl artifacts
3  recompute differences.pl
4  recompute turtle_from_image.pl
5  recompute turtle_from_diff.pl
6  recompute similarities.pl
```

The shared contracts and provider interfaces are documented in [SOW_PHASE_ARCHITECTURE.md](SOW_PHASE_ARCHITECTURE.md) and [TODO.md](TODO.md).

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
        ├── llm_provider.json
        ├── llm_adapter_openai_responses_unsloth_..._L4_extreme_tokens_32000_....md
        ├── LEFT/
        │   ├── README.md
        │   ├── image.png
        │   ├── state.json
        │   ├── objects.pl
        │   ├── differences.pl
        │   ├── similarities.pl
        │   ├── turtle_from_image.pl
        │   ├── turtle_from_diff.pl
        │   ├── rules.pl
        │   └── llm_adapter_...md
        └── SELECT_x_12_y_31/
            └── ...
```

The directory path is the action path. Coordinate actions include their coordinates so distinct selections do not collide.

## Generated state artifacts

- `README.md` — navigation, image, metadata, active transcript, all transcript links, and collapsible latest artifact text.
- `image.png` — authoritative captured visual frame.
- `state.json` — game, level, action, parent, hash, and observation metadata.
- `llm_provider.json` — current latest provider/model/analysis provenance, including restored transcript information when applicable.
- `llm_adapter_<adapter>_<provider>_<model>_<level>_<profile>_tokens_<budget>_<timestamp>.md` — immutable comparison/cache record with restorable artifacts first and debugging interactions below.
- `object_registry.pl` — level-wide friendly identity authority.
- `objects.pl` — facts specific to one state.
- `differences.pl` — parent/current symbolic delta.
- `similarities.pl` — object correspondences and matching evidence.
- `turtle_from_image.pl` — Turtle reconstruction of the current state.
- `turtle_from_diff.pl` — Turtle transformation from parent to current state.
- `rules.pl` — candidate rules and evidence from the branch context.

The transcript's request prompt is rendered as Markdown rather than hidden inside a code fence. Raw provider responses are kept at the very bottom. Completed transcripts contain hidden machine-readable markers around each Prolog artifact so restoration does not depend on headings alone.

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

## Notebooks

```bash
jupyter lab
```

- `notebooks/arc3_debugger.ipynb` — guided debugger workflow.
- `notebooks/arc3_runner.ipynb` — lower-level scripting and API exploration.

Both use `Arc3Runner`, the same action tree, the same identity registry, and the same combined artifacts.

## Replay and level-transition safety

A `WIN` result is stored in the level that was actually won. The debugger does not assume a next level has loaded until the toolkit exposes a changed level identifier or a genuine post-win/reset state. This prevents winning frames from being written into the next level’s initial state or identity registry.

Replay uses the recorded action sequence and verifies deterministic branch reuse. Histories and exports are stored beneath the active level’s actual `histories/` and `exports/` paths, including Windows/UNC fallback directory names.

## Windows and UNC path handling

If a requested action-tree path is blocked by an unusable filesystem entry, the conflicting entry is preserved and a sibling path such as `level_1.dir` is used. The actual chosen path is returned to callers and used for subsequent histories, exports, and child branches.

## Editable LLM configuration

Providers and reusable prompt sections live together in `config/llm_providers.json`. Prompt values may be arrays of physical lines so Git diffs remain readable. Each provider's `prompt_text` array selects and orders the named blocks included in its request.

[← Back to top-level README](README.md)
