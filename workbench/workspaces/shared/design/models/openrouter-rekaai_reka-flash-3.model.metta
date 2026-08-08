(
  (kind model)
  (id openrouter-rekaai_reka-flash-3)
  (label "Reka Flash 3")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model rekaai/reka-flash-3)
  (enabled true)
  (capabilities (
    (audio false)
    (code false)
    (functionCalling false)
    (json true)
    (jsonMode true)
    (local false)
    (multimodal false)
    (reasoning true)
    (text true)
    (tools false)
    (vision false)
  ))
  (limits (
    (contextWindow 65536)
    (maxOutputTokens 65536)
  ))
  (pricing (
    (prompt "0.0000001")
    (completion "0.0000002")
  ))
  (properties (
    (id rekaai/reka-flash-3)
    (canonical_slug rekaai/reka-flash-3)
    (hugging_face_id RekaAI/reka-flash-3)
    (name "Reka Flash 3")
    (created 1741812813)
    (description "Reka Flash 3 is a general-purpose, instruction-tuned large language model with 21 billion parameters, developed by Reka. It excels at general chat, coding tasks, instruction-following, and function calling. Featuring a...")
    (context_length 65536)
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
      (prompt "0.0000001")
      (completion "0.0000002")
    ))
    (top_provider (
      (context_length 65536)
      (max_completion_tokens 65536)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      frequency_penalty
      include_reasoning
      logprobs
      max_tokens
      presence_penalty
      reasoning
      seed
      stop
      structured_outputs
      temperature
      top_k
      top_logprobs
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
    (knowledge_cutoff 2025-01-31)
    (expiration_date null)
    (links (
      (details /api/v1/models/rekaai/reka-flash-3/endpoints)
    ))
    (reasoning (
      (mandatory true)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id rekaai/reka-flash-3)
    (canonical_slug rekaai/reka-flash-3)
    (hugging_face_id RekaAI/reka-flash-3)
    (name "Reka Flash 3")
    (created 1741812813)
    (description "Reka Flash 3 is a general-purpose, instruction-tuned large language model with 21 billion parameters, developed by Reka. It excels at general chat, coding tasks, instruction-following, and function calling. Featuring a...")
    (context_length 65536)
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
      (prompt "0.0000001")
      (completion "0.0000002")
    ))
    (top_provider (
      (context_length 65536)
      (max_completion_tokens 65536)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      frequency_penalty
      include_reasoning
      logprobs
      max_tokens
      presence_penalty
      reasoning
      seed
      stop
      structured_outputs
      temperature
      top_k
      top_logprobs
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
    (knowledge_cutoff 2025-01-31)
    (expiration_date null)
    (links (
      (details /api/v1/models/rekaai/reka-flash-3/endpoints)
    ))
    (reasoning (
      (mandatory true)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId rekaai/reka-flash-3)
  ))
)
