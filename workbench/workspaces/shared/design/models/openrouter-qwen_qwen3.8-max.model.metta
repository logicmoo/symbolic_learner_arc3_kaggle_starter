({}
  (kind model)
  (id openrouter-qwen_qwen3.8-max)
  (label "Qwen: Qwen3.8 Max")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model qwen/qwen3.8-max)
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
    (contextWindow 1000000)
    (maxOutputTokens 131072)
  ))
  (pricing ({}
    (prompt "0.000002")
    (completion "0.000006")
    (input_cache_read "0.00000025")
    (input_cache_write "0.0000025")
  ))
  (properties ({}
    (id qwen/qwen3.8-max)
    (canonical_slug qwen/qwen3.8-max-20260803)
    (hugging_face_id null)
    (name "Qwen: Qwen3.8 Max")
    (created 1785731612)
    (description "Qwen3.8 Max is the flagship model in Alibaba's Qwen3.8 series, the general-availability successor to the Qwen3.8 Max Preview. It is a multimodal reasoning model intended for complex reasoning, visual understanding,...")
    (context_length 1000000)
    (architecture ({}
      (modality text+image+video->text)
      (input_modalities (
        text
        image
        video
      ))
      (output_modalities (
        text
      ))
      (tokenizer Qwen)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.000002")
      (completion "0.000006")
      (input_cache_read "0.00000025")
      (input_cache_write "0.0000025")
    ))
    (top_provider ({}
      (context_length 1000000)
      (max_completion_tokens 131072)
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
      top_k
      top_logprobs
      top_p
    ))
    (default_parameters ({}))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/qwen/qwen3.8-max-20260803/endpoints)
    ))
    (benchmarks ({}
      (design_arena ())
      (artificial_analysis ({}
        (intelligence_index 58.1)
        (coding_index 71.8)
        (agentic_index 58.4)
      ))
    ))
    (reasoning ({}
      (mandatory true)
      (default_enabled true)
      (supported_efforts (
        xhigh
        high
        medium
        low
        minimal
      ))
      (default_effort xhigh)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id qwen/qwen3.8-max)
    (canonical_slug qwen/qwen3.8-max-20260803)
    (hugging_face_id null)
    (name "Qwen: Qwen3.8 Max")
    (created 1785731612)
    (description "Qwen3.8 Max is the flagship model in Alibaba's Qwen3.8 series, the general-availability successor to the Qwen3.8 Max Preview. It is a multimodal reasoning model intended for complex reasoning, visual understanding,...")
    (context_length 1000000)
    (architecture ({}
      (modality text+image+video->text)
      (input_modalities (
        text
        image
        video
      ))
      (output_modalities (
        text
      ))
      (tokenizer Qwen)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.000002")
      (completion "0.000006")
      (input_cache_read "0.00000025")
      (input_cache_write "0.0000025")
    ))
    (top_provider ({}
      (context_length 1000000)
      (max_completion_tokens 131072)
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
      top_k
      top_logprobs
      top_p
    ))
    (default_parameters ({}))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/qwen/qwen3.8-max-20260803/endpoints)
    ))
    (benchmarks ({}
      (design_arena ())
      (artificial_analysis ({}
        (intelligence_index 58.1)
        (coding_index 71.8)
        (agentic_index 58.4)
      ))
    ))
    (reasoning ({}
      (mandatory true)
      (default_enabled true)
      (supported_efforts (
        xhigh
        high
        medium
        low
        minimal
      ))
      (default_effort xhigh)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId qwen/qwen3.8-max)
  ))
)
