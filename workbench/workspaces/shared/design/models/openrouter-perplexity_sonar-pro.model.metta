({}
  (kind model)
  (id openrouter-perplexity_sonar-pro)
  (label "Perplexity: Sonar Pro")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model perplexity/sonar-pro)
  (enabled true)
  (capabilities ({}
    (audio false)
    (code false)
    (functionCalling false)
    (json false)
    (jsonMode false)
    (local false)
    (multimodal true)
    (reasoning false)
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
    (web_search "0.005")
  ))
  (properties ({}
    (id perplexity/sonar-pro)
    (canonical_slug perplexity/sonar-pro)
    (hugging_face_id "")
    (name "Perplexity: Sonar Pro")
    (created 1741312423)
    (description "Note: Sonar Pro pricing includes Perplexity search pricing. See [details here](https://docs.perplexity.ai/guides/pricing#detailed-pricing-breakdown-for-sonar-reasoning-pro-and-sonar-pro) For enterprises seeking more advanced capabilities, the Sonar Pro API can handle in-depth, multi-step queries with added extensibility, like...")
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
      (web_search "0.005")
    ))
    (top_provider ({}
      (context_length 200000)
      (max_completion_tokens 8000)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      max_tokens
      presence_penalty
      temperature
      top_k
      top_p
      web_search_options
    ))
    (default_parameters ({}))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/perplexity/sonar-pro/endpoints)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id perplexity/sonar-pro)
    (canonical_slug perplexity/sonar-pro)
    (hugging_face_id "")
    (name "Perplexity: Sonar Pro")
    (created 1741312423)
    (description "Note: Sonar Pro pricing includes Perplexity search pricing. See [details here](https://docs.perplexity.ai/guides/pricing#detailed-pricing-breakdown-for-sonar-reasoning-pro-and-sonar-pro) For enterprises seeking more advanced capabilities, the Sonar Pro API can handle in-depth, multi-step queries with added extensibility, like...")
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
      (web_search "0.005")
    ))
    (top_provider ({}
      (context_length 200000)
      (max_completion_tokens 8000)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      max_tokens
      presence_penalty
      temperature
      top_k
      top_p
      web_search_options
    ))
    (default_parameters ({}))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/perplexity/sonar-pro/endpoints)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId perplexity/sonar-pro)
  ))
)
