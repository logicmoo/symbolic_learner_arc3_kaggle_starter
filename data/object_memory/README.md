# Object-memory data directory

Canonical, on-disk, **global** persistent store for the symbolic vision
recognizer (`workbench/server/generative_vision/prolog/symbolic_arc.py` +
`object_memory.pl`). Shared across games/levels/sessions so an object seen in one
encounter can be recognized in another. Override the location with the
`OBJECT_MEMORY_DIR` environment variable. Prolog reads both sub-stores before
recognition.

## Two sub-stores

### `shape_dir/shapes.pl` - the colorless SHAPE VOCABULARY (just shapes, no identity)
Regenerated deterministically from the code and **consulted** (read) by Prolog.

- `shape(Key, Name, Turtle)` - each free polyomino (monomino..octomino) keyed by
  its **rotation-normalized full** form via the **Buttered Toast Algorithm**
  (flipped/rotated so the bottom-right corner/quadrant holds the most pixels; see
  `workbench/docs/design/BUTTERED_TOAST_NORMALIZATION.md`). `Name` is a letter
  name (orders 1-5) or a `box_HxW[_cut_...]` descriptor.
- `variant(VKey, Name, Kind, Base)` - the shape's other forms mapping back to it:
  the unrotated full, the **proportional** (un-pixelated by integer block factor),
  the **squared** / **aspect** shrinks, and the **45-degree** diagonal, in both
  unrotated and rotation-normalized orientations. This lets a rescaled / rotated /
  diagonally-placed object be recognized as the same shape. Every "sameness" is
  `filter(A) == filter(B)`: two shapes match under a form iff their form keys are
  equal.

### `identity_dir/identities.db.pl` - persistent OBJECT IDENTITIES
Journaled via `library(persistency)`. Identities carry color; shapes do not.

- `known_object(Key, Color, First, Last, Seen)` - a recognized object
  (rotation-normalized colorless shape key + color), position-invariant; `Seen`
  accumulates across encounters.
- `known_placement(Game, Iid, Gid, Points, Moves)` - a tracked instance's
  move-to-move `(x,y,shape)` trajectory within a game.

## Regeneration

The shape vocabulary is regenerated deterministically (`shapes.pl`), and the
identity DB is runtime state, so both are **git-ignored**; delete
`identity_dir/identities.db.pl` to reset identity memory.