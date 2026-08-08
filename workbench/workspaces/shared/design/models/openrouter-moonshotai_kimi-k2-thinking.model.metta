(
  (kind model)
  (id openrouter-moonshotai_kimi-k2-thinking)
  (label "MoonshotAI: Kimi K2 Thinking")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model moonshotai/kimi-k2-thinking)
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
    (contextWindow 262144)
    (maxOutputTokens 100352)
  ))
  (pricing (
    (prompt "0.0000006")
    (completion "0.0000025")
    (input_cache_read "0.00000015")
  ))
  (properties (
    (id moonshotai/kimi-k2-thinking)
    (canonical_slug moonshotai/kimi-k2-thinking-20251106)
    (hugging_face_id moonshotai/Kimi-K2-Thinking)
    (name "MoonshotAI: Kimi K2 Thinking")
    (created 1762440622)
    (description "Kimi K2 Thinking is Moonshot AI’s most advanced open reasoning model to date, extending the K2 series into agentic, long-horizon reasoning. Built on the trillion-parameter Mixture-of-Experts (MoE) architecture introduced in...")
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
      (prompt "0.0000006")
      (completion "0.0000025")
      (input_cache_read "0.00000015")
    ))
    (top_provider (
      (context_length 262144)
      (max_completion_tokens 100352)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      frequency_penalty
      include_reasoning
      logprobs
      max_tokens
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
      (details /api/v1/models/moonshotai/kimi-k2-thinking-20251106/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena models)
          (category website)
          (elo 1135)
          (win_rate 48.8)
          (rank 82)
        )
      ))
      (artificial_analysis (
        (intelligence_index 17.2)
        (coding_index 21)
        (agentic_index 1.8)
      ))
    ))
    (reasoning (
      (mandatory true)
      (default_enabled true)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id moonshotai/kimi-k2-thinking)
    (canonical_slug moonshotai/kimi-k2-thinking-20251106)
    (hugging_face_id moonshotai/Kimi-K2-Thinking)
    (name "MoonshotAI: Kimi K2 Thinking")
    (created 1762440622)
    (description "Kimi K2 Thinking is Moonshot AI’s most advanced open reasoning model to date, extending the K2 series into agentic, long-horizon reasoning. Built on the trillion-parameter Mixture-of-Experts (MoE) architecture introduced in...")
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
      (prompt "0.0000006")
      (completion "0.0000025")
      (input_cache_read "0.00000015")
    ))
    (top_provider (
      (context_length 262144)
      (max_completion_tokens 100352)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      frequency_penalty
      include_reasoning
      logprobs
      max_tokens
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
      (details /api/v1/models/moonshotai/kimi-k2-thinking-20251106/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena models)
          (category website)
          (elo 1135)
          (win_rate 48.8)
          (rank 82)
        )
      ))
      (artificial_analysis (
        (intelligence_index 17.2)
        (coding_index 21)
        (agentic_index 1.8)
      ))
    ))
    (reasoning (
      (mandatory true)
      (default_enabled true)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId moonshotai/kimi-k2-thinking)
  ))
)
