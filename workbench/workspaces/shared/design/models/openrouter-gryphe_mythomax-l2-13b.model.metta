(
  (kind model)
  (id openrouter-gryphe_mythomax-l2-13b)
  (label "MythoMax 13B")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model gryphe/mythomax-l2-13b)
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
    (contextWindow 8192)
    (maxOutputTokens 4096)
  ))
  (pricing (
    (prompt "0.00000008")
    (completion "0.00000011")
  ))
  (properties (
    (id gryphe/mythomax-l2-13b)
    (canonical_slug gryphe/mythomax-l2-13b)
    (hugging_face_id Gryphe/MythoMax-L2-13b)
    (name "MythoMax 13B")
    (created 1688256000)
    (description "One of the highest performing and most popular fine-tunes of Llama 2 13B, with rich descriptions and roleplay. #merge")
    (context_length 8192)
    (architecture (
      (modality text->text)
      (input_modalities ([]
        text
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Llama2)
      (instruct_type alpaca)
    ))
    (pricing (
      (prompt "0.00000008")
      (completion "0.00000011")
    ))
    (top_provider (
      (context_length 4096)
      (max_completion_tokens 4096)
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
      top_a
      top_k
      top_logprobs
      top_p
    ))
    (default_parameters ())
    (supported_voices null)
    (knowledge_cutoff 2023-06-30)
    (expiration_date null)
    (links (
      (details /api/v1/models/gryphe/mythomax-l2-13b/endpoints)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id gryphe/mythomax-l2-13b)
    (canonical_slug gryphe/mythomax-l2-13b)
    (hugging_face_id Gryphe/MythoMax-L2-13b)
    (name "MythoMax 13B")
    (created 1688256000)
    (description "One of the highest performing and most popular fine-tunes of Llama 2 13B, with rich descriptions and roleplay. #merge")
    (context_length 8192)
    (architecture (
      (modality text->text)
      (input_modalities ([]
        text
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Llama2)
      (instruct_type alpaca)
    ))
    (pricing (
      (prompt "0.00000008")
      (completion "0.00000011")
    ))
    (top_provider (
      (context_length 4096)
      (max_completion_tokens 4096)
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
      top_a
      top_k
      top_logprobs
      top_p
    ))
    (default_parameters ())
    (supported_voices null)
    (knowledge_cutoff 2023-06-30)
    (expiration_date null)
    (links (
      (details /api/v1/models/gryphe/mythomax-l2-13b/endpoints)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId gryphe/mythomax-l2-13b)
  ))
)
