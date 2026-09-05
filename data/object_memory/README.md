# Object-memory data directory

Canonical, on-disk, **global** persistent store for the symbolic vision
recognizer (`workbench/server/generative_vision/prolog/symbolic_arc.py` +
`object_memory.pl`). It is shared across games/levels/sessions so an object seen
in one encounter can be recognized in another. Override the location with the
`OBJECT_MEMORY_DIR` environment variable.

Prolog `db_attach`es the store here **before every operation** (it reads the data
first, then journals updates via `library(persistency)`).

## Contents (`object_memory.db.pl`)

Two kinds of records live here, kept strictly separate:

**Shape vocabulary — just shapes, no identity:**
- `known_shape(Key, Name, Turtle)` — the free polyominoes (monomino..octomino) as
  full-sized named turtle programs. The D4-canonical key already collapses all 8
  flips/rotations onto one entry.
- `known_variant(VKey, Name, Kind, Base)` — each -imino's shrink and diagonal
  forms mapping back to its name: `Kind` is `squared` (rectangle→1x1),
  `aspect` (longer=shorter+1), or `diag45` (45-degree lattice form). These let a
  rescaled or diagonally-placed object be recognized as the same shape.

**Object identities — minted only from real encounters:**
- `known_object(Key, Color, First, Last, Seen)` — a recognized object (shape+color,
  position-invariant); `Seen` accumulates across encounters.
- `known_placement(Game, Iid, Gid, Points, Moves)` — a tracked instance's
  move-to-move `(x,y,shape)` trajectory within a game.

## Regeneration

The shape vocabulary is generated deterministically by the code and re-seeded on
every run (idempotent). The DB itself is runtime state (it also accumulates
game-specific identities), so it is **git-ignored**; delete it to reset memory.
