(
  (kind model)
  (id openrouter-qwen_qwen3-coder-flash)
  (label "Qwen: Qwen3 Coder Flash")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model qwen/qwen3-coder-flash)
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
    (prompt "0.000000195")
    (completion "0.000000975")
    (input_cache_read "0.000000039")
    (input_cache_write "0.00000024375")
    (overrides ([]
      (
        (min_prompt_tokens 32000)
        (prompt "0.000000325")
        (completion "0.000001625")
        (input_cache_read "0.000000065")
        (input_cache_write "0.00000040625")
      )
      (
        (min_prompt_tokens 128000)
        (prompt "0.00000052")
        (completion "0.0000026")
        (input_cache_read "0.000000104")
        (input_cache_write "0.00000065")
      )
    ))
  ))
  (properties (
    (id qwen/qwen3-coder-flash)
    (canonical_slug qwen/qwen3-coder-flash)
    (hugging_face_id "")
    (name "Qwen: Qwen3 Coder Flash")
    (created 1758115536)
    (description "Qwen3 Coder Flash is Alibaba's fast and cost efficient version of their proprietary Qwen3 Coder Plus. It is a powerful coding agent model specializing in autonomous programming via tool calling...")
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
      (prompt "0.000000195")
      (completion "0.000000975")
      (input_cache_read "0.000000039")
      (input_cache_write "0.00000024375")
      (overrides ([]
        (
          (min_prompt_tokens 32000)
          (prompt "0.000000325")
          (completion "0.000001625")
          (input_cache_read "0.000000065")
          (input_cache_write "0.00000040625")
        )
        (
          (min_prompt_tokens 128000)
          (prompt "0.00000052")
          (completion "0.0000026")
          (input_cache_read "0.000000104")
          (input_cache_write "0.00000065")
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
      (details /api/v1/models/qwen/qwen3-coder-flash/endpoints)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id qwen/qwen3-coder-flash)
    (canonical_slug qwen/qwen3-coder-flash)
    (hugging_face_id "")
    (name "Qwen: Qwen3 Coder Flash")
    (created 1758115536)
    (description "Qwen3 Coder Flash is Alibaba's fast and cost efficient version of their proprietary Qwen3 Coder Plus. It is a powerful coding agent model specializing in autonomous programming via tool calling...")
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
      (prompt "0.000000195")
      (completion "0.000000975")
      (input_cache_read "0.000000039")
      (input_cache_write "0.00000024375")
      (overrides ([]
        (
          (min_prompt_tokens 32000)
          (prompt "0.000000325")
          (completion "0.000001625")
          (input_cache_read "0.000000065")
          (input_cache_write "0.00000040625")
        )
        (
          (min_prompt_tokens 128000)
          (prompt "0.00000052")
          (completion "0.0000026")
          (input_cache_read "0.000000104")
          (input_cache_write "0.00000065")
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
      (details /api/v1/models/qwen/qwen3-coder-flash/endpoints)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId qwen/qwen3-coder-flash)
  ))
)
