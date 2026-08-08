(
  (kind model)
  (id openrouter-minimax_minimax-m2.5)
  (label "MiniMax: MiniMax M2.5")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model minimax/minimax-m2.5)
  (enabled true)
  (capabilities (
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
  (limits (
    (contextWindow 204800)
    (maxOutputTokens 196608)
  ))
  (pricing (
    (prompt "0.00000022")
    (completion "0.0000009")
    (input_cache_read "0.00000005")
  ))
  (properties (
    (id minimax/minimax-m2.5)
    (canonical_slug minimax/minimax-m2.5-20260211)
    (hugging_face_id MiniMaxAI/MiniMax-M2.5)
    (name "MiniMax: MiniMax M2.5")
    (created 1770908502)
    (description "MiniMax-M2.5 is a SOTA large language model designed for real-world productivity. Trained in a diverse range of complex real-world digital working environments, M2.5 builds upon the coding expertise of M2.1...")
    (context_length 204800)
    (architecture (
      (modality text->text)
      (input_modalities ([]
        text
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Other)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.00000022")
      (completion "0.0000009")
      (input_cache_read "0.00000005")
    ))
    (top_provider (
      (context_length 196608)
      (max_completion_tokens 196608)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      frequency_penalty
      include_reasoning
      logit_bias
      logprobs
      max_tokens
      min_p
      parallel_tool_calls
      presence_penalty
      reasoning
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
    (default_parameters (
      (temperature 1)
      (top_p 0.95)
      (top_k null)
      (frequency_penalty null)
      (presence_penalty null)
      (repetition_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links (
      (details /api/v1/models/minimax/minimax-m2.5-20260211/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena models)
          (category 3d)
          (elo 1224)
          (win_rate 57.6)
          (rank 40)
        )
        (
          (arena models)
          (category codecategories)
          (elo 1235)
          (win_rate 56.8)
          (rank 37)
        )
        (
          (arena models)
          (category dataviz)
          (elo 1199)
          (win_rate 51.2)
          (rank 48)
        )
        (
          (arena models)
          (category gamedev)
          (elo 1217)
          (win_rate 55.5)
          (rank 41)
        )
        (
          (arena models)
          (category svg)
          (elo 1197)
          (win_rate 54.5)
          (rank 30)
        )
        (
          (arena models)
          (category uicomponent)
          (elo 1206)
          (win_rate 53.4)
          (rank 46)
        )
        (
          (arena models)
          (category website)
          (elo 1244)
          (win_rate 57.5)
          (rank 37)
        )
      ))
    ))
    (reasoning (
      (mandatory true)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id minimax/minimax-m2.5)
    (canonical_slug minimax/minimax-m2.5-20260211)
    (hugging_face_id MiniMaxAI/MiniMax-M2.5)
    (name "MiniMax: MiniMax M2.5")
    (created 1770908502)
    (description "MiniMax-M2.5 is a SOTA large language model designed for real-world productivity. Trained in a diverse range of complex real-world digital working environments, M2.5 builds upon the coding expertise of M2.1...")
    (context_length 204800)
    (architecture (
      (modality text->text)
      (input_modalities ([]
        text
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Other)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.00000022")
      (completion "0.0000009")
      (input_cache_read "0.00000005")
    ))
    (top_provider (
      (context_length 196608)
      (max_completion_tokens 196608)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      frequency_penalty
      include_reasoning
      logit_bias
      logprobs
      max_tokens
      min_p
      parallel_tool_calls
      presence_penalty
      reasoning
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
    (default_parameters (
      (temperature 1)
      (top_p 0.95)
      (top_k null)
      (frequency_penalty null)
      (presence_penalty null)
      (repetition_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links (
      (details /api/v1/models/minimax/minimax-m2.5-20260211/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena models)
          (category 3d)
          (elo 1224)
          (win_rate 57.6)
          (rank 40)
        )
        (
          (arena models)
          (category codecategories)
          (elo 1235)
          (win_rate 56.8)
          (rank 37)
        )
        (
          (arena models)
          (category dataviz)
          (elo 1199)
          (win_rate 51.2)
          (rank 48)
        )
        (
          (arena models)
          (category gamedev)
          (elo 1217)
          (win_rate 55.5)
          (rank 41)
        )
        (
          (arena models)
          (category svg)
          (elo 1197)
          (win_rate 54.5)
          (rank 30)
        )
        (
          (arena models)
          (category uicomponent)
          (elo 1206)
          (win_rate 53.4)
          (rank 46)
        )
        (
          (arena models)
          (category website)
          (elo 1244)
          (win_rate 57.5)
          (rank 37)
        )
      ))
    ))
    (reasoning (
      (mandatory true)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId minimax/minimax-m2.5)
  ))
)
