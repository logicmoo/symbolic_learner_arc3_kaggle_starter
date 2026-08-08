(
  (kind model)
  (id openrouter-openai_gpt-3.5-turbo-instruct)
  (label "OpenAI: GPT-3.5 Turbo Instruct")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model openai/gpt-3.5-turbo-instruct)
  (enabled true)
  (capabilities (
    (audio false)
    (code false)
    (functionCalling false)
    (json true)
    (jsonMode true)
    (local false)
    (multimodal false)
    (reasoning false)
    (text true)
    (tools false)
    (vision false)
  ))
  (limits (
    (contextWindow 4095)
    (maxOutputTokens 4096)
  ))
  (pricing (
    (prompt "0.0000015")
    (completion "0.000002")
  ))
  (properties (
    (id openai/gpt-3.5-turbo-instruct)
    (canonical_slug openai/gpt-3.5-turbo-instruct)
    (hugging_face_id null)
    (name "OpenAI: GPT-3.5 Turbo Instruct")
    (created 1695859200)
    (description "This model is a variant of GPT-3.5 Turbo tuned for instructional prompts and omitting chat-related optimizations. Training data: up to Sep 2021.")
    (context_length 4095)
    (architecture (
      (modality text->text)
      (input_modalities ([]
        text
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer GPT)
      (instruct_type chatml)
    ))
    (pricing (
      (prompt "0.0000015")
      (completion "0.000002")
    ))
    (top_provider (
      (context_length 4095)
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
      top_logprobs
      top_p
    ))
    (default_parameters ())
    (supported_voices null)
    (knowledge_cutoff 2021-09-30)
    (expiration_date null)
    (links (
      (details /api/v1/models/openai/gpt-3.5-turbo-instruct/endpoints)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id openai/gpt-3.5-turbo-instruct)
    (canonical_slug openai/gpt-3.5-turbo-instruct)
    (hugging_face_id null)
    (name "OpenAI: GPT-3.5 Turbo Instruct")
    (created 1695859200)
    (description "This model is a variant of GPT-3.5 Turbo tuned for instructional prompts and omitting chat-related optimizations. Training data: up to Sep 2021.")
    (context_length 4095)
    (architecture (
      (modality text->text)
      (input_modalities ([]
        text
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer GPT)
      (instruct_type chatml)
    ))
    (pricing (
      (prompt "0.0000015")
      (completion "0.000002")
    ))
    (top_provider (
      (context_length 4095)
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
      top_logprobs
      top_p
    ))
    (default_parameters ())
    (supported_voices null)
    (knowledge_cutoff 2021-09-30)
    (expiration_date null)
    (links (
      (details /api/v1/models/openai/gpt-3.5-turbo-instruct/endpoints)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId openai/gpt-3.5-turbo-instruct)
  ))
)
