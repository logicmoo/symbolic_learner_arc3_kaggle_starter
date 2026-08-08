(
  (kind model)
  (id openrouter-deepseek_deepseek-v4-flash-0731)
  (label "DeepSeek: DeepSeek V4 Flash 0731")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model deepseek/deepseek-v4-flash-0731)
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
    (prompt "0.00000009")
    (completion "0.00000018")
    (input_cache_read "0.000000018")
  ))
  (properties (
    (id deepseek/deepseek-v4-flash-0731)
    (canonical_slug deepseek/deepseek-v4-flash-20260731)
    (hugging_face_id deepseek-ai/DeepSeek-V4-Flash-0731)
    (name "DeepSeek: DeepSeek V4 Flash 0731")
    (created 1785478908)
    (description "DeepSeek V4 Flash 0731 is a sparse mixture-of-experts model from DeepSeek, with 13B active parameters out of 284B total. This re-post-trained revision is suited for coding, reasoning, and agent workflows.")
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
      (prompt "0.00000009")
      (completion "0.00000018")
      (input_cache_read "0.000000018")
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
      top_a
      top_k
      top_logprobs
      top_p
    ))
    (default_parameters ())
    (supported_voices ([]))
    (knowledge_cutoff null)
    (expiration_date null)
    (links (
      (details /api/v1/models/deepseek/deepseek-v4-flash-20260731/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena models)
          (category 3d)
          (elo 1272)
          (win_rate 52.5)
          (rank 26)
        )
        (
          (arena models)
          (category codecategories)
          (elo 1258)
          (win_rate 47.2)
          (rank 32)
        )
        (
          (arena models)
          (category dataviz)
          (elo 1194)
          (win_rate 40.7)
          (rank 50)
        )
        (
          (arena models)
          (category gamedev)
          (elo 1247)
          (win_rate 45.6)
          (rank 31)
        )
        (
          (arena models)
          (category uicomponent)
          (elo 1268)
          (win_rate 47.2)
          (rank 29)
        )
        (
          (arena models)
          (category website)
          (elo 1259)
          (win_rate 47)
          (rank 31)
        )
      ))
      (artificial_analysis (
        (intelligence_index 51.8)
        (coding_index 69.1)
        (agentic_index 48.4)
      ))
    ))
    (reasoning (
      (mandatory false)
      (default_enabled true)
      (supported_efforts ([]
        max
        high
        low
      ))
      (default_effort high)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id deepseek/deepseek-v4-flash-0731)
    (canonical_slug deepseek/deepseek-v4-flash-20260731)
    (hugging_face_id deepseek-ai/DeepSeek-V4-Flash-0731)
    (name "DeepSeek: DeepSeek V4 Flash 0731")
    (created 1785478908)
    (description "DeepSeek V4 Flash 0731 is a sparse mixture-of-experts model from DeepSeek, with 13B active parameters out of 284B total. This re-post-trained revision is suited for coding, reasoning, and agent workflows.")
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
      (prompt "0.00000009")
      (completion "0.00000018")
      (input_cache_read "0.000000018")
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
      top_a
      top_k
      top_logprobs
      top_p
    ))
    (default_parameters ())
    (supported_voices ([]))
    (knowledge_cutoff null)
    (expiration_date null)
    (links (
      (details /api/v1/models/deepseek/deepseek-v4-flash-20260731/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena models)
          (category 3d)
          (elo 1272)
          (win_rate 52.5)
          (rank 26)
        )
        (
          (arena models)
          (category codecategories)
          (elo 1258)
          (win_rate 47.2)
          (rank 32)
        )
        (
          (arena models)
          (category dataviz)
          (elo 1194)
          (win_rate 40.7)
          (rank 50)
        )
        (
          (arena models)
          (category gamedev)
          (elo 1247)
          (win_rate 45.6)
          (rank 31)
        )
        (
          (arena models)
          (category uicomponent)
          (elo 1268)
          (win_rate 47.2)
          (rank 29)
        )
        (
          (arena models)
          (category website)
          (elo 1259)
          (win_rate 47)
          (rank 31)
        )
      ))
      (artificial_analysis (
        (intelligence_index 51.8)
        (coding_index 69.1)
        (agentic_index 48.4)
      ))
    ))
    (reasoning (
      (mandatory false)
      (default_enabled true)
      (supported_efforts ([]
        max
        high
        low
      ))
      (default_effort high)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId deepseek/deepseek-v4-flash-0731)
  ))
)
