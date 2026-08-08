({}
  (kind model)
  (id openrouter-openai_gpt-audio-mini)
  (label "OpenAI: GPT Audio Mini")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model openai/gpt-audio-mini)
  (enabled true)
  (capabilities ({}
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
  (limits ({}
    (contextWindow 128000)
    (maxOutputTokens 16384)
  ))
  (pricing ({}
    (prompt "0.0000006")
    (completion "0.0000024")
    (audio "0.0000006")
    (audio_output "0.0000024")
  ))
  (properties ({}
    (id openai/gpt-audio-mini)
    (canonical_slug openai/gpt-audio-mini)
    (hugging_face_id "")
    (name "OpenAI: GPT Audio Mini")
    (created 1768859419)
    (description "A cost-efficient version of GPT Audio. The new snapshot features an upgraded decoder for more natural sounding voices and maintains better voice consistency. Input is priced at $0.60 per million...")
    (context_length 128000)
    (architecture ({}
      (modality text+audio->text+audio)
      (input_modalities (
        text
        audio
      ))
      (output_modalities (
        text
        audio
      ))
      (tokenizer GPT)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.0000006")
      (completion "0.0000024")
      (audio "0.0000006")
      (audio_output "0.0000024")
    ))
    (top_provider ({}
      (context_length 128000)
      (max_completion_tokens 16384)
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
    (default_parameters ({}
      (temperature null)
      (top_p null)
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/openai/gpt-audio-mini/endpoints)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id openai/gpt-audio-mini)
    (canonical_slug openai/gpt-audio-mini)
    (hugging_face_id "")
    (name "OpenAI: GPT Audio Mini")
    (created 1768859419)
    (description "A cost-efficient version of GPT Audio. The new snapshot features an upgraded decoder for more natural sounding voices and maintains better voice consistency. Input is priced at $0.60 per million...")
    (context_length 128000)
    (architecture ({}
      (modality text+audio->text+audio)
      (input_modalities (
        text
        audio
      ))
      (output_modalities (
        text
        audio
      ))
      (tokenizer GPT)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.0000006")
      (completion "0.0000024")
      (audio "0.0000006")
      (audio_output "0.0000024")
    ))
    (top_provider ({}
      (context_length 128000)
      (max_completion_tokens 16384)
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
    (default_parameters ({}
      (temperature null)
      (top_p null)
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/openai/gpt-audio-mini/endpoints)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId openai/gpt-audio-mini)
  ))
)
