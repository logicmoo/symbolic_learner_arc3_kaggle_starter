({}
  (kind model)
  (id openrouter-nvidia_nemotron-3-super-120b-a12b_free)
  (label "NVIDIA: Nemotron 3 Super (free)")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model nvidia/nemotron-3-super-120b-a12b:free)
  (enabled true)
  (capabilities ({}
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
  (limits ({}
    (contextWindow 262144)
    (maxOutputTokens 262144)
  ))
  (pricing ({}
    (prompt "0")
    (completion "0")
  ))
  (properties ({}
    (id nvidia/nemotron-3-super-120b-a12b:free)
    (canonical_slug nvidia/nemotron-3-super-120b-a12b-20230311)
    (hugging_face_id nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-FP8)
    (name "NVIDIA: Nemotron 3 Super (free)")
    (created 1773245239)
    (description "NVIDIA Nemotron 3 Super is a 120B-parameter open hybrid MoE model, activating just 12B parameters for maximum compute efficiency and accuracy in complex multi-agent applications. Built on a hybrid Mamba-Transformer...")
    (context_length 262144)
    (architecture ({}
      (modality text->text)
      (input_modalities (
        text
      ))
      (output_modalities (
        text
      ))
      (tokenizer Other)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0")
      (completion "0")
    ))
    (top_provider ({}
      (context_length 262144)
      (max_completion_tokens 262144)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      include_reasoning
      max_tokens
      reasoning
      reasoning_effort
      response_format
      seed
      structured_outputs
      temperature
      tool_choice
      tools
      top_p
    ))
    (default_parameters ({}
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
    (links ({}
      (details /api/v1/models/nvidia/nemotron-3-super-120b-a12b-20230311/endpoints)
    ))
    (benchmarks ({}
      (design_arena ())
      (artificial_analysis ({}
        (intelligence_index 25.7)
        (coding_index 37.7)
        (agentic_index 8.8)
      ))
    ))
    (reasoning ({}
      (mandatory false)
      (default_enabled true)
      (supports_max_tokens true)
      (supported_efforts (
        medium
        low
      ))
      (default_effort medium)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id nvidia/nemotron-3-super-120b-a12b:free)
    (canonical_slug nvidia/nemotron-3-super-120b-a12b-20230311)
    (hugging_face_id nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-FP8)
    (name "NVIDIA: Nemotron 3 Super (free)")
    (created 1773245239)
    (description "NVIDIA Nemotron 3 Super is a 120B-parameter open hybrid MoE model, activating just 12B parameters for maximum compute efficiency and accuracy in complex multi-agent applications. Built on a hybrid Mamba-Transformer...")
    (context_length 262144)
    (architecture ({}
      (modality text->text)
      (input_modalities (
        text
      ))
      (output_modalities (
        text
      ))
      (tokenizer Other)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0")
      (completion "0")
    ))
    (top_provider ({}
      (context_length 262144)
      (max_completion_tokens 262144)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      include_reasoning
      max_tokens
      reasoning
      reasoning_effort
      response_format
      seed
      structured_outputs
      temperature
      tool_choice
      tools
      top_p
    ))
    (default_parameters ({}
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
    (links ({}
      (details /api/v1/models/nvidia/nemotron-3-super-120b-a12b-20230311/endpoints)
    ))
    (benchmarks ({}
      (design_arena ())
      (artificial_analysis ({}
        (intelligence_index 25.7)
        (coding_index 37.7)
        (agentic_index 8.8)
      ))
    ))
    (reasoning ({}
      (mandatory false)
      (default_enabled true)
      (supports_max_tokens true)
      (supported_efforts (
        medium
        low
      ))
      (default_effort medium)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId nvidia/nemotron-3-super-120b-a12b:free)
  ))
)
