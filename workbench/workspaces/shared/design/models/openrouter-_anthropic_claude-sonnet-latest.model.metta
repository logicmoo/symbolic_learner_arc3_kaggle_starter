(
  (kind model)
  (id openrouter-_anthropic_claude-sonnet-latest)
  (label "Anthropic Claude Sonnet Latest")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model ~anthropic/claude-sonnet-latest)
  (enabled true)
  (capabilities (
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
  (limits (
    (contextWindow 1000000)
    (maxOutputTokens 128000)
  ))
  (pricing (
    (prompt "0.000002")
    (completion "0.00001")
    (web_search "0.01")
    (input_cache_read "0.0000002")
    (input_cache_write "0.0000025")
    (input_cache_write_1h "0.000004")
  ))
  (properties (
    (id ~anthropic/claude-sonnet-latest)
    (canonical_slug ~anthropic/claude-sonnet-latest)
    (alias_target (
      (name "Anthropic: Claude Sonnet 5")
      (slug anthropic/claude-sonnet-5)
    ))
    (hugging_face_id null)
    (name "Anthropic Claude Sonnet Latest")
    (created 1777318368)
    (description "This model always redirects to the latest model in the Anthropic Claude Sonnet family.")
    (context_length 1000000)
    (architecture (
      (modality text+image+file->text)
      (input_modalities ([]
        text
        image
        file
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Router)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.000002")
      (completion "0.00001")
      (web_search "0.01")
      (input_cache_read "0.0000002")
      (input_cache_write "0.0000025")
      (input_cache_write_1h "0.000004")
    ))
    (top_provider (
      (context_length 1000000)
      (max_completion_tokens 128000)
      (is_moderated true)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      include_reasoning
      max_completion_tokens
      max_tokens
      reasoning
      reasoning_effort
      response_format
      stop
      structured_outputs
      tool_choice
      tools
      verbosity
    ))
    (default_parameters (
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
    (links (
      (details /api/v1/models/~anthropic/claude-sonnet-latest/endpoints)
    ))
    (reasoning (
      (mandatory false)
      (default_enabled true)
      (supported_efforts ([]
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
  (providerMetadata (
    (id ~anthropic/claude-sonnet-latest)
    (canonical_slug ~anthropic/claude-sonnet-latest)
    (alias_target (
      (name "Anthropic: Claude Sonnet 5")
      (slug anthropic/claude-sonnet-5)
    ))
    (hugging_face_id null)
    (name "Anthropic Claude Sonnet Latest")
    (created 1777318368)
    (description "This model always redirects to the latest model in the Anthropic Claude Sonnet family.")
    (context_length 1000000)
    (architecture (
      (modality text+image+file->text)
      (input_modalities ([]
        text
        image
        file
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Router)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.000002")
      (completion "0.00001")
      (web_search "0.01")
      (input_cache_read "0.0000002")
      (input_cache_write "0.0000025")
      (input_cache_write_1h "0.000004")
    ))
    (top_provider (
      (context_length 1000000)
      (max_completion_tokens 128000)
      (is_moderated true)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      include_reasoning
      max_completion_tokens
      max_tokens
      reasoning
      reasoning_effort
      response_format
      stop
      structured_outputs
      tool_choice
      tools
      verbosity
    ))
    (default_parameters (
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
    (links (
      (details /api/v1/models/~anthropic/claude-sonnet-latest/endpoints)
    ))
    (reasoning (
      (mandatory false)
      (default_enabled true)
      (supported_efforts ([]
        max
        xhigh
        high
        medium
        low
      ))
      (default_effort high)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId ~anthropic/claude-sonnet-latest)
  ))
)
