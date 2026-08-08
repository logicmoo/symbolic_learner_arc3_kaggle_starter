({}
  (kind model)
  (id openrouter-anthropic_claude-opus-4.5_batch)
  (label "Anthropic: Claude Opus 4.5 (batch)")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model anthropic/claude-opus-4.5:batch)
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
    (contextWindow 200000)
    (maxOutputTokens 64000)
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
    (id anthropic/claude-opus-4.5:batch)
    (canonical_slug anthropic/claude-4.5-opus-20251124)
    (hugging_face_id "")
    (name "Anthropic: Claude Opus 4.5 (batch)")
    (created 1764010580)
    (description "Claude Opus 4.5 is Anthropic’s frontier reasoning model optimized for complex software engineering, agentic workflows, and long-horizon computer use. It offers strong multimodal capabilities, competitive performance across real-world coding and...")
    (context_length 200000)
    (architecture ({}
      (modality text+image+file->text)
      (input_modalities (
        file
        image
        text
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
      (context_length 200000)
      (max_completion_tokens 64000)
      (is_moderated true)
    ))
    (per_request_limits null)
    (supported_parameters (
      include_reasoning
      max_tokens
      reasoning
      response_format
      stop
      structured_outputs
      temperature
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
      (details /api/v1/models/anthropic/claude-4.5-opus-20251124/endpoints)
    ))
    (benchmarks ({}
      (design_arena (
        ({}
          (arena models)
          (category 3d)
          (elo 1267)
          (win_rate 58.5)
          (rank 29)
        )
        ({}
          (arena models)
          (category asciiart)
          (elo 1227)
          (win_rate 54.7)
          (rank 17)
        )
        ({}
          (arena models)
          (category codecategories)
          (elo 1270)
          (win_rate 59.6)
          (rank 26)
        )
        ({}
          (arena models)
          (category dataviz)
          (elo 1270)
          (win_rate 58.5)
          (rank 20)
        )
        ({}
          (arena models)
          (category gamedev)
          (elo 1270)
          (win_rate 59.4)
          (rank 25)
        )
        ({}
          (arena models)
          (category svg)
          (elo 1227)
          (win_rate 58.7)
          (rank 18)
        )
        ({}
          (arena models)
          (category uicomponent)
          (elo 1272)
          (win_rate 58.5)
          (rank 26)
        )
        ({}
          (arena models)
          (category website)
          (elo 1270)
          (win_rate 59.8)
          (rank 27)
        )
        ({}
          (arena agents)
          (category androidnative)
          (elo 1206)
          (win_rate 65.5)
          (rank 13)
        )
        ({}
          (arena agents)
          (category fullstack)
          (elo 1198)
          (win_rate 59.9)
          (rank 16)
        )
        ({}
          (arena agents)
          (category mobileapps)
          (elo 1249)
          (win_rate 60.5)
          (rank 5)
        )
        ({}
          (arena agents)
          (category webapps)
          (elo 1207)
          (win_rate 54.7)
          (rank 18)
        )
      ))
    ))
    (reasoning ({}
      (mandatory false)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id anthropic/claude-opus-4.5:batch)
    (canonical_slug anthropic/claude-4.5-opus-20251124)
    (hugging_face_id "")
    (name "Anthropic: Claude Opus 4.5 (batch)")
    (created 1764010580)
    (description "Claude Opus 4.5 is Anthropic’s frontier reasoning model optimized for complex software engineering, agentic workflows, and long-horizon computer use. It offers strong multimodal capabilities, competitive performance across real-world coding and...")
    (context_length 200000)
    (architecture ({}
      (modality text+image+file->text)
      (input_modalities (
        file
        image
        text
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
      (context_length 200000)
      (max_completion_tokens 64000)
      (is_moderated true)
    ))
    (per_request_limits null)
    (supported_parameters (
      include_reasoning
      max_tokens
      reasoning
      response_format
      stop
      structured_outputs
      temperature
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
      (details /api/v1/models/anthropic/claude-4.5-opus-20251124/endpoints)
    ))
    (benchmarks ({}
      (design_arena (
        ({}
          (arena models)
          (category 3d)
          (elo 1267)
          (win_rate 58.5)
          (rank 29)
        )
        ({}
          (arena models)
          (category asciiart)
          (elo 1227)
          (win_rate 54.7)
          (rank 17)
        )
        ({}
          (arena models)
          (category codecategories)
          (elo 1270)
          (win_rate 59.6)
          (rank 26)
        )
        ({}
          (arena models)
          (category dataviz)
          (elo 1270)
          (win_rate 58.5)
          (rank 20)
        )
        ({}
          (arena models)
          (category gamedev)
          (elo 1270)
          (win_rate 59.4)
          (rank 25)
        )
        ({}
          (arena models)
          (category svg)
          (elo 1227)
          (win_rate 58.7)
          (rank 18)
        )
        ({}
          (arena models)
          (category uicomponent)
          (elo 1272)
          (win_rate 58.5)
          (rank 26)
        )
        ({}
          (arena models)
          (category website)
          (elo 1270)
          (win_rate 59.8)
          (rank 27)
        )
        ({}
          (arena agents)
          (category androidnative)
          (elo 1206)
          (win_rate 65.5)
          (rank 13)
        )
        ({}
          (arena agents)
          (category fullstack)
          (elo 1198)
          (win_rate 59.9)
          (rank 16)
        )
        ({}
          (arena agents)
          (category mobileapps)
          (elo 1249)
          (win_rate 60.5)
          (rank 5)
        )
        ({}
          (arena agents)
          (category webapps)
          (elo 1207)
          (win_rate 54.7)
          (rank 18)
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
    (remoteModelId anthropic/claude-opus-4.5:batch)
  ))
)
