({}
  (kind model)
  (id openrouter-qwen_qwen3-vl-8b-thinking)
  (label "Qwen: Qwen3 VL 8B Thinking")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model qwen/qwen3-vl-8b-thinking)
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
    (contextWindow 131072)
    (maxOutputTokens 32768)
  ))
  (pricing ({}
    (prompt "0.00000018")
    (completion "0.0000021")
  ))
  (properties ({}
    (id qwen/qwen3-vl-8b-thinking)
    (canonical_slug qwen/qwen3-vl-8b-thinking)
    (hugging_face_id Qwen/Qwen3-VL-8B-Thinking)
    (name "Qwen: Qwen3 VL 8B Thinking")
    (created 1760463746)
    (description "Qwen3-VL-8B-Thinking is the reasoning-optimized variant of the Qwen3-VL-8B multimodal model, designed for advanced visual and textual reasoning across complex scenes, documents, and temporal sequences. It integrates enhanced multimodal alignment and...")
    (context_length 131072)
    (architecture ({}
      (modality text+image->text)
      (input_modalities (
        image
        text
      ))
      (output_modalities (
        text
      ))
      (tokenizer Qwen3)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.00000018")
      (completion "0.0000021")
    ))
    (top_provider ({}
      (context_length 131072)
      (max_completion_tokens 32768)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      include_reasoning
      logprobs
      max_tokens
      presence_penalty
      reasoning
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
      (temperature 1)
      (top_p 0.95)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/qwen/qwen3-vl-8b-thinking/endpoints)
    ))
    (reasoning ({}
      (mandatory true)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id qwen/qwen3-vl-8b-thinking)
    (canonical_slug qwen/qwen3-vl-8b-thinking)
    (hugging_face_id Qwen/Qwen3-VL-8B-Thinking)
    (name "Qwen: Qwen3 VL 8B Thinking")
    (created 1760463746)
    (description "Qwen3-VL-8B-Thinking is the reasoning-optimized variant of the Qwen3-VL-8B multimodal model, designed for advanced visual and textual reasoning across complex scenes, documents, and temporal sequences. It integrates enhanced multimodal alignment and...")
    (context_length 131072)
    (architecture ({}
      (modality text+image->text)
      (input_modalities (
        image
        text
      ))
      (output_modalities (
        text
      ))
      (tokenizer Qwen3)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.00000018")
      (completion "0.0000021")
    ))
    (top_provider ({}
      (context_length 131072)
      (max_completion_tokens 32768)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      include_reasoning
      logprobs
      max_tokens
      presence_penalty
      reasoning
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
      (temperature 1)
      (top_p 0.95)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/qwen/qwen3-vl-8b-thinking/endpoints)
    ))
    (reasoning ({}
      (mandatory true)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId qwen/qwen3-vl-8b-thinking)
  ))
)
