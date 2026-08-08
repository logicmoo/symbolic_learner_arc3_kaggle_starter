({}
  (kind model)
  (id openrouter-_google_gemini-pro-latest)
  (label "Google Gemini Pro Latest")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model ~google/gemini-pro-latest)
  (enabled true)
  (capabilities ({}
    (audio true)
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
    (contextWindow 1048576)
    (maxOutputTokens 65536)
  ))
  (pricing ({}
    (prompt "0.000002")
    (completion "0.000012")
    (image "0.000002")
    (audio "0.000002")
    (input_audio_cache "0.0000002")
    (web_search "0.014")
    (internal_reasoning "0.000012")
    (input_cache_read "0.0000002")
    (input_cache_write "0.000000375")
    (overrides (
      ({}
        (min_prompt_tokens 200000)
        (prompt "0.000004")
        (completion "0.000018")
        (audio "0.000004")
        (input_audio_cache "0.0000004")
        (input_cache_read "0.0000004")
      )
    ))
  ))
  (properties ({}
    (id ~google/gemini-pro-latest)
    (canonical_slug ~google/gemini-pro-latest)
    (alias_target ({}
      (name "Google: Gemini 3.1 Pro Preview")
      (slug google/gemini-3.1-pro-preview)
    ))
    (hugging_face_id null)
    (name "Google Gemini Pro Latest")
    (created 1777318451)
    (description "This model always redirects to the latest model in the Google Gemini Pro family.")
    (context_length 1048576)
    (architecture ({}
      (modality text+image+file+audio+video->text)
      (input_modalities (
        audio
        file
        image
        text
        video
      ))
      (output_modalities (
        text
      ))
      (tokenizer Router)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.000002")
      (completion "0.000012")
      (image "0.000002")
      (audio "0.000002")
      (input_audio_cache "0.0000002")
      (web_search "0.014")
      (internal_reasoning "0.000012")
      (input_cache_read "0.0000002")
      (input_cache_write "0.000000375")
      (overrides (
        ({}
          (min_prompt_tokens 200000)
          (prompt "0.000004")
          (completion "0.000018")
          (audio "0.000004")
          (input_audio_cache "0.0000004")
          (input_cache_read "0.0000004")
        )
      ))
    ))
    (top_provider ({}
      (context_length 1048576)
      (max_completion_tokens 65536)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      include_reasoning
      max_tokens
      reasoning
      reasoning_effort
      response_format
      seed
      stop
      structured_outputs
      temperature
      tool_choice
      tools
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
      (details /api/v1/models/~google/gemini-pro-latest/endpoints)
    ))
    (reasoning ({}
      (mandatory true)
      (supported_efforts (
        high
        medium
        low
      ))
      (default_effort medium)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id ~google/gemini-pro-latest)
    (canonical_slug ~google/gemini-pro-latest)
    (alias_target ({}
      (name "Google: Gemini 3.1 Pro Preview")
      (slug google/gemini-3.1-pro-preview)
    ))
    (hugging_face_id null)
    (name "Google Gemini Pro Latest")
    (created 1777318451)
    (description "This model always redirects to the latest model in the Google Gemini Pro family.")
    (context_length 1048576)
    (architecture ({}
      (modality text+image+file+audio+video->text)
      (input_modalities (
        audio
        file
        image
        text
        video
      ))
      (output_modalities (
        text
      ))
      (tokenizer Router)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.000002")
      (completion "0.000012")
      (image "0.000002")
      (audio "0.000002")
      (input_audio_cache "0.0000002")
      (web_search "0.014")
      (internal_reasoning "0.000012")
      (input_cache_read "0.0000002")
      (input_cache_write "0.000000375")
      (overrides (
        ({}
          (min_prompt_tokens 200000)
          (prompt "0.000004")
          (completion "0.000018")
          (audio "0.000004")
          (input_audio_cache "0.0000004")
          (input_cache_read "0.0000004")
        )
      ))
    ))
    (top_provider ({}
      (context_length 1048576)
      (max_completion_tokens 65536)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      include_reasoning
      max_tokens
      reasoning
      reasoning_effort
      response_format
      seed
      stop
      structured_outputs
      temperature
      tool_choice
      tools
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
      (details /api/v1/models/~google/gemini-pro-latest/endpoints)
    ))
    (reasoning ({}
      (mandatory true)
      (supported_efforts (
        high
        medium
        low
      ))
      (default_effort medium)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId ~google/gemini-pro-latest)
  ))
)
