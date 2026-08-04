[← Back to top-level README](../README.md) · [LLM catalog documentation](README.md)

# Optional LLM and Prolog Workflows

The ordinary ARC3 path remains intentionally simple:

1. press lowercase `g` to choose a model;
2. press `4` to run its extreme full-artifact profile;
3. let Prolog or a human cherry-pick the useful evidence.

Press uppercase **`W`** only when a state needs more specialized orchestration.

## Workflow GUI

Uppercase **`W`** opens the Tkinter workflow editor. The editor provides:

- a list of workflows;
- editable workflow ID, label, and description;
- an ordered step table;
- Add, Edit, Delete, Move Up, and Move Down controls for steps;
- transaction, exact-profile, model, level, combine-group, and continue-on-error fields;
- a transaction-reference tab;
- Save and **Save and Run Selected** buttons;
- an OpenRouter availability refresh button;
- raw-JSON access for advanced fields.

Set `ARC3_LLM_WORKFLOW_EDITOR=text` to force the original terminal chooser/editor fallback.

The checked-in [`example_multistep_workflow.json`](example_multistep_workflow.json) is automatically offered in the GUI. It demonstrates:

1. `openai-gpt-5.6-light` extracting objects and Turtle reconstruction from the before/current images;
2. Groq Qwen explaining symbolic object and Turtle changes;
3. Prolog rendering/checking the symbolic evidence;
4. a free OpenRouter code model inducing rules from the generated Prolog;
5. `openai-gpt-5.6-light` performing a final consistency audit.

The first transaction already combines object extraction and Turtle reconstruction in one provider call. Additional adjacent calls are combined only when their dependencies and profiles make that safe.

## Catalog hierarchy

The optional workflow layer extends the existing hierarchy:

1. **Provider backend** — authentication, adapter, endpoint, and health checks.
2. **Model** — exact provider model slug and capabilities such as vision.
3. **Transaction** — one semantic operation and its required inputs/outputs.
4. **Profile** — selects a model plus tokens, sampling, reasoning, image detail, timeout, prompts, and default transaction.
5. **Workflow** — an ordered mix of LLM transactions and runner/Prolog methods.

The base model catalog remains [`llm_providers.json`](llm_providers.json). Optional transactions, workflows, and additional verified free models live in [`llm_workflows.json`](llm_workflows.json).

## Included transactions

- `full_artifact_bundle` — the existing combined ARC3 artifact request.
- `extract_scene_objects` — before/current images to object and Turtle artifacts.
- `explain_object_changes` — symbolic object/Turtle files to differences and correspondences.
- `induce_rules_from_prolog` — existing Prolog evidence to conservative rules.
- `audit_artifact_bundle` — all generated files to `artifact_audit.md`.
- `prolog_render_symbolic_evidence` — invokes a configurable runner/Prolog method without an LLM.

Transactions declare whether vision is required. A text-only free model is rejected before an image transaction begins.

## Included workflows

### Selected model Level 4, Prolog cherry-pick, final audit

This preserves the common workflow: run the selected model at Level 4, invoke Prolog, then perform an optional light audit.

### Staged symbolic analysis

This demonstrates a mixed paid/free pipeline:

1. GPT-5.6 light extracts objects from the before/current images.
2. Groq Qwen explains symbolic changes.
3. Prolog renders or checks the symbolic evidence.
4. a free Nemotron model induces rules from the generated Prolog.
5. GPT-5.6 light audits the complete bundle.

### All-free staged symbolic analysis

This uses a verified free vision model for object extraction, then separate free text/code models for changes, rules, and auditing.

## Combining calls

Workflow steps may use the same `combine_group`. Consecutive `llm_artifacts` transactions are combined only when:

- every transaction declares `combine_safe`;
- the steps select the same profile;
- the steps are adjacent and share the same group.

The executor unions requested artifact keys and input files and sends one provider request. Non-compatible calls remain separate.

## Current verified OpenRouter free models

The companion catalog was checked against OpenRouter's official free-model collection on **August 4, 2026**. It includes:

- `google/gemma-4-26b-a4b-it:free` — multimodal;
- `nvidia/nemotron-3-ultra-550b-a55b:free` — text reasoning/orchestration;
- `nvidia/nemotron-3-super-120b-a12b:free` — text reasoning;
- `nvidia/nemotron-3-nano-30b-a3b:free` — efficient text reasoning;
- `openai/gpt-oss-20b:free` — text reasoning and tools;
- `cohere/north-mini-code:free` — code and agentic tasks;
- `poolside/laguna-xs-2.1:free` — code and symbolic-change tasks;
- `inclusionai/ling-3.0-flash:free` — fast text inference.

The earlier multimodal Nemotron Omni and Nemotron Nano VL entries remain in the base catalog.

Use uppercase `O`, or the GUI's **Refresh OpenRouter** button, to query OpenRouter's `/models` endpoint. Missing or no-longer-free models are skipped. If the live endpoint cannot be reached, statically verified extension entries remain usable and are reported as a fallback rather than falsely reported as live-confirmed.

## Privacy and reliability

Free endpoints may have low rate limits, variable availability, and provider-specific data retention. Several current NVIDIA and Poolside free pages explicitly state that prompts and outputs may be logged or used to improve models. Do not send confidential state, personal data, faces, voices, credentials, or proprietary code without reviewing the selected endpoint's current terms.

OpenRouter's free plan and free-model router are suitable for experimentation and low-volume research, not guaranteed production service.
