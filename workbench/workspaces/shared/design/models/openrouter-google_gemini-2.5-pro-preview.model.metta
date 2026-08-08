(
  (kind model)
  (id openrouter-google_gemini-2.5-pro-preview)
  (label "Google: Gemini 2.5 Pro Preview 06-05")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model google/gemini-2.5-pro-preview)
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
    (prompt "0.00000125")
    (completion "0.00001")
    (image "0.00000125")
    (audio "0.00000125")
    (input_audio_cache "0.000000125")
    (web_search "0.014")
    (internal_reasoning "0.00001")
    (input_cache_read "0.000000125")
    (input_cache_write "0.000000375")
    (overrides ([]
      (
        (min_prompt_tokens 200000)
        (prompt "0.0000025")
        (completion "0.000015")
        (audio "0.0000025")
        (input_audio_cache "0.00000025")
        (input_cache_read "0.00000025")
      )
    ))
  ))
  (properties (
    (id google/gemini-2.5-pro-preview)
    (canonical_slug google/gemini-2.5-pro-preview-06-05)
    (hugging_face_id "")
    (name "Google: Gemini 2.5 Pro Preview 06-05")
    (created 1749137257)
    (description "Gemini 2.5 Pro is Google’s state-of-the-art AI model designed for advanced reasoning, coding, mathematics, and scientific tasks. It employs “thinking” capabilities, enabling it to reason through responses with enhanced accuracy...")
    (context_length 1048576)
    (architecture (
      (modality text+image+file+audio->text)
      (input_modalities ([]
        file
        image
        text
        audio
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Gemini)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.00000125")
      (completion "0.00001")
      (image "0.00000125")
      (audio "0.00000125")
      (input_audio_cache "0.000000125")
      (web_search "0.014")
      (internal_reasoning "0.00001")
      (input_cache_read "0.000000125")
      (input_cache_write "0.000000375")
      (overrides ([]
        (
          (min_prompt_tokens 200000)
          (prompt "0.0000025")
          (completion "0.000015")
          (audio "0.0000025")
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
    (default_parameters ())
    (supported_voices null)
    (knowledge_cutoff 2025-01-31)
    (expiration_date null)
    (links (
      (details /api/v1/models/google/gemini-2.5-pro-preview-06-05/endpoints)
    ))
    (reasoning (
      (mandatory true)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id google/gemini-2.5-pro-preview)
    (canonical_slug google/gemini-2.5-pro-preview-06-05)
    (hugging_face_id "")
    (name "Google: Gemini 2.5 Pro Preview 06-05")
    (created 1749137257)
    (description "Gemini 2.5 Pro is Google’s state-of-the-art AI model designed for advanced reasoning, coding, mathematics, and scientific tasks. It employs “thinking” capabilities, enabling it to reason through responses with enhanced accuracy...")
    (context_length 1048576)
    (architecture (
      (modality text+image+file+audio->text)
      (input_modalities ([]
        file
        image
        text
        audio
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Gemini)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.00000125")
      (completion "0.00001")
      (image "0.00000125")
      (audio "0.00000125")
      (input_audio_cache "0.000000125")
      (web_search "0.014")
      (internal_reasoning "0.00001")
      (input_cache_read "0.000000125")
      (input_cache_write "0.000000375")
      (overrides ([]
        (
          (min_prompt_tokens 200000)
          (prompt "0.0000025")
          (completion "0.000015")
          (audio "0.0000025")
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
    (default_parameters ())
    (supported_voices null)
    (knowledge_cutoff 2025-01-31)
    (expiration_date null)
    (links (
      (details /api/v1/models/google/gemini-2.5-pro-preview-06-05/endpoints)
    ))
    (reasoning (
      (mandatory true)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId google/gemini-2.5-pro-preview)
  ))
)
