(
  (kind model)
  (id openrouter-qwen_qwen-plus-2025-07-28_thinking)
  (label "Qwen: Qwen Plus 0728 (thinking)")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model qwen/qwen-plus-2025-07-28:thinking)
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
    (contextWindow 1000000)
    (maxOutputTokens 32768)
  ))
  (pricing (
    (prompt "0.0000004")
    (completion "0.0000012")
    (input_cache_write "0.0000005")
    (overrides ([]
      (
        (min_prompt_tokens 256000)
        (prompt "0.0000012")
        (completion "0.0000036")
        (input_cache_write "0.0000015")
      )
    ))
  ))
  (properties (
    (id qwen/qwen-plus-2025-07-28:thinking)
    (canonical_slug qwen/qwen-plus-2025-07-28)
    (hugging_face_id "")
    (name "Qwen: Qwen Plus 0728 (thinking)")
    (created 1757347599)
    (description "Qwen Plus 0728, based on the Qwen3 foundation model, is a 1 million context hybrid reasoning model with a balanced performance, speed, and cost combination.")
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
      (prompt "0.0000004")
      (completion "0.0000012")
      (input_cache_write "0.0000005")
      (overrides ([]
        (
          (min_prompt_tokens 256000)
          (prompt "0.0000012")
          (completion "0.0000036")
          (input_cache_write "0.0000015")
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
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff 2025-03-31)
    (expiration_date null)
    (links (
      (details /api/v1/models/qwen/qwen-plus-2025-07-28/endpoints)
    ))
    (reasoning (
      (mandatory false)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id qwen/qwen-plus-2025-07-28:thinking)
    (canonical_slug qwen/qwen-plus-2025-07-28)
    (hugging_face_id "")
    (name "Qwen: Qwen Plus 0728 (thinking)")
    (created 1757347599)
    (description "Qwen Plus 0728, based on the Qwen3 foundation model, is a 1 million context hybrid reasoning model with a balanced performance, speed, and cost combination.")
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
      (prompt "0.0000004")
      (completion "0.0000012")
      (input_cache_write "0.0000005")
      (overrides ([]
        (
          (min_prompt_tokens 256000)
          (prompt "0.0000012")
          (completion "0.0000036")
          (input_cache_write "0.0000015")
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
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff 2025-03-31)
    (expiration_date null)
    (links (
      (details /api/v1/models/qwen/qwen-plus-2025-07-28/endpoints)
    ))
    (reasoning (
      (mandatory false)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId qwen/qwen-plus-2025-07-28:thinking)
  ))
)
