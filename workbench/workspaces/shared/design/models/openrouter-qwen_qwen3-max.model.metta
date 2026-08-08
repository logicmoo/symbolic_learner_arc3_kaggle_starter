({}
  (kind model)
  (id openrouter-qwen_qwen3-max)
  (label "Qwen: Qwen3 Max")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model qwen/qwen3-max)
  (enabled true)
  (capabilities ({}
    (audio false)
    (code false)
    (functionCalling true)
    (json true)
    (jsonMode true)
    (local false)
    (multimodal false)
    (reasoning false)
    (text true)
    (tools true)
    (vision false)
  ))
  (limits ({}
    (contextWindow 262144)
    (maxOutputTokens 65536)
  ))
  (pricing ({}
    (prompt "0.00000078")
    (completion "0.0000039")
    (input_cache_read "0.000000156")
    (input_cache_write "0.000000975")
    (overrides (
      ({}
        (min_prompt_tokens 32000)
        (prompt "0.00000156")
        (completion "0.0000078")
        (input_cache_read "0.000000312")
        (input_cache_write "0.00000195")
      )
      ({}
        (min_prompt_tokens 128000)
        (prompt "0.00000195")
        (completion "0.00000975")
        (input_cache_read "0.00000039")
        (input_cache_write "0.0000024375")
      )
    ))
  ))
  (properties ({}
    (id qwen/qwen3-max)
    (canonical_slug qwen/qwen3-max)
    (hugging_face_id "")
    (name "Qwen: Qwen3 Max")
    (created 1758662808)
    (description "Qwen3-Max is an updated release built on the Qwen3 series, offering major improvements in reasoning, instruction following, multilingual support, and long-tail knowledge coverage compared to the January 2025 version. It...")
    (context_length 262144)
    (architecture ({}
      (modality text->text)
      (input_modalities (
        text
      ))
      (output_modalities (
        text
      ))
      (tokenizer Qwen3)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.00000078")
      (completion "0.0000039")
      (input_cache_read "0.000000156")
      (input_cache_write "0.000000975")
      (overrides (
        ({}
          (min_prompt_tokens 32000)
          (prompt "0.00000156")
          (completion "0.0000078")
          (input_cache_read "0.000000312")
          (input_cache_write "0.00000195")
        )
        ({}
          (min_prompt_tokens 128000)
          (prompt "0.00000195")
          (completion "0.00000975")
          (input_cache_read "0.00000039")
          (input_cache_write "0.0000024375")
        )
      ))
    ))
    (top_provider ({}
      (context_length 262144)
      (max_completion_tokens 65536)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      logprobs
      max_tokens
      presence_penalty
      response_format
      seed
      stop
      structured_outputs
      temperature
      tool_choice
      tools
      top_k
      top_logprobs
      top_p
    ))
    (default_parameters ({}
      (temperature 1)
      (top_p 1)
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff 2025-06-30)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/qwen/qwen3-max/endpoints)
    ))
    (benchmarks ({}
      (design_arena (
        ({}
          (arena models)
          (category 3d)
          (elo 1128)
          (win_rate 43.5)
          (rank 77)
        )
        ({}
          (arena models)
          (category asciiart)
          (elo 1165)
          (win_rate 47.2)
          (rank 39)
        )
        ({}
          (arena models)
          (category codecategories)
          (elo 1137)
          (win_rate 44)
          (rank 79)
        )
        ({}
          (arena models)
          (category dataviz)
          (elo 1127)
          (win_rate 41.1)
          (rank 77)
        )
        ({}
          (arena models)
          (category gamedev)
          (elo 1135)
          (win_rate 43.9)
          (rank 73)
        )
        ({}
          (arena models)
          (category svg)
          (elo 1058)
          (win_rate 37.3)
          (rank 66)
        )
        ({}
          (arena models)
          (category uicomponent)
          (elo 1111)
          (win_rate 40.2)
          (rank 78)
        )
        ({}
          (arena models)
          (category website)
          (elo 1141)
          (win_rate 44.5)
          (rank 80)
        )
      ))
    ))
    (reasoning ({}
      (mandatory false)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id qwen/qwen3-max)
    (canonical_slug qwen/qwen3-max)
    (hugging_face_id "")
    (name "Qwen: Qwen3 Max")
    (created 1758662808)
    (description "Qwen3-Max is an updated release built on the Qwen3 series, offering major improvements in reasoning, instruction following, multilingual support, and long-tail knowledge coverage compared to the January 2025 version. It...")
    (context_length 262144)
    (architecture ({}
      (modality text->text)
      (input_modalities (
        text
      ))
      (output_modalities (
        text
      ))
      (tokenizer Qwen3)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.00000078")
      (completion "0.0000039")
      (input_cache_read "0.000000156")
      (input_cache_write "0.000000975")
      (overrides (
        ({}
          (min_prompt_tokens 32000)
          (prompt "0.00000156")
          (completion "0.0000078")
          (input_cache_read "0.000000312")
          (input_cache_write "0.00000195")
        )
        ({}
          (min_prompt_tokens 128000)
          (prompt "0.00000195")
          (completion "0.00000975")
          (input_cache_read "0.00000039")
          (input_cache_write "0.0000024375")
        )
      ))
    ))
    (top_provider ({}
      (context_length 262144)
      (max_completion_tokens 65536)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      logprobs
      max_tokens
      presence_penalty
      response_format
      seed
      stop
      structured_outputs
      temperature
      tool_choice
      tools
      top_k
      top_logprobs
      top_p
    ))
    (default_parameters ({}
      (temperature 1)
      (top_p 1)
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff 2025-06-30)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/qwen/qwen3-max/endpoints)
    ))
    (benchmarks ({}
      (design_arena (
        ({}
          (arena models)
          (category 3d)
          (elo 1128)
          (win_rate 43.5)
          (rank 77)
        )
        ({}
          (arena models)
          (category asciiart)
          (elo 1165)
          (win_rate 47.2)
          (rank 39)
        )
        ({}
          (arena models)
          (category codecategories)
          (elo 1137)
          (win_rate 44)
          (rank 79)
        )
        ({}
          (arena models)
          (category dataviz)
          (elo 1127)
          (win_rate 41.1)
          (rank 77)
        )
        ({}
          (arena models)
          (category gamedev)
          (elo 1135)
          (win_rate 43.9)
          (rank 73)
        )
        ({}
          (arena models)
          (category svg)
          (elo 1058)
          (win_rate 37.3)
          (rank 66)
        )
        ({}
          (arena models)
          (category uicomponent)
          (elo 1111)
          (win_rate 40.2)
          (rank 78)
        )
        ({}
          (arena models)
          (category website)
          (elo 1141)
          (win_rate 44.5)
          (rank 80)
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
    (remoteModelId qwen/qwen3-max)
  ))
)
