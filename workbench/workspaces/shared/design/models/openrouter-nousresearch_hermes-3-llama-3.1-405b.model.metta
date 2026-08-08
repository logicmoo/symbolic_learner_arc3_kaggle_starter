({}
  (kind model)
  (id openrouter-nousresearch_hermes-3-llama-3.1-405b)
  (label "Nous: Hermes 3 405B Instruct")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model nousresearch/hermes-3-llama-3.1-405b)
  (enabled true)
  (capabilities ({}
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
  (limits ({}
    (contextWindow 131072)
    (maxOutputTokens 16384)
  ))
  (pricing ({}
    (prompt "0.000001")
    (completion "0.000001")
  ))
  (properties ({}
    (id nousresearch/hermes-3-llama-3.1-405b)
    (canonical_slug nousresearch/hermes-3-llama-3.1-405b)
    (hugging_face_id NousResearch/Hermes-3-Llama-3.1-405B)
    (name "Nous: Hermes 3 405B Instruct")
    (created 1723766400)
    (description "Hermes 3 is a generalist language model with many improvements over Hermes 2, including advanced agentic capabilities, much better roleplaying, reasoning, multi-turn conversation, long context coherence, and improvements across the...")
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
      (instruct_type chatml)
    ))
    (pricing ({}
      (prompt "0.000001")
      (completion "0.000001")
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
      max_tokens
      min_p
      presence_penalty
      repetition_penalty
      response_format
      seed
      stop
      structured_outputs
      temperature
      top_k
      top_p
    ))
    (default_parameters ({}))
    (supported_voices null)
    (knowledge_cutoff 2023-12-31)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/nousresearch/hermes-3-llama-3.1-405b/endpoints)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id nousresearch/hermes-3-llama-3.1-405b)
    (canonical_slug nousresearch/hermes-3-llama-3.1-405b)
    (hugging_face_id NousResearch/Hermes-3-Llama-3.1-405B)
    (name "Nous: Hermes 3 405B Instruct")
    (created 1723766400)
    (description "Hermes 3 is a generalist language model with many improvements over Hermes 2, including advanced agentic capabilities, much better roleplaying, reasoning, multi-turn conversation, long context coherence, and improvements across the...")
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
      (instruct_type chatml)
    ))
    (pricing ({}
      (prompt "0.000001")
      (completion "0.000001")
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
      max_tokens
      min_p
      presence_penalty
      repetition_penalty
      response_format
      seed
      stop
      structured_outputs
      temperature
      top_k
      top_p
    ))
    (default_parameters ({}))
    (supported_voices null)
    (knowledge_cutoff 2023-12-31)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/nousresearch/hermes-3-llama-3.1-405b/endpoints)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId nousresearch/hermes-3-llama-3.1-405b)
  ))
)
