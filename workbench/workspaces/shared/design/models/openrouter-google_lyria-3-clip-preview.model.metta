(
  (kind model)
  (id openrouter-google_lyria-3-clip-preview)
  (label "Google: Lyria 3 Clip Preview")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model google/lyria-3-clip-preview)
  (enabled true)
  (capabilities (
    (audio true)
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
  (limits (
    (contextWindow 1048576)
    (maxOutputTokens 65536)
  ))
  (pricing (
    (prompt "0")
    (completion "0")
  ))
  (properties (
    (id google/lyria-3-clip-preview)
    (canonical_slug google/lyria-3-clip-preview-20260330)
    (hugging_face_id null)
    (name "Google: Lyria 3 Clip Preview")
    (created 1774907255)
    (description "30 second duration clips are priced at $0.04 per clip. Lyria 3 is Google's family of music generation models, available through the Gemini API. With Lyria 3, you can generate...")
    (context_length 1048576)
    (architecture (
      (modality text+image->text+audio)
      (input_modalities ([]
        text
        image
      ))
      (output_modalities ([]
        text
        audio
      ))
      (tokenizer Other)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0")
      (completion "0")
    ))
    (top_provider (
      (context_length 1048576)
      (max_completion_tokens 65536)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      max_tokens
      response_format
      seed
      temperature
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
    (knowledge_cutoff null)
    (expiration_date null)
    (links (
      (details /api/v1/models/google/lyria-3-clip-preview-20260330/endpoints)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id google/lyria-3-clip-preview)
    (canonical_slug google/lyria-3-clip-preview-20260330)
    (hugging_face_id null)
    (name "Google: Lyria 3 Clip Preview")
    (created 1774907255)
    (description "30 second duration clips are priced at $0.04 per clip. Lyria 3 is Google's family of music generation models, available through the Gemini API. With Lyria 3, you can generate...")
    (context_length 1048576)
    (architecture (
      (modality text+image->text+audio)
      (input_modalities ([]
        text
        image
      ))
      (output_modalities ([]
        text
        audio
      ))
      (tokenizer Other)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0")
      (completion "0")
    ))
    (top_provider (
      (context_length 1048576)
      (max_completion_tokens 65536)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      max_tokens
      response_format
      seed
      temperature
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
    (knowledge_cutoff null)
    (expiration_date null)
    (links (
      (details /api/v1/models/google/lyria-3-clip-preview-20260330/endpoints)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId google/lyria-3-clip-preview)
  ))
)
