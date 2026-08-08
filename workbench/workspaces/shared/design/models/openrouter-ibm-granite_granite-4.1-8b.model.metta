({}
  (kind model)
  (id openrouter-ibm-granite_granite-4.1-8b)
  (label "IBM: Granite 4.1 8B")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model ibm-granite/granite-4.1-8b)
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
    (contextWindow 131072)
    (maxOutputTokens 131072)
  ))
  (pricing ({}
    (prompt "0.00000005")
    (completion "0.0000001")
    (input_cache_read "0.00000005")
  ))
  (properties ({}
    (id ibm-granite/granite-4.1-8b)
    (canonical_slug ibm-granite/granite-4.1-8b-20260429)
    (hugging_face_id ibm-granite/granite-4.1-8b)
    (name "IBM: Granite 4.1 8B")
    (created 1777577071)
    (description "Granite 4.1 8B is a dense, decoder-only 8-billion-parameter language model from IBM, part of the Granite 4.1 family. It supports a 131K-token context window and is designed for enterprise tasks...")
    (context_length 131072)
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
      (prompt "0.00000005")
      (completion "0.0000001")
      (input_cache_read "0.00000005")
    ))
    (top_provider ({}
      (context_length 131072)
      (max_completion_tokens 131072)
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
      (details /api/v1/models/ibm-granite/granite-4.1-8b-20260429/endpoints)
    ))
    (benchmarks ({}
      (design_arena ())
      (artificial_analysis ({}
        (intelligence_index null)
        (coding_index 9.5)
        (agentic_index null)
      ))
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id ibm-granite/granite-4.1-8b)
    (canonical_slug ibm-granite/granite-4.1-8b-20260429)
    (hugging_face_id ibm-granite/granite-4.1-8b)
    (name "IBM: Granite 4.1 8B")
    (created 1777577071)
    (description "Granite 4.1 8B is a dense, decoder-only 8-billion-parameter language model from IBM, part of the Granite 4.1 family. It supports a 131K-token context window and is designed for enterprise tasks...")
    (context_length 131072)
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
      (prompt "0.00000005")
      (completion "0.0000001")
      (input_cache_read "0.00000005")
    ))
    (top_provider ({}
      (context_length 131072)
      (max_completion_tokens 131072)
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
      (details /api/v1/models/ibm-granite/granite-4.1-8b-20260429/endpoints)
    ))
    (benchmarks ({}
      (design_arena ())
      (artificial_analysis ({}
        (intelligence_index null)
        (coding_index 9.5)
        (agentic_index null)
      ))
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId ibm-granite/granite-4.1-8b)
  ))
)
