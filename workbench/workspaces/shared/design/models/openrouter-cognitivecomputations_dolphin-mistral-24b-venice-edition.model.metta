({}
  (kind model)
  (id openrouter-cognitivecomputations_dolphin-mistral-24b-venice-edition)
  (label "Venice: Uncensored")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model cognitivecomputations/dolphin-mistral-24b-venice-edition)
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
    (contextWindow 128000)
    (maxOutputTokens 8192)
  ))
  (pricing ({}
    (prompt "0.0000002")
    (completion "0.0000009")
  ))
  (properties ({}
    (id cognitivecomputations/dolphin-mistral-24b-venice-edition)
    (canonical_slug venice/uncensored)
    (hugging_face_id cognitivecomputations/Dolphin-Mistral-24B-Venice-Edition)
    (name "Venice: Uncensored")
    (created 1752094966)
    (description "Venice Uncensored Dolphin Mistral 24B Venice Edition is a fine-tuned variant of Mistral-Small-24B-Instruct-2501, developed by dphn.ai in collaboration with Venice.ai. This model is designed as an “uncensored” instruct-tuned LLM, preserving...")
    (context_length 128000)
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
      (prompt "0.0000002")
      (completion "0.0000009")
    ))
    (top_provider ({}
      (context_length 128000)
      (max_completion_tokens 8192)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      max_tokens
      presence_penalty
      response_format
      stop
      temperature
      top_k
      top_p
    ))
    (default_parameters ({}))
    (supported_voices null)
    (knowledge_cutoff 2024-04-30)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/venice/uncensored/endpoints)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id cognitivecomputations/dolphin-mistral-24b-venice-edition)
    (canonical_slug venice/uncensored)
    (hugging_face_id cognitivecomputations/Dolphin-Mistral-24B-Venice-Edition)
    (name "Venice: Uncensored")
    (created 1752094966)
    (description "Venice Uncensored Dolphin Mistral 24B Venice Edition is a fine-tuned variant of Mistral-Small-24B-Instruct-2501, developed by dphn.ai in collaboration with Venice.ai. This model is designed as an “uncensored” instruct-tuned LLM, preserving...")
    (context_length 128000)
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
      (prompt "0.0000002")
      (completion "0.0000009")
    ))
    (top_provider ({}
      (context_length 128000)
      (max_completion_tokens 8192)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      max_tokens
      presence_penalty
      response_format
      stop
      temperature
      top_k
      top_p
    ))
    (default_parameters ({}))
    (supported_voices null)
    (knowledge_cutoff 2024-04-30)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/venice/uncensored/endpoints)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId cognitivecomputations/dolphin-mistral-24b-venice-edition)
  ))
)
