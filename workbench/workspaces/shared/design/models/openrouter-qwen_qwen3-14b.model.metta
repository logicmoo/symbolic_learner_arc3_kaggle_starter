(
  (kind model)
  (id openrouter-qwen_qwen3-14b)
  (label "Qwen: Qwen3 14B")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model qwen/qwen3-14b)
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
    (maxOutputTokens 8192)
  ))
  (pricing (
    (prompt "0.0000002275")
    (completion "0.00000091")
  ))
  (properties (
    (id qwen/qwen3-14b)
    (canonical_slug qwen/qwen3-14b-04-28)
    (hugging_face_id Qwen/Qwen3-14B)
    (name "Qwen: Qwen3 14B")
    (created 1745876478)
    (description "Qwen3-14B is a dense 14.8B parameter causal language model from the Qwen3 series, designed for both complex reasoning and efficient dialogue. It supports seamless switching between a \"thinking\" mode for...")
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
      (prompt "0.0000002275")
      (completion "0.00000091")
    ))
    (top_provider (
      (context_length 131072)
      (max_completion_tokens 8192)
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
      (details /api/v1/models/qwen/qwen3-14b-04-28/endpoints)
    ))
    (benchmarks (
      (design_arena ([]))
      (artificial_analysis (
        (intelligence_index 10.4)
        (coding_index 13.8)
        (agentic_index 1.9)
      ))
    ))
    (reasoning (
      (mandatory false)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id qwen/qwen3-14b)
    (canonical_slug qwen/qwen3-14b-04-28)
    (hugging_face_id Qwen/Qwen3-14B)
    (name "Qwen: Qwen3 14B")
    (created 1745876478)
    (description "Qwen3-14B is a dense 14.8B parameter causal language model from the Qwen3 series, designed for both complex reasoning and efficient dialogue. It supports seamless switching between a \"thinking\" mode for...")
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
      (prompt "0.0000002275")
      (completion "0.00000091")
    ))
    (top_provider (
      (context_length 131072)
      (max_completion_tokens 8192)
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
      (details /api/v1/models/qwen/qwen3-14b-04-28/endpoints)
    ))
    (benchmarks (
      (design_arena ([]))
      (artificial_analysis (
        (intelligence_index 10.4)
        (coding_index 13.8)
        (agentic_index 1.9)
      ))
    ))
    (reasoning (
      (mandatory false)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId qwen/qwen3-14b)
  ))
)
