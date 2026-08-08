(
  (kind model)
  (id openrouter-openai_gpt-5.4-pro)
  (label "OpenAI: GPT-5.4 Pro")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model openai/gpt-5.4-pro)
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
    (contextWindow 1050000)
    (maxOutputTokens 128000)
  ))
  (pricing (
    (prompt "0.00003")
    (completion "0.00018")
    (web_search "0.01")
    (overrides ([]
      (
        (min_prompt_tokens 272000)
        (prompt "0.00006")
        (completion "0.00027")
      )
    ))
  ))
  (properties (
    (id openai/gpt-5.4-pro)
    (canonical_slug openai/gpt-5.4-pro-20260305)
    (hugging_face_id "")
    (name "OpenAI: GPT-5.4 Pro")
    (created 1772734366)
    (description "GPT-5.4 Pro is OpenAI's most advanced model, building on GPT-5.4's unified architecture with enhanced reasoning capabilities for complex, high-stakes tasks. It features a 1M+ token context window (922K input, 128K...")
    (context_length 1050000)
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
      (prompt "0.00003")
      (completion "0.00018")
      (web_search "0.01")
      (overrides ([]
        (
          (min_prompt_tokens 272000)
          (prompt "0.00006")
          (completion "0.00027")
        )
      ))
    ))
    (top_provider (
      (context_length 1050000)
      (max_completion_tokens 128000)
      (is_moderated true)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      include_reasoning
      max_completion_tokens
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
      (top_k null)
      (frequency_penalty null)
      (presence_penalty null)
      (repetition_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links (
      (details /api/v1/models/openai/gpt-5.4-pro-20260305/endpoints)
    ))
    (reasoning (
      (mandatory true)
      (supported_efforts ([]
        xhigh
        high
        medium
      ))
      (default_effort medium)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id openai/gpt-5.4-pro)
    (canonical_slug openai/gpt-5.4-pro-20260305)
    (hugging_face_id "")
    (name "OpenAI: GPT-5.4 Pro")
    (created 1772734366)
    (description "GPT-5.4 Pro is OpenAI's most advanced model, building on GPT-5.4's unified architecture with enhanced reasoning capabilities for complex, high-stakes tasks. It features a 1M+ token context window (922K input, 128K...")
    (context_length 1050000)
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
      (prompt "0.00003")
      (completion "0.00018")
      (web_search "0.01")
      (overrides ([]
        (
          (min_prompt_tokens 272000)
          (prompt "0.00006")
          (completion "0.00027")
        )
      ))
    ))
    (top_provider (
      (context_length 1050000)
      (max_completion_tokens 128000)
      (is_moderated true)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      include_reasoning
      max_completion_tokens
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
      (top_k null)
      (frequency_penalty null)
      (presence_penalty null)
      (repetition_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links (
      (details /api/v1/models/openai/gpt-5.4-pro-20260305/endpoints)
    ))
    (reasoning (
      (mandatory true)
      (supported_efforts ([]
        xhigh
        high
        medium
      ))
      (default_effort medium)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId openai/gpt-5.4-pro)
  ))
)
