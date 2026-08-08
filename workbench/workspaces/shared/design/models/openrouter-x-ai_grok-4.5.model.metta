(
  (kind model)
  (id openrouter-x-ai_grok-4.5)
  (label "SpaceXAI: Grok 4.5")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model x-ai/grok-4.5)
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
    (contextWindow 500000)
    (maxOutputTokens null)
  ))
  (pricing (
    (prompt "0.000002")
    (completion "0.000006")
    (web_search "0.005")
    (input_cache_read "0.0000003")
    (overrides ([]
      (
        (min_prompt_tokens 200000)
        (prompt "0.000004")
        (completion "0.000012")
        (input_cache_read "0.0000006")
      )
    ))
  ))
  (properties (
    (id x-ai/grok-4.5)
    (canonical_slug x-ai/grok-4.5-20260708)
    (hugging_face_id null)
    (name "SpaceXAI: Grok 4.5")
    (created 1783523154)
    (description "Grok 4.5 is SpaceXAI's smartest model with frontier performance on coding, knowledge work, and STEM.")
    (context_length 500000)
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
      (tokenizer Grok)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.000002")
      (completion "0.000006")
      (web_search "0.005")
      (input_cache_read "0.0000003")
      (overrides ([]
        (
          (min_prompt_tokens 200000)
          (prompt "0.000004")
          (completion "0.000012")
          (input_cache_read "0.0000006")
        )
      ))
    ))
    (top_provider (
      (context_length 500000)
      (max_completion_tokens null)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      frequency_penalty
      include_reasoning
      logprobs
      max_tokens
      presence_penalty
      reasoning
      reasoning_effort
      response_format
      seed
      stop
      structured_outputs
      temperature
      tool_choice
      tools
      top_logprobs
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
      (details /api/v1/models/x-ai/grok-4.5-20260708/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena agents)
          (category agenticgamedev)
          (elo 1226)
          (win_rate 56.7)
          (rank 5)
        )
        (
          (arena agents)
          (category androidnative)
          (elo 1277)
          (win_rate 69)
          (rank 2)
        )
        (
          (arena agents)
          (category fullstack)
          (elo 1290)
          (win_rate 66.8)
          (rank 3)
        )
        (
          (arena agents)
          (category godotgamedev)
          (elo 1270)
          (win_rate 62.1)
          (rank 3)
        )
        (
          (arena agents)
          (category htmlslides)
          (elo 1230)
          (win_rate 55.8)
          (rank 5)
        )
        (
          (arena agents)
          (category mobileapps)
          (elo 1267)
          (win_rate 60.8)
          (rank 3)
        )
        (
          (arena agents)
          (category python-pptxslides)
          (elo 1232)
          (win_rate 54.5)
          (rank 8)
        )
        (
          (arena agents)
          (category webapps)
          (elo 1261)
          (win_rate 54.5)
          (rank 9)
        )
        (
          (arena models)
          (category 3d)
          (elo 1311)
          (win_rate 50.1)
          (rank 12)
        )
        (
          (arena models)
          (category asciiart)
          (elo 1297)
          (win_rate 57.9)
          (rank 6)
        )
        (
          (arena models)
          (category codecategories)
          (elo 1312)
          (win_rate 53.4)
          (rank 8)
        )
        (
          (arena models)
          (category dataviz)
          (elo 1313)
          (win_rate 54.7)
          (rank 9)
        )
        (
          (arena models)
          (category gamedev)
          (elo 1322)
          (win_rate 53.6)
          (rank 9)
        )
        (
          (arena models)
          (category svg)
          (elo 1273)
          (win_rate 52.7)
          (rank 6)
        )
        (
          (arena models)
          (category uicomponent)
          (elo 1322)
          (win_rate 53.7)
          (rank 8)
        )
        (
          (arena models)
          (category website)
          (elo 1318)
          (win_rate 56.7)
          (rank 7)
        )
      ))
      (artificial_analysis (
        (intelligence_index 55.8)
        (coding_index 72.4)
        (agentic_index 48.9)
      ))
    ))
    (reasoning (
      (mandatory true)
      (default_enabled true)
      (supported_efforts ([]
        high
        medium
        low
      ))
      (default_effort high)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id x-ai/grok-4.5)
    (canonical_slug x-ai/grok-4.5-20260708)
    (hugging_face_id null)
    (name "SpaceXAI: Grok 4.5")
    (created 1783523154)
    (description "Grok 4.5 is SpaceXAI's smartest model with frontier performance on coding, knowledge work, and STEM.")
    (context_length 500000)
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
      (tokenizer Grok)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.000002")
      (completion "0.000006")
      (web_search "0.005")
      (input_cache_read "0.0000003")
      (overrides ([]
        (
          (min_prompt_tokens 200000)
          (prompt "0.000004")
          (completion "0.000012")
          (input_cache_read "0.0000006")
        )
      ))
    ))
    (top_provider (
      (context_length 500000)
      (max_completion_tokens null)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      frequency_penalty
      include_reasoning
      logprobs
      max_tokens
      presence_penalty
      reasoning
      reasoning_effort
      response_format
      seed
      stop
      structured_outputs
      temperature
      tool_choice
      tools
      top_logprobs
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
      (details /api/v1/models/x-ai/grok-4.5-20260708/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena agents)
          (category agenticgamedev)
          (elo 1226)
          (win_rate 56.7)
          (rank 5)
        )
        (
          (arena agents)
          (category androidnative)
          (elo 1277)
          (win_rate 69)
          (rank 2)
        )
        (
          (arena agents)
          (category fullstack)
          (elo 1290)
          (win_rate 66.8)
          (rank 3)
        )
        (
          (arena agents)
          (category godotgamedev)
          (elo 1270)
          (win_rate 62.1)
          (rank 3)
        )
        (
          (arena agents)
          (category htmlslides)
          (elo 1230)
          (win_rate 55.8)
          (rank 5)
        )
        (
          (arena agents)
          (category mobileapps)
          (elo 1267)
          (win_rate 60.8)
          (rank 3)
        )
        (
          (arena agents)
          (category python-pptxslides)
          (elo 1232)
          (win_rate 54.5)
          (rank 8)
        )
        (
          (arena agents)
          (category webapps)
          (elo 1261)
          (win_rate 54.5)
          (rank 9)
        )
        (
          (arena models)
          (category 3d)
          (elo 1311)
          (win_rate 50.1)
          (rank 12)
        )
        (
          (arena models)
          (category asciiart)
          (elo 1297)
          (win_rate 57.9)
          (rank 6)
        )
        (
          (arena models)
          (category codecategories)
          (elo 1312)
          (win_rate 53.4)
          (rank 8)
        )
        (
          (arena models)
          (category dataviz)
          (elo 1313)
          (win_rate 54.7)
          (rank 9)
        )
        (
          (arena models)
          (category gamedev)
          (elo 1322)
          (win_rate 53.6)
          (rank 9)
        )
        (
          (arena models)
          (category svg)
          (elo 1273)
          (win_rate 52.7)
          (rank 6)
        )
        (
          (arena models)
          (category uicomponent)
          (elo 1322)
          (win_rate 53.7)
          (rank 8)
        )
        (
          (arena models)
          (category website)
          (elo 1318)
          (win_rate 56.7)
          (rank 7)
        )
      ))
      (artificial_analysis (
        (intelligence_index 55.8)
        (coding_index 72.4)
        (agentic_index 48.9)
      ))
    ))
    (reasoning (
      (mandatory true)
      (default_enabled true)
      (supported_efforts ([]
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
    (remoteModelId x-ai/grok-4.5)
  ))
)
