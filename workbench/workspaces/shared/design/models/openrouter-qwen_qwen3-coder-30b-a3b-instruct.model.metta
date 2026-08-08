(
  (kind model)
  (id openrouter-qwen_qwen3-coder-30b-a3b-instruct)
  (label "Qwen: Qwen3 Coder 30B A3B Instruct")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model qwen/qwen3-coder-30b-a3b-instruct)
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
    (maxOutputTokens 32768)
  ))
  (pricing (
    (prompt "0.00000007")
    (completion "0.00000027")
  ))
  (properties (
    (id qwen/qwen3-coder-30b-a3b-instruct)
    (canonical_slug qwen/qwen3-coder-30b-a3b-instruct)
    (hugging_face_id Qwen/Qwen3-Coder-30B-A3B-Instruct)
    (name "Qwen: Qwen3 Coder 30B A3B Instruct")
    (created 1753972379)
    (description "Qwen3-Coder-30B-A3B-Instruct is a 30.5B parameter Mixture-of-Experts (MoE) model with 128 experts (8 active per forward pass), designed for advanced code generation, repository-scale understanding, and agentic tool use. Built on the...")
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
      (prompt "0.00000007")
      (completion "0.00000027")
    ))
    (top_provider (
      (context_length 160000)
      (max_completion_tokens 32768)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      frequency_penalty
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
    (default_parameters ())
    (supported_voices null)
    (knowledge_cutoff 2025-06-30)
    (expiration_date null)
    (links (
      (details /api/v1/models/qwen/qwen3-coder-30b-a3b-instruct/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena models)
          (category dataviz)
          (elo 1112)
          (win_rate 54.7)
          (rank 84)
        )
        (
          (arena models)
          (category uicomponent)
          (elo 1079)
          (win_rate 54.1)
          (rank 83)
        )
        (
          (arena models)
          (category website)
          (elo 1110)
          (win_rate 57.1)
          (rank 88)
        )
      ))
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id qwen/qwen3-coder-30b-a3b-instruct)
    (canonical_slug qwen/qwen3-coder-30b-a3b-instruct)
    (hugging_face_id Qwen/Qwen3-Coder-30B-A3B-Instruct)
    (name "Qwen: Qwen3 Coder 30B A3B Instruct")
    (created 1753972379)
    (description "Qwen3-Coder-30B-A3B-Instruct is a 30.5B parameter Mixture-of-Experts (MoE) model with 128 experts (8 active per forward pass), designed for advanced code generation, repository-scale understanding, and agentic tool use. Built on the...")
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
      (prompt "0.00000007")
      (completion "0.00000027")
    ))
    (top_provider (
      (context_length 160000)
      (max_completion_tokens 32768)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      frequency_penalty
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
    (default_parameters ())
    (supported_voices null)
    (knowledge_cutoff 2025-06-30)
    (expiration_date null)
    (links (
      (details /api/v1/models/qwen/qwen3-coder-30b-a3b-instruct/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena models)
          (category dataviz)
          (elo 1112)
          (win_rate 54.7)
          (rank 84)
        )
        (
          (arena models)
          (category uicomponent)
          (elo 1079)
          (win_rate 54.1)
          (rank 83)
        )
        (
          (arena models)
          (category website)
          (elo 1110)
          (win_rate 57.1)
          (rank 88)
        )
      ))
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId qwen/qwen3-coder-30b-a3b-instruct)
  ))
)
