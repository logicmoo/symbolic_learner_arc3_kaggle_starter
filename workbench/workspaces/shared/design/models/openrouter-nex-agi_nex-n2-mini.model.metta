({}
  (kind model)
  (id openrouter-nex-agi_nex-n2-mini)
  (label "Nex AGI: Nex-N2-Mini")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model nex-agi/nex-n2-mini)
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
    (maxOutputTokens 262144)
  ))
  (pricing ({}
    (prompt "0.000000025")
    (completion "0.0000001")
    (input_cache_read "0.0000000025")
  ))
  (properties ({}
    (id nex-agi/nex-n2-mini)
    (canonical_slug nex-agi/nex-n2-mini)
    (hugging_face_id nex-agi/Nex-N2-Mini)
    (name "Nex AGI: Nex-N2-Mini")
    (created 1782312964)
    (description "Nex-N2-Mini is an open-source agentic mixture-of-experts model from Nex AGI, the smaller sibling in the Nex-N2 series. It accepts text and image input and is built for coding, tool use,...")
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
      (tokenizer Qwen3)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.000000025")
      (completion "0.0000001")
      (input_cache_read "0.0000000025")
    ))
    (top_provider ({}
      (context_length 262144)
      (max_completion_tokens 262144)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      include_reasoning
      logprobs
      max_tokens
      reasoning
      response_format
      structured_outputs
      temperature
      tool_choice
      tools
      top_k
      top_logprobs
      top_p
    ))
    (default_parameters ({}
      (temperature 0.7)
      (top_p 0.95)
      (top_k 40)
      (frequency_penalty null)
      (presence_penalty null)
      (repetition_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/nex-agi/nex-n2-mini/endpoints)
    ))
    (reasoning ({}
      (mandatory false)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id nex-agi/nex-n2-mini)
    (canonical_slug nex-agi/nex-n2-mini)
    (hugging_face_id nex-agi/Nex-N2-Mini)
    (name "Nex AGI: Nex-N2-Mini")
    (created 1782312964)
    (description "Nex-N2-Mini is an open-source agentic mixture-of-experts model from Nex AGI, the smaller sibling in the Nex-N2 series. It accepts text and image input and is built for coding, tool use,...")
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
      (tokenizer Qwen3)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.000000025")
      (completion "0.0000001")
      (input_cache_read "0.0000000025")
    ))
    (top_provider ({}
      (context_length 262144)
      (max_completion_tokens 262144)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      include_reasoning
      logprobs
      max_tokens
      reasoning
      response_format
      structured_outputs
      temperature
      tool_choice
      tools
      top_k
      top_logprobs
      top_p
    ))
    (default_parameters ({}
      (temperature 0.7)
      (top_p 0.95)
      (top_k 40)
      (frequency_penalty null)
      (presence_penalty null)
      (repetition_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/nex-agi/nex-n2-mini/endpoints)
    ))
    (reasoning ({}
      (mandatory false)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId nex-agi/nex-n2-mini)
  ))
)
