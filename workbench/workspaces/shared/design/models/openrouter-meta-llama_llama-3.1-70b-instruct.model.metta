({}
  (kind model)
  (id openrouter-meta-llama_llama-3.1-70b-instruct)
  (label "Meta: Llama 3.1 70B Instruct")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model meta-llama/llama-3.1-70b-instruct)
  (enabled true)
  (capabilities ({}
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
  (limits ({}
    (contextWindow 131072)
    (maxOutputTokens 16384)
  ))
  (pricing ({}
    (prompt "0.0000004")
    (completion "0.0000004")
  ))
  (properties ({}
    (id meta-llama/llama-3.1-70b-instruct)
    (canonical_slug meta-llama/llama-3.1-70b-instruct)
    (hugging_face_id meta-llama/Meta-Llama-3.1-70B-Instruct)
    (name "Meta: Llama 3.1 70B Instruct")
    (created 1721692800)
    (description "Meta's latest class of model (Llama 3.1) launched with a variety of sizes & flavors. This 70B instruct-tuned version is optimized for high quality dialogue usecases. It has demonstrated strong...")
    (context_length 131072)
    (architecture ({}
      (modality text->text)
      (input_modalities (
        text
      ))
      (output_modalities (
        text
      ))
      (tokenizer Llama3)
      (instruct_type llama3)
    ))
    (pricing ({}
      (prompt "0.0000004")
      (completion "0.0000004")
    ))
    (top_provider ({}
      (context_length 131072)
      (max_completion_tokens 16384)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      logit_bias
      logprobs
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
      top_logprobs
      top_p
    ))
    (default_parameters ({}))
    (supported_voices null)
    (knowledge_cutoff 2023-12-31)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/meta-llama/llama-3.1-70b-instruct/endpoints)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id meta-llama/llama-3.1-70b-instruct)
    (canonical_slug meta-llama/llama-3.1-70b-instruct)
    (hugging_face_id meta-llama/Meta-Llama-3.1-70B-Instruct)
    (name "Meta: Llama 3.1 70B Instruct")
    (created 1721692800)
    (description "Meta's latest class of model (Llama 3.1) launched with a variety of sizes & flavors. This 70B instruct-tuned version is optimized for high quality dialogue usecases. It has demonstrated strong...")
    (context_length 131072)
    (architecture ({}
      (modality text->text)
      (input_modalities (
        text
      ))
      (output_modalities (
        text
      ))
      (tokenizer Llama3)
      (instruct_type llama3)
    ))
    (pricing ({}
      (prompt "0.0000004")
      (completion "0.0000004")
    ))
    (top_provider ({}
      (context_length 131072)
      (max_completion_tokens 16384)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      logit_bias
      logprobs
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
      top_logprobs
      top_p
    ))
    (default_parameters ({}))
    (supported_voices null)
    (knowledge_cutoff 2023-12-31)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/meta-llama/llama-3.1-70b-instruct/endpoints)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId meta-llama/llama-3.1-70b-instruct)
  ))
)
