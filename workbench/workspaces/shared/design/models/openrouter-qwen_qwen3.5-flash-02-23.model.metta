({}
  (kind model)
  (id openrouter-qwen_qwen3.5-flash-02-23)
  (label "Qwen: Qwen3.5-Flash")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model qwen/qwen3.5-flash-02-23)
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
    (contextWindow 1000000)
    (maxOutputTokens 65536)
  ))
  (pricing ({}
    (prompt "0.000000065")
    (completion "0.00000026")
  ))
  (properties ({}
    (id qwen/qwen3.5-flash-02-23)
    (canonical_slug qwen/qwen3.5-flash-20260224)
    (hugging_face_id null)
    (name "Qwen: Qwen3.5-Flash")
    (created 1772053776)
    (description "The Qwen3.5 native vision-language Flash models are built on a hybrid architecture that integrates a linear attention mechanism with a sparse mixture-of-experts model, achieving higher inference efficiency. Compared to the...")
    (context_length 1000000)
    (architecture ({}
      (modality text+image+video->text)
      (input_modalities (
        text
        image
        video
      ))
      (output_modalities (
        text
      ))
      (tokenizer Qwen3)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.000000065")
      (completion "0.00000026")
    ))
    (top_provider ({}
      (context_length 1000000)
      (max_completion_tokens 65536)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      include_reasoning
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
      top_p
    ))
    (default_parameters ({}
      (temperature null)
      (top_p null)
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/qwen/qwen3.5-flash-20260224/endpoints)
    ))
    (reasoning ({}
      (mandatory false)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id qwen/qwen3.5-flash-02-23)
    (canonical_slug qwen/qwen3.5-flash-20260224)
    (hugging_face_id null)
    (name "Qwen: Qwen3.5-Flash")
    (created 1772053776)
    (description "The Qwen3.5 native vision-language Flash models are built on a hybrid architecture that integrates a linear attention mechanism with a sparse mixture-of-experts model, achieving higher inference efficiency. Compared to the...")
    (context_length 1000000)
    (architecture ({}
      (modality text+image+video->text)
      (input_modalities (
        text
        image
        video
      ))
      (output_modalities (
        text
      ))
      (tokenizer Qwen3)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.000000065")
      (completion "0.00000026")
    ))
    (top_provider ({}
      (context_length 1000000)
      (max_completion_tokens 65536)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      include_reasoning
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
      top_p
    ))
    (default_parameters ({}
      (temperature null)
      (top_p null)
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/qwen/qwen3.5-flash-20260224/endpoints)
    ))
    (reasoning ({}
      (mandatory false)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId qwen/qwen3.5-flash-02-23)
  ))
)
