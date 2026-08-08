({}
  (kind model)
  (id openrouter-google_gemma-3-12b-it)
  (label "Google: Gemma 3 12B")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model google/gemma-3-12b-it)
  (enabled true)
  (capabilities ({}
    (audio false)
    (code false)
    (functionCalling true)
    (json true)
    (jsonMode true)
    (local false)
    (multimodal true)
    (reasoning false)
    (text true)
    (tools true)
    (vision true)
  ))
  (limits ({}
    (contextWindow 131072)
    (maxOutputTokens 16384)
  ))
  (pricing ({}
    (prompt "0.00000005")
    (completion "0.00000015")
  ))
  (properties ({}
    (id google/gemma-3-12b-it)
    (canonical_slug google/gemma-3-12b-it)
    (hugging_face_id google/gemma-3-12b-it)
    (name "Google: Gemma 3 12B")
    (created 1741902625)
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
      (completion "0.00000015")
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
      tool_choice
      tools
      top_k
      top_p
    ))
    (default_parameters ({}))
    (supported_voices null)
    (knowledge_cutoff 2024-08-31)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/google/gemma-3-12b-it/endpoints)
    ))
    (benchmarks ({}
      (design_arena ())
      (artificial_analysis ({}
        (intelligence_index 5.5)
        (coding_index 5.8)
        (agentic_index 0.3)
      ))
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id google/gemma-3-12b-it)
    (canonical_slug google/gemma-3-12b-it)
    (hugging_face_id google/gemma-3-12b-it)
    (name "Google: Gemma 3 12B")
    (created 1741902625)
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
      (completion "0.00000015")
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
      tool_choice
      tools
      top_k
      top_p
    ))
    (default_parameters ({}))
    (supported_voices null)
    (knowledge_cutoff 2024-08-31)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/google/gemma-3-12b-it/endpoints)
    ))
    (benchmarks ({}
      (design_arena ())
      (artificial_analysis ({}
        (intelligence_index 5.5)
        (coding_index 5.8)
        (agentic_index 0.3)
      ))
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId google/gemma-3-12b-it)
  ))
)
