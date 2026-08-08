({}
  (kind model)
  (id openrouter-bytedance-seed_seed-1.6-flash)
  (label "ByteDance Seed: Seed 1.6 Flash")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model bytedance-seed/seed-1.6-flash)
  (enabled true)
  (capabilities ({}
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
  (limits ({}
    (contextWindow 262144)
    (maxOutputTokens 32768)
  ))
  (pricing ({}
    (prompt "0.000000075")
    (completion "0.0000003")
    (overrides (
      ({}
        (min_prompt_tokens 128000)
        (prompt "0.0000001")
        (completion "0.0000008")
      )
    ))
  ))
  (properties ({}
    (id bytedance-seed/seed-1.6-flash)
    (canonical_slug bytedance-seed/seed-1.6-flash-20250625)
    (hugging_face_id "")
    (name "ByteDance Seed: Seed 1.6 Flash")
    (created 1766505011)
    (description "Seed 1.6 Flash is an ultra-fast multimodal deep thinking model by ByteDance Seed, supporting both text and visual understanding. It features a 256k context window and can generate outputs of...")
    (context_length 262144)
    (architecture ({}
      (modality text+image+video->text)
      (input_modalities (
        image
        text
        video
      ))
      (output_modalities (
        text
      ))
      (tokenizer Other)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.000000075")
      (completion "0.0000003")
      (overrides (
        ({}
          (min_prompt_tokens 128000)
          (prompt "0.0000001")
          (completion "0.0000008")
        )
      ))
    ))
    (top_provider ({}
      (context_length 262144)
      (max_completion_tokens 32768)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      include_reasoning
      max_tokens
      reasoning
      response_format
      stop
      structured_outputs
      temperature
      tool_choice
      tools
      top_p
    ))
    (default_parameters ({}
      (temperature null)
      (top_p null)
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/bytedance-seed/seed-1.6-flash-20250625/endpoints)
    ))
    (reasoning ({}
      (mandatory false)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id bytedance-seed/seed-1.6-flash)
    (canonical_slug bytedance-seed/seed-1.6-flash-20250625)
    (hugging_face_id "")
    (name "ByteDance Seed: Seed 1.6 Flash")
    (created 1766505011)
    (description "Seed 1.6 Flash is an ultra-fast multimodal deep thinking model by ByteDance Seed, supporting both text and visual understanding. It features a 256k context window and can generate outputs of...")
    (context_length 262144)
    (architecture ({}
      (modality text+image+video->text)
      (input_modalities (
        image
        text
        video
      ))
      (output_modalities (
        text
      ))
      (tokenizer Other)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.000000075")
      (completion "0.0000003")
      (overrides (
        ({}
          (min_prompt_tokens 128000)
          (prompt "0.0000001")
          (completion "0.0000008")
        )
      ))
    ))
    (top_provider ({}
      (context_length 262144)
      (max_completion_tokens 32768)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      include_reasoning
      max_tokens
      reasoning
      response_format
      stop
      structured_outputs
      temperature
      tool_choice
      tools
      top_p
    ))
    (default_parameters ({}
      (temperature null)
      (top_p null)
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/bytedance-seed/seed-1.6-flash-20250625/endpoints)
    ))
    (reasoning ({}
      (mandatory false)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId bytedance-seed/seed-1.6-flash)
  ))
)
