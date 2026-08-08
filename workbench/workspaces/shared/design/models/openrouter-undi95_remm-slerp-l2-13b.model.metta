({}
  (kind model)
  (id openrouter-undi95_remm-slerp-l2-13b)
  (label "ReMM SLERP 13B")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model undi95/remm-slerp-l2-13b)
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
    (contextWindow 6144)
    (maxOutputTokens 6144)
  ))
  (pricing ({}
    (prompt "0.00000045")
    (completion "0.00000065")
  ))
  (properties ({}
    (id undi95/remm-slerp-l2-13b)
    (canonical_slug undi95/remm-slerp-l2-13b)
    (hugging_face_id Undi95/ReMM-SLERP-L2-13B)
    (name "ReMM SLERP 13B")
    (created 1689984000)
    (description "A recreation trial of the original MythoMax-L2-B13 but with updated models. #merge")
    (context_length 6144)
    (architecture ({}
      (modality text->text)
      (input_modalities (
        text
      ))
      (output_modalities (
        text
      ))
      (tokenizer Llama2)
      (instruct_type alpaca)
    ))
    (pricing ({}
      (prompt "0.00000045")
      (completion "0.00000065")
    ))
    (top_provider ({}
      (context_length 6144)
      (max_completion_tokens 6144)
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
      structured_outputs
      temperature
      top_a
      top_k
      top_logprobs
      top_p
    ))
    (default_parameters ({}))
    (supported_voices null)
    (knowledge_cutoff 2023-06-30)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/undi95/remm-slerp-l2-13b/endpoints)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id undi95/remm-slerp-l2-13b)
    (canonical_slug undi95/remm-slerp-l2-13b)
    (hugging_face_id Undi95/ReMM-SLERP-L2-13B)
    (name "ReMM SLERP 13B")
    (created 1689984000)
    (description "A recreation trial of the original MythoMax-L2-B13 but with updated models. #merge")
    (context_length 6144)
    (architecture ({}
      (modality text->text)
      (input_modalities (
        text
      ))
      (output_modalities (
        text
      ))
      (tokenizer Llama2)
      (instruct_type alpaca)
    ))
    (pricing ({}
      (prompt "0.00000045")
      (completion "0.00000065")
    ))
    (top_provider ({}
      (context_length 6144)
      (max_completion_tokens 6144)
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
      structured_outputs
      temperature
      top_a
      top_k
      top_logprobs
      top_p
    ))
    (default_parameters ({}))
    (supported_voices null)
    (knowledge_cutoff 2023-06-30)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/undi95/remm-slerp-l2-13b/endpoints)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId undi95/remm-slerp-l2-13b)
  ))
)
