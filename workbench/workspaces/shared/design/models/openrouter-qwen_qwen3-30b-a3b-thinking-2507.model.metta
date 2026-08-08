({}
  (kind model)
  (id openrouter-qwen_qwen3-30b-a3b-thinking-2507)
  (label "Qwen: Qwen3 30B A3B Thinking 2507")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model qwen/qwen3-30b-a3b-thinking-2507)
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
    (contextWindow 81920)
    (maxOutputTokens 32768)
  ))
  (pricing ({}
    (prompt "0.0000002")
    (completion "0.0000024")
  ))
  (properties ({}
    (id qwen/qwen3-30b-a3b-thinking-2507)
    (canonical_slug qwen/qwen3-30b-a3b-thinking-2507)
    (hugging_face_id Qwen/Qwen3-30B-A3B-Thinking-2507)
    (name "Qwen: Qwen3 30B A3B Thinking 2507")
    (created 1756399192)
    (description "Qwen3-30B-A3B-Thinking-2507 is a 30B parameter Mixture-of-Experts reasoning model optimized for complex tasks requiring extended multi-step thinking. The model is designed specifically for “thinking mode,” where internal reasoning traces are separated...")
    (context_length 81920)
    (architecture ({}
      (modality text->text)
      (input_modalities (
        text
      ))
      (output_modalities (
        text
      ))
      (tokenizer Qwen3)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.0000002")
      (completion "0.0000024")
    ))
    (top_provider ({}
      (context_length 81920)
      (max_completion_tokens 32768)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      include_reasoning
      max_tokens
      presence_penalty
      reasoning
      response_format
      seed
      stop
      temperature
      tool_choice
      tools
      top_k
      top_p
    ))
    (default_parameters ({}))
    (supported_voices null)
    (knowledge_cutoff 2025-06-30)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/qwen/qwen3-30b-a3b-thinking-2507/endpoints)
    ))
    (benchmarks ({}
      (design_arena (
        ({}
          (arena models)
          (category dataviz)
          (elo 953)
          (win_rate 33.3)
          (rank 104)
        )
        ({}
          (arena models)
          (category website)
          (elo 953)
          (win_rate 35.5)
          (rank 114)
        )
      ))
      (artificial_analysis ({}
        (intelligence_index 14.6)
        (coding_index 12.1)
        (agentic_index 1.8)
      ))
    ))
    (reasoning ({}
      (mandatory true)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id qwen/qwen3-30b-a3b-thinking-2507)
    (canonical_slug qwen/qwen3-30b-a3b-thinking-2507)
    (hugging_face_id Qwen/Qwen3-30B-A3B-Thinking-2507)
    (name "Qwen: Qwen3 30B A3B Thinking 2507")
    (created 1756399192)
    (description "Qwen3-30B-A3B-Thinking-2507 is a 30B parameter Mixture-of-Experts reasoning model optimized for complex tasks requiring extended multi-step thinking. The model is designed specifically for “thinking mode,” where internal reasoning traces are separated...")
    (context_length 81920)
    (architecture ({}
      (modality text->text)
      (input_modalities (
        text
      ))
      (output_modalities (
        text
      ))
      (tokenizer Qwen3)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.0000002")
      (completion "0.0000024")
    ))
    (top_provider ({}
      (context_length 81920)
      (max_completion_tokens 32768)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      include_reasoning
      max_tokens
      presence_penalty
      reasoning
      response_format
      seed
      stop
      temperature
      tool_choice
      tools
      top_k
      top_p
    ))
    (default_parameters ({}))
    (supported_voices null)
    (knowledge_cutoff 2025-06-30)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/qwen/qwen3-30b-a3b-thinking-2507/endpoints)
    ))
    (benchmarks ({}
      (design_arena (
        ({}
          (arena models)
          (category dataviz)
          (elo 953)
          (win_rate 33.3)
          (rank 104)
        )
        ({}
          (arena models)
          (category website)
          (elo 953)
          (win_rate 35.5)
          (rank 114)
        )
      ))
      (artificial_analysis ({}
        (intelligence_index 14.6)
        (coding_index 12.1)
        (agentic_index 1.8)
      ))
    ))
    (reasoning ({}
      (mandatory true)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId qwen/qwen3-30b-a3b-thinking-2507)
  ))
)
