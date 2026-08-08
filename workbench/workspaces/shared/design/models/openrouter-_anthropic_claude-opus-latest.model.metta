({}
  (kind model)
  (id openrouter-_anthropic_claude-opus-latest)
  (label "Anthropic: Claude Opus Latest")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model ~anthropic/claude-opus-latest)
  (enabled true)
  (capabilities ({}
    (audio false)
    (code false)
    (functionCalling true)
    (json true)
    (jsonMode true)
    (local false)
    (multimodal true)
    (reasoning true)
    (text true)
    (tools true)
    (vision true)
  ))
  (limits ({}
    (contextWindow 1000000)
    (maxOutputTokens 128000)
  ))
  (pricing ({}
    (prompt "0.000005")
    (completion "0.000025")
    (web_search "0.01")
    (input_cache_read "0.0000005")
    (input_cache_write "0.00000625")
    (input_cache_write_1h "0.00001")
  ))
  (properties ({}
    (id ~anthropic/claude-opus-latest)
    (canonical_slug ~anthropic/claude-opus-latest)
    (alias_target ({}
      (name "Claude Opus 5")
      (slug anthropic/claude-opus-5)
    ))
    (hugging_face_id "")
    (name "Anthropic: Claude Opus Latest")
    (created 1776795361)
    (description "This model always redirects to the latest model in the Claude Opus family.")
    (context_length 1000000)
    (architecture ({}
      (modality text+image+file->text)
      (input_modalities (
        text
        image
        file
      ))
      (output_modalities (
        text
      ))
      (tokenizer Router)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.000005")
      (completion "0.000025")
      (web_search "0.01")
      (input_cache_read "0.0000005")
      (input_cache_write "0.00000625")
      (input_cache_write_1h "0.00001")
    ))
    (top_provider ({}
      (context_length 1000000)
      (max_completion_tokens 128000)
      (is_moderated true)
    ))
    (per_request_limits null)
    (supported_parameters (
      include_reasoning
      max_completion_tokens
      max_tokens
      reasoning
      reasoning_effort
      response_format
      stop
      structured_outputs
      temperature
      tool_choice
      tools
      verbosity
    ))
    (default_parameters ({}
      (temperature null)
      (top_p null)
      (top_k null)
      (frequency_penalty null)
      (presence_penalty null)
      (repetition_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/~anthropic/claude-opus-latest/endpoints)
    ))
    (reasoning ({}
      (mandatory false)
      (default_enabled true)
      (supported_efforts (
        max
        xhigh
        high
        medium
        low
      ))
      (default_effort high)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id ~anthropic/claude-opus-latest)
    (canonical_slug ~anthropic/claude-opus-latest)
    (alias_target ({}
      (name "Claude Opus 5")
      (slug anthropic/claude-opus-5)
    ))
    (hugging_face_id "")
    (name "Anthropic: Claude Opus Latest")
    (created 1776795361)
    (description "This model always redirects to the latest model in the Claude Opus family.")
    (context_length 1000000)
    (architecture ({}
      (modality text+image+file->text)
      (input_modalities (
        text
        image
        file
      ))
      (output_modalities (
        text
      ))
      (tokenizer Router)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.000005")
      (completion "0.000025")
      (web_search "0.01")
      (input_cache_read "0.0000005")
      (input_cache_write "0.00000625")
      (input_cache_write_1h "0.00001")
    ))
    (top_provider ({}
      (context_length 1000000)
      (max_completion_tokens 128000)
      (is_moderated true)
    ))
    (per_request_limits null)
    (supported_parameters (
      include_reasoning
      max_completion_tokens
      max_tokens
      reasoning
      reasoning_effort
      response_format
      stop
      structured_outputs
      temperature
      tool_choice
      tools
      verbosity
    ))
    (default_parameters ({}
      (temperature null)
      (top_p null)
      (top_k null)
      (frequency_penalty null)
      (presence_penalty null)
      (repetition_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/~anthropic/claude-opus-latest/endpoints)
    ))
    (reasoning ({}
      (mandatory false)
      (default_enabled true)
      (supported_efforts (
        max
        xhigh
        high
        medium
        low
      ))
      (default_effort high)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId ~anthropic/claude-opus-latest)
  ))
)
