({}
  (kind model)
  (id openrouter-relace_relace-search)
  (label "Relace: Relace Search")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model relace/relace-search)
  (enabled true)
  (capabilities ({}
    (audio false)
    (code false)
    (functionCalling true)
    (json true)
    (jsonMode true)
    (local false)
    (multimodal false)
    (reasoning false)
    (text true)
    (tools true)
    (vision false)
  ))
  (limits ({}
    (contextWindow 256000)
    (maxOutputTokens 128000)
  ))
  (pricing ({}
    (prompt "0.000001")
    (completion "0.000003")
  ))
  (properties ({}
    (id relace/relace-search)
    (canonical_slug relace/relace-search-20251208)
    (hugging_face_id null)
    (name "Relace: Relace Search")
    (created 1765213560)
    (description "The relace-search model uses 4-12 `view_file` and `grep` tools in parallel to explore a codebase and return relevant files to the user request. In contrast to RAG, relace-search performs agentic...")
    (context_length 256000)
    (architecture ({}
      (modality text->text)
      (input_modalities (
        text
      ))
      (output_modalities (
        text
      ))
      (tokenizer Other)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.000001")
      (completion "0.000003")
    ))
    (top_provider ({}
      (context_length 256000)
      (max_completion_tokens 128000)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      max_tokens
      response_format
      seed
      stop
      temperature
      tool_choice
      tools
      top_p
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
      (details /api/v1/models/relace/relace-search-20251208/endpoints)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id relace/relace-search)
    (canonical_slug relace/relace-search-20251208)
    (hugging_face_id null)
    (name "Relace: Relace Search")
    (created 1765213560)
    (description "The relace-search model uses 4-12 `view_file` and `grep` tools in parallel to explore a codebase and return relevant files to the user request. In contrast to RAG, relace-search performs agentic...")
    (context_length 256000)
    (architecture ({}
      (modality text->text)
      (input_modalities (
        text
      ))
      (output_modalities (
        text
      ))
      (tokenizer Other)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.000001")
      (completion "0.000003")
    ))
    (top_provider ({}
      (context_length 256000)
      (max_completion_tokens 128000)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      max_tokens
      response_format
      seed
      stop
      temperature
      tool_choice
      tools
      top_p
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
      (details /api/v1/models/relace/relace-search-20251208/endpoints)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId relace/relace-search)
  ))
)
