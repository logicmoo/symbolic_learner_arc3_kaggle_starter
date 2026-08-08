(
  (kind model)
  (id openrouter-openai_gpt-5-pro)
  (label "OpenAI: GPT-5 Pro")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model openai/gpt-5-pro)
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
    (contextWindow 400000)
    (maxOutputTokens 128000)
  ))
  (pricing (
    (prompt "0.000015")
    (completion "0.00012")
    (web_search "0.01")
  ))
  (properties (
    (id openai/gpt-5-pro)
    (canonical_slug openai/gpt-5-pro-2025-10-06)
    (hugging_face_id "")
    (name "OpenAI: GPT-5 Pro")
    (created 1759776663)
    (description "GPT-5 Pro is OpenAI’s most advanced model, offering major improvements in reasoning, code quality, and user experience. It is optimized for complex tasks that require step-by-step reasoning, instruction following, and...")
    (context_length 400000)
    (architecture (
      (modality text+image+file->text)
      (input_modalities ([]
        image
        text
        file
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer GPT)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.000015")
      (completion "0.00012")
      (web_search "0.01")
    ))
    (top_provider (
      (context_length 400000)
      (max_completion_tokens 128000)
      (is_moderated true)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      include_reasoning
      max_tokens
      reasoning
      reasoning_effort
      response_format
      seed
      structured_outputs
      tool_choice
      tools
    ))
    (default_parameters (
      (temperature null)
      (top_p null)
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff 2024-09-30)
    (expiration_date null)
    (links (
      (details /api/v1/models/openai/gpt-5-pro-2025-10-06/endpoints)
    ))
    (reasoning (
      (mandatory true)
      (supported_efforts ([]
        high
      ))
      (default_effort high)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id openai/gpt-5-pro)
    (canonical_slug openai/gpt-5-pro-2025-10-06)
    (hugging_face_id "")
    (name "OpenAI: GPT-5 Pro")
    (created 1759776663)
    (description "GPT-5 Pro is OpenAI’s most advanced model, offering major improvements in reasoning, code quality, and user experience. It is optimized for complex tasks that require step-by-step reasoning, instruction following, and...")
    (context_length 400000)
    (architecture (
      (modality text+image+file->text)
      (input_modalities ([]
        image
        text
        file
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer GPT)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.000015")
      (completion "0.00012")
      (web_search "0.01")
    ))
    (top_provider (
      (context_length 400000)
      (max_completion_tokens 128000)
      (is_moderated true)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      include_reasoning
      max_tokens
      reasoning
      reasoning_effort
      response_format
      seed
      structured_outputs
      tool_choice
      tools
    ))
    (default_parameters (
      (temperature null)
      (top_p null)
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff 2024-09-30)
    (expiration_date null)
    (links (
      (details /api/v1/models/openai/gpt-5-pro-2025-10-06/endpoints)
    ))
    (reasoning (
      (mandatory true)
      (supported_efforts ([]
        high
      ))
      (default_effort high)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId openai/gpt-5-pro)
  ))
)
