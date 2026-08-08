({}
  (kind model)
  (id openrouter-deepseek_deepseek-v4-flash)
  (label "DeepSeek: DeepSeek V4 Flash 0423")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model deepseek/deepseek-v4-flash)
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
    (contextWindow 1048576)
    (maxOutputTokens 393216)
  ))
  (pricing ({}
    (prompt "0.00000014")
    (completion "0.00000028")
    (input_cache_read "0.000000028")
  ))
  (properties ({}
    (id deepseek/deepseek-v4-flash)
    (canonical_slug deepseek/deepseek-v4-flash-20260423)
    (hugging_face_id deepseek-ai/DeepSeek-V4-Flash)
    (name "DeepSeek: DeepSeek V4 Flash 0423")
    (created 1777000666)
    (description "DeepSeek V4 Flash is an efficiency-optimized Mixture-of-Experts model from DeepSeek with 284B total parameters and 13B activated parameters, supporting a 1M-token context window. It is designed for fast inference and...")
    (context_length 1048576)
    (architecture ({}
      (modality text->text)
      (input_modalities (
        text
      ))
      (output_modalities (
        text
      ))
      (tokenizer DeepSeek)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.00000014")
      (completion "0.00000028")
      (input_cache_read "0.000000028")
    ))
    (top_provider ({}
      (context_length 1048576)
      (max_completion_tokens 393216)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      include_reasoning
      logit_bias
      logprobs
      max_tokens
      min_p
      presence_penalty
      reasoning
      reasoning_effort
      repetition_penalty
      response_format
      seed
      stop
      structured_outputs
      temperature
      tool_choice
      tools
      top_a
      top_k
      top_logprobs
      top_p
    ))
    (default_parameters ({}))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/deepseek/deepseek-v4-flash-20260423/endpoints)
    ))
    (benchmarks ({}
      (design_arena (
        ({}
          (arena models)
          (category 3d)
          (elo 1243)
          (win_rate 49.3)
          (rank 37)
        )
        ({}
          (arena models)
          (category asciiart)
          (elo 1148)
          (win_rate 42.8)
          (rank 45)
        )
        ({}
          (arena models)
          (category codecategories)
          (elo 1233)
          (win_rate 48.9)
          (rank 38)
        )
        ({}
          (arena models)
          (category dataviz)
          (elo 1153)
          (win_rate 40.5)
          (rank 70)
        )
        ({}
          (arena models)
          (category gamedev)
          (elo 1237)
          (win_rate 50.2)
          (rank 35)
        )
        ({}
          (arena models)
          (category svg)
          (elo 1200)
          (win_rate 48.4)
          (rank 28)
        )
        ({}
          (arena models)
          (category uicomponent)
          (elo 1197)
          (win_rate 44.7)
          (rank 51)
        )
        ({}
          (arena models)
          (category website)
          (elo 1230)
          (win_rate 49.1)
          (rank 41)
        )
      ))
    ))
    (reasoning ({}
      (mandatory false)
      (supported_efforts (
        xhigh
        high
      ))
      (default_effort high)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id deepseek/deepseek-v4-flash)
    (canonical_slug deepseek/deepseek-v4-flash-20260423)
    (hugging_face_id deepseek-ai/DeepSeek-V4-Flash)
    (name "DeepSeek: DeepSeek V4 Flash 0423")
    (created 1777000666)
    (description "DeepSeek V4 Flash is an efficiency-optimized Mixture-of-Experts model from DeepSeek with 284B total parameters and 13B activated parameters, supporting a 1M-token context window. It is designed for fast inference and...")
    (context_length 1048576)
    (architecture ({}
      (modality text->text)
      (input_modalities (
        text
      ))
      (output_modalities (
        text
      ))
      (tokenizer DeepSeek)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.00000014")
      (completion "0.00000028")
      (input_cache_read "0.000000028")
    ))
    (top_provider ({}
      (context_length 1048576)
      (max_completion_tokens 393216)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      include_reasoning
      logit_bias
      logprobs
      max_tokens
      min_p
      presence_penalty
      reasoning
      reasoning_effort
      repetition_penalty
      response_format
      seed
      stop
      structured_outputs
      temperature
      tool_choice
      tools
      top_a
      top_k
      top_logprobs
      top_p
    ))
    (default_parameters ({}))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/deepseek/deepseek-v4-flash-20260423/endpoints)
    ))
    (benchmarks ({}
      (design_arena (
        ({}
          (arena models)
          (category 3d)
          (elo 1243)
          (win_rate 49.3)
          (rank 37)
        )
        ({}
          (arena models)
          (category asciiart)
          (elo 1148)
          (win_rate 42.8)
          (rank 45)
        )
        ({}
          (arena models)
          (category codecategories)
          (elo 1233)
          (win_rate 48.9)
          (rank 38)
        )
        ({}
          (arena models)
          (category dataviz)
          (elo 1153)
          (win_rate 40.5)
          (rank 70)
        )
        ({}
          (arena models)
          (category gamedev)
          (elo 1237)
          (win_rate 50.2)
          (rank 35)
        )
        ({}
          (arena models)
          (category svg)
          (elo 1200)
          (win_rate 48.4)
          (rank 28)
        )
        ({}
          (arena models)
          (category uicomponent)
          (elo 1197)
          (win_rate 44.7)
          (rank 51)
        )
        ({}
          (arena models)
          (category website)
          (elo 1230)
          (win_rate 49.1)
          (rank 41)
        )
      ))
    ))
    (reasoning ({}
      (mandatory false)
      (supported_efforts (
        xhigh
        high
      ))
      (default_effort high)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId deepseek/deepseek-v4-flash)
  ))
)
