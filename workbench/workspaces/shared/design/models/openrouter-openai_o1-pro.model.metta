({}
  (kind model)
  (id openrouter-openai_o1-pro)
  (label "OpenAI: o1-pro")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model openai/o1-pro)
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
    (maxOutputTokens 100000)
  ))
  (pricing ({}
    (prompt "0.00015")
    (completion "0.0006")
    (web_search "0.01")
  ))
  (properties ({}
    (id openai/o1-pro)
    (canonical_slug openai/o1-pro)
    (hugging_face_id "")
    (name "OpenAI: o1-pro")
    (created 1742423211)
    (description "The o1 series of models are trained with reinforcement learning to think before they answer and perform complex reasoning. The o1-pro model uses more compute to think harder and provide...")
    (context_length 200000)
    (architecture ({}
      (modality text+image+file->text)
      (input_modalities (
        text
        image
        file
      ))
      (output_modalities (
        text
      ))
      (tokenizer GPT)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.00015")
      (completion "0.0006")
      (web_search "0.01")
    ))
    (top_provider ({}
      (context_length 200000)
      (max_completion_tokens 100000)
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
    ))
    (default_parameters ({}))
    (supported_voices null)
    (knowledge_cutoff 2023-10-31)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/openai/o1-pro/endpoints)
    ))
    (reasoning ({}
      (mandatory false)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id openai/o1-pro)
    (canonical_slug openai/o1-pro)
    (hugging_face_id "")
    (name "OpenAI: o1-pro")
    (created 1742423211)
    (description "The o1 series of models are trained with reinforcement learning to think before they answer and perform complex reasoning. The o1-pro model uses more compute to think harder and provide...")
    (context_length 200000)
    (architecture ({}
      (modality text+image+file->text)
      (input_modalities (
        text
        image
        file
      ))
      (output_modalities (
        text
      ))
      (tokenizer GPT)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.00015")
      (completion "0.0006")
      (web_search "0.01")
    ))
    (top_provider ({}
      (context_length 200000)
      (max_completion_tokens 100000)
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
    ))
    (default_parameters ({}))
    (supported_voices null)
    (knowledge_cutoff 2023-10-31)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/openai/o1-pro/endpoints)
    ))
    (reasoning ({}
      (mandatory false)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId openai/o1-pro)
  ))
)
