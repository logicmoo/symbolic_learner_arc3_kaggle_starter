({}
  (kind model)
  (id openrouter-google_gemini-3.1-flash-image)
  (label "Google: Nano Banana 2 (Gemini 3.1 Flash Image)")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model google/gemini-3.1-flash-image)
  (enabled true)
  (capabilities ({}
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
  (limits ({}
    (contextWindow 131072)
    (maxOutputTokens 32768)
  ))
  (pricing ({}
    (prompt "0.0000005")
    (completion "0.000003")
    (image_output "0.00006")
    (web_search "0.014")
  ))
  (properties ({}
    (id google/gemini-3.1-flash-image)
    (canonical_slug google/gemini-3.1-flash-image-20260528)
    (hugging_face_id null)
    (name "Google: Nano Banana 2 (Gemini 3.1 Flash Image)")
    (created 1781754065)
    (description "Gemini 3.1 Flash Image, a.k.a. \"Nano Banana 2,\" is Google’s latest state of the art image generation and editing model, delivering Pro-level visual quality at Flash speed. It combines advanced...")
    (context_length 131072)
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
      (prompt "0.0000005")
      (completion "0.000003")
      (image_output "0.00006")
      (web_search "0.014")
    ))
    (top_provider ({}
      (context_length 131072)
      (max_completion_tokens 32768)
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
      top_p
    ))
    (default_parameters ({}))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/google/gemini-3.1-flash-image-20260528/endpoints)
    ))
    (reasoning ({}
      (mandatory false)
      (default_enabled true)
      (supported_efforts (
        high
        minimal
      ))
      (default_effort minimal)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id google/gemini-3.1-flash-image)
    (canonical_slug google/gemini-3.1-flash-image-20260528)
    (hugging_face_id null)
    (name "Google: Nano Banana 2 (Gemini 3.1 Flash Image)")
    (created 1781754065)
    (description "Gemini 3.1 Flash Image, a.k.a. \"Nano Banana 2,\" is Google’s latest state of the art image generation and editing model, delivering Pro-level visual quality at Flash speed. It combines advanced...")
    (context_length 131072)
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
      (prompt "0.0000005")
      (completion "0.000003")
      (image_output "0.00006")
      (web_search "0.014")
    ))
    (top_provider ({}
      (context_length 131072)
      (max_completion_tokens 32768)
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
      top_p
    ))
    (default_parameters ({}))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/google/gemini-3.1-flash-image-20260528/endpoints)
    ))
    (reasoning ({}
      (mandatory false)
      (default_enabled true)
      (supported_efforts (
        high
        minimal
      ))
      (default_effort minimal)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId google/gemini-3.1-flash-image)
  ))
)
