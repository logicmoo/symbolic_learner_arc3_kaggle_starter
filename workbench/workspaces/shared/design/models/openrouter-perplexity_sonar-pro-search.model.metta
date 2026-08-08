({}
  (kind model)
  (id openrouter-perplexity_sonar-pro-search)
  (label "Perplexity: Sonar Pro Search")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model perplexity/sonar-pro-search)
  (enabled true)
  (capabilities ({}
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
  (limits ({}
    (contextWindow 200000)
    (maxOutputTokens 8000)
  ))
  (pricing ({}
    (prompt "0.000003")
    (completion "0.000015")
    (web_search "0.018")
  ))
  (properties ({}
    (id perplexity/sonar-pro-search)
    (canonical_slug perplexity/sonar-pro-search)
    (hugging_face_id "")
    (name "Perplexity: Sonar Pro Search")
    (created 1761854366)
    (description "Exclusively available on the OpenRouter API, Sonar Pro's new Pro Search mode is Perplexity's most advanced agentic search system. It is designed for deeper reasoning and analysis. Pricing is based...")
    (context_length 200000)
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
      (prompt "0.000003")
      (completion "0.000015")
      (web_search "0.018")
    ))
    (top_provider ({}
      (context_length 200000)
      (max_completion_tokens 8000)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      include_reasoning
      max_tokens
      presence_penalty
      reasoning
      structured_outputs
      temperature
      top_k
      top_p
      web_search_options
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
      (details /api/v1/models/perplexity/sonar-pro-search/endpoints)
    ))
    (reasoning ({}
      (mandatory true)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id perplexity/sonar-pro-search)
    (canonical_slug perplexity/sonar-pro-search)
    (hugging_face_id "")
    (name "Perplexity: Sonar Pro Search")
    (created 1761854366)
    (description "Exclusively available on the OpenRouter API, Sonar Pro's new Pro Search mode is Perplexity's most advanced agentic search system. It is designed for deeper reasoning and analysis. Pricing is based...")
    (context_length 200000)
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
      (prompt "0.000003")
      (completion "0.000015")
      (web_search "0.018")
    ))
    (top_provider ({}
      (context_length 200000)
      (max_completion_tokens 8000)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      include_reasoning
      max_tokens
      presence_penalty
      reasoning
      structured_outputs
      temperature
      top_k
      top_p
      web_search_options
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
      (details /api/v1/models/perplexity/sonar-pro-search/endpoints)
    ))
    (reasoning ({}
      (mandatory true)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId perplexity/sonar-pro-search)
  ))
)
