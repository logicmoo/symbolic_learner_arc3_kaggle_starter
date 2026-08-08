({}
  (kind model)
  (id openrouter-x-ai_grok-4.20)
  (label "SpaceXAI: Grok 4.20")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model x-ai/grok-4.20)
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
    (contextWindow 2000000)
    (maxOutputTokens null)
  ))
  (pricing ({}
    (prompt "0.00000125")
    (completion "0.0000025")
    (web_search "0.005")
    (input_cache_read "0.0000002")
    (overrides (
      ({}
        (min_prompt_tokens 200000)
        (prompt "0.0000025")
        (completion "0.000005")
        (input_cache_read "0.0000004")
      )
    ))
  ))
  (properties ({}
    (id x-ai/grok-4.20)
    (canonical_slug x-ai/grok-4.20-20260309)
    (hugging_face_id "")
    (name "SpaceXAI: Grok 4.20")
    (created 1774979019)
    (description "Grok 4.20 is a reasoning model from SpaceXAI with industry-leading speed and agentic tool calling capabilities. It combines the lowest hallucination rate on the market with strict prompt adherance, delivering...")
    (context_length 2000000)
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
      (tokenizer Grok)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.00000125")
      (completion "0.0000025")
      (web_search "0.005")
      (input_cache_read "0.0000002")
      (overrides (
        ({}
          (min_prompt_tokens 200000)
          (prompt "0.0000025")
          (completion "0.000005")
          (input_cache_read "0.0000004")
        )
      ))
    ))
    (top_provider ({}
      (context_length 2000000)
      (max_completion_tokens null)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      include_reasoning
      logprobs
      max_tokens
      reasoning
      response_format
      seed
      structured_outputs
      temperature
      tool_choice
      tools
      top_logprobs
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
    (knowledge_cutoff 2025-09-01)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/x-ai/grok-4.20-20260309/endpoints)
    ))
    (benchmarks ({}
      (design_arena (
        ({}
          (arena agents)
          (category androidnative)
          (elo 1079)
          (win_rate 35.1)
          (rank 29)
        )
        ({}
          (arena agents)
          (category fullstack)
          (elo 1094)
          (win_rate 41.1)
          (rank 24)
        )
        ({}
          (arena agents)
          (category godotgamedev)
          (elo 1089)
          (win_rate 38.5)
          (rank 26)
        )
        ({}
          (arena agents)
          (category htmlslides)
          (elo 1183)
          (win_rate 45.7)
          (rank 15)
        )
        ({}
          (arena agents)
          (category mobileapps)
          (elo 1148)
          (win_rate 45.4)
          (rank 27)
        )
        ({}
          (arena agents)
          (category webapps)
          (elo 1192)
          (win_rate 49.6)
          (rank 19)
        )
        ({}
          (arena models)
          (category 3d)
          (elo 1245)
          (win_rate 52.9)
          (rank 36)
        )
        ({}
          (arena models)
          (category asciiart)
          (elo 1213)
          (win_rate 48.5)
          (rank 18)
        )
        ({}
          (arena models)
          (category codecategories)
          (elo 1248)
          (win_rate 53.4)
          (rank 34)
        )
        ({}
          (arena models)
          (category dataviz)
          (elo 1242)
          (win_rate 52.8)
          (rank 34)
        )
        ({}
          (arena models)
          (category gamedev)
          (elo 1237)
          (win_rate 53.1)
          (rank 36)
        )
        ({}
          (arena models)
          (category svg)
          (elo 1210)
          (win_rate 53.5)
          (rank 26)
        )
        ({}
          (arena models)
          (category uicomponent)
          (elo 1236)
          (win_rate 51.1)
          (rank 37)
        )
        ({}
          (arena models)
          (category website)
          (elo 1251)
          (win_rate 53.5)
          (rank 34)
        )
      ))
    ))
    (reasoning ({}
      (mandatory false)
      (default_enabled false)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id x-ai/grok-4.20)
    (canonical_slug x-ai/grok-4.20-20260309)
    (hugging_face_id "")
    (name "SpaceXAI: Grok 4.20")
    (created 1774979019)
    (description "Grok 4.20 is a reasoning model from SpaceXAI with industry-leading speed and agentic tool calling capabilities. It combines the lowest hallucination rate on the market with strict prompt adherance, delivering...")
    (context_length 2000000)
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
      (tokenizer Grok)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.00000125")
      (completion "0.0000025")
      (web_search "0.005")
      (input_cache_read "0.0000002")
      (overrides (
        ({}
          (min_prompt_tokens 200000)
          (prompt "0.0000025")
          (completion "0.000005")
          (input_cache_read "0.0000004")
        )
      ))
    ))
    (top_provider ({}
      (context_length 2000000)
      (max_completion_tokens null)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      include_reasoning
      logprobs
      max_tokens
      reasoning
      response_format
      seed
      structured_outputs
      temperature
      tool_choice
      tools
      top_logprobs
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
    (knowledge_cutoff 2025-09-01)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/x-ai/grok-4.20-20260309/endpoints)
    ))
    (benchmarks ({}
      (design_arena (
        ({}
          (arena agents)
          (category androidnative)
          (elo 1079)
          (win_rate 35.1)
          (rank 29)
        )
        ({}
          (arena agents)
          (category fullstack)
          (elo 1094)
          (win_rate 41.1)
          (rank 24)
        )
        ({}
          (arena agents)
          (category godotgamedev)
          (elo 1089)
          (win_rate 38.5)
          (rank 26)
        )
        ({}
          (arena agents)
          (category htmlslides)
          (elo 1183)
          (win_rate 45.7)
          (rank 15)
        )
        ({}
          (arena agents)
          (category mobileapps)
          (elo 1148)
          (win_rate 45.4)
          (rank 27)
        )
        ({}
          (arena agents)
          (category webapps)
          (elo 1192)
          (win_rate 49.6)
          (rank 19)
        )
        ({}
          (arena models)
          (category 3d)
          (elo 1245)
          (win_rate 52.9)
          (rank 36)
        )
        ({}
          (arena models)
          (category asciiart)
          (elo 1213)
          (win_rate 48.5)
          (rank 18)
        )
        ({}
          (arena models)
          (category codecategories)
          (elo 1248)
          (win_rate 53.4)
          (rank 34)
        )
        ({}
          (arena models)
          (category dataviz)
          (elo 1242)
          (win_rate 52.8)
          (rank 34)
        )
        ({}
          (arena models)
          (category gamedev)
          (elo 1237)
          (win_rate 53.1)
          (rank 36)
        )
        ({}
          (arena models)
          (category svg)
          (elo 1210)
          (win_rate 53.5)
          (rank 26)
        )
        ({}
          (arena models)
          (category uicomponent)
          (elo 1236)
          (win_rate 51.1)
          (rank 37)
        )
        ({}
          (arena models)
          (category website)
          (elo 1251)
          (win_rate 53.5)
          (rank 34)
        )
      ))
    ))
    (reasoning ({}
      (mandatory false)
      (default_enabled false)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId x-ai/grok-4.20)
  ))
)
