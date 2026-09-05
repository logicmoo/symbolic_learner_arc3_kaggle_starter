# Symbolic ARC Recognition — Identity, Recognition, Regeneration, Memory, Replay

[← Back to top-level README](../../../README.md) · Related:
[OBJECT_REGISTRY_CANONICAL](OBJECT_REGISTRY_CANONICAL.md) ·
[BUTTERED_TOAST_NORMALIZATION](BUTTERED_TOAST_NORMALIZATION.md) ·
[PHASE2_OBJECT_MEMORY_DEMONSTRATION](PHASE2_OBJECT_MEMORY_DEMONSTRATION.md)

This is the LLM‑free symbolic object‑recognition line that satisfies SOW Phase 2
(*Object Perception, Recognition, and Persistent Memory*). It runs perception in
Python and grouping/memory in SWI‑Prolog. Everything below is real filesystem /
backend behaviour — no mocks.

- Perception + shape model: `workbench/server/generative_vision/prolog/symbolic_arc.py`
- Persistence: `workbench/server/generative_vision/prolog/object_memory.pl`
- Canonical store (git‑ignored, regenerable): `data/object_memory/`
  - `shape_dir/shapes.pl` — colourless shape vocabulary (regenerated deterministically)
  - `identity_dir/<scope>/identities.db.pl` — persistent object identities + occurrences
- UI: Video Import → **Recognition** subview (per‑object chips + PartOf tree names) and the **Sprite Viewer**.

## Input breadth (grid, image, simple video)

`decode_grid()` reads a clean flat‑colour grid directly at its detected cell
pitch. A **general raster** image (photo / anti‑aliased sprite / gradient / JPEG
noise / video frame) is auto‑detected (pitch collapses to 1, palette explodes)
and made grid‑like: the palette is median‑cut quantized to flatten
anti‑aliasing/gradients/noise into flat regions and the image is downscaled to a
small grid. **Simple video** is handled frame‑by‑frame: `scene_split.py` cuts a
frame stream into scenes (`scene_cuts`) so identity/permanence is threaded within
a scene and never bled across a hard cut; `extract_sequence()` runs the recognizer
over an ordered frame list, threading object identity forward.
Bar per Exhibit A: *modest* degradation and *simple* video, not high‑fidelity
photographs.
Tests: `tests/test_symbolic_arc_input_breadth.py`, `tests/test_scene_split.py`.

## Object identity (colour‑ and scale‑normalized)

A **shape occurrence** is `x · y · fullsize · shapename · colour`. An **object**
is the identity those occurrences bind to. Identity = the shape's *name* after
un‑pixelating to its smallest integer scale (`_identity_name` →
`_proportional_cells` + rotation/reflection normalization → classic polyomino
name, else a box‑cut descriptor, else a compact `shape_HxW_<hash>` for
large/complex regions). Therefore **position, orientation, scale, reflection, and
colour are occurrence attributes**, and a moved / rotated / reflected / resized /
recoloured appearance stays the **same object** (`gid = gobj_<name>`, no colour).
`known_variation(key, colour, size, seen)` records the colours and sizes an
object has appeared as.
Tests: `tests/test_symbolic_arc_memory_scope.py`
(`test_recolor_is_the_same_object`, `test_resize_is_the_same_object`,
`test_identity_is_scale_and_colour_normalized_name`).

## Recognition (recognize vs commit) and duplicate prevention

`remember_objects(..., write=True)` (default, `run_memory`) recognizes each
object against the persistent store, **mints on first sight and accumulates
evidence (`seen`) on recognition** — never storing the same object twice.
`recognize_objects(...)` (`write=False`, `run_recognize`) is a **read‑only** pass:
it reports the stored identity and `seen`/`new` and annotates the frame without
mutating the store. The Recognition page uses recognize‑only per card for display
and commits once per sequence; a registry mode selector and separate
**prolog / LLM / all‑impls** reduce buttons expose both.
Recognized‑vs‑new is surfaced as `memNew` / `memSeen` and `(memory …)` /
`(shape …)` / `(occurrence …)` facts.
Tests: `test_recognize_only_*`, `test_commit_accumulates_across_encounters`,
`test_recognition_demo_*`.

## Regeneration (stored form → shape)

Each shape is stored as a normalized turtle program (`_poly_turtle`) — a `move`
then one scaled `rectangle` per cell in the 0..1000 box. Replaying it regenerates
the exact normalized cells (faithful/exact on clean discrete grids). The Sprite
Viewer renders these programs; `registry_snapshot(include_turtles=True)` returns
them.
Test: `test_symbolic_arc_regeneration_replay.py::test_stored_form_regenerates_its_exact_shape`.

## Persistent memory (evidence, provenance, placement)

`object_memory.pl` uses `library(persistency)`:
`known_object(key, first, last, seen)` (colour‑free identity + evidence count),
`known_variation(key, colour, size, seen)` (occurrence attributes), and
`known_placement(game, iid, gid, points, moves)` (per‑instance move‑to‑move
trajectory). Identity is scoped per **game** by default (shared across a game's
levels via `_game_of`), or one `_all_games_` scope with `cross_game=True` /
`$OBJECT_MEMORY_ACROSS_GAMES`. Non‑mutating recognition leaves the DB
byte‑for‑byte unchanged.
Tests: `test_symbolic_arc_memory_scope.py` (per‑level / per‑game / cross‑game).

## Replay / determinism

The same input yields the same committed identity handles and the same canonical
form (metta) across runs; identity rests on the normalized form, not a
query‑time matcher, so it is independent of colour and position.
Tests: `test_replay_same_input_same_identity_and_form`,
`test_replay_identity_is_colour_and_position_free`.

## Demonstration workflow (Exhibit A)

Input image / game state → object extraction (`extract_frame`) → representation
(shape/colour/size/position/orientation) → matching & correspondence
(`extract_sequence`) → before/after comparison (movement / add / remove /
structural change) → persistent storage (`remember_objects`) → **later
recognition as the same object** on a new encounter under move / reflect /
recolour / resize. Exercised live in the Recognition subview and by
`test_recognition_demo_recognizes_same_object_later`.
