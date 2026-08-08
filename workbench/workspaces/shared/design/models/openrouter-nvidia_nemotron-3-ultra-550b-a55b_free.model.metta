({}
  (kind model)
  (id openrouter-nvidia_nemotron-3-ultra-550b-a55b_free)
  (label "NVIDIA: Nemotron 3 Ultra (free)")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model nvidia/nemotron-3-ultra-550b-a55b:free)
  (enabled true)
  (capabilities ({}
    (audio false)
    (code false)
    (functionCalling true)
    (json false)
    (jsonMode false)
    (local false)
    (multimodal false)
    (reasoning true)
    (text true)
    (tools true)
    (vision false)
  ))
  (limits ({}
    (contextWindow 1000000)
    (maxOutputTokens 65536)
  ))
  (pricing ({}
    (prompt "0")
    (completion "0")
  ))
  (properties ({}
    (id nvidia/nemotron-3-ultra-550b-a55b:free)
    (canonical_slug nvidia/nemotron-3-ultra-550b-a55b-20260604)
    (hugging_face_id nvidia/NVIDIA-Nemotron-3-Ultra-550B-A55B-BF16)
    (name "NVIDIA: Nemotron 3 Ultra (free)")
    (created 1780551208)
    (description "NVIDIA Nemotron 3 Ultra is an open frontier-reasoning and orchestration model from NVIDIA, with 55B active parameters out of 550B total (MoE). Built on a hybrid Transformer-Mamba mixture-of-experts architecture, it...")
    (context_length 1000000)
    (architecture ({}
      (modality text->text)
      (input_modalities (
        text
      ))
      (output_modalities (
        text
      ))
      (tokenizer Other)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0")
      (completion "0")
    ))
    (top_provider ({}
      (context_length 1000000)
      (max_completion_tokens 65536)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      include_reasoning
      max_tokens
      reasoning
      reasoning_effort
      seed
      temperature
      tool_choice
      tools
      top_p
    ))
    (default_parameters ({}
      (temperature 1)
      (top_p 0.95)
      (top_k null)
      (frequency_penalty null)
      (presence_penalty null)
      (repetition_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/nvidia/nemotron-3-ultra-550b-a55b-20260604/endpoints)
    ))
    (benchmarks ({}
      (design_arena (
        ({}
          (arena models)
          (category 3d)
          (elo 1186)
          (win_rate 41.2)
          (rank 52)
        )
        ({}
          (arena models)
          (category asciiart)
          (elo 1118)
          (win_rate 37.7)
          (rank 51)
        )
        ({}
          (arena models)
          (category codecategories)
          (elo 1155)
          (win_rate 36.1)
          (rank 71)
        )
        ({}
          (arena models)
          (category dataviz)
          (elo 1153)
          (win_rate 37.5)
          (rank 71)
        )
        ({}
          (arena models)
          (category gamedev)
          (elo 1169)
          (win_rate 38.7)
          (rank 64)
        )
        ({}
          (arena models)
          (category svg)
          (elo 1126)
          (win_rate 37.5)
          (rank 50)
        )
        ({}
          (arena models)
          (category uicomponent)
          (elo 1177)
          (win_rate 39.2)
          (rank 60)
        )
        ({}
          (arena models)
          (category website)
          (elo 1133)
          (win_rate 33)
          (rank 84)
        )
      ))
      (artificial_analysis ({}
        (intelligence_index 38.3)
        (coding_index 49.3)
        (agentic_index 27.5)
      ))
    ))
    (reasoning ({}
      (mandatory false)
      (default_enabled true)
      (supports_max_tokens true)
      (supported_efforts (
        high
        medium
      ))
      (default_effort high)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id nvidia/nemotron-3-ultra-550b-a55b:free)
    (canonical_slug nvidia/nemotron-3-ultra-550b-a55b-20260604)
    (hugging_face_id nvidia/NVIDIA-Nemotron-3-Ultra-550B-A55B-BF16)
    (name "NVIDIA: Nemotron 3 Ultra (free)")
    (created 1780551208)
    (description "NVIDIA Nemotron 3 Ultra is an open frontier-reasoning and orchestration model from NVIDIA, with 55B active parameters out of 550B total (MoE). Built on a hybrid Transformer-Mamba mixture-of-experts architecture, it...")
    (context_length 1000000)
    (architecture ({}
      (modality text->text)
      (input_modalities (
        text
      ))
      (output_modalities (
        text
      ))
      (tokenizer Other)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0")
      (completion "0")
    ))
    (top_provider ({}
      (context_length 1000000)
      (max_completion_tokens 65536)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      include_reasoning
      max_tokens
      reasoning
      reasoning_effort
      seed
      temperature
      tool_choice
      tools
      top_p
    ))
    (default_parameters ({}
      (temperature 1)
      (top_p 0.95)
      (top_k null)
      (frequency_penalty null)
      (presence_penalty null)
      (repetition_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/nvidia/nemotron-3-ultra-550b-a55b-20260604/endpoints)
    ))
    (benchmarks ({}
      (design_arena (
        ({}
          (arena models)
          (category 3d)
          (elo 1186)
          (win_rate 41.2)
          (rank 52)
        )
        ({}
          (arena models)
          (category asciiart)
          (elo 1118)
          (win_rate 37.7)
          (rank 51)
        )
        ({}
          (arena models)
          (category codecategories)
          (elo 1155)
          (win_rate 36.1)
          (rank 71)
        )
        ({}
          (arena models)
          (category dataviz)
          (elo 1153)
          (win_rate 37.5)
          (rank 71)
        )
        ({}
          (arena models)
          (category gamedev)
          (elo 1169)
          (win_rate 38.7)
          (rank 64)
        )
        ({}
          (arena models)
          (category svg)
          (elo 1126)
          (win_rate 37.5)
          (rank 50)
        )
        ({}
          (arena models)
          (category uicomponent)
          (elo 1177)
          (win_rate 39.2)
          (rank 60)
        )
        ({}
          (arena models)
          (category website)
          (elo 1133)
          (win_rate 33)
          (rank 84)
        )
      ))
      (artificial_analysis ({}
        (intelligence_index 38.3)
        (coding_index 49.3)
        (agentic_index 27.5)
      ))
    ))
    (reasoning ({}
      (mandatory false)
      (default_enabled true)
      (supports_max_tokens true)
      (supported_efforts (
        high
        medium
      ))
      (default_effort high)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId nvidia/nemotron-3-ultra-550b-a55b:free)
  ))
)
