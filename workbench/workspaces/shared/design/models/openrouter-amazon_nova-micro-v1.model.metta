(
  (kind model)
  (id openrouter-amazon_nova-micro-v1)
  (label "Amazon: Nova Micro 1.0")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model amazon/nova-micro-v1)
  (enabled true)
  (capabilities (
    (audio false)
    (code false)
    (functionCalling true)
    (json false)
    (jsonMode false)
    (local false)
    (multimodal false)
    (reasoning false)
    (text true)
    (tools true)
    (vision false)
  ))
  (limits (
    (contextWindow 128000)
    (maxOutputTokens 5120)
  ))
  (pricing (
    (prompt "0.000000035")
    (completion "0.00000014")
  ))
  (properties (
    (id amazon/nova-micro-v1)
    (canonical_slug amazon/nova-micro-v1)
    (hugging_face_id "")
    (name "Amazon: Nova Micro 1.0")
    (created 1733437237)
    (description "Amazon Nova Micro 1.0 is a text-only model that delivers the lowest latency responses in the Amazon Nova family of models at a very low cost. With a context length...")
    (context_length 128000)
    (architecture (
      (modality text->text)
      (input_modalities ([]
        text
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Nova)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.000000035")
      (completion "0.00000014")
    ))
    (top_provider (
      (context_length 128000)
      (max_completion_tokens 5120)
      (is_moderated true)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      max_tokens
      stop
      temperature
      tools
      top_k
      top_p
    ))
    (default_parameters ())
    (supported_voices null)
    (knowledge_cutoff 2024-10-31)
    (expiration_date null)
    (links (
      (details /api/v1/models/amazon/nova-micro-v1/endpoints)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id amazon/nova-micro-v1)
    (canonical_slug amazon/nova-micro-v1)
    (hugging_face_id "")
    (name "Amazon: Nova Micro 1.0")
    (created 1733437237)
    (description "Amazon Nova Micro 1.0 is a text-only model that delivers the lowest latency responses in the Amazon Nova family of models at a very low cost. With a context length...")
    (context_length 128000)
    (architecture (
      (modality text->text)
      (input_modalities ([]
        text
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Nova)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.000000035")
      (completion "0.00000014")
    ))
    (top_provider (
      (context_length 128000)
      (max_completion_tokens 5120)
      (is_moderated true)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      max_tokens
      stop
      temperature
      tools
      top_k
      top_p
    ))
    (default_parameters ())
    (supported_voices null)
    (knowledge_cutoff 2024-10-31)
    (expiration_date null)
    (links (
      (details /api/v1/models/amazon/nova-micro-v1/endpoints)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId amazon/nova-micro-v1)
  ))
)
