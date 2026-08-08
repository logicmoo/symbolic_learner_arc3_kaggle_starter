({}
  (kind model)
  (id openrouter-openai_gpt-5-nano)
  (label "OpenAI: GPT-5 Nano")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model openai/gpt-5-nano)
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
    (prompt "0.00000005")
    (completion "0.0000004")
    (web_search "0.01")
    (input_cache_read "0.000000005")
  ))
  (properties ({}
    (id openai/gpt-5-nano)
    (canonical_slug openai/gpt-5-nano-2025-08-07)
    (hugging_face_id "")
    (name "OpenAI: GPT-5 Nano")
    (created 1754587402)
    (description "GPT-5-Nano is the smallest and fastest variant in the GPT-5 system, optimized for developer tools, rapid interactions, and ultra-low latency environments. While limited in reasoning depth compared to its larger...")
    (context_length 400000)
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
      (tokenizer GPT)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.00000005")
      (completion "0.0000004")
      (web_search "0.01")
      (input_cache_read "0.000000005")
    ))
    (top_provider ({}
      (context_length 400000)
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
    (knowledge_cutoff 2024-05-31)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/openai/gpt-5-nano-2025-08-07/endpoints)
    ))
    (benchmarks ({}
      (design_arena (
        ({}
          (arena models)
          (category 3d)
          (elo 1018)
          (win_rate 36.1)
          (rank 98)
        )
        ({}
          (arena models)
          (category codecategories)
          (elo 1112)
          (win_rate 48.1)
          (rank 84)
        )
        ({}
          (arena models)
          (category dataviz)
          (elo 1091)
          (win_rate 47.2)
          (rank 86)
        )
        ({}
          (arena models)
          (category gamedev)
          (elo 1086)
          (win_rate 46.6)
          (rank 87)
        )
        ({}
          (arena models)
          (category uicomponent)
          (elo 1100)
          (win_rate 51.9)
          (rank 81)
        )
        ({}
          (arena models)
          (category website)
          (elo 1124)
          (win_rate 48.9)
          (rank 86)
        )
      ))
    ))
    (reasoning ({}
      (mandatory true)
      (supported_efforts (
        high
        medium
        low
        minimal
      ))
      (default_effort medium)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id openai/gpt-5-nano)
    (canonical_slug openai/gpt-5-nano-2025-08-07)
    (hugging_face_id "")
    (name "OpenAI: GPT-5 Nano")
    (created 1754587402)
    (description "GPT-5-Nano is the smallest and fastest variant in the GPT-5 system, optimized for developer tools, rapid interactions, and ultra-low latency environments. While limited in reasoning depth compared to its larger...")
    (context_length 400000)
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
      (tokenizer GPT)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.00000005")
      (completion "0.0000004")
      (web_search "0.01")
      (input_cache_read "0.000000005")
    ))
    (top_provider ({}
      (context_length 400000)
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
    (knowledge_cutoff 2024-05-31)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/openai/gpt-5-nano-2025-08-07/endpoints)
    ))
    (benchmarks ({}
      (design_arena (
        ({}
          (arena models)
          (category 3d)
          (elo 1018)
          (win_rate 36.1)
          (rank 98)
        )
        ({}
          (arena models)
          (category codecategories)
          (elo 1112)
          (win_rate 48.1)
          (rank 84)
        )
        ({}
          (arena models)
          (category dataviz)
          (elo 1091)
          (win_rate 47.2)
          (rank 86)
        )
        ({}
          (arena models)
          (category gamedev)
          (elo 1086)
          (win_rate 46.6)
          (rank 87)
        )
        ({}
          (arena models)
          (category uicomponent)
          (elo 1100)
          (win_rate 51.9)
          (rank 81)
        )
        ({}
          (arena models)
          (category website)
          (elo 1124)
          (win_rate 48.9)
          (rank 86)
        )
      ))
    ))
    (reasoning ({}
      (mandatory true)
      (supported_efforts (
        high
        medium
        low
        minimal
      ))
      (default_effort medium)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId openai/gpt-5-nano)
  ))
)
