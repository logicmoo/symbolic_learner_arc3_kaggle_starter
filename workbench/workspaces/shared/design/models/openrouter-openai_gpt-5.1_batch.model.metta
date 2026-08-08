(
  (kind model)
  (id openrouter-openai_gpt-5.1_batch)
  (label "OpenAI: GPT-5.1 (batch)")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model openai/gpt-5.1:batch)
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
    (contextWindow 400000)
    (maxOutputTokens 128000)
  ))
  (pricing (
    (prompt "0.000000625")
    (completion "0.000005")
    (web_search "0.01")
    (input_cache_read "0.0000000625")
  ))
  (properties (
    (id openai/gpt-5.1:batch)
    (canonical_slug openai/gpt-5.1-20251113)
    (hugging_face_id "")
    (name "OpenAI: GPT-5.1 (batch)")
    (created 1763060305)
    (description "GPT-5.1 is the latest frontier-grade model in the GPT-5 series, offering stronger general-purpose reasoning, improved instruction adherence, and a more natural conversational style compared to GPT-5. It uses adaptive reasoning...")
    (context_length 400000)
    (architecture (
      (modality text+image+file->text)
      (input_modalities ([]
        image
        text
        file
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer GPT)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.000000625")
      (completion "0.000005")
      (web_search "0.01")
      (input_cache_read "0.0000000625")
    ))
    (top_provider (
      (context_length 400000)
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
    (knowledge_cutoff null)
    (expiration_date null)
    (links (
      (details /api/v1/models/openai/gpt-5.1-20251113/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena models)
          (category 3d)
          (elo 1116)
          (win_rate 43.9)
          (rank 81)
        )
        (
          (arena models)
          (category asciiart)
          (elo 1156)
          (win_rate 48.6)
          (rank 42)
        )
        (
          (arena models)
          (category codecategories)
          (elo 1199)
          (win_rate 53.1)
          (rank 53)
        )
        (
          (arena models)
          (category dataviz)
          (elo 1232)
          (win_rate 58)
          (rank 37)
        )
        (
          (arena models)
          (category gamedev)
          (elo 1220)
          (win_rate 56)
          (rank 40)
        )
        (
          (arena models)
          (category svg)
          (elo 1196)
          (win_rate 57.4)
          (rank 32)
        )
        (
          (arena models)
          (category uicomponent)
          (elo 1200)
          (win_rate 53)
          (rank 50)
        )
        (
          (arena models)
          (category website)
          (elo 1210)
          (win_rate 54.1)
          (rank 50)
        )
      ))
      (artificial_analysis (
        (intelligence_index 37.5)
        (coding_index 49.4)
        (agentic_index 21.6)
      ))
    ))
    (reasoning (
      (mandatory false)
      (default_enabled true)
      (supported_efforts ([]
        high
        medium
        low
        none
      ))
      (default_effort none)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id openai/gpt-5.1:batch)
    (canonical_slug openai/gpt-5.1-20251113)
    (hugging_face_id "")
    (name "OpenAI: GPT-5.1 (batch)")
    (created 1763060305)
    (description "GPT-5.1 is the latest frontier-grade model in the GPT-5 series, offering stronger general-purpose reasoning, improved instruction adherence, and a more natural conversational style compared to GPT-5. It uses adaptive reasoning...")
    (context_length 400000)
    (architecture (
      (modality text+image+file->text)
      (input_modalities ([]
        image
        text
        file
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer GPT)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.000000625")
      (completion "0.000005")
      (web_search "0.01")
      (input_cache_read "0.0000000625")
    ))
    (top_provider (
      (context_length 400000)
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
    (knowledge_cutoff null)
    (expiration_date null)
    (links (
      (details /api/v1/models/openai/gpt-5.1-20251113/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena models)
          (category 3d)
          (elo 1116)
          (win_rate 43.9)
          (rank 81)
        )
        (
          (arena models)
          (category asciiart)
          (elo 1156)
          (win_rate 48.6)
          (rank 42)
        )
        (
          (arena models)
          (category codecategories)
          (elo 1199)
          (win_rate 53.1)
          (rank 53)
        )
        (
          (arena models)
          (category dataviz)
          (elo 1232)
          (win_rate 58)
          (rank 37)
        )
        (
          (arena models)
          (category gamedev)
          (elo 1220)
          (win_rate 56)
          (rank 40)
        )
        (
          (arena models)
          (category svg)
          (elo 1196)
          (win_rate 57.4)
          (rank 32)
        )
        (
          (arena models)
          (category uicomponent)
          (elo 1200)
          (win_rate 53)
          (rank 50)
        )
        (
          (arena models)
          (category website)
          (elo 1210)
          (win_rate 54.1)
          (rank 50)
        )
      ))
      (artificial_analysis (
        (intelligence_index 37.5)
        (coding_index 49.4)
        (agentic_index 21.6)
      ))
    ))
    (reasoning (
      (mandatory false)
      (default_enabled true)
      (supported_efforts ([]
        high
        medium
        low
        none
      ))
      (default_effort none)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId openai/gpt-5.1:batch)
  ))
)
