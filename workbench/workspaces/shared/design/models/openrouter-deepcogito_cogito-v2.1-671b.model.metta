(
  (kind model)
  (id openrouter-deepcogito_cogito-v2.1-671b)
  (label "Deep Cogito: Cogito v2.1 671B")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model deepcogito/cogito-v2.1-671b)
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
    (contextWindow 128000)
    (maxOutputTokens null)
  ))
  (pricing (
    (prompt "0.00000125")
    (completion "0.00000125")
  ))
  (properties (
    (id deepcogito/cogito-v2.1-671b)
    (canonical_slug deepcogito/cogito-v2.1-671b-20251118)
    (hugging_face_id "")
    (name "Deep Cogito: Cogito v2.1 671B")
    (created 1763071233)
    (description "Cogito v2.1 671B MoE represents one of the strongest open models globally, matching performance of frontier closed and open models. This model is trained using self play with reinforcement learning...")
    (context_length 128000)
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
      (prompt "0.00000125")
      (completion "0.00000125")
    ))
    (top_provider (
      (context_length 128000)
      (max_completion_tokens null)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      frequency_penalty
      include_reasoning
      logit_bias
      max_tokens
      min_p
      presence_penalty
      reasoning
      repetition_penalty
      response_format
      stop
      structured_outputs
      temperature
      top_k
      top_p
    ))
    (default_parameters (
      (temperature null)
      (top_p null)
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links (
      (details /api/v1/models/deepcogito/cogito-v2.1-671b-20251118/endpoints)
    ))
    (reasoning (
      (mandatory false)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id deepcogito/cogito-v2.1-671b)
    (canonical_slug deepcogito/cogito-v2.1-671b-20251118)
    (hugging_face_id "")
    (name "Deep Cogito: Cogito v2.1 671B")
    (created 1763071233)
    (description "Cogito v2.1 671B MoE represents one of the strongest open models globally, matching performance of frontier closed and open models. This model is trained using self play with reinforcement learning...")
    (context_length 128000)
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
      (prompt "0.00000125")
      (completion "0.00000125")
    ))
    (top_provider (
      (context_length 128000)
      (max_completion_tokens null)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      frequency_penalty
      include_reasoning
      logit_bias
      max_tokens
      min_p
      presence_penalty
      reasoning
      repetition_penalty
      response_format
      stop
      structured_outputs
      temperature
      top_k
      top_p
    ))
    (default_parameters (
      (temperature null)
      (top_p null)
      (frequency_penalty null)
    ))
    (supported_voices null)
    (knowledge_cutoff null)
    (expiration_date null)
    (links (
      (details /api/v1/models/deepcogito/cogito-v2.1-671b-20251118/endpoints)
    ))
    (reasoning (
      (mandatory false)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId deepcogito/cogito-v2.1-671b)
  ))
)
