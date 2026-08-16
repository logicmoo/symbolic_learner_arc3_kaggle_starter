[← Back to repository README](../../../../README.md)

# ARC3 Random Player Workflow — English Specification

## Purpose

Run ARC3 games as a bounded learning loop. Select only real games returned by the ARC server, avoid replaying games already recorded as played, observe every move, learn from its visible effect, and retain enough evidence to reproduce the run.

## Inputs and limits

The workflow receives a workspace root, random seed, selection mode, move limit, seconds per game (60 by default), and an optional maximum number of games. Every loop must have an explicit safety bound. No step may invent a game, action, operation, implementation, input, or output that is absent from the supplied catalogs.

## Workflow

1. Create an empty `played_games` list.
2. Ask the ARC server for the live game catalog.
3. Remove every game already present in `played_games`. The result is `unplayed_games`.
4. Build a viewable gallery from those unplayed games.
5. Select one game from `unplayed_games` using the requested selection mode.
6. Add the selected game to `played_games`.
7. Load that game's MeTTa data, legal controls, initial state, and initial screenshot.
8. Build a gallery for the selected game and initialize its runtime session.
9. Enter the per-game loop. Continue while elapsed game time is less than `seconds_per_game`, subject to the move limit.
10. Choose one legal action using retained learning memory and execute it.
11. Capture the resulting observation and compare it with the observation from before the move.
12. If the visible frame did not change, classify the move as ineffective, remember that evidence, exclude that action from the next choice, and return to action selection. This retry loop uses shared operation `control.while`, returns to `pick_random_move_and_execute`, and is bounded to 32 retries.
13. If the frame changed, clear the temporary ineffective-action exclusions and retain the good, bad, or neutral assessment in learning memory.
14. Continue the game until the time or move bound is reached, the game ends, or the user requests rotation.
15. Filter the live catalog again using the updated `played_games` list and select another unplayed game when one exists.
16. The outer loop uses shared operation `control.while`: continue while `unplayed_games` is not empty, bounded to 100 games.
17. For each selected game, the inner time loop also uses shared operation `control.while`: continue while `elapsed_game_seconds` is less than `seconds_per_game`, bounded to 1,000 moves.
18. Return the played-games list, retained memory, observations, assessments, galleries, and automatic session summaries with their provenance.

## Required control structure

The control graph contains three explicit shared-library loops:

- `control.while(unplayed_games not_empty)` around game selection and play.
- `control.while(elapsed_game_seconds less_than seconds_per_game)` around moves within a game.
- `control.while(assessment.frame_changed equals false)` from transition assessment back to move selection, excluding the ineffective action.

Dependencies are a directed graph, not merely the textual order of steps. Generated output must preserve every declared `dependsOn`, input binding, output binding, loop target, and safety bound.

## Acceptance rules

- Use only operation IDs found in the supplied effective operation catalog.
- Use `control.while` and `control.for_each` from `shared_library_system` for reusable loop semantics.
- Keep semantic operations separate from their concrete implementations.
- Every `$value` input must be produced by a reachable prior step or declared as a workflow input.
- Every dependency ID and loop target must name an existing step.
- Preserve stable step IDs when updating an existing workflow.
- Return only the requested serialization format.

## Implementation is resolved afterward

This specification defines the semantic workflow, not a permanently fixed implementation for every operation. Once the complete workflow exists, preflight or runtime resolves each semantic operation to an inherited or workspace-local concrete child. A child may call Python, Prolog, an LLM prompt/model, a human-input adapter, or another supported runtime. When no suitable child exists, a later implementation-producing model may create and validate one using the whole workflow as context. The resolved operation mapping is frozen into each run for reproducibility; it does not replace the semantic workflow.
