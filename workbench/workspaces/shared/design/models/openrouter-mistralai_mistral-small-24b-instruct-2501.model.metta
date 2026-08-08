(
  (kind model)
  (id openrouter-mistralai_mistral-small-24b-instruct-2501)
  (label "Mistral: Mistral Small 3")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model mistralai/mistral-small-24b-instruct-2501)
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
    (contextWindow 32768)
    (maxOutputTokens 16384)
  ))
  (pricing (
    (prompt "0.00000005")
    (completion "0.00000008")
  ))
  (properties (
    (id mistralai/mistral-small-24b-instruct-2501)
    (canonical_slug mistralai/mistral-small-24b-instruct-2501)
    (hugging_face_id mistralai/Mistral-Small-24B-Instruct-2501)
    (name "Mistral: Mistral Small 3")
    (created 1738255409)
    (description "Mistral Small 3 is a 24B-parameter language model optimized for low-latency performance across common AI tasks. Released under the Apache 2.0 license, it features both pre-trained and instruction-tuned versions designed...")
    (context_length 32768)
    (architecture (
      (modality text->text)
      (input_modalities ([]
        text
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Mistral)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.00000005")
      (completion "0.00000008")
    ))
    (top_provider (
      (context_length 32768)
      (max_completion_tokens 16384)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      frequency_penalty
      logit_bias
      max_tokens
      min_p
      presence_penalty
      repetition_penalty
      response_format
      seed
      stop
      structured_outputs
      temperature
      top_k
      top_p
    ))
    (default_parameters (
      (temperature 0.3)
      (top_p null)
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff 2023-10-31)
    (expiration_date null)
    (links (
      (details /api/v1/models/mistralai/mistral-small-24b-instruct-2501/endpoints)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id mistralai/mistral-small-24b-instruct-2501)
    (canonical_slug mistralai/mistral-small-24b-instruct-2501)
    (hugging_face_id mistralai/Mistral-Small-24B-Instruct-2501)
    (name "Mistral: Mistral Small 3")
    (created 1738255409)
    (description "Mistral Small 3 is a 24B-parameter language model optimized for low-latency performance across common AI tasks. Released under the Apache 2.0 license, it features both pre-trained and instruction-tuned versions designed...")
    (context_length 32768)
    (architecture (
      (modality text->text)
      (input_modalities ([]
        text
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Mistral)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.00000005")
      (completion "0.00000008")
    ))
    (top_provider (
      (context_length 32768)
      (max_completion_tokens 16384)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      frequency_penalty
      logit_bias
      max_tokens
      min_p
      presence_penalty
      repetition_penalty
      response_format
      seed
      stop
      structured_outputs
      temperature
      top_k
      top_p
    ))
    (default_parameters (
      (temperature 0.3)
      (top_p null)
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff 2023-10-31)
    (expiration_date null)
    (links (
      (details /api/v1/models/mistralai/mistral-small-24b-instruct-2501/endpoints)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId mistralai/mistral-small-24b-instruct-2501)
  ))
)
