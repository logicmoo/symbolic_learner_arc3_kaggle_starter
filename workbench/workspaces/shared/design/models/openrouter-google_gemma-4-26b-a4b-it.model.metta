(
  (kind model)
  (id openrouter-google_gemma-4-26b-a4b-it)
  (label "Google: Gemma 4 26B A4B ")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model google/gemma-4-26b-a4b-it)
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
    (contextWindow 262144)
    (maxOutputTokens 16384)
  ))
  (pricing (
    (prompt "0.00000007")
    (completion "0.00000034")
  ))
  (properties (
    (id google/gemma-4-26b-a4b-it)
    (canonical_slug google/gemma-4-26b-a4b-it-20260403)
    (hugging_face_id google/gemma-4-26B-A4B-it)
    (name "Google: Gemma 4 26B A4B ")
    (created 1775227989)
    (description "Gemma 4 26B A4B IT is an instruction-tuned Mixture-of-Experts (MoE) model from Google DeepMind. Despite 25.2B total parameters, only 3.8B activate per token during inference — delivering near-31B quality at...")
    (context_length 262144)
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
      (tokenizer Gemma)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.00000007")
      (completion "0.00000034")
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
      (top_k 64)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links (
      (details /api/v1/models/google/gemma-4-26b-a4b-it-20260403/endpoints)
    ))
    (benchmarks (
      (design_arena ([]))
      (artificial_analysis (
        (intelligence_index 26.1)
        (coding_index 39.3)
        (agentic_index 11)
      ))
    ))
    (reasoning (
      (mandatory false)
      (default_enabled false)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id google/gemma-4-26b-a4b-it)
    (canonical_slug google/gemma-4-26b-a4b-it-20260403)
    (hugging_face_id google/gemma-4-26B-A4B-it)
    (name "Google: Gemma 4 26B A4B ")
    (created 1775227989)
    (description "Gemma 4 26B A4B IT is an instruction-tuned Mixture-of-Experts (MoE) model from Google DeepMind. Despite 25.2B total parameters, only 3.8B activate per token during inference — delivering near-31B quality at...")
    (context_length 262144)
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
      (tokenizer Gemma)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.00000007")
      (completion "0.00000034")
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
      (top_k 64)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links (
      (details /api/v1/models/google/gemma-4-26b-a4b-it-20260403/endpoints)
    ))
    (benchmarks (
      (design_arena ([]))
      (artificial_analysis (
        (intelligence_index 26.1)
        (coding_index 39.3)
        (agentic_index 11)
      ))
    ))
    (reasoning (
      (mandatory false)
      (default_enabled false)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId google/gemma-4-26b-a4b-it)
  ))
)
