(
  (kind model)
  (id openrouter-openai_gpt-4-turbo)
  (label "OpenAI: GPT-4 Turbo")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model openai/gpt-4-turbo)
  (enabled true)
  (capabilities (
    (audio false)
    (code false)
    (functionCalling true)
    (json true)
    (jsonMode true)
    (local false)
    (multimodal true)
    (reasoning false)
    (text true)
    (tools true)
    (vision true)
  ))
  (limits (
    (contextWindow 128000)
    (maxOutputTokens 4096)
  ))
  (pricing (
    (prompt "0.00001")
    (completion "0.00003")
  ))
  (properties (
    (id openai/gpt-4-turbo)
    (canonical_slug openai/gpt-4-turbo)
    (hugging_face_id null)
    (name "OpenAI: GPT-4 Turbo")
    (created 1712620800)
    (description "The latest GPT-4 Turbo model with vision capabilities. Vision requests can now use JSON mode and function calling.\n\nTraining data: up to December 2023.")
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
      (tokenizer GPT)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.00001")
      (completion "0.00003")
    ))
    (top_provider (
      (context_length 128000)
      (max_completion_tokens 4096)
      (is_moderated true)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      frequency_penalty
      logit_bias
      logprobs
      max_tokens
      presence_penalty
      response_format
      seed
      stop
      structured_outputs
      temperature
      tool_choice
      tools
      top_logprobs
      top_p
    ))
    (default_parameters ())
    (supported_voices null)
    (knowledge_cutoff 2023-12-31)
    (expiration_date null)
    (links (
      (details /api/v1/models/openai/gpt-4-turbo/endpoints)
    ))
    (benchmarks (
      (design_arena ([]))
      (artificial_analysis (
        (intelligence_index null)
        (coding_index 21.5)
        (agentic_index null)
      ))
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id openai/gpt-4-turbo)
    (canonical_slug openai/gpt-4-turbo)
    (hugging_face_id null)
    (name "OpenAI: GPT-4 Turbo")
    (created 1712620800)
    (description "The latest GPT-4 Turbo model with vision capabilities. Vision requests can now use JSON mode and function calling.\n\nTraining data: up to December 2023.")
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
      (tokenizer GPT)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.00001")
      (completion "0.00003")
    ))
    (top_provider (
      (context_length 128000)
      (max_completion_tokens 4096)
      (is_moderated true)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      frequency_penalty
      logit_bias
      logprobs
      max_tokens
      presence_penalty
      response_format
      seed
      stop
      structured_outputs
      temperature
      tool_choice
      tools
      top_logprobs
      top_p
    ))
    (default_parameters ())
    (supported_voices null)
    (knowledge_cutoff 2023-12-31)
    (expiration_date null)
    (links (
      (details /api/v1/models/openai/gpt-4-turbo/endpoints)
    ))
    (benchmarks (
      (design_arena ([]))
      (artificial_analysis (
        (intelligence_index null)
        (coding_index 21.5)
        (agentic_index null)
      ))
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId openai/gpt-4-turbo)
  ))
)
