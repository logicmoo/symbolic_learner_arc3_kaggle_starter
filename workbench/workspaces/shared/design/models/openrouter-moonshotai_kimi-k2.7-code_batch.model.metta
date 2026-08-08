(
  (kind model)
  (id openrouter-moonshotai_kimi-k2.7-code_batch)
  (label "MoonshotAI: Kimi K2.7 Code (batch)")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model moonshotai/kimi-k2.7-code:batch)
  (enabled true)
  (capabilities (
    (audio false)
    (code true)
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
    (contextWindow 262144)
    (maxOutputTokens null)
  ))
  (pricing (
    (prompt "0.000000475")
    (completion "0.000002")
    (input_cache_read "0.000000095")
  ))
  (properties (
    (id moonshotai/kimi-k2.7-code:batch)
    (canonical_slug moonshotai/kimi-k2.7-code-20260612)
    (hugging_face_id moonshotai/Kimi-K2.7-Code)
    (name "MoonshotAI: Kimi K2.7 Code (batch)")
    (created 1781266361)
    (description "MoonshotAI: Kimi K2.7 Code is a coding-focused model in Moonshot AI's Kimi K2 family, built to complete end-to-end programming tasks reliably over long contexts. It uses a native multimodal mixture-of-experts...")
    (context_length 262144)
    (architecture (
      (modality text+image->text)
      (input_modalities ([]
        text
        image
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Other)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.000000475")
      (completion "0.000002")
      (input_cache_read "0.000000095")
    ))
    (top_provider (
      (context_length 262144)
      (max_completion_tokens null)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      frequency_penalty
      include_reasoning
      logit_bias
      max_tokens
      min_p
      presence_penalty
      reasoning
      repetition_penalty
      response_format
      stop
      structured_outputs
      temperature
      tool_choice
      tools
      top_k
      top_p
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
      (details /api/v1/models/moonshotai/kimi-k2.7-code-20260612/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena agents)
          (category agenticgamedev)
          (elo 1139)
          (win_rate 42.9)
          (rank 16)
        )
        (
          (arena agents)
          (category androidnative)
          (elo 1171)
          (win_rate 47.8)
          (rank 20)
        )
        (
          (arena agents)
          (category fullstack)
          (elo 1218)
          (win_rate 54.4)
          (rank 12)
        )
        (
          (arena agents)
          (category godotgamedev)
          (elo 1184)
          (win_rate 49.3)
          (rank 12)
        )
        (
          (arena agents)
          (category htmlslides)
          (elo 1227)
          (win_rate 53.9)
          (rank 6)
        )
        (
          (arena agents)
          (category mobileapps)
          (elo 1200)
          (win_rate 50.2)
          (rank 16)
        )
        (
          (arena agents)
          (category python-pptxslides)
          (elo 1154)
          (win_rate 42.9)
          (rank 15)
        )
        (
          (arena agents)
          (category webapps)
          (elo 1228)
          (win_rate 49.2)
          (rank 16)
        )
        (
          (arena models)
          (category 3d)
          (elo 1297)
          (win_rate 52.3)
          (rank 19)
        )
        (
          (arena models)
          (category asciiart)
          (elo 1251)
          (win_rate 52.6)
          (rank 11)
        )
        (
          (arena models)
          (category codecategories)
          (elo 1287)
          (win_rate 52.9)
          (rank 20)
        )
        (
          (arena models)
          (category dataviz)
          (elo 1250)
          (win_rate 50.8)
          (rank 32)
        )
        (
          (arena models)
          (category gamedev)
          (elo 1257)
          (win_rate 50.7)
          (rank 29)
        )
        (
          (arena models)
          (category svg)
          (elo 1221)
          (win_rate 48.9)
          (rank 22)
        )
        (
          (arena models)
          (category uicomponent)
          (elo 1294)
          (win_rate 53.6)
          (rank 18)
        )
        (
          (arena models)
          (category website)
          (elo 1297)
          (win_rate 54.7)
          (rank 14)
        )
      ))
      (artificial_analysis (
        (intelligence_index 43)
        (coding_index 60.8)
        (agentic_index 30.3)
      ))
    ))
    (reasoning (
      (mandatory true)
      (default_enabled true)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id moonshotai/kimi-k2.7-code:batch)
    (canonical_slug moonshotai/kimi-k2.7-code-20260612)
    (hugging_face_id moonshotai/Kimi-K2.7-Code)
    (name "MoonshotAI: Kimi K2.7 Code (batch)")
    (created 1781266361)
    (description "MoonshotAI: Kimi K2.7 Code is a coding-focused model in Moonshot AI's Kimi K2 family, built to complete end-to-end programming tasks reliably over long contexts. It uses a native multimodal mixture-of-experts...")
    (context_length 262144)
    (architecture (
      (modality text+image->text)
      (input_modalities ([]
        text
        image
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Other)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.000000475")
      (completion "0.000002")
      (input_cache_read "0.000000095")
    ))
    (top_provider (
      (context_length 262144)
      (max_completion_tokens null)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      frequency_penalty
      include_reasoning
      logit_bias
      max_tokens
      min_p
      presence_penalty
      reasoning
      repetition_penalty
      response_format
      stop
      structured_outputs
      temperature
      tool_choice
      tools
      top_k
      top_p
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
      (details /api/v1/models/moonshotai/kimi-k2.7-code-20260612/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena agents)
          (category agenticgamedev)
          (elo 1139)
          (win_rate 42.9)
          (rank 16)
        )
        (
          (arena agents)
          (category androidnative)
          (elo 1171)
          (win_rate 47.8)
          (rank 20)
        )
        (
          (arena agents)
          (category fullstack)
          (elo 1218)
          (win_rate 54.4)
          (rank 12)
        )
        (
          (arena agents)
          (category godotgamedev)
          (elo 1184)
          (win_rate 49.3)
          (rank 12)
        )
        (
          (arena agents)
          (category htmlslides)
          (elo 1227)
          (win_rate 53.9)
          (rank 6)
        )
        (
          (arena agents)
          (category mobileapps)
          (elo 1200)
          (win_rate 50.2)
          (rank 16)
        )
        (
          (arena agents)
          (category python-pptxslides)
          (elo 1154)
          (win_rate 42.9)
          (rank 15)
        )
        (
          (arena agents)
          (category webapps)
          (elo 1228)
          (win_rate 49.2)
          (rank 16)
        )
        (
          (arena models)
          (category 3d)
          (elo 1297)
          (win_rate 52.3)
          (rank 19)
        )
        (
          (arena models)
          (category asciiart)
          (elo 1251)
          (win_rate 52.6)
          (rank 11)
        )
        (
          (arena models)
          (category codecategories)
          (elo 1287)
          (win_rate 52.9)
          (rank 20)
        )
        (
          (arena models)
          (category dataviz)
          (elo 1250)
          (win_rate 50.8)
          (rank 32)
        )
        (
          (arena models)
          (category gamedev)
          (elo 1257)
          (win_rate 50.7)
          (rank 29)
        )
        (
          (arena models)
          (category svg)
          (elo 1221)
          (win_rate 48.9)
          (rank 22)
        )
        (
          (arena models)
          (category uicomponent)
          (elo 1294)
          (win_rate 53.6)
          (rank 18)
        )
        (
          (arena models)
          (category website)
          (elo 1297)
          (win_rate 54.7)
          (rank 14)
        )
      ))
      (artificial_analysis (
        (intelligence_index 43)
        (coding_index 60.8)
        (agentic_index 30.3)
      ))
    ))
    (reasoning (
      (mandatory true)
      (default_enabled true)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId moonshotai/kimi-k2.7-code:batch)
  ))
)
