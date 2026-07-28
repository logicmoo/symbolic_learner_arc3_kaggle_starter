[← Back to top-level README](README.md)

# SoW Phase Architecture

## Governing principle

This architecture extends the working repository. It does not replace the delivered ARC3 debugger, create phase directories, duplicate native Prolog logic in Python, or alter the protected Kaggle submission surface.

## Phase 1 — delivered and preserved

Existing code fulfills Phase 1:

- `python/arc3_runner.py` — game lifecycle, actions, replay, reset, restart, state/history handling, exports, and analysis commands.
- `python/action_tree.py` — deterministic action-tree recording, images, JSON metadata, GitHub-friendly state READMEs, and level-wide friendly identities.
- `python/gpt_bridge.py` — one combined GPT request and cached Prolog artifacts.
- `python/swipl_bridge.py` plus `prolog/arc3_agent.pl` — SWI-Prolog control seam.
- `prolog/turtle_dsl.pl` — authoritative Turtle execution semantics.
- `scripts/interactive_runner.py` — terminal debugger.
- `scripts/run_webui.py` — browser-UI launcher with repository-root import bootstrap.
- `scripts/prolog_controlled_runner.py` — executable Prolog-controlled demonstration.
- `webui/server.py` — browser terminal exposing the same interactive runner rather than a second debugger.

No Phase 1 implementation is duplicated. Runnable launchers formerly under `examples/` or the repository root now live in `scripts/`.

## Phase 2 — perception, representation, correspondence, and memory

The `python/object_memory/` package uses records, facades, adapters, and provider contracts around existing or future implementations:

- `CandidateObject` — stable facade whose `part(name)` delegates to a provider.
- `GenerativeForm` — interface; `CellLogoForm` maps the SoW name onto existing Turtle programs rather than creating another DSL.
- `ResidualCandidate` — unexplained candidate structure.
- `ResidualGate` — deterministic admission decision.
- `CommittedAtom` — backend-neutral committed record.
- `SingleWriter` — only Python reference mutation path; authoritative Prolog commitments use `prolog/single_writer.pl`.
- `GridAdapter` — thin wrapper around an existing extractor, not a replacement object engine.

Persistent friendly identity remains owned by generated level-wide `object_registry.pl`. The new contracts do not introduce a second identity registry.

## Phase 3 — present and connected, not declared complete

Phase 3 is not deferred to a later architecture rewrite. Its contracts are present and connected through provider-driven pipelines:

- `python/object_memory/learning.py` connects `TransitionAnalyzer`, `TransformationLearner`, `RuleInducer`, `RuleRanker`, `RuleStore`, `RuleExecutor`, `PredictionLedger`, `OutcomeChannel`, and `PredictionEvaluator`.
- `python/object_memory/integration.py` provides validated `GameObjectLearnerPayload` and `GameObjectLearnerResult` records plus `PipelineGameObjectLearnerPlugin`.
- `prolog/game_object_learner_api.pl` connects transition analysis, transformation learning, rule induction/ranking/storage/application, prediction recording, and later grading.
- Python and Prolog tests exercise the connected learning and prediction path.

These are stable contracts and orchestration seams, not a claim that final rule quality, task coverage, or benchmark acceptance has been achieved. Real object correspondences, learned transformations, environment predictions, and evidence grading will be connected incrementally.

Generated action-tree `rules.pl` files remain valid GPT-backed artifacts. Native Prolog rule learning extends that shape instead of creating an unrelated format.

## Three execution modes

One contract is shared by all modes:

1. **PROLOG** — `PrologProvider` delegates to SWI-Prolog predicates and existing `.pl` files. Prolog remains primary for symbolic reasoning where appropriate.
2. **GPT** — `GptArtifactProvider` reads generated or cached `objects.pl`, `similarities.pl`, `differences.pl`, `rules.pl`, and Turtle artifacts. It does not masquerade as native Python reasoning.
3. **PYTHON** — `PythonProvider` runs deterministic native resolvers where useful.

Every provider returns `NormalizedResult`; there are not three object models. Phase 3 analyzers and learners accept replaceable callbacks/providers so the same orchestration can be backed by any mode.

## Protected Kaggle surface

These paths and their behavior remain protected:

- `notebooks/submission.ipynb`
- `notebooks/kernel-metadata.json`
- `scripts/build_notebook.py`
- `scripts/play_local.py`
- `agent/my_agent.py`
- existing Kaggle Makefile commands and packaging paths

See [KAGGLE.md](KAGGLE.md) for the operational workflow.

## Runnable scripts

All runnable Python launchers live in `scripts/`:

- `scripts/interactive_runner.py`
- `scripts/run_webui.py`
- `scripts/prolog_controlled_runner.py`
- `scripts/play_local.py`
- `scripts/build_notebook.py`
- `scripts/slim_framework.py`

`webui/server.py`, [DEBUGGER.md](DEBUGGER.md), [KAGGLE.md](KAGGLE.md), tests, and the root README reference these canonical paths. No duplicate implementation remains under `examples/` or at the repository root.

## Components intentionally not duplicated

- another ARC3 runner (`Arc3Runner` exists);
- another action-tree store (`ActionTreeStore` exists);
- another GPT analyzer (`GptArcAnalyzer` exists);
- another SWI subprocess bridge (`SWIPrologBridge` exists);
- another Turtle interpreter (`turtle_dsl.pl` exists);
- another friendly identity database (`object_registry.pl` exists);
- parallel runners in `examples/` and `scripts/`;
- phase-specific directory trees;
- separate Python rule storage apart from `RuleStore`;
- separate Prolog rule facts apart from `object_memory_contract:transition_rule/2`.

## Gradual integration plan

1. Freeze normalized observation, object, atom, transition, and learner-payload schemas.
2. Use `CandidateObject` and providers as facades over current action-tree facts.
3. Connect Prolog debugger commands to normalized Prolog predicates.
4. Add deterministic grid extraction behind `GridAdapter` only where existing extraction does not satisfy the contract.
5. Route accepted symbolic changes through `SingleWriter`.
6. Feed real object correspondences into the connected Phase 3 transition and transformation pipeline.
7. Record predictions before actions and grade them from independent ARC3 responses.
8. Add raster adapters only after grid replay and identity tests pass.

See [TODO.md](TODO.md) for detailed status and remaining work, and [FILE_TREE.md](FILE_TREE.md) for the clickable repository layout.

[← Back to top-level README](README.md)
