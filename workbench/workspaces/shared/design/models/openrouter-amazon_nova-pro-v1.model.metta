(
  (kind model)
  (id openrouter-amazon_nova-pro-v1)
  (label "Amazon: Nova Pro 1.0")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model amazon/nova-pro-v1)
  (enabled true)
  (capabilities (
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
  (limits (
    (contextWindow 300000)
    (maxOutputTokens 5120)
  ))
  (pricing (
    (prompt "0.0000008")
    (completion "0.0000032")
  ))
  (properties (
    (id amazon/nova-pro-v1)
    (canonical_slug amazon/nova-pro-v1)
    (hugging_face_id "")
    (name "Amazon: Nova Pro 1.0")
    (created 1733436303)
    (description "Amazon Nova Pro 1.0 is a capable multimodal model from Amazon focused on providing a combination of accuracy, speed, and cost for a wide range of tasks. As of December...")
    (context_length 300000)
    (architecture (
      (modality text+image->text)
      (input_modalities ([]
        text
        image
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Nova)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.0000008")
      (completion "0.0000032")
    ))
    (top_provider (
      (context_length 300000)
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
      (details /api/v1/models/amazon/nova-pro-v1/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena models)
          (category website)
          (elo 818)
          (win_rate 21.4)
          (rank 122)
        )
      ))
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id amazon/nova-pro-v1)
    (canonical_slug amazon/nova-pro-v1)
    (hugging_face_id "")
    (name "Amazon: Nova Pro 1.0")
    (created 1733436303)
    (description "Amazon Nova Pro 1.0 is a capable multimodal model from Amazon focused on providing a combination of accuracy, speed, and cost for a wide range of tasks. As of December...")
    (context_length 300000)
    (architecture (
      (modality text+image->text)
      (input_modalities ([]
        text
        image
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Nova)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.0000008")
      (completion "0.0000032")
    ))
    (top_provider (
      (context_length 300000)
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
      (details /api/v1/models/amazon/nova-pro-v1/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena models)
          (category website)
          (elo 818)
          (win_rate 21.4)
          (rank 122)
        )
      ))
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId amazon/nova-pro-v1)
  ))
)
