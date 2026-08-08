({}
  (kind model)
  (id openrouter-mistralai_mistral-small-2603)
  (label "Mistral: Mistral Small 4")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model mistralai/mistral-small-2603)
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
    (maxOutputTokens null)
  ))
  (pricing ({}
    (prompt "0.00000015")
    (completion "0.0000006")
    (input_cache_read "0.000000015")
  ))
  (properties ({}
    (id mistralai/mistral-small-2603)
    (canonical_slug mistralai/mistral-small-2603)
    (hugging_face_id mistralai/Mistral-Small-4-119B-2603)
    (name "Mistral: Mistral Small 4")
    (created 1773695685)
    (description "Mistral Small 4 is the next major release in the Mistral Small family, unifying the capabilities of several flagship Mistral models into a single system. It combines strong reasoning from...")
    (context_length 262144)
    (architecture ({}
      (modality text+image->text)
      (input_modalities (
        text
        image
      ))
      (output_modalities (
        text
      ))
      (tokenizer Mistral)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.00000015")
      (completion "0.0000006")
      (input_cache_read "0.000000015")
    ))
    (top_provider ({}
      (context_length 262144)
      (max_completion_tokens null)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      include_reasoning
      max_tokens
      presence_penalty
      reasoning
      reasoning_effort
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
      (details /api/v1/models/mistralai/mistral-small-2603/endpoints)
    ))
    (benchmarks ({}
      (design_arena ())
      (artificial_analysis ({}
        (intelligence_index 19.7)
        (coding_index 26.6)
        (agentic_index 4.6)
      ))
    ))
    (reasoning ({}
      (mandatory false)
      (default_enabled false)
      (supported_efforts (
        high
        none
      ))
      (default_effort high)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id mistralai/mistral-small-2603)
    (canonical_slug mistralai/mistral-small-2603)
    (hugging_face_id mistralai/Mistral-Small-4-119B-2603)
    (name "Mistral: Mistral Small 4")
    (created 1773695685)
    (description "Mistral Small 4 is the next major release in the Mistral Small family, unifying the capabilities of several flagship Mistral models into a single system. It combines strong reasoning from...")
    (context_length 262144)
    (architecture ({}
      (modality text+image->text)
      (input_modalities (
        text
        image
      ))
      (output_modalities (
        text
      ))
      (tokenizer Mistral)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.00000015")
      (completion "0.0000006")
      (input_cache_read "0.000000015")
    ))
    (top_provider ({}
      (context_length 262144)
      (max_completion_tokens null)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      include_reasoning
      max_tokens
      presence_penalty
      reasoning
      reasoning_effort
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
      (details /api/v1/models/mistralai/mistral-small-2603/endpoints)
    ))
    (benchmarks ({}
      (design_arena ())
      (artificial_analysis ({}
        (intelligence_index 19.7)
        (coding_index 26.6)
        (agentic_index 4.6)
      ))
    ))
    (reasoning ({}
      (mandatory false)
      (default_enabled false)
      (supported_efforts (
        high
        none
      ))
      (default_effort high)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId mistralai/mistral-small-2603)
  ))
)
