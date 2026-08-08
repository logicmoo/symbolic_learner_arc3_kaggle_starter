({}
  (kind model)
  (id openrouter-openai_o3-mini-high_batch)
  (label "OpenAI: o3 Mini High (batch)")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model openai/o3-mini-high:batch)
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
    (vision false)
  ))
  (limits ({}
    (contextWindow 200000)
    (maxOutputTokens 100000)
  ))
  (pricing ({}
    (prompt "0.00000055")
    (completion "0.0000022")
    (web_search "0.01")
    (input_cache_read "0.000000275")
  ))
  (properties ({}
    (id openai/o3-mini-high:batch)
    (canonical_slug openai/o3-mini-high-2025-01-31)
    (hugging_face_id "")
    (name "OpenAI: o3 Mini High (batch)")
    (created 1739372611)
    (description "OpenAI o3-mini-high is the same model as [o3-mini](/openai/o3-mini) with reasoning_effort set to high. o3-mini is a cost-efficient language model optimized for STEM reasoning tasks, particularly excelling in science, mathematics, and...")
    (context_length 200000)
    (architecture ({}
      (modality text+file->text)
      (input_modalities (
        text
        file
      ))
      (output_modalities (
        text
      ))
      (tokenizer GPT)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.00000055")
      (completion "0.0000022")
      (web_search "0.01")
      (input_cache_read "0.000000275")
    ))
    (top_provider ({}
      (context_length 200000)
      (max_completion_tokens 100000)
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
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff 2023-10-31)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/openai/o3-mini-high-2025-01-31/endpoints)
    ))
    (benchmarks ({}
      (design_arena ())
      (artificial_analysis ({}
        (intelligence_index 15.7)
        (coding_index 16.3)
        (agentic_index 1.7)
      ))
    ))
    (reasoning ({}
      (mandatory true)
      (supported_efforts (
        high
      ))
      (default_effort high)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id openai/o3-mini-high:batch)
    (canonical_slug openai/o3-mini-high-2025-01-31)
    (hugging_face_id "")
    (name "OpenAI: o3 Mini High (batch)")
    (created 1739372611)
    (description "OpenAI o3-mini-high is the same model as [o3-mini](/openai/o3-mini) with reasoning_effort set to high. o3-mini is a cost-efficient language model optimized for STEM reasoning tasks, particularly excelling in science, mathematics, and...")
    (context_length 200000)
    (architecture ({}
      (modality text+file->text)
      (input_modalities (
        text
        file
      ))
      (output_modalities (
        text
      ))
      (tokenizer GPT)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.00000055")
      (completion "0.0000022")
      (web_search "0.01")
      (input_cache_read "0.000000275")
    ))
    (top_provider ({}
      (context_length 200000)
      (max_completion_tokens 100000)
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
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff 2023-10-31)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/openai/o3-mini-high-2025-01-31/endpoints)
    ))
    (benchmarks ({}
      (design_arena ())
      (artificial_analysis ({}
        (intelligence_index 15.7)
        (coding_index 16.3)
        (agentic_index 1.7)
      ))
    ))
    (reasoning ({}
      (mandatory true)
      (supported_efforts (
        high
      ))
      (default_effort high)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId openai/o3-mini-high:batch)
  ))
)
