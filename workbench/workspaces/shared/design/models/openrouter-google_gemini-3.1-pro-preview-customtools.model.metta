(
  (kind model)
  (id openrouter-google_gemini-3.1-pro-preview-customtools)
  (label "Google: Gemini 3.1 Pro Preview Custom Tools")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model google/gemini-3.1-pro-preview-customtools)
  (enabled true)
  (capabilities (
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
  (limits (
    (contextWindow 1048576)
    (maxOutputTokens 65536)
  ))
  (pricing (
    (prompt "0.000002")
    (completion "0.000012")
    (image "0.000002")
    (audio "0.000002")
    (input_audio_cache "0.0000002")
    (web_search "0.014")
    (internal_reasoning "0.000012")
    (input_cache_read "0.0000002")
    (input_cache_write "0.000000375")
    (overrides ([]
      (
        (min_prompt_tokens 200000)
        (prompt "0.000004")
        (completion "0.000018")
        (audio "0.000004")
        (input_audio_cache "0.0000004")
        (input_cache_read "0.0000004")
      )
    ))
  ))
  (properties (
    (id google/gemini-3.1-pro-preview-customtools)
    (canonical_slug google/gemini-3.1-pro-preview-customtools-20260219)
    (hugging_face_id null)
    (name "Google: Gemini 3.1 Pro Preview Custom Tools")
    (created 1772045923)
    (description "Gemini 3.1 Pro Preview Custom Tools is a variant of Gemini 3.1 Pro that improves tool selection behavior by preventing overuse of a general bash tool when more efficient third-party...")
    (context_length 1048576)
    (architecture (
      (modality text+image+file+audio+video->text)
      (input_modalities ([]
        text
        audio
        image
        video
        file
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Gemini)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.000002")
      (completion "0.000012")
      (image "0.000002")
      (audio "0.000002")
      (input_audio_cache "0.0000002")
      (web_search "0.014")
      (internal_reasoning "0.000012")
      (input_cache_read "0.0000002")
      (input_cache_write "0.000000375")
      (overrides ([]
        (
          (min_prompt_tokens 200000)
          (prompt "0.000004")
          (completion "0.000018")
          (audio "0.000004")
          (input_audio_cache "0.0000004")
          (input_cache_read "0.0000004")
        )
      ))
    ))
    (top_provider (
      (context_length 1048576)
      (max_completion_tokens 65536)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      include_reasoning
      max_tokens
      reasoning
      reasoning_effort
      response_format
      seed
      structured_outputs
      temperature
      tool_choice
      tools
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
      (details /api/v1/models/google/gemini-3.1-pro-preview-customtools-20260219/endpoints)
    ))
    (reasoning (
      (mandatory true)
      (supported_efforts ([]
        high
        medium
        low
      ))
      (default_effort medium)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id google/gemini-3.1-pro-preview-customtools)
    (canonical_slug google/gemini-3.1-pro-preview-customtools-20260219)
    (hugging_face_id null)
    (name "Google: Gemini 3.1 Pro Preview Custom Tools")
    (created 1772045923)
    (description "Gemini 3.1 Pro Preview Custom Tools is a variant of Gemini 3.1 Pro that improves tool selection behavior by preventing overuse of a general bash tool when more efficient third-party...")
    (context_length 1048576)
    (architecture (
      (modality text+image+file+audio+video->text)
      (input_modalities ([]
        text
        audio
        image
        video
        file
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Gemini)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.000002")
      (completion "0.000012")
      (image "0.000002")
      (audio "0.000002")
      (input_audio_cache "0.0000002")
      (web_search "0.014")
      (internal_reasoning "0.000012")
      (input_cache_read "0.0000002")
      (input_cache_write "0.000000375")
      (overrides ([]
        (
          (min_prompt_tokens 200000)
          (prompt "0.000004")
          (completion "0.000018")
          (audio "0.000004")
          (input_audio_cache "0.0000004")
          (input_cache_read "0.0000004")
        )
      ))
    ))
    (top_provider (
      (context_length 1048576)
      (max_completion_tokens 65536)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      include_reasoning
      max_tokens
      reasoning
      reasoning_effort
      response_format
      seed
      structured_outputs
      temperature
      tool_choice
      tools
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
      (details /api/v1/models/google/gemini-3.1-pro-preview-customtools-20260219/endpoints)
    ))
    (reasoning (
      (mandatory true)
      (supported_efforts ([]
        high
        medium
        low
      ))
      (default_effort medium)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId google/gemini-3.1-pro-preview-customtools)
  ))
)
