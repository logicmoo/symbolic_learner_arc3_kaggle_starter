[← Back to top-level README](README.md)

# Repository File Tree and Responsibilities

This is the clickable source map for the maintained repository. Every listed path links directly to the file and includes its responsibility.

## Root documentation

- [`README.md`](README.md) — top-level documentation index plus runnable commands for every maintained Python and Prolog demonstration.
- [`DEBUGGER.md`](DEBUGGER.md) — ARC3 debugger controls, action trees, symbolic artifacts, replay, browser terminal, and Turtle DSL.
- [`KAGGLE.md`](KAGGLE.md) — ARC Prize 2026 local-development, notebook generation, accelerator, submission, and troubleshooting guide.
- [`SOW_PHASE_ARCHITECTURE.md`](SOW_PHASE_ARCHITECTURE.md) — mapping of existing and connected contracts to SoW Phases 1–3.
- [`TODO.md`](TODO.md) — reconciled implementation status, detailed TODOs, cross-language mapping, and implementation order.
- [`FILE_TREE.md`](FILE_TREE.md) — this clickable source map.

## Repository configuration and protected Kaggle surface

- [`Makefile`](Makefile) — existing setup, local-play, notebook-build, submission, status, and cleanup commands.
- [`.gitignore`](.gitignore) — excludes credentials, generated notebooks, environments, caches, and runtime artifacts.
- [`requirements.txt`](requirements.txt) — debugger, GPT, image, notebook, FastAPI, and PTY dependencies.
- [`agent/my_agent.py`](agent/my_agent.py) — protected ARC-AGI-3 agent entry point used by local play and notebook generation.
- [`scripts/play_local.py`](scripts/play_local.py) — protected local runner that exercises `MyAgent` against real ARC3 games.
- [`scripts/build_notebook.py`](scripts/build_notebook.py) — protected builder that inserts `agent/my_agent.py` into the Kaggle submission notebook.
- [`scripts/slim_framework.py`](scripts/slim_framework.py) — trims optional framework imports for the lightweight Kaggle workflow.
- [`notebooks/submission.ipynb`](notebooks/submission.ipynb) — generated Kaggle submission notebook; do not edit by hand.
- [`notebooks/kernel-metadata.json`](notebooks/kernel-metadata.json) — Kaggle kernel metadata and accelerator settings.
- [`notebooks/arc3_debugger.ipynb`](notebooks/arc3_debugger.ipynb) — guided notebook interface over the same ARC3 debugger runtime.
- [`notebooks/arc3_runner.ipynb`](notebooks/arc3_runner.ipynb) — lower-level notebook interface for scripted ARC3 runner use.

## Runnable debugger and demonstration scripts

- [`scripts/interactive_runner.py`](scripts/interactive_runner.py) — sole terminal debugger implementation and keyboard UI.
- [`scripts/run_webui.py`](scripts/run_webui.py) — browser-UI launcher that bootstraps the repository root before importing `webui.server`.
- [`scripts/prolog_controlled_runner.py`](scripts/prolog_controlled_runner.py) — executable SWI-Prolog action-selection demonstration.
- [`webui/server.py`](webui/server.py) — FastAPI/WebSocket PTY server launching `scripts/interactive_runner.py` rather than duplicating the debugger.
- [`webui/static/index.html`](webui/static/index.html) — browser terminal page and client-side controls.

## Phase 1 debugger and runtime

- [`python/arc3_runner.py`](python/arc3_runner.py) — ARC3 lifecycle, legal actions, level handling, history, replay, state capture, exports, and GPT/Prolog command entry points.
- [`python/action_tree.py`](python/action_tree.py) — deterministic filesystem action tree, state metadata, image hashes, parent/child links, generated node READMEs, and level-wide friendly identities.
- [`python/gpt_bridge.py`](python/gpt_bridge.py) — combined GPT request, cached artifact generation, normalization, and shared Prolog artifact output.
- [`python/swipl_bridge.py`](python/swipl_bridge.py) — existing subprocess bridge into SWI-Prolog; normalized symbolic queries extend this bridge.
- [`python/project_paths.py`](python/project_paths.py) — canonical prompt, action-tree, history, and export path resolution.
- [`python/image_codec.py`](python/image_codec.py) — authoritative frame extraction and PNG encoding used by state capture.
- [`prompts/gpt_prompts.json`](prompts/gpt_prompts.json) — Git-friendly combined GPT prompt definitions.

## Shared Python object-memory contracts

- [`python/object_memory/__init__.py`](python/object_memory/__init__.py) — public exports for all shared Phase 2 and connected Phase 3 contracts.
- [`python/object_memory/models.py`](python/object_memory/models.py) — backend-neutral execution mode, normalized result, object, residual, atom, rule, and prediction records.
- [`python/object_memory/providers.py`](python/object_memory/providers.py) — one provider interface with PROLOG, GPT-artifact, and deterministic PYTHON implementations.
- [`python/object_memory/forms.py`](python/object_memory/forms.py) — `GenerativeForm` interface and `CellLogoForm` facade over existing Turtle programs.
- [`python/object_memory/adapters.py`](python/object_memory/adapters.py) — modality-neutral perception adapter and thin grid-extractor adapter.
- [`python/object_memory/memory.py`](python/object_memory/memory.py) — residual admission, reference storage, zero-confidence commitments, evidence updates, and tombstones through `SingleWriter`.
- [`python/object_memory/prediction.py`](python/object_memory/prediction.py) — exact-identity rule store and prediction-before-outcome ledger.
- [`python/object_memory/learning.py`](python/object_memory/learning.py) — connected transition analysis, transformation learning, rule induction/ranking/execution, prediction, and independent outcome grading pipeline.
- [`python/object_memory/integration.py`](python/object_memory/integration.py) — validated Game Object Learner payload/result contracts and concrete pipeline plugin.

## Existing and connected Prolog contracts

- [`prolog/arc3_agent.pl`](prolog/arc3_agent.pl) — existing action-selection controller seam.
- [`prolog/turtle_dsl.pl`](prolog/turtle_dsl.pl) — authoritative Turtle execution semantics reused by grid generative forms.
- [`prolog/object_memory_contract.pl`](prolog/object_memory_contract.pl) — canonical Prolog dict records and normalized candidate access predicates.
- [`prolog/generative_form.pl`](prolog/generative_form.pl) — grid generative-form facade reusing `turtle_dsl.pl`.
- [`prolog/residual_gate.pl`](prolog/residual_gate.pl) — symbolic residual disposition and admission decisions.
- [`prolog/single_writer.pl`](prolog/single_writer.pl) — sole Prolog mutation path for committed atoms, evidence, and tombstones.
- [`prolog/transition_analysis.pl`](prolog/transition_analysis.pl) — provider-driven transition-analysis contract.
- [`prolog/transformation_learning.pl`](prolog/transformation_learning.pl) — transformation candidate generation, application, and validation seam.
- [`prolog/rule_induction.pl`](prolog/rule_induction.pl) — rule proposal, specialization, and generalization seam.
- [`prolog/rule_ranking.pl`](prolog/rule_ranking.pl) — deterministic scoring and ranking of normalized rules.
- [`prolog/transition_rules.pl`](prolog/transition_rules.pl) — exact rule storage in the canonical contract plus caller-supplied applicability and execution.
- [`prolog/prediction_ledger.pl`](prolog/prediction_ledger.pl) — durable prediction records and prediction-before-outcome enforcement.
- [`prolog/prediction_evaluation.pl`](prolog/prediction_evaluation.pl) — independent comparison and grading of prior predictions.
- [`prolog/game_object_learner_api.pl`](prolog/game_object_learner_api.pl) — connected Prolog orchestration from transition analysis through rule storage, prediction, and later grading.

## Tests and runnable checks

- [`tests/test_object_memory_contracts.py`](tests/test_object_memory_contracts.py) — provider normalization, residual admission, `SingleWriter`, rules, connected Phase 3 flow, prediction ordering, Kaggle-path, and runner-placement tests.
- [`tests/test_documentation_links.py`](tests/test_documentation_links.py) — enforces Markdown back-links, root documentation coverage, valid file-tree links, and per-link descriptions.
- [`prolog/test_object_memory.pl`](prolog/test_object_memory.pl) — Prolog tests for residuals, commitments, rules, the connected Phase 3 path, and prediction grading.
- [`prolog/test_turtle_dsl.pl`](prolog/test_turtle_dsl.pl) — Turtle semantics and pen-width equivalence tests.

## Runtime-generated action-tree files

These files are created beneath `action_trees/<game>/level_<n>/` and are not duplicated as static source files:

- `README.md` — generated state-node navigation and embedded local artifacts.
- `image.png` — authoritative captured frame.
- `state.json` — state metadata and action path.
- `object_registry.pl` — authoritative friendly object identities for the level.
- `objects.pl` — current-state facts referencing the shared registry.
- `differences.pl` — parent/current symbolic delta.
- `similarities.pl` — object correspondences.
- `turtle_from_image.pl` — current-state Turtle reconstruction.
- `turtle_from_diff.pl` — parent-to-current Turtle transformation.
- `rules.pl` — candidate rules and supporting symbolic context.

[← Back to top-level README](README.md)
