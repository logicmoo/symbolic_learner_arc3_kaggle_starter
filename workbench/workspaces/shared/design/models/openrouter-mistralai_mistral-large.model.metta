({}
  (kind model)
  (id openrouter-mistralai_mistral-large)
  (label "Mistral Large")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model mistralai/mistral-large)
  (enabled true)
  (capabilities ({}
    (audio false)
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
    (contextWindow 128000)
    (maxOutputTokens null)
  ))
  (pricing ({}
    (prompt "0.000002")
    (completion "0.000006")
    (input_cache_read "0.0000002")
  ))
  (properties ({}
    (id mistralai/mistral-large)
    (canonical_slug mistralai/mistral-large)
    (hugging_face_id null)
    (name "Mistral Large")
    (created 1708905600)
    (description "This is Mistral AI's flagship model, Mistral Large 2 (version `mistral-large-2407`). It's a proprietary weights-available model and excels at reasoning, code, JSON, chat, and more. Read the launch announcement [here](https://mistral.ai/news/mistral-large-2407/)....")
    (context_length 128000)
    (architecture ({}
      (modality text+file->text)
      (input_modalities (
        text
        file
      ))
      (output_modalities (
        text
      ))
      (tokenizer Mistral)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.000002")
      (completion "0.000006")
      (input_cache_read "0.0000002")
    ))
    (top_provider ({}
      (context_length 128000)
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
      (temperature 0.3)
    ))
    (supported_voices null)
    (knowledge_cutoff 2024-11-30)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/mistralai/mistral-large/endpoints)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id mistralai/mistral-large)
    (canonical_slug mistralai/mistral-large)
    (hugging_face_id null)
    (name "Mistral Large")
    (created 1708905600)
    (description "This is Mistral AI's flagship model, Mistral Large 2 (version `mistral-large-2407`). It's a proprietary weights-available model and excels at reasoning, code, JSON, chat, and more. Read the launch announcement [here](https://mistral.ai/news/mistral-large-2407/)....")
    (context_length 128000)
    (architecture ({}
      (modality text+file->text)
      (input_modalities (
        text
        file
      ))
      (output_modalities (
        text
      ))
      (tokenizer Mistral)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.000002")
      (completion "0.000006")
      (input_cache_read "0.0000002")
    ))
    (top_provider ({}
      (context_length 128000)
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
      (temperature 0.3)
    ))
    (supported_voices null)
    (knowledge_cutoff 2024-11-30)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/mistralai/mistral-large/endpoints)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId mistralai/mistral-large)
  ))
)
