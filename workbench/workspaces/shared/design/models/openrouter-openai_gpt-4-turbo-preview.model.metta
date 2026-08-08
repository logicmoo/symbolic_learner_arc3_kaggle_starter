({}
  (kind model)
  (id openrouter-openai_gpt-4-turbo-preview)
  (label "OpenAI: GPT-4 Turbo Preview")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model openai/gpt-4-turbo-preview)
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
    (contextWindow 128000)
    (maxOutputTokens 4096)
  ))
  (pricing ({}
    (prompt "0.00001")
    (completion "0.00003")
  ))
  (properties ({}
    (id openai/gpt-4-turbo-preview)
    (canonical_slug openai/gpt-4-turbo-preview)
    (hugging_face_id null)
    (name "OpenAI: GPT-4 Turbo Preview")
    (created 1706140800)
    (description "The preview GPT-4 model with improved instruction following, JSON mode, reproducible outputs, parallel function calling, and more. Training data: up to Dec 2023. **Note:** heavily rate limited by OpenAI while...")
    (context_length 128000)
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
      (prompt "0.00001")
      (completion "0.00003")
    ))
    (top_provider ({}
      (context_length 128000)
      (max_completion_tokens 4096)
      (is_moderated true)
    ))
    (per_request_limits null)
    (supported_parameters (
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
    (default_parameters ({}))
    (supported_voices null)
    (knowledge_cutoff 2023-12-31)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/openai/gpt-4-turbo-preview/endpoints)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id openai/gpt-4-turbo-preview)
    (canonical_slug openai/gpt-4-turbo-preview)
    (hugging_face_id null)
    (name "OpenAI: GPT-4 Turbo Preview")
    (created 1706140800)
    (description "The preview GPT-4 model with improved instruction following, JSON mode, reproducible outputs, parallel function calling, and more. Training data: up to Dec 2023. **Note:** heavily rate limited by OpenAI while...")
    (context_length 128000)
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
      (prompt "0.00001")
      (completion "0.00003")
    ))
    (top_provider ({}
      (context_length 128000)
      (max_completion_tokens 4096)
      (is_moderated true)
    ))
    (per_request_limits null)
    (supported_parameters (
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
    (default_parameters ({}))
    (supported_voices null)
    (knowledge_cutoff 2023-12-31)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/openai/gpt-4-turbo-preview/endpoints)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId openai/gpt-4-turbo-preview)
  ))
)
