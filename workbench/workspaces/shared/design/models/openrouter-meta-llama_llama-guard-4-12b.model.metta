({}
  (kind model)
  (id openrouter-meta-llama_llama-guard-4-12b)
  (label "Meta: Llama Guard 4 12B")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model meta-llama/llama-guard-4-12b)
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
    (contextWindow 1048576)
    (maxOutputTokens 16384)
  ))
  (pricing ({}
    (prompt "0.00000018")
    (completion "0.00000018")
  ))
  (properties ({}
    (id meta-llama/llama-guard-4-12b)
    (canonical_slug meta-llama/llama-guard-4-12b)
    (hugging_face_id meta-llama/Llama-Guard-4-12B)
    (name "Meta: Llama Guard 4 12B")
    (created 1745975193)
    (description "Llama Guard 4 is a Llama 4 Scout-derived multimodal pretrained model, fine-tuned for content safety classification. Similar to previous versions, it can be used to classify content in both LLM...")
    (context_length 1048576)
    (architecture ({}
      (modality text+image->text)
      (input_modalities (
        image
        text
      ))
      (output_modalities (
        text
      ))
      (tokenizer Other)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.00000018")
      (completion "0.00000018")
    ))
    (top_provider ({}
      (context_length 163840)
      (max_completion_tokens 16384)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      logit_bias
      max_tokens
      min_p
      presence_penalty
      repetition_penalty
      response_format
      seed
      stop
      temperature
      top_k
      top_p
    ))
    (default_parameters ({}))
    (supported_voices null)
    (knowledge_cutoff 2024-08-31)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/meta-llama/llama-guard-4-12b/endpoints)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id meta-llama/llama-guard-4-12b)
    (canonical_slug meta-llama/llama-guard-4-12b)
    (hugging_face_id meta-llama/Llama-Guard-4-12B)
    (name "Meta: Llama Guard 4 12B")
    (created 1745975193)
    (description "Llama Guard 4 is a Llama 4 Scout-derived multimodal pretrained model, fine-tuned for content safety classification. Similar to previous versions, it can be used to classify content in both LLM...")
    (context_length 1048576)
    (architecture ({}
      (modality text+image->text)
      (input_modalities (
        image
        text
      ))
      (output_modalities (
        text
      ))
      (tokenizer Other)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.00000018")
      (completion "0.00000018")
    ))
    (top_provider ({}
      (context_length 163840)
      (max_completion_tokens 16384)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      logit_bias
      max_tokens
      min_p
      presence_penalty
      repetition_penalty
      response_format
      seed
      stop
      temperature
      top_k
      top_p
    ))
    (default_parameters ({}))
    (supported_voices null)
    (knowledge_cutoff 2024-08-31)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/meta-llama/llama-guard-4-12b/endpoints)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId meta-llama/llama-guard-4-12b)
  ))
)
