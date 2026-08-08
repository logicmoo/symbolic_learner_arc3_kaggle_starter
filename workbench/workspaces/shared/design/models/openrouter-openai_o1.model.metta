({}
  (kind model)
  (id openrouter-openai_o1)
  (label "OpenAI: o1")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model openai/o1)
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
    (contextWindow 200000)
    (maxOutputTokens 100000)
  ))
  (pricing ({}
    (prompt "0.000015")
    (completion "0.00006")
    (web_search "0.01")
    (input_cache_read "0.0000075")
  ))
  (properties ({}
    (id openai/o1)
    (canonical_slug openai/o1-2024-12-17)
    (hugging_face_id "")
    (name "OpenAI: o1")
    (created 1734459999)
    (description "The latest and strongest model family from OpenAI, o1 is designed to spend more time thinking before responding. The o1 model series is trained with large-scale reinforcement learning to reason...")
    (context_length 200000)
    (architecture ({}
      (modality text+image+file->text)
      (input_modalities (
        text
        image
        file
      ))
      (output_modalities (
        text
      ))
      (tokenizer GPT)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.000015")
      (completion "0.00006")
      (web_search "0.01")
      (input_cache_read "0.0000075")
    ))
    (top_provider ({}
      (context_length 200000)
      (max_completion_tokens 100000)
      (is_moderated true)
    ))
    (per_request_limits null)
    (supported_parameters (
      include_reasoning
      max_tokens
      reasoning
      response_format
      seed
      structured_outputs
      tool_choice
      tools
    ))
    (default_parameters ({}
      (temperature null)
      (top_p null)
      (top_k null)
      (frequency_penalty null)
      (presence_penalty null)
      (repetition_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff 2023-10-31)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/openai/o1-2024-12-17/endpoints)
    ))
    (benchmarks ({}
      (design_arena ())
      (artificial_analysis ({}
        (intelligence_index null)
        (coding_index 39.7)
        (agentic_index null)
      ))
    ))
    (reasoning ({}
      (mandatory false)
    ))
    (ownedBy null)
  ))
  (providerMetadata ({}
    (id openai/o1)
    (canonical_slug openai/o1-2024-12-17)
    (hugging_face_id "")
    (name "OpenAI: o1")
    (created 1734459999)
    (description "The latest and strongest model family from OpenAI, o1 is designed to spend more time thinking before responding. The o1 model series is trained with large-scale reinforcement learning to reason...")
    (context_length 200000)
    (architecture ({}
      (modality text+image+file->text)
      (input_modalities (
        text
        image
        file
      ))
      (output_modalities (
        text
      ))
      (tokenizer GPT)
      (instruct_type null)
    ))
    (pricing ({}
      (prompt "0.000015")
      (completion "0.00006")
      (web_search "0.01")
      (input_cache_read "0.0000075")
    ))
    (top_provider ({}
      (context_length 200000)
      (max_completion_tokens 100000)
      (is_moderated true)
    ))
    (per_request_limits null)
    (supported_parameters (
      include_reasoning
      max_tokens
      reasoning
      response_format
      seed
      structured_outputs
      tool_choice
      tools
    ))
    (default_parameters ({}
      (temperature null)
      (top_p null)
      (top_k null)
      (frequency_penalty null)
      (presence_penalty null)
      (repetition_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff 2023-10-31)
    (expiration_date null)
    (links ({}
      (details /api/v1/models/openai/o1-2024-12-17/endpoints)
    ))
    (benchmarks ({}
      (design_arena ())
      (artificial_analysis ({}
        (intelligence_index null)
        (coding_index 39.7)
        (agentic_index null)
      ))
    ))
    (reasoning ({}
      (mandatory false)
    ))
  ))
  (discovery ({}
    (managed true)
    (backendId openrouter)
    (remoteModelId openai/o1)
  ))
)
