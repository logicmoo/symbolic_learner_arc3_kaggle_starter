({}
  (kind model)
  (id openrouter-mistralai_voxtral-small-24b-2507)
  (label "Mistral: Voxtral Small 24B 2507")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model mistralai/voxtral-small-24b-2507)
  (enabled true)
  (capabilities ({}
    (audio true)
    (code false)
    (functionCalling true)
    (json true)
    (jsonMode true)
    (local false)
    (multimodal true)
    (reasoning false)
    (text true)
    (tools true)
    (vision false)
  ))
  (limits ({}
    (contextWindow 32000)
    (maxOutputTokens null)
  ))
  (pricing ({}
    (prompt "0.0000001")
    (completion "0.0000003")
    (audio "0.0001")
    (input_cache_read "0.00000001")
  ))
  (properties ({}
    (id mistralai/voxtral-small-24b-2507)
    (canonical_slug mistralai/voxtral-small-24b-2507)
    (hugging_face_id mistralai/Voxtral-Small-24B-2507)
    (name "Mistral: Voxtral Small 24B 2507")
    (created 1761835144)
    (description "Voxtral Small is an enhancement of Mistral Small 3, incorporating state-of-the-art audio input capabilities while retaining best-in-class text performance. It excels at speech transcription, translation and audio understanding. Input audio...")
    (context_length 32000)
    (architecture ({}
      (modality text+file+audio->text)
      (input_modalities (
        text
        audio
        file
      ))
      (output_modalities (
        text
      ))
      (tokenizer Mistral)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.0000001")
      (completion "0.0000003")
      (audio "0.0001")
      (input_cache_read "0.00000001")
    ))
    (top_provider ({}
      (context_length 32000)
      (max_completion_tokens null)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      max_tokens
      presence_penalty
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
      (temperature 0.2)
      (top_p 0.95)
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/mistralai/voxtral-small-24b-2507/endpoints)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id mistralai/voxtral-small-24b-2507)
    (canonical_slug mistralai/voxtral-small-24b-2507)
    (hugging_face_id mistralai/Voxtral-Small-24B-2507)
    (name "Mistral: Voxtral Small 24B 2507")
    (created 1761835144)
    (description "Voxtral Small is an enhancement of Mistral Small 3, incorporating state-of-the-art audio input capabilities while retaining best-in-class text performance. It excels at speech transcription, translation and audio understanding. Input audio...")
    (context_length 32000)
    (architecture ({}
      (modality text+file+audio->text)
      (input_modalities (
        text
        audio
        file
      ))
      (output_modalities (
        text
      ))
      (tokenizer Mistral)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.0000001")
      (completion "0.0000003")
      (audio "0.0001")
      (input_cache_read "0.00000001")
    ))
    (top_provider ({}
      (context_length 32000)
      (max_completion_tokens null)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      max_tokens
      presence_penalty
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
      (temperature 0.2)
      (top_p 0.95)
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/mistralai/voxtral-small-24b-2507/endpoints)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId mistralai/voxtral-small-24b-2507)
  ))
)
