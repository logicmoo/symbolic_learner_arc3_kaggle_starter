({}
  (kind model)
  (id openrouter-z-ai_glm-5v-turbo)
  (label "Z.ai: GLM 5V Turbo")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model z-ai/glm-5v-turbo)
  (enabled true)
  (capabilities ({}
    (audio false)
    (code false)
    (functionCalling true)
    (json true)
    (jsonMode true)
    (local false)
    (multimodal true)
    (reasoning true)
    (text true)
    (tools true)
    (vision true)
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
    (id z-ai/glm-5v-turbo)
    (canonical_slug z-ai/glm-5v-turbo-20260401)
    (hugging_face_id "")
    (name "Z.ai: GLM 5V Turbo")
    (created 1775061458)
    (description "GLM-5V-Turbo is Z.ai’s first native multimodal agent foundation model, built for vision-based coding and agent-driven tasks. It natively handles image, video, and text inputs, excels at long-horizon planning, complex coding,...")
    (context_length 202752)
    (architecture ({}
      (modality text+image+video->text)
      (input_modalities (
        image
        text
        video
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
      (details /api/v1/models/z-ai/glm-5v-turbo-20260401/endpoints)
    ))
    (benchmarks ({}
      (design_arena (
        ({}
          (arena agents)
          (category agenticgamedev)
          (elo 1108)
          (win_rate 41.5)
          (rank 18)
        )
        ({}
          (arena agents)
          (category agentichtmlslides)
          (elo 1134)
          (win_rate 41.7)
          (rank 8)
        )
        ({}
          (arena agents)
          (category agenticslides)
          (elo 1171)
          (win_rate 51.6)
          (rank 6)
        )
        ({}
          (arena agents)
          (category "agenticslides(html)")
          (elo 1137)
          (win_rate 41.8)
          (rank 8)
        )
        ({}
          (arena agents)
          (category "agenticslides(python-pptx)")
          (elo 1183)
          (win_rate 53.9)
          (rank 6)
        )
        ({}
          (arena agents)
          (category androidnative)
          (elo 1267)
          (win_rate 54.8)
          (rank 4)
        )
        ({}
          (arena agents)
          (category fullstack)
          (elo 1190)
          (win_rate 52.3)
          (rank 17)
        )
        ({}
          (arena agents)
          (category godotgamedev)
          (elo 996)
          (win_rate 26.9)
          (rank 30)
        )
        ({}
          (arena agents)
          (category htmlslides)
          (elo 1152)
          (win_rate 44.5)
          (rank 18)
        )
        ({}
          (arena agents)
          (category mobileapps)
          (elo 1191)
          (win_rate 50.5)
          (rank 19)
        )
        ({}
          (arena agents)
          (category pptxslides)
          (elo 1164)
          (win_rate 52.1)
          (rank 6)
        )
        ({}
          (arena agents)
          (category python-pptxslides)
          (elo 1165)
          (win_rate 51.9)
          (rank 13)
        )
        ({}
          (arena agents)
          (category webapps)
          (elo 1172)
          (win_rate 44.6)
          (rank 23)
        )
        ({}
          (arena models)
          (category 3d)
          (elo 1264)
          (win_rate 54.2)
          (rank 30)
        )
        ({}
          (arena models)
          (category asciiart)
          (elo 1140)
          (win_rate 42.6)
          (rank 47)
        )
        ({}
          (arena models)
          (category codecategories)
          (elo 1257)
          (win_rate 51.7)
          (rank 33)
        )
        ({}
          (arena models)
          (category dataviz)
          (elo 1225)
          (win_rate 48)
          (rank 40)
        )
        ({}
          (arena models)
          (category gamedev)
          (elo 1260)
          (win_rate 53.9)
          (rank 28)
        )
        ({}
          (arena models)
          (category svg)
          (elo 1197)
          (win_rate 50.9)
          (rank 31)
        )
        ({}
          (arena models)
          (category uicomponent)
          (elo 1246)
          (win_rate 50.4)
          (rank 34)
        )
        ({}
          (arena models)
          (category website)
          (elo 1253)
          (win_rate 50.5)
          (rank 33)
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
    (id z-ai/glm-5v-turbo)
    (canonical_slug z-ai/glm-5v-turbo-20260401)
    (hugging_face_id "")
    (name "Z.ai: GLM 5V Turbo")
    (created 1775061458)
    (description "GLM-5V-Turbo is Z.ai’s first native multimodal agent foundation model, built for vision-based coding and agent-driven tasks. It natively handles image, video, and text inputs, excels at long-horizon planning, complex coding,...")
    (context_length 202752)
    (architecture ({}
      (modality text+image+video->text)
      (input_modalities (
        image
        text
        video
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
      (details /api/v1/models/z-ai/glm-5v-turbo-20260401/endpoints)
    ))
    (benchmarks ({}
      (design_arena (
        ({}
          (arena agents)
          (category agenticgamedev)
          (elo 1108)
          (win_rate 41.5)
          (rank 18)
        )
        ({}
          (arena agents)
          (category agentichtmlslides)
          (elo 1134)
          (win_rate 41.7)
          (rank 8)
        )
        ({}
          (arena agents)
          (category agenticslides)
          (elo 1171)
          (win_rate 51.6)
          (rank 6)
        )
        ({}
          (arena agents)
          (category "agenticslides(html)")
          (elo 1137)
          (win_rate 41.8)
          (rank 8)
        )
        ({}
          (arena agents)
          (category "agenticslides(python-pptx)")
          (elo 1183)
          (win_rate 53.9)
          (rank 6)
        )
        ({}
          (arena agents)
          (category androidnative)
          (elo 1267)
          (win_rate 54.8)
          (rank 4)
        )
        ({}
          (arena agents)
          (category fullstack)
          (elo 1190)
          (win_rate 52.3)
          (rank 17)
        )
        ({}
          (arena agents)
          (category godotgamedev)
          (elo 996)
          (win_rate 26.9)
          (rank 30)
        )
        ({}
          (arena agents)
          (category htmlslides)
          (elo 1152)
          (win_rate 44.5)
          (rank 18)
        )
        ({}
          (arena agents)
          (category mobileapps)
          (elo 1191)
          (win_rate 50.5)
          (rank 19)
        )
        ({}
          (arena agents)
          (category pptxslides)
          (elo 1164)
          (win_rate 52.1)
          (rank 6)
        )
        ({}
          (arena agents)
          (category python-pptxslides)
          (elo 1165)
          (win_rate 51.9)
          (rank 13)
        )
        ({}
          (arena agents)
          (category webapps)
          (elo 1172)
          (win_rate 44.6)
          (rank 23)
        )
        ({}
          (arena models)
          (category 3d)
          (elo 1264)
          (win_rate 54.2)
          (rank 30)
        )
        ({}
          (arena models)
          (category asciiart)
          (elo 1140)
          (win_rate 42.6)
          (rank 47)
        )
        ({}
          (arena models)
          (category codecategories)
          (elo 1257)
          (win_rate 51.7)
          (rank 33)
        )
        ({}
          (arena models)
          (category dataviz)
          (elo 1225)
          (win_rate 48)
          (rank 40)
        )
        ({}
          (arena models)
          (category gamedev)
          (elo 1260)
          (win_rate 53.9)
          (rank 28)
        )
        ({}
          (arena models)
          (category svg)
          (elo 1197)
          (win_rate 50.9)
          (rank 31)
        )
        ({}
          (arena models)
          (category uicomponent)
          (elo 1246)
          (win_rate 50.4)
          (rank 34)
        )
        ({}
          (arena models)
          (category website)
          (elo 1253)
          (win_rate 50.5)
          (rank 33)
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
    (remoteModelId z-ai/glm-5v-turbo)
  ))
)
