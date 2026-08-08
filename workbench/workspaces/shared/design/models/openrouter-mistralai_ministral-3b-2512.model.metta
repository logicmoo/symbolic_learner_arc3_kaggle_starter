(
  (kind model)
  (id openrouter-mistralai_ministral-3b-2512)
  (label "Mistral: Ministral 3 3B 2512")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model mistralai/ministral-3b-2512)
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
    (prompt "0.0000001")
    (completion "0.0000001")
    (input_cache_read "0.00000001")
  ))
  (properties (
    (id mistralai/ministral-3b-2512)
    (canonical_slug mistralai/ministral-3b-2512)
    (hugging_face_id mistralai/Ministral-3-3B-Instruct-2512)
    (name "Mistral: Ministral 3 3B 2512")
    (created 1764681560)
    (description "The smallest model in the Ministral 3 family, Ministral 3 3B is a powerful, efficient tiny language model with vision capabilities.")
    (context_length 131072)
    (architecture (
      (modality text+image->text)
      (input_modalities ([]
        text
        image
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Mistral)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.0000001")
      (completion "0.0000001")
      (input_cache_read "0.00000001")
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
      (top_p null)
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links (
      (details /api/v1/models/mistralai/ministral-3b-2512/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena models)
          (category 3d)
          (elo 1017)
          (win_rate 35.9)
          (rank 99)
        )
        (
          (arena models)
          (category codecategories)
          (elo 1038)
          (win_rate 37.3)
          (rank 99)
        )
        (
          (arena models)
          (category gamedev)
          (elo 989)
          (win_rate 33)
          (rank 106)
        )
        (
          (arena models)
          (category website)
          (elo 1050)
          (win_rate 38.2)
          (rank 102)
        )
      ))
      (artificial_analysis (
        (intelligence_index 7.1)
        (coding_index 4.8)
        (agentic_index 1.6)
      ))
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id mistralai/ministral-3b-2512)
    (canonical_slug mistralai/ministral-3b-2512)
    (hugging_face_id mistralai/Ministral-3-3B-Instruct-2512)
    (name "Mistral: Ministral 3 3B 2512")
    (created 1764681560)
    (description "The smallest model in the Ministral 3 family, Ministral 3 3B is a powerful, efficient tiny language model with vision capabilities.")
    (context_length 131072)
    (architecture (
      (modality text+image->text)
      (input_modalities ([]
        text
        image
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Mistral)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.0000001")
      (completion "0.0000001")
      (input_cache_read "0.00000001")
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
      (top_p null)
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links (
      (details /api/v1/models/mistralai/ministral-3b-2512/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena models)
          (category 3d)
          (elo 1017)
          (win_rate 35.9)
          (rank 99)
        )
        (
          (arena models)
          (category codecategories)
          (elo 1038)
          (win_rate 37.3)
          (rank 99)
        )
        (
          (arena models)
          (category gamedev)
          (elo 989)
          (win_rate 33)
          (rank 106)
        )
        (
          (arena models)
          (category website)
          (elo 1050)
          (win_rate 38.2)
          (rank 102)
        )
      ))
      (artificial_analysis (
        (intelligence_index 7.1)
        (coding_index 4.8)
        (agentic_index 1.6)
      ))
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId mistralai/ministral-3b-2512)
  ))
)
