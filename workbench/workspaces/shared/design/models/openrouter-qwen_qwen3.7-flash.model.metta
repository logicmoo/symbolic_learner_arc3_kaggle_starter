({}
  (kind model)
  (id openrouter-qwen_qwen3.7-flash)
  (label "Qwen: Qwen3.7 Flash")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model qwen/qwen3.7-flash)
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
    (prompt "0.00000003")
    (completion "0.00000013")
    (input_cache_read "0.000000006")
    (input_cache_write "0.000000038")
    (overrides (
      ({}
        (min_prompt_tokens 32000)
        (prompt "0.0000001")
        (completion "0.0000004")
        (input_cache_read "0.00000002")
        (input_cache_write "0.000000125")
      )
      ({}
        (min_prompt_tokens 256000)
        (prompt "0.0000002")
        (completion "0.0000008")
        (input_cache_read "0.00000004")
        (input_cache_write "0.00000025")
      )
    ))
  ))
  (properties ({}
    (id qwen/qwen3.7-flash)
    (canonical_slug qwen/qwen3.7-flash-20260727)
    (hugging_face_id null)
    (name "Qwen: Qwen3.7 Flash")
    (created 1785190561)
    (description "Qwen3.7 Flash is a vision-language reasoning model from Alibaba. It is suited for multimodal agents, visual coding, search, and computer interaction, with strengths in object recognition, spatial understanding, and real-world...")
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
      (tokenizer Qwen)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.00000003")
      (completion "0.00000013")
      (input_cache_read "0.000000006")
      (input_cache_write "0.000000038")
      (overrides (
        ({}
          (min_prompt_tokens 32000)
          (prompt "0.0000001")
          (completion "0.0000004")
          (input_cache_read "0.00000002")
          (input_cache_write "0.000000125")
        )
        ({}
          (min_prompt_tokens 256000)
          (prompt "0.0000002")
          (completion "0.0000008")
          (input_cache_read "0.00000004")
          (input_cache_write "0.00000025")
        )
      ))
    ))
    (top_provider ({}
      (context_length 1000000)
      (max_completion_tokens 65536)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      include_reasoning
      logprobs
      max_tokens
      presence_penalty
      reasoning
      response_format
      seed
      temperature
      tool_choice
      tools
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
      (details /api/v1/models/qwen/qwen3.7-flash-20260727/endpoints)
    ))
    (reasoning ({}
      (mandatory false)
      (default_enabled true)
      (supports_max_tokens true)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id qwen/qwen3.7-flash)
    (canonical_slug qwen/qwen3.7-flash-20260727)
    (hugging_face_id null)
    (name "Qwen: Qwen3.7 Flash")
    (created 1785190561)
    (description "Qwen3.7 Flash is a vision-language reasoning model from Alibaba. It is suited for multimodal agents, visual coding, search, and computer interaction, with strengths in object recognition, spatial understanding, and real-world...")
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
      (tokenizer Qwen)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.00000003")
      (completion "0.00000013")
      (input_cache_read "0.000000006")
      (input_cache_write "0.000000038")
      (overrides (
        ({}
          (min_prompt_tokens 32000)
          (prompt "0.0000001")
          (completion "0.0000004")
          (input_cache_read "0.00000002")
          (input_cache_write "0.000000125")
        )
        ({}
          (min_prompt_tokens 256000)
          (prompt "0.0000002")
          (completion "0.0000008")
          (input_cache_read "0.00000004")
          (input_cache_write "0.00000025")
        )
      ))
    ))
    (top_provider ({}
      (context_length 1000000)
      (max_completion_tokens 65536)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      include_reasoning
      logprobs
      max_tokens
      presence_penalty
      reasoning
      response_format
      seed
      temperature
      tool_choice
      tools
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
      (details /api/v1/models/qwen/qwen3.7-flash-20260727/endpoints)
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
    (remoteModelId qwen/qwen3.7-flash)
  ))
)
