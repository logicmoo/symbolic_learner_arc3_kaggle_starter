({}
  (kind model)
  (id openrouter-anthropic_claude-opus-4.1)
  (label "Anthropic: Claude Opus 4.1")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model anthropic/claude-opus-4.1)
  (enabled true)
  (capabilities ({}
    (audio false)
    (code false)
    (functionCalling true)
    (json false)
    (jsonMode false)
    (local false)
    (multimodal true)
    (reasoning true)
    (text true)
    (tools true)
    (vision true)
  ))
  (limits ({}
    (contextWindow 200000)
    (maxOutputTokens 32000)
  ))
  (pricing ({}
    (prompt "0.000015")
    (completion "0.000075")
    (web_search "0.01")
    (input_cache_read "0.0000015")
    (input_cache_write "0.00001875")
    (input_cache_write_1h "0.00003")
  ))
  (properties ({}
    (id anthropic/claude-opus-4.1)
    (canonical_slug anthropic/claude-4.1-opus-20250805)
    (hugging_face_id "")
    (name "Anthropic: Claude Opus 4.1")
    (created 1754411591)
    (description "Claude Opus 4.1 is an updated version of Anthropic’s flagship model, offering improved performance in coding, reasoning, and agentic tasks. It achieves 74.5% on SWE-bench Verified and shows notable gains...")
    (context_length 200000)
    (architecture ({}
      (modality text+image+file->text)
      (input_modalities (
        image
        text
        file
      ))
      (output_modalities (
        text
      ))
      (tokenizer Claude)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.000015")
      (completion "0.000075")
      (web_search "0.01")
      (input_cache_read "0.0000015")
      (input_cache_write "0.00001875")
      (input_cache_write_1h "0.00003")
    ))
    (top_provider ({}
      (context_length 200000)
      (max_completion_tokens 32000)
      (is_moderated true)
    ))
    (per_request_limits null)
    (supported_parameters (
      include_reasoning
      max_tokens
      reasoning
      stop
      temperature
      tool_choice
      tools
      top_k
      top_p
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
    (knowledge_cutoff 2025-01-31)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/anthropic/claude-4.1-opus-20250805/endpoints)
    ))
    (benchmarks ({}
      (design_arena (
        ({}
          (arena models)
          (category 3d)
          (elo 1206)
          (win_rate 51.8)
          (rank 45)
        )
        ({}
          (arena models)
          (category asciiart)
          (elo 1203)
          (win_rate 51.4)
          (rank 21)
        )
        ({}
          (arena models)
          (category codecategories)
          (elo 1199)
          (win_rate 55.8)
          (rank 51)
        )
        ({}
          (arena models)
          (category dataviz)
          (elo 1193)
          (win_rate 56.4)
          (rank 51)
        )
        ({}
          (arena models)
          (category gamedev)
          (elo 1212)
          (win_rate 58.5)
          (rank 43)
        )
        ({}
          (arena models)
          (category svg)
          (elo 1199)
          (win_rate 60.8)
          (rank 29)
        )
        ({}
          (arena models)
          (category uicomponent)
          (elo 1196)
          (win_rate 57.9)
          (rank 52)
        )
        ({}
          (arena models)
          (category website)
          (elo 1199)
          (win_rate 55.3)
          (rank 57)
        )
      ))
    ))
    (reasoning ({}
      (mandatory false)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id anthropic/claude-opus-4.1)
    (canonical_slug anthropic/claude-4.1-opus-20250805)
    (hugging_face_id "")
    (name "Anthropic: Claude Opus 4.1")
    (created 1754411591)
    (description "Claude Opus 4.1 is an updated version of Anthropic’s flagship model, offering improved performance in coding, reasoning, and agentic tasks. It achieves 74.5% on SWE-bench Verified and shows notable gains...")
    (context_length 200000)
    (architecture ({}
      (modality text+image+file->text)
      (input_modalities (
        image
        text
        file
      ))
      (output_modalities (
        text
      ))
      (tokenizer Claude)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.000015")
      (completion "0.000075")
      (web_search "0.01")
      (input_cache_read "0.0000015")
      (input_cache_write "0.00001875")
      (input_cache_write_1h "0.00003")
    ))
    (top_provider ({}
      (context_length 200000)
      (max_completion_tokens 32000)
      (is_moderated true)
    ))
    (per_request_limits null)
    (supported_parameters (
      include_reasoning
      max_tokens
      reasoning
      stop
      temperature
      tool_choice
      tools
      top_k
      top_p
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
    (knowledge_cutoff 2025-01-31)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/anthropic/claude-4.1-opus-20250805/endpoints)
    ))
    (benchmarks ({}
      (design_arena (
        ({}
          (arena models)
          (category 3d)
          (elo 1206)
          (win_rate 51.8)
          (rank 45)
        )
        ({}
          (arena models)
          (category asciiart)
          (elo 1203)
          (win_rate 51.4)
          (rank 21)
        )
        ({}
          (arena models)
          (category codecategories)
          (elo 1199)
          (win_rate 55.8)
          (rank 51)
        )
        ({}
          (arena models)
          (category dataviz)
          (elo 1193)
          (win_rate 56.4)
          (rank 51)
        )
        ({}
          (arena models)
          (category gamedev)
          (elo 1212)
          (win_rate 58.5)
          (rank 43)
        )
        ({}
          (arena models)
          (category svg)
          (elo 1199)
          (win_rate 60.8)
          (rank 29)
        )
        ({}
          (arena models)
          (category uicomponent)
          (elo 1196)
          (win_rate 57.9)
          (rank 52)
        )
        ({}
          (arena models)
          (category website)
          (elo 1199)
          (win_rate 55.3)
          (rank 57)
        )
      ))
    ))
    (reasoning ({}
      (mandatory false)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId anthropic/claude-opus-4.1)
  ))
)
