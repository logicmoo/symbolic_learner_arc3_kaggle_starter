({}
  (kind model)
  (id openrouter-openai_gpt-oss-safeguard-20b)
  (label "OpenAI: gpt-oss-safeguard-20b")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model openai/gpt-oss-safeguard-20b)
  (enabled true)
  (capabilities ({}
    (audio false)
    (code false)
    (functionCalling true)
    (json true)
    (jsonMode true)
    (local false)
    (multimodal false)
    (reasoning true)
    (text true)
    (tools true)
    (vision false)
  ))
  (limits ({}
    (contextWindow 131072)
    (maxOutputTokens 65536)
  ))
  (pricing ({}
    (prompt "0.000000075")
    (completion "0.0000003")
    (input_cache_read "0.0000000375")
  ))
  (properties ({}
    (id openai/gpt-oss-safeguard-20b)
    (canonical_slug openai/gpt-oss-safeguard-20b)
    (hugging_face_id openai/gpt-oss-safeguard-20b)
    (name "OpenAI: gpt-oss-safeguard-20b")
    (created 1761752836)
    (description "gpt-oss-safeguard-20b is a safety reasoning model from OpenAI built upon gpt-oss-20b. This open-weight, 21B-parameter Mixture-of-Experts (MoE) model offers lower latency for safety tasks like content classification, LLM filtering, and trust...")
    (context_length 131072)
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
      (prompt "0.000000075")
      (completion "0.0000003")
      (input_cache_read "0.0000000375")
    ))
    (top_provider ({}
      (context_length 131072)
      (max_completion_tokens 65536)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      include_reasoning
      max_tokens
      reasoning
      response_format
      seed
      stop
      structured_outputs
      temperature
      tool_choice
      tools
      top_p
    ))
    (default_parameters ({}))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/openai/gpt-oss-safeguard-20b/endpoints)
    ))
    (reasoning ({}
      (mandatory true)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id openai/gpt-oss-safeguard-20b)
    (canonical_slug openai/gpt-oss-safeguard-20b)
    (hugging_face_id openai/gpt-oss-safeguard-20b)
    (name "OpenAI: gpt-oss-safeguard-20b")
    (created 1761752836)
    (description "gpt-oss-safeguard-20b is a safety reasoning model from OpenAI built upon gpt-oss-20b. This open-weight, 21B-parameter Mixture-of-Experts (MoE) model offers lower latency for safety tasks like content classification, LLM filtering, and trust...")
    (context_length 131072)
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
      (prompt "0.000000075")
      (completion "0.0000003")
      (input_cache_read "0.0000000375")
    ))
    (top_provider ({}
      (context_length 131072)
      (max_completion_tokens 65536)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      include_reasoning
      max_tokens
      reasoning
      response_format
      seed
      stop
      structured_outputs
      temperature
      tool_choice
      tools
      top_p
    ))
    (default_parameters ({}))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/openai/gpt-oss-safeguard-20b/endpoints)
    ))
    (reasoning ({}
      (mandatory true)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId openai/gpt-oss-safeguard-20b)
  ))
)
