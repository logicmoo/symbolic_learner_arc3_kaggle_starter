({}
  (kind model)
  (id openrouter-openai_gpt-5.4-nano_batch)
  (label "OpenAI: GPT-5.4 Nano (batch)")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model openai/gpt-5.4-nano:batch)
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
    (prompt "0.0000001")
    (completion "0.000000625")
    (web_search "0.01")
    (input_cache_read "0.00000001")
  ))
  (properties ({}
    (id openai/gpt-5.4-nano:batch)
    (canonical_slug openai/gpt-5.4-nano-20260317)
    (hugging_face_id "")
    (name "OpenAI: GPT-5.4 Nano (batch)")
    (created 1773748187)
    (description "GPT-5.4 nano is the most lightweight and cost-efficient variant of the GPT-5.4 family, optimized for speed-critical and high-volume tasks. It supports text and image inputs and is designed for low-latency...")
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
      (prompt "0.0000001")
      (completion "0.000000625")
      (web_search "0.01")
      (input_cache_read "0.00000001")
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
      (details /api/v1/models/openai/gpt-5.4-nano-20260317/endpoints)
    ))
    (benchmarks ({}
      (design_arena ())
      (artificial_analysis ({}
        (intelligence_index 39.7)
        (coding_index 56.1)
        (agentic_index 29.7)
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
    (id openai/gpt-5.4-nano:batch)
    (canonical_slug openai/gpt-5.4-nano-20260317)
    (hugging_face_id "")
    (name "OpenAI: GPT-5.4 Nano (batch)")
    (created 1773748187)
    (description "GPT-5.4 nano is the most lightweight and cost-efficient variant of the GPT-5.4 family, optimized for speed-critical and high-volume tasks. It supports text and image inputs and is designed for low-latency...")
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
      (prompt "0.0000001")
      (completion "0.000000625")
      (web_search "0.01")
      (input_cache_read "0.00000001")
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
      (details /api/v1/models/openai/gpt-5.4-nano-20260317/endpoints)
    ))
    (benchmarks ({}
      (design_arena ())
      (artificial_analysis ({}
        (intelligence_index 39.7)
        (coding_index 56.1)
        (agentic_index 29.7)
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
    (remoteModelId openai/gpt-5.4-nano:batch)
  ))
)
