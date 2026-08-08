({}
  (kind model)
  (id openrouter-mistralai_mistral-saba)
  (label "Mistral: Saba")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model mistralai/mistral-saba)
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
    (contextWindow 32768)
    (maxOutputTokens null)
  ))
  (pricing ({}
    (prompt "0.0000002")
    (completion "0.0000006")
    (input_cache_read "0.00000002")
  ))
  (properties ({}
    (id mistralai/mistral-saba)
    (canonical_slug mistralai/mistral-saba-2502)
    (hugging_face_id "")
    (name "Mistral: Saba")
    (created 1739803239)
    (description "Mistral Saba is a 24B-parameter language model specifically designed for the Middle East and South Asia, delivering accurate and contextually relevant responses while maintaining efficient performance. Trained on curated regional...")
    (context_length 32768)
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
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.0000002")
      (completion "0.0000006")
      (input_cache_read "0.00000002")
    ))
    (top_provider ({}
      (context_length 32768)
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
    (knowledge_cutoff 2024-09-30)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/mistralai/mistral-saba-2502/endpoints)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id mistralai/mistral-saba)
    (canonical_slug mistralai/mistral-saba-2502)
    (hugging_face_id "")
    (name "Mistral: Saba")
    (created 1739803239)
    (description "Mistral Saba is a 24B-parameter language model specifically designed for the Middle East and South Asia, delivering accurate and contextually relevant responses while maintaining efficient performance. Trained on curated regional...")
    (context_length 32768)
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
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.0000002")
      (completion "0.0000006")
      (input_cache_read "0.00000002")
    ))
    (top_provider ({}
      (context_length 32768)
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
    (knowledge_cutoff 2024-09-30)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/mistralai/mistral-saba-2502/endpoints)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId mistralai/mistral-saba)
  ))
)
