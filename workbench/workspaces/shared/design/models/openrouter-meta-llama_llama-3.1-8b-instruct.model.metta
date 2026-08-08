(
  (kind model)
  (id openrouter-meta-llama_llama-3.1-8b-instruct)
  (label "Meta: Llama 3.1 8B Instruct")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model meta-llama/llama-3.1-8b-instruct)
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
    (contextWindow 131072)
    (maxOutputTokens 131072)
  ))
  (pricing (
    (prompt "0.00000005")
    (completion "0.00000008")
    (input_cache_read "0.000000025")
  ))
  (properties (
    (id meta-llama/llama-3.1-8b-instruct)
    (canonical_slug meta-llama/llama-3.1-8b-instruct)
    (hugging_face_id meta-llama/Meta-Llama-3.1-8B-Instruct)
    (name "Meta: Llama 3.1 8B Instruct")
    (created 1721692800)
    (description "Meta's latest class of model (Llama 3.1) launched with a variety of sizes & flavors. This 8B instruct-tuned version is fast and efficient. It has demonstrated strong performance compared to...")
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
      (completion "0.00000008")
      (input_cache_read "0.000000025")
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
    (default_parameters ())
    (supported_voices null)
    (knowledge_cutoff 2023-12-31)
    (expiration_date null)
    (links (
      (details /api/v1/models/meta-llama/llama-3.1-8b-instruct/endpoints)
    ))
    (benchmarks (
      (design_arena ([]))
      (artificial_analysis (
        (intelligence_index 7.8)
        (coding_index 5.4)
        (agentic_index 0.5)
      ))
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id meta-llama/llama-3.1-8b-instruct)
    (canonical_slug meta-llama/llama-3.1-8b-instruct)
    (hugging_face_id meta-llama/Meta-Llama-3.1-8B-Instruct)
    (name "Meta: Llama 3.1 8B Instruct")
    (created 1721692800)
    (description "Meta's latest class of model (Llama 3.1) launched with a variety of sizes & flavors. This 8B instruct-tuned version is fast and efficient. It has demonstrated strong performance compared to...")
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
      (completion "0.00000008")
      (input_cache_read "0.000000025")
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
    (default_parameters ())
    (supported_voices null)
    (knowledge_cutoff 2023-12-31)
    (expiration_date null)
    (links (
      (details /api/v1/models/meta-llama/llama-3.1-8b-instruct/endpoints)
    ))
    (benchmarks (
      (design_arena ([]))
      (artificial_analysis (
        (intelligence_index 7.8)
        (coding_index 5.4)
        (agentic_index 0.5)
      ))
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId meta-llama/llama-3.1-8b-instruct)
  ))
)
