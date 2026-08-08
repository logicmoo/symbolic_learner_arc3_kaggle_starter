(
  (kind model)
  (id openrouter-openai_gpt-4.1-nano_batch)
  (label "OpenAI: GPT-4.1 Nano (batch)")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model openai/gpt-4.1-nano:batch)
  (enabled true)
  (capabilities (
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
  (limits (
    (contextWindow 1047576)
    (maxOutputTokens 32768)
  ))
  (pricing (
    (prompt "0.00000005")
    (completion "0.0000002")
    (web_search "0.01")
    (input_cache_read "0.0000000125")
  ))
  (properties (
    (id openai/gpt-4.1-nano:batch)
    (canonical_slug openai/gpt-4.1-nano-2025-04-14)
    (hugging_face_id "")
    (name "OpenAI: GPT-4.1 Nano (batch)")
    (created 1744651369)
    (description "For tasks that demand low latency, GPT‑4.1 nano is the fastest and cheapest model in the GPT-4.1 series. It delivers exceptional performance at a small size with its 1 million...")
    (context_length 1047576)
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
      (prompt "0.00000005")
      (completion "0.0000002")
      (web_search "0.01")
      (input_cache_read "0.0000000125")
    ))
    (top_provider (
      (context_length 1047576)
      (max_completion_tokens 32768)
      (is_moderated true)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      max_tokens
      response_format
      seed
      structured_outputs
      temperature
      tool_choice
      tools
      top_p
    ))
    (default_parameters ())
    (supported_voices null)
    (knowledge_cutoff 2024-06-30)
    (expiration_date null)
    (links (
      (details /api/v1/models/openai/gpt-4.1-nano-2025-04-14/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena models)
          (category 3d)
          (elo 979)
          (win_rate 46)
          (rank 100)
        )
        (
          (arena models)
          (category codecategories)
          (elo 991)
          (win_rate 47.3)
          (rank 106)
        )
        (
          (arena models)
          (category dataviz)
          (elo 919)
          (win_rate 41.1)
          (rank 109)
        )
        (
          (arena models)
          (category gamedev)
          (elo 1011)
          (win_rate 49.6)
          (rank 102)
        )
        (
          (arena models)
          (category uicomponent)
          (elo 949)
          (win_rate 43.9)
          (rank 102)
        )
        (
          (arena models)
          (category website)
          (elo 995)
          (win_rate 48.1)
          (rank 109)
        )
      ))
      (artificial_analysis (
        (intelligence_index 9.6)
        (coding_index 11.1)
        (agentic_index 1.2)
      ))
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id openai/gpt-4.1-nano:batch)
    (canonical_slug openai/gpt-4.1-nano-2025-04-14)
    (hugging_face_id "")
    (name "OpenAI: GPT-4.1 Nano (batch)")
    (created 1744651369)
    (description "For tasks that demand low latency, GPT‑4.1 nano is the fastest and cheapest model in the GPT-4.1 series. It delivers exceptional performance at a small size with its 1 million...")
    (context_length 1047576)
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
      (prompt "0.00000005")
      (completion "0.0000002")
      (web_search "0.01")
      (input_cache_read "0.0000000125")
    ))
    (top_provider (
      (context_length 1047576)
      (max_completion_tokens 32768)
      (is_moderated true)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      max_tokens
      response_format
      seed
      structured_outputs
      temperature
      tool_choice
      tools
      top_p
    ))
    (default_parameters ())
    (supported_voices null)
    (knowledge_cutoff 2024-06-30)
    (expiration_date null)
    (links (
      (details /api/v1/models/openai/gpt-4.1-nano-2025-04-14/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena models)
          (category 3d)
          (elo 979)
          (win_rate 46)
          (rank 100)
        )
        (
          (arena models)
          (category codecategories)
          (elo 991)
          (win_rate 47.3)
          (rank 106)
        )
        (
          (arena models)
          (category dataviz)
          (elo 919)
          (win_rate 41.1)
          (rank 109)
        )
        (
          (arena models)
          (category gamedev)
          (elo 1011)
          (win_rate 49.6)
          (rank 102)
        )
        (
          (arena models)
          (category uicomponent)
          (elo 949)
          (win_rate 43.9)
          (rank 102)
        )
        (
          (arena models)
          (category website)
          (elo 995)
          (win_rate 48.1)
          (rank 109)
        )
      ))
      (artificial_analysis (
        (intelligence_index 9.6)
        (coding_index 11.1)
        (agentic_index 1.2)
      ))
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId openai/gpt-4.1-nano:batch)
  ))
)
