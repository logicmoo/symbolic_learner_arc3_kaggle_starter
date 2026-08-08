(
  (kind model)
  (id openrouter-inclusionai_ling-3.0-flash)
  (label Ling-3.0-flash)
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model inclusionai/ling-3.0-flash)
  (enabled true)
  (capabilities (
    (audio false)
    (code false)
    (functionCalling true)
    (json false)
    (jsonMode false)
    (local false)
    (multimodal false)
    (reasoning true)
    (text true)
    (tools true)
    (vision false)
  ))
  (limits (
    (contextWindow 262144)
    (maxOutputTokens 32768)
  ))
  (pricing (
    (prompt "0.000000021")
    (completion "0.000000063")
    (input_cache_read "0.0000000042")
  ))
  (properties (
    (id inclusionai/ling-3.0-flash)
    (canonical_slug inclusionai/ling-3.0-flash-20260723)
    (hugging_face_id inclusionAI/Ling-3.0-flash)
    (name Ling-3.0-flash)
    (created 1784818580)
    (description "*Ling-3.0-flash* is a *124B-parameter Mixture-of-Experts (MoE) model*, with approximately *5.1B parameters activated per token*. The model is designed with *token efficiency and production-scale agentic inference* as key priorities, enabling developers...")
    (context_length 262144)
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
      (prompt "0.000000021")
      (completion "0.000000063")
      (input_cache_read "0.0000000042")
    ))
    (top_provider (
      (context_length 262144)
      (max_completion_tokens 32768)
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
      repetition_penalty
      seed
      stop
      temperature
      tool_choice
      tools
      top_k
      top_logprobs
      top_p
    ))
    (default_parameters ())
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links (
      (details /api/v1/models/inclusionai/ling-3.0-flash-20260723/endpoints)
    ))
    (benchmarks (
      (design_arena ([]))
      (artificial_analysis (
        (intelligence_index 37.8)
        (coding_index 50.6)
        (agentic_index 29.3)
      ))
    ))
    (reasoning (
      (mandatory false)
      (default_enabled true)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id inclusionai/ling-3.0-flash)
    (canonical_slug inclusionai/ling-3.0-flash-20260723)
    (hugging_face_id inclusionAI/Ling-3.0-flash)
    (name Ling-3.0-flash)
    (created 1784818580)
    (description "*Ling-3.0-flash* is a *124B-parameter Mixture-of-Experts (MoE) model*, with approximately *5.1B parameters activated per token*. The model is designed with *token efficiency and production-scale agentic inference* as key priorities, enabling developers...")
    (context_length 262144)
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
      (prompt "0.000000021")
      (completion "0.000000063")
      (input_cache_read "0.0000000042")
    ))
    (top_provider (
      (context_length 262144)
      (max_completion_tokens 32768)
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
      repetition_penalty
      seed
      stop
      temperature
      tool_choice
      tools
      top_k
      top_logprobs
      top_p
    ))
    (default_parameters ())
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links (
      (details /api/v1/models/inclusionai/ling-3.0-flash-20260723/endpoints)
    ))
    (benchmarks (
      (design_arena ([]))
      (artificial_analysis (
        (intelligence_index 37.8)
        (coding_index 50.6)
        (agentic_index 29.3)
      ))
    ))
    (reasoning (
      (mandatory false)
      (default_enabled true)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId inclusionai/ling-3.0-flash)
  ))
)
