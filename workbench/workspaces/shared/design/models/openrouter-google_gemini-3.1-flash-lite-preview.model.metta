({}
  (kind model)
  (id openrouter-google_gemini-3.1-flash-lite-preview)
  (label "Google: Gemini 3.1 Flash Lite Preview")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model google/gemini-3.1-flash-lite-preview)
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
    (prompt "0.00000025")
    (completion "0.0000015")
    (image "0.00000025")
    (audio "0.0000005")
    (input_audio_cache "0.00000005")
    (web_search "0.014")
    (internal_reasoning "0.0000015")
    (input_cache_read "0.000000025")
    (input_cache_write "0.0000000833333333333333")
  ))
  (properties ({}
    (id google/gemini-3.1-flash-lite-preview)
    (canonical_slug google/gemini-3.1-flash-lite-preview-20260303)
    (hugging_face_id "")
    (name "Google: Gemini 3.1 Flash Lite Preview")
    (created 1772512673)
    (description "Gemini 3.1 Flash Lite Preview is Google's high-efficiency model optimized for high-volume use cases. It outperforms Gemini 2.5 Flash Lite on overall quality and approaches Gemini 2.5 Flash performance across...")
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
      (prompt "0.00000025")
      (completion "0.0000015")
      (image "0.00000025")
      (audio "0.0000005")
      (input_audio_cache "0.00000005")
      (web_search "0.014")
      (internal_reasoning "0.0000015")
      (input_cache_read "0.000000025")
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
      (details /api/v1/models/google/gemini-3.1-flash-lite-preview-20260303/endpoints)
    ))
    (benchmarks ({}
      (design_arena (
        ({}
          (arena models)
          (category 3d)
          (elo 1102)
          (win_rate 38.8)
          (rank 84)
        )
        ({}
          (arena models)
          (category asciiart)
          (elo 1204)
          (win_rate 50.6)
          (rank 20)
        )
        ({}
          (arena models)
          (category codecategories)
          (elo 1100)
          (win_rate 36.4)
          (rank 87)
        )
        ({}
          (arena models)
          (category dataviz)
          (elo 1072)
          (win_rate 33.3)
          (rank 90)
        )
        ({}
          (arena models)
          (category gamedev)
          (elo 1070)
          (win_rate 33.7)
          (rank 90)
        )
        ({}
          (arena models)
          (category svg)
          (elo 1099)
          (win_rate 42.5)
          (rank 55)
        )
        ({}
          (arena models)
          (category uicomponent)
          (elo 1105)
          (win_rate 37.7)
          (rank 80)
        )
        ({}
          (arena models)
          (category website)
          (elo 1104)
          (win_rate 36.6)
          (rank 89)
        )
      ))
      (artificial_analysis ({}
        (intelligence_index 25.6)
        (coding_index 34.7)
        (agentic_index 6.5)
      ))
    ))
    (reasoning ({}
      (mandatory false)
      (default_enabled true)
      (supported_efforts (
        high
        medium
        low
        minimal
      ))
      (default_effort minimal)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id google/gemini-3.1-flash-lite-preview)
    (canonical_slug google/gemini-3.1-flash-lite-preview-20260303)
    (hugging_face_id "")
    (name "Google: Gemini 3.1 Flash Lite Preview")
    (created 1772512673)
    (description "Gemini 3.1 Flash Lite Preview is Google's high-efficiency model optimized for high-volume use cases. It outperforms Gemini 2.5 Flash Lite on overall quality and approaches Gemini 2.5 Flash performance across...")
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
      (prompt "0.00000025")
      (completion "0.0000015")
      (image "0.00000025")
      (audio "0.0000005")
      (input_audio_cache "0.00000005")
      (web_search "0.014")
      (internal_reasoning "0.0000015")
      (input_cache_read "0.000000025")
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
      (details /api/v1/models/google/gemini-3.1-flash-lite-preview-20260303/endpoints)
    ))
    (benchmarks ({}
      (design_arena (
        ({}
          (arena models)
          (category 3d)
          (elo 1102)
          (win_rate 38.8)
          (rank 84)
        )
        ({}
          (arena models)
          (category asciiart)
          (elo 1204)
          (win_rate 50.6)
          (rank 20)
        )
        ({}
          (arena models)
          (category codecategories)
          (elo 1100)
          (win_rate 36.4)
          (rank 87)
        )
        ({}
          (arena models)
          (category dataviz)
          (elo 1072)
          (win_rate 33.3)
          (rank 90)
        )
        ({}
          (arena models)
          (category gamedev)
          (elo 1070)
          (win_rate 33.7)
          (rank 90)
        )
        ({}
          (arena models)
          (category svg)
          (elo 1099)
          (win_rate 42.5)
          (rank 55)
        )
        ({}
          (arena models)
          (category uicomponent)
          (elo 1105)
          (win_rate 37.7)
          (rank 80)
        )
        ({}
          (arena models)
          (category website)
          (elo 1104)
          (win_rate 36.6)
          (rank 89)
        )
      ))
      (artificial_analysis ({}
        (intelligence_index 25.6)
        (coding_index 34.7)
        (agentic_index 6.5)
      ))
    ))
    (reasoning ({}
      (mandatory false)
      (default_enabled true)
      (supported_efforts (
        high
        medium
        low
        minimal
      ))
      (default_effort minimal)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId google/gemini-3.1-flash-lite-preview)
  ))
)
