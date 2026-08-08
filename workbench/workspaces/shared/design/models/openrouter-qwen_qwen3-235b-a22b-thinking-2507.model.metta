({}
  (kind model)
  (id openrouter-qwen_qwen3-235b-a22b-thinking-2507)
  (label "Qwen: Qwen3 235B A22B Thinking 2507")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model qwen/qwen3-235b-a22b-thinking-2507)
  (enabled true)
  (capabilities ({}
    (audio false)
    (code false)
    (functionCalling true)
    (json true)
    (jsonMode true)
    (local false)
    (multimodal false)
    (reasoning true)
    (text true)
    (tools true)
    (vision false)
  ))
  (limits ({}
    (contextWindow 262144)
    (maxOutputTokens null)
  ))
  (pricing ({}
    (prompt "0.00000023")
    (completion "0.0000023")
  ))
  (properties ({}
    (id qwen/qwen3-235b-a22b-thinking-2507)
    (canonical_slug qwen/qwen3-235b-a22b-thinking-2507)
    (hugging_face_id Qwen/Qwen3-235B-A22B-Thinking-2507)
    (name "Qwen: Qwen3 235B A22B Thinking 2507")
    (created 1753449557)
    (description "Qwen3-235B-A22B-Thinking-2507 is a high-performance, open-weight Mixture-of-Experts (MoE) language model optimized for complex reasoning tasks. It activates 22B of its 235B parameters per forward pass and natively supports up to 262,144...")
    (context_length 262144)
    (architecture ({}
      (modality text->text)
      (input_modalities (
        text
      ))
      (output_modalities (
        text
      ))
      (tokenizer Qwen3)
      (instruct_type qwen3)
    ))
    (pricing ({}
      (prompt "0.00000023")
      (completion "0.0000023")
    ))
    (top_provider ({}
      (context_length 131072)
      (max_completion_tokens null)
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
      repetition_penalty
      response_format
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
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff 2025-06-30)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/qwen/qwen3-235b-a22b-thinking-2507/endpoints)
    ))
    (benchmarks ({}
      (design_arena (
        ({}
          (arena models)
          (category 3d)
          (elo 1053)
          (win_rate 40.7)
          (rank 91)
        )
        ({}
          (arena models)
          (category codecategories)
          (elo 1061)
          (win_rate 40.8)
          (rank 95)
        )
        ({}
          (arena models)
          (category dataviz)
          (elo 974)
          (win_rate 32.3)
          (rank 101)
        )
        ({}
          (arena models)
          (category gamedev)
          (elo 998)
          (win_rate 34.4)
          (rank 104)
        )
        ({}
          (arena models)
          (category uicomponent)
          (elo 975)
          (win_rate 33.9)
          (rank 100)
        )
        ({}
          (arena models)
          (category website)
          (elo 1075)
          (win_rate 42)
          (rank 95)
        )
      ))
      (artificial_analysis ({}
        (intelligence_index 19.9)
        (coding_index 22.1)
        (agentic_index 3.8)
      ))
    ))
    (reasoning ({}
      (mandatory true)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id qwen/qwen3-235b-a22b-thinking-2507)
    (canonical_slug qwen/qwen3-235b-a22b-thinking-2507)
    (hugging_face_id Qwen/Qwen3-235B-A22B-Thinking-2507)
    (name "Qwen: Qwen3 235B A22B Thinking 2507")
    (created 1753449557)
    (description "Qwen3-235B-A22B-Thinking-2507 is a high-performance, open-weight Mixture-of-Experts (MoE) language model optimized for complex reasoning tasks. It activates 22B of its 235B parameters per forward pass and natively supports up to 262,144...")
    (context_length 262144)
    (architecture ({}
      (modality text->text)
      (input_modalities (
        text
      ))
      (output_modalities (
        text
      ))
      (tokenizer Qwen3)
      (instruct_type qwen3)
    ))
    (pricing ({}
      (prompt "0.00000023")
      (completion "0.0000023")
    ))
    (top_provider ({}
      (context_length 131072)
      (max_completion_tokens null)
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
      repetition_penalty
      response_format
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
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff 2025-06-30)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/qwen/qwen3-235b-a22b-thinking-2507/endpoints)
    ))
    (benchmarks ({}
      (design_arena (
        ({}
          (arena models)
          (category 3d)
          (elo 1053)
          (win_rate 40.7)
          (rank 91)
        )
        ({}
          (arena models)
          (category codecategories)
          (elo 1061)
          (win_rate 40.8)
          (rank 95)
        )
        ({}
          (arena models)
          (category dataviz)
          (elo 974)
          (win_rate 32.3)
          (rank 101)
        )
        ({}
          (arena models)
          (category gamedev)
          (elo 998)
          (win_rate 34.4)
          (rank 104)
        )
        ({}
          (arena models)
          (category uicomponent)
          (elo 975)
          (win_rate 33.9)
          (rank 100)
        )
        ({}
          (arena models)
          (category website)
          (elo 1075)
          (win_rate 42)
          (rank 95)
        )
      ))
      (artificial_analysis ({}
        (intelligence_index 19.9)
        (coding_index 22.1)
        (agentic_index 3.8)
      ))
    ))
    (reasoning ({}
      (mandatory true)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId qwen/qwen3-235b-a22b-thinking-2507)
  ))
)
