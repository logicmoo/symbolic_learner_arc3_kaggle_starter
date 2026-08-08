({}
  (kind model)
  (id openrouter-google_gemini-3.6-flash)
  (label "Google: Gemini 3.6 Flash")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model google/gemini-3.6-flash)
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
    (prompt "0.0000015")
    (completion "0.0000075")
    (image "0.0000015")
    (audio "0.0000015")
    (input_audio_cache "0.00000015")
    (web_search "0.014")
    (internal_reasoning "0.0000075")
    (input_cache_read "0.00000015")
    (input_cache_write "0.0000000833333333333333")
  ))
  (properties ({}
    (id google/gemini-3.6-flash)
    (canonical_slug google/gemini-3.6-flash-20260721)
    (hugging_face_id null)
    (name "Google: Gemini 3.6 Flash")
    (created 1784646733)
    (description "Gemini 3.6 Flash is a high-efficiency model from Google for coding, agentic workflows, and web and app development. It is designed to produce polished outputs with fewer unnecessary edits and...")
    (context_length 1048576)
    (architecture ({}
      (modality text+image+file+audio+video->text)
      (input_modalities (
        text
        image
        video
        file
        audio
      ))
      (output_modalities (
        text
      ))
      (tokenizer Gemini)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.0000015")
      (completion "0.0000075")
      (image "0.0000015")
      (audio "0.0000015")
      (input_audio_cache "0.00000015")
      (web_search "0.014")
      (internal_reasoning "0.0000075")
      (input_cache_read "0.00000015")
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
      (details /api/v1/models/google/gemini-3.6-flash-20260721/endpoints)
    ))
    (benchmarks ({}
      (design_arena (
        ({}
          (arena agents)
          (category agenticgamedev)
          (elo 1207)
          (win_rate 54)
          (rank 6)
        )
        ({}
          (arena agents)
          (category androidnative)
          (elo 1232)
          (win_rate 54.3)
          (rank 8)
        )
        ({}
          (arena agents)
          (category fullstack)
          (elo 1204)
          (win_rate 48.7)
          (rank 14)
        )
        ({}
          (arena agents)
          (category htmlslides)
          (elo 1196)
          (win_rate 51.8)
          (rank 13)
        )
        ({}
          (arena agents)
          (category python-pptxslides)
          (elo 1155)
          (win_rate 47.1)
          (rank 14)
        )
        ({}
          (arena models)
          (category 3d)
          (elo 1330)
          (win_rate 54.3)
          (rank 7)
        )
        ({}
          (arena models)
          (category codecategories)
          (elo 1317)
          (win_rate 55.6)
          (rank 7)
        )
        ({}
          (arena models)
          (category dataviz)
          (elo 1345)
          (win_rate 58)
          (rank 4)
        )
        ({}
          (arena models)
          (category gamedev)
          (elo 1289)
          (win_rate 52.8)
          (rank 18)
        )
        ({}
          (arena models)
          (category uicomponent)
          (elo 1340)
          (win_rate 55.9)
          (rank 4)
        )
        ({}
          (arena models)
          (category website)
          (elo 1323)
          (win_rate 57.8)
          (rank 6)
        )
      ))
      (artificial_analysis ({}
        (intelligence_index 51.6)
        (coding_index 69.2)
        (agentic_index 40.5)
      ))
    ))
    (reasoning ({}
      (mandatory true)
      (default_enabled true)
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
    (id google/gemini-3.6-flash)
    (canonical_slug google/gemini-3.6-flash-20260721)
    (hugging_face_id null)
    (name "Google: Gemini 3.6 Flash")
    (created 1784646733)
    (description "Gemini 3.6 Flash is a high-efficiency model from Google for coding, agentic workflows, and web and app development. It is designed to produce polished outputs with fewer unnecessary edits and...")
    (context_length 1048576)
    (architecture ({}
      (modality text+image+file+audio+video->text)
      (input_modalities (
        text
        image
        video
        file
        audio
      ))
      (output_modalities (
        text
      ))
      (tokenizer Gemini)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.0000015")
      (completion "0.0000075")
      (image "0.0000015")
      (audio "0.0000015")
      (input_audio_cache "0.00000015")
      (web_search "0.014")
      (internal_reasoning "0.0000075")
      (input_cache_read "0.00000015")
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
      (details /api/v1/models/google/gemini-3.6-flash-20260721/endpoints)
    ))
    (benchmarks ({}
      (design_arena (
        ({}
          (arena agents)
          (category agenticgamedev)
          (elo 1207)
          (win_rate 54)
          (rank 6)
        )
        ({}
          (arena agents)
          (category androidnative)
          (elo 1232)
          (win_rate 54.3)
          (rank 8)
        )
        ({}
          (arena agents)
          (category fullstack)
          (elo 1204)
          (win_rate 48.7)
          (rank 14)
        )
        ({}
          (arena agents)
          (category htmlslides)
          (elo 1196)
          (win_rate 51.8)
          (rank 13)
        )
        ({}
          (arena agents)
          (category python-pptxslides)
          (elo 1155)
          (win_rate 47.1)
          (rank 14)
        )
        ({}
          (arena models)
          (category 3d)
          (elo 1330)
          (win_rate 54.3)
          (rank 7)
        )
        ({}
          (arena models)
          (category codecategories)
          (elo 1317)
          (win_rate 55.6)
          (rank 7)
        )
        ({}
          (arena models)
          (category dataviz)
          (elo 1345)
          (win_rate 58)
          (rank 4)
        )
        ({}
          (arena models)
          (category gamedev)
          (elo 1289)
          (win_rate 52.8)
          (rank 18)
        )
        ({}
          (arena models)
          (category uicomponent)
          (elo 1340)
          (win_rate 55.9)
          (rank 4)
        )
        ({}
          (arena models)
          (category website)
          (elo 1323)
          (win_rate 57.8)
          (rank 6)
        )
      ))
      (artificial_analysis ({}
        (intelligence_index 51.6)
        (coding_index 69.2)
        (agentic_index 40.5)
      ))
    ))
    (reasoning ({}
      (mandatory true)
      (default_enabled true)
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
    (remoteModelId google/gemini-3.6-flash)
  ))
)
