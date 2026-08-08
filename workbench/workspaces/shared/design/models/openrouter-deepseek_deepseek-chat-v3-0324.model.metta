({}
  (kind model)
  (id openrouter-deepseek_deepseek-chat-v3-0324)
  (label "DeepSeek: DeepSeek V3 0324")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model deepseek/deepseek-chat-v3-0324)
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
    (contextWindow 163840)
    (maxOutputTokens 65536)
  ))
  (pricing ({}
    (prompt "0.00000027")
    (completion "0.00000112")
    (input_cache_read "0.000000135")
  ))
  (properties ({}
    (id deepseek/deepseek-chat-v3-0324)
    (canonical_slug deepseek/deepseek-chat-v3-0324)
    (hugging_face_id deepseek-ai/DeepSeek-V3-0324)
    (name "DeepSeek: DeepSeek V3 0324")
    (created 1742824755)
    (description "DeepSeek V3, a 685B-parameter, mixture-of-experts model, is the latest iteration of the flagship chat model family from the DeepSeek team. It succeeds the [DeepSeek V3](/deepseek/deepseek-chat-v3) model and performs really well...")
    (context_length 163840)
    (architecture ({}
      (modality text->text)
      (input_modalities (
        text
      ))
      (output_modalities (
        text
      ))
      (tokenizer DeepSeek)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.00000027")
      (completion "0.00000112")
      (input_cache_read "0.000000135")
    ))
    (top_provider ({}
      (context_length 163840)
      (max_completion_tokens 65536)
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
      tool_choice
      tools
      top_k
      top_p
    ))
    (default_parameters ({}))
    (supported_voices null)
    (knowledge_cutoff 2024-07-31)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/deepseek/deepseek-chat-v3-0324/endpoints)
    ))
    (benchmarks ({}
      (design_arena ())
      (artificial_analysis ({}
        (intelligence_index 15.2)
        (coding_index 21.2)
        (agentic_index 1.6)
      ))
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id deepseek/deepseek-chat-v3-0324)
    (canonical_slug deepseek/deepseek-chat-v3-0324)
    (hugging_face_id deepseek-ai/DeepSeek-V3-0324)
    (name "DeepSeek: DeepSeek V3 0324")
    (created 1742824755)
    (description "DeepSeek V3, a 685B-parameter, mixture-of-experts model, is the latest iteration of the flagship chat model family from the DeepSeek team. It succeeds the [DeepSeek V3](/deepseek/deepseek-chat-v3) model and performs really well...")
    (context_length 163840)
    (architecture ({}
      (modality text->text)
      (input_modalities (
        text
      ))
      (output_modalities (
        text
      ))
      (tokenizer DeepSeek)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.00000027")
      (completion "0.00000112")
      (input_cache_read "0.000000135")
    ))
    (top_provider ({}
      (context_length 163840)
      (max_completion_tokens 65536)
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
      tool_choice
      tools
      top_k
      top_p
    ))
    (default_parameters ({}))
    (supported_voices null)
    (knowledge_cutoff 2024-07-31)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/deepseek/deepseek-chat-v3-0324/endpoints)
    ))
    (benchmarks ({}
      (design_arena ())
      (artificial_analysis ({}
        (intelligence_index 15.2)
        (coding_index 21.2)
        (agentic_index 1.6)
      ))
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId deepseek/deepseek-chat-v3-0324)
  ))
)
