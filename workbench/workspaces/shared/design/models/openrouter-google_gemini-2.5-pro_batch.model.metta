(
  (kind model)
  (id openrouter-google_gemini-2.5-pro_batch)
  (label "Google: Gemini 2.5 Pro (batch)")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model google/gemini-2.5-pro:batch)
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
    (prompt "0.000000625")
    (completion "0.000005")
    (image "0.000000625")
    (audio "0.000000625")
    (input_audio_cache "0.000000125")
    (web_search "0.014")
    (internal_reasoning "0.000005")
    (input_cache_read "0.000000125")
    (overrides ([]
      (
        (min_prompt_tokens 200000)
        (prompt "0.00000125")
        (completion "0.0000075")
        (audio "0.00000125")
        (input_audio_cache "0.00000025")
        (input_cache_read "0.00000025")
      )
    ))
  ))
  (properties (
    (id google/gemini-2.5-pro:batch)
    (canonical_slug google/gemini-2.5-pro)
    (hugging_face_id "")
    (name "Google: Gemini 2.5 Pro (batch)")
    (created 1750169544)
    (description "Gemini 2.5 Pro is Google’s state-of-the-art AI model designed for advanced reasoning, coding, mathematics, and scientific tasks. It employs “thinking” capabilities, enabling it to reason through responses with enhanced accuracy...")
    (context_length 1048576)
    (architecture (
      (modality text+image+file+audio+video->text)
      (input_modalities ([]
        text
        image
        file
        audio
        video
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Gemini)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.000000625")
      (completion "0.000005")
      (image "0.000000625")
      (audio "0.000000625")
      (input_audio_cache "0.000000125")
      (web_search "0.014")
      (internal_reasoning "0.000005")
      (input_cache_read "0.000000125")
      (overrides ([]
        (
          (min_prompt_tokens 200000)
          (prompt "0.00000125")
          (completion "0.0000075")
          (audio "0.00000125")
          (input_audio_cache "0.00000025")
          (input_cache_read "0.00000025")
        )
      ))
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
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff 2025-01-31)
    (expiration_date null)
    (links (
      (details /api/v1/models/google/gemini-2.5-pro/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena models)
          (category 3d)
          (elo 1136)
          (win_rate 52.1)
          (rank 70)
        )
        (
          (arena models)
          (category codecategories)
          (elo 1182)
          (win_rate 58.3)
          (rank 61)
        )
        (
          (arena models)
          (category dataviz)
          (elo 1273)
          (win_rate 71.8)
          (rank 19)
        )
        (
          (arena models)
          (category gamedev)
          (elo 1150)
          (win_rate 54.9)
          (rank 66)
        )
        (
          (arena models)
          (category uicomponent)
          (elo 1174)
          (win_rate 60.1)
          (rank 61)
        )
        (
          (arena models)
          (category website)
          (elo 1190)
          (win_rate 58.9)
          (rank 61)
        )
      ))
      (artificial_analysis (
        (intelligence_index 25.9)
        (coding_index 33.3)
        (agentic_index 7.2)
      ))
    ))
    (reasoning (
      (mandatory true)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id google/gemini-2.5-pro:batch)
    (canonical_slug google/gemini-2.5-pro)
    (hugging_face_id "")
    (name "Google: Gemini 2.5 Pro (batch)")
    (created 1750169544)
    (description "Gemini 2.5 Pro is Google’s state-of-the-art AI model designed for advanced reasoning, coding, mathematics, and scientific tasks. It employs “thinking” capabilities, enabling it to reason through responses with enhanced accuracy...")
    (context_length 1048576)
    (architecture (
      (modality text+image+file+audio+video->text)
      (input_modalities ([]
        text
        image
        file
        audio
        video
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Gemini)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.000000625")
      (completion "0.000005")
      (image "0.000000625")
      (audio "0.000000625")
      (input_audio_cache "0.000000125")
      (web_search "0.014")
      (internal_reasoning "0.000005")
      (input_cache_read "0.000000125")
      (overrides ([]
        (
          (min_prompt_tokens 200000)
          (prompt "0.00000125")
          (completion "0.0000075")
          (audio "0.00000125")
          (input_audio_cache "0.00000025")
          (input_cache_read "0.00000025")
        )
      ))
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
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff 2025-01-31)
    (expiration_date null)
    (links (
      (details /api/v1/models/google/gemini-2.5-pro/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena models)
          (category 3d)
          (elo 1136)
          (win_rate 52.1)
          (rank 70)
        )
        (
          (arena models)
          (category codecategories)
          (elo 1182)
          (win_rate 58.3)
          (rank 61)
        )
        (
          (arena models)
          (category dataviz)
          (elo 1273)
          (win_rate 71.8)
          (rank 19)
        )
        (
          (arena models)
          (category gamedev)
          (elo 1150)
          (win_rate 54.9)
          (rank 66)
        )
        (
          (arena models)
          (category uicomponent)
          (elo 1174)
          (win_rate 60.1)
          (rank 61)
        )
        (
          (arena models)
          (category website)
          (elo 1190)
          (win_rate 58.9)
          (rank 61)
        )
      ))
      (artificial_analysis (
        (intelligence_index 25.9)
        (coding_index 33.3)
        (agentic_index 7.2)
      ))
    ))
    (reasoning (
      (mandatory true)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId google/gemini-2.5-pro:batch)
  ))
)
