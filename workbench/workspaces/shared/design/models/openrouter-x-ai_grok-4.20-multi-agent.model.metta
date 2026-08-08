({}
  (kind model)
  (id openrouter-x-ai_grok-4.20-multi-agent)
  (label "SpaceXAI: Grok 4.20 Multi-Agent")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model x-ai/grok-4.20-multi-agent)
  (enabled true)
  (capabilities ({}
    (audio false)
    (code false)
    (functionCalling false)
    (json true)
    (jsonMode true)
    (local false)
    (multimodal true)
    (reasoning true)
    (text true)
    (tools false)
    (vision true)
  ))
  (limits ({}
    (contextWindow 2000000)
    (maxOutputTokens null)
  ))
  (pricing ({}
    (prompt "0.00000125")
    (completion "0.0000025")
    (web_search "0.005")
    (input_cache_read "0.0000002")
    (overrides (
      ({}
        (min_prompt_tokens 200000)
        (prompt "0.0000025")
        (completion "0.000005")
        (input_cache_read "0.0000004")
      )
    ))
  ))
  (properties ({}
    (id x-ai/grok-4.20-multi-agent)
    (canonical_slug x-ai/grok-4.20-multi-agent-20260309)
    (hugging_face_id "")
    (name "SpaceXAI: Grok 4.20 Multi-Agent")
    (created 1774979158)
    (description "Grok 4.20 Multi-Agent is a variant of SpaceXAI’s Grok 4.20 designed for collaborative, agent-based workflows. Multiple agents operate in parallel to conduct deep research, coordinate tool use, and synthesize information...")
    (context_length 2000000)
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
      (tokenizer Grok)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.00000125")
      (completion "0.0000025")
      (web_search "0.005")
      (input_cache_read "0.0000002")
      (overrides (
        ({}
          (min_prompt_tokens 200000)
          (prompt "0.0000025")
          (completion "0.000005")
          (input_cache_read "0.0000004")
        )
      ))
    ))
    (top_provider ({}
      (context_length 2000000)
      (max_completion_tokens null)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      include_reasoning
      logprobs
      max_tokens
      reasoning
      reasoning_effort
      response_format
      seed
      structured_outputs
      temperature
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
    (knowledge_cutoff 2025-09-01)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/x-ai/grok-4.20-multi-agent-20260309/endpoints)
    ))
    (reasoning ({}
      (mandatory true)
      (default_enabled true)
      (supported_efforts (
        xhigh
        high
        medium
        low
      ))
      (default_effort medium)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id x-ai/grok-4.20-multi-agent)
    (canonical_slug x-ai/grok-4.20-multi-agent-20260309)
    (hugging_face_id "")
    (name "SpaceXAI: Grok 4.20 Multi-Agent")
    (created 1774979158)
    (description "Grok 4.20 Multi-Agent is a variant of SpaceXAI’s Grok 4.20 designed for collaborative, agent-based workflows. Multiple agents operate in parallel to conduct deep research, coordinate tool use, and synthesize information...")
    (context_length 2000000)
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
      (tokenizer Grok)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.00000125")
      (completion "0.0000025")
      (web_search "0.005")
      (input_cache_read "0.0000002")
      (overrides (
        ({}
          (min_prompt_tokens 200000)
          (prompt "0.0000025")
          (completion "0.000005")
          (input_cache_read "0.0000004")
        )
      ))
    ))
    (top_provider ({}
      (context_length 2000000)
      (max_completion_tokens null)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      include_reasoning
      logprobs
      max_tokens
      reasoning
      reasoning_effort
      response_format
      seed
      structured_outputs
      temperature
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
    (knowledge_cutoff 2025-09-01)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/x-ai/grok-4.20-multi-agent-20260309/endpoints)
    ))
    (reasoning ({}
      (mandatory true)
      (default_enabled true)
      (supported_efforts (
        xhigh
        high
        medium
        low
      ))
      (default_effort medium)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId x-ai/grok-4.20-multi-agent)
  ))
)
