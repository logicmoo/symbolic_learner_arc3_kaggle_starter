({}
  (kind model)
  (id openrouter-anthropic_claude-sonnet-5_batch)
  (label "Anthropic: Claude Sonnet 5 (batch)")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model anthropic/claude-sonnet-5:batch)
  (enabled true)
  (capabilities ({}
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
  (limits ({}
    (contextWindow 1000000)
    (maxOutputTokens 128000)
  ))
  (pricing ({}
    (prompt "0.000001")
    (completion "0.000005")
    (web_search "0.01")
    (input_cache_read "0.0000001")
    (input_cache_write "0.00000125")
    (input_cache_write_1h "0.000002")
  ))
  (properties ({}
    (id anthropic/claude-sonnet-5:batch)
    (canonical_slug anthropic/claude-sonnet-5-20260630)
    (hugging_face_id null)
    (name "Anthropic: Claude Sonnet 5 (batch)")
    (created 1782843083)
    (description "Sonnet 5 is Anthropic's most capable Sonnet-class model, with frontier performance across coding, agents, and professional work. It supports adaptive thinking with selectable reasoning effort levels (low, medium, high, max,...")
    (context_length 1000000)
    (architecture ({}
      (modality text+image+file->text)
      (input_modalities (
        text
        image
        file
      ))
      (output_modalities (
        text
      ))
      (tokenizer Claude)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.000001")
      (completion "0.000005")
      (web_search "0.01")
      (input_cache_read "0.0000001")
      (input_cache_write "0.00000125")
      (input_cache_write_1h "0.000002")
    ))
    (top_provider ({}
      (context_length 1000000)
      (max_completion_tokens 128000)
      (is_moderated true)
    ))
    (per_request_limits null)
    (supported_parameters (
      include_reasoning
      max_tokens
      reasoning
      reasoning_effort
      response_format
      stop
      structured_outputs
      tool_choice
      tools
      verbosity
    ))
    (default_parameters ({}
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
    (links ({}
      (details /api/v1/models/anthropic/claude-sonnet-5-20260630/endpoints)
    ))
    (benchmarks ({}
      (design_arena (
        ({}
          (arena agents)
          (category agenticgamedev)
          (elo 1241)
          (win_rate 56)
          (rank 4)
        )
        ({}
          (arena agents)
          (category androidnative)
          (elo 1269)
          (win_rate 59.1)
          (rank 3)
        )
        ({}
          (arena agents)
          (category fullstack)
          (elo 1274)
          (win_rate 59.9)
          (rank 6)
        )
        ({}
          (arena agents)
          (category godotgamedev)
          (elo 1269)
          (win_rate 60.4)
          (rank 4)
        )
        ({}
          (arena agents)
          (category htmlslides)
          (elo 1232)
          (win_rate 54.1)
          (rank 4)
        )
        ({}
          (arena agents)
          (category mobileapps)
          (elo 1238)
          (win_rate 55.1)
          (rank 8)
        )
        ({}
          (arena agents)
          (category python-pptxslides)
          (elo 1248)
          (win_rate 55.2)
          (rank 6)
        )
        ({}
          (arena agents)
          (category webapps)
          (elo 1301)
          (win_rate 58.4)
          (rank 4)
        )
        ({}
          (arena models)
          (category 3d)
          (elo 1306)
          (win_rate 56.1)
          (rank 13)
        )
        ({}
          (arena models)
          (category asciiart)
          (elo 1246)
          (win_rate 52.8)
          (rank 13)
        )
        ({}
          (arena models)
          (category codecategories)
          (elo 1301)
          (win_rate 55)
          (rank 15)
        )
        ({}
          (arena models)
          (category dataviz)
          (elo 1264)
          (win_rate 52.6)
          (rank 23)
        )
        ({}
          (arena models)
          (category gamedev)
          (elo 1337)
          (win_rate 55.9)
          (rank 4)
        )
        ({}
          (arena models)
          (category svg)
          (elo 1238)
          (win_rate 53.7)
          (rank 16)
        )
        ({}
          (arena models)
          (category uicomponent)
          (elo 1311)
          (win_rate 55)
          (rank 10)
        )
        ({}
          (arena models)
          (category website)
          (elo 1297)
          (win_rate 55.3)
          (rank 12)
        )
      ))
      (artificial_analysis ({}
        (intelligence_index 55.3)
        (coding_index 71.5)
        (agentic_index 49.7)
      ))
    ))
    (reasoning ({}
      (mandatory false)
      (default_enabled true)
      (supported_efforts (
        max
        xhigh
        high
        medium
        low
      ))
      (default_effort high)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id anthropic/claude-sonnet-5:batch)
    (canonical_slug anthropic/claude-sonnet-5-20260630)
    (hugging_face_id null)
    (name "Anthropic: Claude Sonnet 5 (batch)")
    (created 1782843083)
    (description "Sonnet 5 is Anthropic's most capable Sonnet-class model, with frontier performance across coding, agents, and professional work. It supports adaptive thinking with selectable reasoning effort levels (low, medium, high, max,...")
    (context_length 1000000)
    (architecture ({}
      (modality text+image+file->text)
      (input_modalities (
        text
        image
        file
      ))
      (output_modalities (
        text
      ))
      (tokenizer Claude)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.000001")
      (completion "0.000005")
      (web_search "0.01")
      (input_cache_read "0.0000001")
      (input_cache_write "0.00000125")
      (input_cache_write_1h "0.000002")
    ))
    (top_provider ({}
      (context_length 1000000)
      (max_completion_tokens 128000)
      (is_moderated true)
    ))
    (per_request_limits null)
    (supported_parameters (
      include_reasoning
      max_tokens
      reasoning
      reasoning_effort
      response_format
      stop
      structured_outputs
      tool_choice
      tools
      verbosity
    ))
    (default_parameters ({}
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
    (links ({}
      (details /api/v1/models/anthropic/claude-sonnet-5-20260630/endpoints)
    ))
    (benchmarks ({}
      (design_arena (
        ({}
          (arena agents)
          (category agenticgamedev)
          (elo 1241)
          (win_rate 56)
          (rank 4)
        )
        ({}
          (arena agents)
          (category androidnative)
          (elo 1269)
          (win_rate 59.1)
          (rank 3)
        )
        ({}
          (arena agents)
          (category fullstack)
          (elo 1274)
          (win_rate 59.9)
          (rank 6)
        )
        ({}
          (arena agents)
          (category godotgamedev)
          (elo 1269)
          (win_rate 60.4)
          (rank 4)
        )
        ({}
          (arena agents)
          (category htmlslides)
          (elo 1232)
          (win_rate 54.1)
          (rank 4)
        )
        ({}
          (arena agents)
          (category mobileapps)
          (elo 1238)
          (win_rate 55.1)
          (rank 8)
        )
        ({}
          (arena agents)
          (category python-pptxslides)
          (elo 1248)
          (win_rate 55.2)
          (rank 6)
        )
        ({}
          (arena agents)
          (category webapps)
          (elo 1301)
          (win_rate 58.4)
          (rank 4)
        )
        ({}
          (arena models)
          (category 3d)
          (elo 1306)
          (win_rate 56.1)
          (rank 13)
        )
        ({}
          (arena models)
          (category asciiart)
          (elo 1246)
          (win_rate 52.8)
          (rank 13)
        )
        ({}
          (arena models)
          (category codecategories)
          (elo 1301)
          (win_rate 55)
          (rank 15)
        )
        ({}
          (arena models)
          (category dataviz)
          (elo 1264)
          (win_rate 52.6)
          (rank 23)
        )
        ({}
          (arena models)
          (category gamedev)
          (elo 1337)
          (win_rate 55.9)
          (rank 4)
        )
        ({}
          (arena models)
          (category svg)
          (elo 1238)
          (win_rate 53.7)
          (rank 16)
        )
        ({}
          (arena models)
          (category uicomponent)
          (elo 1311)
          (win_rate 55)
          (rank 10)
        )
        ({}
          (arena models)
          (category website)
          (elo 1297)
          (win_rate 55.3)
          (rank 12)
        )
      ))
      (artificial_analysis ({}
        (intelligence_index 55.3)
        (coding_index 71.5)
        (agentic_index 49.7)
      ))
    ))
    (reasoning ({}
      (mandatory false)
      (default_enabled true)
      (supported_efforts (
        max
        xhigh
        high
        medium
        low
      ))
      (default_effort high)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId anthropic/claude-sonnet-5:batch)
  ))
)
