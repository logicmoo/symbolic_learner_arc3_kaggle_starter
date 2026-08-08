(
  (kind model)
  (id openrouter-meta-llama_llama-3.2-3b-instruct)
  (label "Meta: Llama 3.2 3B Instruct")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model meta-llama/llama-3.2-3b-instruct)
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
    (contextWindow 131072)
    (maxOutputTokens 131072)
  ))
  (pricing (
    (prompt "0.00000005")
    (completion "0.00000033")
  ))
  (properties (
    (id meta-llama/llama-3.2-3b-instruct)
    (canonical_slug meta-llama/llama-3.2-3b-instruct)
    (hugging_face_id meta-llama/Llama-3.2-3B-Instruct)
    (name "Meta: Llama 3.2 3B Instruct")
    (created 1727222400)
    (description "Llama 3.2 3B is a 3-billion-parameter multilingual large language model, optimized for advanced natural language processing tasks like dialogue generation, reasoning, and summarization. Designed with the latest transformer architecture, it...")
    (context_length 131072)
    (architecture (
      (modality text->text)
      (input_modalities ([]
        text
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Llama3)
      (instruct_type llama3)
    ))
    (pricing (
      (prompt "0.00000005")
      (completion "0.00000033")
    ))
    (top_provider (
      (context_length 131072)
      (max_completion_tokens 131072)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      frequency_penalty
      logit_bias
      logprobs
      max_tokens
      min_p
      presence_penalty
      repetition_penalty
      seed
      stop
      structured_outputs
      temperature
      top_k
      top_logprobs
      top_p
    ))
    (default_parameters ())
    (supported_voices null)
    (knowledge_cutoff 2023-12-31)
    (expiration_date null)
    (links (
      (details /api/v1/models/meta-llama/llama-3.2-3b-instruct/endpoints)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id meta-llama/llama-3.2-3b-instruct)
    (canonical_slug meta-llama/llama-3.2-3b-instruct)
    (hugging_face_id meta-llama/Llama-3.2-3B-Instruct)
    (name "Meta: Llama 3.2 3B Instruct")
    (created 1727222400)
    (description "Llama 3.2 3B is a 3-billion-parameter multilingual large language model, optimized for advanced natural language processing tasks like dialogue generation, reasoning, and summarization. Designed with the latest transformer architecture, it...")
    (context_length 131072)
    (architecture (
      (modality text->text)
      (input_modalities ([]
        text
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Llama3)
      (instruct_type llama3)
    ))
    (pricing (
      (prompt "0.00000005")
      (completion "0.00000033")
    ))
    (top_provider (
      (context_length 131072)
      (max_completion_tokens 131072)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      frequency_penalty
      logit_bias
      logprobs
      max_tokens
      min_p
      presence_penalty
      repetition_penalty
      seed
      stop
      structured_outputs
      temperature
      top_k
      top_logprobs
      top_p
    ))
    (default_parameters ())
    (supported_voices null)
    (knowledge_cutoff 2023-12-31)
    (expiration_date null)
    (links (
      (details /api/v1/models/meta-llama/llama-3.2-3b-instruct/endpoints)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId meta-llama/llama-3.2-3b-instruct)
  ))
)
