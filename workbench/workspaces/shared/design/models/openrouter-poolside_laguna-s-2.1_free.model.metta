({}
  (kind model)
  (id openrouter-poolside_laguna-s-2.1_free)
  (label "Poolside: Laguna S 2.1 (free)")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model poolside/laguna-s-2.1:free)
  (enabled true)
  (capabilities ({}
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
  (limits ({}
    (contextWindow 262144)
    (maxOutputTokens 32768)
  ))
  (pricing ({}
    (prompt "0")
    (completion "0")
  ))
  (properties ({}
    (id poolside/laguna-s-2.1:free)
    (canonical_slug poolside/laguna-s-2.1-20260720)
    (hugging_face_id poolside/Laguna-S-2.1)
    (name "Poolside: Laguna S 2.1 (free)")
    (created 1784652683)
    (description "Laguna S 2.1 is the latest coding agent model from [Poolside](<https://poolside.ai/>). Laguna S 2.1 is a 118B total parameter model with 8B active parameters, scoring 70.2% on Terminal-Bench 2.1 and...")
    (context_length 262144)
    (architecture ({}
      (modality text->text)
      (input_modalities (
        text
      ))
      (output_modalities (
        text
      ))
      (tokenizer Other)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0")
      (completion "0")
    ))
    (top_provider ({}
      (context_length 262144)
      (max_completion_tokens 32768)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      include_reasoning
      max_tokens
      reasoning
      temperature
      tool_choice
      tools
    ))
    (default_parameters ({}))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/poolside/laguna-s-2.1-20260720/endpoints)
    ))
    (reasoning ({}
      (mandatory false)
      (default_enabled true)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id poolside/laguna-s-2.1:free)
    (canonical_slug poolside/laguna-s-2.1-20260720)
    (hugging_face_id poolside/Laguna-S-2.1)
    (name "Poolside: Laguna S 2.1 (free)")
    (created 1784652683)
    (description "Laguna S 2.1 is the latest coding agent model from [Poolside](<https://poolside.ai/>). Laguna S 2.1 is a 118B total parameter model with 8B active parameters, scoring 70.2% on Terminal-Bench 2.1 and...")
    (context_length 262144)
    (architecture ({}
      (modality text->text)
      (input_modalities (
        text
      ))
      (output_modalities (
        text
      ))
      (tokenizer Other)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0")
      (completion "0")
    ))
    (top_provider ({}
      (context_length 262144)
      (max_completion_tokens 32768)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      include_reasoning
      max_tokens
      reasoning
      temperature
      tool_choice
      tools
    ))
    (default_parameters ({}))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/poolside/laguna-s-2.1-20260720/endpoints)
    ))
    (reasoning ({}
      (mandatory false)
      (default_enabled true)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId poolside/laguna-s-2.1:free)
  ))
)
