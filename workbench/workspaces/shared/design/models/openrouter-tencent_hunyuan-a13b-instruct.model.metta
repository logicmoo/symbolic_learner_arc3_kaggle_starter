(
  (kind model)
  (id openrouter-tencent_hunyuan-a13b-instruct)
  (label "Tencent: Hunyuan A13B Instruct")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model tencent/hunyuan-a13b-instruct)
  (enabled true)
  (capabilities (
    (audio false)
    (code false)
    (functionCalling false)
    (json true)
    (jsonMode true)
    (local false)
    (multimodal false)
    (reasoning true)
    (text true)
    (tools false)
    (vision false)
  ))
  (limits (
    (contextWindow 131072)
    (maxOutputTokens 131072)
  ))
  (pricing (
    (prompt "0.00000014")
    (completion "0.00000057")
  ))
  (properties (
    (id tencent/hunyuan-a13b-instruct)
    (canonical_slug tencent/hunyuan-a13b-instruct)
    (hugging_face_id tencent/Hunyuan-A13B-Instruct)
    (name "Tencent: Hunyuan A13B Instruct")
    (created 1751987664)
    (description "Hunyuan-A13B is a 13B active parameter Mixture-of-Experts (MoE) language model developed by Tencent, with a total parameter count of 80B and support for reasoning via Chain-of-Thought. It offers competitive benchmark...")
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
      (prompt "0.00000014")
      (completion "0.00000057")
    ))
    (top_provider (
      (context_length 131072)
      (max_completion_tokens 131072)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      frequency_penalty
      include_reasoning
      max_tokens
      reasoning
      response_format
      structured_outputs
      temperature
      top_k
      top_p
    ))
    (default_parameters ())
    (supported_voices null)
    (knowledge_cutoff 2025-03-31)
    (expiration_date null)
    (links (
      (details /api/v1/models/tencent/hunyuan-a13b-instruct/endpoints)
    ))
    (reasoning (
      (mandatory false)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id tencent/hunyuan-a13b-instruct)
    (canonical_slug tencent/hunyuan-a13b-instruct)
    (hugging_face_id tencent/Hunyuan-A13B-Instruct)
    (name "Tencent: Hunyuan A13B Instruct")
    (created 1751987664)
    (description "Hunyuan-A13B is a 13B active parameter Mixture-of-Experts (MoE) language model developed by Tencent, with a total parameter count of 80B and support for reasoning via Chain-of-Thought. It offers competitive benchmark...")
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
      (prompt "0.00000014")
      (completion "0.00000057")
    ))
    (top_provider (
      (context_length 131072)
      (max_completion_tokens 131072)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      frequency_penalty
      include_reasoning
      max_tokens
      reasoning
      response_format
      structured_outputs
      temperature
      top_k
      top_p
    ))
    (default_parameters ())
    (supported_voices null)
    (knowledge_cutoff 2025-03-31)
    (expiration_date null)
    (links (
      (details /api/v1/models/tencent/hunyuan-a13b-instruct/endpoints)
    ))
    (reasoning (
      (mandatory false)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId tencent/hunyuan-a13b-instruct)
  ))
)
