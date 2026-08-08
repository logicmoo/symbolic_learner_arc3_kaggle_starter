({}
  (kind model)
  (id openrouter-google_gemini-2.5-flash-image)
  (label "Google: Nano Banana (Gemini 2.5 Flash Image)")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model google/gemini-2.5-flash-image)
  (enabled true)
  (capabilities ({}
    (audio false)
    (code false)
    (functionCalling false)
    (json true)
    (jsonMode true)
    (local false)
    (multimodal true)
    (reasoning false)
    (text true)
    (tools false)
    (vision true)
  ))
  (limits ({}
    (contextWindow 32768)
    (maxOutputTokens 8192)
  ))
  (pricing ({}
    (prompt "0.0000003")
    (completion "0.0000025")
    (image "0.0000003")
    (image_output "0.00003")
    (audio "0.000001")
    (input_audio_cache "0.0000001")
    (web_search "0.014")
    (internal_reasoning "0.0000025")
    (input_cache_read "0.00000003")
    (input_cache_write "0.0000000833333333333333")
  ))
  (properties ({}
    (id google/gemini-2.5-flash-image)
    (canonical_slug google/gemini-2.5-flash-image)
    (hugging_face_id "")
    (name "Google: Nano Banana (Gemini 2.5 Flash Image)")
    (created 1759870431)
    (description "Gemini 2.5 Flash Image, a.k.a. \"Nano Banana,\" is now generally available. It is a state of the art image generation model with contextual understanding. It is capable of image generation,...")
    (context_length 32768)
    (architecture ({}
      (modality text+image->text+image)
      (input_modalities (
        image
        text
      ))
      (output_modalities (
        image
        text
      ))
      (tokenizer Gemini)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.0000003")
      (completion "0.0000025")
      (image "0.0000003")
      (image_output "0.00003")
      (audio "0.000001")
      (input_audio_cache "0.0000001")
      (web_search "0.014")
      (internal_reasoning "0.0000025")
      (input_cache_read "0.00000003")
      (input_cache_write "0.0000000833333333333333")
    ))
    (top_provider ({}
      (context_length 32768)
      (max_completion_tokens 8192)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      max_tokens
      response_format
      seed
      stop
      structured_outputs
      temperature
      top_p
    ))
    (default_parameters ({}
      (temperature null)
      (top_p null)
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff 2025-01-31)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/google/gemini-2.5-flash-image/endpoints)
    ))
    (benchmarks ({}
      (design_arena (
        ({}
          (arena models)
          (category graphicdesign)
          (elo 1195)
          (win_rate 56.9)
          (rank 8)
        )
        ({}
          (arena models)
          (category image)
          (elo 1208)
          (win_rate 55.6)
          (rank 8)
        )
        ({}
          (arena models)
          (category logo)
          (elo 1183)
          (win_rate 51.4)
          (rank 9)
        )
      ))
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id google/gemini-2.5-flash-image)
    (canonical_slug google/gemini-2.5-flash-image)
    (hugging_face_id "")
    (name "Google: Nano Banana (Gemini 2.5 Flash Image)")
    (created 1759870431)
    (description "Gemini 2.5 Flash Image, a.k.a. \"Nano Banana,\" is now generally available. It is a state of the art image generation model with contextual understanding. It is capable of image generation,...")
    (context_length 32768)
    (architecture ({}
      (modality text+image->text+image)
      (input_modalities (
        image
        text
      ))
      (output_modalities (
        image
        text
      ))
      (tokenizer Gemini)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.0000003")
      (completion "0.0000025")
      (image "0.0000003")
      (image_output "0.00003")
      (audio "0.000001")
      (input_audio_cache "0.0000001")
      (web_search "0.014")
      (internal_reasoning "0.0000025")
      (input_cache_read "0.00000003")
      (input_cache_write "0.0000000833333333333333")
    ))
    (top_provider ({}
      (context_length 32768)
      (max_completion_tokens 8192)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      max_tokens
      response_format
      seed
      stop
      structured_outputs
      temperature
      top_p
    ))
    (default_parameters ({}
      (temperature null)
      (top_p null)
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff 2025-01-31)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/google/gemini-2.5-flash-image/endpoints)
    ))
    (benchmarks ({}
      (design_arena (
        ({}
          (arena models)
          (category graphicdesign)
          (elo 1195)
          (win_rate 56.9)
          (rank 8)
        )
        ({}
          (arena models)
          (category image)
          (elo 1208)
          (win_rate 55.6)
          (rank 8)
        )
        ({}
          (arena models)
          (category logo)
          (elo 1183)
          (win_rate 51.4)
          (rank 9)
        )
      ))
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId google/gemini-2.5-flash-image)
  ))
)
