({}
  (kind model)
  (id openrouter-thedrummer_rocinante-12b)
  (label "TheDrummer: Rocinante 12B")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model thedrummer/rocinante-12b)
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
    (contextWindow 65536)
    (maxOutputTokens 65536)
  ))
  (pricing ({}
    (prompt "0.00000025")
    (completion "0.0000005")
  ))
  (properties ({}
    (id thedrummer/rocinante-12b)
    (canonical_slug thedrummer/rocinante-12b)
    (hugging_face_id TheDrummer/Rocinante-12B-v1.1)
    (name "TheDrummer: Rocinante 12B")
    (created 1727654400)
    (description "Rocinante 12B is designed for engaging storytelling and rich prose. Early testers have reported: - Expanded vocabulary with unique and expressive word choices - Enhanced creativity for vivid narratives -...")
    (context_length 65536)
    (architecture ({}
      (modality text->text)
      (input_modalities (
        text
      ))
      (output_modalities (
        text
      ))
      (tokenizer Qwen)
      (instruct_type chatml)
    ))
    (pricing ({}
      (prompt "0.00000025")
      (completion "0.0000005")
    ))
    (top_provider ({}
      (context_length 65536)
      (max_completion_tokens 65536)
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
    (knowledge_cutoff 2024-04-30)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/thedrummer/rocinante-12b/endpoints)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id thedrummer/rocinante-12b)
    (canonical_slug thedrummer/rocinante-12b)
    (hugging_face_id TheDrummer/Rocinante-12B-v1.1)
    (name "TheDrummer: Rocinante 12B")
    (created 1727654400)
    (description "Rocinante 12B is designed for engaging storytelling and rich prose. Early testers have reported: - Expanded vocabulary with unique and expressive word choices - Enhanced creativity for vivid narratives -...")
    (context_length 65536)
    (architecture ({}
      (modality text->text)
      (input_modalities (
        text
      ))
      (output_modalities (
        text
      ))
      (tokenizer Qwen)
      (instruct_type chatml)
    ))
    (pricing ({}
      (prompt "0.00000025")
      (completion "0.0000005")
    ))
    (top_provider ({}
      (context_length 65536)
      (max_completion_tokens 65536)
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
    (knowledge_cutoff 2024-04-30)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/thedrummer/rocinante-12b/endpoints)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId thedrummer/rocinante-12b)
  ))
)
