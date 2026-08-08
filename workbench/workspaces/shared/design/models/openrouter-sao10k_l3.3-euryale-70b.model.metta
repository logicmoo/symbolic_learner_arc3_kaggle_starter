(
  (kind model)
  (id openrouter-sao10k_l3.3-euryale-70b)
  (label "Sao10K: Llama 3.3 Euryale 70B")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model sao10k/l3.3-euryale-70b)
  (enabled true)
  (capabilities (
    (audio false)
    (code false)
    (functionCalling false)
    (json true)
    (jsonMode true)
    (local false)
    (multimodal false)
    (reasoning true)
    (text true)
    (tools false)
    (vision false)
  ))
  (limits (
    (contextWindow 131072)
    (maxOutputTokens 16384)
  ))
  (pricing (
    (prompt "0.00000065")
    (completion "0.00000075")
  ))
  (properties (
    (id sao10k/l3.3-euryale-70b)
    (canonical_slug sao10k/l3.3-euryale-70b-v2.3)
    (hugging_face_id Sao10K/L3.3-70B-Euryale-v2.3)
    (name "Sao10K: Llama 3.3 Euryale 70B")
    (created 1734535928)
    (description "Euryale L3.3 70B is a model focused on creative roleplay from [Sao10k](https://ko-fi.com/sao10k). It is the successor of [Euryale L3 70B v2.2](/models/sao10k/l3-euryale-70b).")
    (context_length 131072)
    (architecture (
      (modality text->text)
      (input_modalities ([]
        text
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Llama3)
      (instruct_type llama3)
    ))
    (pricing (
      (prompt "0.00000065")
      (completion "0.00000075")
    ))
    (top_provider (
      (context_length 131072)
      (max_completion_tokens 16384)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      frequency_penalty
      logprobs
      max_tokens
      presence_penalty
      repetition_penalty
      response_format
      seed
      stop
      structured_outputs
      temperature
      top_logprobs
      top_p
    ))
    (default_parameters ())
    (supported_voices null)
    (knowledge_cutoff 2023-12-31)
    (expiration_date null)
    (links (
      (details /api/v1/models/sao10k/l3.3-euryale-70b-v2.3/endpoints)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id sao10k/l3.3-euryale-70b)
    (canonical_slug sao10k/l3.3-euryale-70b-v2.3)
    (hugging_face_id Sao10K/L3.3-70B-Euryale-v2.3)
    (name "Sao10K: Llama 3.3 Euryale 70B")
    (created 1734535928)
    (description "Euryale L3.3 70B is a model focused on creative roleplay from [Sao10k](https://ko-fi.com/sao10k). It is the successor of [Euryale L3 70B v2.2](/models/sao10k/l3-euryale-70b).")
    (context_length 131072)
    (architecture (
      (modality text->text)
      (input_modalities ([]
        text
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Llama3)
      (instruct_type llama3)
    ))
    (pricing (
      (prompt "0.00000065")
      (completion "0.00000075")
    ))
    (top_provider (
      (context_length 131072)
      (max_completion_tokens 16384)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      frequency_penalty
      logprobs
      max_tokens
      presence_penalty
      repetition_penalty
      response_format
      seed
      stop
      structured_outputs
      temperature
      top_logprobs
      top_p
    ))
    (default_parameters ())
    (supported_voices null)
    (knowledge_cutoff 2023-12-31)
    (expiration_date null)
    (links (
      (details /api/v1/models/sao10k/l3.3-euryale-70b-v2.3/endpoints)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId sao10k/l3.3-euryale-70b)
  ))
)
