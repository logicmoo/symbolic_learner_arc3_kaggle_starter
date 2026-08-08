(
  (kind model)
  (id openrouter-qwen_qwen3-coder)
  (label "Qwen: Qwen3 Coder 480B A35B")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model qwen/qwen3-coder)
  (enabled true)
  (capabilities (
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
  (limits (
    (contextWindow 262144)
    (maxOutputTokens 65536)
  ))
  (pricing (
    (prompt "0.0000003")
    (completion "0.000001")
    (input_cache_read "0.0000001")
  ))
  (properties (
    (id qwen/qwen3-coder)
    (canonical_slug qwen/qwen3-coder-480b-a35b-07-25)
    (hugging_face_id Qwen/Qwen3-Coder-480B-A35B-Instruct)
    (name "Qwen: Qwen3 Coder 480B A35B")
    (created 1753230546)
    (description "Qwen3-Coder-480B-A35B-Instruct is a Mixture-of-Experts (MoE) code generation model developed by the Qwen team. It is optimized for agentic coding tasks such as function calling, tool use, and long-context reasoning over...")
    (context_length 262144)
    (architecture (
      (modality text->text)
      (input_modalities ([]
        text
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Qwen3)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.0000003")
      (completion "0.000001")
      (input_cache_read "0.0000001")
    ))
    (top_provider (
      (context_length 262144)
      (max_completion_tokens 65536)
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
    (default_parameters ())
    (supported_voices null)
    (knowledge_cutoff 2025-06-30)
    (expiration_date null)
    (links (
      (details /api/v1/models/qwen/qwen3-coder-480b-a35b-07-25/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena models)
          (category codecategories)
          (elo 1171)
          (win_rate 61.2)
          (rank 64)
        )
        (
          (arena models)
          (category dataviz)
          (elo 1109)
          (win_rate 54.9)
          (rank 85)
        )
        (
          (arena models)
          (category gamedev)
          (elo 1140)
          (win_rate 58.7)
          (rank 69)
        )
        (
          (arena models)
          (category uicomponent)
          (elo 1146)
          (win_rate 61.4)
          (rank 66)
        )
        (
          (arena models)
          (category website)
          (elo 1181)
          (win_rate 61.7)
          (rank 66)
        )
      ))
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id qwen/qwen3-coder)
    (canonical_slug qwen/qwen3-coder-480b-a35b-07-25)
    (hugging_face_id Qwen/Qwen3-Coder-480B-A35B-Instruct)
    (name "Qwen: Qwen3 Coder 480B A35B")
    (created 1753230546)
    (description "Qwen3-Coder-480B-A35B-Instruct is a Mixture-of-Experts (MoE) code generation model developed by the Qwen team. It is optimized for agentic coding tasks such as function calling, tool use, and long-context reasoning over...")
    (context_length 262144)
    (architecture (
      (modality text->text)
      (input_modalities ([]
        text
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Qwen3)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.0000003")
      (completion "0.000001")
      (input_cache_read "0.0000001")
    ))
    (top_provider (
      (context_length 262144)
      (max_completion_tokens 65536)
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
    (default_parameters ())
    (supported_voices null)
    (knowledge_cutoff 2025-06-30)
    (expiration_date null)
    (links (
      (details /api/v1/models/qwen/qwen3-coder-480b-a35b-07-25/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena models)
          (category codecategories)
          (elo 1171)
          (win_rate 61.2)
          (rank 64)
        )
        (
          (arena models)
          (category dataviz)
          (elo 1109)
          (win_rate 54.9)
          (rank 85)
        )
        (
          (arena models)
          (category gamedev)
          (elo 1140)
          (win_rate 58.7)
          (rank 69)
        )
        (
          (arena models)
          (category uicomponent)
          (elo 1146)
          (win_rate 61.4)
          (rank 66)
        )
        (
          (arena models)
          (category website)
          (elo 1181)
          (win_rate 61.7)
          (rank 66)
        )
      ))
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId qwen/qwen3-coder)
  ))
)
