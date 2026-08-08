(
  (kind model)
  (id openrouter-openai_gpt-chat-latest)
  (label "OpenAI: GPT Chat Latest")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model openai/gpt-chat-latest)
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
    (contextWindow 400000)
    (maxOutputTokens 128000)
  ))
  (pricing (
    (prompt "0.000005")
    (completion "0.00003")
    (web_search "0.01")
    (input_cache_read "0.0000005")
  ))
  (properties (
    (id openai/gpt-chat-latest)
    (canonical_slug openai/gpt-chat-latest-20260505)
    (hugging_face_id null)
    (name "OpenAI: GPT Chat Latest")
    (created 1778000212)
    (description "GPT Chat Latest points to OpenAI's stable API alias `chat-latest` that always resolves to the latest Instant chat model used in ChatGPT. As OpenAI rolls out new Instant model updates...")
    (context_length 400000)
    (architecture (
      (modality text+image+file->text)
      (input_modalities ([]
        text
        image
        file
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer GPT)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.000005")
      (completion "0.00003")
      (web_search "0.01")
      (input_cache_read "0.0000005")
    ))
    (top_provider (
      (context_length 400000)
      (max_completion_tokens 128000)
      (is_moderated true)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      max_tokens
      response_format
      seed
      structured_outputs
      tool_choice
      tools
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
      (details /api/v1/models/openai/gpt-chat-latest-20260505/endpoints)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id openai/gpt-chat-latest)
    (canonical_slug openai/gpt-chat-latest-20260505)
    (hugging_face_id null)
    (name "OpenAI: GPT Chat Latest")
    (created 1778000212)
    (description "GPT Chat Latest points to OpenAI's stable API alias `chat-latest` that always resolves to the latest Instant chat model used in ChatGPT. As OpenAI rolls out new Instant model updates...")
    (context_length 400000)
    (architecture (
      (modality text+image+file->text)
      (input_modalities ([]
        text
        image
        file
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer GPT)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.000005")
      (completion "0.00003")
      (web_search "0.01")
      (input_cache_read "0.0000005")
    ))
    (top_provider (
      (context_length 400000)
      (max_completion_tokens 128000)
      (is_moderated true)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      max_tokens
      response_format
      seed
      structured_outputs
      tool_choice
      tools
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
      (details /api/v1/models/openai/gpt-chat-latest-20260505/endpoints)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId openai/gpt-chat-latest)
  ))
)
