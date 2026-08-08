({}
  (kind model)
  (id openrouter-anthropic_claude-opus-4.8_batch)
  (label "Anthropic: Claude Opus 4.8 (batch)")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model anthropic/claude-opus-4.8:batch)
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
    (prompt "0.0000025")
    (completion "0.0000125")
    (web_search "0.01")
    (input_cache_read "0.00000025")
    (input_cache_write "0.000003125")
    (input_cache_write_1h "0.000005")
  ))
  (properties ({}
    (id anthropic/claude-opus-4.8:batch)
    (canonical_slug anthropic/claude-4.8-opus-20260528)
    (hugging_face_id null)
    (name "Anthropic: Claude Opus 4.8 (batch)")
    (created 1779905091)
    (description "Claude Opus 4.8 is Anthropic's most capable generally available model in the Opus family. It supports text, image, and file inputs with text output, with reasoning support and a 1M-token...")
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
      (prompt "0.0000025")
      (completion "0.0000125")
      (web_search "0.01")
      (input_cache_read "0.00000025")
      (input_cache_write "0.000003125")
      (input_cache_write_1h "0.000005")
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
      (details /api/v1/models/anthropic/claude-4.8-opus-20260528/endpoints)
    ))
    (benchmarks ({}
      (design_arena (
        ({}
          (arena agents)
          (category agenticgamedev)
          (elo 1262)
          (win_rate 61.6)
          (rank 2)
        )
        ({}
          (arena agents)
          (category agentichtmlslides)
          (elo 1227)
          (win_rate 55.6)
          (rank 4)
        )
        ({}
          (arena agents)
          (category agenticslides)
          (elo 1294)
          (win_rate 64.8)
          (rank 2)
        )
        ({}
          (arena agents)
          (category "agenticslides(html)")
          (elo 1230)
          (win_rate 56)
          (rank 4)
        )
        ({}
          (arena agents)
          (category "agenticslides(python-pptx)")
          (elo 1310)
          (win_rate 68.9)
          (rank 2)
        )
        ({}
          (arena agents)
          (category androidnative)
          (elo 1265)
          (win_rate 59.5)
          (rank 5)
        )
        ({}
          (arena agents)
          (category fullstack)
          (elo 1284)
          (win_rate 62)
          (rank 4)
        )
        ({}
          (arena agents)
          (category godotgamedev)
          (elo 1254)
          (win_rate 58.9)
          (rank 5)
        )
        ({}
          (arena agents)
          (category htmlslides)
          (elo 1238)
          (win_rate 57.1)
          (rank 3)
        )
        ({}
          (arena agents)
          (category mobileapps)
          (elo 1256)
          (win_rate 57.6)
          (rank 4)
        )
        ({}
          (arena agents)
          (category pptxslides)
          (elo 1306)
          (win_rate 67.9)
          (rank 2)
        )
        ({}
          (arena agents)
          (category python-pptxslides)
          (elo 1298)
          (win_rate 65.9)
          (rank 4)
        )
        ({}
          (arena agents)
          (category webapps)
          (elo 1272)
          (win_rate 53.8)
          (rank 6)
        )
        ({}
          (arena models)
          (category 3d)
          (elo 1274)
          (win_rate 53.3)
          (rank 25)
        )
        ({}
          (arena models)
          (category asciiart)
          (elo 1308)
          (win_rate 63.3)
          (rank 4)
        )
        ({}
          (arena models)
          (category codecategories)
          (elo 1271)
          (win_rate 53.7)
          (rank 24)
        )
        ({}
          (arena models)
          (category dataviz)
          (elo 1265)
          (win_rate 54.6)
          (rank 22)
        )
        ({}
          (arena models)
          (category gamedev)
          (elo 1284)
          (win_rate 54.4)
          (rank 20)
        )
        ({}
          (arena models)
          (category svg)
          (elo 1225)
          (win_rate 53.4)
          (rank 19)
        )
        ({}
          (arena models)
          (category uicomponent)
          (elo 1280)
          (win_rate 54.6)
          (rank 23)
        )
        ({}
          (arena models)
          (category website)
          (elo 1270)
          (win_rate 54.1)
          (rank 28)
        )
      ))
      (artificial_analysis ({}
        (intelligence_index 57.3)
        (coding_index 74.3)
        (agentic_index 49.4)
      ))
    ))
    (reasoning ({}
      (mandatory false)
      (default_enabled false)
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
    (id anthropic/claude-opus-4.8:batch)
    (canonical_slug anthropic/claude-4.8-opus-20260528)
    (hugging_face_id null)
    (name "Anthropic: Claude Opus 4.8 (batch)")
    (created 1779905091)
    (description "Claude Opus 4.8 is Anthropic's most capable generally available model in the Opus family. It supports text, image, and file inputs with text output, with reasoning support and a 1M-token...")
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
      (prompt "0.0000025")
      (completion "0.0000125")
      (web_search "0.01")
      (input_cache_read "0.00000025")
      (input_cache_write "0.000003125")
      (input_cache_write_1h "0.000005")
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
      (details /api/v1/models/anthropic/claude-4.8-opus-20260528/endpoints)
    ))
    (benchmarks ({}
      (design_arena (
        ({}
          (arena agents)
          (category agenticgamedev)
          (elo 1262)
          (win_rate 61.6)
          (rank 2)
        )
        ({}
          (arena agents)
          (category agentichtmlslides)
          (elo 1227)
          (win_rate 55.6)
          (rank 4)
        )
        ({}
          (arena agents)
          (category agenticslides)
          (elo 1294)
          (win_rate 64.8)
          (rank 2)
        )
        ({}
          (arena agents)
          (category "agenticslides(html)")
          (elo 1230)
          (win_rate 56)
          (rank 4)
        )
        ({}
          (arena agents)
          (category "agenticslides(python-pptx)")
          (elo 1310)
          (win_rate 68.9)
          (rank 2)
        )
        ({}
          (arena agents)
          (category androidnative)
          (elo 1265)
          (win_rate 59.5)
          (rank 5)
        )
        ({}
          (arena agents)
          (category fullstack)
          (elo 1284)
          (win_rate 62)
          (rank 4)
        )
        ({}
          (arena agents)
          (category godotgamedev)
          (elo 1254)
          (win_rate 58.9)
          (rank 5)
        )
        ({}
          (arena agents)
          (category htmlslides)
          (elo 1238)
          (win_rate 57.1)
          (rank 3)
        )
        ({}
          (arena agents)
          (category mobileapps)
          (elo 1256)
          (win_rate 57.6)
          (rank 4)
        )
        ({}
          (arena agents)
          (category pptxslides)
          (elo 1306)
          (win_rate 67.9)
          (rank 2)
        )
        ({}
          (arena agents)
          (category python-pptxslides)
          (elo 1298)
          (win_rate 65.9)
          (rank 4)
        )
        ({}
          (arena agents)
          (category webapps)
          (elo 1272)
          (win_rate 53.8)
          (rank 6)
        )
        ({}
          (arena models)
          (category 3d)
          (elo 1274)
          (win_rate 53.3)
          (rank 25)
        )
        ({}
          (arena models)
          (category asciiart)
          (elo 1308)
          (win_rate 63.3)
          (rank 4)
        )
        ({}
          (arena models)
          (category codecategories)
          (elo 1271)
          (win_rate 53.7)
          (rank 24)
        )
        ({}
          (arena models)
          (category dataviz)
          (elo 1265)
          (win_rate 54.6)
          (rank 22)
        )
        ({}
          (arena models)
          (category gamedev)
          (elo 1284)
          (win_rate 54.4)
          (rank 20)
        )
        ({}
          (arena models)
          (category svg)
          (elo 1225)
          (win_rate 53.4)
          (rank 19)
        )
        ({}
          (arena models)
          (category uicomponent)
          (elo 1280)
          (win_rate 54.6)
          (rank 23)
        )
        ({}
          (arena models)
          (category website)
          (elo 1270)
          (win_rate 54.1)
          (rank 28)
        )
      ))
      (artificial_analysis ({}
        (intelligence_index 57.3)
        (coding_index 74.3)
        (agentic_index 49.4)
      ))
    ))
    (reasoning ({}
      (mandatory false)
      (default_enabled false)
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
    (remoteModelId anthropic/claude-opus-4.8:batch)
  ))
)
