(
  (kind model)
  (id openrouter-anthropic_claude-opus-4.6)
  (label "Anthropic: Claude Opus 4.6")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model anthropic/claude-opus-4.6)
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
    (contextWindow 1000000)
    (maxOutputTokens 128000)
  ))
  (pricing (
    (prompt "0.000005")
    (completion "0.000025")
    (web_search "0.01")
    (input_cache_read "0.0000005")
    (input_cache_write "0.00000625")
    (input_cache_write_1h "0.00001")
  ))
  (properties (
    (id anthropic/claude-opus-4.6)
    (canonical_slug anthropic/claude-4.6-opus-20260205)
    (hugging_face_id "")
    (name "Anthropic: Claude Opus 4.6")
    (created 1770219050)
    (description "Opus 4.6 is Anthropic’s strongest model for coding and long-running professional tasks. It is built for agents that operate across entire workflows rather than single prompts, making it especially effective...")
    (context_length 1000000)
    (architecture (
      (modality text+image+file->text)
      (input_modalities ([]
        text
        image
        file
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Claude)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.000005")
      (completion "0.000025")
      (web_search "0.01")
      (input_cache_read "0.0000005")
      (input_cache_write "0.00000625")
      (input_cache_write_1h "0.00001")
    ))
    (top_provider (
      (context_length 1000000)
      (max_completion_tokens 128000)
      (is_moderated true)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      include_reasoning
      max_completion_tokens
      max_tokens
      reasoning
      reasoning_effort
      response_format
      stop
      structured_outputs
      temperature
      tool_choice
      tools
      top_k
      top_p
      verbosity
    ))
    (default_parameters (
      (temperature null)
      (top_p null)
      (top_k null)
      (frequency_penalty null)
      (presence_penalty null)
      (repetition_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links (
      (details /api/v1/models/anthropic/claude-4.6-opus-20260205/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena agents)
          (category androidnative)
          (elo 1232)
          (win_rate 68)
          (rank 7)
        )
        (
          (arena agents)
          (category fullstack)
          (elo 1263)
          (win_rate 68.5)
          (rank 7)
        )
        (
          (arena agents)
          (category mobileapps)
          (elo 1278)
          (win_rate 64.7)
          (rank 1)
        )
        (
          (arena agents)
          (category webapps)
          (elo 1252)
          (win_rate 60.6)
          (rank 12)
        )
        (
          (arena models)
          (category 3d)
          (elo 1329)
          (win_rate 62.5)
          (rank 8)
        )
        (
          (arena models)
          (category asciiart)
          (elo 1291)
          (win_rate 63)
          (rank 8)
        )
        (
          (arena models)
          (category codecategories)
          (elo 1318)
          (win_rate 61.3)
          (rank 5)
        )
        (
          (arena models)
          (category dataviz)
          (elo 1311)
          (win_rate 58.7)
          (rank 10)
        )
        (
          (arena models)
          (category gamedev)
          (elo 1320)
          (win_rate 61.2)
          (rank 10)
        )
        (
          (arena models)
          (category svg)
          (elo 1275)
          (win_rate 61)
          (rank 5)
        )
        (
          (arena models)
          (category uicomponent)
          (elo 1319)
          (win_rate 60)
          (rank 9)
        )
        (
          (arena models)
          (category website)
          (elo 1314)
          (win_rate 61.2)
          (rank 9)
        )
      ))
    ))
    (reasoning (
      (mandatory false)
      (default_enabled false)
      (supports_max_tokens true)
      (supported_efforts ([]
        max
        high
        medium
        low
      ))
      (default_effort high)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id anthropic/claude-opus-4.6)
    (canonical_slug anthropic/claude-4.6-opus-20260205)
    (hugging_face_id "")
    (name "Anthropic: Claude Opus 4.6")
    (created 1770219050)
    (description "Opus 4.6 is Anthropic’s strongest model for coding and long-running professional tasks. It is built for agents that operate across entire workflows rather than single prompts, making it especially effective...")
    (context_length 1000000)
    (architecture (
      (modality text+image+file->text)
      (input_modalities ([]
        text
        image
        file
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Claude)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.000005")
      (completion "0.000025")
      (web_search "0.01")
      (input_cache_read "0.0000005")
      (input_cache_write "0.00000625")
      (input_cache_write_1h "0.00001")
    ))
    (top_provider (
      (context_length 1000000)
      (max_completion_tokens 128000)
      (is_moderated true)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      include_reasoning
      max_completion_tokens
      max_tokens
      reasoning
      reasoning_effort
      response_format
      stop
      structured_outputs
      temperature
      tool_choice
      tools
      top_k
      top_p
      verbosity
    ))
    (default_parameters (
      (temperature null)
      (top_p null)
      (top_k null)
      (frequency_penalty null)
      (presence_penalty null)
      (repetition_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links (
      (details /api/v1/models/anthropic/claude-4.6-opus-20260205/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena agents)
          (category androidnative)
          (elo 1232)
          (win_rate 68)
          (rank 7)
        )
        (
          (arena agents)
          (category fullstack)
          (elo 1263)
          (win_rate 68.5)
          (rank 7)
        )
        (
          (arena agents)
          (category mobileapps)
          (elo 1278)
          (win_rate 64.7)
          (rank 1)
        )
        (
          (arena agents)
          (category webapps)
          (elo 1252)
          (win_rate 60.6)
          (rank 12)
        )
        (
          (arena models)
          (category 3d)
          (elo 1329)
          (win_rate 62.5)
          (rank 8)
        )
        (
          (arena models)
          (category asciiart)
          (elo 1291)
          (win_rate 63)
          (rank 8)
        )
        (
          (arena models)
          (category codecategories)
          (elo 1318)
          (win_rate 61.3)
          (rank 5)
        )
        (
          (arena models)
          (category dataviz)
          (elo 1311)
          (win_rate 58.7)
          (rank 10)
        )
        (
          (arena models)
          (category gamedev)
          (elo 1320)
          (win_rate 61.2)
          (rank 10)
        )
        (
          (arena models)
          (category svg)
          (elo 1275)
          (win_rate 61)
          (rank 5)
        )
        (
          (arena models)
          (category uicomponent)
          (elo 1319)
          (win_rate 60)
          (rank 9)
        )
        (
          (arena models)
          (category website)
          (elo 1314)
          (win_rate 61.2)
          (rank 9)
        )
      ))
    ))
    (reasoning (
      (mandatory false)
      (default_enabled false)
      (supports_max_tokens true)
      (supported_efforts ([]
        max
        high
        medium
        low
      ))
      (default_effort high)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId anthropic/claude-opus-4.6)
  ))
)
