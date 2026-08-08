({}
  (kind model)
  (id openrouter-google_gemini-2.5-flash)
  (label "Google: Gemini 2.5 Flash")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model google/gemini-2.5-flash)
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
    (maxOutputTokens 65535)
  ))
  (pricing ({}
    (prompt "0.0000003")
    (completion "0.0000025")
    (image "0.0000003")
    (audio "0.000001")
    (input_audio_cache "0.0000001")
    (web_search "0.014")
    (internal_reasoning "0.0000025")
    (input_cache_read "0.00000003")
    (input_cache_write "0.0000000833333333333333")
  ))
  (properties ({}
    (id google/gemini-2.5-flash)
    (canonical_slug google/gemini-2.5-flash)
    (hugging_face_id "")
    (name "Google: Gemini 2.5 Flash")
    (created 1750172488)
    (description "Gemini 2.5 Flash is Google's state-of-the-art workhorse model, specifically designed for advanced reasoning, coding, mathematics, and scientific tasks. It includes built-in \"thinking\" capabilities, enabling it to provide responses with greater...")
    (context_length 1048576)
    (architecture ({}
      (modality text+image+file+audio+video->text)
      (input_modalities (
        file
        image
        text
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
      (prompt "0.0000003")
      (completion "0.0000025")
      (image "0.0000003")
      (audio "0.000001")
      (input_audio_cache "0.0000001")
      (web_search "0.014")
      (internal_reasoning "0.0000025")
      (input_cache_read "0.00000003")
      (input_cache_write "0.0000000833333333333333")
    ))
    (top_provider ({}
      (context_length 1048576)
      (max_completion_tokens 65535)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      include_reasoning
      max_tokens
      reasoning
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
    (knowledge_cutoff 2025-01-31)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/google/gemini-2.5-flash/endpoints)
    ))
    (benchmarks ({}
      (design_arena (
        ({}
          (arena models)
          (category 3d)
          (elo 1125)
          (win_rate 47.4)
          (rank 80)
        )
        ({}
          (arena models)
          (category codecategories)
          (elo 1132)
          (win_rate 46.9)
          (rank 81)
        )
        ({}
          (arena models)
          (category dataviz)
          (elo 1154)
          (win_rate 48.4)
          (rank 69)
        )
        ({}
          (arena models)
          (category gamedev)
          (elo 1106)
          (win_rate 44.3)
          (rank 83)
        )
        ({}
          (arena models)
          (category uicomponent)
          (elo 1126)
          (win_rate 48.9)
          (rank 75)
        )
        ({}
          (arena models)
          (category website)
          (elo 1137)
          (win_rate 47.1)
          (rank 81)
        )
        ({}
          (arena models)
          (category svg)
          (elo 1067)
          (win_rate 43.1)
          (rank 63)
        )
      ))
    ))
    (reasoning ({}
      (mandatory false)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id google/gemini-2.5-flash)
    (canonical_slug google/gemini-2.5-flash)
    (hugging_face_id "")
    (name "Google: Gemini 2.5 Flash")
    (created 1750172488)
    (description "Gemini 2.5 Flash is Google's state-of-the-art workhorse model, specifically designed for advanced reasoning, coding, mathematics, and scientific tasks. It includes built-in \"thinking\" capabilities, enabling it to provide responses with greater...")
    (context_length 1048576)
    (architecture ({}
      (modality text+image+file+audio+video->text)
      (input_modalities (
        file
        image
        text
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
      (prompt "0.0000003")
      (completion "0.0000025")
      (image "0.0000003")
      (audio "0.000001")
      (input_audio_cache "0.0000001")
      (web_search "0.014")
      (internal_reasoning "0.0000025")
      (input_cache_read "0.00000003")
      (input_cache_write "0.0000000833333333333333")
    ))
    (top_provider ({}
      (context_length 1048576)
      (max_completion_tokens 65535)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      include_reasoning
      max_tokens
      reasoning
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
    (knowledge_cutoff 2025-01-31)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/google/gemini-2.5-flash/endpoints)
    ))
    (benchmarks ({}
      (design_arena (
        ({}
          (arena models)
          (category 3d)
          (elo 1125)
          (win_rate 47.4)
          (rank 80)
        )
        ({}
          (arena models)
          (category codecategories)
          (elo 1132)
          (win_rate 46.9)
          (rank 81)
        )
        ({}
          (arena models)
          (category dataviz)
          (elo 1154)
          (win_rate 48.4)
          (rank 69)
        )
        ({}
          (arena models)
          (category gamedev)
          (elo 1106)
          (win_rate 44.3)
          (rank 83)
        )
        ({}
          (arena models)
          (category uicomponent)
          (elo 1126)
          (win_rate 48.9)
          (rank 75)
        )
        ({}
          (arena models)
          (category website)
          (elo 1137)
          (win_rate 47.1)
          (rank 81)
        )
        ({}
          (arena models)
          (category svg)
          (elo 1067)
          (win_rate 43.1)
          (rank 63)
        )
      ))
    ))
    (reasoning ({}
      (mandatory false)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId google/gemini-2.5-flash)
  ))
)
