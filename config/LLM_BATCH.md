[← Back to LLM provider documentation](README.md)

# Multi-LLM Batch Profiles

The interactive debugger has two related LLM controls:

- lowercase **`g`** cycles the single active provider;
- uppercase **`G`** opens the multi-LLM batch profile chooser.

A batch profile is a complete runnable configuration, not a global preset. The same provider or model may therefore appear several times with different settings.

Each row independently defines:

- provider and exact model slug;
- enabled/disabled state;
- analysis level 2, 3, or 4;
- maximum output tokens;
- temperature and top-p;
- optional seed;
- reasoning effort;
- current and parent image detail;
- request timeout.

Profiles live in [`llm_batch_profiles.json`](llm_batch_profiles.json). Set `ARC3_LLM_BATCH_CONFIG` to use another file.

## Interactive commands

Press uppercase **`G`** from the debugger. The menu accepts:

```text
number       toggle one profile
e NUMBER     edit every runtime parameter for one profile
a            enable every profile whose provider is configured
n            disable all profiles
s            save current toggles and edits back to JSON
r            run every checked profile
Enter        cancel
```

The runner skips profiles whose provider credentials are absent. A provider that fails during inference is recorded as failed and the remaining checked rows continue.

Every attempted provider call keeps its own Markdown comparison transcript in the current action-tree node. Successful transcripts contain restorable Prolog snapshots.

After the batch finishes, the debugger restores a completed transcript belonging to the provider selected with lowercase `g`. That provider therefore remains the mutable `.pl` view and the active run shown in the node's real `README.md`; the other runs remain linked comparison transcripts.

## Checked-in OpenRouter profiles

The initial file includes several independently editable profiles for:

- `openrouter/free`, which selects a compatible free model for each request;
- `nvidia/nemotron-nano-12b-v2-vl:free`;
- `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free`.

The two explicit NVIDIA models accept image input, which is required by the ARC3 artifact request. Free endpoints have quotas, availability changes, and provider-specific data policies; do not send confidential images or state data without reviewing the endpoint terms.

## Example profile

```json
{
  "id": "nemotron-omni-deep",
  "label": "Nemotron 3 Nano Omni — deep",
  "provider_id": "openrouter-free",
  "model": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
  "enabled": true,
  "analysis_level": 3,
  "max_output_tokens": 16000,
  "temperature": 0.05,
  "top_p": 0.95,
  "reasoning_effort": "medium",
  "current_image_detail": "high",
  "parent_image_detail": "low",
  "timeout_seconds": 480
}
```

Keep `OPENROUTER_API_KEY` in `.env` or the process environment, never in either JSON configuration file.
