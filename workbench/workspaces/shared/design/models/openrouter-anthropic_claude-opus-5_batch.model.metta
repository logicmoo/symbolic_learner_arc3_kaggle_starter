({}
  (kind model)
  (id openrouter-anthropic_claude-opus-5_batch)
  (label "Claude Opus 5 (batch)")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model anthropic/claude-opus-5:batch)
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
    (id anthropic/claude-opus-5:batch)
    (canonical_slug anthropic/claude-opus-5-20260723)
    (hugging_face_id null)
    (name "Claude Opus 5 (batch)")
    (created 1784912544)
    (description "Claude Opus 5 is Anthropic’s flagship model for demanding reasoning, coding, and long-horizon agentic work. It is particularly strong at end-to-end software tasks, code review and bug finding, visual analysis...")
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
      (details /api/v1/models/anthropic/claude-opus-5-20260723/endpoints)
    ))
    (benchmarks ({}
      (design_arena (
        ({}
          (arena agents)
          (category webapps)
          (elo 1287)
          (win_rate 55.8)
          (rank 5)
        )
        ({}
          (arena models)
          (category 3d)
          (elo 1390)
          (win_rate 64.9)
          (rank 2)
        )
        ({}
          (arena models)
          (category codecategories)
          (elo 1359)
          (win_rate 60.8)
          (rank 2)
        )
        ({}
          (arena models)
          (category dataviz)
          (elo 1394)
          (win_rate 65.3)
          (rank 1)
        )
        ({}
          (arena models)
          (category gamedev)
          (elo 1443)
          (win_rate 71.7)
          (rank 1)
        )
        ({}
          (arena models)
          (category uicomponent)
          (elo 1384)
          (win_rate 62.1)
          (rank 2)
        )
        ({}
          (arena models)
          (category website)
          (elo 1339)
          (win_rate 58.8)
          (rank 2)
        )
      ))
      (artificial_analysis ({}
        (intelligence_index 63.1)
        (coding_index 78)
        (agentic_index 59.2)
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
    (id anthropic/claude-opus-5:batch)
    (canonical_slug anthropic/claude-opus-5-20260723)
    (hugging_face_id null)
    (name "Claude Opus 5 (batch)")
    (created 1784912544)
    (description "Claude Opus 5 is Anthropic’s flagship model for demanding reasoning, coding, and long-horizon agentic work. It is particularly strong at end-to-end software tasks, code review and bug finding, visual analysis...")
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
      (details /api/v1/models/anthropic/claude-opus-5-20260723/endpoints)
    ))
    (benchmarks ({}
      (design_arena (
        ({}
          (arena agents)
          (category webapps)
          (elo 1287)
          (win_rate 55.8)
          (rank 5)
        )
        ({}
          (arena models)
          (category 3d)
          (elo 1390)
          (win_rate 64.9)
          (rank 2)
        )
        ({}
          (arena models)
          (category codecategories)
          (elo 1359)
          (win_rate 60.8)
          (rank 2)
        )
        ({}
          (arena models)
          (category dataviz)
          (elo 1394)
          (win_rate 65.3)
          (rank 1)
        )
        ({}
          (arena models)
          (category gamedev)
          (elo 1443)
          (win_rate 71.7)
          (rank 1)
        )
        ({}
          (arena models)
          (category uicomponent)
          (elo 1384)
          (win_rate 62.1)
          (rank 2)
        )
        ({}
          (arena models)
          (category website)
          (elo 1339)
          (win_rate 58.8)
          (rank 2)
        )
      ))
      (artificial_analysis ({}
        (intelligence_index 63.1)
        (coding_index 78)
        (agentic_index 59.2)
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
    (remoteModelId anthropic/claude-opus-5:batch)
  ))
)
