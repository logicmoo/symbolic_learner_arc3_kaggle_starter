(
  (kind model)
  (id openrouter-qwen_qwen3-coder-plus)
  (label "Qwen: Qwen3 Coder Plus")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model qwen/qwen3-coder-plus)
  (enabled true)
  (capabilities (
    (audio false)
    (code true)
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
    (maxOutputTokens 65536)
  ))
  (pricing (
    (prompt "0.00000065")
    (completion "0.00000325")
    (input_cache_read "0.00000013")
    (input_cache_write "0.0000008125")
    (overrides ([]
      (
        (min_prompt_tokens 32000)
        (prompt "0.00000117")
        (completion "0.00000585")
        (input_cache_read "0.000000234")
        (input_cache_write "0.0000014625")
      )
      (
        (min_prompt_tokens 128000)
        (prompt "0.00000195")
        (completion "0.00000975")
        (input_cache_read "0.00000039")
        (input_cache_write "0.0000024375")
      )
    ))
  ))
  (properties (
    (id qwen/qwen3-coder-plus)
    (canonical_slug qwen/qwen3-coder-plus)
    (hugging_face_id "")
    (name "Qwen: Qwen3 Coder Plus")
    (created 1758662707)
    (description "Qwen3 Coder Plus is Alibaba's proprietary version of the Open Source Qwen3 Coder 480B A35B. It is a powerful coding agent model specializing in autonomous programming via tool calling and...")
    (context_length 1000000)
    (architecture (
      (modality text->text)
      (input_modalities ([]
        text
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Qwen3)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.00000065")
      (completion "0.00000325")
      (input_cache_read "0.00000013")
      (input_cache_write "0.0000008125")
      (overrides ([]
        (
          (min_prompt_tokens 32000)
          (prompt "0.00000117")
          (completion "0.00000585")
          (input_cache_read "0.000000234")
          (input_cache_write "0.0000014625")
        )
        (
          (min_prompt_tokens 128000)
          (prompt "0.00000195")
          (completion "0.00000975")
          (input_cache_read "0.00000039")
          (input_cache_write "0.0000024375")
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
    (default_parameters (
      (temperature null)
      (top_p null)
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff 2025-06-30)
    (expiration_date null)
    (links (
      (details /api/v1/models/qwen/qwen3-coder-plus/endpoints)
    ))
    (reasoning (
      (mandatory false)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id qwen/qwen3-coder-plus)
    (canonical_slug qwen/qwen3-coder-plus)
    (hugging_face_id "")
    (name "Qwen: Qwen3 Coder Plus")
    (created 1758662707)
    (description "Qwen3 Coder Plus is Alibaba's proprietary version of the Open Source Qwen3 Coder 480B A35B. It is a powerful coding agent model specializing in autonomous programming via tool calling and...")
    (context_length 1000000)
    (architecture (
      (modality text->text)
      (input_modalities ([]
        text
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Qwen3)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.00000065")
      (completion "0.00000325")
      (input_cache_read "0.00000013")
      (input_cache_write "0.0000008125")
      (overrides ([]
        (
          (min_prompt_tokens 32000)
          (prompt "0.00000117")
          (completion "0.00000585")
          (input_cache_read "0.000000234")
          (input_cache_write "0.0000014625")
        )
        (
          (min_prompt_tokens 128000)
          (prompt "0.00000195")
          (completion "0.00000975")
          (input_cache_read "0.00000039")
          (input_cache_write "0.0000024375")
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
    (default_parameters (
      (temperature null)
      (top_p null)
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff 2025-06-30)
    (expiration_date null)
    (links (
      (details /api/v1/models/qwen/qwen3-coder-plus/endpoints)
    ))
    (reasoning (
      (mandatory false)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId qwen/qwen3-coder-plus)
  ))
)
