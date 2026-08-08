(
  (kind model)
  (id openrouter-allenai_olmo-3-32b-think)
  (label "AllenAI: Olmo 3 32B Think")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model allenai/olmo-3-32b-think)
  (enabled true)
  (capabilities (
    (audio false)
    (code false)
    (functionCalling false)
    (json true)
    (jsonMode true)
    (local false)
    (multimodal false)
    (reasoning true)
    (text true)
    (tools false)
    (vision false)
  ))
  (limits (
    (contextWindow 65536)
    (maxOutputTokens 65536)
  ))
  (pricing (
    (prompt "0.00000015")
    (completion "0.0000005")
  ))
  (properties (
    (id allenai/olmo-3-32b-think)
    (canonical_slug allenai/olmo-3-32b-think-20251121)
    (hugging_face_id allenai/Olmo-3-32B-Think)
    (name "AllenAI: Olmo 3 32B Think")
    (created 1763758276)
    (description "Olmo 3 32B Think is a large-scale, 32-billion-parameter model purpose-built for deep reasoning, complex logic chains and advanced instruction-following scenarios. Its capacity enables strong performance on demanding evaluation tasks and...")
    (context_length 65536)
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
      (prompt "0.00000015")
      (completion "0.0000005")
    ))
    (top_provider (
      (context_length 65536)
      (max_completion_tokens 65536)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      frequency_penalty
      include_reasoning
      logit_bias
      max_tokens
      presence_penalty
      reasoning
      repetition_penalty
      response_format
      seed
      stop
      structured_outputs
      temperature
      top_k
      top_p
    ))
    (default_parameters (
      (temperature 0.6)
      (top_p 0.95)
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links (
      (details /api/v1/models/allenai/olmo-3-32b-think-20251121/endpoints)
    ))
    (reasoning (
      (mandatory true)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id allenai/olmo-3-32b-think)
    (canonical_slug allenai/olmo-3-32b-think-20251121)
    (hugging_face_id allenai/Olmo-3-32B-Think)
    (name "AllenAI: Olmo 3 32B Think")
    (created 1763758276)
    (description "Olmo 3 32B Think is a large-scale, 32-billion-parameter model purpose-built for deep reasoning, complex logic chains and advanced instruction-following scenarios. Its capacity enables strong performance on demanding evaluation tasks and...")
    (context_length 65536)
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
      (prompt "0.00000015")
      (completion "0.0000005")
    ))
    (top_provider (
      (context_length 65536)
      (max_completion_tokens 65536)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      frequency_penalty
      include_reasoning
      logit_bias
      max_tokens
      presence_penalty
      reasoning
      repetition_penalty
      response_format
      seed
      stop
      structured_outputs
      temperature
      top_k
      top_p
    ))
    (default_parameters (
      (temperature 0.6)
      (top_p 0.95)
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links (
      (details /api/v1/models/allenai/olmo-3-32b-think-20251121/endpoints)
    ))
    (reasoning (
      (mandatory true)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId allenai/olmo-3-32b-think)
  ))
)
