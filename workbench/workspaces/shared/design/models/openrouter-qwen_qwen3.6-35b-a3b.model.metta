(
  (kind model)
  (id openrouter-qwen_qwen3.6-35b-a3b)
  (label "Qwen: Qwen3.6 35B A3B")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model qwen/qwen3.6-35b-a3b)
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
    (maxOutputTokens 262144)
  ))
  (pricing (
    (prompt "0.00000014")
    (completion "0.000001")
    (input_cache_read "0.00000005")
  ))
  (properties (
    (id qwen/qwen3.6-35b-a3b)
    (canonical_slug qwen/qwen3.6-35b-a3b-20260415)
    (hugging_face_id Qwen/Qwen3.6-35B-A3B)
    (name "Qwen: Qwen3.6 35B A3B")
    (created 1777260255)
    (description "Qwen3.6-35B-A3B is an open-weight multimodal model from Alibaba Cloud with 35 billion total parameters and 3 billion active parameters per token. It uses a hybrid sparse mixture-of-experts architecture combining Gated...")
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
      (tokenizer Qwen)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.00000014")
      (completion "0.000001")
      (input_cache_read "0.00000005")
    ))
    (top_provider (
      (context_length 262144)
      (max_completion_tokens 262144)
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
      (temperature 1)
      (top_p 0.95)
      (top_k 20)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links (
      (details /api/v1/models/qwen/qwen3.6-35b-a3b-20260415/endpoints)
    ))
    (benchmarks (
      (design_arena ([]))
      (artificial_analysis (
        (intelligence_index 32.1)
        (coding_index 41.9)
        (agentic_index 21.6)
      ))
    ))
    (reasoning (
      (mandatory false)
      (default_enabled true)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id qwen/qwen3.6-35b-a3b)
    (canonical_slug qwen/qwen3.6-35b-a3b-20260415)
    (hugging_face_id Qwen/Qwen3.6-35B-A3B)
    (name "Qwen: Qwen3.6 35B A3B")
    (created 1777260255)
    (description "Qwen3.6-35B-A3B is an open-weight multimodal model from Alibaba Cloud with 35 billion total parameters and 3 billion active parameters per token. It uses a hybrid sparse mixture-of-experts architecture combining Gated...")
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
      (tokenizer Qwen)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.00000014")
      (completion "0.000001")
      (input_cache_read "0.00000005")
    ))
    (top_provider (
      (context_length 262144)
      (max_completion_tokens 262144)
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
      (temperature 1)
      (top_p 0.95)
      (top_k 20)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links (
      (details /api/v1/models/qwen/qwen3.6-35b-a3b-20260415/endpoints)
    ))
    (benchmarks (
      (design_arena ([]))
      (artificial_analysis (
        (intelligence_index 32.1)
        (coding_index 41.9)
        (agentic_index 21.6)
      ))
    ))
    (reasoning (
      (mandatory false)
      (default_enabled true)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId qwen/qwen3.6-35b-a3b)
  ))
)
