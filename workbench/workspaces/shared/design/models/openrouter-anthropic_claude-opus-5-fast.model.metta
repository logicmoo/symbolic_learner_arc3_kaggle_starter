({}
  (kind model)
  (id openrouter-anthropic_claude-opus-5-fast)
  (label "Claude Opus 5 (Fast)")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model anthropic/claude-opus-5-fast)
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
    (maxOutputTokens 128000)
  ))
  (pricing ({}
    (prompt "0.00001")
    (completion "0.00005")
    (web_search "0.01")
    (input_cache_read "0.000001")
    (input_cache_write "0.0000125")
    (input_cache_write_1h "0.00002")
  ))
  (properties ({}
    (id anthropic/claude-opus-5-fast)
    (canonical_slug anthropic/claude-opus-5-fast-20260723)
    (hugging_face_id null)
    (name "Claude Opus 5 (Fast)")
    (created 1784912546)
    (description "Fast-mode variant of [Opus 5](/anthropic/claude-opus-5) - identical capabilities with higher output speed at 2x pricing relative to regular Opus 5.\n\nLearn more in Anthropic's docs: https://platform.claude.com/docs/en/build-with-claude/fast-mode")
    (context_length 1000000)
    (architecture ({}
      (modality text+image+file->text)
      (input_modalities (
        text
        image
        file
      ))
      (output_modalities (
        text
      ))
      (tokenizer Claude)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.00001")
      (completion "0.00005")
      (web_search "0.01")
      (input_cache_read "0.000001")
      (input_cache_write "0.0000125")
      (input_cache_write_1h "0.00002")
    ))
    (top_provider ({}
      (context_length 1000000)
      (max_completion_tokens 128000)
      (is_moderated true)
    ))
    (per_request_limits null)
    (supported_parameters (
      include_reasoning
      max_tokens
      reasoning
      reasoning_effort
      response_format
      stop
      structured_outputs
      tool_choice
      tools
      verbosity
    ))
    (default_parameters ({}))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/anthropic/claude-opus-5-fast-20260723/endpoints)
    ))
    (reasoning ({}
      (mandatory false)
      (default_enabled true)
      (supported_efforts (
        max
        xhigh
        high
        medium
        low
      ))
      (default_effort high)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id anthropic/claude-opus-5-fast)
    (canonical_slug anthropic/claude-opus-5-fast-20260723)
    (hugging_face_id null)
    (name "Claude Opus 5 (Fast)")
    (created 1784912546)
    (description "Fast-mode variant of [Opus 5](/anthropic/claude-opus-5) - identical capabilities with higher output speed at 2x pricing relative to regular Opus 5.\n\nLearn more in Anthropic's docs: https://platform.claude.com/docs/en/build-with-claude/fast-mode")
    (context_length 1000000)
    (architecture ({}
      (modality text+image+file->text)
      (input_modalities (
        text
        image
        file
      ))
      (output_modalities (
        text
      ))
      (tokenizer Claude)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.00001")
      (completion "0.00005")
      (web_search "0.01")
      (input_cache_read "0.000001")
      (input_cache_write "0.0000125")
      (input_cache_write_1h "0.00002")
    ))
    (top_provider ({}
      (context_length 1000000)
      (max_completion_tokens 128000)
      (is_moderated true)
    ))
    (per_request_limits null)
    (supported_parameters (
      include_reasoning
      max_tokens
      reasoning
      reasoning_effort
      response_format
      stop
      structured_outputs
      tool_choice
      tools
      verbosity
    ))
    (default_parameters ({}))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/anthropic/claude-opus-5-fast-20260723/endpoints)
    ))
    (reasoning ({}
      (mandatory false)
      (default_enabled true)
      (supported_efforts (
        max
        xhigh
        high
        medium
        low
      ))
      (default_effort high)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId anthropic/claude-opus-5-fast)
  ))
)
