({}
  (kind model)
  (id openrouter-arcee-ai_virtuoso-large)
  (label "Arcee AI: Virtuoso Large")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model arcee-ai/virtuoso-large)
  (enabled true)
  (capabilities ({}
    (audio false)
    (code false)
    (functionCalling true)
    (json false)
    (jsonMode false)
    (local false)
    (multimodal false)
    (reasoning false)
    (text true)
    (tools true)
    (vision false)
  ))
  (limits ({}
    (contextWindow 131072)
    (maxOutputTokens 64000)
  ))
  (pricing ({}
    (prompt "0.00000075")
    (completion "0.0000012")
  ))
  (properties ({}
    (id arcee-ai/virtuoso-large)
    (canonical_slug arcee-ai/virtuoso-large)
    (hugging_face_id "")
    (name "Arcee AI: Virtuoso Large")
    (created 1746478885)
    (description "Virtuoso‑Large is Arcee's top‑tier general‑purpose LLM at 72 B parameters, tuned to tackle cross‑domain reasoning, creative writing and enterprise QA. Unlike many 70 B peers, it retains the 128 k...")
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
      (prompt "0.00000075")
      (completion "0.0000012")
    ))
    (top_provider ({}
      (context_length 131072)
      (max_completion_tokens 64000)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      logit_bias
      max_tokens
      min_p
      presence_penalty
      repetition_penalty
      stop
      temperature
      tool_choice
      tools
      top_k
      top_p
    ))
    (default_parameters ({}))
    (supported_voices null)
    (knowledge_cutoff 2025-03-31)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/arcee-ai/virtuoso-large/endpoints)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id arcee-ai/virtuoso-large)
    (canonical_slug arcee-ai/virtuoso-large)
    (hugging_face_id "")
    (name "Arcee AI: Virtuoso Large")
    (created 1746478885)
    (description "Virtuoso‑Large is Arcee's top‑tier general‑purpose LLM at 72 B parameters, tuned to tackle cross‑domain reasoning, creative writing and enterprise QA. Unlike many 70 B peers, it retains the 128 k...")
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
      (prompt "0.00000075")
      (completion "0.0000012")
    ))
    (top_provider ({}
      (context_length 131072)
      (max_completion_tokens 64000)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      logit_bias
      max_tokens
      min_p
      presence_penalty
      repetition_penalty
      stop
      temperature
      tool_choice
      tools
      top_k
      top_p
    ))
    (default_parameters ({}))
    (supported_voices null)
    (knowledge_cutoff 2025-03-31)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/arcee-ai/virtuoso-large/endpoints)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId arcee-ai/virtuoso-large)
  ))
)
