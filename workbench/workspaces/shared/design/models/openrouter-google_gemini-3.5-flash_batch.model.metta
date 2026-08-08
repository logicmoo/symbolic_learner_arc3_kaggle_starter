(
  (kind model)
  (id openrouter-google_gemini-3.5-flash_batch)
  (label "Google: Gemini 3.5 Flash (batch)")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model google/gemini-3.5-flash:batch)
  (enabled true)
  (capabilities (
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
  (limits (
    (contextWindow 1048576)
    (maxOutputTokens 65536)
  ))
  (pricing (
    (prompt "0.00000075")
    (completion "0.0000045")
    (image "0.00000075")
    (audio "0.0000015")
    (input_audio_cache "0.00000015")
    (web_search "0.014")
    (internal_reasoning "0.0000045")
    (input_cache_read "0.000000075")
  ))
  (properties (
    (id google/gemini-3.5-flash:batch)
    (canonical_slug google/gemini-3.5-flash-20260519)
    (hugging_face_id null)
    (name "Google: Gemini 3.5 Flash (batch)")
    (created 1779193800)
    (description "Gemini 3.5 Flash is Google's high-efficiency multimodal model, bringing near-Pro level coding and reasoning at Flash-tier cost and speed. It is highly optimized for coding proficiency and parallel agentic execution...")
    (context_length 1048576)
    (architecture (
      (modality text+image+file+audio+video->text)
      (input_modalities ([]
        text
        image
        video
        file
        audio
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Gemini)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.00000075")
      (completion "0.0000045")
      (image "0.00000075")
      (audio "0.0000015")
      (input_audio_cache "0.00000015")
      (web_search "0.014")
      (internal_reasoning "0.0000045")
      (input_cache_read "0.000000075")
    ))
    (top_provider (
      (context_length 1048576)
      (max_completion_tokens 65536)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
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
    (default_parameters (
      (temperature null)
      (top_p null)
      (top_k null)
      (frequency_penalty null)
      (presence_penalty null)
      (repetition_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff 2025-01-01)
    (expiration_date null)
    (links (
      (details /api/v1/models/google/gemini-3.5-flash-20260519/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena agents)
          (category agenticgamedev)
          (elo 1188)
          (win_rate 54)
          (rank 11)
        )
        (
          (arena agents)
          (category agentichtmlslides)
          (elo 1162)
          (win_rate 45.8)
          (rank 7)
        )
        (
          (arena agents)
          (category agenticslides)
          (elo 1244)
          (win_rate 57.5)
          (rank 4)
        )
        (
          (arena agents)
          (category "agenticslides(html)")
          (elo 1162)
          (win_rate 45.7)
          (rank 7)
        )
        (
          (arena agents)
          (category "agenticslides(python-pptx)")
          (elo 1242)
          (win_rate 57.8)
          (rank 3)
        )
        (
          (arena agents)
          (category androidnative)
          (elo 1218)
          (win_rate 55.8)
          (rank 10)
        )
        (
          (arena agents)
          (category fullstack)
          (elo 1234)
          (win_rate 56.7)
          (rank 10)
        )
        (
          (arena agents)
          (category godotgamedev)
          (elo 1135)
          (win_rate 42.9)
          (rank 21)
        )
        (
          (arena agents)
          (category htmlslides)
          (elo 1172)
          (win_rate 46.5)
          (rank 16)
        )
        (
          (arena agents)
          (category mobileapps)
          (elo 1218)
          (win_rate 53.5)
          (rank 10)
        )
        (
          (arena agents)
          (category pptxslides)
          (elo 1244)
          (win_rate 57.7)
          (rank 3)
        )
        (
          (arena agents)
          (category python-pptxslides)
          (elo 1247)
          (win_rate 57.4)
          (rank 7)
        )
        (
          (arena agents)
          (category webapps)
          (elo 1247)
          (win_rate 53)
          (rank 14)
        )
        (
          (arena models)
          (category 3d)
          (elo 1294)
          (win_rate 57.7)
          (rank 20)
        )
        (
          (arena models)
          (category asciiart)
          (elo 1295)
          (win_rate 59.7)
          (rank 7)
        )
        (
          (arena models)
          (category codecategories)
          (elo 1289)
          (win_rate 56.1)
          (rank 17)
        )
        (
          (arena models)
          (category dataviz)
          (elo 1263)
          (win_rate 55)
          (rank 24)
        )
        (
          (arena models)
          (category gamedev)
          (elo 1309)
          (win_rate 56.4)
          (rank 12)
        )
        (
          (arena models)
          (category svg)
          (elo 1296)
          (win_rate 60.9)
          (rank 3)
        )
        (
          (arena models)
          (category uicomponent)
          (elo 1308)
          (win_rate 56.8)
          (rank 11)
        )
        (
          (arena models)
          (category website)
          (elo 1282)
          (win_rate 55.3)
          (rank 22)
        )
      ))
      (artificial_analysis (
        (intelligence_index 52)
        (coding_index 70.1)
        (agentic_index 39.7)
      ))
    ))
    (reasoning (
      (mandatory true)
      (default_enabled true)
      (supported_efforts ([]
        high
        medium
        low
        minimal
      ))
      (default_effort medium)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id google/gemini-3.5-flash:batch)
    (canonical_slug google/gemini-3.5-flash-20260519)
    (hugging_face_id null)
    (name "Google: Gemini 3.5 Flash (batch)")
    (created 1779193800)
    (description "Gemini 3.5 Flash is Google's high-efficiency multimodal model, bringing near-Pro level coding and reasoning at Flash-tier cost and speed. It is highly optimized for coding proficiency and parallel agentic execution...")
    (context_length 1048576)
    (architecture (
      (modality text+image+file+audio+video->text)
      (input_modalities ([]
        text
        image
        video
        file
        audio
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Gemini)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.00000075")
      (completion "0.0000045")
      (image "0.00000075")
      (audio "0.0000015")
      (input_audio_cache "0.00000015")
      (web_search "0.014")
      (internal_reasoning "0.0000045")
      (input_cache_read "0.000000075")
    ))
    (top_provider (
      (context_length 1048576)
      (max_completion_tokens 65536)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
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
    (default_parameters (
      (temperature null)
      (top_p null)
      (top_k null)
      (frequency_penalty null)
      (presence_penalty null)
      (repetition_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff 2025-01-01)
    (expiration_date null)
    (links (
      (details /api/v1/models/google/gemini-3.5-flash-20260519/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena agents)
          (category agenticgamedev)
          (elo 1188)
          (win_rate 54)
          (rank 11)
        )
        (
          (arena agents)
          (category agentichtmlslides)
          (elo 1162)
          (win_rate 45.8)
          (rank 7)
        )
        (
          (arena agents)
          (category agenticslides)
          (elo 1244)
          (win_rate 57.5)
          (rank 4)
        )
        (
          (arena agents)
          (category "agenticslides(html)")
          (elo 1162)
          (win_rate 45.7)
          (rank 7)
        )
        (
          (arena agents)
          (category "agenticslides(python-pptx)")
          (elo 1242)
          (win_rate 57.8)
          (rank 3)
        )
        (
          (arena agents)
          (category androidnative)
          (elo 1218)
          (win_rate 55.8)
          (rank 10)
        )
        (
          (arena agents)
          (category fullstack)
          (elo 1234)
          (win_rate 56.7)
          (rank 10)
        )
        (
          (arena agents)
          (category godotgamedev)
          (elo 1135)
          (win_rate 42.9)
          (rank 21)
        )
        (
          (arena agents)
          (category htmlslides)
          (elo 1172)
          (win_rate 46.5)
          (rank 16)
        )
        (
          (arena agents)
          (category mobileapps)
          (elo 1218)
          (win_rate 53.5)
          (rank 10)
        )
        (
          (arena agents)
          (category pptxslides)
          (elo 1244)
          (win_rate 57.7)
          (rank 3)
        )
        (
          (arena agents)
          (category python-pptxslides)
          (elo 1247)
          (win_rate 57.4)
          (rank 7)
        )
        (
          (arena agents)
          (category webapps)
          (elo 1247)
          (win_rate 53)
          (rank 14)
        )
        (
          (arena models)
          (category 3d)
          (elo 1294)
          (win_rate 57.7)
          (rank 20)
        )
        (
          (arena models)
          (category asciiart)
          (elo 1295)
          (win_rate 59.7)
          (rank 7)
        )
        (
          (arena models)
          (category codecategories)
          (elo 1289)
          (win_rate 56.1)
          (rank 17)
        )
        (
          (arena models)
          (category dataviz)
          (elo 1263)
          (win_rate 55)
          (rank 24)
        )
        (
          (arena models)
          (category gamedev)
          (elo 1309)
          (win_rate 56.4)
          (rank 12)
        )
        (
          (arena models)
          (category svg)
          (elo 1296)
          (win_rate 60.9)
          (rank 3)
        )
        (
          (arena models)
          (category uicomponent)
          (elo 1308)
          (win_rate 56.8)
          (rank 11)
        )
        (
          (arena models)
          (category website)
          (elo 1282)
          (win_rate 55.3)
          (rank 22)
        )
      ))
      (artificial_analysis (
        (intelligence_index 52)
        (coding_index 70.1)
        (agentic_index 39.7)
      ))
    ))
    (reasoning (
      (mandatory true)
      (default_enabled true)
      (supported_efforts ([]
        high
        medium
        low
        minimal
      ))
      (default_effort medium)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId google/gemini-3.5-flash:batch)
  ))
)
