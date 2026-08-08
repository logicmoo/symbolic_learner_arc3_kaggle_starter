(
  (kind model)
  (id openrouter-z-ai_glm-4.5-air)
  (label "Z.ai: GLM 4.5 Air")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model z-ai/glm-4.5-air)
  (enabled true)
  (capabilities (
    (audio false)
    (code false)
    (functionCalling true)
    (json false)
    (jsonMode false)
    (local false)
    (multimodal false)
    (reasoning true)
    (text true)
    (tools true)
    (vision false)
  ))
  (limits (
    (contextWindow 131072)
    (maxOutputTokens 98304)
  ))
  (pricing (
    (prompt "0.00000013")
    (completion "0.00000085")
    (input_cache_read "0.000000025")
  ))
  (properties (
    (id z-ai/glm-4.5-air)
    (canonical_slug z-ai/glm-4.5-air)
    (hugging_face_id zai-org/GLM-4.5-Air)
    (name "Z.ai: GLM 4.5 Air")
    (created 1753471258)
    (description "GLM-4.5-Air is the lightweight variant of our latest flagship model family, also purpose-built for agent-centric applications. Like GLM-4.5, it adopts the Mixture-of-Experts (MoE) architecture but with a more compact parameter...")
    (context_length 131072)
    (architecture (
      (modality text->text)
      (input_modalities ([]
        text
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Other)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.00000013")
      (completion "0.00000085")
      (input_cache_read "0.000000025")
    ))
    (top_provider (
      (context_length 131072)
      (max_completion_tokens 98304)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      frequency_penalty
      include_reasoning
      max_tokens
      presence_penalty
      reasoning
      repetition_penalty
      seed
      stop
      temperature
      tool_choice
      tools
      top_k
      top_p
    ))
    (default_parameters (
      (temperature 0.75)
      (top_p null)
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff 2024-12-31)
    (expiration_date null)
    (links (
      (details /api/v1/models/z-ai/glm-4.5-air/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena models)
          (category 3d)
          (elo 1176)
          (win_rate 54.1)
          (rank 56)
        )
        (
          (arena models)
          (category codecategories)
          (elo 1165)
          (win_rate 51.5)
          (rank 68)
        )
        (
          (arena models)
          (category dataviz)
          (elo 1218)
          (win_rate 59.2)
          (rank 42)
        )
        (
          (arena models)
          (category gamedev)
          (elo 1135)
          (win_rate 48.4)
          (rank 72)
        )
        (
          (arena models)
          (category svg)
          (elo 1118)
          (win_rate 50.8)
          (rank 52)
        )
        (
          (arena models)
          (category uicomponent)
          (elo 1157)
          (win_rate 54.5)
          (rank 65)
        )
        (
          (arena models)
          (category website)
          (elo 1169)
          (win_rate 51.3)
          (rank 68)
        )
      ))
    ))
    (reasoning (
      (mandatory false)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id z-ai/glm-4.5-air)
    (canonical_slug z-ai/glm-4.5-air)
    (hugging_face_id zai-org/GLM-4.5-Air)
    (name "Z.ai: GLM 4.5 Air")
    (created 1753471258)
    (description "GLM-4.5-Air is the lightweight variant of our latest flagship model family, also purpose-built for agent-centric applications. Like GLM-4.5, it adopts the Mixture-of-Experts (MoE) architecture but with a more compact parameter...")
    (context_length 131072)
    (architecture (
      (modality text->text)
      (input_modalities ([]
        text
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Other)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.00000013")
      (completion "0.00000085")
      (input_cache_read "0.000000025")
    ))
    (top_provider (
      (context_length 131072)
      (max_completion_tokens 98304)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      frequency_penalty
      include_reasoning
      max_tokens
      presence_penalty
      reasoning
      repetition_penalty
      seed
      stop
      temperature
      tool_choice
      tools
      top_k
      top_p
    ))
    (default_parameters (
      (temperature 0.75)
      (top_p null)
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff 2024-12-31)
    (expiration_date null)
    (links (
      (details /api/v1/models/z-ai/glm-4.5-air/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena models)
          (category 3d)
          (elo 1176)
          (win_rate 54.1)
          (rank 56)
        )
        (
          (arena models)
          (category codecategories)
          (elo 1165)
          (win_rate 51.5)
          (rank 68)
        )
        (
          (arena models)
          (category dataviz)
          (elo 1218)
          (win_rate 59.2)
          (rank 42)
        )
        (
          (arena models)
          (category gamedev)
          (elo 1135)
          (win_rate 48.4)
          (rank 72)
        )
        (
          (arena models)
          (category svg)
          (elo 1118)
          (win_rate 50.8)
          (rank 52)
        )
        (
          (arena models)
          (category uicomponent)
          (elo 1157)
          (win_rate 54.5)
          (rank 65)
        )
        (
          (arena models)
          (category website)
          (elo 1169)
          (win_rate 51.3)
          (rank 68)
        )
      ))
    ))
    (reasoning (
      (mandatory false)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId z-ai/glm-4.5-air)
  ))
)
