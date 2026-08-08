({}
  (kind model)
  (id openrouter-google_gemini-3-flash-preview)
  (label "Google: Gemini 3 Flash Preview")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model google/gemini-3-flash-preview)
  (enabled true)
  (capabilities ({}
    (audio true)
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
    (contextWindow 1048576)
    (maxOutputTokens 65536)
  ))
  (pricing ({}
    (prompt "0.0000005")
    (completion "0.000003")
    (image "0.0000005")
    (audio "0.000001")
    (input_audio_cache "0.0000001")
    (web_search "0.014")
    (internal_reasoning "0.000003")
    (input_cache_read "0.00000005")
    (input_cache_write "0.0000000833333333333333")
  ))
  (properties ({}
    (id google/gemini-3-flash-preview)
    (canonical_slug google/gemini-3-flash-preview-20251217)
    (hugging_face_id "")
    (name "Google: Gemini 3 Flash Preview")
    (created 1765987078)
    (description "Gemini 3 Flash Preview is a high speed, high value thinking model designed for agentic workflows, multi turn chat, and coding assistance. It delivers near Pro level reasoning and tool...")
    (context_length 1048576)
    (architecture ({}
      (modality text+image+file+audio+video->text)
      (input_modalities (
        text
        image
        file
        audio
        video
      ))
      (output_modalities (
        text
      ))
      (tokenizer Gemini)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.0000005")
      (completion "0.000003")
      (image "0.0000005")
      (audio "0.000001")
      (input_audio_cache "0.0000001")
      (web_search "0.014")
      (internal_reasoning "0.000003")
      (input_cache_read "0.00000005")
      (input_cache_write "0.0000000833333333333333")
    ))
    (top_provider ({}
      (context_length 1048576)
      (max_completion_tokens 65536)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      include_reasoning
      max_tokens
      reasoning
      reasoning_effort
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
      (temperature null)
      (top_p null)
      (top_k null)
      (frequency_penalty null)
      (presence_penalty null)
      (repetition_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/google/gemini-3-flash-preview-20251217/endpoints)
    ))
    (benchmarks ({}
      (design_arena (
        ({}
          (arena agents)
          (category agenticslides)
          (elo 1073)
          (win_rate 39.3)
          (rank 9)
        )
        ({}
          (arena agents)
          (category "agenticslides(python-pptx)")
          (elo 1075)
          (win_rate 39.3)
          (rank 9)
        )
        ({}
          (arena agents)
          (category androidnative)
          (elo 1081)
          (win_rate 48.1)
          (rank 27)
        )
        ({}
          (arena agents)
          (category fullstack)
          (elo 1104)
          (win_rate 47.1)
          (rank 22)
        )
        ({}
          (arena agents)
          (category godotgamedev)
          (elo 1161)
          (win_rate 50.6)
          (rank 14)
        )
        ({}
          (arena agents)
          (category mobileapps)
          (elo 1150)
          (win_rate 46.6)
          (rank 25)
        )
        ({}
          (arena agents)
          (category python-pptxslides)
          (elo 1019)
          (win_rate 38.3)
          (rank 19)
        )
        ({}
          (arena agents)
          (category webapps)
          (elo 1161)
          (win_rate 48.4)
          (rank 25)
        )
        ({}
          (arena models)
          (category 3d)
          (elo 1238)
          (win_rate 62.7)
          (rank 38)
        )
        ({}
          (arena models)
          (category codecategories)
          (elo 1217)
          (win_rate 57.6)
          (rank 42)
        )
        ({}
          (arena models)
          (category gamedev)
          (elo 1207)
          (win_rate 58.3)
          (rank 46)
        )
        ({}
          (arena models)
          (category website)
          (elo 1218)
          (win_rate 57)
          (rank 43)
        )
      ))
    ))
    (reasoning ({}
      (mandatory false)
      (supported_efforts (
        high
        medium
        low
        minimal
      ))
      (default_effort medium)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id google/gemini-3-flash-preview)
    (canonical_slug google/gemini-3-flash-preview-20251217)
    (hugging_face_id "")
    (name "Google: Gemini 3 Flash Preview")
    (created 1765987078)
    (description "Gemini 3 Flash Preview is a high speed, high value thinking model designed for agentic workflows, multi turn chat, and coding assistance. It delivers near Pro level reasoning and tool...")
    (context_length 1048576)
    (architecture ({}
      (modality text+image+file+audio+video->text)
      (input_modalities (
        text
        image
        file
        audio
        video
      ))
      (output_modalities (
        text
      ))
      (tokenizer Gemini)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.0000005")
      (completion "0.000003")
      (image "0.0000005")
      (audio "0.000001")
      (input_audio_cache "0.0000001")
      (web_search "0.014")
      (internal_reasoning "0.000003")
      (input_cache_read "0.00000005")
      (input_cache_write "0.0000000833333333333333")
    ))
    (top_provider ({}
      (context_length 1048576)
      (max_completion_tokens 65536)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      include_reasoning
      max_tokens
      reasoning
      reasoning_effort
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
      (temperature null)
      (top_p null)
      (top_k null)
      (frequency_penalty null)
      (presence_penalty null)
      (repetition_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/google/gemini-3-flash-preview-20251217/endpoints)
    ))
    (benchmarks ({}
      (design_arena (
        ({}
          (arena agents)
          (category agenticslides)
          (elo 1073)
          (win_rate 39.3)
          (rank 9)
        )
        ({}
          (arena agents)
          (category "agenticslides(python-pptx)")
          (elo 1075)
          (win_rate 39.3)
          (rank 9)
        )
        ({}
          (arena agents)
          (category androidnative)
          (elo 1081)
          (win_rate 48.1)
          (rank 27)
        )
        ({}
          (arena agents)
          (category fullstack)
          (elo 1104)
          (win_rate 47.1)
          (rank 22)
        )
        ({}
          (arena agents)
          (category godotgamedev)
          (elo 1161)
          (win_rate 50.6)
          (rank 14)
        )
        ({}
          (arena agents)
          (category mobileapps)
          (elo 1150)
          (win_rate 46.6)
          (rank 25)
        )
        ({}
          (arena agents)
          (category python-pptxslides)
          (elo 1019)
          (win_rate 38.3)
          (rank 19)
        )
        ({}
          (arena agents)
          (category webapps)
          (elo 1161)
          (win_rate 48.4)
          (rank 25)
        )
        ({}
          (arena models)
          (category 3d)
          (elo 1238)
          (win_rate 62.7)
          (rank 38)
        )
        ({}
          (arena models)
          (category codecategories)
          (elo 1217)
          (win_rate 57.6)
          (rank 42)
        )
        ({}
          (arena models)
          (category gamedev)
          (elo 1207)
          (win_rate 58.3)
          (rank 46)
        )
        ({}
          (arena models)
          (category website)
          (elo 1218)
          (win_rate 57)
          (rank 43)
        )
      ))
    ))
    (reasoning ({}
      (mandatory false)
      (supported_efforts (
        high
        medium
        low
        minimal
      ))
      (default_effort medium)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId google/gemini-3-flash-preview)
  ))
)
