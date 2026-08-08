({}
  (kind model)
  (id openrouter-openai_gpt-4o-2024-11-20)
  (label "OpenAI: GPT-4o (2024-11-20)")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model openai/gpt-4o-2024-11-20)
  (enabled true)
  (capabilities ({}
    (audio false)
    (code false)
    (functionCalling true)
    (json true)
    (jsonMode true)
    (local false)
    (multimodal true)
    (reasoning false)
    (text true)
    (tools true)
    (vision true)
  ))
  (limits ({}
    (contextWindow 128000)
    (maxOutputTokens 16384)
  ))
  (pricing ({}
    (prompt "0.0000025")
    (completion "0.00001")
    (input_cache_read "0.00000125")
  ))
  (properties ({}
    (id openai/gpt-4o-2024-11-20)
    (canonical_slug openai/gpt-4o-2024-11-20)
    (hugging_face_id "")
    (name "OpenAI: GPT-4o (2024-11-20)")
    (created 1732127594)
    (description "The 2024-11-20 version of GPT-4o offers a leveled-up creative writing ability with more natural, engaging, and tailored writing to improve relevance & readability. It’s also better at working with uploaded...")
    (context_length 128000)
    (architecture ({}
      (modality text+image+file->text)
      (input_modalities (
        text
        image
        file
      ))
      (output_modalities (
        text
      ))
      (tokenizer GPT)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.0000025")
      (completion "0.00001")
      (input_cache_read "0.00000125")
    ))
    (top_provider ({}
      (context_length 128000)
      (max_completion_tokens 16384)
      (is_moderated true)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      logit_bias
      logprobs
      max_tokens
      prediction
      presence_penalty
      response_format
      seed
      stop
      structured_outputs
      temperature
      tool_choice
      tools
      top_logprobs
      top_p
      web_search_options
    ))
    (default_parameters ({}))
    (supported_voices null)
    (knowledge_cutoff 2023-10-31)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/openai/gpt-4o-2024-11-20/endpoints)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id openai/gpt-4o-2024-11-20)
    (canonical_slug openai/gpt-4o-2024-11-20)
    (hugging_face_id "")
    (name "OpenAI: GPT-4o (2024-11-20)")
    (created 1732127594)
    (description "The 2024-11-20 version of GPT-4o offers a leveled-up creative writing ability with more natural, engaging, and tailored writing to improve relevance & readability. It’s also better at working with uploaded...")
    (context_length 128000)
    (architecture ({}
      (modality text+image+file->text)
      (input_modalities (
        text
        image
        file
      ))
      (output_modalities (
        text
      ))
      (tokenizer GPT)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.0000025")
      (completion "0.00001")
      (input_cache_read "0.00000125")
    ))
    (top_provider ({}
      (context_length 128000)
      (max_completion_tokens 16384)
      (is_moderated true)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      logit_bias
      logprobs
      max_tokens
      prediction
      presence_penalty
      response_format
      seed
      stop
      structured_outputs
      temperature
      tool_choice
      tools
      top_logprobs
      top_p
      web_search_options
    ))
    (default_parameters ({}))
    (supported_voices null)
    (knowledge_cutoff 2023-10-31)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/openai/gpt-4o-2024-11-20/endpoints)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId openai/gpt-4o-2024-11-20)
  ))
)
