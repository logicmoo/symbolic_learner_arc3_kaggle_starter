(
  (kind model)
  (id openrouter-deepseek_deepseek-v4-pro)
  (label "DeepSeek: DeepSeek V4 Pro")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model deepseek/deepseek-v4-pro)
  (enabled true)
  (capabilities (
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
  (limits (
    (contextWindow 1048576)
    (maxOutputTokens 384000)
  ))
  (pricing (
    (prompt "0.000000435")
    (completion "0.00000087")
    (input_cache_read "0.000000003625")
  ))
  (properties (
    (id deepseek/deepseek-v4-pro)
    (canonical_slug deepseek/deepseek-v4-pro-20260423)
    (hugging_face_id deepseek-ai/DeepSeek-V4-Pro)
    (name "DeepSeek: DeepSeek V4 Pro")
    (created 1777000679)
    (description "DeepSeek V4 Pro is a large-scale Mixture-of-Experts model from DeepSeek with 1.6T total parameters and 49B activated parameters, supporting a 1M-token context window. It is designed for advanced reasoning, coding,...")
    (context_length 1048576)
    (architecture (
      (modality text->text)
      (input_modalities ([]
        text
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer DeepSeek)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.000000435")
      (completion "0.00000087")
      (input_cache_read "0.000000003625")
    ))
    (top_provider (
      (context_length 1048576)
      (max_completion_tokens 384000)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
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
      top_k
      top_logprobs
      top_p
    ))
    (default_parameters (
      (temperature 1)
      (top_p 1)
      (top_k null)
      (frequency_penalty null)
      (presence_penalty null)
      (repetition_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links (
      (details /api/v1/models/deepseek/deepseek-v4-pro-20260423/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena agents)
          (category fullstack)
          (elo 948)
          (win_rate 22.1)
          (rank 34)
        )
        (
          (arena agents)
          (category godotgamedev)
          (elo 1059)
          (win_rate 34)
          (rank 27)
        )
        (
          (arena agents)
          (category webapps)
          (elo 1000)
          (win_rate 26.4)
          (rank 32)
        )
        (
          (arena models)
          (category 3d)
          (elo 1312)
          (win_rate 58.5)
          (rank 11)
        )
        (
          (arena models)
          (category asciiart)
          (elo 1189)
          (win_rate 46.7)
          (rank 28)
        )
        (
          (arena models)
          (category codecategories)
          (elo 1271)
          (win_rate 53.6)
          (rank 25)
        )
        (
          (arena models)
          (category dataviz)
          (elo 1226)
          (win_rate 49.4)
          (rank 39)
        )
        (
          (arena models)
          (category gamedev)
          (elo 1273)
          (win_rate 55.1)
          (rank 24)
        )
        (
          (arena models)
          (category svg)
          (elo 1182)
          (win_rate 46.4)
          (rank 38)
        )
        (
          (arena models)
          (category uicomponent)
          (elo 1255)
          (win_rate 51.5)
          (rank 33)
        )
        (
          (arena models)
          (category website)
          (elo 1259)
          (win_rate 52.1)
          (rank 32)
        )
      ))
      (artificial_analysis (
        (intelligence_index 45.3)
        (coding_index 59.4)
        (agentic_index 37.8)
      ))
    ))
    (reasoning (
      (mandatory false)
      (supported_efforts ([]
        xhigh
        high
      ))
      (default_effort high)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id deepseek/deepseek-v4-pro)
    (canonical_slug deepseek/deepseek-v4-pro-20260423)
    (hugging_face_id deepseek-ai/DeepSeek-V4-Pro)
    (name "DeepSeek: DeepSeek V4 Pro")
    (created 1777000679)
    (description "DeepSeek V4 Pro is a large-scale Mixture-of-Experts model from DeepSeek with 1.6T total parameters and 49B activated parameters, supporting a 1M-token context window. It is designed for advanced reasoning, coding,...")
    (context_length 1048576)
    (architecture (
      (modality text->text)
      (input_modalities ([]
        text
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer DeepSeek)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.000000435")
      (completion "0.00000087")
      (input_cache_read "0.000000003625")
    ))
    (top_provider (
      (context_length 1048576)
      (max_completion_tokens 384000)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
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
      top_k
      top_logprobs
      top_p
    ))
    (default_parameters (
      (temperature 1)
      (top_p 1)
      (top_k null)
      (frequency_penalty null)
      (presence_penalty null)
      (repetition_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links (
      (details /api/v1/models/deepseek/deepseek-v4-pro-20260423/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena agents)
          (category fullstack)
          (elo 948)
          (win_rate 22.1)
          (rank 34)
        )
        (
          (arena agents)
          (category godotgamedev)
          (elo 1059)
          (win_rate 34)
          (rank 27)
        )
        (
          (arena agents)
          (category webapps)
          (elo 1000)
          (win_rate 26.4)
          (rank 32)
        )
        (
          (arena models)
          (category 3d)
          (elo 1312)
          (win_rate 58.5)
          (rank 11)
        )
        (
          (arena models)
          (category asciiart)
          (elo 1189)
          (win_rate 46.7)
          (rank 28)
        )
        (
          (arena models)
          (category codecategories)
          (elo 1271)
          (win_rate 53.6)
          (rank 25)
        )
        (
          (arena models)
          (category dataviz)
          (elo 1226)
          (win_rate 49.4)
          (rank 39)
        )
        (
          (arena models)
          (category gamedev)
          (elo 1273)
          (win_rate 55.1)
          (rank 24)
        )
        (
          (arena models)
          (category svg)
          (elo 1182)
          (win_rate 46.4)
          (rank 38)
        )
        (
          (arena models)
          (category uicomponent)
          (elo 1255)
          (win_rate 51.5)
          (rank 33)
        )
        (
          (arena models)
          (category website)
          (elo 1259)
          (win_rate 52.1)
          (rank 32)
        )
      ))
      (artificial_analysis (
        (intelligence_index 45.3)
        (coding_index 59.4)
        (agentic_index 37.8)
      ))
    ))
    (reasoning (
      (mandatory false)
      (supported_efforts ([]
        xhigh
        high
      ))
      (default_effort high)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId deepseek/deepseek-v4-pro)
  ))
)
