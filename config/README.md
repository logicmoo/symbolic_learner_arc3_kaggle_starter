[← Back to top-level README](../README.md)

# LLM Provider, Model, and Profile Catalog

The symbolic workbench routes one shared multimodal artifact pipeline through an editable catalog:

[`llm_providers.json`](llm_providers.json)

The file contains reusable prompt blocks plus three normalized lists:

- `llm_providers` — backend transport, authentication, endpoints, and health settings;
- `llm_models` — selectable model IDs that reference provider backends;
- `llm_profiles` — level-specific request configurations that reference models.

This means OpenRouter authentication and endpoint settings appear once even though OpenRouter supplies several selectable models.

See [Single and Batch Model Profiles](LLM_BATCH.md) for the interactive editor and batch workflow.

See [Symbolic Datatypes Manifest Explained](../docs/DATATYPES_MANIFEST_EXPLAINED.md) for the semantic-information, typed-silo, operation-port, implementation-species, provenance, and event-driven workflow model, together with the generated datatype graph.

## Catalog shape

```json
{
  "default_model": "openrouter-nemotron-omni",
  "default_profile": "openrouter-nemotron-omni-deep",
  "prompt_text": {
    "response_contract": ["Return strict JSON."],
    "objects": ["Describe current-state objects."],
    "rules": ["Analyze rules and evidence."]
  },
  "llm_providers": [
    {
      "id": "openrouter",
      "adapter": "openai_responses",
      "api_key_env": "OPENROUTER_API_KEY",
      "base_url": "https://openrouter.ai/api/v1",
      "enabled": "auto",
      "default_model": "openrouter-auto-free"
    }
  ],
  "llm_models": [
    {
      "id": "openrouter-nemotron-omni",
      "provider": "openrouter",
      "label": "Nemotron 3 Nano Omni free",
      "model": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
      "supports_reasoning": true,
      "vision": true,
      "default_level": 3
    }
  ],
  "llm_profiles": [
    {
      "id": "openrouter-nemotron-omni-deep",
      "model": "openrouter-nemotron-omni",
      "analysis_level": 3,
      "single_enabled": true,
      "batch_enabled": true,
      "max_output_tokens": 16000,
      "temperature": 0.05,
      "top_p": 0.95,
      "reasoning_effort": "medium",
      "current_image_detail": "high",
      "parent_image_detail": "low",
      "timeout_seconds": 480,
      "seed": null,
      "prompt_text": [
        "response_contract",
        "objects",
        "rules"
      ]
    }
  ]
}
```

## Prompt composition

Each profile owns an ordered `prompt_text` list. A light and extreme profile for the same model can therefore differ in both request parameters and instructions.

The checked-in reusable prompt sections are:

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

Unknown or duplicate section names are rejected before a provider request. The exact ordered list and assembled request are preserved in the comparison transcript.

## Interactive controls

Start the debugger:

```bat
scripts\interactive_runner.bat ls20
```

- lowercase **`g`** cycles configured and ready models;
- commands **`2`**, **`3`**, and **`4`** run that model's Single-enabled level profile;
- uppercase **`G`** opens the unified backend/model/profile editor and can run all Batch-enabled profiles;
- **`p`** enters Prolog mode;
- LLM command **`1`** lists and restores historical transcripts or opens the raw catalog.

## Comparison transcripts

Every actual LLM request creates a uniquely named Markdown transcript in the current action-tree node.

Each completed transcript contains:

1. a restorable Prolog artifact snapshot;
2. backend, model, and profile identity;
3. profile level, prompt sections, token and sampling settings;
4. timing and provider-reported usage;
5. image hashes and links;
6. the exact request text;
7. malformed-JSON repair history;
8. normalized JSON and raw provider responses.

The individual `.pl` files remain the mutable latest view. Restoring a completed transcript rewrites those files and makes that transcript active in the node `README.md`.

Configure transcript behavior with:

```dotenv
ARC3_LLM_SAVE_TRANSCRIPT=1
ARC3_LLM_RESPONSE_DIR=C:/symbolic_learner_arc3_kaggle_starter/.llm_responses
ARC3_LLM_JSON_RETRY=1
```

## Credentials and endpoints

Keep keys in `.env` or the process environment, never in JSON.

### OpenAI

```bat
set OPENAI_API_KEY=your-key
set ARC3_OPENAI_MODEL=gpt-5.6
```

### Anthropic

```bat
set ANTHROPIC_API_KEY=your-key
set ARC3_CLAUDE_MODEL=claude-sonnet-4-20250514
set ARC3_CLAUDE_BASE_URL=https://api.anthropic.com/v1
```

### Groq

```bat
set GROQ_API_KEY=your-key
set ARC3_GROQ_MODEL=qwen/qwen3.6-27b
set ARC3_GROQ_BASE_URL=https://api.groq.com/openai/v1
```

### OpenRouter

```bat
set OPENROUTER_API_KEY=your-key
set ARC3_OPENROUTER_MODEL=openrouter/free
set ARC3_OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
```

The OpenRouter backend currently supplies model entries for automatic free routing and two explicit free Nemotron vision models. Add more models by adding `llm_models` rows that reference `openrouter`, then add level profiles for those model IDs.

Free endpoints have changing quotas and availability. Review upstream privacy and retention terms before sending confidential state images.

### Unsloth Studio

Start Studio locally:

```powershell
unsloth studio -H 127.0.0.1 -p 8888
```

Create an API key under **Settings → API Access** and configure:

```bat
set ARC3_UNSLOTH_API_KEY=sk-unsloth-your-key
set ARC3_UNSLOTH_MODEL=unsloth/gemma-4-E2B-it-GGUF
set ARC3_UNSLOTH_BASE_URL=http://127.0.0.1:8888/v1
```

The workbench checks inference status, reuses a matching loaded model, or loads the configured GGUF and waits for readiness.

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

## Initial selection compatibility

`ARC3_LLM_PROVIDER` remains accepted for compatibility. It may name:

- a profile ID;
- a model ID;
- a provider backend ID, in which case that backend's default model and the model's default level are selected.

The GUI writes the catalog itself; restarting or reloading the runner applies saved changes.

## Alternate catalog

```bat
set ARC3_LLM_CONFIG=C:\path\to\my_llm_providers.json
```

A replacement catalog must define `prompt_text`, `llm_providers`, `llm_models`, and `llm_profiles` with valid references between the three layers.
