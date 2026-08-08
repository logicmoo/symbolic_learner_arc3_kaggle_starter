(
  (kind model)
  (id openrouter-aion-labs_aion-3.0-mini)
  (label "AionLabs: Aion-3.0-Mini")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model aion-labs/aion-3.0-mini)
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
    (maxOutputTokens 32768)
  ))
  (pricing (
    (prompt "0.0000007")
    (completion "0.0000014")
    (input_cache_read "0.00000018")
  ))
  (properties (
    (id aion-labs/aion-3.0-mini)
    (canonical_slug aion-labs/aion-3.0-mini-20260707)
    (hugging_face_id null)
    (name "AionLabs: Aion-3.0-Mini")
    (created 1783443096)
    (description "Aion-3.0 Mini is a multi-model roleplaying and storytelling system from AionLabs, built on the DeepSeek family of models. It uses a collaborative generation process in which multiple specialized models each...")
    (context_length 131072)
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
      (prompt "0.0000007")
      (completion "0.0000014")
      (input_cache_read "0.00000018")
    ))
    (top_provider (
      (context_length 131072)
      (max_completion_tokens 32768)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      include_reasoning
      max_tokens
      reasoning
      response_format
      temperature
      tool_choice
      tools
      top_p
    ))
    (default_parameters ())
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links (
      (details /api/v1/models/aion-labs/aion-3.0-mini-20260707/endpoints)
    ))
    (reasoning (
      (mandatory true)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id aion-labs/aion-3.0-mini)
    (canonical_slug aion-labs/aion-3.0-mini-20260707)
    (hugging_face_id null)
    (name "AionLabs: Aion-3.0-Mini")
    (created 1783443096)
    (description "Aion-3.0 Mini is a multi-model roleplaying and storytelling system from AionLabs, built on the DeepSeek family of models. It uses a collaborative generation process in which multiple specialized models each...")
    (context_length 131072)
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
      (prompt "0.0000007")
      (completion "0.0000014")
      (input_cache_read "0.00000018")
    ))
    (top_provider (
      (context_length 131072)
      (max_completion_tokens 32768)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      include_reasoning
      max_tokens
      reasoning
      response_format
      temperature
      tool_choice
      tools
      top_p
    ))
    (default_parameters ())
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links (
      (details /api/v1/models/aion-labs/aion-3.0-mini-20260707/endpoints)
    ))
    (reasoning (
      (mandatory true)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId aion-labs/aion-3.0-mini)
  ))
)
