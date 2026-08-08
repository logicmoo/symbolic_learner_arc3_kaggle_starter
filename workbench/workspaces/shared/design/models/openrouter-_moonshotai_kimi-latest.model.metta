({}
  (kind model)
  (id openrouter-_moonshotai_kimi-latest)
  (label "MoonshotAI Kimi Latest")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model ~moonshotai/kimi-latest)
  (enabled true)
  (capabilities ({}
    (audio false)
    (code false)
    (functionCalling true)
    (json true)
    (jsonMode true)
    (local false)
    (multimodal true)
    (reasoning true)
    (text true)
    (tools true)
    (vision true)
  ))
  (limits ({}
    (contextWindow 1048576)
    (maxOutputTokens 1048576)
  ))
  (pricing ({}
    (prompt "0.0000025")
    (completion "0.000014")
    (input_cache_read "0.00000029")
  ))
  (properties ({}
    (id ~moonshotai/kimi-latest)
    (canonical_slug ~moonshotai/kimi-latest)
    (alias_target ({}
      (name "MoonshotAI: Kimi K3")
      (slug moonshotai/kimi-k3)
    ))
    (hugging_face_id null)
    (name "MoonshotAI Kimi Latest")
    (created 1777318428)
    (description "This model always redirects to the latest model in the MoonshotAI Kimi family.")
    (context_length 1048576)
    (architecture ({}
      (modality text+image->text)
      (input_modalities (
        text
        image
      ))
      (output_modalities (
        text
      ))
      (tokenizer Router)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.0000025")
      (completion "0.000014")
      (input_cache_read "0.00000029")
    ))
    (top_provider ({}
      (context_length 1048576)
      (max_completion_tokens 1048576)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      include_reasoning
      logit_bias
      logprobs
      max_tokens
      min_p
      presence_penalty
      reasoning
      reasoning_effort
      repetition_penalty
      response_format
      seed
      stop
      structured_outputs
      temperature
      tool_choice
      tools
      top_k
      top_logprobs
      top_p
    ))
    (default_parameters ({}
      (temperature null)
      (top_p 0.95)
      (top_k null)
      (frequency_penalty null)
      (presence_penalty null)
      (repetition_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/~moonshotai/kimi-latest/endpoints)
    ))
    (reasoning ({}
      (mandatory false)
      (default_enabled true)
      (supported_efforts (
        max
        high
        low
      ))
      (default_effort max)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id ~moonshotai/kimi-latest)
    (canonical_slug ~moonshotai/kimi-latest)
    (alias_target ({}
      (name "MoonshotAI: Kimi K3")
      (slug moonshotai/kimi-k3)
    ))
    (hugging_face_id null)
    (name "MoonshotAI Kimi Latest")
    (created 1777318428)
    (description "This model always redirects to the latest model in the MoonshotAI Kimi family.")
    (context_length 1048576)
    (architecture ({}
      (modality text+image->text)
      (input_modalities (
        text
        image
      ))
      (output_modalities (
        text
      ))
      (tokenizer Router)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.0000025")
      (completion "0.000014")
      (input_cache_read "0.00000029")
    ))
    (top_provider ({}
      (context_length 1048576)
      (max_completion_tokens 1048576)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      include_reasoning
      logit_bias
      logprobs
      max_tokens
      min_p
      presence_penalty
      reasoning
      reasoning_effort
      repetition_penalty
      response_format
      seed
      stop
      structured_outputs
      temperature
      tool_choice
      tools
      top_k
      top_logprobs
      top_p
    ))
    (default_parameters ({}
      (temperature null)
      (top_p 0.95)
      (top_k null)
      (frequency_penalty null)
      (presence_penalty null)
      (repetition_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/~moonshotai/kimi-latest/endpoints)
    ))
    (reasoning ({}
      (mandatory false)
      (default_enabled true)
      (supported_efforts (
        max
        high
        low
      ))
      (default_effort max)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId ~moonshotai/kimi-latest)
  ))
)
