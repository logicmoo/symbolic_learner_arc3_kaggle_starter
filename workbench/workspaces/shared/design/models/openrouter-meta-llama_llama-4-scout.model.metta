(
  (kind model)
  (id openrouter-meta-llama_llama-4-scout)
  (label "Meta: Llama 4 Scout")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model meta-llama/llama-4-scout)
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
    (contextWindow 1310720)
    (maxOutputTokens 16384)
  ))
  (pricing (
    (prompt "0.0000001")
    (completion "0.0000003")
  ))
  (properties (
    (id meta-llama/llama-4-scout)
    (canonical_slug meta-llama/llama-4-scout-17b-16e-instruct)
    (hugging_face_id meta-llama/Llama-4-Scout-17B-16E-Instruct)
    (name "Meta: Llama 4 Scout")
    (created 1743881519)
    (description "Llama 4 Scout 17B Instruct (16E) is a mixture-of-experts (MoE) language model developed by Meta, activating 17 billion parameters out of a total of 109B. It supports native multimodal input...")
    (context_length 1310720)
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
      (prompt "0.0000001")
      (completion "0.0000003")
    ))
    (top_provider (
      (context_length 327680)
      (max_completion_tokens 16384)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
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
    (default_parameters ())
    (supported_voices null)
    (knowledge_cutoff 2024-08-31)
    (expiration_date null)
    (links (
      (details /api/v1/models/meta-llama/llama-4-scout-17b-16e-instruct/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena models)
          (category codecategories)
          (elo 818)
          (win_rate 26.6)
          (rank 116)
        )
        (
          (arena models)
          (category dataviz)
          (elo 923)
          (win_rate 39.3)
          (rank 108)
        )
        (
          (arena models)
          (category gamedev)
          (elo 813)
          (win_rate 27.4)
          (rank 115)
        )
        (
          (arena models)
          (category uicomponent)
          (elo 801)
          (win_rate 25.5)
          (rank 110)
        )
        (
          (arena models)
          (category website)
          (elo 772)
          (win_rate 22.7)
          (rank 123)
        )
      ))
      (artificial_analysis (
        (intelligence_index 10.3)
        (coding_index 8.2)
        (agentic_index 1.1)
      ))
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id meta-llama/llama-4-scout)
    (canonical_slug meta-llama/llama-4-scout-17b-16e-instruct)
    (hugging_face_id meta-llama/Llama-4-Scout-17B-16E-Instruct)
    (name "Meta: Llama 4 Scout")
    (created 1743881519)
    (description "Llama 4 Scout 17B Instruct (16E) is a mixture-of-experts (MoE) language model developed by Meta, activating 17 billion parameters out of a total of 109B. It supports native multimodal input...")
    (context_length 1310720)
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
      (prompt "0.0000001")
      (completion "0.0000003")
    ))
    (top_provider (
      (context_length 327680)
      (max_completion_tokens 16384)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
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
    (default_parameters ())
    (supported_voices null)
    (knowledge_cutoff 2024-08-31)
    (expiration_date null)
    (links (
      (details /api/v1/models/meta-llama/llama-4-scout-17b-16e-instruct/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena models)
          (category codecategories)
          (elo 818)
          (win_rate 26.6)
          (rank 116)
        )
        (
          (arena models)
          (category dataviz)
          (elo 923)
          (win_rate 39.3)
          (rank 108)
        )
        (
          (arena models)
          (category gamedev)
          (elo 813)
          (win_rate 27.4)
          (rank 115)
        )
        (
          (arena models)
          (category uicomponent)
          (elo 801)
          (win_rate 25.5)
          (rank 110)
        )
        (
          (arena models)
          (category website)
          (elo 772)
          (win_rate 22.7)
          (rank 123)
        )
      ))
      (artificial_analysis (
        (intelligence_index 10.3)
        (coding_index 8.2)
        (agentic_index 1.1)
      ))
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId meta-llama/llama-4-scout)
  ))
)
