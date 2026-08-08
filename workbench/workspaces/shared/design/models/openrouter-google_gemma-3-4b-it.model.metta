({}
  (kind model)
  (id openrouter-google_gemma-3-4b-it)
  (label "Google: Gemma 3 4B")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model google/gemma-3-4b-it)
  (enabled true)
  (capabilities ({}
    (audio false)
    (code false)
    (functionCalling false)
    (json true)
    (jsonMode true)
    (local false)
    (multimodal true)
    (reasoning false)
    (text true)
    (tools false)
    (vision true)
  ))
  (limits ({}
    (contextWindow 131072)
    (maxOutputTokens 16384)
  ))
  (pricing ({}
    (prompt "0.00000005")
    (completion "0.0000001")
  ))
  (properties ({}
    (id google/gemma-3-4b-it)
    (canonical_slug google/gemma-3-4b-it)
    (hugging_face_id google/gemma-3-4b-it)
    (name "Google: Gemma 3 4B")
    (created 1741905510)
    (description "Gemma 3 introduces multimodality, supporting vision-language input and text outputs. It handles context windows up to 128k tokens, understands over 140 languages, and offers improved math, reasoning, and chat capabilities,...")
    (context_length 131072)
    (architecture ({}
      (modality text+image->text)
      (input_modalities (
        text
        image
      ))
      (output_modalities (
        text
      ))
      (tokenizer Gemini)
      (instruct_type gemma)
    ))
    (pricing ({}
      (prompt "0.00000005")
      (completion "0.0000001")
    ))
    (top_provider ({}
      (context_length 131072)
      (max_completion_tokens 16384)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      logit_bias
      max_tokens
      min_p
      presence_penalty
      repetition_penalty
      response_format
      seed
      stop
      structured_outputs
      temperature
      top_k
      top_p
    ))
    (default_parameters ({}))
    (supported_voices null)
    (knowledge_cutoff 2024-08-31)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/google/gemma-3-4b-it/endpoints)
    ))
    (benchmarks ({}
      (design_arena ())
      (artificial_analysis ({}
        (intelligence_index null)
        (coding_index 2.7)
        (agentic_index null)
      ))
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id google/gemma-3-4b-it)
    (canonical_slug google/gemma-3-4b-it)
    (hugging_face_id google/gemma-3-4b-it)
    (name "Google: Gemma 3 4B")
    (created 1741905510)
    (description "Gemma 3 introduces multimodality, supporting vision-language input and text outputs. It handles context windows up to 128k tokens, understands over 140 languages, and offers improved math, reasoning, and chat capabilities,...")
    (context_length 131072)
    (architecture ({}
      (modality text+image->text)
      (input_modalities (
        text
        image
      ))
      (output_modalities (
        text
      ))
      (tokenizer Gemini)
      (instruct_type gemma)
    ))
    (pricing ({}
      (prompt "0.00000005")
      (completion "0.0000001")
    ))
    (top_provider ({}
      (context_length 131072)
      (max_completion_tokens 16384)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      logit_bias
      max_tokens
      min_p
      presence_penalty
      repetition_penalty
      response_format
      seed
      stop
      structured_outputs
      temperature
      top_k
      top_p
    ))
    (default_parameters ({}))
    (supported_voices null)
    (knowledge_cutoff 2024-08-31)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/google/gemma-3-4b-it/endpoints)
    ))
    (benchmarks ({}
      (design_arena ())
      (artificial_analysis ({}
        (intelligence_index null)
        (coding_index 2.7)
        (agentic_index null)
      ))
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId google/gemma-3-4b-it)
  ))
)
