(
  (kind model)
  (id openrouter-deepseek_deepseek-r1-distill-llama-70b)
  (label "DeepSeek: R1 Distill Llama 70B")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model deepseek/deepseek-r1-distill-llama-70b)
  (enabled true)
  (capabilities (
    (audio false)
    (code false)
    (functionCalling false)
    (json false)
    (jsonMode false)
    (local false)
    (multimodal false)
    (reasoning true)
    (text true)
    (tools false)
    (vision false)
  ))
  (limits (
    (contextWindow 8192)
    (maxOutputTokens 8192)
  ))
  (pricing (
    (prompt "0.0000008")
    (completion "0.0000008")
  ))
  (properties (
    (id deepseek/deepseek-r1-distill-llama-70b)
    (canonical_slug deepseek/deepseek-r1-distill-llama-70b)
    (hugging_face_id deepseek-ai/DeepSeek-R1-Distill-Llama-70B)
    (name "DeepSeek: R1 Distill Llama 70B")
    (created 1737663169)
    (description "DeepSeek R1 Distill Llama 70B is a distilled large language model based on [Llama-3.3-70B-Instruct](/meta-llama/llama-3.3-70b-instruct), using outputs from [DeepSeek R1](/deepseek/deepseek-r1). The model combines advanced distillation techniques to achieve high performance across...")
    (context_length 8192)
    (architecture (
      (modality text->text)
      (input_modalities ([]
        text
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Llama3)
      (instruct_type deepseek-r1)
    ))
    (pricing (
      (prompt "0.0000008")
      (completion "0.0000008")
    ))
    (top_provider (
      (context_length 8192)
      (max_completion_tokens 8192)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      frequency_penalty
      include_reasoning
      max_tokens
      presence_penalty
      reasoning
      repetition_penalty
      seed
      stop
      temperature
      top_k
      top_p
    ))
    (default_parameters ())
    (supported_voices null)
    (knowledge_cutoff 2024-07-31)
    (expiration_date null)
    (links (
      (details /api/v1/models/deepseek/deepseek-r1-distill-llama-70b/endpoints)
    ))
    (reasoning (
      (mandatory false)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id deepseek/deepseek-r1-distill-llama-70b)
    (canonical_slug deepseek/deepseek-r1-distill-llama-70b)
    (hugging_face_id deepseek-ai/DeepSeek-R1-Distill-Llama-70B)
    (name "DeepSeek: R1 Distill Llama 70B")
    (created 1737663169)
    (description "DeepSeek R1 Distill Llama 70B is a distilled large language model based on [Llama-3.3-70B-Instruct](/meta-llama/llama-3.3-70b-instruct), using outputs from [DeepSeek R1](/deepseek/deepseek-r1). The model combines advanced distillation techniques to achieve high performance across...")
    (context_length 8192)
    (architecture (
      (modality text->text)
      (input_modalities ([]
        text
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Llama3)
      (instruct_type deepseek-r1)
    ))
    (pricing (
      (prompt "0.0000008")
      (completion "0.0000008")
    ))
    (top_provider (
      (context_length 8192)
      (max_completion_tokens 8192)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      frequency_penalty
      include_reasoning
      max_tokens
      presence_penalty
      reasoning
      repetition_penalty
      seed
      stop
      temperature
      top_k
      top_p
    ))
    (default_parameters ())
    (supported_voices null)
    (knowledge_cutoff 2024-07-31)
    (expiration_date null)
    (links (
      (details /api/v1/models/deepseek/deepseek-r1-distill-llama-70b/endpoints)
    ))
    (reasoning (
      (mandatory false)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId deepseek/deepseek-r1-distill-llama-70b)
  ))
)
