({}
  (kind model)
  (id openrouter-openrouter_fusion)
  (label "OpenRouter: Fusion")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model openrouter/fusion)
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
    (contextWindow 1000000)
    (maxOutputTokens null)
  ))
  (pricing ({}
    (prompt "-1")
    (completion "-1")
  ))
  (properties ({}
    (id openrouter/fusion)
    (canonical_slug openrouter/fusion)
    (hugging_face_id null)
    (name "OpenRouter: Fusion")
    (created 1781371647)
    (description "Fusion turns your prompt into a small multi-model deliberation. A panel of expert models (see below) analyzes your prompt in parallel with web search and web fetch enabled, then a...")
    (context_length 1000000)
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
      (top_k null)
      (frequency_penalty null)
      (presence_penalty null)
      (repetition_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/openrouter/fusion/endpoints)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id openrouter/fusion)
    (canonical_slug openrouter/fusion)
    (hugging_face_id null)
    (name "OpenRouter: Fusion")
    (created 1781371647)
    (description "Fusion turns your prompt into a small multi-model deliberation. A panel of expert models (see below) analyzes your prompt in parallel with web search and web fetch enabled, then a...")
    (context_length 1000000)
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
      (top_k null)
      (frequency_penalty null)
      (presence_penalty null)
      (repetition_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/openrouter/fusion/endpoints)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId openrouter/fusion)
  ))
)
