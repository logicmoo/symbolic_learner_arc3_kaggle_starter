(
  (kind model)
  (id openrouter-anthropic_claude-sonnet-4.6)
  (label "Anthropic: Claude Sonnet 4.6")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model anthropic/claude-sonnet-4.6)
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
    (prompt "0.000003")
    (completion "0.000015")
    (web_search "0.01")
    (input_cache_read "0.0000003")
    (input_cache_write "0.00000375")
    (input_cache_write_1h "0.000006")
  ))
  (properties (
    (id anthropic/claude-sonnet-4.6)
    (canonical_slug anthropic/claude-4.6-sonnet-20260217)
    (hugging_face_id "")
    (name "Anthropic: Claude Sonnet 4.6")
    (created 1771342990)
    (description "Sonnet 4.6 is Anthropic's most capable Sonnet-class model yet, with frontier performance across coding, agents, and professional work. It excels at iterative development, complex codebase navigation, end-to-end project management with...")
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
      (prompt "0.000003")
      (completion "0.000015")
      (web_search "0.01")
      (input_cache_read "0.0000003")
      (input_cache_write "0.00000375")
      (input_cache_write_1h "0.000006")
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
      (details /api/v1/models/anthropic/claude-4.6-sonnet-20260217/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena agents)
          (category agenticgamedev)
          (elo 1190)
          (win_rate 52.2)
          (rank 9)
        )
        (
          (arena agents)
          (category androidnative)
          (elo 1227)
          (win_rate 62)
          (rank 9)
        )
        (
          (arena agents)
          (category fullstack)
          (elo 1253)
          (win_rate 64.1)
          (rank 8)
        )
        (
          (arena agents)
          (category godotgamedev)
          (elo 1226)
          (win_rate 60.6)
          (rank 7)
        )
        (
          (arena agents)
          (category mobileapps)
          (elo 1270)
          (win_rate 63.4)
          (rank 2)
        )
        (
          (arena agents)
          (category webapps)
          (elo 1240)
          (win_rate 56.8)
          (rank 15)
        )
        (
          (arena models)
          (category 3d)
          (elo 1289)
          (win_rate 57.6)
          (rank 22)
        )
        (
          (arena models)
          (category asciiart)
          (elo 1268)
          (win_rate 59.8)
          (rank 10)
        )
        (
          (arena models)
          (category codecategories)
          (elo 1305)
          (win_rate 59.5)
          (rank 10)
        )
        (
          (arena models)
          (category dataviz)
          (elo 1309)
          (win_rate 58.3)
          (rank 12)
        )
        (
          (arena models)
          (category gamedev)
          (elo 1300)
          (win_rate 58.9)
          (rank 15)
        )
        (
          (arena models)
          (category svg)
          (elo 1244)
          (win_rate 58.8)
          (rank 14)
        )
        (
          (arena models)
          (category uicomponent)
          (elo 1306)
          (win_rate 58.4)
          (rank 13)
        )
        (
          (arena models)
          (category website)
          (elo 1308)
          (win_rate 60.1)
          (rank 10)
        )
      ))
      (artificial_analysis (
        (intelligence_index 48.4)
        (coding_index 63)
        (agentic_index 42.1)
      ))
    ))
    (reasoning (
      (mandatory false)
      (supported_efforts ([]
        max
        high
        medium
        low
      ))
      (default_effort medium)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id anthropic/claude-sonnet-4.6)
    (canonical_slug anthropic/claude-4.6-sonnet-20260217)
    (hugging_face_id "")
    (name "Anthropic: Claude Sonnet 4.6")
    (created 1771342990)
    (description "Sonnet 4.6 is Anthropic's most capable Sonnet-class model yet, with frontier performance across coding, agents, and professional work. It excels at iterative development, complex codebase navigation, end-to-end project management with...")
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
      (prompt "0.000003")
      (completion "0.000015")
      (web_search "0.01")
      (input_cache_read "0.0000003")
      (input_cache_write "0.00000375")
      (input_cache_write_1h "0.000006")
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
      (details /api/v1/models/anthropic/claude-4.6-sonnet-20260217/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena agents)
          (category agenticgamedev)
          (elo 1190)
          (win_rate 52.2)
          (rank 9)
        )
        (
          (arena agents)
          (category androidnative)
          (elo 1227)
          (win_rate 62)
          (rank 9)
        )
        (
          (arena agents)
          (category fullstack)
          (elo 1253)
          (win_rate 64.1)
          (rank 8)
        )
        (
          (arena agents)
          (category godotgamedev)
          (elo 1226)
          (win_rate 60.6)
          (rank 7)
        )
        (
          (arena agents)
          (category mobileapps)
          (elo 1270)
          (win_rate 63.4)
          (rank 2)
        )
        (
          (arena agents)
          (category webapps)
          (elo 1240)
          (win_rate 56.8)
          (rank 15)
        )
        (
          (arena models)
          (category 3d)
          (elo 1289)
          (win_rate 57.6)
          (rank 22)
        )
        (
          (arena models)
          (category asciiart)
          (elo 1268)
          (win_rate 59.8)
          (rank 10)
        )
        (
          (arena models)
          (category codecategories)
          (elo 1305)
          (win_rate 59.5)
          (rank 10)
        )
        (
          (arena models)
          (category dataviz)
          (elo 1309)
          (win_rate 58.3)
          (rank 12)
        )
        (
          (arena models)
          (category gamedev)
          (elo 1300)
          (win_rate 58.9)
          (rank 15)
        )
        (
          (arena models)
          (category svg)
          (elo 1244)
          (win_rate 58.8)
          (rank 14)
        )
        (
          (arena models)
          (category uicomponent)
          (elo 1306)
          (win_rate 58.4)
          (rank 13)
        )
        (
          (arena models)
          (category website)
          (elo 1308)
          (win_rate 60.1)
          (rank 10)
        )
      ))
      (artificial_analysis (
        (intelligence_index 48.4)
        (coding_index 63)
        (agentic_index 42.1)
      ))
    ))
    (reasoning (
      (mandatory false)
      (supported_efforts ([]
        max
        high
        medium
        low
      ))
      (default_effort medium)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId anthropic/claude-sonnet-4.6)
  ))
)
