({}
  (kind model)
  (id openrouter-openai_gpt-5_batch)
  (label "OpenAI: GPT-5 (batch)")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model openai/gpt-5:batch)
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
    (contextWindow 400000)
    (maxOutputTokens 128000)
  ))
  (pricing ({}
    (prompt "0.000000625")
    (completion "0.000005")
    (web_search "0.01")
    (input_cache_read "0.0000000625")
  ))
  (properties ({}
    (id openai/gpt-5:batch)
    (canonical_slug openai/gpt-5-2025-08-07)
    (hugging_face_id "")
    (name "OpenAI: GPT-5 (batch)")
    (created 1754587413)
    (description "GPT-5 is OpenAI’s most advanced model, offering major improvements in reasoning, code quality, and user experience. It is optimized for complex tasks that require step-by-step reasoning, instruction following, and accuracy...")
    (context_length 400000)
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
      (tokenizer GPT)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.000000625")
      (completion "0.000005")
      (web_search "0.01")
      (input_cache_read "0.0000000625")
    ))
    (top_provider ({}
      (context_length 400000)
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
      seed
      structured_outputs
      tool_choice
      tools
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
    (knowledge_cutoff 2024-09-30)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/openai/gpt-5-2025-08-07/endpoints)
    ))
    (benchmarks ({}
      (design_arena (
        ({}
          (arena models)
          (category 3d)
          (elo 1110)
          (win_rate 41.4)
          (rank 83)
        )
        ({}
          (arena models)
          (category asciiart)
          (elo 1178)
          (win_rate 49)
          (rank 35)
        )
        ({}
          (arena models)
          (category codecategories)
          (elo 1196)
          (win_rate 54.7)
          (rank 55)
        )
        ({}
          (arena models)
          (category dataviz)
          (elo 1263)
          (win_rate 62.9)
          (rank 25)
        )
        ({}
          (arena models)
          (category gamedev)
          (elo 1227)
          (win_rate 59.5)
          (rank 39)
        )
        ({}
          (arena models)
          (category svg)
          (elo 1235)
          (win_rate 64.1)
          (rank 17)
        )
        ({}
          (arena models)
          (category uicomponent)
          (elo 1215)
          (win_rate 58.2)
          (rank 42)
        )
        ({}
          (arena models)
          (category website)
          (elo 1207)
          (win_rate 53.8)
          (rank 54)
        )
      ))
      (artificial_analysis ({}
        (intelligence_index 35.3)
        (coding_index 37.8)
        (agentic_index 26.5)
      ))
    ))
    (reasoning ({}
      (mandatory true)
      (supported_efforts (
        high
        medium
        low
        minimal
      ))
      (default_effort medium)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id openai/gpt-5:batch)
    (canonical_slug openai/gpt-5-2025-08-07)
    (hugging_face_id "")
    (name "OpenAI: GPT-5 (batch)")
    (created 1754587413)
    (description "GPT-5 is OpenAI’s most advanced model, offering major improvements in reasoning, code quality, and user experience. It is optimized for complex tasks that require step-by-step reasoning, instruction following, and accuracy...")
    (context_length 400000)
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
      (tokenizer GPT)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.000000625")
      (completion "0.000005")
      (web_search "0.01")
      (input_cache_read "0.0000000625")
    ))
    (top_provider ({}
      (context_length 400000)
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
      seed
      structured_outputs
      tool_choice
      tools
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
    (knowledge_cutoff 2024-09-30)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/openai/gpt-5-2025-08-07/endpoints)
    ))
    (benchmarks ({}
      (design_arena (
        ({}
          (arena models)
          (category 3d)
          (elo 1110)
          (win_rate 41.4)
          (rank 83)
        )
        ({}
          (arena models)
          (category asciiart)
          (elo 1178)
          (win_rate 49)
          (rank 35)
        )
        ({}
          (arena models)
          (category codecategories)
          (elo 1196)
          (win_rate 54.7)
          (rank 55)
        )
        ({}
          (arena models)
          (category dataviz)
          (elo 1263)
          (win_rate 62.9)
          (rank 25)
        )
        ({}
          (arena models)
          (category gamedev)
          (elo 1227)
          (win_rate 59.5)
          (rank 39)
        )
        ({}
          (arena models)
          (category svg)
          (elo 1235)
          (win_rate 64.1)
          (rank 17)
        )
        ({}
          (arena models)
          (category uicomponent)
          (elo 1215)
          (win_rate 58.2)
          (rank 42)
        )
        ({}
          (arena models)
          (category website)
          (elo 1207)
          (win_rate 53.8)
          (rank 54)
        )
      ))
      (artificial_analysis ({}
        (intelligence_index 35.3)
        (coding_index 37.8)
        (agentic_index 26.5)
      ))
    ))
    (reasoning ({}
      (mandatory true)
      (supported_efforts (
        high
        medium
        low
        minimal
      ))
      (default_effort medium)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId openai/gpt-5:batch)
  ))
)
