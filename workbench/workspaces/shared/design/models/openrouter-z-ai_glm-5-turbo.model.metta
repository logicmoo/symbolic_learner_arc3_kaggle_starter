({}
  (kind model)
  (id openrouter-z-ai_glm-5-turbo)
  (label "Z.ai: GLM 5 Turbo")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model z-ai/glm-5-turbo)
  (enabled true)
  (capabilities ({}
    (audio false)
    (code false)
    (functionCalling true)
    (json true)
    (jsonMode true)
    (local false)
    (multimodal false)
    (reasoning true)
    (text true)
    (tools true)
    (vision false)
  ))
  (limits ({}
    (contextWindow 202752)
    (maxOutputTokens 131072)
  ))
  (pricing ({}
    (prompt "0.0000012")
    (completion "0.000004")
    (input_cache_read "0.00000024")
  ))
  (properties ({}
    (id z-ai/glm-5-turbo)
    (canonical_slug z-ai/glm-5-turbo-20260315)
    (hugging_face_id "")
    (name "Z.ai: GLM 5 Turbo")
    (created 1773583573)
    (description "GLM-5 Turbo is a new model from Z.ai designed for fast inference and strong performance in agent-driven environments such as OpenClaw scenarios. It is deeply optimized for real-world agent workflows...")
    (context_length 202752)
    (architecture ({}
      (modality text->text)
      (input_modalities (
        text
      ))
      (output_modalities (
        text
      ))
      (tokenizer Other)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.0000012")
      (completion "0.000004")
      (input_cache_read "0.00000024")
    ))
    (top_provider ({}
      (context_length 202752)
      (max_completion_tokens 131072)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      include_reasoning
      max_tokens
      reasoning
      response_format
      temperature
      tool_choice
      tools
      top_k
      top_p
    ))
    (default_parameters ({}
      (temperature 1)
      (top_p 0.95)
      (top_k null)
      (frequency_penalty null)
      (presence_penalty null)
      (repetition_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date 2098-12-31)
    (links ({}
      (details /api/v1/models/z-ai/glm-5-turbo-20260315/endpoints)
    ))
    (benchmarks ({}
      (design_arena (
        ({}
          (arena models)
          (category 3d)
          (elo 1304)
          (win_rate 58.2)
          (rank 14)
        )
        ({}
          (arena models)
          (category asciiart)
          (elo 1191)
          (win_rate 50)
          (rank 25)
        )
        ({}
          (arena models)
          (category codecategories)
          (elo 1296)
          (win_rate 56.3)
          (rank 16)
        )
        ({}
          (arena models)
          (category dataviz)
          (elo 1291)
          (win_rate 57.3)
          (rank 15)
        )
        ({}
          (arena models)
          (category gamedev)
          (elo 1295)
          (win_rate 57.4)
          (rank 17)
        )
        ({}
          (arena models)
          (category svg)
          (elo 1254)
          (win_rate 57)
          (rank 12)
        )
        ({}
          (arena models)
          (category uicomponent)
          (elo 1296)
          (win_rate 57.1)
          (rank 17)
        )
        ({}
          (arena models)
          (category website)
          (elo 1293)
          (win_rate 55.5)
          (rank 18)
        )
      ))
    ))
    (reasoning ({}
      (mandatory false)
      (default_enabled true)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id z-ai/glm-5-turbo)
    (canonical_slug z-ai/glm-5-turbo-20260315)
    (hugging_face_id "")
    (name "Z.ai: GLM 5 Turbo")
    (created 1773583573)
    (description "GLM-5 Turbo is a new model from Z.ai designed for fast inference and strong performance in agent-driven environments such as OpenClaw scenarios. It is deeply optimized for real-world agent workflows...")
    (context_length 202752)
    (architecture ({}
      (modality text->text)
      (input_modalities (
        text
      ))
      (output_modalities (
        text
      ))
      (tokenizer Other)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.0000012")
      (completion "0.000004")
      (input_cache_read "0.00000024")
    ))
    (top_provider ({}
      (context_length 202752)
      (max_completion_tokens 131072)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      include_reasoning
      max_tokens
      reasoning
      response_format
      temperature
      tool_choice
      tools
      top_k
      top_p
    ))
    (default_parameters ({}
      (temperature 1)
      (top_p 0.95)
      (top_k null)
      (frequency_penalty null)
      (presence_penalty null)
      (repetition_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date 2098-12-31)
    (links ({}
      (details /api/v1/models/z-ai/glm-5-turbo-20260315/endpoints)
    ))
    (benchmarks ({}
      (design_arena (
        ({}
          (arena models)
          (category 3d)
          (elo 1304)
          (win_rate 58.2)
          (rank 14)
        )
        ({}
          (arena models)
          (category asciiart)
          (elo 1191)
          (win_rate 50)
          (rank 25)
        )
        ({}
          (arena models)
          (category codecategories)
          (elo 1296)
          (win_rate 56.3)
          (rank 16)
        )
        ({}
          (arena models)
          (category dataviz)
          (elo 1291)
          (win_rate 57.3)
          (rank 15)
        )
        ({}
          (arena models)
          (category gamedev)
          (elo 1295)
          (win_rate 57.4)
          (rank 17)
        )
        ({}
          (arena models)
          (category svg)
          (elo 1254)
          (win_rate 57)
          (rank 12)
        )
        ({}
          (arena models)
          (category uicomponent)
          (elo 1296)
          (win_rate 57.1)
          (rank 17)
        )
        ({}
          (arena models)
          (category website)
          (elo 1293)
          (win_rate 55.5)
          (rank 18)
        )
      ))
    ))
    (reasoning ({}
      (mandatory false)
      (default_enabled true)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId z-ai/glm-5-turbo)
  ))
)
