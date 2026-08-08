(
  (kind model)
  (id openrouter-nvidia_nemotron-3-super-120b-a12b)
  (label "NVIDIA: Nemotron 3 Super")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model nvidia/nemotron-3-super-120b-a12b)
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
    (contextWindow 1000000)
    (maxOutputTokens 16384)
  ))
  (pricing (
    (prompt "0.000000085")
    (completion "0.0000004")
  ))
  (properties (
    (id nvidia/nemotron-3-super-120b-a12b)
    (canonical_slug nvidia/nemotron-3-super-120b-a12b-20230311)
    (hugging_face_id nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-FP8)
    (name "NVIDIA: Nemotron 3 Super")
    (created 1773245239)
    (description "NVIDIA Nemotron 3 Super is a 120B-parameter open hybrid MoE model, activating just 12B parameters for maximum compute efficiency and accuracy in complex multi-agent applications. Built on a hybrid Mamba-Transformer...")
    (context_length 1000000)
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
      (prompt "0.000000085")
      (completion "0.0000004")
    ))
    (top_provider (
      (context_length 262144)
      (max_completion_tokens 16384)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      frequency_penalty
      include_reasoning
      logit_bias
      logprobs
      max_tokens
      min_p
      presence_penalty
      reasoning
      reasoning_effort
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
      (temperature 1)
      (top_p 0.95)
      (top_k null)
      (frequency_penalty null)
      (presence_penalty null)
      (repetition_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links (
      (details /api/v1/models/nvidia/nemotron-3-super-120b-a12b-20230311/endpoints)
    ))
    (benchmarks (
      (design_arena ([]))
      (artificial_analysis (
        (intelligence_index 25.7)
        (coding_index 37.7)
        (agentic_index 8.8)
      ))
    ))
    (reasoning (
      (mandatory false)
      (default_enabled true)
      (supports_max_tokens true)
      (supported_efforts ([]
        medium
        low
      ))
      (default_effort medium)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id nvidia/nemotron-3-super-120b-a12b)
    (canonical_slug nvidia/nemotron-3-super-120b-a12b-20230311)
    (hugging_face_id nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-FP8)
    (name "NVIDIA: Nemotron 3 Super")
    (created 1773245239)
    (description "NVIDIA Nemotron 3 Super is a 120B-parameter open hybrid MoE model, activating just 12B parameters for maximum compute efficiency and accuracy in complex multi-agent applications. Built on a hybrid Mamba-Transformer...")
    (context_length 1000000)
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
      (prompt "0.000000085")
      (completion "0.0000004")
    ))
    (top_provider (
      (context_length 262144)
      (max_completion_tokens 16384)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      frequency_penalty
      include_reasoning
      logit_bias
      logprobs
      max_tokens
      min_p
      presence_penalty
      reasoning
      reasoning_effort
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
      (temperature 1)
      (top_p 0.95)
      (top_k null)
      (frequency_penalty null)
      (presence_penalty null)
      (repetition_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links (
      (details /api/v1/models/nvidia/nemotron-3-super-120b-a12b-20230311/endpoints)
    ))
    (benchmarks (
      (design_arena ([]))
      (artificial_analysis (
        (intelligence_index 25.7)
        (coding_index 37.7)
        (agentic_index 8.8)
      ))
    ))
    (reasoning (
      (mandatory false)
      (default_enabled true)
      (supports_max_tokens true)
      (supported_efforts ([]
        medium
        low
      ))
      (default_effort medium)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId nvidia/nemotron-3-super-120b-a12b)
  ))
)
