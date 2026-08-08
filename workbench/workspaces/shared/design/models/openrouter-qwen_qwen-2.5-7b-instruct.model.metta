(
  (kind model)
  (id openrouter-qwen_qwen-2.5-7b-instruct)
  (label "Qwen: Qwen2.5 7B Instruct")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model qwen/qwen-2.5-7b-instruct)
  (enabled true)
  (capabilities (
    (audio false)
    (code false)
    (functionCalling true)
    (json true)
    (jsonMode true)
    (local false)
    (multimodal false)
    (reasoning false)
    (text true)
    (tools true)
    (vision false)
  ))
  (limits (
    (contextWindow 32768)
    (maxOutputTokens 32768)
  ))
  (pricing (
    (prompt "0.0000001")
    (completion "0.0000002")
  ))
  (properties (
    (id qwen/qwen-2.5-7b-instruct)
    (canonical_slug qwen/qwen-2.5-7b-instruct)
    (hugging_face_id Qwen/Qwen2.5-7B-Instruct)
    (name "Qwen: Qwen2.5 7B Instruct")
    (created 1729036800)
    (description "Qwen2.5 7B is the latest series of Qwen large language models. Qwen2.5 brings the following improvements upon Qwen2: - Significantly more knowledge and has greatly improved capabilities in coding and...")
    (context_length 32768)
    (architecture (
      (modality text->text)
      (input_modalities ([]
        text
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Qwen)
      (instruct_type chatml)
    ))
    (pricing (
      (prompt "0.0000001")
      (completion "0.0000002")
    ))
    (top_provider (
      (context_length 32768)
      (max_completion_tokens 32768)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      frequency_penalty
      logit_bias
      max_tokens
      min_p
      presence_penalty
      repetition_penalty
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
    (default_parameters (
      (temperature null)
      (top_p null)
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff 2024-06-30)
    (expiration_date null)
    (links (
      (details /api/v1/models/qwen/qwen-2.5-7b-instruct/endpoints)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id qwen/qwen-2.5-7b-instruct)
    (canonical_slug qwen/qwen-2.5-7b-instruct)
    (hugging_face_id Qwen/Qwen2.5-7B-Instruct)
    (name "Qwen: Qwen2.5 7B Instruct")
    (created 1729036800)
    (description "Qwen2.5 7B is the latest series of Qwen large language models. Qwen2.5 brings the following improvements upon Qwen2: - Significantly more knowledge and has greatly improved capabilities in coding and...")
    (context_length 32768)
    (architecture (
      (modality text->text)
      (input_modalities ([]
        text
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Qwen)
      (instruct_type chatml)
    ))
    (pricing (
      (prompt "0.0000001")
      (completion "0.0000002")
    ))
    (top_provider (
      (context_length 32768)
      (max_completion_tokens 32768)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      frequency_penalty
      logit_bias
      max_tokens
      min_p
      presence_penalty
      repetition_penalty
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
    (default_parameters (
      (temperature null)
      (top_p null)
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff 2024-06-30)
    (expiration_date null)
    (links (
      (details /api/v1/models/qwen/qwen-2.5-7b-instruct/endpoints)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId qwen/qwen-2.5-7b-instruct)
  ))
)
