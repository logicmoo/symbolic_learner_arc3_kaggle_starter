(
  (kind model)
  (id openrouter-cohere_command-r7b-12-2024)
  (label "Cohere: Command R7B (12-2024)")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model cohere/command-r7b-12-2024)
  (enabled true)
  (capabilities (
    (audio false)
    (code false)
    (functionCalling false)
    (json true)
    (jsonMode true)
    (local false)
    (multimodal false)
    (reasoning false)
    (text true)
    (tools false)
    (vision false)
  ))
  (limits (
    (contextWindow 128000)
    (maxOutputTokens 4000)
  ))
  (pricing (
    (prompt "0.0000000375")
    (completion "0.00000015")
  ))
  (properties (
    (id cohere/command-r7b-12-2024)
    (canonical_slug cohere/command-r7b-12-2024)
    (hugging_face_id "")
    (name "Cohere: Command R7B (12-2024)")
    (created 1734158152)
    (description "Command R7B (12-2024) is a small, fast update of the Command R+ model, delivered in December 2024. It excels at RAG, tool use, agents, and similar tasks requiring complex reasoning...")
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
      (prompt "0.0000000375")
      (completion "0.00000015")
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
      top_k
      top_p
    ))
    (default_parameters ())
    (supported_voices null)
    (knowledge_cutoff 2024-08-31)
    (expiration_date null)
    (links (
      (details /api/v1/models/cohere/command-r7b-12-2024/endpoints)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id cohere/command-r7b-12-2024)
    (canonical_slug cohere/command-r7b-12-2024)
    (hugging_face_id "")
    (name "Cohere: Command R7B (12-2024)")
    (created 1734158152)
    (description "Command R7B (12-2024) is a small, fast update of the Command R+ model, delivered in December 2024. It excels at RAG, tool use, agents, and similar tasks requiring complex reasoning...")
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
      (prompt "0.0000000375")
      (completion "0.00000015")
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
      top_k
      top_p
    ))
    (default_parameters ())
    (supported_voices null)
    (knowledge_cutoff 2024-08-31)
    (expiration_date null)
    (links (
      (details /api/v1/models/cohere/command-r7b-12-2024/endpoints)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId cohere/command-r7b-12-2024)
  ))
)
