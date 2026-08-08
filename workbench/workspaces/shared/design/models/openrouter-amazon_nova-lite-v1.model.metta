({}
  (kind model)
  (id openrouter-amazon_nova-lite-v1)
  (label "Amazon: Nova Lite 1.0")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model amazon/nova-lite-v1)
  (enabled true)
  (capabilities ({}
    (audio false)
    (code false)
    (functionCalling true)
    (json false)
    (jsonMode false)
    (local false)
    (multimodal true)
    (reasoning false)
    (text true)
    (tools true)
    (vision true)
  ))
  (limits ({}
    (contextWindow 300000)
    (maxOutputTokens 5120)
  ))
  (pricing ({}
    (prompt "0.00000006")
    (completion "0.00000024")
  ))
  (properties ({}
    (id amazon/nova-lite-v1)
    (canonical_slug amazon/nova-lite-v1)
    (hugging_face_id "")
    (name "Amazon: Nova Lite 1.0")
    (created 1733437363)
    (description "Amazon Nova Lite 1.0 is a very low-cost multimodal model from Amazon that focused on fast processing of image, video, and text inputs to generate text output. Amazon Nova Lite...")
    (context_length 300000)
    (architecture ({}
      (modality text+image->text)
      (input_modalities (
        text
        image
      ))
      (output_modalities (
        text
      ))
      (tokenizer Nova)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.00000006")
      (completion "0.00000024")
    ))
    (top_provider ({}
      (context_length 300000)
      (max_completion_tokens 5120)
      (is_moderated true)
    ))
    (per_request_limits null)
    (supported_parameters (
      max_tokens
      stop
      temperature
      tools
      top_k
      top_p
    ))
    (default_parameters ({}))
    (supported_voices null)
    (knowledge_cutoff 2024-10-31)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/amazon/nova-lite-v1/endpoints)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id amazon/nova-lite-v1)
    (canonical_slug amazon/nova-lite-v1)
    (hugging_face_id "")
    (name "Amazon: Nova Lite 1.0")
    (created 1733437363)
    (description "Amazon Nova Lite 1.0 is a very low-cost multimodal model from Amazon that focused on fast processing of image, video, and text inputs to generate text output. Amazon Nova Lite...")
    (context_length 300000)
    (architecture ({}
      (modality text+image->text)
      (input_modalities (
        text
        image
      ))
      (output_modalities (
        text
      ))
      (tokenizer Nova)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.00000006")
      (completion "0.00000024")
    ))
    (top_provider ({}
      (context_length 300000)
      (max_completion_tokens 5120)
      (is_moderated true)
    ))
    (per_request_limits null)
    (supported_parameters (
      max_tokens
      stop
      temperature
      tools
      top_k
      top_p
    ))
    (default_parameters ({}))
    (supported_voices null)
    (knowledge_cutoff 2024-10-31)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/amazon/nova-lite-v1/endpoints)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId amazon/nova-lite-v1)
  ))
)
