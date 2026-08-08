({}
  (kind model)
  (id openrouter-mistralai_mixtral-8x22b-instruct)
  (label "Mistral: Mixtral 8x22B Instruct")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model mistralai/mixtral-8x22b-instruct)
  (enabled true)
  (capabilities ({}
    (audio false)
    (code false)
    (functionCalling true)
    (json true)
    (jsonMode true)
    (local false)
    (multimodal true)
    (reasoning false)
    (text true)
    (tools true)
    (vision false)
  ))
  (limits ({}
    (contextWindow 65536)
    (maxOutputTokens null)
  ))
  (pricing ({}
    (prompt "0.000002")
    (completion "0.000006")
    (input_cache_read "0.0000002")
  ))
  (properties ({}
    (id mistralai/mixtral-8x22b-instruct)
    (canonical_slug mistralai/mixtral-8x22b-instruct)
    (hugging_face_id mistralai/Mixtral-8x22B-Instruct-v0.1)
    (name "Mistral: Mixtral 8x22B Instruct")
    (created 1713312000)
    (description "Mistral's official instruct fine-tuned version of [Mixtral 8x22B](/models/mistralai/mixtral-8x22b). It uses 39B active parameters out of 141B, offering unparalleled cost efficiency for its size. Its strengths include: - strong math, coding,...")
    (context_length 65536)
    (architecture ({}
      (modality text+file->text)
      (input_modalities (
        text
        file
      ))
      (output_modalities (
        text
      ))
      (tokenizer Mistral)
      (instruct_type mistral)
    ))
    (pricing ({}
      (prompt "0.000002")
      (completion "0.000006")
      (input_cache_read "0.0000002")
    ))
    (top_provider ({}
      (context_length 65536)
      (max_completion_tokens null)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      max_tokens
      presence_penalty
      response_format
      seed
      stop
      structured_outputs
      temperature
      tool_choice
      tools
      top_p
    ))
    (default_parameters ({}
      (temperature 0.3)
    ))
    (supported_voices null)
    (knowledge_cutoff 2024-01-31)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/mistralai/mixtral-8x22b-instruct/endpoints)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id mistralai/mixtral-8x22b-instruct)
    (canonical_slug mistralai/mixtral-8x22b-instruct)
    (hugging_face_id mistralai/Mixtral-8x22B-Instruct-v0.1)
    (name "Mistral: Mixtral 8x22B Instruct")
    (created 1713312000)
    (description "Mistral's official instruct fine-tuned version of [Mixtral 8x22B](/models/mistralai/mixtral-8x22b). It uses 39B active parameters out of 141B, offering unparalleled cost efficiency for its size. Its strengths include: - strong math, coding,...")
    (context_length 65536)
    (architecture ({}
      (modality text+file->text)
      (input_modalities (
        text
        file
      ))
      (output_modalities (
        text
      ))
      (tokenizer Mistral)
      (instruct_type mistral)
    ))
    (pricing ({}
      (prompt "0.000002")
      (completion "0.000006")
      (input_cache_read "0.0000002")
    ))
    (top_provider ({}
      (context_length 65536)
      (max_completion_tokens null)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      max_tokens
      presence_penalty
      response_format
      seed
      stop
      structured_outputs
      temperature
      tool_choice
      tools
      top_p
    ))
    (default_parameters ({}
      (temperature 0.3)
    ))
    (supported_voices null)
    (knowledge_cutoff 2024-01-31)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/mistralai/mixtral-8x22b-instruct/endpoints)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId mistralai/mixtral-8x22b-instruct)
  ))
)
