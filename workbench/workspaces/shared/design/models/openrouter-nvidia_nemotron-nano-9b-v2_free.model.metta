(
  (kind model)
  (id openrouter-nvidia_nemotron-nano-9b-v2_free)
  (label "NVIDIA: Nemotron Nano 9B V2 (free)")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model nvidia/nemotron-nano-9b-v2:free)
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
    (contextWindow 128000)
    (maxOutputTokens null)
  ))
  (pricing (
    (prompt "0")
    (completion "0")
  ))
  (properties (
    (id nvidia/nemotron-nano-9b-v2:free)
    (canonical_slug nvidia/nemotron-nano-9b-v2)
    (hugging_face_id nvidia/NVIDIA-Nemotron-Nano-9B-v2)
    (name "NVIDIA: Nemotron Nano 9B V2 (free)")
    (created 1757106807)
    (description "NVIDIA-Nemotron-Nano-9B-v2 is a large language model (LLM) trained from scratch by NVIDIA, and designed as a unified model for both reasoning and non-reasoning tasks. It responds to user queries and...")
    (context_length 128000)
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
      (prompt "0")
      (completion "0")
    ))
    (top_provider (
      (context_length 128000)
      (max_completion_tokens null)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      include_reasoning
      max_tokens
      reasoning
      response_format
      seed
      structured_outputs
      temperature
      tool_choice
      tools
      top_p
    ))
    (default_parameters (
      (temperature null)
      (top_p null)
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff 2025-03-31)
    (expiration_date null)
    (links (
      (details /api/v1/models/nvidia/nemotron-nano-9b-v2/endpoints)
    ))
    (reasoning (
      (mandatory false)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id nvidia/nemotron-nano-9b-v2:free)
    (canonical_slug nvidia/nemotron-nano-9b-v2)
    (hugging_face_id nvidia/NVIDIA-Nemotron-Nano-9B-v2)
    (name "NVIDIA: Nemotron Nano 9B V2 (free)")
    (created 1757106807)
    (description "NVIDIA-Nemotron-Nano-9B-v2 is a large language model (LLM) trained from scratch by NVIDIA, and designed as a unified model for both reasoning and non-reasoning tasks. It responds to user queries and...")
    (context_length 128000)
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
      (prompt "0")
      (completion "0")
    ))
    (top_provider (
      (context_length 128000)
      (max_completion_tokens null)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      include_reasoning
      max_tokens
      reasoning
      response_format
      seed
      structured_outputs
      temperature
      tool_choice
      tools
      top_p
    ))
    (default_parameters (
      (temperature null)
      (top_p null)
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff 2025-03-31)
    (expiration_date null)
    (links (
      (details /api/v1/models/nvidia/nemotron-nano-9b-v2/endpoints)
    ))
    (reasoning (
      (mandatory false)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId nvidia/nemotron-nano-9b-v2:free)
  ))
)
