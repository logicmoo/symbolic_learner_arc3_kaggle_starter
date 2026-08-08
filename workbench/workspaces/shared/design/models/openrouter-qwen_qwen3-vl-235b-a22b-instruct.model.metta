(
  (kind model)
  (id openrouter-qwen_qwen3-vl-235b-a22b-instruct)
  (label "Qwen: Qwen3 VL 235B A22B Instruct")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model qwen/qwen3-vl-235b-a22b-instruct)
  (enabled true)
  (capabilities (
    (audio false)
    (code false)
    (functionCalling true)
    (json true)
    (jsonMode true)
    (local false)
    (multimodal true)
    (reasoning false)
    (text true)
    (tools true)
    (vision true)
  ))
  (limits (
    (contextWindow 262144)
    (maxOutputTokens 32768)
  ))
  (pricing (
    (prompt "0.00000021")
    (completion "0.0000019")
    (input_cache_read "0.0000001")
  ))
  (properties (
    (id qwen/qwen3-vl-235b-a22b-instruct)
    (canonical_slug qwen/qwen3-vl-235b-a22b-instruct)
    (hugging_face_id Qwen/Qwen3-VL-235B-A22B-Instruct)
    (name "Qwen: Qwen3 VL 235B A22B Instruct")
    (created 1758668687)
    (description "Qwen3-VL-235B-A22B Instruct is an open-weight multimodal model that unifies strong text generation with visual understanding across images and video. The Instruct model targets general vision-language use (VQA, document parsing, chart/table...")
    (context_length 262144)
    (architecture (
      (modality text+image->text)
      (input_modalities ([]
        text
        image
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Qwen3)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.00000021")
      (completion "0.0000019")
      (input_cache_read "0.0000001")
    ))
    (top_provider (
      (context_length 131072)
      (max_completion_tokens 32768)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
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
    (default_parameters (
      (temperature 0.7)
      (top_p 0.8)
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff 2025-03-31)
    (expiration_date null)
    (links (
      (details /api/v1/models/qwen/qwen3-vl-235b-a22b-instruct/endpoints)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id qwen/qwen3-vl-235b-a22b-instruct)
    (canonical_slug qwen/qwen3-vl-235b-a22b-instruct)
    (hugging_face_id Qwen/Qwen3-VL-235B-A22B-Instruct)
    (name "Qwen: Qwen3 VL 235B A22B Instruct")
    (created 1758668687)
    (description "Qwen3-VL-235B-A22B Instruct is an open-weight multimodal model that unifies strong text generation with visual understanding across images and video. The Instruct model targets general vision-language use (VQA, document parsing, chart/table...")
    (context_length 262144)
    (architecture (
      (modality text+image->text)
      (input_modalities ([]
        text
        image
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Qwen3)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.00000021")
      (completion "0.0000019")
      (input_cache_read "0.0000001")
    ))
    (top_provider (
      (context_length 131072)
      (max_completion_tokens 32768)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
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
    (default_parameters (
      (temperature 0.7)
      (top_p 0.8)
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff 2025-03-31)
    (expiration_date null)
    (links (
      (details /api/v1/models/qwen/qwen3-vl-235b-a22b-instruct/endpoints)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId qwen/qwen3-vl-235b-a22b-instruct)
  ))
)
