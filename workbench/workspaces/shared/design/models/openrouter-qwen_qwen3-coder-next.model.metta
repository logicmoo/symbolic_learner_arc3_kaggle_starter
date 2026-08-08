({}
  (kind model)
  (id openrouter-qwen_qwen3-coder-next)
  (label "Qwen: Qwen3 Coder Next")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model qwen/qwen3-coder-next)
  (enabled true)
  (capabilities ({}
    (audio false)
    (code true)
    (functionCalling true)
    (json true)
    (jsonMode true)
    (local false)
    (multimodal false)
    (reasoning false)
    (text true)
    (tools true)
    (vision false)
  ))
  (limits ({}
    (contextWindow 262144)
    (maxOutputTokens 262144)
  ))
  (pricing ({}
    (prompt "0.00000012")
    (completion "0.0000008")
    (input_cache_read "0.00000007")
  ))
  (properties ({}
    (id qwen/qwen3-coder-next)
    (canonical_slug qwen/qwen3-coder-next-2025-02-03)
    (hugging_face_id Qwen/Qwen3-Coder-Next)
    (name "Qwen: Qwen3 Coder Next")
    (created 1770164101)
    (description "Qwen3-Coder-Next is an open-weight causal language model optimized for coding agents and local development workflows. It uses a sparse MoE design with 80B total parameters and only 3B activated per...")
    (context_length 262144)
    (architecture ({}
      (modality text->text)
      (input_modalities (
        text
      ))
      (output_modalities (
        text
      ))
      (tokenizer Qwen)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.00000012")
      (completion "0.0000008")
      (input_cache_read "0.00000007")
    ))
    (top_provider ({}
      (context_length 262144)
      (max_completion_tokens 262144)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      logit_bias
      logprobs
      max_tokens
      presence_penalty
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
      (temperature 1)
      (top_p 0.95)
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/qwen/qwen3-coder-next-2025-02-03/endpoints)
    ))
    (benchmarks ({}
      (design_arena ())
      (artificial_analysis ({}
        (intelligence_index 21.3)
        (coding_index 36.2)
        (agentic_index 8.9)
      ))
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id qwen/qwen3-coder-next)
    (canonical_slug qwen/qwen3-coder-next-2025-02-03)
    (hugging_face_id Qwen/Qwen3-Coder-Next)
    (name "Qwen: Qwen3 Coder Next")
    (created 1770164101)
    (description "Qwen3-Coder-Next is an open-weight causal language model optimized for coding agents and local development workflows. It uses a sparse MoE design with 80B total parameters and only 3B activated per...")
    (context_length 262144)
    (architecture ({}
      (modality text->text)
      (input_modalities (
        text
      ))
      (output_modalities (
        text
      ))
      (tokenizer Qwen)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.00000012")
      (completion "0.0000008")
      (input_cache_read "0.00000007")
    ))
    (top_provider ({}
      (context_length 262144)
      (max_completion_tokens 262144)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      logit_bias
      logprobs
      max_tokens
      presence_penalty
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
      (temperature 1)
      (top_p 0.95)
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/qwen/qwen3-coder-next-2025-02-03/endpoints)
    ))
    (benchmarks ({}
      (design_arena ())
      (artificial_analysis ({}
        (intelligence_index 21.3)
        (coding_index 36.2)
        (agentic_index 8.9)
      ))
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId qwen/qwen3-coder-next)
  ))
)
