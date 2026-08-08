(
  (kind model)
  (id openrouter-tencent_hy3-preview)
  (label "Tencent: Hy3 preview")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model tencent/hy3-preview)
  (enabled true)
  (capabilities (
    (audio false)
    (code false)
    (functionCalling true)
    (json false)
    (jsonMode false)
    (local false)
    (multimodal false)
    (reasoning true)
    (text true)
    (tools true)
    (vision false)
  ))
  (limits (
    (contextWindow 262144)
    (maxOutputTokens null)
  ))
  (pricing (
    (prompt "0.000000063")
    (completion "0.00000021")
    (input_cache_read "0.000000021")
  ))
  (properties (
    (id tencent/hy3-preview)
    (canonical_slug tencent/hy3-preview-20260421)
    (hugging_face_id tencent/Hy3-preview)
    (name "Tencent: Hy3 preview")
    (created 1776878150)
    (description "Hy3 preview is a high-efficiency Mixture-of-Experts model from Tencent designed for agentic workflows and production use. It supports configurable reasoning levels across disabled, low, and high modes, allowing it to...")
    (context_length 262144)
    (architecture (
      (modality text->text)
      (input_modalities ([]
        text
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Other)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.000000063")
      (completion "0.00000021")
      (input_cache_read "0.000000021")
    ))
    (top_provider (
      (context_length 262144)
      (max_completion_tokens null)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      include_reasoning
      max_tokens
      reasoning
      reasoning_effort
      seed
      temperature
      tool_choice
      tools
      top_p
    ))
    (default_parameters (
      (temperature 0.9)
      (top_p 1)
      (top_k null)
      (frequency_penalty null)
      (presence_penalty null)
      (repetition_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links (
      (details /api/v1/models/tencent/hy3-preview-20260421/endpoints)
    ))
    (benchmarks (
      (design_arena ([]))
      (artificial_analysis (
        (intelligence_index 42.2)
        (coding_index 58.8)
        (agentic_index 31.4)
      ))
    ))
    (reasoning (
      (mandatory false)
      (default_enabled true)
      (supported_efforts ([]
        high
        low
        none
      ))
      (default_effort high)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id tencent/hy3-preview)
    (canonical_slug tencent/hy3-preview-20260421)
    (hugging_face_id tencent/Hy3-preview)
    (name "Tencent: Hy3 preview")
    (created 1776878150)
    (description "Hy3 preview is a high-efficiency Mixture-of-Experts model from Tencent designed for agentic workflows and production use. It supports configurable reasoning levels across disabled, low, and high modes, allowing it to...")
    (context_length 262144)
    (architecture (
      (modality text->text)
      (input_modalities ([]
        text
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Other)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.000000063")
      (completion "0.00000021")
      (input_cache_read "0.000000021")
    ))
    (top_provider (
      (context_length 262144)
      (max_completion_tokens null)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      include_reasoning
      max_tokens
      reasoning
      reasoning_effort
      seed
      temperature
      tool_choice
      tools
      top_p
    ))
    (default_parameters (
      (temperature 0.9)
      (top_p 1)
      (top_k null)
      (frequency_penalty null)
      (presence_penalty null)
      (repetition_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links (
      (details /api/v1/models/tencent/hy3-preview-20260421/endpoints)
    ))
    (benchmarks (
      (design_arena ([]))
      (artificial_analysis (
        (intelligence_index 42.2)
        (coding_index 58.8)
        (agentic_index 31.4)
      ))
    ))
    (reasoning (
      (mandatory false)
      (default_enabled true)
      (supported_efforts ([]
        high
        low
        none
      ))
      (default_effort high)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId tencent/hy3-preview)
  ))
)
