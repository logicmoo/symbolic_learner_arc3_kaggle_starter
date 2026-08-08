({}
  (kind model)
  (id openrouter-thinkingmachines_inkling-small)
  (label "Thinking Machines: Inkling Small")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model thinkingmachines/inkling-small)
  (enabled true)
  (capabilities ({}
    (audio true)
    (code false)
    (functionCalling true)
    (json false)
    (jsonMode false)
    (local false)
    (multimodal true)
    (reasoning true)
    (text true)
    (tools true)
    (vision true)
  ))
  (limits ({}
    (contextWindow 524288)
    (maxOutputTokens 262144)
  ))
  (pricing ({}
    (prompt "0.00000045")
    (completion "0.0000012")
    (input_cache_read "0.0000001")
  ))
  (properties ({}
    (id thinkingmachines/inkling-small)
    (canonical_slug thinkingmachines/inkling-small-20260730)
    (hugging_face_id thinkingmachines/Inkling-Small)
    (name "Thinking Machines: Inkling Small")
    (created 1785443117)
    (description "Inkling Small is an open-weight multimodal mixture-of-experts model from Thinking Machines Lab, with 12B active parameters out of 276B total. It is positioned as the smaller, more efficient member of...")
    (context_length 524288)
    (architecture ({}
      (modality text+image+audio->text)
      (input_modalities (
        text
        image
        audio
      ))
      (output_modalities (
        text
      ))
      (tokenizer Other)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.00000045")
      (completion "0.0000012")
      (input_cache_read "0.0000001")
    ))
    (top_provider ({}
      (context_length 524288)
      (max_completion_tokens 262144)
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
      seed
      stop
      temperature
      tool_choice
      tools
      top_k
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
      (details /api/v1/models/thinkingmachines/inkling-small-20260730/endpoints)
    ))
    (benchmarks ({}
      (design_arena ())
      (artificial_analysis ({}
        (intelligence_index 41.2)
        (coding_index 52.9)
        (agentic_index 31.9)
      ))
    ))
    (reasoning ({}
      (mandatory false)
      (default_enabled true)
      (supported_efforts (
        max
        high
        medium
        low
        minimal
        none
      ))
      (default_effort high)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id thinkingmachines/inkling-small)
    (canonical_slug thinkingmachines/inkling-small-20260730)
    (hugging_face_id thinkingmachines/Inkling-Small)
    (name "Thinking Machines: Inkling Small")
    (created 1785443117)
    (description "Inkling Small is an open-weight multimodal mixture-of-experts model from Thinking Machines Lab, with 12B active parameters out of 276B total. It is positioned as the smaller, more efficient member of...")
    (context_length 524288)
    (architecture ({}
      (modality text+image+audio->text)
      (input_modalities (
        text
        image
        audio
      ))
      (output_modalities (
        text
      ))
      (tokenizer Other)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.00000045")
      (completion "0.0000012")
      (input_cache_read "0.0000001")
    ))
    (top_provider ({}
      (context_length 524288)
      (max_completion_tokens 262144)
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
      seed
      stop
      temperature
      tool_choice
      tools
      top_k
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
      (details /api/v1/models/thinkingmachines/inkling-small-20260730/endpoints)
    ))
    (benchmarks ({}
      (design_arena ())
      (artificial_analysis ({}
        (intelligence_index 41.2)
        (coding_index 52.9)
        (agentic_index 31.9)
      ))
    ))
    (reasoning ({}
      (mandatory false)
      (default_enabled true)
      (supported_efforts (
        max
        high
        medium
        low
        minimal
        none
      ))
      (default_effort high)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId thinkingmachines/inkling-small)
  ))
)
