(
  (kind model)
  (id openrouter-mistralai_mistral-small-3.1-24b-instruct)
  (label "Mistral: Mistral Small 3.1 24B")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model mistralai/mistral-small-3.1-24b-instruct)
  (enabled true)
  (capabilities (
    (audio false)
    (code false)
    (functionCalling false)
    (json false)
    (jsonMode false)
    (local false)
    (multimodal true)
    (reasoning false)
    (text true)
    (tools false)
    (vision true)
  ))
  (limits (
    (contextWindow 128000)
    (maxOutputTokens 128000)
  ))
  (pricing (
    (prompt "0.000000351")
    (completion "0.000000555")
  ))
  (properties (
    (id mistralai/mistral-small-3.1-24b-instruct)
    (canonical_slug mistralai/mistral-small-3.1-24b-instruct-2503)
    (hugging_face_id mistralai/Mistral-Small-3.1-24B-Instruct-2503)
    (name "Mistral: Mistral Small 3.1 24B")
    (created 1742238937)
    (description "Mistral Small 3.1 24B Instruct is an upgraded variant of Mistral Small 3 (2501), featuring 24 billion parameters with advanced multimodal capabilities. It provides state-of-the-art performance in text-based reasoning and...")
    (context_length 128000)
    (architecture (
      (modality text+image->text)
      (input_modalities ([]
        text
        image
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Mistral)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.000000351")
      (completion "0.000000555")
    ))
    (top_provider (
      (context_length 128000)
      (max_completion_tokens 128000)
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
      seed
      stop
      temperature
      top_k
      top_logprobs
      top_p
    ))
    (default_parameters (
      (temperature 0.3)
    ))
    (supported_voices null)
    (knowledge_cutoff 2023-10-31)
    (expiration_date null)
    (links (
      (details /api/v1/models/mistralai/mistral-small-3.1-24b-instruct-2503/endpoints)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id mistralai/mistral-small-3.1-24b-instruct)
    (canonical_slug mistralai/mistral-small-3.1-24b-instruct-2503)
    (hugging_face_id mistralai/Mistral-Small-3.1-24B-Instruct-2503)
    (name "Mistral: Mistral Small 3.1 24B")
    (created 1742238937)
    (description "Mistral Small 3.1 24B Instruct is an upgraded variant of Mistral Small 3 (2501), featuring 24 billion parameters with advanced multimodal capabilities. It provides state-of-the-art performance in text-based reasoning and...")
    (context_length 128000)
    (architecture (
      (modality text+image->text)
      (input_modalities ([]
        text
        image
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Mistral)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.000000351")
      (completion "0.000000555")
    ))
    (top_provider (
      (context_length 128000)
      (max_completion_tokens 128000)
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
      seed
      stop
      temperature
      top_k
      top_logprobs
      top_p
    ))
    (default_parameters (
      (temperature 0.3)
    ))
    (supported_voices null)
    (knowledge_cutoff 2023-10-31)
    (expiration_date null)
    (links (
      (details /api/v1/models/mistralai/mistral-small-3.1-24b-instruct-2503/endpoints)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId mistralai/mistral-small-3.1-24b-instruct)
  ))
)
