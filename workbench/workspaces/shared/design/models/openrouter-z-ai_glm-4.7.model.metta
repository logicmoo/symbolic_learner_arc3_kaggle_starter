(
  (kind model)
  (id openrouter-z-ai_glm-4.7)
  (label "Z.ai: GLM 4.7")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model z-ai/glm-4.7)
  (enabled true)
  (capabilities (
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
  (limits (
    (contextWindow 204800)
    (maxOutputTokens 131072)
  ))
  (pricing (
    (prompt "0.0000004")
    (completion "0.00000175")
    (input_cache_read "0.00000008")
  ))
  (properties (
    (id z-ai/glm-4.7)
    (canonical_slug z-ai/glm-4.7-20251222)
    (hugging_face_id zai-org/GLM-4.7)
    (name "Z.ai: GLM 4.7")
    (created 1766378014)
    (description "GLM-4.7 is Z.ai’s latest flagship model, featuring upgrades in two key areas: enhanced programming capabilities and more stable multi-step reasoning/execution. It demonstrates significant improvements in executing complex agent tasks while...")
    (context_length 204800)
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
      (prompt "0.0000004")
      (completion "0.00000175")
      (input_cache_read "0.00000008")
    ))
    (top_provider (
      (context_length 202752)
      (max_completion_tokens 131072)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      frequency_penalty
      include_reasoning
      logit_bias
      logprobs
      max_tokens
      min_p
      presence_penalty
      reasoning
      repetition_penalty
      response_format
      seed
      stop
      structured_outputs
      temperature
      tool_choice
      tools
      top_a
      top_k
      top_logprobs
      top_p
    ))
    (default_parameters (
      (temperature 1)
      (top_p 0.95)
      (top_k null)
      (frequency_penalty null)
      (presence_penalty null)
      (repetition_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links (
      (details /api/v1/models/z-ai/glm-4.7-20251222/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena agents)
          (category androidnative)
          (elo 1143)
          (win_rate 56.1)
          (rank 22)
        )
        (
          (arena agents)
          (category fullstack)
          (elo 1092)
          (win_rate 44.9)
          (rank 25)
        )
        (
          (arena agents)
          (category godotgamedev)
          (elo 1058)
          (win_rate 35.8)
          (rank 28)
        )
        (
          (arena agents)
          (category mobileapps)
          (elo 1166)
          (win_rate 49)
          (rank 21)
        )
        (
          (arena models)
          (category 3d)
          (elo 1245)
          (win_rate 54.3)
          (rank 35)
        )
        (
          (arena models)
          (category asciiart)
          (elo 1203)
          (win_rate 48.1)
          (rank 22)
        )
        (
          (arena models)
          (category codecategories)
          (elo 1245)
          (win_rate 54.8)
          (rank 35)
        )
        (
          (arena models)
          (category dataviz)
          (elo 1223)
          (win_rate 51.2)
          (rank 41)
        )
        (
          (arena models)
          (category gamedev)
          (elo 1229)
          (win_rate 55.2)
          (rank 38)
        )
        (
          (arena models)
          (category svg)
          (elo 1190)
          (win_rate 54.3)
          (rank 34)
        )
        (
          (arena models)
          (category uicomponent)
          (elo 1232)
          (win_rate 51)
          (rank 38)
        )
        (
          (arena models)
          (category website)
          (elo 1248)
          (win_rate 55.3)
          (rank 35)
        )
      ))
      (artificial_analysis (
        (intelligence_index 34.5)
        (coding_index 45.3)
        (agentic_index 26.2)
      ))
    ))
    (reasoning (
      (mandatory false)
      (default_enabled true)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id z-ai/glm-4.7)
    (canonical_slug z-ai/glm-4.7-20251222)
    (hugging_face_id zai-org/GLM-4.7)
    (name "Z.ai: GLM 4.7")
    (created 1766378014)
    (description "GLM-4.7 is Z.ai’s latest flagship model, featuring upgrades in two key areas: enhanced programming capabilities and more stable multi-step reasoning/execution. It demonstrates significant improvements in executing complex agent tasks while...")
    (context_length 204800)
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
      (prompt "0.0000004")
      (completion "0.00000175")
      (input_cache_read "0.00000008")
    ))
    (top_provider (
      (context_length 202752)
      (max_completion_tokens 131072)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      frequency_penalty
      include_reasoning
      logit_bias
      logprobs
      max_tokens
      min_p
      presence_penalty
      reasoning
      repetition_penalty
      response_format
      seed
      stop
      structured_outputs
      temperature
      tool_choice
      tools
      top_a
      top_k
      top_logprobs
      top_p
    ))
    (default_parameters (
      (temperature 1)
      (top_p 0.95)
      (top_k null)
      (frequency_penalty null)
      (presence_penalty null)
      (repetition_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links (
      (details /api/v1/models/z-ai/glm-4.7-20251222/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena agents)
          (category androidnative)
          (elo 1143)
          (win_rate 56.1)
          (rank 22)
        )
        (
          (arena agents)
          (category fullstack)
          (elo 1092)
          (win_rate 44.9)
          (rank 25)
        )
        (
          (arena agents)
          (category godotgamedev)
          (elo 1058)
          (win_rate 35.8)
          (rank 28)
        )
        (
          (arena agents)
          (category mobileapps)
          (elo 1166)
          (win_rate 49)
          (rank 21)
        )
        (
          (arena models)
          (category 3d)
          (elo 1245)
          (win_rate 54.3)
          (rank 35)
        )
        (
          (arena models)
          (category asciiart)
          (elo 1203)
          (win_rate 48.1)
          (rank 22)
        )
        (
          (arena models)
          (category codecategories)
          (elo 1245)
          (win_rate 54.8)
          (rank 35)
        )
        (
          (arena models)
          (category dataviz)
          (elo 1223)
          (win_rate 51.2)
          (rank 41)
        )
        (
          (arena models)
          (category gamedev)
          (elo 1229)
          (win_rate 55.2)
          (rank 38)
        )
        (
          (arena models)
          (category svg)
          (elo 1190)
          (win_rate 54.3)
          (rank 34)
        )
        (
          (arena models)
          (category uicomponent)
          (elo 1232)
          (win_rate 51)
          (rank 38)
        )
        (
          (arena models)
          (category website)
          (elo 1248)
          (win_rate 55.3)
          (rank 35)
        )
      ))
      (artificial_analysis (
        (intelligence_index 34.5)
        (coding_index 45.3)
        (agentic_index 26.2)
      ))
    ))
    (reasoning (
      (mandatory false)
      (default_enabled true)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId z-ai/glm-4.7)
  ))
)
