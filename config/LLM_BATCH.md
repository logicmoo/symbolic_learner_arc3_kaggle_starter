[← Back to top-level README](../README.md) · [LLM catalog documentation](README.md)

# Single and Batch Model Profiles

ARC3 now uses one catalog for both ordinary single-model runs and multi-model batches:

[`llm_providers.json`](llm_providers.json)

There is no separate batch configuration file.

## Three layers

The catalog separates three concepts:

1. **Provider backends** contain transport details: adapter, API-key environment variable, endpoint, health endpoint, and an optional default model.
2. **Models** select one provider backend and contain the exact provider model slug plus model capabilities.
3. **Level profiles** select one model and contain all request settings for one analysis level.

A provider such as OpenRouter can therefore expose many models without duplicating its authentication and endpoint settings.

## Profile fields

Every level profile independently contains:

- `single_enabled` — whether lowercase `g` plus command `2`, `3`, or `4` may use it;
- `batch_enabled` — whether uppercase `G` runs it as part of the batch;
- `analysis_level` — 2/light, 3/deep, or 4/extreme;
- `max_output_tokens`;
- `temperature` and `top_p`;
- `reasoning_effort`;
- current and parent image detail;
- request timeout;
- optional seed;
- its own ordered `prompt_text` section list.

A profile may be enabled for Single, Batch, both, or neither.

## Lowercase `g`: select a model

Press lowercase **`g`** repeatedly to cycle through configured and ready models, not provider backends.

After selecting a model:

- `2` runs that model's Single-enabled light profile;
- `3` runs that model's Single-enabled deep profile;
- `4` runs that model's Single-enabled extreme profile.

A model whose required key is absent, whose backend is unavailable, or whose selected profile failed during the current session is skipped.

## Uppercase `G`: edit and batch

Press uppercase **`G`** to open the Tkinter catalog editor. It contains three tabs:

- **Provider backends**;
- **Models**;
- **Level profiles**.

The Level Profiles tab has separate **Single** and **Batch** checkboxes and editable fields for every runtime parameter and the ordered prompt-section list.

Buttons:

- **Save** validates and rewrites `llm_providers.json`;
- **Save and Run Batch-Enabled Profiles** saves, then executes every checked Batch row;
- **Cancel** closes without saving.

Set this to force the command-line fallback:

```dotenv
ARC3_LLM_PROFILE_EDITOR=text
```

The text editor can toggle Single and Batch flags, open the unified JSON in the configured editor, save, and run.

## Output and active README behavior

Every attempted call gets its own Markdown comparison transcript. Successful calls contain a restorable snapshot of the generated Prolog artifacts.

After a batch finishes, ARC3 restores the newest completed transcript belonging to the model selected with lowercase `g`. That model therefore remains the mutable `.pl` view and the active run shown in the node's real `README.md`.

Other successful runs remain linked comparison transcripts. Failed runs remain debug-only transcripts when enough information was captured.

## Seeded models and profiles

The checked-in catalog includes light, deep, and extreme profiles for every model already configured in the repository:

- GPT-5.6 through OpenAI;
- Claude Sonnet through Anthropic;
- Qwen 3.6 27B through Groq;
- OpenRouter automatic free routing;
- Nemotron Nano 12B 2 VL through OpenRouter;
- Nemotron 3 Nano Omni through OpenRouter;
- Gemma 4 E2B through local Unsloth Studio.

The free and local deep profiles are Batch-enabled by default. Paid OpenAI and Anthropic profiles are Single-enabled but not Batch-enabled by default to avoid accidental multi-call charges.

All flags and parameters are editable.
