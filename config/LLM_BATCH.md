[← Back to LLM provider documentation](README.md)

# Multi-LLM Provider Profiles

The debugger has two related controls:

- lowercase **`g`** cycles the one provider whose output should remain active;
- uppercase **`G`** opens the provider-profile editor and can run many checked rows.

## One unified JSON file

Provider definitions, prompt sections, and runnable profiles all live in [`llm_providers.json`](llm_providers.json).

Each provider may contain a `run_profiles` array. A profile is a complete provider-specific request configuration, so the same provider or exact model may appear several times with different parameters.

```json
{
  "id": "openrouter-free",
  "adapter": "openai_responses",
  "api_key_env": "OPENROUTER_API_KEY",
  "base_url": "https://openrouter.ai/api/v1",
  "run_profiles": [
    {
      "id": "nemotron-omni-deep",
      "label": "Nemotron 3 Nano Omni — deep",
      "model": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
      "enabled": true,
      "analysis_level": 3,
      "max_output_tokens": 16000,
      "temperature": 0.05,
      "top_p": 0.95,
      "reasoning_effort": "medium",
      "current_image_detail": "high",
      "parent_image_detail": "low",
      "timeout_seconds": 480,
      "seed": null
    }
  ]
}
```

The temporary `llm_batch_profiles.json` file is only a migration source for older checkouts. When uppercase `G` is first used, its rows are moved under the matching providers in `llm_providers.json`; the unified file then becomes authoritative.

## GUI editor

Press uppercase **`G`**. When Tkinter is available, a small desktop editor opens with one row per runnable profile and columns for:

- enabled checkbox;
- provider ID and label;
- exact model slug;
- analysis level;
- maximum output tokens;
- temperature and top-p;
- reasoning effort;
- current and parent image detail;
- request timeout;
- optional seed.

Use **Save** to update `llm_providers.json`, or **Save and Run Checked** to update the file and execute every checked row.

Set this to force the terminal editor instead:

```dotenv
ARC3_LLM_PROFILE_EDITOR=text
```

The text editor supports toggling, editing, enabling every configured provider, disabling all rows, saving, and running.

## Batch behavior

Profiles whose provider key is absent are skipped. A request that times out or fails creates its debug transcript when possible, then the batch continues with the next checked row.

Every successful run stores a separate restorable Markdown comparison transcript in the current action-tree node.

After all checked rows finish, ARC3 restores the newest successful transcript belonging to the provider selected with lowercase `g`. That provider therefore owns the mutable `.pl` files and the active section of the node's real `README.md`; all other outputs remain linked comparison transcripts.

## Initial free OpenRouter profiles

The migration seed includes independently editable rows for:

- `openrouter/free`;
- `nvidia/nemotron-nano-12b-v2-vl:free`;
- `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free`.

Keep `OPENROUTER_API_KEY` in `.env` or the process environment. Free endpoints have quotas, changing availability, and provider-specific data policies, so review them before sending confidential state images.
