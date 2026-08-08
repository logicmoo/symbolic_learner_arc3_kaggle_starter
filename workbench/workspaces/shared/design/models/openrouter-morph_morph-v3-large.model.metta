({}
  (kind model)
  (id openrouter-morph_morph-v3-large)
  (label "Morph: Morph V3 Large")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model morph/morph-v3-large)
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
    (contextWindow 262144)
    (maxOutputTokens 131072)
  ))
  (pricing ({}
    (prompt "0.0000009")
    (completion "0.0000019")
  ))
  (properties ({}
    (id morph/morph-v3-large)
    (canonical_slug morph/morph-v3-large)
    (hugging_face_id "")
    (name "Morph: Morph V3 Large")
    (created 1751910858)
    (description "Morph's high-accuracy apply model for complex code edits. ~4,500 tokens/sec with 98% accuracy for precise code transformations. The model requires the prompt to be in the following format: <instruction>{instruction}</instruction> <code>{initial_code}</code>...")
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
      (prompt "0.0000009")
      (completion "0.0000019")
    ))
    (top_provider ({}
      (context_length 262144)
      (max_completion_tokens 131072)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      logprobs
      max_tokens
      response_format
      stop
      structured_outputs
      temperature
      top_logprobs
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
      (details /api/v1/models/morph/morph-v3-large/endpoints)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id morph/morph-v3-large)
    (canonical_slug morph/morph-v3-large)
    (hugging_face_id "")
    (name "Morph: Morph V3 Large")
    (created 1751910858)
    (description "Morph's high-accuracy apply model for complex code edits. ~4,500 tokens/sec with 98% accuracy for precise code transformations. The model requires the prompt to be in the following format: <instruction>{instruction}</instruction> <code>{initial_code}</code>...")
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
      (prompt "0.0000009")
      (completion "0.0000019")
    ))
    (top_provider ({}
      (context_length 262144)
      (max_completion_tokens 131072)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      logprobs
      max_tokens
      response_format
      stop
      structured_outputs
      temperature
      top_logprobs
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
      (details /api/v1/models/morph/morph-v3-large/endpoints)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId morph/morph-v3-large)
  ))
)
