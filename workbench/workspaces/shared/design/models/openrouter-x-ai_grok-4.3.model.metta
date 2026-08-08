({}
  (kind model)
  (id openrouter-x-ai_grok-4.3)
  (label "SpaceXAI: Grok 4.3")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model x-ai/grok-4.3)
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
    (id x-ai/grok-4.3)
    (canonical_slug x-ai/grok-4.3-20260430)
    (hugging_face_id null)
    (name "SpaceXAI: Grok 4.3")
    (created 1777591821)
    (description "Grok 4.3 is a reasoning model from SpaceXAI. It accepts text and image inputs with text output, and is suited for agentic workflows, instruction-following tasks, and applications requiring high factual...")
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
      (context_length 1000000)
      (max_completion_tokens null)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
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
      (details /api/v1/models/x-ai/grok-4.3-20260430/endpoints)
    ))
    (benchmarks ({}
      (design_arena (
        ({}
          (arena agents)
          (category agenticgamedev)
          (elo 1012)
          (win_rate 28)
          (rank 19)
        )
        ({}
          (arena agents)
          (category agentichtmlslides)
          (elo 1066)
          (win_rate 31.8)
          (rank 10)
        )
        ({}
          (arena agents)
          (category agenticslides)
          (elo 1072)
          (win_rate 31.9)
          (rank 10)
        )
        ({}
          (arena agents)
          (category "agenticslides(html)")
          (elo 1066)
          (win_rate 31.7)
          (rank 10)
        )
        ({}
          (arena agents)
          (category "agenticslides(python-pptx)")
          (elo 1068)
          (win_rate 32.4)
          (rank 10)
        )
        ({}
          (arena agents)
          (category androidnative)
          (elo 987)
          (win_rate 22)
          (rank 31)
        )
        ({}
          (arena agents)
          (category fullstack)
          (elo 1047)
          (win_rate 30.2)
          (rank 31)
        )
        ({}
          (arena agents)
          (category godotgamedev)
          (elo 1035)
          (win_rate 31.2)
          (rank 29)
        )
        ({}
          (arena agents)
          (category htmlslides)
          (elo 1046)
          (win_rate 29.2)
          (rank 20)
        )
        ({}
          (arena agents)
          (category mobileapps)
          (elo 1113)
          (win_rate 37.3)
          (rank 31)
        )
        ({}
          (arena agents)
          (category pptxslides)
          (elo 1071)
          (win_rate 32.5)
          (rank 9)
        )
        ({}
          (arena agents)
          (category python-pptxslides)
          (elo 1072)
          (win_rate 30.8)
          (rank 18)
        )
        ({}
          (arena agents)
          (category webapps)
          (elo 1178)
          (win_rate 45.4)
          (rank 21)
        )
        ({}
          (arena models)
          (category 3d)
          (elo 1178)
          (win_rate 43.4)
          (rank 55)
        )
        ({}
          (arena models)
          (category asciiart)
          (elo 1179)
          (win_rate 46.3)
          (rank 34)
        )
        ({}
          (arena models)
          (category codecategories)
          (elo 1214)
          (win_rate 47)
          (rank 43)
        )
        ({}
          (arena models)
          (category dataviz)
          (elo 1212)
          (win_rate 46.8)
          (rank 43)
        )
        ({}
          (arena models)
          (category gamedev)
          (elo 1217)
          (win_rate 48.8)
          (rank 42)
        )
        ({}
          (arena models)
          (category svg)
          (elo 1129)
          (win_rate 40.9)
          (rank 49)
        )
        ({}
          (arena models)
          (category uicomponent)
          (elo 1225)
          (win_rate 47.3)
          (rank 39)
        )
        ({}
          (arena models)
          (category website)
          (elo 1214)
          (win_rate 46.7)
          (rank 46)
        )
      ))
      (artificial_analysis ({}
        (intelligence_index 37.9)
        (coding_index 42.2)
        (agentic_index 24.2)
      ))
    ))
    (reasoning ({}
      (mandatory false)
      (default_enabled true)
      (supported_efforts (
        high
        medium
        low
        none
      ))
      (default_effort low)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id x-ai/grok-4.3)
    (canonical_slug x-ai/grok-4.3-20260430)
    (hugging_face_id null)
    (name "SpaceXAI: Grok 4.3")
    (created 1777591821)
    (description "Grok 4.3 is a reasoning model from SpaceXAI. It accepts text and image inputs with text output, and is suited for agentic workflows, instruction-following tasks, and applications requiring high factual...")
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
      (context_length 1000000)
      (max_completion_tokens null)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
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
      (details /api/v1/models/x-ai/grok-4.3-20260430/endpoints)
    ))
    (benchmarks ({}
      (design_arena (
        ({}
          (arena agents)
          (category agenticgamedev)
          (elo 1012)
          (win_rate 28)
          (rank 19)
        )
        ({}
          (arena agents)
          (category agentichtmlslides)
          (elo 1066)
          (win_rate 31.8)
          (rank 10)
        )
        ({}
          (arena agents)
          (category agenticslides)
          (elo 1072)
          (win_rate 31.9)
          (rank 10)
        )
        ({}
          (arena agents)
          (category "agenticslides(html)")
          (elo 1066)
          (win_rate 31.7)
          (rank 10)
        )
        ({}
          (arena agents)
          (category "agenticslides(python-pptx)")
          (elo 1068)
          (win_rate 32.4)
          (rank 10)
        )
        ({}
          (arena agents)
          (category androidnative)
          (elo 987)
          (win_rate 22)
          (rank 31)
        )
        ({}
          (arena agents)
          (category fullstack)
          (elo 1047)
          (win_rate 30.2)
          (rank 31)
        )
        ({}
          (arena agents)
          (category godotgamedev)
          (elo 1035)
          (win_rate 31.2)
          (rank 29)
        )
        ({}
          (arena agents)
          (category htmlslides)
          (elo 1046)
          (win_rate 29.2)
          (rank 20)
        )
        ({}
          (arena agents)
          (category mobileapps)
          (elo 1113)
          (win_rate 37.3)
          (rank 31)
        )
        ({}
          (arena agents)
          (category pptxslides)
          (elo 1071)
          (win_rate 32.5)
          (rank 9)
        )
        ({}
          (arena agents)
          (category python-pptxslides)
          (elo 1072)
          (win_rate 30.8)
          (rank 18)
        )
        ({}
          (arena agents)
          (category webapps)
          (elo 1178)
          (win_rate 45.4)
          (rank 21)
        )
        ({}
          (arena models)
          (category 3d)
          (elo 1178)
          (win_rate 43.4)
          (rank 55)
        )
        ({}
          (arena models)
          (category asciiart)
          (elo 1179)
          (win_rate 46.3)
          (rank 34)
        )
        ({}
          (arena models)
          (category codecategories)
          (elo 1214)
          (win_rate 47)
          (rank 43)
        )
        ({}
          (arena models)
          (category dataviz)
          (elo 1212)
          (win_rate 46.8)
          (rank 43)
        )
        ({}
          (arena models)
          (category gamedev)
          (elo 1217)
          (win_rate 48.8)
          (rank 42)
        )
        ({}
          (arena models)
          (category svg)
          (elo 1129)
          (win_rate 40.9)
          (rank 49)
        )
        ({}
          (arena models)
          (category uicomponent)
          (elo 1225)
          (win_rate 47.3)
          (rank 39)
        )
        ({}
          (arena models)
          (category website)
          (elo 1214)
          (win_rate 46.7)
          (rank 46)
        )
      ))
      (artificial_analysis ({}
        (intelligence_index 37.9)
        (coding_index 42.2)
        (agentic_index 24.2)
      ))
    ))
    (reasoning ({}
      (mandatory false)
      (default_enabled true)
      (supported_efforts (
        high
        medium
        low
        none
      ))
      (default_effort low)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId x-ai/grok-4.3)
  ))
)
