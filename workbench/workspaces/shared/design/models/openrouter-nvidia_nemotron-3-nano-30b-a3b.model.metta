({}
  (kind model)
  (id openrouter-nvidia_nemotron-3-nano-30b-a3b)
  (label "NVIDIA: Nemotron 3 Nano 30B A3B")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model nvidia/nemotron-3-nano-30b-a3b)
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
    (prompt "0.00000005")
    (completion "0.0000002")
    (input_cache_read "0.00000003")
  ))
  (properties ({}
    (id nvidia/nemotron-3-nano-30b-a3b)
    (canonical_slug nvidia/nemotron-3-nano-30b-a3b)
    (hugging_face_id nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16)
    (name "NVIDIA: Nemotron 3 Nano 30B A3B")
    (created 1765731275)
    (description "NVIDIA Nemotron 3 Nano 30B A3B is a small language MoE model with highest compute efficiency and accuracy for developers to build specialized agentic AI systems. The model is fully...")
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
      (prompt "0.00000005")
      (completion "0.0000002")
      (input_cache_read "0.00000003")
    ))
    (top_provider ({}
      (context_length 262144)
      (max_completion_tokens 262144)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      include_reasoning
      logit_bias
      logprobs
      max_tokens
      min_p
      presence_penalty
      reasoning
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
    (default_parameters ({}
      (temperature null)
      (top_p null)
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/nvidia/nemotron-3-nano-30b-a3b/endpoints)
    ))
    (benchmarks ({}
      (design_arena ())
      (artificial_analysis ({}
        (intelligence_index 14.5)
        (coding_index 14.4)
        (agentic_index 2)
      ))
    ))
    (reasoning ({}
      (mandatory false)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id nvidia/nemotron-3-nano-30b-a3b)
    (canonical_slug nvidia/nemotron-3-nano-30b-a3b)
    (hugging_face_id nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16)
    (name "NVIDIA: Nemotron 3 Nano 30B A3B")
    (created 1765731275)
    (description "NVIDIA Nemotron 3 Nano 30B A3B is a small language MoE model with highest compute efficiency and accuracy for developers to build specialized agentic AI systems. The model is fully...")
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
      (prompt "0.00000005")
      (completion "0.0000002")
      (input_cache_read "0.00000003")
    ))
    (top_provider ({}
      (context_length 262144)
      (max_completion_tokens 262144)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      include_reasoning
      logit_bias
      logprobs
      max_tokens
      min_p
      presence_penalty
      reasoning
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
    (default_parameters ({}
      (temperature null)
      (top_p null)
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/nvidia/nemotron-3-nano-30b-a3b/endpoints)
    ))
    (benchmarks ({}
      (design_arena ())
      (artificial_analysis ({}
        (intelligence_index 14.5)
        (coding_index 14.4)
        (agentic_index 2)
      ))
    ))
    (reasoning ({}
      (mandatory false)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId nvidia/nemotron-3-nano-30b-a3b)
  ))
)
