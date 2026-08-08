(
  (kind model)
  (id openrouter-_openai_gpt-mini-latest)
  (label "OpenAI GPT Mini Latest")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model ~openai/gpt-mini-latest)
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
    (contextWindow 400000)
    (maxOutputTokens 128000)
  ))
  (pricing (
    (prompt "0.00000075")
    (completion "0.0000045")
    (web_search "0.01")
    (input_cache_read "0.000000075")
  ))
  (properties (
    (id ~openai/gpt-mini-latest)
    (canonical_slug ~openai/gpt-mini-latest)
    (alias_target (
      (name "OpenAI: GPT-5.4 Mini")
      (slug openai/gpt-5.4-mini)
    ))
    (hugging_face_id null)
    (name "OpenAI GPT Mini Latest")
    (created 1777318471)
    (description "This model always redirects to the latest model in the OpenAI GPT Mini family.")
    (context_length 400000)
    (architecture (
      (modality text+image+file->text)
      (input_modalities ([]
        file
        image
        text
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Router)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.00000075")
      (completion "0.0000045")
      (web_search "0.01")
      (input_cache_read "0.000000075")
    ))
    (top_provider (
      (context_length 400000)
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
      seed
      structured_outputs
      tool_choice
      tools
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
    (knowledge_cutoff 2025-08-31)
    (expiration_date null)
    (links (
      (details /api/v1/models/~openai/gpt-mini-latest/endpoints)
    ))
    (reasoning (
      (mandatory false)
      (default_enabled false)
      (supported_efforts ([]
        xhigh
        high
        medium
        low
        none
      ))
      (default_effort medium)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id ~openai/gpt-mini-latest)
    (canonical_slug ~openai/gpt-mini-latest)
    (alias_target (
      (name "OpenAI: GPT-5.4 Mini")
      (slug openai/gpt-5.4-mini)
    ))
    (hugging_face_id null)
    (name "OpenAI GPT Mini Latest")
    (created 1777318471)
    (description "This model always redirects to the latest model in the OpenAI GPT Mini family.")
    (context_length 400000)
    (architecture (
      (modality text+image+file->text)
      (input_modalities ([]
        file
        image
        text
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Router)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.00000075")
      (completion "0.0000045")
      (web_search "0.01")
      (input_cache_read "0.000000075")
    ))
    (top_provider (
      (context_length 400000)
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
      seed
      structured_outputs
      tool_choice
      tools
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
    (knowledge_cutoff 2025-08-31)
    (expiration_date null)
    (links (
      (details /api/v1/models/~openai/gpt-mini-latest/endpoints)
    ))
    (reasoning (
      (mandatory false)
      (default_enabled false)
      (supported_efforts ([]
        xhigh
        high
        medium
        low
        none
      ))
      (default_effort medium)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId ~openai/gpt-mini-latest)
  ))
)
