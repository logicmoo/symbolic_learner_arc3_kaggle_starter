(
  (kind model)
  (id openrouter-bytedance_ui-tars-1.5-7b)
  (label "ByteDance: UI-TARS 7B ")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model bytedance/ui-tars-1.5-7b)
  (enabled true)
  (capabilities (
    (audio false)
    (code false)
    (functionCalling false)
    (json true)
    (jsonMode true)
    (local false)
    (multimodal true)
    (reasoning false)
    (text true)
    (tools false)
    (vision true)
  ))
  (limits (
    (contextWindow 128000)
    (maxOutputTokens 2048)
  ))
  (pricing (
    (prompt "0.0000001")
    (completion "0.0000002")
    (input_cache_read "0.0000001")
  ))
  (properties (
    (id bytedance/ui-tars-1.5-7b)
    (canonical_slug bytedance/ui-tars-1.5-7b)
    (hugging_face_id ByteDance-Seed/UI-TARS-1.5-7B)
    (name "ByteDance: UI-TARS 7B ")
    (created 1753205056)
    (description "UI-TARS-1.5 is a multimodal vision-language agent optimized for GUI-based environments, including desktop interfaces, web browsers, mobile systems, and games. Built by ByteDance, it builds upon the UI-TARS framework with reinforcement...")
    (context_length 128000)
    (architecture (
      (modality text+image->text)
      (input_modalities ([]
        image
        text
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Other)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.0000001")
      (completion "0.0000002")
      (input_cache_read "0.0000001")
    ))
    (top_provider (
      (context_length 128000)
      (max_completion_tokens 2048)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      frequency_penalty
      logit_bias
      logprobs
      max_tokens
      presence_penalty
      repetition_penalty
      seed
      stop
      structured_outputs
      temperature
      top_k
      top_logprobs
      top_p
    ))
    (default_parameters ())
    (supported_voices null)
    (knowledge_cutoff 2025-01-31)
    (expiration_date null)
    (links (
      (details /api/v1/models/bytedance/ui-tars-1.5-7b/endpoints)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id bytedance/ui-tars-1.5-7b)
    (canonical_slug bytedance/ui-tars-1.5-7b)
    (hugging_face_id ByteDance-Seed/UI-TARS-1.5-7B)
    (name "ByteDance: UI-TARS 7B ")
    (created 1753205056)
    (description "UI-TARS-1.5 is a multimodal vision-language agent optimized for GUI-based environments, including desktop interfaces, web browsers, mobile systems, and games. Built by ByteDance, it builds upon the UI-TARS framework with reinforcement...")
    (context_length 128000)
    (architecture (
      (modality text+image->text)
      (input_modalities ([]
        image
        text
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Other)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.0000001")
      (completion "0.0000002")
      (input_cache_read "0.0000001")
    ))
    (top_provider (
      (context_length 128000)
      (max_completion_tokens 2048)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      frequency_penalty
      logit_bias
      logprobs
      max_tokens
      presence_penalty
      repetition_penalty
      seed
      stop
      structured_outputs
      temperature
      top_k
      top_logprobs
      top_p
    ))
    (default_parameters ())
    (supported_voices null)
    (knowledge_cutoff 2025-01-31)
    (expiration_date null)
    (links (
      (details /api/v1/models/bytedance/ui-tars-1.5-7b/endpoints)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId bytedance/ui-tars-1.5-7b)
  ))
)
