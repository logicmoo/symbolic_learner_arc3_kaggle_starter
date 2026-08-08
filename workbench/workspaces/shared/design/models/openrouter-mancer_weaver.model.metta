(
  (kind model)
  (id openrouter-mancer_weaver)
  (label "Mancer: Weaver (alpha)")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model mancer/weaver)
  (enabled true)
  (capabilities (
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
  (limits (
    (contextWindow 8000)
    (maxOutputTokens 6000)
  ))
  (pricing (
    (prompt "0.0000005")
    (completion "0.00000075")
  ))
  (properties (
    (id mancer/weaver)
    (canonical_slug mancer/weaver)
    (hugging_face_id null)
    (name "Mancer: Weaver (alpha)")
    (created 1690934400)
    (description "An attempt to recreate Claude-style verbosity, but don't expect the same level of coherence or memory. Meant for use in roleplay/narrative situations.")
    (context_length 8000)
    (architecture (
      (modality text->text)
      (input_modalities ([]
        text
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Llama2)
      (instruct_type alpaca)
    ))
    (pricing (
      (prompt "0.0000005")
      (completion "0.00000075")
    ))
    (top_provider (
      (context_length 8000)
      (max_completion_tokens 6000)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      frequency_penalty
      logit_bias
      logprobs
      max_tokens
      min_p
      presence_penalty
      repetition_penalty
      response_format
      seed
      stop
      structured_outputs
      temperature
      top_a
      top_k
      top_logprobs
      top_p
    ))
    (default_parameters ())
    (supported_voices null)
    (knowledge_cutoff 2023-06-30)
    (expiration_date null)
    (links (
      (details /api/v1/models/mancer/weaver/endpoints)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id mancer/weaver)
    (canonical_slug mancer/weaver)
    (hugging_face_id null)
    (name "Mancer: Weaver (alpha)")
    (created 1690934400)
    (description "An attempt to recreate Claude-style verbosity, but don't expect the same level of coherence or memory. Meant for use in roleplay/narrative situations.")
    (context_length 8000)
    (architecture (
      (modality text->text)
      (input_modalities ([]
        text
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Llama2)
      (instruct_type alpaca)
    ))
    (pricing (
      (prompt "0.0000005")
      (completion "0.00000075")
    ))
    (top_provider (
      (context_length 8000)
      (max_completion_tokens 6000)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      frequency_penalty
      logit_bias
      logprobs
      max_tokens
      min_p
      presence_penalty
      repetition_penalty
      response_format
      seed
      stop
      structured_outputs
      temperature
      top_a
      top_k
      top_logprobs
      top_p
    ))
    (default_parameters ())
    (supported_voices null)
    (knowledge_cutoff 2023-06-30)
    (expiration_date null)
    (links (
      (details /api/v1/models/mancer/weaver/endpoints)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId mancer/weaver)
  ))
)
