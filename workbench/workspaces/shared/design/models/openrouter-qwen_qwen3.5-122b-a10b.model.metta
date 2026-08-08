(
  (kind model)
  (id openrouter-qwen_qwen3.5-122b-a10b)
  (label "Qwen: Qwen3.5-122B-A10B")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model qwen/qwen3.5-122b-a10b)
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
    (contextWindow 262144)
    (maxOutputTokens 81920)
  ))
  (pricing (
    (prompt "0.00000029")
    (completion "0.0000024")
  ))
  (properties (
    (id qwen/qwen3.5-122b-a10b)
    (canonical_slug qwen/qwen3.5-122b-a10b-20260224)
    (hugging_face_id Qwen/Qwen3.5-122B-A10B)
    (name "Qwen: Qwen3.5-122B-A10B")
    (created 1772053789)
    (description "The Qwen3.5 122B-A10B native vision-language model is built on a hybrid architecture that integrates a linear attention mechanism with a sparse mixture-of-experts model, achieving higher inference efficiency. In terms of...")
    (context_length 262144)
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
      (prompt "0.00000029")
      (completion "0.0000024")
    ))
    (top_provider (
      (context_length 262144)
      (max_completion_tokens 81920)
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
      (temperature 0.6)
      (top_p 0.95)
      (top_k 20)
      (frequency_penalty null)
      (presence_penalty null)
      (repetition_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links (
      (details /api/v1/models/qwen/qwen3.5-122b-a10b-20260224/endpoints)
    ))
    (benchmarks (
      (design_arena ([]))
      (artificial_analysis (
        (intelligence_index 32.8)
        (coding_index 45.7)
        (agentic_index 21.3)
      ))
    ))
    (reasoning (
      (mandatory false)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id qwen/qwen3.5-122b-a10b)
    (canonical_slug qwen/qwen3.5-122b-a10b-20260224)
    (hugging_face_id Qwen/Qwen3.5-122B-A10B)
    (name "Qwen: Qwen3.5-122B-A10B")
    (created 1772053789)
    (description "The Qwen3.5 122B-A10B native vision-language model is built on a hybrid architecture that integrates a linear attention mechanism with a sparse mixture-of-experts model, achieving higher inference efficiency. In terms of...")
    (context_length 262144)
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
      (prompt "0.00000029")
      (completion "0.0000024")
    ))
    (top_provider (
      (context_length 262144)
      (max_completion_tokens 81920)
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
      (temperature 0.6)
      (top_p 0.95)
      (top_k 20)
      (frequency_penalty null)
      (presence_penalty null)
      (repetition_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links (
      (details /api/v1/models/qwen/qwen3.5-122b-a10b-20260224/endpoints)
    ))
    (benchmarks (
      (design_arena ([]))
      (artificial_analysis (
        (intelligence_index 32.8)
        (coding_index 45.7)
        (agentic_index 21.3)
      ))
    ))
    (reasoning (
      (mandatory false)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId qwen/qwen3.5-122b-a10b)
  ))
)
