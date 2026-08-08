(
  (kind model)
  (id openrouter-_anthropic_claude-haiku-latest)
  (label "Anthropic Claude Haiku Latest")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model ~anthropic/claude-haiku-latest)
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
    (contextWindow 200000)
    (maxOutputTokens 64000)
  ))
  (pricing (
    (prompt "0.000001")
    (completion "0.000005")
    (web_search "0.01")
    (input_cache_read "0.0000001")
    (input_cache_write "0.00000125")
    (input_cache_write_1h "0.000002")
  ))
  (properties (
    (id ~anthropic/claude-haiku-latest)
    (canonical_slug ~anthropic/claude-haiku-latest)
    (alias_target (
      (name "Anthropic: Claude Haiku 4.5")
      (slug anthropic/claude-haiku-4.5)
    ))
    (hugging_face_id null)
    (name "Anthropic Claude Haiku Latest")
    (created 1777318492)
    (description "This model always redirects to the latest model in the Anthropic Claude Haiku family.")
    (context_length 200000)
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
      (prompt "0.000001")
      (completion "0.000005")
      (web_search "0.01")
      (input_cache_read "0.0000001")
      (input_cache_write "0.00000125")
      (input_cache_write_1h "0.000002")
    ))
    (top_provider (
      (context_length 200000)
      (max_completion_tokens 64000)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      include_reasoning
      max_completion_tokens
      max_tokens
      reasoning
      response_format
      stop
      structured_outputs
      temperature
      tool_choice
      tools
      top_k
      top_p
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
      (details /api/v1/models/~anthropic/claude-haiku-latest/endpoints)
    ))
    (reasoning (
      (mandatory false)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id ~anthropic/claude-haiku-latest)
    (canonical_slug ~anthropic/claude-haiku-latest)
    (alias_target (
      (name "Anthropic: Claude Haiku 4.5")
      (slug anthropic/claude-haiku-4.5)
    ))
    (hugging_face_id null)
    (name "Anthropic Claude Haiku Latest")
    (created 1777318492)
    (description "This model always redirects to the latest model in the Anthropic Claude Haiku family.")
    (context_length 200000)
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
      (prompt "0.000001")
      (completion "0.000005")
      (web_search "0.01")
      (input_cache_read "0.0000001")
      (input_cache_write "0.00000125")
      (input_cache_write_1h "0.000002")
    ))
    (top_provider (
      (context_length 200000)
      (max_completion_tokens 64000)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      include_reasoning
      max_completion_tokens
      max_tokens
      reasoning
      response_format
      stop
      structured_outputs
      temperature
      tool_choice
      tools
      top_k
      top_p
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
      (details /api/v1/models/~anthropic/claude-haiku-latest/endpoints)
    ))
    (reasoning (
      (mandatory false)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId ~anthropic/claude-haiku-latest)
  ))
)
