({}
  (kind model)
  (id openrouter-arcee-ai_trinity-large-thinking)
  (label "Arcee AI: Trinity Large Thinking")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model arcee-ai/trinity-large-thinking)
  (enabled true)
  (capabilities ({}
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
  (limits ({}
    (contextWindow 262144)
    (maxOutputTokens 262144)
  ))
  (pricing ({}
    (prompt "0.00000022")
    (completion "0.00000085")
    (input_cache_read "0.00000006")
  ))
  (properties ({}
    (id arcee-ai/trinity-large-thinking)
    (canonical_slug arcee-ai/trinity-large-thinking)
    (hugging_face_id arcee-ai/Trinity-Large-Thinking)
    (name "Arcee AI: Trinity Large Thinking")
    (created 1775058318)
    (description "Trinity Large Thinking is a powerful open source reasoning model from the team at Arcee AI. It shows strong performance in PinchBench, agentic workloads, and reasoning tasks. Launch video: https://youtu.be/Gc82AXLa0Rg?si=4RLn6WBz33qT--B7...")
    (context_length 262144)
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
      (prompt "0.00000022")
      (completion "0.00000085")
      (input_cache_read "0.00000006")
    ))
    (top_provider ({}
      (context_length 262144)
      (max_completion_tokens 262144)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      include_reasoning
      logit_bias
      logprobs
      max_tokens
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
      (temperature 0.3)
      (top_p 0.8)
      (top_k null)
      (frequency_penalty null)
      (presence_penalty null)
      (repetition_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/arcee-ai/trinity-large-thinking/endpoints)
    ))
    (benchmarks ({}
      (design_arena (
        ({}
          (arena models)
          (category 3d)
          (elo 1136)
          (win_rate 41.3)
          (rank 72)
        )
        ({}
          (arena models)
          (category asciiart)
          (elo 1079)
          (win_rate 37.1)
          (rank 53)
        )
        ({}
          (arena models)
          (category codecategories)
          (elo 1145)
          (win_rate 40.1)
          (rank 74)
        )
        ({}
          (arena models)
          (category dataviz)
          (elo 1126)
          (win_rate 39.3)
          (rank 79)
        )
        ({}
          (arena models)
          (category gamedev)
          (elo 1119)
          (win_rate 38.4)
          (rank 80)
        )
        ({}
          (arena models)
          (category svg)
          (elo 1063)
          (win_rate 35.2)
          (rank 65)
        )
        ({}
          (arena models)
          (category uicomponent)
          (elo 1078)
          (win_rate 32.6)
          (rank 84)
        )
        ({}
          (arena models)
          (category website)
          (elo 1159)
          (win_rate 41.3)
          (rank 72)
        )
      ))
      (artificial_analysis ({}
        (intelligence_index 18.6)
        (coding_index 25.8)
        (agentic_index 3.7)
      ))
    ))
    (reasoning ({}
      (mandatory true)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id arcee-ai/trinity-large-thinking)
    (canonical_slug arcee-ai/trinity-large-thinking)
    (hugging_face_id arcee-ai/Trinity-Large-Thinking)
    (name "Arcee AI: Trinity Large Thinking")
    (created 1775058318)
    (description "Trinity Large Thinking is a powerful open source reasoning model from the team at Arcee AI. It shows strong performance in PinchBench, agentic workloads, and reasoning tasks. Launch video: https://youtu.be/Gc82AXLa0Rg?si=4RLn6WBz33qT--B7...")
    (context_length 262144)
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
      (prompt "0.00000022")
      (completion "0.00000085")
      (input_cache_read "0.00000006")
    ))
    (top_provider ({}
      (context_length 262144)
      (max_completion_tokens 262144)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters (
      frequency_penalty
      include_reasoning
      logit_bias
      logprobs
      max_tokens
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
      (temperature 0.3)
      (top_p 0.8)
      (top_k null)
      (frequency_penalty null)
      (presence_penalty null)
      (repetition_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/arcee-ai/trinity-large-thinking/endpoints)
    ))
    (benchmarks ({}
      (design_arena (
        ({}
          (arena models)
          (category 3d)
          (elo 1136)
          (win_rate 41.3)
          (rank 72)
        )
        ({}
          (arena models)
          (category asciiart)
          (elo 1079)
          (win_rate 37.1)
          (rank 53)
        )
        ({}
          (arena models)
          (category codecategories)
          (elo 1145)
          (win_rate 40.1)
          (rank 74)
        )
        ({}
          (arena models)
          (category dataviz)
          (elo 1126)
          (win_rate 39.3)
          (rank 79)
        )
        ({}
          (arena models)
          (category gamedev)
          (elo 1119)
          (win_rate 38.4)
          (rank 80)
        )
        ({}
          (arena models)
          (category svg)
          (elo 1063)
          (win_rate 35.2)
          (rank 65)
        )
        ({}
          (arena models)
          (category uicomponent)
          (elo 1078)
          (win_rate 32.6)
          (rank 84)
        )
        ({}
          (arena models)
          (category website)
          (elo 1159)
          (win_rate 41.3)
          (rank 72)
        )
      ))
      (artificial_analysis ({}
        (intelligence_index 18.6)
        (coding_index 25.8)
        (agentic_index 3.7)
      ))
    ))
    (reasoning ({}
      (mandatory true)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId arcee-ai/trinity-large-thinking)
  ))
)
