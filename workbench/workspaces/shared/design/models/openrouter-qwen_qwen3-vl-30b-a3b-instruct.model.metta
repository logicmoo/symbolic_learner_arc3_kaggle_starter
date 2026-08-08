(
  (kind model)
  (id openrouter-qwen_qwen3-vl-30b-a3b-instruct)
  (label "Qwen: Qwen3 VL 30B A3B Instruct")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model qwen/qwen3-vl-30b-a3b-instruct)
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
    (maxOutputTokens 16384)
  ))
  (pricing (
    (prompt "0.00000015")
    (completion "0.0000006")
  ))
  (properties (
    (id qwen/qwen3-vl-30b-a3b-instruct)
    (canonical_slug qwen/qwen3-vl-30b-a3b-instruct)
    (hugging_face_id Qwen/Qwen3-VL-30B-A3B-Instruct)
    (name "Qwen: Qwen3 VL 30B A3B Instruct")
    (created 1759794476)
    (description "Qwen3-VL-30B-A3B-Instruct is a multimodal model that unifies strong text generation with visual understanding for images and videos. Its Instruct variant optimizes instruction-following for general multimodal tasks. It excels in perception...")
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
      (prompt "0.00000015")
      (completion "0.0000006")
    ))
    (top_provider (
      (context_length 262144)
      (max_completion_tokens 16384)
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
      (top_k 20)
      (frequency_penalty null)
      (presence_penalty null)
      (repetition_penalty 1)
    ))
    (supported_voices null)
    (knowledge_cutoff 2025-03-31)
    (expiration_date null)
    (links (
      (details /api/v1/models/qwen/qwen3-vl-30b-a3b-instruct/endpoints)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id qwen/qwen3-vl-30b-a3b-instruct)
    (canonical_slug qwen/qwen3-vl-30b-a3b-instruct)
    (hugging_face_id Qwen/Qwen3-VL-30B-A3B-Instruct)
    (name "Qwen: Qwen3 VL 30B A3B Instruct")
    (created 1759794476)
    (description "Qwen3-VL-30B-A3B-Instruct is a multimodal model that unifies strong text generation with visual understanding for images and videos. Its Instruct variant optimizes instruction-following for general multimodal tasks. It excels in perception...")
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
      (prompt "0.00000015")
      (completion "0.0000006")
    ))
    (top_provider (
      (context_length 262144)
      (max_completion_tokens 16384)
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
      (top_k 20)
      (frequency_penalty null)
      (presence_penalty null)
      (repetition_penalty 1)
    ))
    (supported_voices null)
    (knowledge_cutoff 2025-03-31)
    (expiration_date null)
    (links (
      (details /api/v1/models/qwen/qwen3-vl-30b-a3b-instruct/endpoints)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId qwen/qwen3-vl-30b-a3b-instruct)
  ))
)
