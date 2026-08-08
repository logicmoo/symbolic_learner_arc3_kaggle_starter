(
  (kind model)
  (id openrouter-mistralai_mistral-small-3.2-24b-instruct)
  (label "Mistral: Mistral Small 3.2 24B")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model mistralai/mistral-small-3.2-24b-instruct)
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
    (contextWindow 256000)
    (maxOutputTokens 16384)
  ))
  (pricing (
    (prompt "0.00000009375")
    (completion "0.00000025")
  ))
  (properties (
    (id mistralai/mistral-small-3.2-24b-instruct)
    (canonical_slug mistralai/mistral-small-3.2-24b-instruct-2506)
    (hugging_face_id mistralai/Mistral-Small-3.2-24B-Instruct-2506)
    (name "Mistral: Mistral Small 3.2 24B")
    (created 1750443016)
    (description "Mistral-Small-3.2-24B-Instruct-2506 is an updated 24B parameter model from Mistral optimized for instruction following, repetition reduction, and improved function calling. Compared to the 3.1 release, version 3.2 significantly improves accuracy on...")
    (context_length 256000)
    (architecture (
      (modality text+image->text)
      (input_modalities ([]
        image
        text
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Mistral)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.00000009375")
      (completion "0.00000025")
    ))
    (top_provider (
      (context_length 256000)
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
    (default_parameters (
      (temperature 0.3)
    ))
    (supported_voices null)
    (knowledge_cutoff 2023-10-31)
    (expiration_date null)
    (links (
      (details /api/v1/models/mistralai/mistral-small-3.2-24b-instruct-2506/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena models)
          (category codecategories)
          (elo 935)
          (win_rate 39.8)
          (rank 111)
        )
        (
          (arena models)
          (category dataviz)
          (elo 955)
          (win_rate 43.3)
          (rank 103)
        )
        (
          (arena models)
          (category gamedev)
          (elo 929)
          (win_rate 39.4)
          (rank 112)
        )
        (
          (arena models)
          (category uicomponent)
          (elo 940)
          (win_rate 40.5)
          (rank 104)
        )
        (
          (arena models)
          (category website)
          (elo 918)
          (win_rate 38.3)
          (rank 115)
        )
      ))
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id mistralai/mistral-small-3.2-24b-instruct)
    (canonical_slug mistralai/mistral-small-3.2-24b-instruct-2506)
    (hugging_face_id mistralai/Mistral-Small-3.2-24B-Instruct-2506)
    (name "Mistral: Mistral Small 3.2 24B")
    (created 1750443016)
    (description "Mistral-Small-3.2-24B-Instruct-2506 is an updated 24B parameter model from Mistral optimized for instruction following, repetition reduction, and improved function calling. Compared to the 3.1 release, version 3.2 significantly improves accuracy on...")
    (context_length 256000)
    (architecture (
      (modality text+image->text)
      (input_modalities ([]
        image
        text
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Mistral)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.00000009375")
      (completion "0.00000025")
    ))
    (top_provider (
      (context_length 256000)
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
    (default_parameters (
      (temperature 0.3)
    ))
    (supported_voices null)
    (knowledge_cutoff 2023-10-31)
    (expiration_date null)
    (links (
      (details /api/v1/models/mistralai/mistral-small-3.2-24b-instruct-2506/endpoints)
    ))
    (benchmarks (
      (design_arena ([]
        (
          (arena models)
          (category codecategories)
          (elo 935)
          (win_rate 39.8)
          (rank 111)
        )
        (
          (arena models)
          (category dataviz)
          (elo 955)
          (win_rate 43.3)
          (rank 103)
        )
        (
          (arena models)
          (category gamedev)
          (elo 929)
          (win_rate 39.4)
          (rank 112)
        )
        (
          (arena models)
          (category uicomponent)
          (elo 940)
          (win_rate 40.5)
          (rank 104)
        )
        (
          (arena models)
          (category website)
          (elo 918)
          (win_rate 38.3)
          (rank 115)
        )
      ))
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId mistralai/mistral-small-3.2-24b-instruct)
  ))
)
