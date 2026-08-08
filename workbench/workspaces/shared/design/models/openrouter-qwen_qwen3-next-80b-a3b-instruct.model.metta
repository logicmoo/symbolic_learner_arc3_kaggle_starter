({}
  (kind model)
  (id openrouter-qwen_qwen3-next-80b-a3b-instruct)
  (label "Qwen: Qwen3 Next 80B A3B Instruct")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model qwen/qwen3-next-80b-a3b-instruct)
  (enabled true)
  (capabilities ({}
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
  (limits ({}
    (contextWindow 262144)
    (maxOutputTokens 16384)
  ))
  (pricing ({}
    (prompt "0.00000009")
    (completion "0.0000011")
  ))
  (properties ({}
    (id qwen/qwen3-next-80b-a3b-instruct)
    (canonical_slug qwen/qwen3-next-80b-a3b-instruct-2509)
    (hugging_face_id Qwen/Qwen3-Next-80B-A3B-Instruct)
    (name "Qwen: Qwen3 Next 80B A3B Instruct")
    (created 1757612213)
    (description "Qwen3-Next-80B-A3B-Instruct is an instruction-tuned chat model in the Qwen3-Next series optimized for fast, stable responses without “thinking” traces. It targets complex tasks across reasoning, code generation, knowledge QA, and multilingual...")
    (context_length 262144)
    (architecture ({}
      (modality text->text)
      (input_modalities (
        text
      ))
      (output_modalities (
        text
      ))
      (tokenizer Qwen3)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.00000009")
      (completion "0.0000011")
    ))
    (top_provider ({}
      (context_length 262144)
      (max_completion_tokens 16384)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      logit_bias
      logprobs
      max_tokens
      min_p
      presence_penalty
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
    (default_parameters ({}))
    (supported_voices null)
    (knowledge_cutoff 2025-09-30)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/qwen/qwen3-next-80b-a3b-instruct-2509/endpoints)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id qwen/qwen3-next-80b-a3b-instruct)
    (canonical_slug qwen/qwen3-next-80b-a3b-instruct-2509)
    (hugging_face_id Qwen/Qwen3-Next-80B-A3B-Instruct)
    (name "Qwen: Qwen3 Next 80B A3B Instruct")
    (created 1757612213)
    (description "Qwen3-Next-80B-A3B-Instruct is an instruction-tuned chat model in the Qwen3-Next series optimized for fast, stable responses without “thinking” traces. It targets complex tasks across reasoning, code generation, knowledge QA, and multilingual...")
    (context_length 262144)
    (architecture ({}
      (modality text->text)
      (input_modalities (
        text
      ))
      (output_modalities (
        text
      ))
      (tokenizer Qwen3)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.00000009")
      (completion "0.0000011")
    ))
    (top_provider ({}
      (context_length 262144)
      (max_completion_tokens 16384)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      logit_bias
      logprobs
      max_tokens
      min_p
      presence_penalty
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
    (default_parameters ({}))
    (supported_voices null)
    (knowledge_cutoff 2025-09-30)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/qwen/qwen3-next-80b-a3b-instruct-2509/endpoints)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId qwen/qwen3-next-80b-a3b-instruct)
  ))
)
