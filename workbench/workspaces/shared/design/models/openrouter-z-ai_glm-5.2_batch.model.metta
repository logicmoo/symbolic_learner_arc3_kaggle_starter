({}
  (kind model)
  (id openrouter-z-ai_glm-5.2_batch)
  (label "Z.ai: GLM 5.2 (batch)")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model z-ai/glm-5.2:batch)
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
    (contextWindow 512000)
    (maxOutputTokens null)
  ))
  (pricing ({}
    (prompt "0.0000007")
    (completion "0.0000022")
    (input_cache_read "0.00000013")
  ))
  (properties ({}
    (id z-ai/glm-5.2:batch)
    (canonical_slug z-ai/glm-5.2-20260616)
    (hugging_face_id zai-org/GLM-5.2)
    (name "Z.ai: GLM 5.2 (batch)")
    (created 1781631930)
    (description "GLM 5.2 is a large-scale reasoning model from Z.ai. It supports text input and output with a 1M-token context window, and is suited for long-horizon agent workflows, project-level software engineering,...")
    (context_length 512000)
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
      (prompt "0.0000007")
      (completion "0.0000022")
      (input_cache_read "0.00000013")
    ))
    (top_provider ({}
      (context_length 512000)
      (max_completion_tokens null)
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
      reasoning_effort
      repetition_penalty
      response_format
      stop
      structured_outputs
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
    (expiration_date null)
    (links ({}
      (details /api/v1/models/z-ai/glm-5.2-20260616/endpoints)
    ))
    (benchmarks ({}
      (design_arena (
        ({}
          (arena agents)
          (category agenticgamedev)
          (elo 1189)
          (win_rate 48.8)
          (rank 10)
        )
        ({}
          (arena agents)
          (category androidnative)
          (elo 1213)
          (win_rate 55.8)
          (rank 12)
        )
        ({}
          (arena agents)
          (category fullstack)
          (elo 1275)
          (win_rate 63.9)
          (rank 5)
        )
        ({}
          (arena agents)
          (category godotgamedev)
          (elo 1142)
          (win_rate 40.1)
          (rank 17)
        )
        ({}
          (arena agents)
          (category htmlslides)
          (elo 1206)
          (win_rate 51.6)
          (rank 9)
        )
        ({}
          (arena agents)
          (category mobileapps)
          (elo 1218)
          (win_rate 53.9)
          (rank 11)
        )
        ({}
          (arena agents)
          (category python-pptxslides)
          (elo 1191)
          (win_rate 48.5)
          (rank 10)
        )
        ({}
          (arena agents)
          (category webapps)
          (elo 1268)
          (win_rate 57)
          (rank 7)
        )
        ({}
          (arena models)
          (category 3d)
          (elo 1362)
          (win_rate 59.7)
          (rank 4)
        )
        ({}
          (arena models)
          (category asciiart)
          (elo 1244)
          (win_rate 50.7)
          (rank 14)
        )
        ({}
          (arena models)
          (category codecategories)
          (elo 1341)
          (win_rate 59.7)
          (rank 4)
        )
        ({}
          (arena models)
          (category dataviz)
          (elo 1327)
          (win_rate 57.2)
          (rank 6)
        )
        ({}
          (arena models)
          (category gamedev)
          (elo 1335)
          (win_rate 58.9)
          (rank 6)
        )
        ({}
          (arena models)
          (category svg)
          (elo 1260)
          (win_rate 55.3)
          (rank 11)
        )
        ({}
          (arena models)
          (category uicomponent)
          (elo 1339)
          (win_rate 58.4)
          (rank 5)
        )
        ({}
          (arena models)
          (category website)
          (elo 1336)
          (win_rate 60)
          (rank 3)
        )
      ))
      (artificial_analysis ({}
        (intelligence_index 52.6)
        (coding_index 68.8)
        (agentic_index 45.7)
      ))
    ))
    (reasoning ({}
      (mandatory false)
      (default_enabled true)
      (supported_efforts (
        xhigh
        high
      ))
      (default_effort high)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id z-ai/glm-5.2:batch)
    (canonical_slug z-ai/glm-5.2-20260616)
    (hugging_face_id zai-org/GLM-5.2)
    (name "Z.ai: GLM 5.2 (batch)")
    (created 1781631930)
    (description "GLM 5.2 is a large-scale reasoning model from Z.ai. It supports text input and output with a 1M-token context window, and is suited for long-horizon agent workflows, project-level software engineering,...")
    (context_length 512000)
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
      (prompt "0.0000007")
      (completion "0.0000022")
      (input_cache_read "0.00000013")
    ))
    (top_provider ({}
      (context_length 512000)
      (max_completion_tokens null)
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
      reasoning_effort
      repetition_penalty
      response_format
      stop
      structured_outputs
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
    (expiration_date null)
    (links ({}
      (details /api/v1/models/z-ai/glm-5.2-20260616/endpoints)
    ))
    (benchmarks ({}
      (design_arena (
        ({}
          (arena agents)
          (category agenticgamedev)
          (elo 1189)
          (win_rate 48.8)
          (rank 10)
        )
        ({}
          (arena agents)
          (category androidnative)
          (elo 1213)
          (win_rate 55.8)
          (rank 12)
        )
        ({}
          (arena agents)
          (category fullstack)
          (elo 1275)
          (win_rate 63.9)
          (rank 5)
        )
        ({}
          (arena agents)
          (category godotgamedev)
          (elo 1142)
          (win_rate 40.1)
          (rank 17)
        )
        ({}
          (arena agents)
          (category htmlslides)
          (elo 1206)
          (win_rate 51.6)
          (rank 9)
        )
        ({}
          (arena agents)
          (category mobileapps)
          (elo 1218)
          (win_rate 53.9)
          (rank 11)
        )
        ({}
          (arena agents)
          (category python-pptxslides)
          (elo 1191)
          (win_rate 48.5)
          (rank 10)
        )
        ({}
          (arena agents)
          (category webapps)
          (elo 1268)
          (win_rate 57)
          (rank 7)
        )
        ({}
          (arena models)
          (category 3d)
          (elo 1362)
          (win_rate 59.7)
          (rank 4)
        )
        ({}
          (arena models)
          (category asciiart)
          (elo 1244)
          (win_rate 50.7)
          (rank 14)
        )
        ({}
          (arena models)
          (category codecategories)
          (elo 1341)
          (win_rate 59.7)
          (rank 4)
        )
        ({}
          (arena models)
          (category dataviz)
          (elo 1327)
          (win_rate 57.2)
          (rank 6)
        )
        ({}
          (arena models)
          (category gamedev)
          (elo 1335)
          (win_rate 58.9)
          (rank 6)
        )
        ({}
          (arena models)
          (category svg)
          (elo 1260)
          (win_rate 55.3)
          (rank 11)
        )
        ({}
          (arena models)
          (category uicomponent)
          (elo 1339)
          (win_rate 58.4)
          (rank 5)
        )
        ({}
          (arena models)
          (category website)
          (elo 1336)
          (win_rate 60)
          (rank 3)
        )
      ))
      (artificial_analysis ({}
        (intelligence_index 52.6)
        (coding_index 68.8)
        (agentic_index 45.7)
      ))
    ))
    (reasoning ({}
      (mandatory false)
      (default_enabled true)
      (supported_efforts (
        xhigh
        high
      ))
      (default_effort high)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId z-ai/glm-5.2:batch)
  ))
)
