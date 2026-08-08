(
  (kind model)
  (id openrouter-moonshotai_kimi-k2.5)
  (label "MoonshotAI: Kimi K2.5")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model moonshotai/kimi-k2.5)
  (enabled true)
  (capabilities (
    (audio false)
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
  (limits (
    (contextWindow 262144)
    (maxOutputTokens 262144)
  ))
  (pricing (
    (prompt "0.00000057")
    (completion "0.00000285")
    (input_cache_read "0.000000095")
  ))
  (properties (
    (id moonshotai/kimi-k2.5)
    (canonical_slug moonshotai/kimi-k2.5-0127)
    (hugging_face_id moonshotai/Kimi-K2.5)
    (name "MoonshotAI: Kimi K2.5")
    (created 1769487076)
    (description "Kimi K2.5 is Moonshot AI's native multimodal model, delivering state-of-the-art visual coding capability and a self-directed agent swarm paradigm. Built on Kimi K2 with continued pretraining over approximately 15T mixed...")
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
      (tokenizer Other)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.00000057")
      (completion "0.00000285")
      (input_cache_read "0.000000095")
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
      (temperature null)
      (top_p null)
      (top_k null)
      (frequency_penalty null)
      (presence_penalty null)
      (repetition_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links (
      (details /api/v1/models/moonshotai/kimi-k2.5-0127/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena agents)
          (category androidnative)
          (elo 1150)
          (win_rate 58)
          (rank 21)
        )
        (
          (arena agents)
          (category fullstack)
          (elo 1157)
          (win_rate 54.2)
          (rank 19)
        )
        (
          (arena agents)
          (category godotgamedev)
          (elo 1219)
          (win_rate 59.8)
          (rank 9)
        )
        (
          (arena agents)
          (category mobileapps)
          (elo 1204)
          (win_rate 54.2)
          (rank 15)
        )
        (
          (arena agents)
          (category webapps)
          (elo 1184)
          (win_rate 51.3)
          (rank 20)
        )
        (
          (arena models)
          (category 3d)
          (elo 1259)
          (win_rate 53.1)
          (rank 31)
        )
        (
          (arena models)
          (category asciiart)
          (elo 1205)
          (win_rate 46.5)
          (rank 19)
        )
        (
          (arena models)
          (category codecategories)
          (elo 1265)
          (win_rate 54.1)
          (rank 28)
        )
        (
          (arena models)
          (category dataviz)
          (elo 1248)
          (win_rate 51.3)
          (rank 33)
        )
        (
          (arena models)
          (category gamedev)
          (elo 1247)
          (win_rate 53.4)
          (rank 32)
        )
        (
          (arena models)
          (category svg)
          (elo 1195)
          (win_rate 48.4)
          (rank 33)
        )
        (
          (arena models)
          (category uicomponent)
          (elo 1270)
          (win_rate 53.6)
          (rank 27)
        )
        (
          (arena models)
          (category website)
          (elo 1272)
          (win_rate 55.2)
          (rank 25)
        )
      ))
      (artificial_analysis (
        (intelligence_index 36)
        (coding_index 46.8)
        (agentic_index 21.7)
      ))
    ))
    (reasoning (
      (mandatory false)
      (default_enabled true)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id moonshotai/kimi-k2.5)
    (canonical_slug moonshotai/kimi-k2.5-0127)
    (hugging_face_id moonshotai/Kimi-K2.5)
    (name "MoonshotAI: Kimi K2.5")
    (created 1769487076)
    (description "Kimi K2.5 is Moonshot AI's native multimodal model, delivering state-of-the-art visual coding capability and a self-directed agent swarm paradigm. Built on Kimi K2 with continued pretraining over approximately 15T mixed...")
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
      (tokenizer Other)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.00000057")
      (completion "0.00000285")
      (input_cache_read "0.000000095")
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
      (temperature null)
      (top_p null)
      (top_k null)
      (frequency_penalty null)
      (presence_penalty null)
      (repetition_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links (
      (details /api/v1/models/moonshotai/kimi-k2.5-0127/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena agents)
          (category androidnative)
          (elo 1150)
          (win_rate 58)
          (rank 21)
        )
        (
          (arena agents)
          (category fullstack)
          (elo 1157)
          (win_rate 54.2)
          (rank 19)
        )
        (
          (arena agents)
          (category godotgamedev)
          (elo 1219)
          (win_rate 59.8)
          (rank 9)
        )
        (
          (arena agents)
          (category mobileapps)
          (elo 1204)
          (win_rate 54.2)
          (rank 15)
        )
        (
          (arena agents)
          (category webapps)
          (elo 1184)
          (win_rate 51.3)
          (rank 20)
        )
        (
          (arena models)
          (category 3d)
          (elo 1259)
          (win_rate 53.1)
          (rank 31)
        )
        (
          (arena models)
          (category asciiart)
          (elo 1205)
          (win_rate 46.5)
          (rank 19)
        )
        (
          (arena models)
          (category codecategories)
          (elo 1265)
          (win_rate 54.1)
          (rank 28)
        )
        (
          (arena models)
          (category dataviz)
          (elo 1248)
          (win_rate 51.3)
          (rank 33)
        )
        (
          (arena models)
          (category gamedev)
          (elo 1247)
          (win_rate 53.4)
          (rank 32)
        )
        (
          (arena models)
          (category svg)
          (elo 1195)
          (win_rate 48.4)
          (rank 33)
        )
        (
          (arena models)
          (category uicomponent)
          (elo 1270)
          (win_rate 53.6)
          (rank 27)
        )
        (
          (arena models)
          (category website)
          (elo 1272)
          (win_rate 55.2)
          (rank 25)
        )
      ))
      (artificial_analysis (
        (intelligence_index 36)
        (coding_index 46.8)
        (agentic_index 21.7)
      ))
    ))
    (reasoning (
      (mandatory false)
      (default_enabled true)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId moonshotai/kimi-k2.5)
  ))
)
