({}
  (kind model)
  (id openrouter-inclusionai_ling-2.6-flash)
  (label "inclusionAI: Ling-2.6-flash")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model inclusionai/ling-2.6-flash)
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
    (contextWindow 262144)
    (maxOutputTokens 32768)
  ))
  (pricing ({}
    (prompt "0.00000001")
    (completion "0.00000003")
    (input_cache_read "0.000000002")
  ))
  (properties ({}
    (id inclusionai/ling-2.6-flash)
    (canonical_slug inclusionai/ling-2.6-flash-20260421)
    (hugging_face_id "")
    (name "inclusionAI: Ling-2.6-flash")
    (created 1776795886)
    (description "Ling-2.6-flash is an instant (instruct) model from inclusionAI with 104B total parameters and 7.4B active parameters, designed for real-world agents that require fast responses, strong execution, and high token efficiency....")
    (context_length 262144)
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
      (prompt "0.00000001")
      (completion "0.00000003")
      (input_cache_read "0.000000002")
    ))
    (top_provider ({}
      (context_length 262144)
      (max_completion_tokens 32768)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      logprobs
      max_tokens
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
      top_logprobs
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
      (details /api/v1/models/inclusionai/ling-2.6-flash-20260421/endpoints)
    ))
    (benchmarks ({}
      (design_arena ())
      (artificial_analysis ({}
        (intelligence_index 14.2)
        (coding_index 25.3)
        (agentic_index 2.3)
      ))
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id inclusionai/ling-2.6-flash)
    (canonical_slug inclusionai/ling-2.6-flash-20260421)
    (hugging_face_id "")
    (name "inclusionAI: Ling-2.6-flash")
    (created 1776795886)
    (description "Ling-2.6-flash is an instant (instruct) model from inclusionAI with 104B total parameters and 7.4B active parameters, designed for real-world agents that require fast responses, strong execution, and high token efficiency....")
    (context_length 262144)
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
      (prompt "0.00000001")
      (completion "0.00000003")
      (input_cache_read "0.000000002")
    ))
    (top_provider ({}
      (context_length 262144)
      (max_completion_tokens 32768)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      logprobs
      max_tokens
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
      top_logprobs
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
      (details /api/v1/models/inclusionai/ling-2.6-flash-20260421/endpoints)
    ))
    (benchmarks ({}
      (design_arena ())
      (artificial_analysis ({}
        (intelligence_index 14.2)
        (coding_index 25.3)
        (agentic_index 2.3)
      ))
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId inclusionai/ling-2.6-flash)
  ))
)
