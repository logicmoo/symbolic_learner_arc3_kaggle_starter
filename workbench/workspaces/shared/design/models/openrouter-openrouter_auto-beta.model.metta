({}
  (kind model)
  (id openrouter-openrouter_auto-beta)
  (label "Auto Router (Beta)")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model openrouter/auto-beta)
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
    (contextWindow 2000000)
    (maxOutputTokens null)
  ))
  (pricing ({}
    (prompt "-1")
    (completion "-1")
  ))
  (properties ({}
    (id openrouter/auto-beta)
    (canonical_slug openrouter/auto-beta)
    (hugging_face_id null)
    (name "Auto Router (Beta)")
    (created 1784311165)
    (description "Auto Router (Beta) is a task-aware router from OpenRouter. It classifies each request, then routes it the [most popular model](/rankings#task-spend) for that task based on aggregate spend, filtered by your...")
    (context_length 2000000)
    (architecture ({}
      (modality text+image+file+audio+video->text+image)
      (input_modalities (
        text
        image
        audio
        file
        video
      ))
      (output_modalities (
        text
        image
      ))
      (tokenizer Router)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "-1")
      (completion "-1")
    ))
    (top_provider ({}
      (context_length null)
      (max_completion_tokens null)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      include_reasoning
      logit_bias
      logprobs
      max_tokens
      min_p
      prediction
      presence_penalty
      reasoning
      reasoning_effort
      repetition_penalty
      response_format
      seed
      stop
      structured_outputs
      temperature
      tool_choice
      tools
      top_a
      top_k
      top_logprobs
      top_p
      web_search_options
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
      (details /api/v1/models/openrouter/auto-beta/endpoints)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id openrouter/auto-beta)
    (canonical_slug openrouter/auto-beta)
    (hugging_face_id null)
    (name "Auto Router (Beta)")
    (created 1784311165)
    (description "Auto Router (Beta) is a task-aware router from OpenRouter. It classifies each request, then routes it the [most popular model](/rankings#task-spend) for that task based on aggregate spend, filtered by your...")
    (context_length 2000000)
    (architecture ({}
      (modality text+image+file+audio+video->text+image)
      (input_modalities (
        text
        image
        audio
        file
        video
      ))
      (output_modalities (
        text
        image
      ))
      (tokenizer Router)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "-1")
      (completion "-1")
    ))
    (top_provider ({}
      (context_length null)
      (max_completion_tokens null)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      include_reasoning
      logit_bias
      logprobs
      max_tokens
      min_p
      prediction
      presence_penalty
      reasoning
      reasoning_effort
      repetition_penalty
      response_format
      seed
      stop
      structured_outputs
      temperature
      tool_choice
      tools
      top_a
      top_k
      top_logprobs
      top_p
      web_search_options
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
      (details /api/v1/models/openrouter/auto-beta/endpoints)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId openrouter/auto-beta)
  ))
)
