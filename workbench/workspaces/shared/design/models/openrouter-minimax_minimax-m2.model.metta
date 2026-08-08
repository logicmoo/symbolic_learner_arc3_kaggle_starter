(
  (kind model)
  (id openrouter-minimax_minimax-m2)
  (label "MiniMax: MiniMax M2")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model minimax/minimax-m2)
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
    (maxOutputTokens 131072)
  ))
  (pricing (
    (prompt "0.000000255")
    (completion "0.00000102")
  ))
  (properties (
    (id minimax/minimax-m2)
    (canonical_slug minimax/minimax-m2)
    (hugging_face_id MiniMaxAI/MiniMax-M2)
    (name "MiniMax: MiniMax M2")
    (created 1761252093)
    (description "MiniMax-M2 is a compact, high-efficiency large language model optimized for end-to-end coding and agentic workflows. With 10 billion activated parameters (230 billion total), it delivers near-frontier intelligence across general reasoning,...")
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
      (prompt "0.000000255")
      (completion "0.00000102")
    ))
    (top_provider (
      (context_length 204800)
      (max_completion_tokens 131072)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      frequency_penalty
      include_reasoning
      logprobs
      max_tokens
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
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links (
      (details /api/v1/models/minimax/minimax-m2/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena models)
          (category 3d)
          (elo 1151)
          (win_rate 48.3)
          (rank 65)
        )
        (
          (arena models)
          (category codecategories)
          (elo 1163)
          (win_rate 48.1)
          (rank 69)
        )
        (
          (arena models)
          (category dataviz)
          (elo 1168)
          (win_rate 50)
          (rank 64)
        )
        (
          (arena models)
          (category gamedev)
          (elo 1158)
          (win_rate 48.1)
          (rank 65)
        )
        (
          (arena models)
          (category svg)
          (elo 1147)
          (win_rate 55.3)
          (rank 45)
        )
        (
          (arena models)
          (category uicomponent)
          (elo 1169)
          (win_rate 49.2)
          (rank 63)
        )
        (
          (arena models)
          (category website)
          (elo 1165)
          (win_rate 48)
          (rank 70)
        )
      ))
    ))
    (reasoning (
      (mandatory true)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id minimax/minimax-m2)
    (canonical_slug minimax/minimax-m2)
    (hugging_face_id MiniMaxAI/MiniMax-M2)
    (name "MiniMax: MiniMax M2")
    (created 1761252093)
    (description "MiniMax-M2 is a compact, high-efficiency large language model optimized for end-to-end coding and agentic workflows. With 10 billion activated parameters (230 billion total), it delivers near-frontier intelligence across general reasoning,...")
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
      (prompt "0.000000255")
      (completion "0.00000102")
    ))
    (top_provider (
      (context_length 204800)
      (max_completion_tokens 131072)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      frequency_penalty
      include_reasoning
      logprobs
      max_tokens
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
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links (
      (details /api/v1/models/minimax/minimax-m2/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena models)
          (category 3d)
          (elo 1151)
          (win_rate 48.3)
          (rank 65)
        )
        (
          (arena models)
          (category codecategories)
          (elo 1163)
          (win_rate 48.1)
          (rank 69)
        )
        (
          (arena models)
          (category dataviz)
          (elo 1168)
          (win_rate 50)
          (rank 64)
        )
        (
          (arena models)
          (category gamedev)
          (elo 1158)
          (win_rate 48.1)
          (rank 65)
        )
        (
          (arena models)
          (category svg)
          (elo 1147)
          (win_rate 55.3)
          (rank 45)
        )
        (
          (arena models)
          (category uicomponent)
          (elo 1169)
          (win_rate 49.2)
          (rank 63)
        )
        (
          (arena models)
          (category website)
          (elo 1165)
          (win_rate 48)
          (rank 70)
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
    (remoteModelId minimax/minimax-m2)
  ))
)
