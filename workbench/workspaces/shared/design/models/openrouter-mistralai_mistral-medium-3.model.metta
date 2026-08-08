(
  (kind model)
  (id openrouter-mistralai_mistral-medium-3)
  (label "Mistral: Mistral Medium 3")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model mistralai/mistral-medium-3)
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
    (contextWindow 131072)
    (maxOutputTokens null)
  ))
  (pricing (
    (prompt "0.0000004")
    (completion "0.000002")
    (input_cache_read "0.00000004")
  ))
  (properties (
    (id mistralai/mistral-medium-3)
    (canonical_slug mistralai/mistral-medium-3)
    (hugging_face_id "")
    (name "Mistral: Mistral Medium 3")
    (created 1746627341)
    (description "Mistral Medium 3 is a high-performance enterprise-grade language model designed to deliver frontier-level capabilities at significantly reduced operational cost. It balances state-of-the-art reasoning and multimodal performance with 8× lower cost...")
    (context_length 131072)
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
      (tokenizer Mistral)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.0000004")
      (completion "0.000002")
      (input_cache_read "0.00000004")
    ))
    (top_provider (
      (context_length 131072)
      (max_completion_tokens null)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      frequency_penalty
      max_tokens
      presence_penalty
      response_format
      seed
      stop
      structured_outputs
      temperature
      tool_choice
      tools
      top_p
    ))
    (default_parameters (
      (temperature 0.3)
    ))
    (supported_voices null)
    (knowledge_cutoff 2025-03-31)
    (expiration_date null)
    (links (
      (details /api/v1/models/mistralai/mistral-medium-3/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena models)
          (category 3d)
          (elo 1137)
          (win_rate 54.7)
          (rank 69)
        )
        (
          (arena models)
          (category codecategories)
          (elo 1097)
          (win_rate 48.1)
          (rank 88)
        )
        (
          (arena models)
          (category dataviz)
          (elo 1059)
          (win_rate 45.7)
          (rank 92)
        )
        (
          (arena models)
          (category gamedev)
          (elo 1059)
          (win_rate 45.3)
          (rank 92)
        )
        (
          (arena models)
          (category uicomponent)
          (elo 1059)
          (win_rate 49.9)
          (rank 86)
        )
        (
          (arena models)
          (category website)
          (elo 1101)
          (win_rate 47.7)
          (rank 92)
        )
      ))
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id mistralai/mistral-medium-3)
    (canonical_slug mistralai/mistral-medium-3)
    (hugging_face_id "")
    (name "Mistral: Mistral Medium 3")
    (created 1746627341)
    (description "Mistral Medium 3 is a high-performance enterprise-grade language model designed to deliver frontier-level capabilities at significantly reduced operational cost. It balances state-of-the-art reasoning and multimodal performance with 8× lower cost...")
    (context_length 131072)
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
      (tokenizer Mistral)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.0000004")
      (completion "0.000002")
      (input_cache_read "0.00000004")
    ))
    (top_provider (
      (context_length 131072)
      (max_completion_tokens null)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      frequency_penalty
      max_tokens
      presence_penalty
      response_format
      seed
      stop
      structured_outputs
      temperature
      tool_choice
      tools
      top_p
    ))
    (default_parameters (
      (temperature 0.3)
    ))
    (supported_voices null)
    (knowledge_cutoff 2025-03-31)
    (expiration_date null)
    (links (
      (details /api/v1/models/mistralai/mistral-medium-3/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena models)
          (category 3d)
          (elo 1137)
          (win_rate 54.7)
          (rank 69)
        )
        (
          (arena models)
          (category codecategories)
          (elo 1097)
          (win_rate 48.1)
          (rank 88)
        )
        (
          (arena models)
          (category dataviz)
          (elo 1059)
          (win_rate 45.7)
          (rank 92)
        )
        (
          (arena models)
          (category gamedev)
          (elo 1059)
          (win_rate 45.3)
          (rank 92)
        )
        (
          (arena models)
          (category uicomponent)
          (elo 1059)
          (win_rate 49.9)
          (rank 86)
        )
        (
          (arena models)
          (category website)
          (elo 1101)
          (win_rate 47.7)
          (rank 92)
        )
      ))
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId mistralai/mistral-medium-3)
  ))
)
