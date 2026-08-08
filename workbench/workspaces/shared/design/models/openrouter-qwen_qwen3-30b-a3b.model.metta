({}
  (kind model)
  (id openrouter-qwen_qwen3-30b-a3b)
  (label "Qwen: Qwen3 30B A3B")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model qwen/qwen3-30b-a3b)
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
    (contextWindow 131072)
    (maxOutputTokens 16384)
  ))
  (pricing ({}
    (prompt "0.00000012")
    (completion "0.0000005")
  ))
  (properties ({}
    (id qwen/qwen3-30b-a3b)
    (canonical_slug qwen/qwen3-30b-a3b-04-28)
    (hugging_face_id Qwen/Qwen3-30B-A3B)
    (name "Qwen: Qwen3 30B A3B")
    (created 1745878604)
    (description "Qwen3, the latest generation in the Qwen large language model series, features both dense and mixture-of-experts (MoE) architectures to excel in reasoning, multilingual support, and advanced agent tasks. Its unique...")
    (context_length 131072)
    (architecture ({}
      (modality text->text)
      (input_modalities (
        text
      ))
      (output_modalities (
        text
      ))
      (tokenizer Qwen3)
      (instruct_type qwen3)
    ))
    (pricing ({}
      (prompt "0.00000012")
      (completion "0.0000005")
    ))
    (top_provider ({}
      (context_length 40960)
      (max_completion_tokens 16384)
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
      (details /api/v1/models/qwen/qwen3-30b-a3b-04-28/endpoints)
    ))
    (benchmarks ({}
      (design_arena (
        ({}
          (arena models)
          (category codecategories)
          (elo 970)
          (win_rate 37.5)
          (rank 110)
        )
        ({}
          (arena models)
          (category dataviz)
          (elo 995)
          (win_rate 39)
          (rank 99)
        )
        ({}
          (arena models)
          (category gamedev)
          (elo 939)
          (win_rate 33.9)
          (rank 110)
        )
        ({}
          (arena models)
          (category uicomponent)
          (elo 979)
          (win_rate 42.4)
          (rank 99)
        )
        ({}
          (arena models)
          (category website)
          (elo 977)
          (win_rate 37.7)
          (rank 112)
        )
      ))
    ))
    (reasoning ({}
      (mandatory false)
      (default_enabled true)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id qwen/qwen3-30b-a3b)
    (canonical_slug qwen/qwen3-30b-a3b-04-28)
    (hugging_face_id Qwen/Qwen3-30B-A3B)
    (name "Qwen: Qwen3 30B A3B")
    (created 1745878604)
    (description "Qwen3, the latest generation in the Qwen large language model series, features both dense and mixture-of-experts (MoE) architectures to excel in reasoning, multilingual support, and advanced agent tasks. Its unique...")
    (context_length 131072)
    (architecture ({}
      (modality text->text)
      (input_modalities (
        text
      ))
      (output_modalities (
        text
      ))
      (tokenizer Qwen3)
      (instruct_type qwen3)
    ))
    (pricing ({}
      (prompt "0.00000012")
      (completion "0.0000005")
    ))
    (top_provider ({}
      (context_length 40960)
      (max_completion_tokens 16384)
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
      (details /api/v1/models/qwen/qwen3-30b-a3b-04-28/endpoints)
    ))
    (benchmarks ({}
      (design_arena (
        ({}
          (arena models)
          (category codecategories)
          (elo 970)
          (win_rate 37.5)
          (rank 110)
        )
        ({}
          (arena models)
          (category dataviz)
          (elo 995)
          (win_rate 39)
          (rank 99)
        )
        ({}
          (arena models)
          (category gamedev)
          (elo 939)
          (win_rate 33.9)
          (rank 110)
        )
        ({}
          (arena models)
          (category uicomponent)
          (elo 979)
          (win_rate 42.4)
          (rank 99)
        )
        ({}
          (arena models)
          (category website)
          (elo 977)
          (win_rate 37.7)
          (rank 112)
        )
      ))
    ))
    (reasoning ({}
      (mandatory false)
      (default_enabled true)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId qwen/qwen3-30b-a3b)
  ))
)
