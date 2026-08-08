({}
  (kind model)
  (id openrouter-deepseek_deepseek-v3.1-terminus)
  (label "DeepSeek: DeepSeek V3.1 Terminus")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model deepseek/deepseek-v3.1-terminus)
  (enabled true)
  (capabilities ({}
    (audio false)
    (code false)
    (functionCalling true)
    (json true)
    (jsonMode true)
    (local false)
    (multimodal false)
    (reasoning true)
    (text true)
    (tools true)
    (vision false)
  ))
  (limits ({}
    (contextWindow 163840)
    (maxOutputTokens 32768)
  ))
  (pricing ({}
    (prompt "0.00000027")
    (completion "0.000001")
    (input_cache_read "0.000000135")
  ))
  (properties ({}
    (id deepseek/deepseek-v3.1-terminus)
    (canonical_slug deepseek/deepseek-v3.1-terminus)
    (hugging_face_id deepseek-ai/DeepSeek-V3.1-Terminus)
    (name "DeepSeek: DeepSeek V3.1 Terminus")
    (created 1758548275)
    (description "DeepSeek-V3.1 Terminus is an update to [DeepSeek V3.1](/deepseek/deepseek-chat-v3.1) that maintains the model's original capabilities while addressing issues reported by users, including language consistency and agent capabilities, further optimizing the model's...")
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
      (instruct_type deepseek-v3.1)
    ))
    (pricing ({}
      (prompt "0.00000027")
      (completion "0.000001")
      (input_cache_read "0.000000135")
    ))
    (top_provider ({}
      (context_length 131072)
      (max_completion_tokens 32768)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      include_reasoning
      logit_bias
      max_tokens
      min_p
      presence_penalty
      reasoning
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
    (default_parameters ({}
      (temperature null)
      (top_p null)
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff 2025-03-31)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/deepseek/deepseek-v3.1-terminus/endpoints)
    ))
    (benchmarks ({}
      (design_arena (
        ({}
          (arena models)
          (category 3d)
          (elo 1194)
          (win_rate 56)
          (rank 47)
        )
        ({}
          (arena models)
          (category codecategories)
          (elo 1203)
          (win_rate 56)
          (rank 49)
        )
        ({}
          (arena models)
          (category dataviz)
          (elo 1189)
          (win_rate 52.8)
          (rank 56)
        )
        ({}
          (arena models)
          (category gamedev)
          (elo 1171)
          (win_rate 52.5)
          (rank 62)
        )
        ({}
          (arena models)
          (category svg)
          (elo 1112)
          (win_rate 50.1)
          (rank 54)
        )
        ({}
          (arena models)
          (category uicomponent)
          (elo 1216)
          (win_rate 59.5)
          (rank 41)
        )
        ({}
          (arena models)
          (category website)
          (elo 1209)
          (win_rate 56.4)
          (rank 52)
        )
      ))
      (artificial_analysis ({}
        (intelligence_index 30.6)
        (coding_index 43.5)
        (agentic_index 18.1)
      ))
    ))
    (reasoning ({}
      (mandatory false)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id deepseek/deepseek-v3.1-terminus)
    (canonical_slug deepseek/deepseek-v3.1-terminus)
    (hugging_face_id deepseek-ai/DeepSeek-V3.1-Terminus)
    (name "DeepSeek: DeepSeek V3.1 Terminus")
    (created 1758548275)
    (description "DeepSeek-V3.1 Terminus is an update to [DeepSeek V3.1](/deepseek/deepseek-chat-v3.1) that maintains the model's original capabilities while addressing issues reported by users, including language consistency and agent capabilities, further optimizing the model's...")
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
      (instruct_type deepseek-v3.1)
    ))
    (pricing ({}
      (prompt "0.00000027")
      (completion "0.000001")
      (input_cache_read "0.000000135")
    ))
    (top_provider ({}
      (context_length 131072)
      (max_completion_tokens 32768)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      include_reasoning
      logit_bias
      max_tokens
      min_p
      presence_penalty
      reasoning
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
    (default_parameters ({}
      (temperature null)
      (top_p null)
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff 2025-03-31)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/deepseek/deepseek-v3.1-terminus/endpoints)
    ))
    (benchmarks ({}
      (design_arena (
        ({}
          (arena models)
          (category 3d)
          (elo 1194)
          (win_rate 56)
          (rank 47)
        )
        ({}
          (arena models)
          (category codecategories)
          (elo 1203)
          (win_rate 56)
          (rank 49)
        )
        ({}
          (arena models)
          (category dataviz)
          (elo 1189)
          (win_rate 52.8)
          (rank 56)
        )
        ({}
          (arena models)
          (category gamedev)
          (elo 1171)
          (win_rate 52.5)
          (rank 62)
        )
        ({}
          (arena models)
          (category svg)
          (elo 1112)
          (win_rate 50.1)
          (rank 54)
        )
        ({}
          (arena models)
          (category uicomponent)
          (elo 1216)
          (win_rate 59.5)
          (rank 41)
        )
        ({}
          (arena models)
          (category website)
          (elo 1209)
          (win_rate 56.4)
          (rank 52)
        )
      ))
      (artificial_analysis ({}
        (intelligence_index 30.6)
        (coding_index 43.5)
        (agentic_index 18.1)
      ))
    ))
    (reasoning ({}
      (mandatory false)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId deepseek/deepseek-v3.1-terminus)
  ))
)
