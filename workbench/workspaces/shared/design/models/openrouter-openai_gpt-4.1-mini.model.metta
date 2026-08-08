({}
  (kind model)
  (id openrouter-openai_gpt-4.1-mini)
  (label "OpenAI: GPT-4.1 Mini")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model openai/gpt-4.1-mini)
  (enabled true)
  (capabilities ({}
    (audio false)
    (code false)
    (functionCalling true)
    (json true)
    (jsonMode true)
    (local false)
    (multimodal true)
    (reasoning false)
    (text true)
    (tools true)
    (vision true)
  ))
  (limits ({}
    (contextWindow 1047576)
    (maxOutputTokens 32768)
  ))
  (pricing ({}
    (prompt "0.0000004")
    (completion "0.0000016")
    (web_search "0.01")
    (input_cache_read "0.0000001")
  ))
  (properties ({}
    (id openai/gpt-4.1-mini)
    (canonical_slug openai/gpt-4.1-mini-2025-04-14)
    (hugging_face_id "")
    (name "OpenAI: GPT-4.1 Mini")
    (created 1744651381)
    (description "GPT-4.1 Mini is a mid-sized model delivering performance competitive with GPT-4o at substantially lower latency and cost. It retains a 1 million token context window and scores 45.1% on hard...")
    (context_length 1047576)
    (architecture ({}
      (modality text+image+file->text)
      (input_modalities (
        image
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
      (prompt "0.0000004")
      (completion "0.0000016")
      (web_search "0.01")
      (input_cache_read "0.0000001")
    ))
    (top_provider ({}
      (context_length 1047576)
      (max_completion_tokens 32768)
      (is_moderated true)
    ))
    (per_request_limits null)
    (supported_parameters (
      max_completion_tokens
      max_tokens
      response_format
      seed
      structured_outputs
      temperature
      tool_choice
      tools
      top_p
    ))
    (default_parameters ({}))
    (supported_voices null)
    (knowledge_cutoff 2024-06-30)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/openai/gpt-4.1-mini-2025-04-14/endpoints)
    ))
    (benchmarks ({}
      (design_arena (
        ({}
          (arena models)
          (category 3d)
          (elo 891)
          (win_rate 30.5)
          (rank 107)
        )
        ({}
          (arena models)
          (category codecategories)
          (elo 1022)
          (win_rate 47.5)
          (rank 104)
        )
        ({}
          (arena models)
          (category dataviz)
          (elo 1061)
          (win_rate 49.2)
          (rank 91)
        )
        ({}
          (arena models)
          (category gamedev)
          (elo 1111)
          (win_rate 58.5)
          (rank 82)
        )
        ({}
          (arena models)
          (category uicomponent)
          (elo 995)
          (win_rate 45.4)
          (rank 96)
        )
        ({}
          (arena models)
          (category website)
          (elo 1020)
          (win_rate 47.8)
          (rank 106)
        )
      ))
      (artificial_analysis ({}
        (intelligence_index 14.8)
        (coding_index 20.2)
        (agentic_index 1.8)
      ))
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id openai/gpt-4.1-mini)
    (canonical_slug openai/gpt-4.1-mini-2025-04-14)
    (hugging_face_id "")
    (name "OpenAI: GPT-4.1 Mini")
    (created 1744651381)
    (description "GPT-4.1 Mini is a mid-sized model delivering performance competitive with GPT-4o at substantially lower latency and cost. It retains a 1 million token context window and scores 45.1% on hard...")
    (context_length 1047576)
    (architecture ({}
      (modality text+image+file->text)
      (input_modalities (
        image
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
      (prompt "0.0000004")
      (completion "0.0000016")
      (web_search "0.01")
      (input_cache_read "0.0000001")
    ))
    (top_provider ({}
      (context_length 1047576)
      (max_completion_tokens 32768)
      (is_moderated true)
    ))
    (per_request_limits null)
    (supported_parameters (
      max_completion_tokens
      max_tokens
      response_format
      seed
      structured_outputs
      temperature
      tool_choice
      tools
      top_p
    ))
    (default_parameters ({}))
    (supported_voices null)
    (knowledge_cutoff 2024-06-30)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/openai/gpt-4.1-mini-2025-04-14/endpoints)
    ))
    (benchmarks ({}
      (design_arena (
        ({}
          (arena models)
          (category 3d)
          (elo 891)
          (win_rate 30.5)
          (rank 107)
        )
        ({}
          (arena models)
          (category codecategories)
          (elo 1022)
          (win_rate 47.5)
          (rank 104)
        )
        ({}
          (arena models)
          (category dataviz)
          (elo 1061)
          (win_rate 49.2)
          (rank 91)
        )
        ({}
          (arena models)
          (category gamedev)
          (elo 1111)
          (win_rate 58.5)
          (rank 82)
        )
        ({}
          (arena models)
          (category uicomponent)
          (elo 995)
          (win_rate 45.4)
          (rank 96)
        )
        ({}
          (arena models)
          (category website)
          (elo 1020)
          (win_rate 47.8)
          (rank 106)
        )
      ))
      (artificial_analysis ({}
        (intelligence_index 14.8)
        (coding_index 20.2)
        (agentic_index 1.8)
      ))
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId openai/gpt-4.1-mini)
  ))
)
