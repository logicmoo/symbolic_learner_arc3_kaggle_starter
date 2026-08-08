(
  (kind model)
  (id openrouter-perceptron_perceptron-mk1)
  (label "Perceptron: Perceptron Mk1")
  (description "Discovered from OpenRouter.")
  (inherits openrouter)
  (model perceptron/perceptron-mk1)
  (enabled true)
  (capabilities (
    (audio false)
    (code false)
    (functionCalling false)
    (json true)
    (jsonMode true)
    (local false)
    (multimodal true)
    (reasoning true)
    (text true)
    (tools false)
    (vision true)
  ))
  (limits (
    (contextWindow 32768)
    (maxOutputTokens 8192)
  ))
  (pricing (
    (prompt "0.00000015")
    (completion "0.0000015")
  ))
  (properties (
    (id perceptron/perceptron-mk1)
    (canonical_slug perceptron/perceptron-mk1-20260512)
    (hugging_face_id null)
    (name "Perceptron: Perceptron Mk1")
    (created 1778597029)
    (description "Perceptron Mk1 (Mark One) is Perceptron's highest-quality vision-language model for video and embodied reasoning.** It accepts image and video inputs paired with natural language queries, and produces detailed visual understanding...")
    (context_length 32768)
    (architecture (
      (modality text+image+video->text)
      (input_modalities ([]
        text
        image
        video
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Other)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.00000015")
      (completion "0.0000015")
    ))
    (top_provider (
      (context_length 32768)
      (max_completion_tokens 8192)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      frequency_penalty
      include_reasoning
      max_tokens
      presence_penalty
      reasoning
      structured_outputs
      temperature
      top_k
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
      (details /api/v1/models/perceptron/perceptron-mk1-20260512/endpoints)
    ))
    (reasoning (
      (mandatory false)
    ))
    (ownedBy null)
  ))
  (providerMetadata (
    (id perceptron/perceptron-mk1)
    (canonical_slug perceptron/perceptron-mk1-20260512)
    (hugging_face_id null)
    (name "Perceptron: Perceptron Mk1")
    (created 1778597029)
    (description "Perceptron Mk1 (Mark One) is Perceptron's highest-quality vision-language model for video and embodied reasoning.** It accepts image and video inputs paired with natural language queries, and produces detailed visual understanding...")
    (context_length 32768)
    (architecture (
      (modality text+image+video->text)
      (input_modalities ([]
        text
        image
        video
      ))
      (output_modalities ([]
        text
      ))
      (tokenizer Other)
      (instruct_type null)
    ))
    (pricing (
      (prompt "0.00000015")
      (completion "0.0000015")
    ))
    (top_provider (
      (context_length 32768)
      (max_completion_tokens 8192)
      (is_moderated false)
    ))
    (per_request_limits null)
    (supported_parameters ([]
      frequency_penalty
      include_reasoning
      max_tokens
      presence_penalty
      reasoning
      structured_outputs
      temperature
      top_k
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
      (details /api/v1/models/perceptron/perceptron-mk1-20260512/endpoints)
    ))
    (reasoning (
      (mandatory false)
    ))
  ))
  (discovery (
    (managed true)
    (backendId openrouter)
    (remoteModelId perceptron/perceptron-mk1)
  ))
)
