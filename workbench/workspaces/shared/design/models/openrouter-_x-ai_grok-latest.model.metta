({}
  (kind model)
  (id openrouter-_x-ai_grok-latest)
  (label "xAI: Grok Latest")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model ~x-ai/grok-latest)
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
    (contextWindow 500000)
    (maxOutputTokens null)
  ))
  (pricing ({}
    (prompt "0.000002")
    (completion "0.000006")
    (web_search "0.005")
    (input_cache_read "0.0000003")
    (overrides (
      ({}
        (min_prompt_tokens 200000)
        (prompt "0.000004")
        (completion "0.000012")
        (input_cache_read "0.0000006")
      )
    ))
  ))
  (properties ({}
    (id ~x-ai/grok-latest)
    (canonical_slug ~x-ai/grok-latest)
    (alias_target ({}
      (name "SpaceXAI: Grok 4.5")
      (slug x-ai/grok-4.5)
    ))
    (hugging_face_id null)
    (name "xAI: Grok Latest")
    (created 1783519360)
    (description "This model always redirects to the latest Grok model from xAI.")
    (context_length 500000)
    (architecture ({}
      (modality text+image+file->text)
      (input_modalities (
        text
        image
        file
      ))
      (output_modalities (
        text
      ))
      (tokenizer Router)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.000002")
      (completion "0.000006")
      (web_search "0.005")
      (input_cache_read "0.0000003")
      (overrides (
        ({}
          (min_prompt_tokens 200000)
          (prompt "0.000004")
          (completion "0.000012")
          (input_cache_read "0.0000006")
        )
      ))
    ))
    (top_provider ({}
      (context_length 500000)
      (max_completion_tokens null)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      include_reasoning
      logprobs
      max_tokens
      presence_penalty
      reasoning
      reasoning_effort
      response_format
      seed
      stop
      structured_outputs
      temperature
      tool_choice
      tools
      top_logprobs
      top_p
    ))
    (default_parameters ({}
      (temperature null)
      (top_p null)
      (top_k null)
      (frequency_penalty null)
      (presence_penalty null)
      (repetition_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/~x-ai/grok-latest/endpoints)
    ))
    (reasoning ({}
      (mandatory true)
      (default_enabled true)
      (supported_efforts (
        high
        medium
        low
      ))
      (default_effort high)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id ~x-ai/grok-latest)
    (canonical_slug ~x-ai/grok-latest)
    (alias_target ({}
      (name "SpaceXAI: Grok 4.5")
      (slug x-ai/grok-4.5)
    ))
    (hugging_face_id null)
    (name "xAI: Grok Latest")
    (created 1783519360)
    (description "This model always redirects to the latest Grok model from xAI.")
    (context_length 500000)
    (architecture ({}
      (modality text+image+file->text)
      (input_modalities (
        text
        image
        file
      ))
      (output_modalities (
        text
      ))
      (tokenizer Router)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.000002")
      (completion "0.000006")
      (web_search "0.005")
      (input_cache_read "0.0000003")
      (overrides (
        ({}
          (min_prompt_tokens 200000)
          (prompt "0.000004")
          (completion "0.000012")
          (input_cache_read "0.0000006")
        )
      ))
    ))
    (top_provider ({}
      (context_length 500000)
      (max_completion_tokens null)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      include_reasoning
      logprobs
      max_tokens
      presence_penalty
      reasoning
      reasoning_effort
      response_format
      seed
      stop
      structured_outputs
      temperature
      tool_choice
      tools
      top_logprobs
      top_p
    ))
    (default_parameters ({}
      (temperature null)
      (top_p null)
      (top_k null)
      (frequency_penalty null)
      (presence_penalty null)
      (repetition_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/~x-ai/grok-latest/endpoints)
    ))
    (reasoning ({}
      (mandatory true)
      (default_enabled true)
      (supported_efforts (
        high
        medium
        low
      ))
      (default_effort high)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId ~x-ai/grok-latest)
  ))
)
