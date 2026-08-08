(
  (kind model)
  (id openrouter-openai_gpt-5.5_batch)
  (label "OpenAI: GPT-5.5 (batch)")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model openai/gpt-5.5:batch)
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
    (contextWindow 1050000)
    (maxOutputTokens 128000)
  ))
  (pricing (
    (prompt "0.0000025")
    (completion "0.000015")
    (web_search "0.01")
    (input_cache_read "0.00000025")
    (overrides ([]
      (
        (min_prompt_tokens 272000)
        (prompt "0.000005")
        (completion "0.0000225")
        (input_cache_read "0.0000005")
      )
    ))
  ))
  (properties (
    (id openai/gpt-5.5:batch)
    (canonical_slug openai/gpt-5.5-20260423)
    (hugging_face_id "")
    (name "OpenAI: GPT-5.5 (batch)")
    (created 1777051893)
    (description "GPT-5.5 is OpenAI’s frontier model designed for complex professional workloads, building on GPT-5.4 with stronger reasoning, higher reliability, and improved token efficiency on hard tasks. It features a 1M+ token...")
    (context_length 1050000)
    (architecture (
      (modality text+image+file->text)
      (input_modalities ([]
        file
        image
        text
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer GPT)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.0000025")
      (completion "0.000015")
      (web_search "0.01")
      (input_cache_read "0.00000025")
      (overrides ([]
        (
          (min_prompt_tokens 272000)
          (prompt "0.000005")
          (completion "0.0000225")
          (input_cache_read "0.0000005")
        )
      ))
    ))
    (top_provider (
      (context_length 1050000)
      (max_completion_tokens 128000)
      (is_moderated true)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      include_reasoning
      max_tokens
      reasoning
      reasoning_effort
      response_format
      seed
      structured_outputs
      tool_choice
      tools
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
    (knowledge_cutoff 2025-12-01)
    (expiration_date null)
    (links (
      (details /api/v1/models/openai/gpt-5.5-20260423/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena agents)
          (category agenticgamedev)
          (elo 1187)
          (win_rate 51.6)
          (rank 12)
        )
        (
          (arena agents)
          (category agentichtmlslides)
          (elo 1084)
          (win_rate 34.2)
          (rank 9)
        )
        (
          (arena agents)
          (category agenticslides)
          (elo 1150)
          (win_rate 43.5)
          (rank 7)
        )
        (
          (arena agents)
          (category "agenticslides(html)")
          (elo 1077)
          (win_rate 33.2)
          (rank 9)
        )
        (
          (arena agents)
          (category "agenticslides(python-pptx)")
          (elo 1155)
          (win_rate 45.2)
          (rank 7)
        )
        (
          (arena agents)
          (category androidnative)
          (elo 1197)
          (win_rate 50.8)
          (rank 14)
        )
        (
          (arena agents)
          (category fullstack)
          (elo 1129)
          (win_rate 43.2)
          (rank 20)
        )
        (
          (arena agents)
          (category godotgamedev)
          (elo 1211)
          (win_rate 52.4)
          (rank 10)
        )
        (
          (arena agents)
          (category htmlslides)
          (elo 1090)
          (win_rate 34.8)
          (rank 19)
        )
        (
          (arena agents)
          (category mobileapps)
          (elo 1208)
          (win_rate 51.7)
          (rank 13)
        )
        (
          (arena agents)
          (category pptxslides)
          (elo 1157)
          (win_rate 45.3)
          (rank 7)
        )
        (
          (arena agents)
          (category python-pptxslides)
          (elo 1152)
          (win_rate 43.3)
          (rank 16)
        )
        (
          (arena agents)
          (category webapps)
          (elo 1166)
          (win_rate 42.8)
          (rank 24)
        )
        (
          (arena models)
          (category 3d)
          (elo 1250)
          (win_rate 52.1)
          (rank 33)
        )
        (
          (arena models)
          (category asciiart)
          (elo 1289)
          (win_rate 60.8)
          (rank 9)
        )
        (
          (arena models)
          (category codecategories)
          (elo 1286)
          (win_rate 55.7)
          (rank 21)
        )
        (
          (arena models)
          (category dataviz)
          (elo 1282)
          (win_rate 56.4)
          (rank 17)
        )
        (
          (arena models)
          (category gamedev)
          (elo 1336)
          (win_rate 60.8)
          (rank 5)
        )
        (
          (arena models)
          (category svg)
          (elo 1278)
          (win_rate 58)
          (rank 4)
        )
        (
          (arena models)
          (category uicomponent)
          (elo 1291)
          (win_rate 56.4)
          (rank 19)
        )
        (
          (arena models)
          (category website)
          (elo 1280)
          (win_rate 55.1)
          (rank 23)
        )
      ))
      (artificial_analysis (
        (intelligence_index 56.3)
        (coding_index 74.9)
        (agentic_index 47.4)
      ))
    ))
    (reasoning (
      (mandatory false)
      (default_enabled true)
      (supported_efforts ([]
        xhigh
        high
        medium
        low
        none
      ))
      (default_effort medium)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id openai/gpt-5.5:batch)
    (canonical_slug openai/gpt-5.5-20260423)
    (hugging_face_id "")
    (name "OpenAI: GPT-5.5 (batch)")
    (created 1777051893)
    (description "GPT-5.5 is OpenAI’s frontier model designed for complex professional workloads, building on GPT-5.4 with stronger reasoning, higher reliability, and improved token efficiency on hard tasks. It features a 1M+ token...")
    (context_length 1050000)
    (architecture (
      (modality text+image+file->text)
      (input_modalities ([]
        file
        image
        text
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer GPT)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.0000025")
      (completion "0.000015")
      (web_search "0.01")
      (input_cache_read "0.00000025")
      (overrides ([]
        (
          (min_prompt_tokens 272000)
          (prompt "0.000005")
          (completion "0.0000225")
          (input_cache_read "0.0000005")
        )
      ))
    ))
    (top_provider (
      (context_length 1050000)
      (max_completion_tokens 128000)
      (is_moderated true)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      include_reasoning
      max_tokens
      reasoning
      reasoning_effort
      response_format
      seed
      structured_outputs
      tool_choice
      tools
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
    (knowledge_cutoff 2025-12-01)
    (expiration_date null)
    (links (
      (details /api/v1/models/openai/gpt-5.5-20260423/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena agents)
          (category agenticgamedev)
          (elo 1187)
          (win_rate 51.6)
          (rank 12)
        )
        (
          (arena agents)
          (category agentichtmlslides)
          (elo 1084)
          (win_rate 34.2)
          (rank 9)
        )
        (
          (arena agents)
          (category agenticslides)
          (elo 1150)
          (win_rate 43.5)
          (rank 7)
        )
        (
          (arena agents)
          (category "agenticslides(html)")
          (elo 1077)
          (win_rate 33.2)
          (rank 9)
        )
        (
          (arena agents)
          (category "agenticslides(python-pptx)")
          (elo 1155)
          (win_rate 45.2)
          (rank 7)
        )
        (
          (arena agents)
          (category androidnative)
          (elo 1197)
          (win_rate 50.8)
          (rank 14)
        )
        (
          (arena agents)
          (category fullstack)
          (elo 1129)
          (win_rate 43.2)
          (rank 20)
        )
        (
          (arena agents)
          (category godotgamedev)
          (elo 1211)
          (win_rate 52.4)
          (rank 10)
        )
        (
          (arena agents)
          (category htmlslides)
          (elo 1090)
          (win_rate 34.8)
          (rank 19)
        )
        (
          (arena agents)
          (category mobileapps)
          (elo 1208)
          (win_rate 51.7)
          (rank 13)
        )
        (
          (arena agents)
          (category pptxslides)
          (elo 1157)
          (win_rate 45.3)
          (rank 7)
        )
        (
          (arena agents)
          (category python-pptxslides)
          (elo 1152)
          (win_rate 43.3)
          (rank 16)
        )
        (
          (arena agents)
          (category webapps)
          (elo 1166)
          (win_rate 42.8)
          (rank 24)
        )
        (
          (arena models)
          (category 3d)
          (elo 1250)
          (win_rate 52.1)
          (rank 33)
        )
        (
          (arena models)
          (category asciiart)
          (elo 1289)
          (win_rate 60.8)
          (rank 9)
        )
        (
          (arena models)
          (category codecategories)
          (elo 1286)
          (win_rate 55.7)
          (rank 21)
        )
        (
          (arena models)
          (category dataviz)
          (elo 1282)
          (win_rate 56.4)
          (rank 17)
        )
        (
          (arena models)
          (category gamedev)
          (elo 1336)
          (win_rate 60.8)
          (rank 5)
        )
        (
          (arena models)
          (category svg)
          (elo 1278)
          (win_rate 58)
          (rank 4)
        )
        (
          (arena models)
          (category uicomponent)
          (elo 1291)
          (win_rate 56.4)
          (rank 19)
        )
        (
          (arena models)
          (category website)
          (elo 1280)
          (win_rate 55.1)
          (rank 23)
        )
      ))
      (artificial_analysis (
        (intelligence_index 56.3)
        (coding_index 74.9)
        (agentic_index 47.4)
      ))
    ))
    (reasoning (
      (mandatory false)
      (default_enabled true)
      (supported_efforts ([]
        xhigh
        high
        medium
        low
        none
      ))
      (default_effort medium)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId openai/gpt-5.5:batch)
  ))
)
