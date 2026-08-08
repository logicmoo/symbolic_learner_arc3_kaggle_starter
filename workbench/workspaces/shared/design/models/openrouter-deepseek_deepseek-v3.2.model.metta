(
  (kind model)
  (id openrouter-deepseek_deepseek-v3.2)
  (label "DeepSeek: DeepSeek V3.2")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model deepseek/deepseek-v3.2)
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
    (contextWindow 163840)
    (maxOutputTokens 163840)
  ))
  (pricing (
    (prompt "0.00000026")
    (completion "0.00000038")
    (input_cache_read "0.00000013")
  ))
  (properties (
    (id deepseek/deepseek-v3.2)
    (canonical_slug deepseek/deepseek-v3.2-20251201)
    (hugging_face_id deepseek-ai/DeepSeek-V3.2)
    (name "DeepSeek: DeepSeek V3.2")
    (created 1764594642)
    (description "DeepSeek-V3.2 is a large language model designed to harmonize high computational efficiency with strong reasoning and agentic tool-use performance. It introduces DeepSeek Sparse Attention (DSA), a fine-grained sparse attention mechanism...")
    (context_length 163840)
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
      (prompt "0.00000026")
      (completion "0.00000038")
      (input_cache_read "0.00000013")
    ))
    (top_provider (
      (context_length 163840)
      (max_completion_tokens 163840)
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
      (top_p 0.95)
      (top_k null)
      (frequency_penalty null)
      (presence_penalty null)
      (repetition_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links (
      (details /api/v1/models/deepseek/deepseek-v3.2-20251201/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena models)
          (category 3d)
          (elo 1187)
          (win_rate 49.5)
          (rank 51)
        )
        (
          (arena models)
          (category asciiart)
          (elo 1120)
          (win_rate 40.5)
          (rank 50)
        )
        (
          (arena models)
          (category codecategories)
          (elo 1192)
          (win_rate 49.3)
          (rank 59)
        )
        (
          (arena models)
          (category dataviz)
          (elo 1186)
          (win_rate 48.1)
          (rank 58)
        )
        (
          (arena models)
          (category gamedev)
          (elo 1172)
          (win_rate 46.6)
          (rank 61)
        )
        (
          (arena models)
          (category svg)
          (elo 1079)
          (win_rate 40.8)
          (rank 59)
        )
        (
          (arena models)
          (category uicomponent)
          (elo 1182)
          (win_rate 46.8)
          (rank 58)
        )
        (
          (arena models)
          (category website)
          (elo 1197)
          (win_rate 50.2)
          (rank 58)
        )
      ))
      (artificial_analysis (
        (intelligence_index 32.6)
        (coding_index 44.2)
        (agentic_index 18.3)
      ))
    ))
    (reasoning (
      (mandatory false)
      (default_enabled false)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id deepseek/deepseek-v3.2)
    (canonical_slug deepseek/deepseek-v3.2-20251201)
    (hugging_face_id deepseek-ai/DeepSeek-V3.2)
    (name "DeepSeek: DeepSeek V3.2")
    (created 1764594642)
    (description "DeepSeek-V3.2 is a large language model designed to harmonize high computational efficiency with strong reasoning and agentic tool-use performance. It introduces DeepSeek Sparse Attention (DSA), a fine-grained sparse attention mechanism...")
    (context_length 163840)
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
      (prompt "0.00000026")
      (completion "0.00000038")
      (input_cache_read "0.00000013")
    ))
    (top_provider (
      (context_length 163840)
      (max_completion_tokens 163840)
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
      (top_p 0.95)
      (top_k null)
      (frequency_penalty null)
      (presence_penalty null)
      (repetition_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links (
      (details /api/v1/models/deepseek/deepseek-v3.2-20251201/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena models)
          (category 3d)
          (elo 1187)
          (win_rate 49.5)
          (rank 51)
        )
        (
          (arena models)
          (category asciiart)
          (elo 1120)
          (win_rate 40.5)
          (rank 50)
        )
        (
          (arena models)
          (category codecategories)
          (elo 1192)
          (win_rate 49.3)
          (rank 59)
        )
        (
          (arena models)
          (category dataviz)
          (elo 1186)
          (win_rate 48.1)
          (rank 58)
        )
        (
          (arena models)
          (category gamedev)
          (elo 1172)
          (win_rate 46.6)
          (rank 61)
        )
        (
          (arena models)
          (category svg)
          (elo 1079)
          (win_rate 40.8)
          (rank 59)
        )
        (
          (arena models)
          (category uicomponent)
          (elo 1182)
          (win_rate 46.8)
          (rank 58)
        )
        (
          (arena models)
          (category website)
          (elo 1197)
          (win_rate 50.2)
          (rank 58)
        )
      ))
      (artificial_analysis (
        (intelligence_index 32.6)
        (coding_index 44.2)
        (agentic_index 18.3)
      ))
    ))
    (reasoning (
      (mandatory false)
      (default_enabled false)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId deepseek/deepseek-v3.2)
  ))
)
