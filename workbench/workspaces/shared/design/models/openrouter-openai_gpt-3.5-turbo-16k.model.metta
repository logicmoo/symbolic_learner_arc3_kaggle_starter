({}
  (kind model)
  (id openrouter-openai_gpt-3.5-turbo-16k)
  (label "OpenAI: GPT-3.5 Turbo 16k")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model openai/gpt-3.5-turbo-16k)
  (enabled true)
  (capabilities ({}
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
  (limits ({}
    (contextWindow 16385)
    (maxOutputTokens 4096)
  ))
  (pricing ({}
    (prompt "0.000003")
    (completion "0.000004")
  ))
  (properties ({}
    (id openai/gpt-3.5-turbo-16k)
    (canonical_slug openai/gpt-3.5-turbo-16k)
    (hugging_face_id null)
    (name "OpenAI: GPT-3.5 Turbo 16k")
    (created 1693180800)
    (description "This model offers four times the context length of gpt-3.5-turbo, allowing it to support approximately 20 pages of text in a single request at a higher cost. Training data: up...")
    (context_length 16385)
    (architecture ({}
      (modality text->text)
      (input_modalities (
        text
      ))
      (output_modalities (
        text
      ))
      (tokenizer GPT)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.000003")
      (completion "0.000004")
    ))
    (top_provider ({}
      (context_length 16385)
      (max_completion_tokens 4096)
      (is_moderated true)
    ))
    (per_request_limits null)
    (supported_parameters (
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
    (default_parameters ({}))
    (supported_voices null)
    (knowledge_cutoff 2021-09-30)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/openai/gpt-3.5-turbo-16k/endpoints)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id openai/gpt-3.5-turbo-16k)
    (canonical_slug openai/gpt-3.5-turbo-16k)
    (hugging_face_id null)
    (name "OpenAI: GPT-3.5 Turbo 16k")
    (created 1693180800)
    (description "This model offers four times the context length of gpt-3.5-turbo, allowing it to support approximately 20 pages of text in a single request at a higher cost. Training data: up...")
    (context_length 16385)
    (architecture ({}
      (modality text->text)
      (input_modalities (
        text
      ))
      (output_modalities (
        text
      ))
      (tokenizer GPT)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.000003")
      (completion "0.000004")
    ))
    (top_provider ({}
      (context_length 16385)
      (max_completion_tokens 4096)
      (is_moderated true)
    ))
    (per_request_limits null)
    (supported_parameters (
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
    (default_parameters ({}))
    (supported_voices null)
    (knowledge_cutoff 2021-09-30)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/openai/gpt-3.5-turbo-16k/endpoints)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId openai/gpt-3.5-turbo-16k)
  ))
)
