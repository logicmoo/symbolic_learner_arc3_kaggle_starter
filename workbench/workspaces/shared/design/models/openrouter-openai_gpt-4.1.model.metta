(
  (kind model)
  (id openrouter-openai_gpt-4.1)
  (label "OpenAI: GPT-4.1")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model openai/gpt-4.1)
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
    (prompt "0.000002")
    (completion "0.000008")
    (web_search "0.01")
    (input_cache_read "0.0000005")
  ))
  (properties (
    (id openai/gpt-4.1)
    (canonical_slug openai/gpt-4.1-2025-04-14)
    (hugging_face_id "")
    (name "OpenAI: GPT-4.1")
    (created 1744651385)
    (description "GPT-4.1 is a flagship large language model optimized for advanced instruction following, real-world software engineering, and long-context reasoning. It supports a 1 million token context window and outperforms GPT-4o and...")
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
      (prompt "0.000002")
      (completion "0.000008")
      (web_search "0.01")
      (input_cache_read "0.0000005")
    ))
    (top_provider (
      (context_length 1047576)
      (max_completion_tokens 32768)
      (is_moderated true)
    ))
    (per_request_limits null)
    (supported_parameters ([]
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
    (default_parameters ())
    (supported_voices null)
    (knowledge_cutoff 2024-06-30)
    (expiration_date null)
    (links (
      (details /api/v1/models/openai/gpt-4.1-2025-04-14/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena models)
          (category 3d)
          (elo 904)
          (win_rate 30.9)
          (rank 106)
        )
        (
          (arena models)
          (category codecategories)
          (elo 1054)
          (win_rate 50.9)
          (rank 96)
        )
        (
          (arena models)
          (category dataviz)
          (elo 1131)
          (win_rate 59.5)
          (rank 75)
        )
        (
          (arena models)
          (category gamedev)
          (elo 1120)
          (win_rate 59.1)
          (rank 79)
        )
        (
          (arena models)
          (category uicomponent)
          (elo 1034)
          (win_rate 49.7)
          (rank 92)
        )
        (
          (arena models)
          (category website)
          (elo 1061)
          (win_rate 52.3)
          (rank 98)
        )
      ))
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id openai/gpt-4.1)
    (canonical_slug openai/gpt-4.1-2025-04-14)
    (hugging_face_id "")
    (name "OpenAI: GPT-4.1")
    (created 1744651385)
    (description "GPT-4.1 is a flagship large language model optimized for advanced instruction following, real-world software engineering, and long-context reasoning. It supports a 1 million token context window and outperforms GPT-4o and...")
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
      (prompt "0.000002")
      (completion "0.000008")
      (web_search "0.01")
      (input_cache_read "0.0000005")
    ))
    (top_provider (
      (context_length 1047576)
      (max_completion_tokens 32768)
      (is_moderated true)
    ))
    (per_request_limits null)
    (supported_parameters ([]
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
    (default_parameters ())
    (supported_voices null)
    (knowledge_cutoff 2024-06-30)
    (expiration_date null)
    (links (
      (details /api/v1/models/openai/gpt-4.1-2025-04-14/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena models)
          (category 3d)
          (elo 904)
          (win_rate 30.9)
          (rank 106)
        )
        (
          (arena models)
          (category codecategories)
          (elo 1054)
          (win_rate 50.9)
          (rank 96)
        )
        (
          (arena models)
          (category dataviz)
          (elo 1131)
          (win_rate 59.5)
          (rank 75)
        )
        (
          (arena models)
          (category gamedev)
          (elo 1120)
          (win_rate 59.1)
          (rank 79)
        )
        (
          (arena models)
          (category uicomponent)
          (elo 1034)
          (win_rate 49.7)
          (rank 92)
        )
        (
          (arena models)
          (category website)
          (elo 1061)
          (win_rate 52.3)
          (rank 98)
        )
      ))
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId openai/gpt-4.1)
  ))
)
