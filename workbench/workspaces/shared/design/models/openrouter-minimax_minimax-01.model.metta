({}
  (kind model)
  (id openrouter-minimax_minimax-01)
  (label "MiniMax: MiniMax-01")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model minimax/minimax-01)
  (enabled true)
  (capabilities ({}
    (audio false)
    (code false)
    (functionCalling false)
    (json false)
    (jsonMode false)
    (local false)
    (multimodal true)
    (reasoning false)
    (text true)
    (tools false)
    (vision true)
  ))
  (limits ({}
    (contextWindow 1000192)
    (maxOutputTokens 1000192)
  ))
  (pricing ({}
    (prompt "0.0000002")
    (completion "0.0000011")
  ))
  (properties ({}
    (id minimax/minimax-01)
    (canonical_slug minimax/minimax-01)
    (hugging_face_id MiniMaxAI/MiniMax-Text-01)
    (name "MiniMax: MiniMax-01")
    (created 1736915462)
    (description "MiniMax-01 is a combines MiniMax-Text-01 for text generation and MiniMax-VL-01 for image understanding. It has 456 billion parameters, with 45.9 billion parameters activated per inference, and can handle a context...")
    (context_length 1000192)
    (architecture ({}
      (modality text+image->text)
      (input_modalities (
        text
        image
      ))
      (output_modalities (
        text
      ))
      (tokenizer Other)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.0000002")
      (completion "0.0000011")
    ))
    (top_provider ({}
      (context_length 1000192)
      (max_completion_tokens 1000192)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      max_tokens
      temperature
      top_p
    ))
    (default_parameters ({}
      (temperature null)
      (top_p null)
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff 2024-03-31)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/minimax/minimax-01/endpoints)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id minimax/minimax-01)
    (canonical_slug minimax/minimax-01)
    (hugging_face_id MiniMaxAI/MiniMax-Text-01)
    (name "MiniMax: MiniMax-01")
    (created 1736915462)
    (description "MiniMax-01 is a combines MiniMax-Text-01 for text generation and MiniMax-VL-01 for image understanding. It has 456 billion parameters, with 45.9 billion parameters activated per inference, and can handle a context...")
    (context_length 1000192)
    (architecture ({}
      (modality text+image->text)
      (input_modalities (
        text
        image
      ))
      (output_modalities (
        text
      ))
      (tokenizer Other)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.0000002")
      (completion "0.0000011")
    ))
    (top_provider ({}
      (context_length 1000192)
      (max_completion_tokens 1000192)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      max_tokens
      temperature
      top_p
    ))
    (default_parameters ({}
      (temperature null)
      (top_p null)
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff 2024-03-31)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/minimax/minimax-01/endpoints)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId minimax/minimax-01)
  ))
)
