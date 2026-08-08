(
  (kind model)
  (id openrouter-meta-llama_llama-3.3-70b-instruct)
  (label "Meta: Llama 3.3 70B Instruct")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model meta-llama/llama-3.3-70b-instruct)
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
    (maxOutputTokens 16384)
  ))
  (pricing (
    (prompt "0.0000001")
    (completion "0.00000032")
  ))
  (properties (
    (id meta-llama/llama-3.3-70b-instruct)
    (canonical_slug meta-llama/llama-3.3-70b-instruct)
    (hugging_face_id meta-llama/Llama-3.3-70B-Instruct)
    (name "Meta: Llama 3.3 70B Instruct")
    (created 1733506137)
    (description "The Meta Llama 3.3 multilingual large language model (LLM) is a pretrained and instruction tuned generative model in 70B (text in/text out). The Llama 3.3 instruction tuned text only model...")
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
      (prompt "0.0000001")
      (completion "0.00000032")
    ))
    (top_provider (
      (context_length 131072)
      (max_completion_tokens 16384)
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
      (details /api/v1/models/meta-llama/llama-3.3-70b-instruct/endpoints)
    ))
    (benchmarks (
      (design_arena ([]))
      (artificial_analysis (
        (intelligence_index 9.3)
        (coding_index 11.9)
        (agentic_index 0.3)
      ))
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id meta-llama/llama-3.3-70b-instruct)
    (canonical_slug meta-llama/llama-3.3-70b-instruct)
    (hugging_face_id meta-llama/Llama-3.3-70B-Instruct)
    (name "Meta: Llama 3.3 70B Instruct")
    (created 1733506137)
    (description "The Meta Llama 3.3 multilingual large language model (LLM) is a pretrained and instruction tuned generative model in 70B (text in/text out). The Llama 3.3 instruction tuned text only model...")
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
      (prompt "0.0000001")
      (completion "0.00000032")
    ))
    (top_provider (
      (context_length 131072)
      (max_completion_tokens 16384)
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
      (details /api/v1/models/meta-llama/llama-3.3-70b-instruct/endpoints)
    ))
    (benchmarks (
      (design_arena ([]))
      (artificial_analysis (
        (intelligence_index 9.3)
        (coding_index 11.9)
        (agentic_index 0.3)
      ))
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId meta-llama/llama-3.3-70b-instruct)
  ))
)
