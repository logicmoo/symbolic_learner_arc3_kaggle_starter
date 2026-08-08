(
  (kind model)
  (id openrouter-openrouter_pareto-code)
  (label "Pareto Code Router")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model openrouter/pareto-code)
  (enabled true)
  (capabilities (
    (audio false)
    (code true)
    (functionCalling false)
    (json false)
    (jsonMode false)
    (local false)
    (multimodal false)
    (reasoning false)
    (text true)
    (tools false)
    (vision false)
  ))
  (limits (
    (contextWindow 2000000)
    (maxOutputTokens null)
  ))
  (pricing (
    (prompt "-1")
    (completion "-1")
  ))
  (properties (
    (id openrouter/pareto-code)
    (canonical_slug openrouter/pareto-code)
    (hugging_face_id "")
    (name "Pareto Code Router")
    (created 1776747900)
    (description "The Pareto Router maintains a tiered shortlist of strong coding models, ranked by [Artificial Analysis](https://artificialanalysis.ai/) coding percentiles. Set min_coding_score between 0 and 1 on the [pareto-router plugin](https://openrouter.ai/docs/guides/routing/routers/pareto-router#the-min_coding_score-parameter) to control how...")
    (context_length 2000000)
    (architecture (
      (modality text->text)
      (input_modalities ([]
        text
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Router)
      (instruct_type null)
    ))
    (pricing (
      (prompt "-1")
      (completion "-1")
    ))
    (top_provider (
      (context_length null)
      (max_completion_tokens null)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]))
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
      (details /api/v1/models/openrouter/pareto-code/endpoints)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id openrouter/pareto-code)
    (canonical_slug openrouter/pareto-code)
    (hugging_face_id "")
    (name "Pareto Code Router")
    (created 1776747900)
    (description "The Pareto Router maintains a tiered shortlist of strong coding models, ranked by [Artificial Analysis](https://artificialanalysis.ai/) coding percentiles. Set min_coding_score between 0 and 1 on the [pareto-router plugin](https://openrouter.ai/docs/guides/routing/routers/pareto-router#the-min_coding_score-parameter) to control how...")
    (context_length 2000000)
    (architecture (
      (modality text->text)
      (input_modalities ([]
        text
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Router)
      (instruct_type null)
    ))
    (pricing (
      (prompt "-1")
      (completion "-1")
    ))
    (top_provider (
      (context_length null)
      (max_completion_tokens null)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]))
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
      (details /api/v1/models/openrouter/pareto-code/endpoints)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId openrouter/pareto-code)
  ))
)
