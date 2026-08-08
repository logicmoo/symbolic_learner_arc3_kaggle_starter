(
  (kind model)
  (id openrouter-openai_o4-mini-high_batch)
  (label "OpenAI: o4 Mini High (batch)")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model openai/o4-mini-high:batch)
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
    (maxOutputTokens 100000)
  ))
  (pricing (
    (prompt "0.00000055")
    (completion "0.0000022")
    (web_search "0.01")
    (input_cache_read "0.0000001375")
  ))
  (properties (
    (id openai/o4-mini-high:batch)
    (canonical_slug openai/o4-mini-high-2025-04-16)
    (hugging_face_id "")
    (name "OpenAI: o4 Mini High (batch)")
    (created 1744824212)
    (description "OpenAI o4-mini-high is the same model as [o4-mini](/openai/o4-mini) with reasoning_effort set to high. OpenAI o4-mini is a compact reasoning model in the o-series, optimized for fast, cost-efficient performance while retaining...")
    (context_length 200000)
    (architecture (
      (modality text+image+file->text)
      (input_modalities ([]
        image
        text
        file
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer GPT)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.00000055")
      (completion "0.0000022")
      (web_search "0.01")
      (input_cache_read "0.0000001375")
    ))
    (top_provider (
      (context_length 200000)
      (max_completion_tokens 100000)
      (is_moderated true)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      include_reasoning
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
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff 2024-06-30)
    (expiration_date null)
    (links (
      (details /api/v1/models/openai/o4-mini-high-2025-04-16/endpoints)
    ))
    (reasoning (
      (mandatory true)
      (supported_efforts ([]
        high
      ))
      (default_effort high)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id openai/o4-mini-high:batch)
    (canonical_slug openai/o4-mini-high-2025-04-16)
    (hugging_face_id "")
    (name "OpenAI: o4 Mini High (batch)")
    (created 1744824212)
    (description "OpenAI o4-mini-high is the same model as [o4-mini](/openai/o4-mini) with reasoning_effort set to high. OpenAI o4-mini is a compact reasoning model in the o-series, optimized for fast, cost-efficient performance while retaining...")
    (context_length 200000)
    (architecture (
      (modality text+image+file->text)
      (input_modalities ([]
        image
        text
        file
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer GPT)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.00000055")
      (completion "0.0000022")
      (web_search "0.01")
      (input_cache_read "0.0000001375")
    ))
    (top_provider (
      (context_length 200000)
      (max_completion_tokens 100000)
      (is_moderated true)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      include_reasoning
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
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff 2024-06-30)
    (expiration_date null)
    (links (
      (details /api/v1/models/openai/o4-mini-high-2025-04-16/endpoints)
    ))
    (reasoning (
      (mandatory true)
      (supported_efforts ([]
        high
      ))
      (default_effort high)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId openai/o4-mini-high:batch)
  ))
)
