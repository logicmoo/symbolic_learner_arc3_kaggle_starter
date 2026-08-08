({}
  (kind model)
  (id openrouter-qwen_qwen2.5-vl-72b-instruct)
  (label "Qwen: Qwen2.5 VL 72B Instruct")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model qwen/qwen2.5-vl-72b-instruct)
  (enabled true)
  (capabilities ({}
    (audio false)
    (code false)
    (functionCalling false)
    (json true)
    (jsonMode true)
    (local false)
    (multimodal true)
    (reasoning false)
    (text true)
    (tools false)
    (vision true)
  ))
  (limits ({}
    (contextWindow 128000)
    (maxOutputTokens null)
  ))
  (pricing ({}
    (prompt "0.00000025")
    (completion "0.00000075")
  ))
  (properties ({}
    (id qwen/qwen2.5-vl-72b-instruct)
    (canonical_slug qwen/qwen2.5-vl-72b-instruct)
    (hugging_face_id Qwen/Qwen2.5-VL-72B-Instruct)
    (name "Qwen: Qwen2.5 VL 72B Instruct")
    (created 1738410311)
    (description "Qwen2.5-VL is proficient in recognizing common objects such as flowers, birds, fish, and insects. It is also highly capable of analyzing texts, charts, icons, graphics, and layouts within images.")
    (context_length 128000)
    (architecture ({}
      (modality text+image->text)
      (input_modalities (
        text
        image
      ))
      (output_modalities (
        text
      ))
      (tokenizer Qwen)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.00000025")
      (completion "0.00000075")
    ))
    (top_provider ({}
      (context_length 32000)
      (max_completion_tokens null)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      logit_bias
      logprobs
      max_tokens
      presence_penalty
      repetition_penalty
      response_format
      seed
      stop
      structured_outputs
      temperature
      top_k
      top_logprobs
      top_p
    ))
    (default_parameters ({}))
    (supported_voices null)
    (knowledge_cutoff 2024-06-30)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/qwen/qwen2.5-vl-72b-instruct/endpoints)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id qwen/qwen2.5-vl-72b-instruct)
    (canonical_slug qwen/qwen2.5-vl-72b-instruct)
    (hugging_face_id Qwen/Qwen2.5-VL-72B-Instruct)
    (name "Qwen: Qwen2.5 VL 72B Instruct")
    (created 1738410311)
    (description "Qwen2.5-VL is proficient in recognizing common objects such as flowers, birds, fish, and insects. It is also highly capable of analyzing texts, charts, icons, graphics, and layouts within images.")
    (context_length 128000)
    (architecture ({}
      (modality text+image->text)
      (input_modalities (
        text
        image
      ))
      (output_modalities (
        text
      ))
      (tokenizer Qwen)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.00000025")
      (completion "0.00000075")
    ))
    (top_provider ({}
      (context_length 32000)
      (max_completion_tokens null)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      logit_bias
      logprobs
      max_tokens
      presence_penalty
      repetition_penalty
      response_format
      seed
      stop
      structured_outputs
      temperature
      top_k
      top_logprobs
      top_p
    ))
    (default_parameters ({}))
    (supported_voices null)
    (knowledge_cutoff 2024-06-30)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/qwen/qwen2.5-vl-72b-instruct/endpoints)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId qwen/qwen2.5-vl-72b-instruct)
  ))
)
