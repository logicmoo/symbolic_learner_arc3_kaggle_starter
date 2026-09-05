# The canonical object registry

**Decision:** `data/object_memory/` is the **canonical object registry** for the
symbolic recognizer line (`workbench/server/generative_vision/prolog/symbolic_arc.py`
+ `object_memory.pl`). It is the single source of truth for the shapes the system
knows and the objects it has recognized.

## Why designate rather than merge

There are two independent memory lines in this repo:

- **Symbolic recognizer line (this, canonical):** deterministic, LLM-free. Produces
  the colorless shape vocabulary and per-game object identities and stores them in
  `data/object_memory/`.
- **Action-tree / LLM line (`python/object_memory/`):** a separate framework of
  JSON semantic records, action-tree catalogs, correspondence authority, and the
  per-game-level `object_registry.pl` it generates. It serves the LLM/action-tree
  workflow and has its own large test suite.

These are different paradigms serving different pipelines. Forcing a merge would
risk the action-tree framework's behaviour for no current consumer. So the symbolic
line's store is **designated canonical for object recognition**, and the two lines
are kept as distinct, documented boundaries rather than fused. A bridge/export
between them should be added only when a concrete consumer needs it (YAGNI).

## Single source of truth

Every process resolves the same location via `symbolic_arc.memory_dir()`
(`<repo>/data/object_memory`, override with `$OBJECT_MEMORY_DIR`):

- the recognizer (`extract_sequence` / `remember_objects`) **writes** here,
- the reduce pipeline (`video_import_pipeline`) writes here,
- the registry API (`GET /workbench/registry/snapshot`) and the **Sprite Viewer**
  read here.

No other store is authoritative for recognizer shapes/identities.

## Layout (see `data/object_memory/README.md`)

- `shape_dir/shapes.pl` — colorless SHAPE vocabulary (`shape/3` + `variant/4`),
  regenerated deterministically, consulted before recognition.
- `identity_dir/<scope>/identities.db.pl` — persistent IDENTITIES per scope, where
  a scope is a game (identity shared across its levels) or `_all_games_`
  (`OBJECT_MEMORY_ACROSS_GAMES`). `known_object` (shape+color) and
  `known_placement` (per-game trajectory).

## Inspect / reset

- **Inspect:** the Sprite Viewer page, or `GET /workbench/registry/snapshot`.
- **Reset:** delete `identity_dir/<scope>/identities.db.pl` (identities are runtime
  state); the shape vocabulary regenerates deterministically.
