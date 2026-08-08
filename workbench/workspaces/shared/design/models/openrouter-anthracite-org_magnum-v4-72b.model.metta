({}
  (kind model)
  (id openrouter-anthracite-org_magnum-v4-72b)
  (label "Magnum v4 72B")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model anthracite-org/magnum-v4-72b)
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
    (contextWindow 16384)
    (maxOutputTokens 2048)
  ))
  (pricing ({}
    (prompt "0.000003")
    (completion "0.000005")
  ))
  (properties ({}
    (id anthracite-org/magnum-v4-72b)
    (canonical_slug anthracite-org/magnum-v4-72b)
    (hugging_face_id anthracite-org/magnum-v4-72b)
    (name "Magnum v4 72B")
    (created 1729555200)
    (description "This is a series of models designed to replicate the prose quality of the Claude 3 models, specifically Sonnet(https://openrouter.ai/anthropic/claude-3.5-sonnet) and Opus(https://openrouter.ai/anthropic/claude-3-opus).\n\nThe model is fine-tuned on top of [Qwen2.5 72B](https://openrouter.ai/qwen/qwen-2.5-72b-instruct).")
    (context_length 16384)
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
      (prompt "0.000003")
      (completion "0.000005")
    ))
    (top_provider ({}
      (context_length 16384)
      (max_completion_tokens 2048)
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
    (knowledge_cutoff 2024-06-30)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/anthracite-org/magnum-v4-72b/endpoints)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id anthracite-org/magnum-v4-72b)
    (canonical_slug anthracite-org/magnum-v4-72b)
    (hugging_face_id anthracite-org/magnum-v4-72b)
    (name "Magnum v4 72B")
    (created 1729555200)
    (description "This is a series of models designed to replicate the prose quality of the Claude 3 models, specifically Sonnet(https://openrouter.ai/anthropic/claude-3.5-sonnet) and Opus(https://openrouter.ai/anthropic/claude-3-opus).\n\nThe model is fine-tuned on top of [Qwen2.5 72B](https://openrouter.ai/qwen/qwen-2.5-72b-instruct).")
    (context_length 16384)
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
      (prompt "0.000003")
      (completion "0.000005")
    ))
    (top_provider ({}
      (context_length 16384)
      (max_completion_tokens 2048)
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
    (knowledge_cutoff 2024-06-30)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/anthracite-org/magnum-v4-72b/endpoints)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId anthracite-org/magnum-v4-72b)
  ))
)
