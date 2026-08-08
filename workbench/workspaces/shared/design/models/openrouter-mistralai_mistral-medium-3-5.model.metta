(
  (kind model)
  (id openrouter-mistralai_mistral-medium-3-5)
  (label "Mistral: Mistral Medium 3.5")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model mistralai/mistral-medium-3-5)
  (enabled true)
  (capabilities (
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
  (limits (
    (contextWindow 262144)
    (maxOutputTokens null)
  ))
  (pricing (
    (prompt "0.0000015")
    (completion "0.0000075")
  ))
  (properties (
    (id mistralai/mistral-medium-3-5)
    (canonical_slug mistralai/mistral-medium-3.5-20260430)
    (hugging_face_id null)
    (name "Mistral: Mistral Medium 3.5")
    (created 1777570439)
    (description "Mistral Medium 3.5 is a dense 128B instruction-following model from Mistral AI. It supports text and image inputs with text output, and is designed for agentic workflows, coding, and complex...")
    (context_length 262144)
    (architecture (
      (modality text+image+file->text)
      (input_modalities ([]
        text
        image
        file
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Mistral)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.0000015")
      (completion "0.0000075")
    ))
    (top_provider (
      (context_length 262144)
      (max_completion_tokens null)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
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
      top_p
    ))
    (default_parameters (
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
    (links (
      (details /api/v1/models/mistralai/mistral-medium-3.5-20260430/endpoints)
    ))
    (benchmarks (
      (design_arena ([]))
      (artificial_analysis (
        (intelligence_index 30.4)
        (coding_index 46.9)
        (agentic_index 19.2)
      ))
    ))
    (reasoning (
      (mandatory false)
      (supported_efforts ([]
        high
        none
      ))
      (default_effort high)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id mistralai/mistral-medium-3-5)
    (canonical_slug mistralai/mistral-medium-3.5-20260430)
    (hugging_face_id null)
    (name "Mistral: Mistral Medium 3.5")
    (created 1777570439)
    (description "Mistral Medium 3.5 is a dense 128B instruction-following model from Mistral AI. It supports text and image inputs with text output, and is designed for agentic workflows, coding, and complex...")
    (context_length 262144)
    (architecture (
      (modality text+image+file->text)
      (input_modalities ([]
        text
        image
        file
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Mistral)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.0000015")
      (completion "0.0000075")
    ))
    (top_provider (
      (context_length 262144)
      (max_completion_tokens null)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
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
      top_p
    ))
    (default_parameters (
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
    (links (
      (details /api/v1/models/mistralai/mistral-medium-3.5-20260430/endpoints)
    ))
    (benchmarks (
      (design_arena ([]))
      (artificial_analysis (
        (intelligence_index 30.4)
        (coding_index 46.9)
        (agentic_index 19.2)
      ))
    ))
    (reasoning (
      (mandatory false)
      (supported_efforts ([]
        high
        none
      ))
      (default_effort high)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId mistralai/mistral-medium-3-5)
  ))
)
