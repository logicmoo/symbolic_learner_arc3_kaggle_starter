({}
  (kind model)
  (id openrouter-xiaomi_mimo-v2.5)
  (label "Xiaomi: MiMo-V2.5")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model xiaomi/mimo-v2.5)
  (enabled true)
  (capabilities ({}
    (audio true)
    (code false)
    (functionCalling true)
    (json true)
    (jsonMode true)
    (local false)
    (multimodal true)
    (reasoning true)
    (text true)
    (tools true)
    (vision true)
  ))
  (limits ({}
    (contextWindow 1050000)
    (maxOutputTokens 131072)
  ))
  (pricing ({}
    (prompt "0.00000014")
    (completion "0.00000028")
    (input_cache_read "0.0000000028")
  ))
  (properties ({}
    (id xiaomi/mimo-v2.5)
    (canonical_slug xiaomi/mimo-v2.5-20260422)
    (hugging_face_id XiaomiMiMo/MiMo-V2.5)
    (name "Xiaomi: MiMo-V2.5")
    (created 1776874269)
    (description "MiMo-V2.5 is a native omnimodal model by Xiaomi. It delivers Pro-level agentic performance at roughly half the inference cost, while surpassing MiMo-V2-Omni in multimodal perception across image and video understanding...")
    (context_length 1050000)
    (architecture ({}
      (modality text+image+audio+video->text)
      (input_modalities (
        text
        audio
        image
        video
      ))
      (output_modalities (
        text
      ))
      (tokenizer Other)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.00000014")
      (completion "0.00000028")
      (input_cache_read "0.0000000028")
    ))
    (top_provider ({}
      (context_length 1048576)
      (max_completion_tokens 131072)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
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
      (details /api/v1/models/xiaomi/mimo-v2.5-20260422/endpoints)
    ))
    (benchmarks ({}
      (design_arena (
        ({}
          (arena models)
          (category 3d)
          (elo 1268)
          (win_rate 51.8)
          (rank 28)
        )
        ({}
          (arena models)
          (category asciiart)
          (elo 1175)
          (win_rate 45.8)
          (rank 38)
        )
        ({}
          (arena models)
          (category codecategories)
          (elo 1289)
          (win_rate 55.1)
          (rank 18)
        )
        ({}
          (arena models)
          (category dataviz)
          (elo 1281)
          (win_rate 55.4)
          (rank 18)
        )
        ({}
          (arena models)
          (category gamedev)
          (elo 1279)
          (win_rate 55.5)
          (rank 22)
        )
        ({}
          (arena models)
          (category svg)
          (elo 1217)
          (win_rate 52.5)
          (rank 23)
        )
        ({}
          (arena models)
          (category uicomponent)
          (elo 1291)
          (win_rate 55.3)
          (rank 20)
        )
        ({}
          (arena models)
          (category website)
          (elo 1291)
          (win_rate 55.5)
          (rank 20)
        )
      ))
      (artificial_analysis ({}
        (intelligence_index 38)
        (coding_index 56.8)
        (agentic_index 24.4)
      ))
    ))
    (reasoning ({}
      (mandatory false)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id xiaomi/mimo-v2.5)
    (canonical_slug xiaomi/mimo-v2.5-20260422)
    (hugging_face_id XiaomiMiMo/MiMo-V2.5)
    (name "Xiaomi: MiMo-V2.5")
    (created 1776874269)
    (description "MiMo-V2.5 is a native omnimodal model by Xiaomi. It delivers Pro-level agentic performance at roughly half the inference cost, while surpassing MiMo-V2-Omni in multimodal perception across image and video understanding...")
    (context_length 1050000)
    (architecture ({}
      (modality text+image+audio+video->text)
      (input_modalities (
        text
        audio
        image
        video
      ))
      (output_modalities (
        text
      ))
      (tokenizer Other)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.00000014")
      (completion "0.00000028")
      (input_cache_read "0.0000000028")
    ))
    (top_provider ({}
      (context_length 1048576)
      (max_completion_tokens 131072)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
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
      (details /api/v1/models/xiaomi/mimo-v2.5-20260422/endpoints)
    ))
    (benchmarks ({}
      (design_arena (
        ({}
          (arena models)
          (category 3d)
          (elo 1268)
          (win_rate 51.8)
          (rank 28)
        )
        ({}
          (arena models)
          (category asciiart)
          (elo 1175)
          (win_rate 45.8)
          (rank 38)
        )
        ({}
          (arena models)
          (category codecategories)
          (elo 1289)
          (win_rate 55.1)
          (rank 18)
        )
        ({}
          (arena models)
          (category dataviz)
          (elo 1281)
          (win_rate 55.4)
          (rank 18)
        )
        ({}
          (arena models)
          (category gamedev)
          (elo 1279)
          (win_rate 55.5)
          (rank 22)
        )
        ({}
          (arena models)
          (category svg)
          (elo 1217)
          (win_rate 52.5)
          (rank 23)
        )
        ({}
          (arena models)
          (category uicomponent)
          (elo 1291)
          (win_rate 55.3)
          (rank 20)
        )
        ({}
          (arena models)
          (category website)
          (elo 1291)
          (win_rate 55.5)
          (rank 20)
        )
      ))
      (artificial_analysis ({}
        (intelligence_index 38)
        (coding_index 56.8)
        (agentic_index 24.4)
      ))
    ))
    (reasoning ({}
      (mandatory false)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId xiaomi/mimo-v2.5)
  ))
)
