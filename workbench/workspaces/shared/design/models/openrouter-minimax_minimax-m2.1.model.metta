({}
  (kind model)
  (id openrouter-minimax_minimax-m2.1)
  (label "MiniMax: MiniMax M2.1")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model minimax/minimax-m2.1)
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
    (contextWindow 204800)
    (maxOutputTokens 131072)
  ))
  (pricing ({}
    (prompt "0.0000003")
    (completion "0.0000012")
    (input_cache_read "0.00000003")
  ))
  (properties ({}
    (id minimax/minimax-m2.1)
    (canonical_slug minimax/minimax-m2.1)
    (hugging_face_id MiniMaxAI/MiniMax-M2.1)
    (name "MiniMax: MiniMax M2.1")
    (created 1766454997)
    (description "MiniMax-M2.1 is a lightweight, state-of-the-art large language model optimized for coding, agentic workflows, and modern application development. With only 10 billion activated parameters, it delivers a major jump in real-world...")
    (context_length 204800)
    (architecture ({}
      (modality text->text)
      (input_modalities (
        text
      ))
      (output_modalities (
        text
      ))
      (tokenizer Other)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.0000003")
      (completion "0.0000012")
      (input_cache_read "0.00000003")
    ))
    (top_provider ({}
      (context_length 204800)
      (max_completion_tokens 131072)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      include_reasoning
      max_tokens
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
      top_p
    ))
    (default_parameters ({}
      (temperature 1)
      (top_p 0.9)
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/minimax/minimax-m2.1/endpoints)
    ))
    (benchmarks ({}
      (design_arena (
        ({}
          (arena models)
          (category 3d)
          (elo 1219)
          (win_rate 57.5)
          (rank 42)
        )
        ({}
          (arena models)
          (category codecategories)
          (elo 1218)
          (win_rate 55.3)
          (rank 41)
        )
        ({}
          (arena models)
          (category dataviz)
          (elo 1234)
          (win_rate 57)
          (rank 36)
        )
        ({}
          (arena models)
          (category gamedev)
          (elo 1175)
          (win_rate 50.4)
          (rank 60)
        )
        ({}
          (arena models)
          (category svg)
          (elo 1179)
          (win_rate 55.4)
          (rank 39)
        )
        ({}
          (arena models)
          (category uicomponent)
          (elo 1256)
          (win_rate 60.9)
          (rank 31)
        )
        ({}
          (arena models)
          (category website)
          (elo 1224)
          (win_rate 55.4)
          (rank 42)
        )
      ))
    ))
    (reasoning ({}
      (mandatory true)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id minimax/minimax-m2.1)
    (canonical_slug minimax/minimax-m2.1)
    (hugging_face_id MiniMaxAI/MiniMax-M2.1)
    (name "MiniMax: MiniMax M2.1")
    (created 1766454997)
    (description "MiniMax-M2.1 is a lightweight, state-of-the-art large language model optimized for coding, agentic workflows, and modern application development. With only 10 billion activated parameters, it delivers a major jump in real-world...")
    (context_length 204800)
    (architecture ({}
      (modality text->text)
      (input_modalities (
        text
      ))
      (output_modalities (
        text
      ))
      (tokenizer Other)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.0000003")
      (completion "0.0000012")
      (input_cache_read "0.00000003")
    ))
    (top_provider ({}
      (context_length 204800)
      (max_completion_tokens 131072)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      include_reasoning
      max_tokens
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
      top_p
    ))
    (default_parameters ({}
      (temperature 1)
      (top_p 0.9)
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/minimax/minimax-m2.1/endpoints)
    ))
    (benchmarks ({}
      (design_arena (
        ({}
          (arena models)
          (category 3d)
          (elo 1219)
          (win_rate 57.5)
          (rank 42)
        )
        ({}
          (arena models)
          (category codecategories)
          (elo 1218)
          (win_rate 55.3)
          (rank 41)
        )
        ({}
          (arena models)
          (category dataviz)
          (elo 1234)
          (win_rate 57)
          (rank 36)
        )
        ({}
          (arena models)
          (category gamedev)
          (elo 1175)
          (win_rate 50.4)
          (rank 60)
        )
        ({}
          (arena models)
          (category svg)
          (elo 1179)
          (win_rate 55.4)
          (rank 39)
        )
        ({}
          (arena models)
          (category uicomponent)
          (elo 1256)
          (win_rate 60.9)
          (rank 31)
        )
        ({}
          (arena models)
          (category website)
          (elo 1224)
          (win_rate 55.4)
          (rank 42)
        )
      ))
    ))
    (reasoning ({}
      (mandatory true)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId minimax/minimax-m2.1)
  ))
)
