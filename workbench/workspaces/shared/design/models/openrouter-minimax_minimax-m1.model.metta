(
  (kind model)
  (id openrouter-minimax_minimax-m1)
  (label "MiniMax: MiniMax M1")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model minimax/minimax-m1)
  (enabled true)
  (capabilities (
    (audio false)
    (code false)
    (functionCalling true)
    (json false)
    (jsonMode false)
    (local false)
    (multimodal false)
    (reasoning true)
    (text true)
    (tools true)
    (vision false)
  ))
  (limits (
    (contextWindow 1000000)
    (maxOutputTokens 40000)
  ))
  (pricing (
    (prompt "0.00000055")
    (completion "0.0000022")
  ))
  (properties (
    (id minimax/minimax-m1)
    (canonical_slug minimax/minimax-m1)
    (hugging_face_id "")
    (name "MiniMax: MiniMax M1")
    (created 1750200414)
    (description "MiniMax-M1 is a large-scale, open-weight reasoning model designed for extended context and high-efficiency inference. It leverages a hybrid Mixture-of-Experts (MoE) architecture paired with a custom \"lightning attention\" mechanism, allowing it...")
    (context_length 1000000)
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
      (prompt "0.00000055")
      (completion "0.0000022")
    ))
    (top_provider (
      (context_length 1000000)
      (max_completion_tokens 40000)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      frequency_penalty
      include_reasoning
      max_tokens
      presence_penalty
      reasoning
      repetition_penalty
      seed
      stop
      temperature
      tool_choice
      tools
      top_k
      top_p
    ))
    (default_parameters (
      (temperature null)
      (top_p null)
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff 2024-06-30)
    (expiration_date null)
    (links (
      (details /api/v1/models/minimax/minimax-m1/endpoints)
    ))
    (reasoning (
      (mandatory false)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id minimax/minimax-m1)
    (canonical_slug minimax/minimax-m1)
    (hugging_face_id "")
    (name "MiniMax: MiniMax M1")
    (created 1750200414)
    (description "MiniMax-M1 is a large-scale, open-weight reasoning model designed for extended context and high-efficiency inference. It leverages a hybrid Mixture-of-Experts (MoE) architecture paired with a custom \"lightning attention\" mechanism, allowing it...")
    (context_length 1000000)
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
      (prompt "0.00000055")
      (completion "0.0000022")
    ))
    (top_provider (
      (context_length 1000000)
      (max_completion_tokens 40000)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      frequency_penalty
      include_reasoning
      max_tokens
      presence_penalty
      reasoning
      repetition_penalty
      seed
      stop
      temperature
      tool_choice
      tools
      top_k
      top_p
    ))
    (default_parameters (
      (temperature null)
      (top_p null)
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff 2024-06-30)
    (expiration_date null)
    (links (
      (details /api/v1/models/minimax/minimax-m1/endpoints)
    ))
    (reasoning (
      (mandatory false)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId minimax/minimax-m1)
  ))
)
