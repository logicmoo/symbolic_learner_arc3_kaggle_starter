(
  (kind model)
  (id openrouter-amazon_nova-2-lite-v1)
  (label "Amazon: Nova 2 Lite")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model amazon/nova-2-lite-v1)
  (enabled true)
  (capabilities (
    (audio false)
    (code false)
    (functionCalling true)
    (json false)
    (jsonMode false)
    (local false)
    (multimodal true)
    (reasoning true)
    (text true)
    (tools true)
    (vision true)
  ))
  (limits (
    (contextWindow 1000000)
    (maxOutputTokens 65535)
  ))
  (pricing (
    (prompt "0.0000003")
    (completion "0.0000025")
  ))
  (properties (
    (id amazon/nova-2-lite-v1)
    (canonical_slug amazon/nova-2-lite-v1)
    (hugging_face_id "")
    (name "Amazon: Nova 2 Lite")
    (created 1764696672)
    (description "Nova 2 Lite is a fast, cost-effective reasoning model for everyday workloads that can process text, images, and videos to generate text. Nova 2 Lite demonstrates standout capabilities in processing...")
    (context_length 1000000)
    (architecture (
      (modality text+image+file+video->text)
      (input_modalities ([]
        text
        image
        video
        file
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Nova)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.0000003")
      (completion "0.0000025")
    ))
    (top_provider (
      (context_length 1000000)
      (max_completion_tokens 65535)
      (is_moderated true)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      include_reasoning
      max_tokens
      reasoning
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
    (knowledge_cutoff null)
    (expiration_date null)
    (links (
      (details /api/v1/models/amazon/nova-2-lite-v1/endpoints)
    ))
    (benchmarks (
      (design_arena ([]))
      (artificial_analysis (
        (intelligence_index 18.4)
        (coding_index 23)
        (agentic_index 3.1)
      ))
    ))
    (reasoning (
      (mandatory false)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id amazon/nova-2-lite-v1)
    (canonical_slug amazon/nova-2-lite-v1)
    (hugging_face_id "")
    (name "Amazon: Nova 2 Lite")
    (created 1764696672)
    (description "Nova 2 Lite is a fast, cost-effective reasoning model for everyday workloads that can process text, images, and videos to generate text. Nova 2 Lite demonstrates standout capabilities in processing...")
    (context_length 1000000)
    (architecture (
      (modality text+image+file+video->text)
      (input_modalities ([]
        text
        image
        video
        file
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Nova)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.0000003")
      (completion "0.0000025")
    ))
    (top_provider (
      (context_length 1000000)
      (max_completion_tokens 65535)
      (is_moderated true)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      include_reasoning
      max_tokens
      reasoning
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
    (knowledge_cutoff null)
    (expiration_date null)
    (links (
      (details /api/v1/models/amazon/nova-2-lite-v1/endpoints)
    ))
    (benchmarks (
      (design_arena ([]))
      (artificial_analysis (
        (intelligence_index 18.4)
        (coding_index 23)
        (agentic_index 3.1)
      ))
    ))
    (reasoning (
      (mandatory false)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId amazon/nova-2-lite-v1)
  ))
)
