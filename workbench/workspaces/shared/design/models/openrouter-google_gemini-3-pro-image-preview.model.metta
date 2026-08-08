(
  (kind model)
  (id openrouter-google_gemini-3-pro-image-preview)
  (label "Google: Nano Banana Pro (Gemini 3 Pro Image Preview)")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model google/gemini-3-pro-image-preview)
  (enabled true)
  (capabilities (
    (audio false)
    (code false)
    (functionCalling false)
    (json true)
    (jsonMode true)
    (local false)
    (multimodal true)
    (reasoning true)
    (text true)
    (tools false)
    (vision true)
  ))
  (limits (
    (contextWindow 65536)
    (maxOutputTokens 32768)
  ))
  (pricing (
    (prompt "0.000002")
    (completion "0.000012")
    (image "0.000002")
    (image_output "0.00012")
    (audio "0.000002")
    (input_audio_cache "0.0000002")
    (web_search "0.014")
    (internal_reasoning "0.000012")
    (input_cache_read "0.0000002")
    (input_cache_write "0.000000375")
  ))
  (properties (
    (id google/gemini-3-pro-image-preview)
    (canonical_slug google/gemini-3-pro-image-preview-20251120)
    (hugging_face_id "")
    (name "Google: Nano Banana Pro (Gemini 3 Pro Image Preview)")
    (created 1763653797)
    (description "Nano Banana Pro is Google’s most advanced image-generation and editing model, built on Gemini 3 Pro. It extends the original Nano Banana with significantly improved multimodal reasoning, real-world grounding, and...")
    (context_length 65536)
    (architecture (
      (modality text+image->text+image)
      (input_modalities ([]
        image
        text
      ))
      (output_modalities ([]
        image
        text
      ))
      (tokenizer Gemini)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.000002")
      (completion "0.000012")
      (image "0.000002")
      (image_output "0.00012")
      (audio "0.000002")
      (input_audio_cache "0.0000002")
      (web_search "0.014")
      (internal_reasoning "0.000012")
      (input_cache_read "0.0000002")
      (input_cache_write "0.000000375")
    ))
    (top_provider (
      (context_length 65536)
      (max_completion_tokens 32768)
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
      top_p
    ))
    (default_parameters (
      (temperature null)
      (top_p null)
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links (
      (details /api/v1/models/google/gemini-3-pro-image-preview-20251120/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena models)
          (category graphicdesign)
          (elo 1278)
          (win_rate 65.8)
          (rank 3)
        )
        (
          (arena models)
          (category image)
          (elo 1266)
          (win_rate 62.1)
          (rank 3)
        )
        (
          (arena models)
          (category logo)
          (elo 1255)
          (win_rate 61)
          (rank 4)
        )
        (
          (arena models)
          (category imageediting)
          (elo 1267)
          (win_rate 65.4)
          (rank 2)
        )
      ))
    ))
    (reasoning (
      (mandatory true)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id google/gemini-3-pro-image-preview)
    (canonical_slug google/gemini-3-pro-image-preview-20251120)
    (hugging_face_id "")
    (name "Google: Nano Banana Pro (Gemini 3 Pro Image Preview)")
    (created 1763653797)
    (description "Nano Banana Pro is Google’s most advanced image-generation and editing model, built on Gemini 3 Pro. It extends the original Nano Banana with significantly improved multimodal reasoning, real-world grounding, and...")
    (context_length 65536)
    (architecture (
      (modality text+image->text+image)
      (input_modalities ([]
        image
        text
      ))
      (output_modalities ([]
        image
        text
      ))
      (tokenizer Gemini)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.000002")
      (completion "0.000012")
      (image "0.000002")
      (image_output "0.00012")
      (audio "0.000002")
      (input_audio_cache "0.0000002")
      (web_search "0.014")
      (internal_reasoning "0.000012")
      (input_cache_read "0.0000002")
      (input_cache_write "0.000000375")
    ))
    (top_provider (
      (context_length 65536)
      (max_completion_tokens 32768)
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
      top_p
    ))
    (default_parameters (
      (temperature null)
      (top_p null)
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links (
      (details /api/v1/models/google/gemini-3-pro-image-preview-20251120/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena models)
          (category graphicdesign)
          (elo 1278)
          (win_rate 65.8)
          (rank 3)
        )
        (
          (arena models)
          (category image)
          (elo 1266)
          (win_rate 62.1)
          (rank 3)
        )
        (
          (arena models)
          (category logo)
          (elo 1255)
          (win_rate 61)
          (rank 4)
        )
        (
          (arena models)
          (category imageediting)
          (elo 1267)
          (win_rate 65.4)
          (rank 2)
        )
      ))
    ))
    (reasoning (
      (mandatory true)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId google/gemini-3-pro-image-preview)
  ))
)
