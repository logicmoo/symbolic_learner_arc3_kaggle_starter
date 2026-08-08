({}
  (kind model)
  (id openrouter-perplexity_sonar-reasoning-pro)
  (label "Perplexity: Sonar Reasoning Pro")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model perplexity/sonar-reasoning-pro)
  (enabled true)
  (capabilities ({}
    (audio false)
    (code false)
    (functionCalling false)
    (json false)
    (jsonMode false)
    (local false)
    (multimodal true)
    (reasoning true)
    (text true)
    (tools false)
    (vision true)
  ))
  (limits ({}
    (contextWindow 128000)
    (maxOutputTokens null)
  ))
  (pricing ({}
    (prompt "0.000002")
    (completion "0.000008")
    (web_search "0.005")
  ))
  (properties ({}
    (id perplexity/sonar-reasoning-pro)
    (canonical_slug perplexity/sonar-reasoning-pro)
    (hugging_face_id "")
    (name "Perplexity: Sonar Reasoning Pro")
    (created 1741313308)
    (description "Note: Sonar Pro pricing includes Perplexity search pricing. See [details here](https://docs.perplexity.ai/guides/pricing#detailed-pricing-breakdown-for-sonar-reasoning-pro-and-sonar-pro) Sonar Reasoning Pro is a premier reasoning model powered by DeepSeek R1 with Chain of Thought (CoT). Designed for...")
    (context_length 128000)
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
      (instruct_type deepseek-r1)
    ))
    (pricing ({}
      (prompt "0.000002")
      (completion "0.000008")
      (web_search "0.005")
    ))
    (top_provider ({}
      (context_length 128000)
      (max_completion_tokens null)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      include_reasoning
      max_tokens
      presence_penalty
      reasoning
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
      (details /api/v1/models/perplexity/sonar-reasoning-pro/endpoints)
    ))
    (reasoning ({}
      (mandatory false)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id perplexity/sonar-reasoning-pro)
    (canonical_slug perplexity/sonar-reasoning-pro)
    (hugging_face_id "")
    (name "Perplexity: Sonar Reasoning Pro")
    (created 1741313308)
    (description "Note: Sonar Pro pricing includes Perplexity search pricing. See [details here](https://docs.perplexity.ai/guides/pricing#detailed-pricing-breakdown-for-sonar-reasoning-pro-and-sonar-pro) Sonar Reasoning Pro is a premier reasoning model powered by DeepSeek R1 with Chain of Thought (CoT). Designed for...")
    (context_length 128000)
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
      (instruct_type deepseek-r1)
    ))
    (pricing ({}
      (prompt "0.000002")
      (completion "0.000008")
      (web_search "0.005")
    ))
    (top_provider ({}
      (context_length 128000)
      (max_completion_tokens null)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      include_reasoning
      max_tokens
      presence_penalty
      reasoning
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
      (details /api/v1/models/perplexity/sonar-reasoning-pro/endpoints)
    ))
    (reasoning ({}
      (mandatory false)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId perplexity/sonar-reasoning-pro)
  ))
)
