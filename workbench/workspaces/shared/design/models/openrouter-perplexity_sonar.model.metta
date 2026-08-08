(
  (kind model)
  (id openrouter-perplexity_sonar)
  (label "Perplexity: Sonar")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model perplexity/sonar)
  (enabled true)
  (capabilities (
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
  (limits (
    (contextWindow 127072)
    (maxOutputTokens null)
  ))
  (pricing (
    (prompt "0.000001")
    (completion "0.000001")
    (web_search "0.005")
  ))
  (properties (
    (id perplexity/sonar)
    (canonical_slug perplexity/sonar)
    (hugging_face_id "")
    (name "Perplexity: Sonar")
    (created 1738013808)
    (description "Sonar is lightweight, affordable, fast, and simple to use — now featuring citations and the ability to customize sources. It is designed for companies seeking to integrate lightweight question-and-answer features...")
    (context_length 127072)
    (architecture (
      (modality text+image->text)
      (input_modalities ([]
        text
        image
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Other)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.000001")
      (completion "0.000001")
      (web_search "0.005")
    ))
    (top_provider (
      (context_length 127072)
      (max_completion_tokens null)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      frequency_penalty
      max_tokens
      presence_penalty
      temperature
      top_k
      top_p
      web_search_options
    ))
    (default_parameters ())
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links (
      (details /api/v1/models/perplexity/sonar/endpoints)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id perplexity/sonar)
    (canonical_slug perplexity/sonar)
    (hugging_face_id "")
    (name "Perplexity: Sonar")
    (created 1738013808)
    (description "Sonar is lightweight, affordable, fast, and simple to use — now featuring citations and the ability to customize sources. It is designed for companies seeking to integrate lightweight question-and-answer features...")
    (context_length 127072)
    (architecture (
      (modality text+image->text)
      (input_modalities ([]
        text
        image
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Other)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.000001")
      (completion "0.000001")
      (web_search "0.005")
    ))
    (top_provider (
      (context_length 127072)
      (max_completion_tokens null)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      frequency_penalty
      max_tokens
      presence_penalty
      temperature
      top_k
      top_p
      web_search_options
    ))
    (default_parameters ())
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links (
      (details /api/v1/models/perplexity/sonar/endpoints)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId perplexity/sonar)
  ))
)
