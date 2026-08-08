({}
  (kind model)
  (id openrouter-ibm-granite_granite-4.0-h-micro)
  (label "IBM: Granite 4.0 Micro")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model ibm-granite/granite-4.0-h-micro)
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
    (contextWindow 131000)
    (maxOutputTokens 131000)
  ))
  (pricing ({}
    (prompt "0.000000017")
    (completion "0.000000112")
  ))
  (properties ({}
    (id ibm-granite/granite-4.0-h-micro)
    (canonical_slug ibm-granite/granite-4.0-h-micro)
    (hugging_face_id ibm-granite/granite-4.0-h-micro)
    (name "IBM: Granite 4.0 Micro")
    (created 1760927695)
    (description "Granite-4.0-H-Micro is a 3B parameter from the Granite 4 family of models. These models are the latest in a series of models released by IBM. They are fine-tuned for long...")
    (context_length 131000)
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
      (prompt "0.000000017")
      (completion "0.000000112")
    ))
    (top_provider ({}
      (context_length 131000)
      (max_completion_tokens 131000)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
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
      temperature
      top_k
      top_logprobs
      top_p
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
      (details /api/v1/models/ibm-granite/granite-4.0-h-micro/endpoints)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id ibm-granite/granite-4.0-h-micro)
    (canonical_slug ibm-granite/granite-4.0-h-micro)
    (hugging_face_id ibm-granite/granite-4.0-h-micro)
    (name "IBM: Granite 4.0 Micro")
    (created 1760927695)
    (description "Granite-4.0-H-Micro is a 3B parameter from the Granite 4 family of models. These models are the latest in a series of models released by IBM. They are fine-tuned for long...")
    (context_length 131000)
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
      (prompt "0.000000017")
      (completion "0.000000112")
    ))
    (top_provider ({}
      (context_length 131000)
      (max_completion_tokens 131000)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
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
      temperature
      top_k
      top_logprobs
      top_p
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
      (details /api/v1/models/ibm-granite/granite-4.0-h-micro/endpoints)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId ibm-granite/granite-4.0-h-micro)
  ))
)
