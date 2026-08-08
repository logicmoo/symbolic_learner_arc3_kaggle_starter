(
  (kind model)
  (id openrouter-openai_gpt-5.1-codex)
  (label "OpenAI: GPT-5.1-Codex")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model openai/gpt-5.1-codex)
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
    (contextWindow 400000)
    (maxOutputTokens 128000)
  ))
  (pricing (
    (prompt "0.00000125")
    (completion "0.00001")
    (web_search "0.01")
    (input_cache_read "0.00000013")
  ))
  (properties (
    (id openai/gpt-5.1-codex)
    (canonical_slug openai/gpt-5.1-codex-20251113)
    (hugging_face_id "")
    (name "OpenAI: GPT-5.1-Codex")
    (created 1763060298)
    (description "GPT-5.1-Codex is a specialized version of GPT-5.1 optimized for software engineering and coding workflows. It is designed for both interactive development sessions and long, independent execution of complex engineering tasks....")
    (context_length 400000)
    (architecture (
      (modality text+image->text)
      (input_modalities ([]
        text
        image
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer GPT)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.00000125")
      (completion "0.00001")
      (web_search "0.01")
      (input_cache_read "0.00000013")
    ))
    (top_provider (
      (context_length 400000)
      (max_completion_tokens 128000)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      include_reasoning
      max_completion_tokens
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
      (details /api/v1/models/openai/gpt-5.1-codex-20251113/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena agents)
          (category fullstack)
          (elo 1086)
          (win_rate 44.5)
          (rank 26)
        )
        (
          (arena agents)
          (category mobileapps)
          (elo 1191)
          (win_rate 53.4)
          (rank 20)
        )
        (
          (arena agents)
          (category webapps)
          (elo 1068)
          (win_rate 44.1)
          (rank 31)
        )
        (
          (arena models)
          (category codecategories)
          (elo 1179)
          (win_rate 55.3)
          (rank 62)
        )
        (
          (arena models)
          (category dataviz)
          (elo 1205)
          (win_rate 51.4)
          (rank 45)
        )
        (
          (arena models)
          (category gamedev)
          (elo 1179)
          (win_rate 52.3)
          (rank 57)
        )
        (
          (arena models)
          (category website)
          (elo 1183)
          (win_rate 56)
          (rank 65)
        )
      ))
    ))
    (reasoning (
      (mandatory true)
      (supported_efforts ([]
        high
        medium
        low
      ))
      (default_effort medium)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id openai/gpt-5.1-codex)
    (canonical_slug openai/gpt-5.1-codex-20251113)
    (hugging_face_id "")
    (name "OpenAI: GPT-5.1-Codex")
    (created 1763060298)
    (description "GPT-5.1-Codex is a specialized version of GPT-5.1 optimized for software engineering and coding workflows. It is designed for both interactive development sessions and long, independent execution of complex engineering tasks....")
    (context_length 400000)
    (architecture (
      (modality text+image->text)
      (input_modalities ([]
        text
        image
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer GPT)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.00000125")
      (completion "0.00001")
      (web_search "0.01")
      (input_cache_read "0.00000013")
    ))
    (top_provider (
      (context_length 400000)
      (max_completion_tokens 128000)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      include_reasoning
      max_completion_tokens
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
      (details /api/v1/models/openai/gpt-5.1-codex-20251113/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena agents)
          (category fullstack)
          (elo 1086)
          (win_rate 44.5)
          (rank 26)
        )
        (
          (arena agents)
          (category mobileapps)
          (elo 1191)
          (win_rate 53.4)
          (rank 20)
        )
        (
          (arena agents)
          (category webapps)
          (elo 1068)
          (win_rate 44.1)
          (rank 31)
        )
        (
          (arena models)
          (category codecategories)
          (elo 1179)
          (win_rate 55.3)
          (rank 62)
        )
        (
          (arena models)
          (category dataviz)
          (elo 1205)
          (win_rate 51.4)
          (rank 45)
        )
        (
          (arena models)
          (category gamedev)
          (elo 1179)
          (win_rate 52.3)
          (rank 57)
        )
        (
          (arena models)
          (category website)
          (elo 1183)
          (win_rate 56)
          (rank 65)
        )
      ))
    ))
    (reasoning (
      (mandatory true)
      (supported_efforts ([]
        high
        medium
        low
      ))
      (default_effort medium)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId openai/gpt-5.1-codex)
  ))
)
