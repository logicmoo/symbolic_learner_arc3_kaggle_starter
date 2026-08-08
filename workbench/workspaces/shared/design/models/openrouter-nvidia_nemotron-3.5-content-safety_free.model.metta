(
  (kind model)
  (id openrouter-nvidia_nemotron-3.5-content-safety_free)
  (label "NVIDIA: Nemotron 3.5 Content Safety (free)")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model nvidia/nemotron-3.5-content-safety:free)
  (enabled true)
  (capabilities (
    (audio false)
    (code false)
    (functionCalling false)
    (json false)
    (jsonMode false)
    (local false)
    (multimodal true)
    (reasoning true)
    (text true)
    (tools false)
    (vision true)
  ))
  (limits (
    (contextWindow 128000)
    (maxOutputTokens 8192)
  ))
  (pricing (
    (prompt "0")
    (completion "0")
  ))
  (properties (
    (id nvidia/nemotron-3.5-content-safety:free)
    (canonical_slug nvidia/nemotron-3.5-content-safety-20260604)
    (hugging_face_id nvidia/Nemotron-3.5-Content-Safety)
    (name "NVIDIA: Nemotron 3.5 Content Safety (free)")
    (created 1780581864)
    (description "NVIDIA Nemotron 3.5 Content Safety is a compact 4B-parameter multimodal guardrail model from NVIDIA, fine-tuned from Google Gemma-3-4B. It moderates both inputs to and responses from LLMs and VLMs, accepting...")
    (context_length 128000)
    (architecture (
      (modality text+image->text)
      (input_modalities ([]
        text
        image
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Other)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0")
      (completion "0")
    ))
    (top_provider (
      (context_length 128000)
      (max_completion_tokens 8192)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      include_reasoning
      max_tokens
      reasoning
      seed
      temperature
      top_p
    ))
    (default_parameters (
      (temperature null)
      (top_p null)
      (top_k null)
      (frequency_penalty null)
      (presence_penalty null)
      (repetition_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links (
      (details /api/v1/models/nvidia/nemotron-3.5-content-safety-20260604/endpoints)
    ))
    (reasoning (
      (mandatory false)
      (default_enabled true)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id nvidia/nemotron-3.5-content-safety:free)
    (canonical_slug nvidia/nemotron-3.5-content-safety-20260604)
    (hugging_face_id nvidia/Nemotron-3.5-Content-Safety)
    (name "NVIDIA: Nemotron 3.5 Content Safety (free)")
    (created 1780581864)
    (description "NVIDIA Nemotron 3.5 Content Safety is a compact 4B-parameter multimodal guardrail model from NVIDIA, fine-tuned from Google Gemma-3-4B. It moderates both inputs to and responses from LLMs and VLMs, accepting...")
    (context_length 128000)
    (architecture (
      (modality text+image->text)
      (input_modalities ([]
        text
        image
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Other)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0")
      (completion "0")
    ))
    (top_provider (
      (context_length 128000)
      (max_completion_tokens 8192)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      include_reasoning
      max_tokens
      reasoning
      seed
      temperature
      top_p
    ))
    (default_parameters (
      (temperature null)
      (top_p null)
      (top_k null)
      (frequency_penalty null)
      (presence_penalty null)
      (repetition_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links (
      (details /api/v1/models/nvidia/nemotron-3.5-content-safety-20260604/endpoints)
    ))
    (reasoning (
      (mandatory false)
      (default_enabled true)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId nvidia/nemotron-3.5-content-safety:free)
  ))
)
