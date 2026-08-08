({}
  (kind model)
  (id openrouter-writer_palmyra-x5)
  (label "Writer: Palmyra X5")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model writer/palmyra-x5)
  (enabled true)
  (capabilities ({}
    (audio false)
    (code false)
    (functionCalling false)
    (json false)
    (jsonMode false)
    (local false)
    (multimodal false)
    (reasoning false)
    (text true)
    (tools false)
    (vision false)
  ))
  (limits ({}
    (contextWindow 1040000)
    (maxOutputTokens 8192)
  ))
  (pricing ({}
    (prompt "0.0000006")
    (completion "0.000006")
  ))
  (properties ({}
    (id writer/palmyra-x5)
    (canonical_slug writer/palmyra-x5-20250428)
    (hugging_face_id "")
    (name "Writer: Palmyra X5")
    (created 1769003823)
    (description "Palmyra X5 is Writer's most advanced model, purpose-built for building and scaling AI agents across the enterprise. It delivers industry-leading speed and efficiency on context windows up to 1 million...")
    (context_length 1040000)
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
      (prompt "0.0000006")
      (completion "0.000006")
    ))
    (top_provider ({}
      (context_length 1040000)
      (max_completion_tokens 8192)
      (is_moderated true)
    ))
    (per_request_limits null)
    (supported_parameters (
      max_tokens
      stop
      temperature
      top_k
      top_p
    ))
    (default_parameters ({}
      (temperature null)
      (top_p null)
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/writer/palmyra-x5-20250428/endpoints)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id writer/palmyra-x5)
    (canonical_slug writer/palmyra-x5-20250428)
    (hugging_face_id "")
    (name "Writer: Palmyra X5")
    (created 1769003823)
    (description "Palmyra X5 is Writer's most advanced model, purpose-built for building and scaling AI agents across the enterprise. It delivers industry-leading speed and efficiency on context windows up to 1 million...")
    (context_length 1040000)
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
      (prompt "0.0000006")
      (completion "0.000006")
    ))
    (top_provider ({}
      (context_length 1040000)
      (max_completion_tokens 8192)
      (is_moderated true)
    ))
    (per_request_limits null)
    (supported_parameters (
      max_tokens
      stop
      temperature
      top_k
      top_p
    ))
    (default_parameters ({}
      (temperature null)
      (top_p null)
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/writer/palmyra-x5-20250428/endpoints)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId writer/palmyra-x5)
  ))
)
