(
  (kind model)
  (id openrouter-poolside_laguna-xs-2.1)
  (label "Poolside: Laguna XS 2.1")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model poolside/laguna-xs-2.1)
  (enabled true)
  (capabilities (
    (audio false)
    (code false)
    (functionCalling true)
    (json false)
    (jsonMode false)
    (local false)
    (multimodal false)
    (reasoning true)
    (text true)
    (tools true)
    (vision false)
  ))
  (limits (
    (contextWindow 262144)
    (maxOutputTokens 32768)
  ))
  (pricing (
    (prompt "0.00000006")
    (completion "0.00000012")
    (input_cache_read "0.00000003")
  ))
  (properties (
    (id poolside/laguna-xs-2.1)
    (canonical_slug poolside/laguna-xs-2.1-20260625)
    (hugging_face_id poolside/Laguna-XS-2.1)
    (name "Poolside: Laguna XS 2.1")
    (created 1783002429)
    (description "Laguna XS 2.1 is the latest coding agent model in the 33B-A3B category from [Poolside](https://poolside.ai/) and a step forward from their Laguna XS.2 model (released in April 2026). It combines...")
    (context_length 262144)
    (architecture (
      (modality text->text)
      (input_modalities ([]
        text
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Other)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.00000006")
      (completion "0.00000012")
      (input_cache_read "0.00000003")
    ))
    (top_provider (
      (context_length 262144)
      (max_completion_tokens 32768)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      include_reasoning
      max_tokens
      reasoning
      temperature
      tool_choice
      tools
    ))
    (default_parameters ())
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links (
      (details /api/v1/models/poolside/laguna-xs-2.1-20260625/endpoints)
    ))
    (reasoning (
      (mandatory false)
      (default_enabled true)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id poolside/laguna-xs-2.1)
    (canonical_slug poolside/laguna-xs-2.1-20260625)
    (hugging_face_id poolside/Laguna-XS-2.1)
    (name "Poolside: Laguna XS 2.1")
    (created 1783002429)
    (description "Laguna XS 2.1 is the latest coding agent model in the 33B-A3B category from [Poolside](https://poolside.ai/) and a step forward from their Laguna XS.2 model (released in April 2026). It combines...")
    (context_length 262144)
    (architecture (
      (modality text->text)
      (input_modalities ([]
        text
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Other)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.00000006")
      (completion "0.00000012")
      (input_cache_read "0.00000003")
    ))
    (top_provider (
      (context_length 262144)
      (max_completion_tokens 32768)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      include_reasoning
      max_tokens
      reasoning
      temperature
      tool_choice
      tools
    ))
    (default_parameters ())
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links (
      (details /api/v1/models/poolside/laguna-xs-2.1-20260625/endpoints)
    ))
    (reasoning (
      (mandatory false)
      (default_enabled true)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId poolside/laguna-xs-2.1)
  ))
)
