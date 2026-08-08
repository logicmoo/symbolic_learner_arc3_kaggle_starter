(
  (kind model)
  (id openrouter-nex-agi_nex-n2-pro)
  (label "Nex AGI: Nex-N2-Pro")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model nex-agi/nex-n2-pro)
  (enabled true)
  (capabilities (
    (audio false)
    (code false)
    (functionCalling true)
    (json false)
    (jsonMode false)
    (local false)
    (multimodal true)
    (reasoning true)
    (text true)
    (tools true)
    (vision true)
  ))
  (limits (
    (contextWindow 262144)
    (maxOutputTokens 262144)
  ))
  (pricing (
    (prompt "0.00000025")
    (completion "0.000001")
    (input_cache_read "0.000000025")
  ))
  (properties (
    (id nex-agi/nex-n2-pro)
    (canonical_slug nex-agi/nex-n2-pro)
    (hugging_face_id nex-agi/Nex-N2-Pro)
    (name "Nex AGI: Nex-N2-Pro")
    (created 1780937140)
    (description "Nex-N2-Pro is an agentic mixture-of-experts model from Nex AGI, with 17B active parameters out of 397B total. Built on the Qwen3.5 architecture, it accepts text and image input and produces...")
    (context_length 262144)
    (architecture (
      (modality text+image->text)
      (input_modalities ([]
        text
        image
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Qwen3)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.00000025")
      (completion "0.000001")
      (input_cache_read "0.000000025")
    ))
    (top_provider (
      (context_length 262144)
      (max_completion_tokens 262144)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      frequency_penalty
      include_reasoning
      logprobs
      max_tokens
      reasoning
      temperature
      tool_choice
      tools
      top_k
      top_logprobs
      top_p
    ))
    (default_parameters (
      (temperature 0.7)
      (top_p 0.95)
      (top_k 40)
      (frequency_penalty null)
      (presence_penalty null)
      (repetition_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links (
      (details /api/v1/models/nex-agi/nex-n2-pro/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena models)
          (category 3d)
          (elo 1304)
          (win_rate 53.7)
          (rank 16)
        )
        (
          (arena models)
          (category asciiart)
          (elo 1129)
          (win_rate 36.8)
          (rank 49)
        )
        (
          (arena models)
          (category codecategories)
          (elo 1264)
          (win_rate 49.8)
          (rank 29)
        )
        (
          (arena models)
          (category dataviz)
          (elo 1268)
          (win_rate 51.5)
          (rank 21)
        )
        (
          (arena models)
          (category gamedev)
          (elo 1261)
          (win_rate 50.3)
          (rank 27)
        )
        (
          (arena models)
          (category svg)
          (elo 1247)
          (win_rate 52.2)
          (rank 13)
        )
        (
          (arena models)
          (category uicomponent)
          (elo 1256)
          (win_rate 48.7)
          (rank 32)
        )
        (
          (arena models)
          (category website)
          (elo 1246)
          (win_rate 47.5)
          (rank 36)
        )
      ))
      (artificial_analysis (
        (intelligence_index 41.7)
        (coding_index 59.1)
        (agentic_index 31)
      ))
    ))
    (reasoning (
      (mandatory false)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id nex-agi/nex-n2-pro)
    (canonical_slug nex-agi/nex-n2-pro)
    (hugging_face_id nex-agi/Nex-N2-Pro)
    (name "Nex AGI: Nex-N2-Pro")
    (created 1780937140)
    (description "Nex-N2-Pro is an agentic mixture-of-experts model from Nex AGI, with 17B active parameters out of 397B total. Built on the Qwen3.5 architecture, it accepts text and image input and produces...")
    (context_length 262144)
    (architecture (
      (modality text+image->text)
      (input_modalities ([]
        text
        image
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Qwen3)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.00000025")
      (completion "0.000001")
      (input_cache_read "0.000000025")
    ))
    (top_provider (
      (context_length 262144)
      (max_completion_tokens 262144)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      frequency_penalty
      include_reasoning
      logprobs
      max_tokens
      reasoning
      temperature
      tool_choice
      tools
      top_k
      top_logprobs
      top_p
    ))
    (default_parameters (
      (temperature 0.7)
      (top_p 0.95)
      (top_k 40)
      (frequency_penalty null)
      (presence_penalty null)
      (repetition_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links (
      (details /api/v1/models/nex-agi/nex-n2-pro/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena models)
          (category 3d)
          (elo 1304)
          (win_rate 53.7)
          (rank 16)
        )
        (
          (arena models)
          (category asciiart)
          (elo 1129)
          (win_rate 36.8)
          (rank 49)
        )
        (
          (arena models)
          (category codecategories)
          (elo 1264)
          (win_rate 49.8)
          (rank 29)
        )
        (
          (arena models)
          (category dataviz)
          (elo 1268)
          (win_rate 51.5)
          (rank 21)
        )
        (
          (arena models)
          (category gamedev)
          (elo 1261)
          (win_rate 50.3)
          (rank 27)
        )
        (
          (arena models)
          (category svg)
          (elo 1247)
          (win_rate 52.2)
          (rank 13)
        )
        (
          (arena models)
          (category uicomponent)
          (elo 1256)
          (win_rate 48.7)
          (rank 32)
        )
        (
          (arena models)
          (category website)
          (elo 1246)
          (win_rate 47.5)
          (rank 36)
        )
      ))
      (artificial_analysis (
        (intelligence_index 41.7)
        (coding_index 59.1)
        (agentic_index 31)
      ))
    ))
    (reasoning (
      (mandatory false)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId nex-agi/nex-n2-pro)
  ))
)
