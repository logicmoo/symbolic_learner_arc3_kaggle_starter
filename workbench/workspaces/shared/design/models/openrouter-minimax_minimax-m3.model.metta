(
  (kind model)
  (id openrouter-minimax_minimax-m3)
  (label "MiniMax: MiniMax M3")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model minimax/minimax-m3)
  (enabled true)
  (capabilities (
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
  (limits (
    (contextWindow 1048576)
    (maxOutputTokens 512000)
  ))
  (pricing (
    (prompt "0.0000003")
    (completion "0.0000012")
    (input_cache_read "0.00000006")
  ))
  (properties (
    (id minimax/minimax-m3)
    (canonical_slug minimax/minimax-m3-20260531)
    (hugging_face_id MiniMaxAI/Minimax-M3)
    (name "MiniMax: MiniMax M3")
    (created 1780245374)
    (description "MiniMax-M3 is a multimodal foundation model from MiniMax. It supports text, image, and video inputs with text output, a 1M-token context window, and is suited for long-horizon agentic work, coding,...")
    (context_length 1048576)
    (architecture (
      (modality text+image+video->text)
      (input_modalities ([]
        text
        image
        video
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Other)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.0000003")
      (completion "0.0000012")
      (input_cache_read "0.00000006")
    ))
    (top_provider (
      (context_length 524288)
      (max_completion_tokens 512000)
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
      (details /api/v1/models/minimax/minimax-m3-20260531/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena agents)
          (category agenticgamedev)
          (elo 1196)
          (win_rate 52.3)
          (rank 7)
        )
        (
          (arena agents)
          (category androidnative)
          (elo 1192)
          (win_rate 49.4)
          (rank 16)
        )
        (
          (arena agents)
          (category fullstack)
          (elo 1227)
          (win_rate 52.8)
          (rank 11)
        )
        (
          (arena agents)
          (category htmlslides)
          (elo 1206)
          (win_rate 51.6)
          (rank 10)
        )
        (
          (arena agents)
          (category mobileapps)
          (elo 1242)
          (win_rate 56.1)
          (rank 7)
        )
        (
          (arena agents)
          (category webapps)
          (elo 1249)
          (win_rate 52.4)
          (rank 13)
        )
        (
          (arena models)
          (category 3d)
          (elo 1272)
          (win_rate 53.8)
          (rank 27)
        )
        (
          (arena models)
          (category asciiart)
          (elo 1192)
          (win_rate 47.1)
          (rank 23)
        )
        (
          (arena models)
          (category codecategories)
          (elo 1283)
          (win_rate 54.2)
          (rank 22)
        )
        (
          (arena models)
          (category dataviz)
          (elo 1262)
          (win_rate 53)
          (rank 27)
        )
        (
          (arena models)
          (category gamedev)
          (elo 1264)
          (win_rate 51)
          (rank 26)
        )
        (
          (arena models)
          (category svg)
          (elo 1216)
          (win_rate 49.7)
          (rank 24)
        )
        (
          (arena models)
          (category uicomponent)
          (elo 1283)
          (win_rate 53.9)
          (rank 22)
        )
        (
          (arena models)
          (category website)
          (elo 1284)
          (win_rate 54.4)
          (rank 21)
        )
      ))
      (artificial_analysis (
        (intelligence_index 45.4)
        (coding_index 58.6)
        (agentic_index 36.1)
      ))
    ))
    (reasoning (
      (mandatory false)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id minimax/minimax-m3)
    (canonical_slug minimax/minimax-m3-20260531)
    (hugging_face_id MiniMaxAI/Minimax-M3)
    (name "MiniMax: MiniMax M3")
    (created 1780245374)
    (description "MiniMax-M3 is a multimodal foundation model from MiniMax. It supports text, image, and video inputs with text output, a 1M-token context window, and is suited for long-horizon agentic work, coding,...")
    (context_length 1048576)
    (architecture (
      (modality text+image+video->text)
      (input_modalities ([]
        text
        image
        video
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Other)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.0000003")
      (completion "0.0000012")
      (input_cache_read "0.00000006")
    ))
    (top_provider (
      (context_length 524288)
      (max_completion_tokens 512000)
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
      (details /api/v1/models/minimax/minimax-m3-20260531/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena agents)
          (category agenticgamedev)
          (elo 1196)
          (win_rate 52.3)
          (rank 7)
        )
        (
          (arena agents)
          (category androidnative)
          (elo 1192)
          (win_rate 49.4)
          (rank 16)
        )
        (
          (arena agents)
          (category fullstack)
          (elo 1227)
          (win_rate 52.8)
          (rank 11)
        )
        (
          (arena agents)
          (category htmlslides)
          (elo 1206)
          (win_rate 51.6)
          (rank 10)
        )
        (
          (arena agents)
          (category mobileapps)
          (elo 1242)
          (win_rate 56.1)
          (rank 7)
        )
        (
          (arena agents)
          (category webapps)
          (elo 1249)
          (win_rate 52.4)
          (rank 13)
        )
        (
          (arena models)
          (category 3d)
          (elo 1272)
          (win_rate 53.8)
          (rank 27)
        )
        (
          (arena models)
          (category asciiart)
          (elo 1192)
          (win_rate 47.1)
          (rank 23)
        )
        (
          (arena models)
          (category codecategories)
          (elo 1283)
          (win_rate 54.2)
          (rank 22)
        )
        (
          (arena models)
          (category dataviz)
          (elo 1262)
          (win_rate 53)
          (rank 27)
        )
        (
          (arena models)
          (category gamedev)
          (elo 1264)
          (win_rate 51)
          (rank 26)
        )
        (
          (arena models)
          (category svg)
          (elo 1216)
          (win_rate 49.7)
          (rank 24)
        )
        (
          (arena models)
          (category uicomponent)
          (elo 1283)
          (win_rate 53.9)
          (rank 22)
        )
        (
          (arena models)
          (category website)
          (elo 1284)
          (win_rate 54.4)
          (rank 21)
        )
      ))
      (artificial_analysis (
        (intelligence_index 45.4)
        (coding_index 58.6)
        (agentic_index 36.1)
      ))
    ))
    (reasoning (
      (mandatory false)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId minimax/minimax-m3)
  ))
)
