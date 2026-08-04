[← Back to top-level README](README.md)

# Repository File Tree and Responsibilities

This is the clickable source map for the maintained repository. Every listed path links directly to the file and includes its responsibility.

## Root documentation

- [`README.md`](README.md) — top-level documentation index, runtime-home rules, installation, and runnable commands.
- [`README_WINDOWS.md`](README_WINDOWS.md) — native Windows installation, long paths, Python aliases, `.venv`, line endings, batch launchers, Prolog, Kaggle, PyCharm, and UNC-path troubleshooting.
- [`config/README.md`](config/README.md) — unified provider/prompt configuration, provider cycling, comparison transcripts, artifact restoration, Unsloth Studio, Claude, and OpenAI.
- [`DEBUGGER.md`](DEBUGGER.md) — ARC3 debugger controls, action trees, symbolic artifacts, replay, browser terminal, and Turtle DSL.
- [`KAGGLE.md`](KAGGLE.md) — ARC Prize 2026 local-development, notebook generation, accelerator, submission, and troubleshooting guide.
- [`SOW_PHASE_ARCHITECTURE.md`](SOW_PHASE_ARCHITECTURE.md) — mapping of existing and connected contracts to SoW Phases 1–3.
- [`TODO.md`](TODO.md) — reconciled implementation status, detailed TODOs, cross-language mapping, and implementation order.
- [`FILE_TREE.md`](FILE_TREE.md) — this clickable source map.

## Repository configuration and protected Kaggle surface

- [`.gitattributes`](.gitattributes) — enforces LF repository text with CRLF only for native Windows `.bat` and `.cmd` scripts.
- [`.env.example`](.env.example) — realistic placeholders for unified LLM config, transcript logging, provider keys/models/endpoints, analysis profiles, runtime paths, web UI, PyCharm, and Kaggle.
- [`config/llm_providers.json`](config/llm_providers.json) — single source for reusable `prompt_text` blocks and ordered `llm_providers`, with each provider selecting its own prompt-section list.
- [`pyproject.toml`](pyproject.toml) — canonical package metadata, dependency extras, platform-specific terminal dependencies, package layout, and pytest configuration.
- [`requirements.txt`](requirements.txt) — compatibility installer for debugger, notebook, and test extras.
- [`Makefile`](Makefile) — POSIX setup, local-play, notebook-build, submission, status, and cleanup commands; native Windows alternatives are documented separately.
- [`.gitignore`](.gitignore) — excludes credentials, generated notebooks, environments, caches, and runtime artifacts.
- [`agent/my_agent.py`](agent/my_agent.py) — protected ARC-AGI-3 agent entry point used by local play and notebook generation.
- [`scripts/play_local.py`](scripts/play_local.py) — protected local runner that exercises `MyAgent` against real ARC3 games after resolving the runtime home.
- [`scripts/build_notebook.py`](scripts/build_notebook.py) — protected builder that resolves the runtime home and inserts `agent/my_agent.py` into the Kaggle submission notebook.
- [`scripts/slim_framework.py`](scripts/slim_framework.py) — trims optional framework imports in the vendored ARC-AGI-3 Agents framework.
- [`notebooks/submission.ipynb`](notebooks/submission.ipynb) — generated Kaggle submission notebook; do not edit by hand.
- [`notebooks/kernel-metadata.json`](notebooks/kernel-metadata.json) — Kaggle kernel metadata and accelerator settings.
- [`notebooks/arc3_debugger.ipynb`](notebooks/arc3_debugger.ipynb) — guided notebook interface over the same ARC3 debugger runtime.
- [`notebooks/arc3_runner.ipynb`](notebooks/arc3_runner.ipynb) — lower-level notebook interface for scripted ARC3 runner use.

## Runnable scripts and runtime bootstrap

- [`scripts/_runtime.py`](scripts/_runtime.py) — shared resolver that checks `ARC3_RUNTIME_HOME`, then the working directory, then the script location; it loads `.env`, changes into the selected project root, and configures import paths.
- [`scripts/setup_windows.bat`](scripts/setup_windows.bat) — native Windows setup using Python 3.12+, `.venv`, all optional dependencies, the vendored Agents framework, and import verification.
- [`scripts/interactive_runner.bat`](scripts/interactive_runner.bat) — native Windows debugger launcher that isolates Python paths, repairs missing core dependencies, and calls `.venv\Scripts\python.exe` directly.
- [`scripts/interactive_runner.py`](scripts/interactive_runner.py) — runtime-aware terminal launcher that installs the multi-LLM runner into the existing debugger UI loop.
- [`python/interactive_runner.py`](python/interactive_runner.py) — full terminal debugger implementation imported and extended by the launcher.
- [`scripts/run_webui.py`](scripts/run_webui.py) — runtime-aware browser-UI launcher; the browser subprocess uses the same multi-LLM interactive script.
- [`scripts/prolog_controlled_runner.py`](scripts/prolog_controlled_runner.py) — runtime-aware SWI-Prolog action-selection demonstration.
- [`scripts/re_play.py`](scripts/re_play.py) — direct ARC3 action-space and one-step smoke demo.
- [`scripts/my_play.py`](scripts/my_play.py) — direct ARC3 repeated-`ACTION1` smoke demo.
- [`scripts/me_play.py`](scripts/me_play.py) — random-action ARC3 demo with terminal rendering.
- [`scripts/he_play.py`](scripts/he_play.py) — random-action ARC3 demo with human rendering.
- [`webui/server.py`](webui/server.py) — FastAPI/WebSocket cross-platform PTY server launching `scripts/interactive_runner.py`; Windows uses ConPTY through `pywinpty`.
- [`webui/static/index.html`](webui/static/index.html) — browser terminal page and client-side controls.

## Phase 1 debugger and runtime

- [`python/arc3_runner.py`](python/arc3_runner.py) — ARC3 lifecycle, legal actions, level handling, history, replay, state capture, exports, and GPT/Prolog-compatible command entry points.
- [`python/multillm_runner.py`](python/multillm_runner.py) — provider-switching runner extension, transcript chooser/restoration, provider-aware regeneration, and per-node LLM provenance.
- [`python/llm_providers.py`](python/llm_providers.py) — unified provider/prompt registry, ordered prompt-section composition, OpenAI Responses routing, OpenAI-compatible local routing, Anthropic translation, and provider usage metadata.
- [`python/unsloth_studio.py`](python/unsloth_studio.py) — authenticated Unsloth inference-status probing, automatic GGUF loading, readiness waiting, lifecycle status reporting, and one no-model retry.
- [`python/llm_json.py`](python/llm_json.py) — strict JSON parsing, deterministic malformed-JSON repair, required-key validation, and normalized strict serialization.
- [`python/llm_json_patch.py`](python/llm_json_patch.py) — response wrapper that starts one Markdown transcript, records raw output, performs local or text-only repair, and keeps all interactions in the same run record.
- [`python/llm_transcripts.py`](python/llm_transcripts.py) — artifact-first Markdown comparison/cache writer, token/timing/request/image/debug capture, transcript metadata, transcript listing, and artifact restoration into latest files.
- [`python/llm_readme_patch.py`](python/llm_readme_patch.py) — node-README integration that marks the active restorable transcript, links every historical run, and prevents recursive transcript embedding.
- [`python/action_tree.py`](python/action_tree.py) — deterministic filesystem action tree, state metadata, image hashes, parent/child links, generated node READMEs, and level-wide friendly identities.
- [`python/gpt_bridge.py`](python/gpt_bridge.py) — provider-selected composed prompt, shared multimodal analysis request, artifact generation, normalization, and Prolog artifact output; retained under its compatibility name.
- [`python/swipl_bridge.py`](python/swipl_bridge.py) — existing subprocess bridge into SWI-Prolog; normalized symbolic queries extend this bridge.
- [`python/project_paths.py`](python/project_paths.py) — unified config, action-tree, history, and export path resolution; legacy prompt-path functions point to the unified LLM config.
- [`python/image_codec.py`](python/image_codec.py) — authoritative frame extraction and PNG encoding used by state capture.

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

- [`tests/test_llm_providers.py`](tests/test_llm_providers.py) — provider availability/cycling, provider-selected prompt sections, transition exclusion, model routing, usage metadata, and Claude image conversion.
- [`tests/test_unsloth_studio.py`](tests/test_unsloth_studio.py) — authenticated Unsloth status/load lifecycle, already-loaded reuse, automatic loading, payload settings, and status reporting.
- [`tests/test_llm_json.py`](tests/test_llm_json.py) — missing-comma/newline repair, required-key validation, and one-transcript text-only fallback logging.
- [`tests/test_llm_transcripts.py`](tests/test_llm_transcripts.py) — artifact-first transcript layout, Markdown prompt rendering, response-at-bottom behavior, README history links, and artifact restoration.
- [`tests/test_env_example.py`](tests/test_env_example.py) — parses `.env.example` and enforces unified config, transcript, provider, runtime, debugger, and Kaggle variables.
- [`tests/test_dotenv_runtime.py`](tests/test_dotenv_runtime.py) — validates project-root `.env` loading and shell/IDE precedence.
- [`tests/test_windows_dependency_bootstrap.py`](tests/test_windows_dependency_bootstrap.py) — locks in venv-direct execution, path sanitization, Command Prompt quoting, and automatic dependency repair.
- [`tests/test_object_memory_contracts.py`](tests/test_object_memory_contracts.py) — provider normalization, residual admission, `SingleWriter`, rules, connected Phase 3 flow, prediction ordering, Kaggle-path, and runner-placement tests.
- [`tests/test_documentation_links.py`](tests/test_documentation_links.py) — enforces Markdown back-links, root documentation coverage, valid file-tree links, and per-link descriptions.
- [`tests/test_runtime_home.py`](tests/test_runtime_home.py) — validates runtime-home precedence, working-directory fallback, script-location fallback, and script bootstrap coverage.
- [`prolog/test_object_memory.pl`](prolog/test_object_memory.pl) — Prolog tests for residuals, commitments, rules, the connected Phase 3 path, and prediction grading.
- [`prolog/test_turtle_dsl.pl`](prolog/test_turtle_dsl.pl) — Turtle semantics and pen-width equivalence tests.

## Runtime-generated action-tree files

These files are created beneath `action_trees/<game>/level_<n>/` and are not duplicated as static source files:

- `README.md` — state-node navigation, active transcript metadata, links to all historical LLM runs, and embedded latest mutable artifacts.
- `image.png` — authoritative captured frame.
- `state.json` — state metadata and action path.
- `llm_provider.json` — provider, adapter, model, endpoint, analysis level, generation timestamp, and restored-transcript provenance for the current latest artifacts.
- `llm_adapter_<adapter>_<provider>_<model>_<level>_<profile>_tokens_<budget>_<timestamp>.md` — immutable artifact-first comparison/cache snapshot followed by exact request/response debugging details; completed records can restore latest `.pl` files.
- `object_registry.pl` — authoritative friendly object identities for the level.
- `objects.pl` — current-state facts referencing the shared registry.
- `differences.pl` — parent/current symbolic delta.
- `similarities.pl` — object correspondences.
- `turtle_from_image.pl` — current-state Turtle reconstruction.
- `turtle_from_diff.pl` — parent-to-current Turtle transformation.
- `rules.pl` — candidate rules and supporting symbolic context.

[← Back to top-level README](README.md)
