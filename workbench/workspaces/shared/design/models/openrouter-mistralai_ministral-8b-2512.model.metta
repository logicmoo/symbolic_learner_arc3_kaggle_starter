({}
  (kind model)
  (id openrouter-mistralai_ministral-8b-2512)
  (label "Mistral: Ministral 3 8B 2512")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model mistralai/ministral-8b-2512)
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
    (contextWindow 262144)
    (maxOutputTokens null)
  ))
  (pricing ({}
    (prompt "0.00000015")
    (completion "0.00000015")
    (input_cache_read "0.000000015")
  ))
  (properties ({}
    (id mistralai/ministral-8b-2512)
    (canonical_slug mistralai/ministral-8b-2512)
    (hugging_face_id mistralai/Ministral-3-8B-Instruct-2512)
    (name "Mistral: Ministral 3 8B 2512")
    (created 1764681654)
    (description "A balanced model in the Ministral 3 family, Ministral 3 8B is a powerful, efficient tiny language model with vision capabilities.")
    (context_length 262144)
    (architecture ({}
      (modality text+image->text)
      (input_modalities (
        text
        image
      ))
      (output_modalities (
        text
      ))
      (tokenizer Mistral)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.00000015")
      (completion "0.00000015")
      (input_cache_read "0.000000015")
    ))
    (top_provider ({}
      (context_length 262144)
      (max_completion_tokens null)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
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
    (default_parameters ({}
      (temperature 0.3)
      (top_p null)
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/mistralai/ministral-8b-2512/endpoints)
    ))
    (benchmarks ({}
      (design_arena (
        ({}
          (arena models)
          (category 3d)
          (elo 1086)
          (win_rate 46.2)
          (rank 86)
        )
        ({}
          (arena models)
          (category codecategories)
          (elo 1081)
          (win_rate 42.9)
          (rank 90)
        )
        ({}
          (arena models)
          (category gamedev)
          (elo 1031)
          (win_rate 38.7)
          (rank 98)
        )
        ({}
          (arena models)
          (category website)
          (elo 1087)
          (win_rate 42.9)
          (rank 93)
        )
      ))
      (artificial_analysis ({}
        (intelligence_index 9)
        (coding_index 9.7)
        (agentic_index 1.2)
      ))
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id mistralai/ministral-8b-2512)
    (canonical_slug mistralai/ministral-8b-2512)
    (hugging_face_id mistralai/Ministral-3-8B-Instruct-2512)
    (name "Mistral: Ministral 3 8B 2512")
    (created 1764681654)
    (description "A balanced model in the Ministral 3 family, Ministral 3 8B is a powerful, efficient tiny language model with vision capabilities.")
    (context_length 262144)
    (architecture ({}
      (modality text+image->text)
      (input_modalities (
        text
        image
      ))
      (output_modalities (
        text
      ))
      (tokenizer Mistral)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.00000015")
      (completion "0.00000015")
      (input_cache_read "0.000000015")
    ))
    (top_provider ({}
      (context_length 262144)
      (max_completion_tokens null)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
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
    (default_parameters ({}
      (temperature 0.3)
      (top_p null)
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/mistralai/ministral-8b-2512/endpoints)
    ))
    (benchmarks ({}
      (design_arena (
        ({}
          (arena models)
          (category 3d)
          (elo 1086)
          (win_rate 46.2)
          (rank 86)
        )
        ({}
          (arena models)
          (category codecategories)
          (elo 1081)
          (win_rate 42.9)
          (rank 90)
        )
        ({}
          (arena models)
          (category gamedev)
          (elo 1031)
          (win_rate 38.7)
          (rank 98)
        )
        ({}
          (arena models)
          (category website)
          (elo 1087)
          (win_rate 42.9)
          (rank 93)
        )
      ))
      (artificial_analysis ({}
        (intelligence_index 9)
        (coding_index 9.7)
        (agentic_index 1.2)
      ))
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId mistralai/ministral-8b-2512)
  ))
)
