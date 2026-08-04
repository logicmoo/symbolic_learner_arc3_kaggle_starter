[← Back to LLM catalog documentation](README.md)

# LLM Catalog Schema Reference

`llm_providers.json` has three independently editable layers.

## `llm_providers`

Provider backends contain transport and authentication only:

- `id`, `label`;
- `adapter`;
- `api_key_env`, `api_key_optional`;
- `base_url`, `base_url_env`;
- `health_url`, `health_url_env`;
- `enabled`;
- `supports_reasoning` backend default;
- `timeout_seconds` backend default;
- `default_model`.

A provider may expose many models.

## `llm_models`

Models select providers:

- `id`, `label`;
- `provider` — provider backend ID;
- `model` — exact provider model slug;
- optional `model_env` override;
- `supports_reasoning`;
- `vision`;
- `default_level`.

## `llm_profiles`

Profiles select models and one analysis level:

- `id`, `label`;
- `model` — model ID;
- `analysis_level` — 2, 3, or 4;
- `single_enabled`, `batch_enabled`;
- `max_output_tokens`;
- `temperature`, `top_p`, optional `seed`;
- `reasoning_effort`;
- `current_image_detail`, `parent_image_detail`;
- `timeout_seconds`;
- ordered `prompt_text` section names.

The catalog rejects duplicate IDs, broken provider/model references, broken model/profile references, duplicate or unknown prompt sections, invalid levels, and non-positive token or timeout values.
