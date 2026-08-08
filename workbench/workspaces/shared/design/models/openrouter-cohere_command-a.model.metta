(
  (kind model)
  (id openrouter-cohere_command-a)
  (label "Cohere: Command A")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model cohere/command-a)
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
    (contextWindow 256000)
    (maxOutputTokens 8192)
  ))
  (pricing (
    (prompt "0.0000025")
    (completion "0.00001")
  ))
  (properties (
    (id cohere/command-a)
    (canonical_slug cohere/command-a-03-2025)
    (hugging_face_id CohereForAI/c4ai-command-a-03-2025)
    (name "Cohere: Command A")
    (created 1741894342)
    (description "Command A is an open-weights 111B parameter model with a 256k context window focused on delivering great performance across agentic, multilingual, and coding use cases. Compared to other leading proprietary...")
    (context_length 256000)
    (architecture (
      (modality text->text)
      (input_modalities ([]
        text
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Other)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.0000025")
      (completion "0.00001")
    ))
    (top_provider (
      (context_length 256000)
      (max_completion_tokens 8192)
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
      (details /api/v1/models/cohere/command-a-03-2025/endpoints)
    ))
    (benchmarks (
      (design_arena ([]))
      (artificial_analysis (
        (intelligence_index 22.8)
        (coding_index 27.8)
        (agentic_index 9.2)
      ))
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id cohere/command-a)
    (canonical_slug cohere/command-a-03-2025)
    (hugging_face_id CohereForAI/c4ai-command-a-03-2025)
    (name "Cohere: Command A")
    (created 1741894342)
    (description "Command A is an open-weights 111B parameter model with a 256k context window focused on delivering great performance across agentic, multilingual, and coding use cases. Compared to other leading proprietary...")
    (context_length 256000)
    (architecture (
      (modality text->text)
      (input_modalities ([]
        text
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Other)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.0000025")
      (completion "0.00001")
    ))
    (top_provider (
      (context_length 256000)
      (max_completion_tokens 8192)
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
      (details /api/v1/models/cohere/command-a-03-2025/endpoints)
    ))
    (benchmarks (
      (design_arena ([]))
      (artificial_analysis (
        (intelligence_index 22.8)
        (coding_index 27.8)
        (agentic_index 9.2)
      ))
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId cohere/command-a)
  ))
)
