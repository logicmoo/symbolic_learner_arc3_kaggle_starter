({}
  (kind model)
  (id openrouter-openai_gpt-5-codex_batch)
  (label "OpenAI: GPT-5 Codex (batch)")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model openai/gpt-5-codex:batch)
  (enabled true)
  (capabilities ({}
    (audio false)
    (code true)
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
  (limits ({}
    (contextWindow 400000)
    (maxOutputTokens 128000)
  ))
  (pricing ({}
    (prompt "0.000000625")
    (completion "0.000005")
    (web_search "0.01")
    (input_cache_read "0.0000000625")
  ))
  (properties ({}
    (id openai/gpt-5-codex:batch)
    (canonical_slug openai/gpt-5-codex)
    (hugging_face_id "")
    (name "OpenAI: GPT-5 Codex (batch)")
    (created 1758643403)
    (description "GPT-5-Codex is a specialized version of GPT-5 optimized for software engineering and coding workflows. It is designed for both interactive development sessions and long, independent execution of complex engineering tasks....")
    (context_length 400000)
    (architecture ({}
      (modality text+image->text)
      (input_modalities (
        text
        image
      ))
      (output_modalities (
        text
      ))
      (tokenizer GPT)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.000000625")
      (completion "0.000005")
      (web_search "0.01")
      (input_cache_read "0.0000000625")
    ))
    (top_provider ({}
      (context_length 400000)
      (max_completion_tokens 128000)
      (is_moderated true)
    ))
    (per_request_limits null)
    (supported_parameters (
      include_reasoning
      max_tokens
      reasoning
      response_format
      seed
      structured_outputs
      tool_choice
      tools
    ))
    (default_parameters ({}
      (temperature null)
      (top_p null)
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff 2024-09-30)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/openai/gpt-5-codex/endpoints)
    ))
    (reasoning ({}
      (mandatory true)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id openai/gpt-5-codex:batch)
    (canonical_slug openai/gpt-5-codex)
    (hugging_face_id "")
    (name "OpenAI: GPT-5 Codex (batch)")
    (created 1758643403)
    (description "GPT-5-Codex is a specialized version of GPT-5 optimized for software engineering and coding workflows. It is designed for both interactive development sessions and long, independent execution of complex engineering tasks....")
    (context_length 400000)
    (architecture ({}
      (modality text+image->text)
      (input_modalities (
        text
        image
      ))
      (output_modalities (
        text
      ))
      (tokenizer GPT)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.000000625")
      (completion "0.000005")
      (web_search "0.01")
      (input_cache_read "0.0000000625")
    ))
    (top_provider ({}
      (context_length 400000)
      (max_completion_tokens 128000)
      (is_moderated true)
    ))
    (per_request_limits null)
    (supported_parameters (
      include_reasoning
      max_tokens
      reasoning
      response_format
      seed
      structured_outputs
      tool_choice
      tools
    ))
    (default_parameters ({}
      (temperature null)
      (top_p null)
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff 2024-09-30)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/openai/gpt-5-codex/endpoints)
    ))
    (reasoning ({}
      (mandatory true)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId openai/gpt-5-codex:batch)
  ))
)
