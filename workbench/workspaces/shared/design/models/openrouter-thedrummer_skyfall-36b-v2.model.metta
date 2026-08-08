({}
  (kind model)
  (id openrouter-thedrummer_skyfall-36b-v2)
  (label "TheDrummer: Skyfall 36B V2")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model thedrummer/skyfall-36b-v2)
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
    (contextWindow 32768)
    (maxOutputTokens 32768)
  ))
  (pricing ({}
    (prompt "0.00000055")
    (completion "0.0000008")
    (input_cache_read "0.00000025")
  ))
  (properties ({}
    (id thedrummer/skyfall-36b-v2)
    (canonical_slug thedrummer/skyfall-36b-v2)
    (hugging_face_id TheDrummer/Skyfall-36B-v2)
    (name "TheDrummer: Skyfall 36B V2")
    (created 1741636566)
    (description "Skyfall 36B v2 is an enhanced iteration of Mistral Small 2501, specifically fine-tuned for improved creativity, nuanced writing, role-playing, and coherent storytelling.")
    (context_length 32768)
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
      (prompt "0.00000055")
      (completion "0.0000008")
      (input_cache_read "0.00000025")
    ))
    (top_provider ({}
      (context_length 32768)
      (max_completion_tokens 32768)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      logit_bias
      logprobs
      max_tokens
      presence_penalty
      repetition_penalty
      response_format
      seed
      stop
      structured_outputs
      temperature
      top_k
      top_logprobs
      top_p
    ))
    (default_parameters ({}))
    (supported_voices null)
    (knowledge_cutoff 2024-06-30)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/thedrummer/skyfall-36b-v2/endpoints)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id thedrummer/skyfall-36b-v2)
    (canonical_slug thedrummer/skyfall-36b-v2)
    (hugging_face_id TheDrummer/Skyfall-36B-v2)
    (name "TheDrummer: Skyfall 36B V2")
    (created 1741636566)
    (description "Skyfall 36B v2 is an enhanced iteration of Mistral Small 2501, specifically fine-tuned for improved creativity, nuanced writing, role-playing, and coherent storytelling.")
    (context_length 32768)
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
      (prompt "0.00000055")
      (completion "0.0000008")
      (input_cache_read "0.00000025")
    ))
    (top_provider ({}
      (context_length 32768)
      (max_completion_tokens 32768)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      logit_bias
      logprobs
      max_tokens
      presence_penalty
      repetition_penalty
      response_format
      seed
      stop
      structured_outputs
      temperature
      top_k
      top_logprobs
      top_p
    ))
    (default_parameters ({}))
    (supported_voices null)
    (knowledge_cutoff 2024-06-30)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/thedrummer/skyfall-36b-v2/endpoints)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId thedrummer/skyfall-36b-v2)
  ))
)
