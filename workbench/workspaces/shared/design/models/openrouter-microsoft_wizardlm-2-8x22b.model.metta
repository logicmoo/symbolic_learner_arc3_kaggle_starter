(
  (kind model)
  (id openrouter-microsoft_wizardlm-2-8x22b)
  (label "WizardLM-2 8x22B")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model microsoft/wizardlm-2-8x22b)
  (enabled true)
  (capabilities (
    (audio false)
    (code false)
    (functionCalling false)
    (json true)
    (jsonMode true)
    (local false)
    (multimodal false)
    (reasoning false)
    (text true)
    (tools false)
    (vision false)
  ))
  (limits (
    (contextWindow 65535)
    (maxOutputTokens 8000)
  ))
  (pricing (
    (prompt "0.00000062")
    (completion "0.00000062")
  ))
  (properties (
    (id microsoft/wizardlm-2-8x22b)
    (canonical_slug microsoft/wizardlm-2-8x22b)
    (hugging_face_id microsoft/WizardLM-2-8x22B)
    (name "WizardLM-2 8x22B")
    (created 1713225600)
    (description "WizardLM-2 8x22B is Microsoft AI's most advanced Wizard model. It demonstrates highly competitive performance compared to leading proprietary models, and it consistently outperforms all existing state-of-the-art opensource models. It is...")
    (context_length 65535)
    (architecture (
      (modality text->text)
      (input_modalities ([]
        text
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Mistral)
      (instruct_type vicuna)
    ))
    (pricing (
      (prompt "0.00000062")
      (completion "0.00000062")
    ))
    (top_provider (
      (context_length 65535)
      (max_completion_tokens 8000)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      frequency_penalty
      max_tokens
      presence_penalty
      repetition_penalty
      response_format
      seed
      stop
      temperature
      top_k
      top_p
    ))
    (default_parameters ())
    (supported_voices null)
    (knowledge_cutoff 2024-04-30)
    (expiration_date null)
    (links (
      (details /api/v1/models/microsoft/wizardlm-2-8x22b/endpoints)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id microsoft/wizardlm-2-8x22b)
    (canonical_slug microsoft/wizardlm-2-8x22b)
    (hugging_face_id microsoft/WizardLM-2-8x22B)
    (name "WizardLM-2 8x22B")
    (created 1713225600)
    (description "WizardLM-2 8x22B is Microsoft AI's most advanced Wizard model. It demonstrates highly competitive performance compared to leading proprietary models, and it consistently outperforms all existing state-of-the-art opensource models. It is...")
    (context_length 65535)
    (architecture (
      (modality text->text)
      (input_modalities ([]
        text
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Mistral)
      (instruct_type vicuna)
    ))
    (pricing (
      (prompt "0.00000062")
      (completion "0.00000062")
    ))
    (top_provider (
      (context_length 65535)
      (max_completion_tokens 8000)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      frequency_penalty
      max_tokens
      presence_penalty
      repetition_penalty
      response_format
      seed
      stop
      temperature
      top_k
      top_p
    ))
    (default_parameters ())
    (supported_voices null)
    (knowledge_cutoff 2024-04-30)
    (expiration_date null)
    (links (
      (details /api/v1/models/microsoft/wizardlm-2-8x22b/endpoints)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId microsoft/wizardlm-2-8x22b)
  ))
)
