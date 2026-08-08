({}
  (kind model)
  (id openrouter-moonshotai_kimi-k3)
  (label "MoonshotAI: Kimi K3")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model moonshotai/kimi-k3)
  (enabled true)
  (capabilities ({}
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
  (limits ({}
    (contextWindow 1048576)
    (maxOutputTokens null)
  ))
  (pricing ({}
    (prompt "0.000003")
    (completion "0.000015")
    (input_cache_read "0.0000003")
  ))
  (properties ({}
    (id moonshotai/kimi-k3)
    (canonical_slug moonshotai/kimi-k3-20260715)
    (hugging_face_id moonshotai/Kimi-K3)
    (name "MoonshotAI: Kimi K3")
    (created 1784215858)
    (description "Kimi K3 is a 2.8T parameter open-weight multimodal reasoning model from Moonshot AI. It is suited for complex coding, knowledge work, and long-horizon agentic workflows, and is particularly strong at...")
    (context_length 1048576)
    (architecture ({}
      (modality text+image->text)
      (input_modalities (
        text
        image
      ))
      (output_modalities (
        text
      ))
      (tokenizer Other)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.000003")
      (completion "0.000015")
      (input_cache_read "0.0000003")
    ))
    (top_provider ({}
      (context_length 1048576)
      (max_completion_tokens null)
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
      reasoning_effort
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
      (temperature null)
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
      (details /api/v1/models/moonshotai/kimi-k3-20260715/endpoints)
    ))
    (benchmarks ({}
      (design_arena (
        ({}
          (arena agents)
          (category godotgamedev)
          (elo 1199)
          (win_rate 48.5)
          (rank 11)
        )
        ({}
          (arena agents)
          (category python-pptxslides)
          (elo 1373)
          (win_rate 70.5)
          (rank 1)
        )
        ({}
          (arena agents)
          (category webapps)
          (elo 1328)
          (win_rate 63.2)
          (rank 1)
        )
        ({}
          (arena models)
          (category 3d)
          (elo 1453)
          (win_rate 69.4)
          (rank 1)
        )
        ({}
          (arena models)
          (category codecategories)
          (elo 1415)
          (win_rate 66.7)
          (rank 1)
        )
        ({}
          (arena models)
          (category dataviz)
          (elo 1382)
          (win_rate 65.6)
          (rank 2)
        )
        ({}
          (arena models)
          (category uicomponent)
          (elo 1393)
          (win_rate 64.5)
          (rank 1)
        )
        ({}
          (arena models)
          (category website)
          (elo 1378)
          (win_rate 63.5)
          (rank 1)
        )
      ))
      (artificial_analysis ({}
        (intelligence_index 59.7)
        (coding_index 76.2)
        (agentic_index 54.3)
      ))
    ))
    (reasoning ({}
      (mandatory false)
      (default_enabled true)
      (supported_efforts (
        max
        high
        low
      ))
      (default_effort max)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id moonshotai/kimi-k3)
    (canonical_slug moonshotai/kimi-k3-20260715)
    (hugging_face_id moonshotai/Kimi-K3)
    (name "MoonshotAI: Kimi K3")
    (created 1784215858)
    (description "Kimi K3 is a 2.8T parameter open-weight multimodal reasoning model from Moonshot AI. It is suited for complex coding, knowledge work, and long-horizon agentic workflows, and is particularly strong at...")
    (context_length 1048576)
    (architecture ({}
      (modality text+image->text)
      (input_modalities (
        text
        image
      ))
      (output_modalities (
        text
      ))
      (tokenizer Other)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.000003")
      (completion "0.000015")
      (input_cache_read "0.0000003")
    ))
    (top_provider ({}
      (context_length 1048576)
      (max_completion_tokens null)
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
      reasoning_effort
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
      (temperature null)
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
      (details /api/v1/models/moonshotai/kimi-k3-20260715/endpoints)
    ))
    (benchmarks ({}
      (design_arena (
        ({}
          (arena agents)
          (category godotgamedev)
          (elo 1199)
          (win_rate 48.5)
          (rank 11)
        )
        ({}
          (arena agents)
          (category python-pptxslides)
          (elo 1373)
          (win_rate 70.5)
          (rank 1)
        )
        ({}
          (arena agents)
          (category webapps)
          (elo 1328)
          (win_rate 63.2)
          (rank 1)
        )
        ({}
          (arena models)
          (category 3d)
          (elo 1453)
          (win_rate 69.4)
          (rank 1)
        )
        ({}
          (arena models)
          (category codecategories)
          (elo 1415)
          (win_rate 66.7)
          (rank 1)
        )
        ({}
          (arena models)
          (category dataviz)
          (elo 1382)
          (win_rate 65.6)
          (rank 2)
        )
        ({}
          (arena models)
          (category uicomponent)
          (elo 1393)
          (win_rate 64.5)
          (rank 1)
        )
        ({}
          (arena models)
          (category website)
          (elo 1378)
          (win_rate 63.5)
          (rank 1)
        )
      ))
      (artificial_analysis ({}
        (intelligence_index 59.7)
        (coding_index 76.2)
        (agentic_index 54.3)
      ))
    ))
    (reasoning ({}
      (mandatory false)
      (default_enabled true)
      (supported_efforts (
        max
        high
        low
      ))
      (default_effort max)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId moonshotai/kimi-k3)
  ))
)
