({}
  (kind model)
  (id openrouter-x-ai_grok-build-0.1)
  (label "SpaceXAI: Grok Build 0.1")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model x-ai/grok-build-0.1)
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
    (contextWindow 256000)
    (maxOutputTokens null)
  ))
  (pricing ({}
    (prompt "0.000001")
    (completion "0.000002")
    (web_search "0.005")
    (input_cache_read "0.0000002")
    (overrides (
      ({}
        (min_prompt_tokens 200000)
        (prompt "0.000002")
        (completion "0.000004")
        (input_cache_read "0.0000004")
      )
    ))
  ))
  (properties ({}
    (id x-ai/grok-build-0.1)
    (canonical_slug x-ai/grok-build-0.1-20260520)
    (hugging_face_id null)
    (name "SpaceXAI: Grok Build 0.1")
    (created 1779298123)
    (description "Grok Build 0.1 is SpaceXAI’s fast coding model trained specifically for agentic software engineering workflows. It supports text and image inputs with text output, and is optimized for interactive coding...")
    (context_length 256000)
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
      (tokenizer Grok)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.000001")
      (completion "0.000002")
      (web_search "0.005")
      (input_cache_read "0.0000002")
      (overrides (
        ({}
          (min_prompt_tokens 200000)
          (prompt "0.000002")
          (completion "0.000004")
          (input_cache_read "0.0000004")
        )
      ))
    ))
    (top_provider ({}
      (context_length 256000)
      (max_completion_tokens null)
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
      (details /api/v1/models/x-ai/grok-build-0.1-20260520/endpoints)
    ))
    (benchmarks ({}
      (design_arena ())
      (artificial_analysis ({}
        (intelligence_index 40.7)
        (coding_index 51.5)
        (agentic_index 28.9)
      ))
    ))
    (reasoning ({}
      (mandatory true)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id x-ai/grok-build-0.1)
    (canonical_slug x-ai/grok-build-0.1-20260520)
    (hugging_face_id null)
    (name "SpaceXAI: Grok Build 0.1")
    (created 1779298123)
    (description "Grok Build 0.1 is SpaceXAI’s fast coding model trained specifically for agentic software engineering workflows. It supports text and image inputs with text output, and is optimized for interactive coding...")
    (context_length 256000)
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
      (tokenizer Grok)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.000001")
      (completion "0.000002")
      (web_search "0.005")
      (input_cache_read "0.0000002")
      (overrides (
        ({}
          (min_prompt_tokens 200000)
          (prompt "0.000002")
          (completion "0.000004")
          (input_cache_read "0.0000004")
        )
      ))
    ))
    (top_provider ({}
      (context_length 256000)
      (max_completion_tokens null)
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
      (details /api/v1/models/x-ai/grok-build-0.1-20260520/endpoints)
    ))
    (benchmarks ({}
      (design_arena ())
      (artificial_analysis ({}
        (intelligence_index 40.7)
        (coding_index 51.5)
        (agentic_index 28.9)
      ))
    ))
    (reasoning ({}
      (mandatory true)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId x-ai/grok-build-0.1)
  ))
)
