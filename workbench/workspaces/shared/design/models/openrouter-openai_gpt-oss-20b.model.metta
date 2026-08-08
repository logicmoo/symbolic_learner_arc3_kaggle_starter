(
  (kind model)
  (id openrouter-openai_gpt-oss-20b)
  (label "OpenAI: gpt-oss-20b")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model openai/gpt-oss-20b)
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
    (maxOutputTokens 131072)
  ))
  (pricing (
    (prompt "0.00000003")
    (completion "0.00000013")
    (input_cache_read "0.00000003")
  ))
  (properties (
    (id openai/gpt-oss-20b)
    (canonical_slug openai/gpt-oss-20b)
    (hugging_face_id openai/gpt-oss-20b)
    (name "OpenAI: gpt-oss-20b")
    (created 1754414229)
    (description "gpt-oss-20b is an open-weight 21B parameter model released by OpenAI under the Apache 2.0 license. It uses a Mixture-of-Experts (MoE) architecture with 3.6B active parameters per forward pass, optimized for...")
    (context_length 131072)
    (architecture (
      (modality text->text)
      (input_modalities ([]
        text
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer GPT)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.00000003")
      (completion "0.00000013")
      (input_cache_read "0.00000003")
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
      (temperature null)
      (top_p null)
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff 2024-06-30)
    (expiration_date null)
    (links (
      (details /api/v1/models/openai/gpt-oss-20b/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena models)
          (category dataviz)
          (elo 961)
          (win_rate 39.7)
          (rank 102)
        )
        (
          (arena models)
          (category website)
          (elo 875)
          (win_rate 27.9)
          (rank 118)
        )
      ))
      (artificial_analysis (
        (intelligence_index 15.2)
        (coding_index 20.7)
        (agentic_index 3.1)
      ))
    ))
    (reasoning (
      (mandatory true)
      (supported_efforts ([]
        high
        medium
        low
      ))
      (default_effort medium)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id openai/gpt-oss-20b)
    (canonical_slug openai/gpt-oss-20b)
    (hugging_face_id openai/gpt-oss-20b)
    (name "OpenAI: gpt-oss-20b")
    (created 1754414229)
    (description "gpt-oss-20b is an open-weight 21B parameter model released by OpenAI under the Apache 2.0 license. It uses a Mixture-of-Experts (MoE) architecture with 3.6B active parameters per forward pass, optimized for...")
    (context_length 131072)
    (architecture (
      (modality text->text)
      (input_modalities ([]
        text
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer GPT)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.00000003")
      (completion "0.00000013")
      (input_cache_read "0.00000003")
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
      (temperature null)
      (top_p null)
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff 2024-06-30)
    (expiration_date null)
    (links (
      (details /api/v1/models/openai/gpt-oss-20b/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena models)
          (category dataviz)
          (elo 961)
          (win_rate 39.7)
          (rank 102)
        )
        (
          (arena models)
          (category website)
          (elo 875)
          (win_rate 27.9)
          (rank 118)
        )
      ))
      (artificial_analysis (
        (intelligence_index 15.2)
        (coding_index 20.7)
        (agentic_index 3.1)
      ))
    ))
    (reasoning (
      (mandatory true)
      (supported_efforts ([]
        high
        medium
        low
      ))
      (default_effort medium)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId openai/gpt-oss-20b)
  ))
)
