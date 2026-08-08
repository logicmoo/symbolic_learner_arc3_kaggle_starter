({}
  (kind model)
  (id openrouter-qwen_qwen3-max-thinking)
  (label "Qwen: Qwen3 Max Thinking")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model qwen/qwen3-max-thinking)
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
    (contextWindow 262144)
    (maxOutputTokens 65536)
  ))
  (pricing ({}
    (prompt "0.00000078")
    (completion "0.0000039")
    (overrides (
      ({}
        (min_prompt_tokens 32000)
        (prompt "0.00000156")
        (completion "0.0000078")
      )
      ({}
        (min_prompt_tokens 128000)
        (prompt "0.00000195")
        (completion "0.00000975")
      )
    ))
  ))
  (properties ({}
    (id qwen/qwen3-max-thinking)
    (canonical_slug qwen/qwen3-max-thinking-20260123)
    (hugging_face_id null)
    (name "Qwen: Qwen3 Max Thinking")
    (created 1770671901)
    (description "Qwen3-Max-Thinking is the flagship reasoning model in the Qwen3 series, designed for high-stakes cognitive tasks that require deep, multi-step reasoning. By significantly scaling model capacity and reinforcement learning compute, it...")
    (context_length 262144)
    (architecture ({}
      (modality text->text)
      (input_modalities (
        text
      ))
      (output_modalities (
        text
      ))
      (tokenizer Qwen)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.00000078")
      (completion "0.0000039")
      (overrides (
        ({}
          (min_prompt_tokens 32000)
          (prompt "0.00000156")
          (completion "0.0000078")
        )
        ({}
          (min_prompt_tokens 128000)
          (prompt "0.00000195")
          (completion "0.00000975")
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
    (default_parameters ({}
      (temperature null)
      (top_p null)
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/qwen/qwen3-max-thinking-20260123/endpoints)
    ))
    (reasoning ({}
      (mandatory false)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id qwen/qwen3-max-thinking)
    (canonical_slug qwen/qwen3-max-thinking-20260123)
    (hugging_face_id null)
    (name "Qwen: Qwen3 Max Thinking")
    (created 1770671901)
    (description "Qwen3-Max-Thinking is the flagship reasoning model in the Qwen3 series, designed for high-stakes cognitive tasks that require deep, multi-step reasoning. By significantly scaling model capacity and reinforcement learning compute, it...")
    (context_length 262144)
    (architecture ({}
      (modality text->text)
      (input_modalities (
        text
      ))
      (output_modalities (
        text
      ))
      (tokenizer Qwen)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.00000078")
      (completion "0.0000039")
      (overrides (
        ({}
          (min_prompt_tokens 32000)
          (prompt "0.00000156")
          (completion "0.0000078")
        )
        ({}
          (min_prompt_tokens 128000)
          (prompt "0.00000195")
          (completion "0.00000975")
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
    (default_parameters ({}
      (temperature null)
      (top_p null)
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/qwen/qwen3-max-thinking-20260123/endpoints)
    ))
    (reasoning ({}
      (mandatory false)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId qwen/qwen3-max-thinking)
  ))
)
