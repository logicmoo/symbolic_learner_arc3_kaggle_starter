(
  (kind model)
  (id openrouter-google_gemma-3n-e4b-it)
  (label "Google: Gemma 3n 4B")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model google/gemma-3n-e4b-it)
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
    (contextWindow 32768)
    (maxOutputTokens null)
  ))
  (pricing (
    (prompt "0.00000006")
    (completion "0.00000012")
  ))
  (properties (
    (id google/gemma-3n-e4b-it)
    (canonical_slug google/gemma-3n-e4b-it)
    (hugging_face_id google/gemma-3n-E4B-it)
    (name "Google: Gemma 3n 4B")
    (created 1747776824)
    (description "Gemma 3n E4B-it is optimized for efficient execution on mobile and low-resource devices, such as phones, laptops, and tablets. It supports multimodal inputs—including text, visual data, and audio—enabling diverse tasks...")
    (context_length 32768)
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
      (prompt "0.00000006")
      (completion "0.00000012")
    ))
    (top_provider (
      (context_length 32768)
      (max_completion_tokens null)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      frequency_penalty
      logit_bias
      max_tokens
      min_p
      presence_penalty
      repetition_penalty
      response_format
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
      (details /api/v1/models/google/gemma-3n-e4b-it/endpoints)
    ))
    (benchmarks (
      (design_arena ([]))
      (artificial_analysis (
        (intelligence_index null)
        (coding_index 3.2)
        (agentic_index null)
      ))
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id google/gemma-3n-e4b-it)
    (canonical_slug google/gemma-3n-e4b-it)
    (hugging_face_id google/gemma-3n-E4B-it)
    (name "Google: Gemma 3n 4B")
    (created 1747776824)
    (description "Gemma 3n E4B-it is optimized for efficient execution on mobile and low-resource devices, such as phones, laptops, and tablets. It supports multimodal inputs—including text, visual data, and audio—enabling diverse tasks...")
    (context_length 32768)
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
      (prompt "0.00000006")
      (completion "0.00000012")
    ))
    (top_provider (
      (context_length 32768)
      (max_completion_tokens null)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      frequency_penalty
      logit_bias
      max_tokens
      min_p
      presence_penalty
      repetition_penalty
      response_format
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
      (details /api/v1/models/google/gemma-3n-e4b-it/endpoints)
    ))
    (benchmarks (
      (design_arena ([]))
      (artificial_analysis (
        (intelligence_index null)
        (coding_index 3.2)
        (agentic_index null)
      ))
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId google/gemma-3n-e4b-it)
  ))
)
