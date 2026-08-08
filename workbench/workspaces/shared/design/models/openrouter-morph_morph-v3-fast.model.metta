(
  (kind model)
  (id openrouter-morph_morph-v3-fast)
  (label "Morph: Morph V3 Fast")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model morph/morph-v3-fast)
  (enabled true)
  (capabilities (
    (audio false)
    (code false)
    (functionCalling false)
    (json false)
    (jsonMode false)
    (local false)
    (multimodal false)
    (reasoning false)
    (text true)
    (tools false)
    (vision false)
  ))
  (limits (
    (contextWindow 81920)
    (maxOutputTokens 38000)
  ))
  (pricing (
    (prompt "0.0000008")
    (completion "0.0000012")
  ))
  (properties (
    (id morph/morph-v3-fast)
    (canonical_slug morph/morph-v3-fast)
    (hugging_face_id "")
    (name "Morph: Morph V3 Fast")
    (created 1751910002)
    (description "Morph's fastest apply model for code edits. ~10,500 tokens/sec with 96% accuracy for rapid code transformations. The model requires the prompt to be in the following format: <instruction>{instruction}</instruction> <code>{initial_code}</code> <update>{edit_snippet}</update>...")
    (context_length 81920)
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
      (prompt "0.0000008")
      (completion "0.0000012")
    ))
    (top_provider (
      (context_length 81920)
      (max_completion_tokens 38000)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      max_tokens
      stop
      temperature
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
      (details /api/v1/models/morph/morph-v3-fast/endpoints)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id morph/morph-v3-fast)
    (canonical_slug morph/morph-v3-fast)
    (hugging_face_id "")
    (name "Morph: Morph V3 Fast")
    (created 1751910002)
    (description "Morph's fastest apply model for code edits. ~10,500 tokens/sec with 96% accuracy for rapid code transformations. The model requires the prompt to be in the following format: <instruction>{instruction}</instruction> <code>{initial_code}</code> <update>{edit_snippet}</update>...")
    (context_length 81920)
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
      (prompt "0.0000008")
      (completion "0.0000012")
    ))
    (top_provider (
      (context_length 81920)
      (max_completion_tokens 38000)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      max_tokens
      stop
      temperature
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
      (details /api/v1/models/morph/morph-v3-fast/endpoints)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId morph/morph-v3-fast)
  ))
)
