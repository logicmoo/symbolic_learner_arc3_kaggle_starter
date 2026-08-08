(
  (kind model)
  (id openrouter-openai_gpt-5.4-image-2)
  (label "OpenAI: GPT-5.4 Image 2")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model openai/gpt-5.4-image-2)
  (enabled true)
  (capabilities (
    (audio false)
    (code false)
    (functionCalling false)
    (json true)
    (jsonMode true)
    (local false)
    (multimodal true)
    (reasoning true)
    (text true)
    (tools false)
    (vision true)
  ))
  (limits (
    (contextWindow 272000)
    (maxOutputTokens 128000)
  ))
  (pricing (
    (prompt "0.000008")
    (completion "0.000015")
    (image_output "0.00003")
    (web_search "0.01")
    (input_cache_read "0.000002")
  ))
  (properties (
    (id openai/gpt-5.4-image-2)
    (canonical_slug openai/gpt-5.4-image-2-20260421)
    (hugging_face_id "")
    (name "OpenAI: GPT-5.4 Image 2")
    (created 1776797528)
    (description "[GPT-5.4](https://openrouter.ai/openai/gpt-5.4) Image 2 combines OpenAI's GPT-5.4 model with state-of-the-art image generation capabilities from GPT Image 2. It enables rich multimodal workflows, allowing users to seamlessly move between reasoning, coding, and...")
    (context_length 272000)
    (architecture (
      (modality text+image+file->text+image)
      (input_modalities ([]
        image
        text
        file
      ))
      (output_modalities ([]
        image
        text
      ))
      (tokenizer GPT)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.000008")
      (completion "0.000015")
      (image_output "0.00003")
      (web_search "0.01")
      (input_cache_read "0.000002")
    ))
    (top_provider (
      (context_length 272000)
      (max_completion_tokens 128000)
      (is_moderated true)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      frequency_penalty
      include_reasoning
      logit_bias
      logprobs
      max_tokens
      presence_penalty
      reasoning
      reasoning_effort
      response_format
      seed
      stop
      structured_outputs
      top_logprobs
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
      (details /api/v1/models/openai/gpt-5.4-image-2-20260421/endpoints)
    ))
    (reasoning (
      (mandatory false)
      (default_enabled false)
      (supported_efforts ([]
        xhigh
        high
        medium
        low
        none
      ))
      (default_effort medium)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id openai/gpt-5.4-image-2)
    (canonical_slug openai/gpt-5.4-image-2-20260421)
    (hugging_face_id "")
    (name "OpenAI: GPT-5.4 Image 2")
    (created 1776797528)
    (description "[GPT-5.4](https://openrouter.ai/openai/gpt-5.4) Image 2 combines OpenAI's GPT-5.4 model with state-of-the-art image generation capabilities from GPT Image 2. It enables rich multimodal workflows, allowing users to seamlessly move between reasoning, coding, and...")
    (context_length 272000)
    (architecture (
      (modality text+image+file->text+image)
      (input_modalities ([]
        image
        text
        file
      ))
      (output_modalities ([]
        image
        text
      ))
      (tokenizer GPT)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.000008")
      (completion "0.000015")
      (image_output "0.00003")
      (web_search "0.01")
      (input_cache_read "0.000002")
    ))
    (top_provider (
      (context_length 272000)
      (max_completion_tokens 128000)
      (is_moderated true)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      frequency_penalty
      include_reasoning
      logit_bias
      logprobs
      max_tokens
      presence_penalty
      reasoning
      reasoning_effort
      response_format
      seed
      stop
      structured_outputs
      top_logprobs
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
      (details /api/v1/models/openai/gpt-5.4-image-2-20260421/endpoints)
    ))
    (reasoning (
      (mandatory false)
      (default_enabled false)
      (supported_efforts ([]
        xhigh
        high
        medium
        low
        none
      ))
      (default_effort medium)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId openai/gpt-5.4-image-2)
  ))
)
