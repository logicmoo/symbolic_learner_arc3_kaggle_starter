(
  (kind model)
  (id openrouter-z-ai_glm-4.6v)
  (label "Z.ai: GLM 4.6V")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model z-ai/glm-4.6v)
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
    (prompt "0.0000003")
    (completion "0.0000009")
    (input_cache_read "0.000000055")
  ))
  (properties (
    (id z-ai/glm-4.6v)
    (canonical_slug z-ai/glm-4.6-20251208)
    (hugging_face_id zai-org/GLM-4.6V)
    (name "Z.ai: GLM 4.6V")
    (created 1765207462)
    (description "GLM-4.6V is a large multimodal model designed for high-fidelity visual understanding and long-context reasoning across images, documents, and mixed media. It supports up to 128K tokens, processes complex page layouts...")
    (context_length 131072)
    (architecture (
      (modality text+image+video->text)
      (input_modalities ([]
        image
        text
        video
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Other)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.0000003")
      (completion "0.0000009")
      (input_cache_read "0.000000055")
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
      max_tokens
      presence_penalty
      reasoning
      repetition_penalty
      response_format
      seed
      stop
      temperature
      tool_choice
      tools
      top_k
      top_p
    ))
    (default_parameters (
      (temperature 0.8)
      (top_p 0.6)
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links (
      (details /api/v1/models/z-ai/glm-4.6-20251208/endpoints)
    ))
    (reasoning (
      (mandatory false)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id z-ai/glm-4.6v)
    (canonical_slug z-ai/glm-4.6-20251208)
    (hugging_face_id zai-org/GLM-4.6V)
    (name "Z.ai: GLM 4.6V")
    (created 1765207462)
    (description "GLM-4.6V is a large multimodal model designed for high-fidelity visual understanding and long-context reasoning across images, documents, and mixed media. It supports up to 128K tokens, processes complex page layouts...")
    (context_length 131072)
    (architecture (
      (modality text+image+video->text)
      (input_modalities ([]
        image
        text
        video
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Other)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.0000003")
      (completion "0.0000009")
      (input_cache_read "0.000000055")
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
      max_tokens
      presence_penalty
      reasoning
      repetition_penalty
      response_format
      seed
      stop
      temperature
      tool_choice
      tools
      top_k
      top_p
    ))
    (default_parameters (
      (temperature 0.8)
      (top_p 0.6)
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links (
      (details /api/v1/models/z-ai/glm-4.6-20251208/endpoints)
    ))
    (reasoning (
      (mandatory false)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId z-ai/glm-4.6v)
  ))
)
