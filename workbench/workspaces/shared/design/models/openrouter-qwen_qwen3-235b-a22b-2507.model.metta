(
  (kind model)
  (id openrouter-qwen_qwen3-235b-a22b-2507)
  (label "Qwen: Qwen3 235B A22B Instruct 2507")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model qwen/qwen3-235b-a22b-2507)
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
    (contextWindow 262144)
    (maxOutputTokens 16384)
  ))
  (pricing (
    (prompt "0.00000009")
    (completion "0.00000055")
  ))
  (properties (
    (id qwen/qwen3-235b-a22b-2507)
    (canonical_slug qwen/qwen3-235b-a22b-07-25)
    (hugging_face_id Qwen/Qwen3-235B-A22B-Instruct-2507)
    (name "Qwen: Qwen3 235B A22B Instruct 2507")
    (created 1753119555)
    (description "Qwen3-235B-A22B-Instruct-2507 is a multilingual, instruction-tuned mixture-of-experts language model based on the Qwen3-235B architecture, with 22B active parameters per forward pass. It is optimized for general-purpose text generation, including instruction following,...")
    (context_length 262144)
    (architecture (
      (modality text->text)
      (input_modalities ([]
        text
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Qwen3)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.00000009")
      (completion "0.00000055")
    ))
    (top_provider (
      (context_length 262144)
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
    (knowledge_cutoff 2025-06-30)
    (expiration_date null)
    (links (
      (details /api/v1/models/qwen/qwen3-235b-a22b-07-25/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena models)
          (category 3d)
          (elo 1049)
          (win_rate 41.1)
          (rank 92)
        )
        (
          (arena models)
          (category codecategories)
          (elo 1066)
          (win_rate 42.7)
          (rank 91)
        )
        (
          (arena models)
          (category dataviz)
          (elo 1085)
          (win_rate 47.7)
          (rank 87)
        )
        (
          (arena models)
          (category gamedev)
          (elo 993)
          (win_rate 35.3)
          (rank 105)
        )
        (
          (arena models)
          (category uicomponent)
          (elo 1000)
          (win_rate 38.9)
          (rank 95)
        )
        (
          (arena models)
          (category website)
          (elo 1080)
          (win_rate 43.7)
          (rank 94)
        )
      ))
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id qwen/qwen3-235b-a22b-2507)
    (canonical_slug qwen/qwen3-235b-a22b-07-25)
    (hugging_face_id Qwen/Qwen3-235B-A22B-Instruct-2507)
    (name "Qwen: Qwen3 235B A22B Instruct 2507")
    (created 1753119555)
    (description "Qwen3-235B-A22B-Instruct-2507 is a multilingual, instruction-tuned mixture-of-experts language model based on the Qwen3-235B architecture, with 22B active parameters per forward pass. It is optimized for general-purpose text generation, including instruction following,...")
    (context_length 262144)
    (architecture (
      (modality text->text)
      (input_modalities ([]
        text
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Qwen3)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.00000009")
      (completion "0.00000055")
    ))
    (top_provider (
      (context_length 262144)
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
    (knowledge_cutoff 2025-06-30)
    (expiration_date null)
    (links (
      (details /api/v1/models/qwen/qwen3-235b-a22b-07-25/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena models)
          (category 3d)
          (elo 1049)
          (win_rate 41.1)
          (rank 92)
        )
        (
          (arena models)
          (category codecategories)
          (elo 1066)
          (win_rate 42.7)
          (rank 91)
        )
        (
          (arena models)
          (category dataviz)
          (elo 1085)
          (win_rate 47.7)
          (rank 87)
        )
        (
          (arena models)
          (category gamedev)
          (elo 993)
          (win_rate 35.3)
          (rank 105)
        )
        (
          (arena models)
          (category uicomponent)
          (elo 1000)
          (win_rate 38.9)
          (rank 95)
        )
        (
          (arena models)
          (category website)
          (elo 1080)
          (win_rate 43.7)
          (rank 94)
        )
      ))
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId qwen/qwen3-235b-a22b-2507)
  ))
)
