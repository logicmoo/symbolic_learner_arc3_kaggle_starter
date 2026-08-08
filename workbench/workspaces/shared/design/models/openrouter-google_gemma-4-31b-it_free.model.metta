({}
  (kind model)
  (id openrouter-google_gemma-4-31b-it_free)
  (label "Google: Gemma 4 31B (free)")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model google/gemma-4-31b-it:free)
  (enabled true)
  (capabilities ({}
    (audio false)
    (code false)
    (functionCalling true)
    (json true)
    (jsonMode true)
    (local false)
    (multimodal true)
    (reasoning true)
    (text true)
    (tools true)
    (vision true)
  ))
  (limits ({}
    (contextWindow 262144)
    (maxOutputTokens 32768)
  ))
  (pricing ({}
    (prompt "0")
    (completion "0")
  ))
  (properties ({}
    (id google/gemma-4-31b-it:free)
    (canonical_slug google/gemma-4-31b-it-20260402)
    (hugging_face_id google/gemma-4-31B-it)
    (name "Google: Gemma 4 31B (free)")
    (created 1775148486)
    (description "Gemma 4 31B Instruct is Google DeepMind's 30.7B dense multimodal model supporting text and image input with text output. Features a 256K token context window, configurable thinking/reasoning mode, native function...")
    (context_length 262144)
    (architecture ({}
      (modality text+image+video->text)
      (input_modalities (
        image
        text
        video
      ))
      (output_modalities (
        text
      ))
      (tokenizer Gemma)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0")
      (completion "0")
    ))
    (top_provider ({}
      (context_length 262144)
      (max_completion_tokens 32768)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      include_reasoning
      max_tokens
      reasoning
      response_format
      seed
      temperature
      tool_choice
      tools
      top_p
    ))
    (default_parameters ({}
      (temperature 1)
      (top_p 0.95)
      (top_k 64)
      (frequency_penalty null)
      (presence_penalty null)
      (repetition_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/google/gemma-4-31b-it-20260402/endpoints)
    ))
    (benchmarks ({}
      (design_arena ())
      (artificial_analysis ({}
        (intelligence_index 29.7)
        (coding_index 43.4)
        (agentic_index 14.4)
      ))
    ))
    (reasoning ({}
      (mandatory false)
      (default_enabled false)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id google/gemma-4-31b-it:free)
    (canonical_slug google/gemma-4-31b-it-20260402)
    (hugging_face_id google/gemma-4-31B-it)
    (name "Google: Gemma 4 31B (free)")
    (created 1775148486)
    (description "Gemma 4 31B Instruct is Google DeepMind's 30.7B dense multimodal model supporting text and image input with text output. Features a 256K token context window, configurable thinking/reasoning mode, native function...")
    (context_length 262144)
    (architecture ({}
      (modality text+image+video->text)
      (input_modalities (
        image
        text
        video
      ))
      (output_modalities (
        text
      ))
      (tokenizer Gemma)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0")
      (completion "0")
    ))
    (top_provider ({}
      (context_length 262144)
      (max_completion_tokens 32768)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      include_reasoning
      max_tokens
      reasoning
      response_format
      seed
      temperature
      tool_choice
      tools
      top_p
    ))
    (default_parameters ({}
      (temperature 1)
      (top_p 0.95)
      (top_k 64)
      (frequency_penalty null)
      (presence_penalty null)
      (repetition_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/google/gemma-4-31b-it-20260402/endpoints)
    ))
    (benchmarks ({}
      (design_arena ())
      (artificial_analysis ({}
        (intelligence_index 29.7)
        (coding_index 43.4)
        (agentic_index 14.4)
      ))
    ))
    (reasoning ({}
      (mandatory false)
      (default_enabled false)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId google/gemma-4-31b-it:free)
  ))
)
