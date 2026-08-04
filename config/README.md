[← Back to top-level README](../README.md)

# LLM Providers, Prompt Sections, and Comparison Transcripts

The debugger keeps one analysis/artifact pipeline while routing the final multimodal request through different LLM providers. Provider definitions and prompt text now live together in [`llm_providers.json`](llm_providers.json); there is no separate `prompts/` directory.

## Unified configuration shape

The file has two main sections:

- `prompt_text` — reusable named text blocks;
- `llm_providers` — provider definitions, each with an ordered `prompt_text` list selecting which blocks are sent.

A simplified example:

```json
{
  "prompt_text": {
    "response_contract": ["Return strict JSON."],
    "objects": ["Describe current-state objects."],
    "transitions": ["TRANSITIONS: describe parent/current changes."],
    "rules": ["Analyze supported and hypothetical rules."]
  },
  "llm_providers": [
    {
      "id": "cloud-full",
      "adapter": "openai_responses",
      "model": "example-cloud-model",
      "prompt_text": [
        "response_contract",
        "objects",
        "transitions",
        "rules"
      ]
    },
    {
      "id": "local-no-transitions",
      "adapter": "openai_responses",
      "model": "example-local-model",
      "prompt_text": [
        "response_contract",
        "objects",
        "rules"
      ]
    }
  ]
}
```

The second provider excludes `transitions` simply by omitting that section name. Sections may be created for one provider only, so provider-specific instructions do not require copying the complete prompt.

The checked-in reusable sections currently include:

- `response_contract`;
- `coordinate_contract`;
- `identity_contract`;
- `object_extraction`;
- `turtle_reconstruction`;
- `transitions`;
- `correspondences`;
- `rule_analysis`;
- `file_separation`;
- `root_state`;
- `quality_control`.

The router validates unknown or duplicate section names before any provider request. The exact assembled text and selected section list are recorded in each comparison transcript.

## Switching providers

Start the debugger:

```bat
scripts\interactive_runner.bat ls20
```

Press **`g` repeatedly** to select the next configured provider. The provider display includes the provider, adapter endpoint, model, and selected `prompt_text` list. Press `2`, `3`, or `4` for the demo, deep, or extreme analysis profile.

A provider with `enabled: "auto"` participates in the cycle only when its required API-key environment variable is set. This means users can add one or both free cloud keys without changing code or disabling the paid/local choices.

Pressing `p` still enters Prolog mode.

## Markdown comparison/cache transcripts

Every actual LLM request creates a uniquely named Markdown transcript in the current action-tree node. A typical filename is:

```text
llm_adapter_openai_responses_unsloth_unsloth_gemma-4-E2B-it-GGUF_L4_extreme_tokens_32000_20260804T145700_000000Z.md
```

The filename carries the adapter, provider, model, analysis level/profile, requested token budget, and timestamp so runs can be compared directly.

Each completed transcript has two major halves:

1. **Restorable Prolog artifact snapshot first** — `object_registry.pl`, `objects.pl`, differences, similarities, Turtle programs, and rules exactly as they existed for that run.
2. **Debug transcript second** — state/action context, provider/adapter/model, prompt section list, profile and token settings, timing, provider-reported usage, image hashes/details, the exact request text, repair history, normalized JSON, and raw provider responses at the very bottom.

The initial prompt text is rendered as ordinary Markdown between hidden markers rather than buried in a code fence. Raw responses remain fenced at the end so arbitrary output cannot break the document.

Configure transcript behavior with:

```dotenv
ARC3_LLM_SAVE_TRANSCRIPT=1
ARC3_LLM_RESPONSE_DIR=C:/symbolic_learner_arc3_kaggle_starter/.llm_responses
ARC3_LLM_JSON_RETRY=1
```

`ARC3_LLM_RESPONSE_DIR` is only a fallback for calls made without an active action-tree node.

### Latest files versus historical cache

The individual `.pl` files remain the mutable **latest view** used by the debugger and Prolog code. Markdown transcripts are immutable historical cache/comparison records.

After a completed run:

- its Markdown transcript stores copies of all generated `.pl` artifacts;
- the normal individual `.pl` files remain on disk as the latest view;
- the node `README.md` identifies the active completed transcript;
- the README links every historical transcript but does not recursively embed their large bodies;
- the README continues embedding the latest mutable `.pl` files.

### Restore an older run

In LLM mode, press `1` to open the transcript cache chooser. Select a completed transcript number to:

1. extract its embedded artifact snapshot;
2. rewrite the individual latest `.pl` files;
3. rewrite `llm_provider.json` with the restored provider/model/level;
4. make that transcript active;
5. regenerate the node `README.md` so its embedded artifacts and active link match the restored run.

The same menu uses `E` to edit the unified provider-and-prompt config.

Failed or incomplete LLM runs remain linked as **debug-only** transcripts, but they are not considered restorable active snapshots.

## Malformed JSON recovery

For almost-correct LLM output, ARC3:

1. records the raw response in the current Markdown transcript;
2. attempts strict JSON parsing;
3. deterministically repairs common syntax defects locally;
4. validates every requested artifact key;
5. uses one text-only provider repair request only when local recovery is incomplete;
6. records both interactions in the same transcript;
7. never repeats the original image request merely because JSON syntax was malformed.

## Default providers

The checked-in providers are:

- **ChatGPT / OpenAI API** through the OpenAI Responses API;
- **Claude / Anthropic API** through the Anthropic Messages API;
- **Groq Free / Qwen 3.6 27B** through Groq's OpenAI-compatible Responses API;
- **OpenRouter Free** through the `openrouter/free` multimodal model router;
- **Unsloth Studio local** through its OpenAI-compatible Responses endpoint.

Providers requiring an API key are skipped when the key is absent. Groq and OpenRouter are free-tier choices with provider-controlled quotas, rate limits, and model availability; they are intended for experimentation and low-volume analysis rather than guaranteed unlimited service.

## OpenAI / ChatGPT

```bat
set OPENAI_API_KEY=your-key
set ARC3_OPENAI_MODEL=your-openai-model
```

A ChatGPT web subscription is separate from OpenAI API authentication.

## Claude / Anthropic

```bat
set ANTHROPIC_API_KEY=your-key
set ARC3_CLAUDE_MODEL=your-claude-model
```

The adapter converts the existing Responses-style text and base64 PNG blocks into Anthropic Messages content blocks.

## Groq Free / Qwen

Create a Groq API key, then configure:

```bat
set GROQ_API_KEY=your-free-tier-key
set ARC3_GROQ_MODEL=qwen/qwen3.6-27b
set ARC3_GROQ_BASE_URL=https://api.groq.com/openai/v1
```

The checked-in Qwen model accepts text and image inputs. Groq Free-plan rate limits can be lower than the ARC3 deep and extreme profiles; when necessary, start with command `2` and reduce `ARC3_GPT_2_MAX_OUTPUT_TOKENS` in `.env`.

## OpenRouter Free

Create an OpenRouter API key, then configure:

```bat
set OPENROUTER_API_KEY=your-key
set ARC3_OPENROUTER_MODEL=openrouter/free
set ARC3_OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
```

`openrouter/free` chooses an available zero-cost model and filters for capabilities required by the request, including image understanding. The selected upstream model can differ between runs, and free-model capacity can temporarily be unavailable. The transcript records the model reported by the provider for comparison.

To pin a particular free variant instead, override `ARC3_OPENROUTER_MODEL` with a current OpenRouter model id ending in `:free`.

## Unsloth Studio local

Start Studio locally:

```powershell
unsloth studio -H 127.0.0.1 -p 8888
```

The default configuration uses:

```text
Responses endpoint: http://127.0.0.1:8888/v1/responses
Health endpoint:    http://127.0.0.1:8888/api/health
Status endpoint:    http://127.0.0.1:8888/api/inference/status
Load endpoint:      http://127.0.0.1:8888/api/inference/load
Model:              unsloth/gemma-4-E2B-it-GGUF
GGUF variant:       UD-Q4_K_XL
```

Create a Studio API key under **Settings → API Access** (called **API** in some versions). Real keys begin with `sk-unsloth-`:

```bat
set ARC3_UNSLOTH_API_KEY=sk-unsloth-your-key
```

Before an Unsloth request, ARC3 checks authenticated inference status, reuses a matching loaded model, or loads the configured GGUF and waits for it to become resident.

Default lifecycle settings:

```dotenv
ARC3_UNSLOTH_AUTO_LOAD=1
ARC3_UNSLOTH_GGUF_VARIANT=UD-Q4_K_XL
ARC3_UNSLOTH_MAX_SEQ_LENGTH=131072
ARC3_UNSLOTH_N_PARALLEL=1
ARC3_UNSLOTH_GPU_MEMORY_MODE=auto
ARC3_UNSLOTH_LOAD_TIMEOUT=900
ARC3_UNSLOTH_FORCE_CANCEL_ACTIVE=0
ARC3_UNSLOTH_TRUST_REMOTE_CODE=0
```

For private or gated Hugging Face repositories:

```bat
set HF_TOKEN=hf_your-token
```

## Alternate configuration file

```bat
set ARC3_LLM_CONFIG=C:\path\to\my_llm_providers.json
```

Keep API keys in environment variables rather than JSON. A replacement config must define `prompt_text` and `llm_providers`, and each provider must select at least one valid prompt section.
