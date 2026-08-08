(
  (kind model)
  (id openrouter-xiaomi_mimo-v2.5-pro)
  (label "Xiaomi: MiMo-V2.5-Pro")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model xiaomi/mimo-v2.5-pro)
  (enabled true)
  (capabilities (
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
  (limits (
    (contextWindow 1050000)
    (maxOutputTokens 131072)
  ))
  (pricing (
    (prompt "0.000000435")
    (completion "0.00000087")
    (input_cache_read "0.0000000036")
  ))
  (properties (
    (id xiaomi/mimo-v2.5-pro)
    (canonical_slug xiaomi/mimo-v2.5-pro-20260422)
    (hugging_face_id XiaomiMiMo/MiMo-V2.5-Pro)
    (name "Xiaomi: MiMo-V2.5-Pro")
    (created 1776874273)
    (description "MiMo-V2.5-Pro is Xiaomi’s flagship model, delivering strong performance in general agentic capabilities, complex software engineering, and long-horizon tasks, with top rankings on benchmarks such as ClawEval, GDPVal, and SWE-bench Pro....")
    (context_length 1050000)
    (architecture (
      (modality text->text)
      (input_modalities ([]
        text
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Other)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.000000435")
      (completion "0.00000087")
      (input_cache_read "0.0000000036")
    ))
    (top_provider (
      (context_length 1048576)
      (max_completion_tokens 131072)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      frequency_penalty
      include_reasoning
      logit_bias
      logprobs
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
      top_logprobs
      top_p
    ))
    (default_parameters (
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
    (links (
      (details /api/v1/models/xiaomi/mimo-v2.5-pro-20260422/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena models)
          (category 3d)
          (elo 1304)
          (win_rate 56.9)
          (rank 15)
        )
        (
          (arena models)
          (category asciiart)
          (elo 1187)
          (win_rate 48)
          (rank 30)
        )
        (
          (arena models)
          (category codecategories)
          (elo 1304)
          (win_rate 56.3)
          (rank 13)
        )
        (
          (arena models)
          (category dataviz)
          (elo 1298)
          (win_rate 54.9)
          (rank 13)
        )
        (
          (arena models)
          (category gamedev)
          (elo 1312)
          (win_rate 58.5)
          (rank 11)
        )
        (
          (arena models)
          (category svg)
          (elo 1223)
          (win_rate 51.9)
          (rank 21)
        )
        (
          (arena models)
          (category uicomponent)
          (elo 1289)
          (win_rate 55.1)
          (rank 21)
        )
        (
          (arena models)
          (category website)
          (elo 1300)
          (win_rate 55.8)
          (rank 11)
        )
      ))
      (artificial_analysis (
        (intelligence_index 42.9)
        (coding_index 60.2)
        (agentic_index 29.5)
      ))
    ))
    (reasoning (
      (mandatory false)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id xiaomi/mimo-v2.5-pro)
    (canonical_slug xiaomi/mimo-v2.5-pro-20260422)
    (hugging_face_id XiaomiMiMo/MiMo-V2.5-Pro)
    (name "Xiaomi: MiMo-V2.5-Pro")
    (created 1776874273)
    (description "MiMo-V2.5-Pro is Xiaomi’s flagship model, delivering strong performance in general agentic capabilities, complex software engineering, and long-horizon tasks, with top rankings on benchmarks such as ClawEval, GDPVal, and SWE-bench Pro....")
    (context_length 1050000)
    (architecture (
      (modality text->text)
      (input_modalities ([]
        text
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Other)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.000000435")
      (completion "0.00000087")
      (input_cache_read "0.0000000036")
    ))
    (top_provider (
      (context_length 1048576)
      (max_completion_tokens 131072)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      frequency_penalty
      include_reasoning
      logit_bias
      logprobs
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
      top_logprobs
      top_p
    ))
    (default_parameters (
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
    (links (
      (details /api/v1/models/xiaomi/mimo-v2.5-pro-20260422/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena models)
          (category 3d)
          (elo 1304)
          (win_rate 56.9)
          (rank 15)
        )
        (
          (arena models)
          (category asciiart)
          (elo 1187)
          (win_rate 48)
          (rank 30)
        )
        (
          (arena models)
          (category codecategories)
          (elo 1304)
          (win_rate 56.3)
          (rank 13)
        )
        (
          (arena models)
          (category dataviz)
          (elo 1298)
          (win_rate 54.9)
          (rank 13)
        )
        (
          (arena models)
          (category gamedev)
          (elo 1312)
          (win_rate 58.5)
          (rank 11)
        )
        (
          (arena models)
          (category svg)
          (elo 1223)
          (win_rate 51.9)
          (rank 21)
        )
        (
          (arena models)
          (category uicomponent)
          (elo 1289)
          (win_rate 55.1)
          (rank 21)
        )
        (
          (arena models)
          (category website)
          (elo 1300)
          (win_rate 55.8)
          (rank 11)
        )
      ))
      (artificial_analysis (
        (intelligence_index 42.9)
        (coding_index 60.2)
        (agentic_index 29.5)
      ))
    ))
    (reasoning (
      (mandatory false)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId xiaomi/mimo-v2.5-pro)
  ))
)
