# SoW Phase Architecture

## Governing principle

This design extends the working repository. It does not replace the delivered
ARC3 debugger, create phase directories, duplicate Prolog logic in Python, or
alter the protected Kaggle submission surface.

## Phase 1 — already delivered and preserved

Existing code fulfills Phase 1:

- `python/arc3_runner.py`: game lifecycle, actions, replay, reset, restart,
  state/history handling, and combined analysis commands.
- `python/action_tree.py`: deterministic action-tree recording, state images,
  JSON metadata, GitHub-friendly node READMEs, and level-wide friendly identity
  registry.
- `python/gpt_bridge.py`: one combined GPT request and cached Prolog artifacts.
- `python/swipl_bridge.py` plus `prolog/arc3_agent.pl`: SWI-Prolog control seam.
- `prolog/turtle_dsl.pl`: authoritative Turtle execution semantics.
- `examples/interactive_runner.py`: terminal debugger.
- `webui/server.py`: browser terminal exposing that same runner, not a second UI
  engine.

No Phase 1 code was renamed or replaced.

## Phase 2 — perception, representation, correspondence, and memory

The new `python/object_memory/` package is intentionally lightweight. Its types
are records, facades, adapters, and provider contracts around existing or future
implementations:

- `CandidateObject`: stable facade whose `part(name)` delegates to a provider.
- `GenerativeForm`: interface; `CellLogoForm` maps the name onto existing Turtle
  programs rather than creating another DSL.
- `ResidualCandidate`: record for unexplained candidate structure.
- `ResidualGate`: deterministic admission decision.
- `CommittedAtom`: backend-neutral committed-record shape.
- `SingleWriter`: only Python reference mutation path; authoritative Prolog
  commitments use `prolog/single_writer.pl`.
- `GridAdapter`: thin wrapper around an existing extractor, not a replacement
  object extractor.

Persistent friendly identity remains owned by the existing level-wide
`object_registry.pl`. The new contracts do not introduce another identity
registry.

## Phase 3 — transformations, rules, and prediction

- `TransitionRule`: normalized rule record.
- `PredictionRecord`: prior prediction plus later outcome fields.
- `PredictionLedger`: enforces that an outcome occurs after the prediction.
- `GameObjectLearnerPlugin`: stable handoff boundary for the game-learning side.

Rule facts already generated in action-tree `rules.pl` remain valid GPT-backed
artifacts. Native Prolog rule learning and application should extend those
contracts rather than create unrelated formats.

## Three execution modes

One contract is shared by all modes:

1. **PROLOG** — `PrologProvider` delegates to SWI-Prolog predicates and existing
   `.pl` files. Prolog remains primary for symbolic reasoning where appropriate.
2. **GPT** — `GptArtifactProvider` reads the existing generated or cached
   `objects.pl`, `similarities.pl`, `differences.pl`, `rules.pl`, and Turtle
   artifacts. It does not masquerade as native Python reasoning.
3. **PYTHON** — `PythonProvider` runs deterministic native resolvers when useful.

Every provider returns `NormalizedResult`; there are not three object models.

## Protected Kaggle surface

These paths and their behavior are protected and were not modified:

- `notebooks/submission.ipynb`
- `scripts/build_notebook.py`
- `scripts/play_local.py`
- `agent/my_agent.py`
- existing Kaggle Makefile commands and paths

## Examples and scripts

No runner was moved in this change. `webui/server.py` currently launches
`examples/interactive_runner.py`, and the existing README documents that path.
Moving it without a coordinated migration would break Phase 1. The gradual plan
is:

1. verify all references;
2. move one executable implementation to `scripts/`;
3. update web UI, README, notebooks, tests, Makefiles, and CI;
4. retain a thin forwarding launcher only when a verified compatibility need
   remains;
5. remove stale `examples/` commands.

## Components intentionally not added

The following were not added because existing code already fulfills the role:

- another ARC3 runner (`Arc3Runner` exists);
- another action-tree store (`ActionTreeStore` exists);
- another GPT analyzer (`GptArcAnalyzer` exists);
- another SWI subprocess bridge (`SWIPrologBridge` exists);
- another Turtle interpreter (`turtle_dsl.pl` exists);
- another friendly identity database (`object_registry.pl` exists);
- duplicate runners under both `examples/` and `scripts/`;
- phase-specific directory trees.

## Gradual integration plan

1. Use `CandidateObject` and providers as facades over current action-tree facts.
2. Connect Prolog-mode debugger commands to the normalized Prolog predicates.
3. Add deterministic grid extraction behind `GridAdapter` only where existing
   extraction code does not already satisfy the contract.
4. Route accepted symbolic changes through `SingleWriter`.
5. Add transition learning and rule application against the existing `rules.pl`
   shape.
6. Record predictions before executing or observing the tested transition.
7. Add raster adapters only after the grid path passes deterministic replay and
   identity tests.

See [FILE_TREE.md](FILE_TREE.md) for an annotated description of every relevant
file.
