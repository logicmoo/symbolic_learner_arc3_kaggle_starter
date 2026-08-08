(
  (kind model)
  (id openrouter-z-ai_glm-5.1)
  (label "Z.ai: GLM 5.1")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model z-ai/glm-5.1)
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
    (prompt "0.000000952")
    (completion "0.000002992")
    (input_cache_read "0.0000001768")
  ))
  (properties (
    (id z-ai/glm-5.1)
    (canonical_slug z-ai/glm-5.1-20260406)
    (hugging_face_id zai-org/GLM-5.1)
    (name "Z.ai: GLM 5.1")
    (created 1775578025)
    (description "GLM-5.1 delivers a major leap in coding capability, with particularly significant gains in handling long-horizon tasks. Unlike previous models built around minute-level interactions, GLM-5.1 can work independently and continuously on...")
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
      (prompt "0.000000952")
      (completion "0.000002992")
      (input_cache_read "0.0000001768")
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
      (details /api/v1/models/z-ai/glm-5.1-20260406/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena models)
          (category 3d)
          (elo 1336)
          (win_rate 62.6)
          (rank 6)
        )
        (
          (arena models)
          (category asciiart)
          (elo 1186)
          (win_rate 47.3)
          (rank 31)
        )
        (
          (arena models)
          (category codecategories)
          (elo 1302)
          (win_rate 56.5)
          (rank 14)
        )
        (
          (arena models)
          (category dataviz)
          (elo 1366)
          (win_rate 67)
          (rank 3)
        )
        (
          (arena models)
          (category gamedev)
          (elo 1303)
          (win_rate 58.7)
          (rank 14)
        )
        (
          (arena models)
          (category svg)
          (elo 1267)
          (win_rate 59.2)
          (rank 8)
        )
        (
          (arena models)
          (category uicomponent)
          (elo 1306)
          (win_rate 55.9)
          (rank 14)
        )
        (
          (arena models)
          (category website)
          (elo 1294)
          (win_rate 55.1)
          (rank 17)
        )
        (
          (arena agents)
          (category agenticgamedev)
          (elo 1178)
          (win_rate 50.8)
          (rank 14)
        )
        (
          (arena agents)
          (category agentichtmlslides)
          (elo 1205)
          (win_rate 52)
          (rank 6)
        )
        (
          (arena agents)
          (category agenticslides)
          (elo 1245)
          (win_rate 54.4)
          (rank 3)
        )
        (
          (arena agents)
          (category "agenticslides(html)")
          (elo 1204)
          (win_rate 51.8)
          (rank 6)
        )
        (
          (arena agents)
          (category "agenticslides(python-pptx)")
          (elo 1240)
          (win_rate 53.3)
          (rank 4)
        )
        (
          (arena agents)
          (category androidnative)
          (elo 1216)
          (win_rate 53.7)
          (rank 11)
        )
        (
          (arena agents)
          (category fullstack)
          (elo 1208)
          (win_rate 55.9)
          (rank 13)
        )
        (
          (arena agents)
          (category godotgamedev)
          (elo 1104)
          (win_rate 39.5)
          (rank 25)
        )
        (
          (arena agents)
          (category htmlslides)
          (elo 1203)
          (win_rate 51.4)
          (rank 12)
        )
        (
          (arena agents)
          (category mobileapps)
          (elo 1217)
          (win_rate 54.6)
          (rank 12)
        )
        (
          (arena agents)
          (category pptxslides)
          (elo 1241)
          (win_rate 53.5)
          (rank 4)
        )
        (
          (arena agents)
          (category python-pptxslides)
          (elo 1258)
          (win_rate 54.2)
          (rank 5)
        )
        (
          (arena agents)
          (category webapps)
          (elo 1226)
          (win_rate 53.7)
          (rank 17)
        )
      ))
      (artificial_analysis (
        (intelligence_index 41)
        (coding_index 55.8)
        (agentic_index 30.6)
      ))
    ))
    (reasoning (
      (mandatory false)
      (default_enabled true)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id z-ai/glm-5.1)
    (canonical_slug z-ai/glm-5.1-20260406)
    (hugging_face_id zai-org/GLM-5.1)
    (name "Z.ai: GLM 5.1")
    (created 1775578025)
    (description "GLM-5.1 delivers a major leap in coding capability, with particularly significant gains in handling long-horizon tasks. Unlike previous models built around minute-level interactions, GLM-5.1 can work independently and continuously on...")
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
      (prompt "0.000000952")
      (completion "0.000002992")
      (input_cache_read "0.0000001768")
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
      (details /api/v1/models/z-ai/glm-5.1-20260406/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena models)
          (category 3d)
          (elo 1336)
          (win_rate 62.6)
          (rank 6)
        )
        (
          (arena models)
          (category asciiart)
          (elo 1186)
          (win_rate 47.3)
          (rank 31)
        )
        (
          (arena models)
          (category codecategories)
          (elo 1302)
          (win_rate 56.5)
          (rank 14)
        )
        (
          (arena models)
          (category dataviz)
          (elo 1366)
          (win_rate 67)
          (rank 3)
        )
        (
          (arena models)
          (category gamedev)
          (elo 1303)
          (win_rate 58.7)
          (rank 14)
        )
        (
          (arena models)
          (category svg)
          (elo 1267)
          (win_rate 59.2)
          (rank 8)
        )
        (
          (arena models)
          (category uicomponent)
          (elo 1306)
          (win_rate 55.9)
          (rank 14)
        )
        (
          (arena models)
          (category website)
          (elo 1294)
          (win_rate 55.1)
          (rank 17)
        )
        (
          (arena agents)
          (category agenticgamedev)
          (elo 1178)
          (win_rate 50.8)
          (rank 14)
        )
        (
          (arena agents)
          (category agentichtmlslides)
          (elo 1205)
          (win_rate 52)
          (rank 6)
        )
        (
          (arena agents)
          (category agenticslides)
          (elo 1245)
          (win_rate 54.4)
          (rank 3)
        )
        (
          (arena agents)
          (category "agenticslides(html)")
          (elo 1204)
          (win_rate 51.8)
          (rank 6)
        )
        (
          (arena agents)
          (category "agenticslides(python-pptx)")
          (elo 1240)
          (win_rate 53.3)
          (rank 4)
        )
        (
          (arena agents)
          (category androidnative)
          (elo 1216)
          (win_rate 53.7)
          (rank 11)
        )
        (
          (arena agents)
          (category fullstack)
          (elo 1208)
          (win_rate 55.9)
          (rank 13)
        )
        (
          (arena agents)
          (category godotgamedev)
          (elo 1104)
          (win_rate 39.5)
          (rank 25)
        )
        (
          (arena agents)
          (category htmlslides)
          (elo 1203)
          (win_rate 51.4)
          (rank 12)
        )
        (
          (arena agents)
          (category mobileapps)
          (elo 1217)
          (win_rate 54.6)
          (rank 12)
        )
        (
          (arena agents)
          (category pptxslides)
          (elo 1241)
          (win_rate 53.5)
          (rank 4)
        )
        (
          (arena agents)
          (category python-pptxslides)
          (elo 1258)
          (win_rate 54.2)
          (rank 5)
        )
        (
          (arena agents)
          (category webapps)
          (elo 1226)
          (win_rate 53.7)
          (rank 17)
        )
      ))
      (artificial_analysis (
        (intelligence_index 41)
        (coding_index 55.8)
        (agentic_index 30.6)
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
    (remoteModelId z-ai/glm-5.1)
  ))
)
