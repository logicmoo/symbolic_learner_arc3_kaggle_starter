(
  (kind model)
  (id openrouter-meta-llama_llama-4-maverick)
  (label "Meta: Llama 4 Maverick")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model meta-llama/llama-4-maverick)
  (enabled true)
  (capabilities (
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
  (limits (
    (contextWindow 1048576)
    (maxOutputTokens 16384)
  ))
  (pricing (
    (prompt "0.0000002")
    (completion "0.0000008")
  ))
  (properties (
    (id meta-llama/llama-4-maverick)
    (canonical_slug meta-llama/llama-4-maverick-17b-128e-instruct)
    (hugging_face_id meta-llama/Llama-4-Maverick-17B-128E-Instruct)
    (name "Meta: Llama 4 Maverick")
    (created 1743881822)
    (description "Llama 4 Maverick 17B Instruct (128E) is a high-capacity multimodal language model from Meta, built on a mixture-of-experts (MoE) architecture with 128 experts and 17 billion active parameters per forward...")
    (context_length 1048576)
    (architecture (
      (modality text+image->text)
      (input_modalities ([]
        text
        image
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Llama4)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.0000002")
      (completion "0.0000008")
    ))
    (top_provider (
      (context_length 1048576)
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
    (knowledge_cutoff 2024-08-31)
    (expiration_date null)
    (links (
      (details /api/v1/models/meta-llama/llama-4-maverick-17b-128e-instruct/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena models)
          (category 3d)
          (elo 954)
          (win_rate 40.2)
          (rank 102)
        )
        (
          (arena models)
          (category codecategories)
          (elo 908)
          (win_rate 35.8)
          (rank 113)
        )
        (
          (arena models)
          (category dataviz)
          (elo 909)
          (win_rate 38.4)
          (rank 110)
        )
        (
          (arena models)
          (category gamedev)
          (elo 878)
          (win_rate 33.7)
          (rank 113)
        )
        (
          (arena models)
          (category uicomponent)
          (elo 933)
          (win_rate 40.8)
          (rank 105)
        )
        (
          (arena models)
          (category website)
          (elo 893)
          (win_rate 34.4)
          (rank 117)
        )
      ))
      (artificial_analysis (
        (intelligence_index 14.5)
        (coding_index 16.3)
        (agentic_index 1.2)
      ))
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id meta-llama/llama-4-maverick)
    (canonical_slug meta-llama/llama-4-maverick-17b-128e-instruct)
    (hugging_face_id meta-llama/Llama-4-Maverick-17B-128E-Instruct)
    (name "Meta: Llama 4 Maverick")
    (created 1743881822)
    (description "Llama 4 Maverick 17B Instruct (128E) is a high-capacity multimodal language model from Meta, built on a mixture-of-experts (MoE) architecture with 128 experts and 17 billion active parameters per forward...")
    (context_length 1048576)
    (architecture (
      (modality text+image->text)
      (input_modalities ([]
        text
        image
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Llama4)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.0000002")
      (completion "0.0000008")
    ))
    (top_provider (
      (context_length 1048576)
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
    (knowledge_cutoff 2024-08-31)
    (expiration_date null)
    (links (
      (details /api/v1/models/meta-llama/llama-4-maverick-17b-128e-instruct/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena models)
          (category 3d)
          (elo 954)
          (win_rate 40.2)
          (rank 102)
        )
        (
          (arena models)
          (category codecategories)
          (elo 908)
          (win_rate 35.8)
          (rank 113)
        )
        (
          (arena models)
          (category dataviz)
          (elo 909)
          (win_rate 38.4)
          (rank 110)
        )
        (
          (arena models)
          (category gamedev)
          (elo 878)
          (win_rate 33.7)
          (rank 113)
        )
        (
          (arena models)
          (category uicomponent)
          (elo 933)
          (win_rate 40.8)
          (rank 105)
        )
        (
          (arena models)
          (category website)
          (elo 893)
          (win_rate 34.4)
          (rank 117)
        )
      ))
      (artificial_analysis (
        (intelligence_index 14.5)
        (coding_index 16.3)
        (agentic_index 1.2)
      ))
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId meta-llama/llama-4-maverick)
  ))
)
