(
  (kind model)
  (id enullm-8801-emullm_default)
  (label "EMULLM · Default")
  (description "Discovered from EMULLM API at http://127.0.0.1:8801/v1.")
  (implements (
    (enullm-8801 ())
  ))
  (inheritsFrom (
    (enullm-8801 (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
  ))
  (dependsOn (
    (enullm-8801 ())
  ))
  (model emullm/default)
  (enabled true)
  (capabilities (
    (audio true)
    (code false)
    (functionCalling false)
    (json false)
    (jsonMode false)
    (imageGeneration false)
    (imageOutput false)
    (local true)
    (multimodal true)
    (reasoning false)
    (text true)
    (tools false)
    (vision true)
  ))
  (limits (
    (contextWindow 200000)
    (maxOutputTokens null)
  ))
  (pricing ())
  (properties (
    (id emullm/default)
    (object model)
    (display_name "EMULLM · Default")
    (description "Stable alias for the configured default model 'google/gemma-4-31b-it'. An explicit route_targets override on emullm/default takes precedence.")
    (context_length 200000)
    (supported_parameters ([]
      messages
      temperature
      stream
    ))
    (owned_by emullm)
    (connected true)
    (default true)
    (resolved_model google/gemma-4-31b-it)
    (route_targets ([]
      worker-in-name
      worker-copilot-*
      worker-codex-*
      worker-unknown-*
      backend-https://llm.a.singularitycompute.com/v1
      backend-*
    ))
    (routing_mode configured)
    (simulated true)
    (input_modalities (
      (attachment_transport (
        (supported true)
        (media_types ([]
          */*
        ))
        (source "resolved model route")
      ))
      (image (
        (enabled true)
        (status resolved_model_dependent)
      ))
      (audio (
        (enabled true)
        (status resolved_model_dependent)
      ))
      (general_file (
        (enabled true)
        (status transport_supported)
        (model_comprehension resolved-model-dependent)
      ))
    ))
    (on_demand false)
    (task_capabilities (
      (code (
        (enabled false)
      ))
      (summarization (
        (enabled false)
      ))
    ))
    (ownedBy emullm)
  ))
  (providerMetadata (
    (id emullm/default)
    (object model)
    (display_name "EMULLM · Default")
    (description "Stable alias for the configured default model 'google/gemma-4-31b-it'. An explicit route_targets override on emullm/default takes precedence.")
    (context_length 200000)
    (supported_parameters ([]
      messages
      temperature
      stream
    ))
    (owned_by emullm)
    (connected true)
    (default true)
    (resolved_model google/gemma-4-31b-it)
    (route_targets ([]
      worker-in-name
      worker-copilot-*
      worker-codex-*
      worker-unknown-*
      backend-https://llm.a.singularitycompute.com/v1
      backend-*
    ))
    (routing_mode configured)
    (simulated true)
    (input_modalities (
      (attachment_transport (
        (supported true)
        (media_types ([]
          */*
        ))
        (source "resolved model route")
      ))
      (image (
        (enabled true)
        (status resolved_model_dependent)
      ))
      (audio (
        (enabled true)
        (status resolved_model_dependent)
      ))
      (general_file (
        (enabled true)
        (status transport_supported)
        (model_comprehension resolved-model-dependent)
      ))
    ))
    (on_demand false)
    (task_capabilities (
      (code (
        (enabled false)
      ))
      (summarization (
        (enabled false)
      ))
    ))
  ))
  (discovery (
    (managed true)
    (backendId enullm-8801)
    (remoteModelId emullm/default)
  ))
)
