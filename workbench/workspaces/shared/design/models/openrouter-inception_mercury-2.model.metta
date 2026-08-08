({}
  (kind model)
  (id openrouter-inception_mercury-2)
  (label "Inception: Mercury 2")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model inception/mercury-2)
  (enabled true)
  (capabilities ({}
    (audio false)
    (code false)
    (functionCalling true)
    (json true)
    (jsonMode true)
    (local false)
    (multimodal false)
    (reasoning true)
    (text true)
    (tools true)
    (vision false)
  ))
  (limits ({}
    (contextWindow 128000)
    (maxOutputTokens 50000)
  ))
  (pricing ({}
    (prompt "0.00000025")
    (completion "0.00000075")
    (input_cache_read "0.000000025")
  ))
  (properties ({}
    (id inception/mercury-2)
    (canonical_slug inception/mercury-2-20260304)
    (hugging_face_id null)
    (name "Inception: Mercury 2")
    (created 1772636275)
    (description "Mercury 2 is an extremely fast reasoning LLM, and the first reasoning diffusion LLM (dLLM). Instead of generating tokens sequentially, Mercury 2 produces and refines multiple tokens in parallel, achieving...")
    (context_length 128000)
    (architecture ({}
      (modality text->text)
      (input_modalities (
        text
      ))
      (output_modalities (
        text
      ))
      (tokenizer Other)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.00000025")
      (completion "0.00000075")
      (input_cache_read "0.000000025")
    ))
    (top_provider ({}
      (context_length 128000)
      (max_completion_tokens 50000)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      include_reasoning
      max_tokens
      reasoning
      reasoning_effort
      response_format
      stop
      structured_outputs
      temperature
      tool_choice
      tools
    ))
    (default_parameters ({}
      (temperature 0.75)
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
      (details /api/v1/models/inception/mercury-2-20260304/endpoints)
    ))
    (benchmarks ({}
      (design_arena (
        ({}
          (arena models)
          (category 3d)
          (elo 1038)
          (win_rate 23.8)
          (rank 95)
        )
        ({}
          (arena models)
          (category asciiart)
          (elo 1042)
          (win_rate 27.3)
          (rank 55)
        )
        ({}
          (arena models)
          (category codecategories)
          (elo 1023)
          (win_rate 20.7)
          (rank 103)
        )
        ({}
          (arena models)
          (category dataviz)
          (elo 1015)
          (win_rate 21.8)
          (rank 98)
        )
        ({}
          (arena models)
          (category gamedev)
          (elo 1017)
          (win_rate 20.7)
          (rank 99)
        )
        ({}
          (arena models)
          (category svg)
          (elo 1015)
          (win_rate 24)
          (rank 74)
        )
        ({}
          (arena models)
          (category uicomponent)
          (elo 993)
          (win_rate 18.2)
          (rank 97)
        )
        ({}
          (arena models)
          (category website)
          (elo 1016)
          (win_rate 19.8)
          (rank 107)
        )
      ))
      (artificial_analysis ({}
        (intelligence_index 21.9)
        (coding_index 31.1)
        (agentic_index 9.5)
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
      (default_effort medium)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id inception/mercury-2)
    (canonical_slug inception/mercury-2-20260304)
    (hugging_face_id null)
    (name "Inception: Mercury 2")
    (created 1772636275)
    (description "Mercury 2 is an extremely fast reasoning LLM, and the first reasoning diffusion LLM (dLLM). Instead of generating tokens sequentially, Mercury 2 produces and refines multiple tokens in parallel, achieving...")
    (context_length 128000)
    (architecture ({}
      (modality text->text)
      (input_modalities (
        text
      ))
      (output_modalities (
        text
      ))
      (tokenizer Other)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.00000025")
      (completion "0.00000075")
      (input_cache_read "0.000000025")
    ))
    (top_provider ({}
      (context_length 128000)
      (max_completion_tokens 50000)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      include_reasoning
      max_tokens
      reasoning
      reasoning_effort
      response_format
      stop
      structured_outputs
      temperature
      tool_choice
      tools
    ))
    (default_parameters ({}
      (temperature 0.75)
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
      (details /api/v1/models/inception/mercury-2-20260304/endpoints)
    ))
    (benchmarks ({}
      (design_arena (
        ({}
          (arena models)
          (category 3d)
          (elo 1038)
          (win_rate 23.8)
          (rank 95)
        )
        ({}
          (arena models)
          (category asciiart)
          (elo 1042)
          (win_rate 27.3)
          (rank 55)
        )
        ({}
          (arena models)
          (category codecategories)
          (elo 1023)
          (win_rate 20.7)
          (rank 103)
        )
        ({}
          (arena models)
          (category dataviz)
          (elo 1015)
          (win_rate 21.8)
          (rank 98)
        )
        ({}
          (arena models)
          (category gamedev)
          (elo 1017)
          (win_rate 20.7)
          (rank 99)
        )
        ({}
          (arena models)
          (category svg)
          (elo 1015)
          (win_rate 24)
          (rank 74)
        )
        ({}
          (arena models)
          (category uicomponent)
          (elo 993)
          (win_rate 18.2)
          (rank 97)
        )
        ({}
          (arena models)
          (category website)
          (elo 1016)
          (win_rate 19.8)
          (rank 107)
        )
      ))
      (artificial_analysis ({}
        (intelligence_index 21.9)
        (coding_index 31.1)
        (agentic_index 9.5)
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
      (default_effort medium)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId inception/mercury-2)
  ))
)
