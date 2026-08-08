({}
  (kind model)
  (id openrouter-openai_gpt-5.4-mini_batch)
  (label "OpenAI: GPT-5.4 Mini (batch)")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model openai/gpt-5.4-mini:batch)
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
    (contextWindow 400000)
    (maxOutputTokens 128000)
  ))
  (pricing ({}
    (prompt "0.000000375")
    (completion "0.00000225")
    (web_search "0.01")
    (input_cache_read "0.0000000375")
  ))
  (properties ({}
    (id openai/gpt-5.4-mini:batch)
    (canonical_slug openai/gpt-5.4-mini-20260317)
    (hugging_face_id "")
    (name "OpenAI: GPT-5.4 Mini (batch)")
    (created 1773748178)
    (description "GPT-5.4 mini brings the core capabilities of GPT-5.4 to a faster, more efficient model optimized for high-throughput workloads. It supports text and image inputs with strong performance across reasoning, coding,...")
    (context_length 400000)
    (architecture ({}
      (modality text+image+file->text)
      (input_modalities (
        file
        image
        text
      ))
      (output_modalities (
        text
      ))
      (tokenizer GPT)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.000000375")
      (completion "0.00000225")
      (web_search "0.01")
      (input_cache_read "0.0000000375")
    ))
    (top_provider ({}
      (context_length 400000)
      (max_completion_tokens 128000)
      (is_moderated true)
    ))
    (per_request_limits null)
    (supported_parameters (
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
    (default_parameters ({}
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
    (links ({}
      (details /api/v1/models/openai/gpt-5.4-mini-20260317/endpoints)
    ))
    (benchmarks ({}
      (design_arena ())
      (artificial_analysis ({}
        (intelligence_index 40.9)
        (coding_index 56.1)
        (agentic_index 31.5)
      ))
    ))
    (reasoning ({}
      (mandatory false)
      (default_enabled false)
      (supported_efforts (
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
  (providerMetadata ({}
    (id openai/gpt-5.4-mini:batch)
    (canonical_slug openai/gpt-5.4-mini-20260317)
    (hugging_face_id "")
    (name "OpenAI: GPT-5.4 Mini (batch)")
    (created 1773748178)
    (description "GPT-5.4 mini brings the core capabilities of GPT-5.4 to a faster, more efficient model optimized for high-throughput workloads. It supports text and image inputs with strong performance across reasoning, coding,...")
    (context_length 400000)
    (architecture ({}
      (modality text+image+file->text)
      (input_modalities (
        file
        image
        text
      ))
      (output_modalities (
        text
      ))
      (tokenizer GPT)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.000000375")
      (completion "0.00000225")
      (web_search "0.01")
      (input_cache_read "0.0000000375")
    ))
    (top_provider ({}
      (context_length 400000)
      (max_completion_tokens 128000)
      (is_moderated true)
    ))
    (per_request_limits null)
    (supported_parameters (
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
    (default_parameters ({}
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
    (links ({}
      (details /api/v1/models/openai/gpt-5.4-mini-20260317/endpoints)
    ))
    (benchmarks ({}
      (design_arena ())
      (artificial_analysis ({}
        (intelligence_index 40.9)
        (coding_index 56.1)
        (agentic_index 31.5)
      ))
    ))
    (reasoning ({}
      (mandatory false)
      (default_enabled false)
      (supported_efforts (
        xhigh
        high
        medium
        low
        none
      ))
      (default_effort medium)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId openai/gpt-5.4-mini:batch)
  ))
)
