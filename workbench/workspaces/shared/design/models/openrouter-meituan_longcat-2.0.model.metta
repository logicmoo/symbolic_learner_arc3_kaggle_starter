({}
  (kind model)
  (id openrouter-meituan_longcat-2.0)
  (label "Meituan: LongCat 2.0")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model meituan/longcat-2.0)
  (enabled true)
  (capabilities ({}
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
  (limits ({}
    (contextWindow 1048756)
    (maxOutputTokens 262144)
  ))
  (pricing ({}
    (prompt "0.0000003")
    (completion "0.0000012")
    (input_cache_read "0.000000006")
  ))
  (properties ({}
    (id meituan/longcat-2.0)
    (canonical_slug meituan/longcat-2.0-20260720)
    (hugging_face_id meituan-longcat/LongCat-2.0)
    (name "Meituan: LongCat 2.0")
    (created 1784554658)
    (description "LongCat 2.0 is a sparse mixture-of-experts language model from Meituan, with 48B active parameters out of 1.6T total. It is suited for coding, repository-level changes, long-horizon problem solving, and agentic...")
    (context_length 1048756)
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
      (prompt "0.0000003")
      (completion "0.0000012")
      (input_cache_read "0.000000006")
    ))
    (top_provider ({}
      (context_length 1048756)
      (max_completion_tokens 262144)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      include_reasoning
      logit_bias
      max_tokens
      min_p
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
    (default_parameters ({}))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/meituan/longcat-2.0-20260720/endpoints)
    ))
    (reasoning ({}
      (mandatory false)
      (default_enabled true)
      (supports_max_tokens true)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id meituan/longcat-2.0)
    (canonical_slug meituan/longcat-2.0-20260720)
    (hugging_face_id meituan-longcat/LongCat-2.0)
    (name "Meituan: LongCat 2.0")
    (created 1784554658)
    (description "LongCat 2.0 is a sparse mixture-of-experts language model from Meituan, with 48B active parameters out of 1.6T total. It is suited for coding, repository-level changes, long-horizon problem solving, and agentic...")
    (context_length 1048756)
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
      (prompt "0.0000003")
      (completion "0.0000012")
      (input_cache_read "0.000000006")
    ))
    (top_provider ({}
      (context_length 1048756)
      (max_completion_tokens 262144)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      include_reasoning
      logit_bias
      max_tokens
      min_p
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
    (default_parameters ({}))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/meituan/longcat-2.0-20260720/endpoints)
    ))
    (reasoning ({}
      (mandatory false)
      (default_enabled true)
      (supports_max_tokens true)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId meituan/longcat-2.0)
  ))
)
