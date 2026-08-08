(
  (kind model)
  (id openrouter-qwen_qwen-plus)
  (label "Qwen: Qwen-Plus")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model qwen/qwen-plus)
  (enabled true)
  (capabilities (
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
  (limits (
    (contextWindow 1000000)
    (maxOutputTokens 32768)
  ))
  (pricing (
    (prompt "0.00000026")
    (completion "0.00000078")
    (input_cache_read "0.000000052")
    (input_cache_write "0.000000325")
    (overrides ([]
      (
        (min_prompt_tokens 256000)
        (prompt "0.00000078")
        (completion "0.00000234")
        (input_cache_read "0.000000156")
        (input_cache_write "0.000000975")
      )
    ))
  ))
  (properties (
    (id qwen/qwen-plus)
    (canonical_slug qwen/qwen-plus-2025-01-25)
    (hugging_face_id "")
    (name "Qwen: Qwen-Plus")
    (created 1738409840)
    (description "Qwen-Plus, based on the Qwen2.5 foundation model, is a 131K context model with a balanced performance, speed, and cost combination.")
    (context_length 1000000)
    (architecture (
      (modality text->text)
      (input_modalities ([]
        text
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Qwen)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.00000026")
      (completion "0.00000078")
      (input_cache_read "0.000000052")
      (input_cache_write "0.000000325")
      (overrides ([]
        (
          (min_prompt_tokens 256000)
          (prompt "0.00000078")
          (completion "0.00000234")
          (input_cache_read "0.000000156")
          (input_cache_write "0.000000975")
        )
      ))
    ))
    (top_provider (
      (context_length 1000000)
      (max_completion_tokens 32768)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
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
    (default_parameters ())
    (supported_voices null)
    (knowledge_cutoff 2025-03-31)
    (expiration_date null)
    (links (
      (details /api/v1/models/qwen/qwen-plus-2025-01-25/endpoints)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id qwen/qwen-plus)
    (canonical_slug qwen/qwen-plus-2025-01-25)
    (hugging_face_id "")
    (name "Qwen: Qwen-Plus")
    (created 1738409840)
    (description "Qwen-Plus, based on the Qwen2.5 foundation model, is a 131K context model with a balanced performance, speed, and cost combination.")
    (context_length 1000000)
    (architecture (
      (modality text->text)
      (input_modalities ([]
        text
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Qwen)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.00000026")
      (completion "0.00000078")
      (input_cache_read "0.000000052")
      (input_cache_write "0.000000325")
      (overrides ([]
        (
          (min_prompt_tokens 256000)
          (prompt "0.00000078")
          (completion "0.00000234")
          (input_cache_read "0.000000156")
          (input_cache_write "0.000000975")
        )
      ))
    ))
    (top_provider (
      (context_length 1000000)
      (max_completion_tokens 32768)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
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
    (default_parameters ())
    (supported_voices null)
    (knowledge_cutoff 2025-03-31)
    (expiration_date null)
    (links (
      (details /api/v1/models/qwen/qwen-plus-2025-01-25/endpoints)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId qwen/qwen-plus)
  ))
)
