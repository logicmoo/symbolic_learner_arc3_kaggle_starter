[Back to repository README](../../../../README.md)

# ARC3 Random Player Workspace

This workspace runs a real outer learning loop against the ARC service. It
fetches the live game catalog, selects a game, captures image evidence, chooses
legal actions, assesses each transition, updates durable action-outcome memory,
and rotates games after a configurable budget (ten minutes by default).

Start continuous play from the repository root:

```powershell
.\.venv\Scripts\python.exe scripts\play_random_arc3.py
```

Use bounded arguments for a smoke run:

```powershell
.\.venv\Scripts\python.exe scripts\play_random_arc3.py --seconds-per-game 30 --max-games 1 --max-steps-per-game 5 --seed 7
```

Generated records live under `runtime/`: catalog and action-tree states,
action events, goal-run summaries and ARC histories, and the reusable
`contexts/action_learning_memory.json`. Runtime files are generated evidence,
not design mocks.

The design catalog deliberately separates abstract Operations from concrete
Python and prompt-backed alternatives. Python is preferred for the first
working outer loop. The prompt variants for selection, action proposal, and
transition critique establish the binding points for the later vision phase.
Richer image understanding should extend those variants rather than changing
the scheduler, persistence model, or domain-neutral observe/act/assess/remember
shape.

In Workbench terms, each Operation is also a durable delayed Codex/agent task
specification. It can be inspected and configured before execution; its input
contract, output contract, selected implementation, status, and produced
evidence remain explicit after execution. A `python.callable` child is a
deterministic implementation of that task, not a replacement for the abstract
Operation contract. Implementations may progress from Codex/agent or LLM
execution through smaller task-specialized models to ILP/program synthesis.
Those synthesis systems can learn from the specification and accumulated
evidence, write implementation code, and promote that result into a
deterministic callable; non-model execution is therefore not limited to code
written manually.

ARC discovery fans out into independent consumers. The chooser may consume the
original `$games` candidate list directly, so selection does not require image
downloads or Gallery rendering. Separately, disabled-by-default preview and
`gallery.curate_resource` probe steps can materialize a typed Gallery Resource
for human or AI inspection. They behave like test points on a circuit board:
useful when observing the flow, non-blocking when unused. Their `probe`
configuration remains overrideable; a specialized workflow may set
`required true` (and normally `blocking true`) when review must become a gate.
