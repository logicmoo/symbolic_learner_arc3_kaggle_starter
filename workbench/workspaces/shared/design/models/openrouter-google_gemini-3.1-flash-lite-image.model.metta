(
  (kind model)
  (id openrouter-google_gemini-3.1-flash-lite-image)
  (label "Google: Nano Banana 2 Lite (Gemini 3.1 Flash Lite Image)")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model google/gemini-3.1-flash-lite-image)
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
    (maxOutputTokens 65536)
  ))
  (pricing (
    (prompt "0.00000025")
    (completion "0.0000015")
    (image_output "0.00003")
    (web_search "0.014")
  ))
  (properties (
    (id google/gemini-3.1-flash-lite-image)
    (canonical_slug google/gemini-3.1-flash-lite-image-20260630)
    (hugging_face_id null)
    (name "Google: Nano Banana 2 Lite (Gemini 3.1 Flash Lite Image)")
    (created 1782837225)
    (description "Nano Banana 2 Lite (Gemini 3.1 Flash Lite Image) is Google's fastest, most cost-efficient Gemini image model, built for high-velocity developer pipelines and rapid-fire visual exploration. It delivers text-to-image generation...")
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
      (prompt "0.00000025")
      (completion "0.0000015")
      (image_output "0.00003")
      (web_search "0.014")
    ))
    (top_provider (
      (context_length 65536)
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
      temperature
      top_p
    ))
    (default_parameters ())
    (supported_voices null)
    (knowledge_cutoff 2025-01-01)
    (expiration_date null)
    (links (
      (details /api/v1/models/google/gemini-3.1-flash-lite-image-20260630/endpoints)
    ))
    (reasoning (
      (mandatory false)
      (default_enabled true)
      (supported_efforts ([]
        high
        minimal
      ))
      (default_effort minimal)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id google/gemini-3.1-flash-lite-image)
    (canonical_slug google/gemini-3.1-flash-lite-image-20260630)
    (hugging_face_id null)
    (name "Google: Nano Banana 2 Lite (Gemini 3.1 Flash Lite Image)")
    (created 1782837225)
    (description "Nano Banana 2 Lite (Gemini 3.1 Flash Lite Image) is Google's fastest, most cost-efficient Gemini image model, built for high-velocity developer pipelines and rapid-fire visual exploration. It delivers text-to-image generation...")
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
      (prompt "0.00000025")
      (completion "0.0000015")
      (image_output "0.00003")
      (web_search "0.014")
    ))
    (top_provider (
      (context_length 65536)
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
      temperature
      top_p
    ))
    (default_parameters ())
    (supported_voices null)
    (knowledge_cutoff 2025-01-01)
    (expiration_date null)
    (links (
      (details /api/v1/models/google/gemini-3.1-flash-lite-image-20260630/endpoints)
    ))
    (reasoning (
      (mandatory false)
      (default_enabled true)
      (supported_efforts ([]
        high
        minimal
      ))
      (default_effort minimal)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId google/gemini-3.1-flash-lite-image)
  ))
)
