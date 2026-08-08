(
  (kind model)
  (id openrouter-qwen_qwen3.6-plus)
  (label "Qwen: Qwen3.6 Plus")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model qwen/qwen3.6-plus)
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
    (contextWindow 1000000)
    (maxOutputTokens 65536)
  ))
  (pricing (
    (prompt "0.000000325")
    (completion "0.00000195")
    (input_cache_write "0.00000040625")
    (overrides ([]
      (
        (min_prompt_tokens 256000)
        (prompt "0.0000013")
        (completion "0.0000039")
        (input_cache_write "0.000001625")
      )
    ))
  ))
  (properties (
    (id qwen/qwen3.6-plus)
    (canonical_slug qwen/qwen3.6-plus-04-02)
    (hugging_face_id "")
    (name "Qwen: Qwen3.6 Plus")
    (created 1775133557)
    (description "Qwen 3.6 Plus builds on a hybrid architecture that combines efficient linear attention with sparse mixture-of-experts routing, enabling strong scalability and high-performance inference. Compared to the 3.5 series, it delivers...")
    (context_length 1000000)
    (architecture (
      (modality text+image+video->text)
      (input_modalities ([]
        text
        image
        video
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Qwen3)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.000000325")
      (completion "0.00000195")
      (input_cache_write "0.00000040625")
      (overrides ([]
        (
          (min_prompt_tokens 256000)
          (prompt "0.0000013")
          (completion "0.0000039")
          (input_cache_write "0.000001625")
        )
      ))
    ))
    (top_provider (
      (context_length 1000000)
      (max_completion_tokens 65536)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      frequency_penalty
      include_reasoning
      logprobs
      max_tokens
      presence_penalty
      reasoning
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
      (details /api/v1/models/qwen/qwen3.6-plus-04-02/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena models)
          (category 3d)
          (elo 1254)
          (win_rate 51.5)
          (rank 32)
        )
        (
          (arena models)
          (category asciiart)
          (elo 1157)
          (win_rate 44.4)
          (rank 41)
        )
        (
          (arena models)
          (category codecategories)
          (elo 1262)
          (win_rate 52.1)
          (rank 31)
        )
        (
          (arena models)
          (category dataviz)
          (elo 1256)
          (win_rate 51.6)
          (rank 30)
        )
        (
          (arena models)
          (category gamedev)
          (elo 1245)
          (win_rate 50.8)
          (rank 33)
        )
        (
          (arena models)
          (category svg)
          (elo 1208)
          (win_rate 51.6)
          (rank 27)
        )
        (
          (arena models)
          (category uicomponent)
          (elo 1270)
          (win_rate 52.7)
          (rank 28)
        )
        (
          (arena models)
          (category website)
          (elo 1262)
          (win_rate 52.5)
          (rank 30)
        )
      ))
      (artificial_analysis (
        (intelligence_index 40.5)
        (coding_index 54.5)
        (agentic_index 29)
      ))
    ))
    (reasoning (
      (mandatory false)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id qwen/qwen3.6-plus)
    (canonical_slug qwen/qwen3.6-plus-04-02)
    (hugging_face_id "")
    (name "Qwen: Qwen3.6 Plus")
    (created 1775133557)
    (description "Qwen 3.6 Plus builds on a hybrid architecture that combines efficient linear attention with sparse mixture-of-experts routing, enabling strong scalability and high-performance inference. Compared to the 3.5 series, it delivers...")
    (context_length 1000000)
    (architecture (
      (modality text+image+video->text)
      (input_modalities ([]
        text
        image
        video
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Qwen3)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.000000325")
      (completion "0.00000195")
      (input_cache_write "0.00000040625")
      (overrides ([]
        (
          (min_prompt_tokens 256000)
          (prompt "0.0000013")
          (completion "0.0000039")
          (input_cache_write "0.000001625")
        )
      ))
    ))
    (top_provider (
      (context_length 1000000)
      (max_completion_tokens 65536)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      frequency_penalty
      include_reasoning
      logprobs
      max_tokens
      presence_penalty
      reasoning
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
      (details /api/v1/models/qwen/qwen3.6-plus-04-02/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena models)
          (category 3d)
          (elo 1254)
          (win_rate 51.5)
          (rank 32)
        )
        (
          (arena models)
          (category asciiart)
          (elo 1157)
          (win_rate 44.4)
          (rank 41)
        )
        (
          (arena models)
          (category codecategories)
          (elo 1262)
          (win_rate 52.1)
          (rank 31)
        )
        (
          (arena models)
          (category dataviz)
          (elo 1256)
          (win_rate 51.6)
          (rank 30)
        )
        (
          (arena models)
          (category gamedev)
          (elo 1245)
          (win_rate 50.8)
          (rank 33)
        )
        (
          (arena models)
          (category svg)
          (elo 1208)
          (win_rate 51.6)
          (rank 27)
        )
        (
          (arena models)
          (category uicomponent)
          (elo 1270)
          (win_rate 52.7)
          (rank 28)
        )
        (
          (arena models)
          (category website)
          (elo 1262)
          (win_rate 52.5)
          (rank 30)
        )
      ))
      (artificial_analysis (
        (intelligence_index 40.5)
        (coding_index 54.5)
        (agentic_index 29)
      ))
    ))
    (reasoning (
      (mandatory false)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId qwen/qwen3.6-plus)
  ))
)
