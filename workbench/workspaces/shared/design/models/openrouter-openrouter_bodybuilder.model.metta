({}
  (kind model)
  (id openrouter-openrouter_bodybuilder)
  (label "Body Builder (beta)")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model openrouter/bodybuilder)
  (enabled true)
  (capabilities ({}
    (audio false)
    (code false)
    (functionCalling false)
    (json false)
    (jsonMode false)
    (local false)
    (multimodal false)
    (reasoning false)
    (text true)
    (tools false)
    (vision false)
  ))
  (limits ({}
    (contextWindow 128000)
    (maxOutputTokens null)
  ))
  (pricing ({}
    (prompt "-1")
    (completion "-1")
  ))
  (properties ({}
    (id openrouter/bodybuilder)
    (canonical_slug openrouter/bodybuilder)
    (hugging_face_id "")
    (name "Body Builder (beta)")
    (created 1764903653)
    (description "Transform your natural language requests into structured OpenRouter API request objects. Describe what you want to accomplish with AI models, and Body Builder will construct the appropriate API calls. Example:...")
    (context_length 128000)
    (architecture ({}
      (modality text->text)
      (input_modalities (
        text
      ))
      (output_modalities (
        text
      ))
      (tokenizer Router)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "-1")
      (completion "-1")
    ))
    (top_provider ({}
      (context_length null)
      (max_completion_tokens null)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ())
    (default_parameters ({}
      (temperature null)
      (top_p null)
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/openrouter/bodybuilder/endpoints)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id openrouter/bodybuilder)
    (canonical_slug openrouter/bodybuilder)
    (hugging_face_id "")
    (name "Body Builder (beta)")
    (created 1764903653)
    (description "Transform your natural language requests into structured OpenRouter API request objects. Describe what you want to accomplish with AI models, and Body Builder will construct the appropriate API calls. Example:...")
    (context_length 128000)
    (architecture ({}
      (modality text->text)
      (input_modalities (
        text
      ))
      (output_modalities (
        text
      ))
      (tokenizer Router)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "-1")
      (completion "-1")
    ))
    (top_provider ({}
      (context_length null)
      (max_completion_tokens null)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ())
    (default_parameters ({}
      (temperature null)
      (top_p null)
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/openrouter/bodybuilder/endpoints)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId openrouter/bodybuilder)
  ))
)
