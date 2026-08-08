(
  (kind model)
  (id openrouter-qwen_qwen3-32b)
  (label "Qwen: Qwen3 32B")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model qwen/qwen3-32b)
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
    (contextWindow 131072)
    (maxOutputTokens 16384)
  ))
  (pricing (
    (prompt "0.00000008")
    (completion "0.00000028")
  ))
  (properties (
    (id qwen/qwen3-32b)
    (canonical_slug qwen/qwen3-32b-04-28)
    (hugging_face_id Qwen/Qwen3-32B)
    (name "Qwen: Qwen3 32B")
    (created 1745875945)
    (description "Qwen3-32B is a dense 32.8B parameter causal language model from the Qwen3 series, optimized for both complex reasoning and efficient dialogue. It supports seamless switching between a \"thinking\" mode for...")
    (context_length 131072)
    (architecture (
      (modality text->text)
      (input_modalities ([]
        text
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Qwen3)
      (instruct_type qwen3)
    ))
    (pricing (
      (prompt "0.00000008")
      (completion "0.00000028")
    ))
    (top_provider (
      (context_length 40960)
      (max_completion_tokens 16384)
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
    (default_parameters ())
    (supported_voices null)
    (knowledge_cutoff 2025-03-31)
    (expiration_date null)
    (links (
      (details /api/v1/models/qwen/qwen3-32b-04-28/endpoints)
    ))
    (benchmarks (
      (design_arena ([]))
      (artificial_analysis (
        (intelligence_index 11.4)
        (coding_index 15.3)
        (agentic_index 1.8)
      ))
    ))
    (reasoning (
      (mandatory false)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id qwen/qwen3-32b)
    (canonical_slug qwen/qwen3-32b-04-28)
    (hugging_face_id Qwen/Qwen3-32B)
    (name "Qwen: Qwen3 32B")
    (created 1745875945)
    (description "Qwen3-32B is a dense 32.8B parameter causal language model from the Qwen3 series, optimized for both complex reasoning and efficient dialogue. It supports seamless switching between a \"thinking\" mode for...")
    (context_length 131072)
    (architecture (
      (modality text->text)
      (input_modalities ([]
        text
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Qwen3)
      (instruct_type qwen3)
    ))
    (pricing (
      (prompt "0.00000008")
      (completion "0.00000028")
    ))
    (top_provider (
      (context_length 40960)
      (max_completion_tokens 16384)
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
    (default_parameters ())
    (supported_voices null)
    (knowledge_cutoff 2025-03-31)
    (expiration_date null)
    (links (
      (details /api/v1/models/qwen/qwen3-32b-04-28/endpoints)
    ))
    (benchmarks (
      (design_arena ([]))
      (artificial_analysis (
        (intelligence_index 11.4)
        (coding_index 15.3)
        (agentic_index 1.8)
      ))
    ))
    (reasoning (
      (mandatory false)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId qwen/qwen3-32b)
  ))
)
