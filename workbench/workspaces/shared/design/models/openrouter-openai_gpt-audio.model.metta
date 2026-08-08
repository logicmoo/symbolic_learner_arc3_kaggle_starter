(
  (kind model)
  (id openrouter-openai_gpt-audio)
  (label "OpenAI: GPT Audio")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model openai/gpt-audio)
  (enabled true)
  (capabilities (
    (audio true)
    (code false)
    (functionCalling true)
    (json true)
    (jsonMode true)
    (local false)
    (multimodal true)
    (reasoning false)
    (text true)
    (tools true)
    (vision false)
  ))
  (limits (
    (contextWindow 128000)
    (maxOutputTokens 16384)
  ))
  (pricing (
    (prompt "0.0000025")
    (completion "0.00001")
    (audio "0.000032")
    (audio_output "0.000064")
  ))
  (properties (
    (id openai/gpt-audio)
    (canonical_slug openai/gpt-audio)
    (hugging_face_id "")
    (name "OpenAI: GPT Audio")
    (created 1768862569)
    (description "The gpt-audio model is OpenAI's first generally available audio model. The new snapshot features an upgraded decoder for more natural sounding voices and maintains better voice consistency. Audio is priced...")
    (context_length 128000)
    (architecture (
      (modality text+audio->text+audio)
      (input_modalities ([]
        text
        audio
      ))
      (output_modalities ([]
        text
        audio
      ))
      (tokenizer GPT)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.0000025")
      (completion "0.00001")
      (audio "0.000032")
      (audio_output "0.000064")
    ))
    (top_provider (
      (context_length 128000)
      (max_completion_tokens 16384)
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
      (details /api/v1/models/openai/gpt-audio/endpoints)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id openai/gpt-audio)
    (canonical_slug openai/gpt-audio)
    (hugging_face_id "")
    (name "OpenAI: GPT Audio")
    (created 1768862569)
    (description "The gpt-audio model is OpenAI's first generally available audio model. The new snapshot features an upgraded decoder for more natural sounding voices and maintains better voice consistency. Audio is priced...")
    (context_length 128000)
    (architecture (
      (modality text+audio->text+audio)
      (input_modalities ([]
        text
        audio
      ))
      (output_modalities ([]
        text
        audio
      ))
      (tokenizer GPT)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.0000025")
      (completion "0.00001")
      (audio "0.000032")
      (audio_output "0.000064")
    ))
    (top_provider (
      (context_length 128000)
      (max_completion_tokens 16384)
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
      (details /api/v1/models/openai/gpt-audio/endpoints)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId openai/gpt-audio)
  ))
)
