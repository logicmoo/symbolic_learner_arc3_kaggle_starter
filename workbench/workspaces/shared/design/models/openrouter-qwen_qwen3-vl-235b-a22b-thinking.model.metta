(
  (kind model)
  (id openrouter-qwen_qwen3-vl-235b-a22b-thinking)
  (label "Qwen: Qwen3 VL 235B A22B Thinking")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model qwen/qwen3-vl-235b-a22b-thinking)
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
    (contextWindow 131072)
    (maxOutputTokens 32768)
  ))
  (pricing (
    (prompt "0.0000004")
    (completion "0.000004")
  ))
  (properties (
    (id qwen/qwen3-vl-235b-a22b-thinking)
    (canonical_slug qwen/qwen3-vl-235b-a22b-thinking)
    (hugging_face_id Qwen/Qwen3-VL-235B-A22B-Thinking)
    (name "Qwen: Qwen3 VL 235B A22B Thinking")
    (created 1758668690)
    (description "Qwen3-VL-235B-A22B Thinking is a multimodal model that unifies strong text generation with visual understanding across images and video. The Thinking model is optimized for multimodal reasoning in STEM and math....")
    (context_length 131072)
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
      (prompt "0.0000004")
      (completion "0.000004")
    ))
    (top_provider (
      (context_length 131072)
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
      (temperature 0.8)
      (top_p 0.95)
      (top_k 20)
      (frequency_penalty null)
      (presence_penalty null)
      (repetition_penalty 1)
    ))
    (supported_voices null)
    (knowledge_cutoff 2025-03-31)
    (expiration_date null)
    (links (
      (details /api/v1/models/qwen/qwen3-vl-235b-a22b-thinking/endpoints)
    ))
    (reasoning (
      (mandatory true)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id qwen/qwen3-vl-235b-a22b-thinking)
    (canonical_slug qwen/qwen3-vl-235b-a22b-thinking)
    (hugging_face_id Qwen/Qwen3-VL-235B-A22B-Thinking)
    (name "Qwen: Qwen3 VL 235B A22B Thinking")
    (created 1758668690)
    (description "Qwen3-VL-235B-A22B Thinking is a multimodal model that unifies strong text generation with visual understanding across images and video. The Thinking model is optimized for multimodal reasoning in STEM and math....")
    (context_length 131072)
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
      (prompt "0.0000004")
      (completion "0.000004")
    ))
    (top_provider (
      (context_length 131072)
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
      (temperature 0.8)
      (top_p 0.95)
      (top_k 20)
      (frequency_penalty null)
      (presence_penalty null)
      (repetition_penalty 1)
    ))
    (supported_voices null)
    (knowledge_cutoff 2025-03-31)
    (expiration_date null)
    (links (
      (details /api/v1/models/qwen/qwen3-vl-235b-a22b-thinking/endpoints)
    ))
    (reasoning (
      (mandatory true)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId qwen/qwen3-vl-235b-a22b-thinking)
  ))
)
