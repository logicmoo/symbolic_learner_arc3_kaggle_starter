[← Back to top-level README](README.md)

# Repository File Tree and Responsibilities

This is the clickable source map for the maintained repository. Every listed path links directly to the file and includes its responsibility.

## Root documentation

- [`README.md`](README.md) — top-level documentation index, delivered-debugger phase boundary, layered resource discovery, installation, and runnable commands.
- [`README_WINDOWS.md`](README_WINDOWS.md) — native Windows installation, long paths, Python aliases, `.venv`, line endings, batch launchers, Prolog, Kaggle, PyCharm, and UNC-path troubleshooting.
- [`config/README.md`](config/README.md) — unified provider/prompt configuration, provider cycling, comparison transcripts, artifact restoration, Unsloth Studio, Claude, and OpenAI.
- [`DEBUGGER.md`](DEBUGGER.md) — ARC3 debugger controls, pluggable commands, action trees, provider artifacts, replay, browser terminal, and Turtle mock inspection.
- [`KAGGLE.md`](KAGGLE.md) — ARC Prize 2026 local development, notebook generation, accelerator, submission, and troubleshooting guide.
- [`SOW_PHASE_ARCHITECTURE.md`](SOW_PHASE_ARCHITECTURE.md) — large technical overview separating the delivered debugger from Phase 2 object semantics and Phase 3 learning/prediction.
- [`TODO.md`](TODO.md) — post-delivery debugger maintenance plus concrete Phase 2 and Phase 3 implementation work.
- [`SOW_DELIVERABLES.md`](SOW_DELIVERABLES.md) — completed Phase 1 debugger checklist and partial/open Phase 2 and Phase 3 outcomes with evidence links.
- [`FILE_TREE.md`](FILE_TREE.md) — this clickable source map.
- [`docs/WORLD_ANALYSIS_WORKBENCH.md`](docs/WORLD_ANALYSIS_WORKBENCH.md) — domain-neutral observations, information silos, world models, goals, simulations, and ARC3 human-demonstration workflow.

The planning documents have deliberately separate scopes and cross-link one another:

- architecture explains how the debugger, object memory, and learner are designed;
- TODO tracks what is actively being implemented;
- deliverables tracks what is delivered and what remains to be checked off.

## World Analysis Workbench core

- [`python/worldworkbench/core.py`](python/worldworkbench/core.py) — versioned information silos, observations, interventions, human demonstrations, world models, goals, simulations, and orchestration contracts.
- [`python/worldworkbench/__init__.py`](python/worldworkbench/__init__.py) — public domain-neutral workbench API.
- [`python/worldworkbench/adapters/arc3.py`](python/worldworkbench/adapters/arc3.py) — ARC3 observation, intervention, human-choice, and artifact translation boundary.
- [`python/worldworkbench/adapters/__init__.py`](python/worldworkbench/adapters/__init__.py) — public ARC3 adapter exports.
- [`config/world_workbench_datatypes.json`](config/world_workbench_datatypes.json) — domain-neutral semantic and representation datatype manifest.
- [`config/world_workbench_operations.json`](config/world_workbench_operations.json) — reusable processing-resource contracts, including object extraction and Turtle representation operations.
- [`config/llm_workflows.json`](config/llm_workflows.json) — runnable workflow-desktop catalog, including the seven-step `ls20` human-observation workflow and its nested subworkflows.
- [`python/workflow_operation_editor.py`](python/workflow_operation_editor.py) — MeTTaSymbolicLearnerWorkbench desktop for composing, validating, inspecting, saving, and running typed operations and nested subworkflows.

## Repository configuration and protected Kaggle surface

- [`.gitattributes`](.gitattributes) — repository line-ending policy.
- [`.env.example`](.env.example) — realistic placeholders for unified LLM config, transcript logging, provider keys/models/endpoints, analysis profiles, runtime paths, web UI, PyCharm, and Kaggle.
- [`config/llm_providers.json`](config/llm_providers.json) — single source for reusable `prompt_text` blocks and ordered `llm_providers`, with each provider selecting its own prompt-section list.
- [`pyproject.toml`](pyproject.toml) — canonical package metadata, dependency extras, platform-specific terminal dependencies, package layout, and pytest configuration.
- [`requirements.txt`](requirements.txt) — compatibility installer for debugger, notebook, and test extras.
- [`Makefile`](Makefile) — POSIX setup, local-play, notebook-build, submission, status, and cleanup commands; native Windows alternatives are documented separately.
- [`.gitignore`](.gitignore) — excludes credentials, generated notebooks, environments, caches, and runtime artifacts.
- [`agent/my_agent.py`](agent/my_agent.py) — protected ARC-AGI-3 agent entry point used by local play and notebook generation.
- [`scripts/play_local.py`](scripts/play_local.py) — protected local runner that exercises `MyAgent` against real ARC3 games after resolving runtime resources.
- [`scripts/build_notebook.py`](scripts/build_notebook.py) — protected builder that inserts `agent/my_agent.py` into the generated Kaggle submission notebook.
- [`scripts/slim_framework.py`](scripts/slim_framework.py) — trims optional framework imports in the vendored ARC-AGI-3 Agents framework.
- [`notebooks/submission.ipynb`](notebooks/submission.ipynb) — generated Kaggle submission notebook; do not edit by hand.
- [`notebooks/kernel-metadata.json`](notebooks/kernel-metadata.json) — Kaggle kernel metadata and accelerator settings.
- [`notebooks/arc3_debugger.ipynb`](notebooks/arc3_debugger.ipynb) — guided notebook interface over the same ARC3 debugger runtime.
- [`notebooks/arc3_runner.ipynb`](notebooks/arc3_runner.ipynb) — lower-level notebook interface for scripted ARC3 runner use.

## Runnable scripts and runtime bootstrap

- [`scripts/_runtime.py`](scripts/_runtime.py) — layered resolver for launch directory, code checkout, `.env` files, LLM config, action-tree output, import paths, startup reporting, and optional PyCharm attachment.
- [`scripts/setup_windows.bat`](scripts/setup_windows.bat) — native Windows setup using Python 3.12+, `.venv`, optional dependencies, the vendored Agents framework, and import verification.
- [`scripts/interactive_runner.bat`](scripts/interactive_runner.bat) — native Windows launcher that preserves the caller workspace, isolates Python paths, repairs missing core dependencies, and invokes the project interpreter directly.
- [`scripts/interactive_runner.py`](scripts/interactive_runner.py) — runtime-aware terminal launcher that installs the multi-LLM and provider command extensions into the debugger UI loop.
- [`python/interactive_runner.py`](python/interactive_runner.py) — full terminal debugger implementation imported and extended by the launcher.
- [`scripts/run_webui.py`](scripts/run_webui.py) — runtime-aware browser-UI launcher; the browser subprocess uses the same multi-LLM interactive script.
- [`scripts/prolog_controlled_runner.py`](scripts/prolog_controlled_runner.py) — runtime-aware SWI-Prolog action-selection demonstration.
- [`scripts/re_play.py`](scripts/re_play.py) — direct ARC3 action-space and one-step smoke demo.
- [`scripts/my_play.py`](scripts/my_play.py) — direct ARC3 repeated-`ACTION1` smoke demo.
- [`scripts/me_play.py`](scripts/me_play.py) — random-action ARC3 demo with terminal rendering.
- [`scripts/he_play.py`](scripts/he_play.py) — random-action ARC3 demo with human rendering.
- [`webui/server.py`](webui/server.py) — FastAPI/WebSocket cross-platform PTY server launching `scripts/interactive_runner.py`; Windows uses ConPTY through `pywinpty`.
- [`webui/static/index.html`](webui/static/index.html) — browser terminal page and client-side controls.

## Phase 1 delivered debugger, providers, and evidence

- [`python/arc3_runner.py`](python/arc3_runner.py) — ARC3 lifecycle, legal actions, level handling, rendered observations, action history, replay, reset/restart, exports, and pluggable symbolic command entry points.
- [`python/multillm_runner.py`](python/multillm_runner.py) — provider-switching debugger extension, transcript chooser/restoration, provider-aware regeneration, and per-node LLM provenance.
- [`python/llm_providers.py`](python/llm_providers.py) — unified provider/prompt registry, prompt-section composition, OpenAI-compatible routing, Anthropic translation, and provider usage metadata.
- [`python/unsloth_studio.py`](python/unsloth_studio.py) — authenticated Unsloth inference-status probing, automatic GGUF loading, readiness waiting, lifecycle reporting, and one no-model retry.
- [`python/llm_json.py`](python/llm_json.py) — strict JSON parsing, deterministic malformed-JSON repair, required-key validation, and normalized strict serialization.
- [`python/llm_json_patch.py`](python/llm_json_patch.py) — response wrapper that records initial output, performs local or text-only repair, and keeps interactions in one run record.
- [`python/llm_transcripts.py`](python/llm_transcripts.py) — artifact-first Markdown comparison/cache writer, request/image/debug capture, transcript metadata, listing, and artifact restoration.
- [`python/llm_readme_patch.py`](python/llm_readme_patch.py) — README integration that marks the active restorable transcript, links historical runs, and prevents recursive embedding.
- [`python/action_tree.py`](python/action_tree.py) — deterministic action tree, rendered state metadata, encounter/action history, replay paths, generated READMEs, level-wide `object_registry.pl`, and provider artifact storage.
- [`python/gpt_bridge.py`](python/gpt_bridge.py) — provider-selected prompt, shared multimodal request, artifact generation, friendly-identity normalization, and debugger-visible Prolog outputs; it is a bridge, not the final native object learner.
- [`python/swipl_bridge.py`](python/swipl_bridge.py) — subprocess bridge into SWI-Prolog and the Turtle interpreter; later semantic queries extend this bridge.
- [`python/project_paths.py`](python/project_paths.py) — unified workbench/legacy ARC3 config, analysis-run/action-tree, history, and export path access.
- [`python/image_codec.py`](python/image_codec.py) — authoritative rendered-frame extraction and PNG encoding used by debugger state capture.

## Shared Python object-memory and learner contracts

- [`python/object_memory/__init__.py`](python/object_memory/__init__.py) — public exports for shared Phase 2 and connected Phase 3 contracts.
- [`python/object_memory/models.py`](python/object_memory/models.py) — backend-neutral execution mode, normalized result, object, residual, atom, rule, evidence, confidence, and prediction records.
- [`python/object_memory/providers.py`](python/object_memory/providers.py) — one provider interface with PROLOG, GPT-artifact, and deterministic PYTHON implementations.
- [`python/object_memory/forms.py`](python/object_memory/forms.py) — `GenerativeForm` and `CellLogoForm`; Phase 2 extends these into one regenerating Turtle program per object using movement, rotation, pen state, and pen width rather than box filling.
- [`python/object_memory/adapters.py`](python/object_memory/adapters.py) — modality-neutral perception adapter and thin grid-extractor adapter, with later image and simple-video providers sharing the same contracts.
- [`python/object_memory/memory.py`](python/object_memory/memory.py) — residual admission, reference storage, zero-confidence commitments, positive/negative evidence updates, confidence governance, and tombstones through `SingleWriter`.
- [`python/object_memory/prediction.py`](python/object_memory/prediction.py) — exact-identity rule store and prediction-before-outcome ledger.
- [`python/object_memory/learning.py`](python/object_memory/learning.py) — connected transition analysis, transformation learning, competing-rule induction/ranking/execution, prediction, and independent outcome grading pipeline.
- [`python/object_memory/integration.py`](python/object_memory/integration.py) — validated Game Object Learner payload/result contracts and concrete pipeline plugin independent of debugger internals.

## Existing and connected Prolog contracts

- [`prolog/arc3_agent.pl`](prolog/arc3_agent.pl) — action-selection controller seam.
- [`prolog/turtle_dsl.pl`](prolog/turtle_dsl.pl) — authoritative Turtle execution semantics, including movement and pen-width behavior reused by Phase 2 object programs.
- [`prolog/object_memory_contract.pl`](prolog/object_memory_contract.pl) — canonical Prolog records and normalized candidate access predicates.
- [`prolog/generative_form.pl`](prolog/generative_form.pl) — grid generative-form facade reusing `turtle_dsl.pl`.
- [`prolog/residual_gate.pl`](prolog/residual_gate.pl) — symbolic residual disposition and admission decisions.
- [`prolog/single_writer.pl`](prolog/single_writer.pl) — sole Prolog mutation path for committed atoms, evidence, confidence, and tombstones.
- [`prolog/transition_analysis.pl`](prolog/transition_analysis.pl) — provider-driven transition-analysis contract.
- [`prolog/transformation_learning.pl`](prolog/transformation_learning.pl) — transformation candidate generation, application, and validation seam.
- [`prolog/rule_induction.pl`](prolog/rule_induction.pl) — competing-rule proposal, specialization, generalization, assumptions, and critique seam.
- [`prolog/rule_ranking.pl`](prolog/rule_ranking.pl) — deterministic scoring and ranking of normalized rules using evidence and prediction history.
- [`prolog/transition_rules.pl`](prolog/transition_rules.pl) — exact rule storage plus caller-supplied applicability and execution.
- [`prolog/prediction_ledger.pl`](prolog/prediction_ledger.pl) — durable prediction records and prediction-before-outcome enforcement.
- [`prolog/prediction_evaluation.pl`](prolog/prediction_evaluation.pl) — independent comparison and grading of prior predictions.
- [`prolog/game_object_learner_api.pl`](prolog/game_object_learner_api.pl) — connected orchestration from transition analysis through rule storage, prediction, later grading, and debugger-visible result handoff.

## Tests and runnable checks

- [`tests/test_llm_providers.py`](tests/test_llm_providers.py) — provider availability/cycling, selected prompt sections, transition exclusion, model routing, usage metadata, and Claude image conversion.
- [`tests/test_unsloth_studio.py`](tests/test_unsloth_studio.py) — Unsloth status/load lifecycle, already-loaded reuse, automatic loading, payload settings, and status reporting.
- [`tests/test_llm_json.py`](tests/test_llm_json.py) — malformed-JSON repair, required-key validation, and one-transcript text-only fallback logging.
- [`tests/test_llm_transcripts.py`](tests/test_llm_transcripts.py) — artifact-first layout, Markdown prompt rendering, response-at-bottom behavior, README history links, and artifact restoration.
- [`tests/test_env_example.py`](tests/test_env_example.py) — `.env.example` parsing and expected unified settings.
- [`tests/test_dotenv_runtime.py`](tests/test_dotenv_runtime.py) — `.env` loading and shell/IDE precedence.
- [`tests/test_resource_discovery.py`](tests/test_resource_discovery.py) — launch-workspace config/action-tree discovery and startup path reporting.
- [`tests/test_windows_dependency_bootstrap.py`](tests/test_windows_dependency_bootstrap.py) — venv-direct execution, path sanitization, Command Prompt quoting, workspace preservation, and dependency repair.
- [`tests/test_object_memory_contracts.py`](tests/test_object_memory_contracts.py) — provider normalization, residual admission, `SingleWriter`, rules, connected Phase 3 flow, prediction ordering, Kaggle-path, and runner-placement tests.
- [`tests/test_documentation_links.py`](tests/test_documentation_links.py) — root-document coverage, cross-links, valid file-tree links, and descriptions.
- [`tests/test_runtime_home.py`](tests/test_runtime_home.py) — code-root precedence and script bootstrap coverage.
- [`tests/test_world_workbench.py`](tests/test_world_workbench.py) — versioned silos, goal-directed simulation, human-demonstration observation, ARC3 adapter isolation, and seven-step workflow tests.
- [`prolog/test_object_memory.pl`](prolog/test_object_memory.pl) — Prolog tests for residuals, commitments, rules, connected Phase 3 flow, and prediction grading.
- [`prolog/test_turtle_dsl.pl`](prolog/test_turtle_dsl.pl) — Turtle movement, pen state, pen width, and thick/thin equivalence tests.

## Runtime-generated action-tree files

These files are created beneath `action_trees/<game>/level_<n>/`:

- `README.md` — state navigation, active transcript, historical run links, embedded latest provider artifacts, readable identities, Turtle mocks, candidate rules, critiques, and confidence outputs.
- `image.png` — authoritative captured rendered frame.
- `state.json` — debugger metadata and action path.
- `llm_provider.json` — provider, model, endpoint, analysis level, generation time, and restored-transcript provenance for current artifacts.
- `llm_adapter_<adapter>_<provider>_<model>_<level>_<profile>_tokens_<budget>_<timestamp>.md` — immutable artifact snapshot followed by exact request/response debugging details.
- `object_registry.pl` — Phase 1 readable provider identities for the level and the bootstrap point for Phase 2 persistent identity.
- `objects.pl` — provider-proposed current-state object descriptions.
- `differences.pl` — provider-proposed parent/current symbolic delta.
- `similarities.pl` — provider-proposed object correspondence or similarity.
- `turtle_from_image.pl` — provider-supplied Turtle mock or reconstruction.
- `turtle_from_diff.pl` — provider-supplied visual transformation description.
- `rules.pl` — candidate rules, assumptions, critiques, probability or confidence output, and supporting context.

Phase 2 and Phase 3 add semantic object records, per-object Turtle programs, recognition accounts, evidence, calibrated confidence, learner payloads, predictions, outcomes, and grades while continuing to expose them through this Phase 1 debugger evidence surface.

[← Back to top-level README](README.md)
