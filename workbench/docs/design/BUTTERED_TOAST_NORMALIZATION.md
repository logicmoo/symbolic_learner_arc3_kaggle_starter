# The Buttered Toast Algorithm (bottom-right shape normalization)

## What it is

A deterministic way to pick a **canonical orientation** for a shape so that the
same shape always keys the same way regardless of how it was rotated or flipped
when observed.

The name is the mnemonic: **buttered toast always lands butter-side down.** We
rotate/flip a shape until its "heavy" side falls to the **bottom-right** — the
butter settles into the bottom-right corner. Two shapes that are rotations or
reflections of each other therefore normalize to the exact same orientation, so
they share one key ("the same shape").

## Where it lives

- `workbench/server/generative_vision/prolog/symbolic_arc.py`
  - `_canon_br(offs)` — the algorithm.
  - `_shape_sig(cells, hex)` — an object's identity key uses the buttered-toast
    (rotation-normalized) shape.
  - `_shape_forms(offs)` — produces each shape's *rotation-normalized* forms
    (`full_rn`, `squared_rn`, `aspect_rn`) via this rule, alongside the unrotated
    forms.
  - The `shape_dir/shapes.pl` vocabulary is keyed by the buttered-toast full form.

It shares the same D4 equivalence classes as the older lexicographic-smallest
`_canon_key`; it just chooses a *bottom-right* representative instead of the
lexicographically smallest one.

## The algorithm

Enumerate the **8 D4 orientations** of the shape (identity, rot90, rot180,
rot270, and the four reflections). Normalize each to the top-left origin, then
score it. Keep the highest-scoring orientation. If no orientation beats the one
you already have, the shape is **already normalized**.

The score is compared **lexicographically, highest priority first** — each rule
is only a tie-breaker for the previous one:

1. **Corner touch** — the bottom-right corner cell `(w-1, h-1)` is filled.
   *Actually touching the bottom-right wall beats any mere pixel count.*
2. **Bottom-right quadrant** — the most filled cells in the bottom-right quarter
   (`2x >= w and 2y >= h`).
3. **Bottom half** — if it can't settle bottom-right, settle **bottom**: the most
   filled cells in the bottom half (`2y >= h`).
4. **Mass** — the greatest total `sum(x + y)` (overall pull toward bottom-right).
5. **Lexicographic** — the largest sorted cell tuple, purely to make ties
   deterministic.

```
score(orientation) = ( corner_filled,        # 1 / 0   -- touches BR corner
                       br_quadrant_pixels,    # count   -- most in BR quarter
                       bottom_half_pixels,    # count   -- else most in bottom
                       sum(x + y),            # mass    -- pull to BR
                       sorted_cells )         # tie-break
pick argmax over the 8 D4 orientations
```

## Properties

- **Orientation-invariant:** every rotation/reflection of a shape yields the same
  buttered-toast result, so they converge to one key.
- **Deterministic:** the full lexicographic score has no unresolved ties.
- **Symmetry-aware:** a symmetric shape simply reports "already normalized"
  because multiple orientations share the top score and the tie-breaks settle it.

## Examples

- **L-tetromino** — normalizes so the long arm sits on the right and the foot in
  the bottom-right; all 8 observed orientations collapse to this one.
- **T-tetromino** — the bar sits along the bottom (bottom-half rule), stem up.
- **Domino** — a horizontal and a vertical domino are the same free shape; both
  normalize to one representative (the tie-breaks decide which).

## Why bottom-right (and not top-left)

Top-left is where the bounding box origin already is, so "settle to the origin"
carries no information. Pushing mass to the *opposite* corner is what actually
selects an orientation, and the bottom-right corner + quadrant + bottom-half
cascade gives a stable, human-describable rule: *let the butter fall.*
