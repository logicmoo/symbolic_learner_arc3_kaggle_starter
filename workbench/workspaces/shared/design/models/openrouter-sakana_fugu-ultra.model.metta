({}
  (kind model)
  (id openrouter-sakana_fugu-ultra)
  (label "Sakana: Fugu Ultra")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model sakana/fugu-ultra)
  (enabled true)
  (capabilities ({}
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
  (limits ({}
    (contextWindow 1000000)
    (maxOutputTokens 128000)
  ))
  (pricing ({}
    (prompt "0.000005")
    (completion "0.00003")
    (web_search "0.01")
    (input_cache_read "0.0000005")
    (overrides (
      ({}
        (min_prompt_tokens 272000)
        (prompt "0.00001")
        (completion "0.000045")
        (input_cache_read "0.000001")
      )
    ))
  ))
  (properties ({}
    (id sakana/fugu-ultra)
    (canonical_slug sakana/fugu-ultra-20260615)
    (hugging_face_id null)
    (name "Sakana: Fugu Ultra")
    (created 1782276303)
    (description "Fugu Ultra is the higher-performance model in Sakana AI's Fugu family. Rather than a single monolithic model, Fugu is a learned multi-agent orchestration system: a language model trained to route...")
    (context_length 1000000)
    (architecture ({}
      (modality text+image->text)
      (input_modalities (
        text
        image
      ))
      (output_modalities (
        text
      ))
      (tokenizer Other)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.000005")
      (completion "0.00003")
      (web_search "0.01")
      (input_cache_read "0.0000005")
      (overrides (
        ({}
          (min_prompt_tokens 272000)
          (prompt "0.00001")
          (completion "0.000045")
          (input_cache_read "0.000001")
        )
      ))
    ))
    (top_provider ({}
      (context_length 1000000)
      (max_completion_tokens 128000)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      include_reasoning
      reasoning
      reasoning_effort
      structured_outputs
      tool_choice
      tools
      web_search_options
    ))
    (default_parameters ({}
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
    (links ({}
      (details /api/v1/models/sakana/fugu-ultra-20260615/endpoints)
    ))
    (reasoning ({}
      (mandatory true)
      (default_enabled true)
      (supported_efforts (
        max
        xhigh
        high
      ))
      (default_effort xhigh)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id sakana/fugu-ultra)
    (canonical_slug sakana/fugu-ultra-20260615)
    (hugging_face_id null)
    (name "Sakana: Fugu Ultra")
    (created 1782276303)
    (description "Fugu Ultra is the higher-performance model in Sakana AI's Fugu family. Rather than a single monolithic model, Fugu is a learned multi-agent orchestration system: a language model trained to route...")
    (context_length 1000000)
    (architecture ({}
      (modality text+image->text)
      (input_modalities (
        text
        image
      ))
      (output_modalities (
        text
      ))
      (tokenizer Other)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.000005")
      (completion "0.00003")
      (web_search "0.01")
      (input_cache_read "0.0000005")
      (overrides (
        ({}
          (min_prompt_tokens 272000)
          (prompt "0.00001")
          (completion "0.000045")
          (input_cache_read "0.000001")
        )
      ))
    ))
    (top_provider ({}
      (context_length 1000000)
      (max_completion_tokens 128000)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      include_reasoning
      reasoning
      reasoning_effort
      structured_outputs
      tool_choice
      tools
      web_search_options
    ))
    (default_parameters ({}
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
    (links ({}
      (details /api/v1/models/sakana/fugu-ultra-20260615/endpoints)
    ))
    (reasoning ({}
      (mandatory true)
      (default_enabled true)
      (supported_efforts (
        max
        xhigh
        high
      ))
      (default_effort xhigh)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId sakana/fugu-ultra)
  ))
)
