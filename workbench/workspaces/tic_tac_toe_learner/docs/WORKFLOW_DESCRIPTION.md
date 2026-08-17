# Observe Board and Choose a Move

[← Back to repository README](../../../../README.md)

## Purpose

Observe one supplied tic-tac-toe board and pause for a person to choose a legal empty cell. Return both the preserved board observation and the selected move.

## Inputs and outputs

The workflow receives `board`, represented as an array. It returns `observedBoard` and the human-selected `move`.

## Workflow

1. Copy the supplied board into `observed_board` so the exact position used for the decision is retained.
2. After the observation exists, pause for a human move decision.
3. Ask the human for an empty-cell name such as `center`, `top_left`, or `bottom_right`.
4. Return the preserved observed board together with the selected move.

## Acceptance requirements

The move decision must depend on the preserved board observation. Do not alter the board, automatically choose a move, or accept a cell that the displayed board shows as occupied. Keep the board and move linked in the run evidence so the decision can be reviewed later.
