(
  (kind model)
  (id openrouter-cohere_command-r-08-2024)
  (label "Cohere: Command R (08-2024)")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model cohere/command-r-08-2024)
  (enabled true)
  (capabilities (
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
  (limits (
    (contextWindow 128000)
    (maxOutputTokens 4000)
  ))
  (pricing (
    (prompt "0.00000015")
    (completion "0.0000006")
  ))
  (properties (
    (id cohere/command-r-08-2024)
    (canonical_slug cohere/command-r-08-2024)
    (hugging_face_id null)
    (name "Cohere: Command R (08-2024)")
    (created 1724976000)
    (description "command-r-08-2024 is an update of the [Command R](/models/cohere/command-r) with improved performance for multilingual retrieval-augmented generation (RAG) and tool use. More broadly, it is better at math, code and reasoning and...")
    (context_length 128000)
    (architecture (
      (modality text->text)
      (input_modalities ([]
        text
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Cohere)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.00000015")
      (completion "0.0000006")
    ))
    (top_provider (
      (context_length 128000)
      (max_completion_tokens 4000)
      (is_moderated true)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      frequency_penalty
      max_tokens
      presence_penalty
      response_format
      seed
      stop
      structured_outputs
      temperature
      tool_choice
      tools
      top_k
      top_p
    ))
    (default_parameters ())
    (supported_voices null)
    (knowledge_cutoff 2024-03-31)
    (expiration_date null)
    (links (
      (details /api/v1/models/cohere/command-r-08-2024/endpoints)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id cohere/command-r-08-2024)
    (canonical_slug cohere/command-r-08-2024)
    (hugging_face_id null)
    (name "Cohere: Command R (08-2024)")
    (created 1724976000)
    (description "command-r-08-2024 is an update of the [Command R](/models/cohere/command-r) with improved performance for multilingual retrieval-augmented generation (RAG) and tool use. More broadly, it is better at math, code and reasoning and...")
    (context_length 128000)
    (architecture (
      (modality text->text)
      (input_modalities ([]
        text
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Cohere)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.00000015")
      (completion "0.0000006")
    ))
    (top_provider (
      (context_length 128000)
      (max_completion_tokens 4000)
      (is_moderated true)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      frequency_penalty
      max_tokens
      presence_penalty
      response_format
      seed
      stop
      structured_outputs
      temperature
      tool_choice
      tools
      top_k
      top_p
    ))
    (default_parameters ())
    (supported_voices null)
    (knowledge_cutoff 2024-03-31)
    (expiration_date null)
    (links (
      (details /api/v1/models/cohere/command-r-08-2024/endpoints)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId cohere/command-r-08-2024)
  ))
)
