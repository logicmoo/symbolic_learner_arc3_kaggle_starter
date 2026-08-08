({}
  (kind model)
  (id openrouter-google_gemma-2-27b-it)
  (label "Google: Gemma 2 27B")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model google/gemma-2-27b-it)
  (enabled true)
  (capabilities ({}
    (audio false)
    (code false)
    (functionCalling false)
    (json true)
    (jsonMode true)
    (local false)
    (multimodal false)
    (reasoning false)
    (text true)
    (tools false)
    (vision false)
  ))
  (limits ({}
    (contextWindow 8192)
    (maxOutputTokens 2048)
  ))
  (pricing ({}
    (prompt "0.00000065")
    (completion "0.00000065")
  ))
  (properties ({}
    (id google/gemma-2-27b-it)
    (canonical_slug google/gemma-2-27b-it)
    (hugging_face_id google/gemma-2-27b-it)
    (name "Google: Gemma 2 27B")
    (created 1720828800)
    (description "Gemma 2 27B by Google is an open model built from the same research and technology used to create the [Gemini models](/models?q=gemini). Gemma models are well-suited for a variety of...")
    (context_length 8192)
    (architecture ({}
      (modality text->text)
      (input_modalities (
        text
      ))
      (output_modalities (
        text
      ))
      (tokenizer Gemini)
      (instruct_type gemma)
    ))
    (pricing ({}
      (prompt "0.00000065")
      (completion "0.00000065")
    ))
    (top_provider ({}
      (context_length 8192)
      (max_completion_tokens 2048)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      max_tokens
      presence_penalty
      repetition_penalty
      response_format
      seed
      stop
      structured_outputs
      temperature
      top_p
    ))
    (default_parameters ({}))
    (supported_voices null)
    (knowledge_cutoff 2024-06-30)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/google/gemma-2-27b-it/endpoints)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id google/gemma-2-27b-it)
    (canonical_slug google/gemma-2-27b-it)
    (hugging_face_id google/gemma-2-27b-it)
    (name "Google: Gemma 2 27B")
    (created 1720828800)
    (description "Gemma 2 27B by Google is an open model built from the same research and technology used to create the [Gemini models](/models?q=gemini). Gemma models are well-suited for a variety of...")
    (context_length 8192)
    (architecture ({}
      (modality text->text)
      (input_modalities (
        text
      ))
      (output_modalities (
        text
      ))
      (tokenizer Gemini)
      (instruct_type gemma)
    ))
    (pricing ({}
      (prompt "0.00000065")
      (completion "0.00000065")
    ))
    (top_provider ({}
      (context_length 8192)
      (max_completion_tokens 2048)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      max_tokens
      presence_penalty
      repetition_penalty
      response_format
      seed
      stop
      structured_outputs
      temperature
      top_p
    ))
    (default_parameters ({}))
    (supported_voices null)
    (knowledge_cutoff 2024-06-30)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/google/gemma-2-27b-it/endpoints)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId google/gemma-2-27b-it)
  ))
)
