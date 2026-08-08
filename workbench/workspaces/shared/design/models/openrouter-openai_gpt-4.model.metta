(
  (kind model)
  (id openrouter-openai_gpt-4)
  (label "OpenAI: GPT-4")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model openai/gpt-4)
  (enabled true)
  (capabilities (
    (audio false)
    (code false)
    (functionCalling true)
    (json true)
    (jsonMode true)
    (local false)
    (multimodal false)
    (reasoning false)
    (text true)
    (tools true)
    (vision false)
  ))
  (limits (
    (contextWindow 8191)
    (maxOutputTokens 4096)
  ))
  (pricing (
    (prompt "0.00003")
    (completion "0.00006")
  ))
  (properties (
    (id openai/gpt-4)
    (canonical_slug openai/gpt-4)
    (hugging_face_id null)
    (name "OpenAI: GPT-4")
    (created 1685232000)
    (description "OpenAI's flagship model, GPT-4 is a large-scale multimodal language model capable of solving difficult problems with greater accuracy than previous models due to its broader general knowledge and advanced reasoning...")
    (context_length 8191)
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
      (prompt "0.00003")
      (completion "0.00006")
    ))
    (top_provider (
      (context_length 8191)
      (max_completion_tokens 4096)
      (is_moderated true)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      frequency_penalty
      logit_bias
      logprobs
      max_completion_tokens
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
    (knowledge_cutoff 2021-09-30)
    (expiration_date null)
    (links (
      (details /api/v1/models/openai/gpt-4/endpoints)
    ))
    (benchmarks (
      (design_arena ([]))
      (artificial_analysis (
        (intelligence_index null)
        (coding_index 13.1)
        (agentic_index null)
      ))
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id openai/gpt-4)
    (canonical_slug openai/gpt-4)
    (hugging_face_id null)
    (name "OpenAI: GPT-4")
    (created 1685232000)
    (description "OpenAI's flagship model, GPT-4 is a large-scale multimodal language model capable of solving difficult problems with greater accuracy than previous models due to its broader general knowledge and advanced reasoning...")
    (context_length 8191)
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
      (prompt "0.00003")
      (completion "0.00006")
    ))
    (top_provider (
      (context_length 8191)
      (max_completion_tokens 4096)
      (is_moderated true)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      frequency_penalty
      logit_bias
      logprobs
      max_completion_tokens
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
    (knowledge_cutoff 2021-09-30)
    (expiration_date null)
    (links (
      (details /api/v1/models/openai/gpt-4/endpoints)
    ))
    (benchmarks (
      (design_arena ([]))
      (artificial_analysis (
        (intelligence_index null)
        (coding_index 13.1)
        (agentic_index null)
      ))
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId openai/gpt-4)
  ))
)
