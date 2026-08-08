({}
  (kind model)
  (id openrouter-z-ai_glm-4.6)
  (label "Z.ai: GLM 4.6")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model z-ai/glm-4.6)
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
    (contextWindow 204800)
    (maxOutputTokens 131072)
  ))
  (pricing ({}
    (prompt "0.0000005")
    (completion "0.000002")
    (input_cache_read "0.0000001")
  ))
  (properties ({}
    (id z-ai/glm-4.6)
    (canonical_slug z-ai/glm-4.6)
    (hugging_face_id zai-org/GLM-4.6)
    (name "Z.ai: GLM 4.6")
    (created 1759235576)
    (description "Compared with GLM-4.5, this generation brings several key improvements: Longer context window: The context window has been expanded from 128K to 200K tokens, enabling the model to handle more complex...")
    (context_length 204800)
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
      (prompt "0.0000005")
      (completion "0.000002")
      (input_cache_read "0.0000001")
    ))
    (top_provider ({}
      (context_length 202752)
      (max_completion_tokens 131072)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      include_reasoning
      logit_bias
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
      top_k
      top_p
    ))
    (default_parameters ({}
      (temperature 0.6)
      (top_p null)
      (top_k null)
      (frequency_penalty null)
      (presence_penalty null)
      (repetition_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff 2025-03-31)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/z-ai/glm-4.6/endpoints)
    ))
    (benchmarks ({}
      (design_arena (
        ({}
          (arena agents)
          (category androidnative)
          (elo 1115)
          (win_rate 52.6)
          (rank 24)
        )
        ({}
          (arena agents)
          (category fullstack)
          (elo 1073)
          (win_rate 42.3)
          (rank 29)
        )
        ({}
          (arena agents)
          (category godotgamedev)
          (elo 1180)
          (win_rate 53.2)
          (rank 13)
        )
        ({}
          (arena agents)
          (category mobileapps)
          (elo 1154)
          (win_rate 46.8)
          (rank 22)
        )
        ({}
          (arena models)
          (category 3d)
          (elo 1182)
          (win_rate 54)
          (rank 54)
        )
        ({}
          (arena models)
          (category codecategories)
          (elo 1194)
          (win_rate 54.3)
          (rank 57)
        )
        ({}
          (arena models)
          (category dataviz)
          (elo 1190)
          (win_rate 52.6)
          (rank 55)
        )
        ({}
          (arena models)
          (category gamedev)
          (elo 1191)
          (win_rate 54.7)
          (rank 52)
        )
        ({}
          (arena models)
          (category svg)
          (elo 1156)
          (win_rate 52.1)
          (rank 43)
        )
        ({}
          (arena models)
          (category uicomponent)
          (elo 1191)
          (win_rate 53.9)
          (rank 56)
        )
        ({}
          (arena models)
          (category website)
          (elo 1197)
          (win_rate 54.4)
          (rank 59)
        )
      ))
      (artificial_analysis ({}
        (intelligence_index 29.3)
        (coding_index 45.8)
        (agentic_index 18.6)
      ))
    ))
    (reasoning ({}
      (mandatory false)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id z-ai/glm-4.6)
    (canonical_slug z-ai/glm-4.6)
    (hugging_face_id zai-org/GLM-4.6)
    (name "Z.ai: GLM 4.6")
    (created 1759235576)
    (description "Compared with GLM-4.5, this generation brings several key improvements: Longer context window: The context window has been expanded from 128K to 200K tokens, enabling the model to handle more complex...")
    (context_length 204800)
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
      (prompt "0.0000005")
      (completion "0.000002")
      (input_cache_read "0.0000001")
    ))
    (top_provider ({}
      (context_length 202752)
      (max_completion_tokens 131072)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      include_reasoning
      logit_bias
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
      top_k
      top_p
    ))
    (default_parameters ({}
      (temperature 0.6)
      (top_p null)
      (top_k null)
      (frequency_penalty null)
      (presence_penalty null)
      (repetition_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff 2025-03-31)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/z-ai/glm-4.6/endpoints)
    ))
    (benchmarks ({}
      (design_arena (
        ({}
          (arena agents)
          (category androidnative)
          (elo 1115)
          (win_rate 52.6)
          (rank 24)
        )
        ({}
          (arena agents)
          (category fullstack)
          (elo 1073)
          (win_rate 42.3)
          (rank 29)
        )
        ({}
          (arena agents)
          (category godotgamedev)
          (elo 1180)
          (win_rate 53.2)
          (rank 13)
        )
        ({}
          (arena agents)
          (category mobileapps)
          (elo 1154)
          (win_rate 46.8)
          (rank 22)
        )
        ({}
          (arena models)
          (category 3d)
          (elo 1182)
          (win_rate 54)
          (rank 54)
        )
        ({}
          (arena models)
          (category codecategories)
          (elo 1194)
          (win_rate 54.3)
          (rank 57)
        )
        ({}
          (arena models)
          (category dataviz)
          (elo 1190)
          (win_rate 52.6)
          (rank 55)
        )
        ({}
          (arena models)
          (category gamedev)
          (elo 1191)
          (win_rate 54.7)
          (rank 52)
        )
        ({}
          (arena models)
          (category svg)
          (elo 1156)
          (win_rate 52.1)
          (rank 43)
        )
        ({}
          (arena models)
          (category uicomponent)
          (elo 1191)
          (win_rate 53.9)
          (rank 56)
        )
        ({}
          (arena models)
          (category website)
          (elo 1197)
          (win_rate 54.4)
          (rank 59)
        )
      ))
      (artificial_analysis ({}
        (intelligence_index 29.3)
        (coding_index 45.8)
        (agentic_index 18.6)
      ))
    ))
    (reasoning ({}
      (mandatory false)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId z-ai/glm-4.6)
  ))
)
