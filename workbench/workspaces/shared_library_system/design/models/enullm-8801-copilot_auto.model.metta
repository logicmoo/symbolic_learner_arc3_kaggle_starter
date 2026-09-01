(
  (kind model)
  (id enullm-8801-copilot_auto)
  (label "GitHub Copilot · Auto")
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
  (model copilot/auto)
  (enabled true)
  (capabilities (
    (audio false)
    (code false)
    (functionCalling false)
    (json false)
    (jsonMode false)
    (imageGeneration false)
    (imageOutput false)
    (local true)
    (multimodal false)
    (reasoning false)
    (text true)
    (tools false)
    (vision false)
  ))
  (limits (
    (contextWindow 0)
    (maxOutputTokens null)
  ))
  (pricing ())
  (properties (
    (id copilot/auto)
    (name Auto)
    (capabilities (
      (supports ())
      (limits (
        (max_context_window_tokens 0)
      ))
    ))
    (billing (
      (discountPercent 10)
    ))
    (quality_rank null)
    (quality_tier unranked)
    (object model)
    (display_name "GitHub Copilot · Auto")
    (description "Authenticated GitHub Copilot backing model 'auto'. Requesting this ID lazily starts or reuses one of 46 elastic workers (worker-copilot-5..50).")
    (context_length 0)
    (supported_parameters ([]
      messages
      temperature
      stream
    ))
    (owned_by github-copilot)
    (provider github-copilot)
    (backing_model auto)
    (connected true)
    (active_workers ([]
      worker-copilot-10
    ))
    (route_targets ([]))
    (routing_mode on_demand)
    (on_demand true)
    (on_demand_worker_prefix worker-copilot-)
    (on_demand_worker_start 5)
    (on_demand_worker_limit 46)
    (max_concurrent_calls 50)
    (simulated false)
    (policy ())
    (input_modalities (
      (attachment_transport (
        (supported true)
        (source "Copilot SDK blob attachments via EMULLM cloud-file transport")
        (media_types ([]
          */*
        ))
      ))
      (image (
        (status not_advertised)
        (media_types ([]))
        (enabled false)
      ))
      (audio (
        (status not_advertised)
        (source "Copilot SDK schema has no audio capability field")
        (media_types ([]))
        (transport_supported true)
        (enabled false)
      ))
      (general_file (
        (status transport_supported)
        (model_comprehension model-dependent)
        (enabled true)
      ))
    ))
    (task_capabilities (
      (code (
        (enabled false)
        (status not_advertised)
      ))
      (image_generation (
        (enabled false)
        (status not_advertised)
      ))
      (image_output (
        (enabled false)
        (status not_advertised)
      ))
      (summarization (
        (enabled true)
        (status general_chat_capability)
      ))
    ))
    (output_modalities (
      (image (
        (enabled false)
        (capability image_output)
        (status not_advertised)
        (media_types ([]))
      ))
    ))
    (backingModelMetadata (
      (id auto)
      (name Auto)
      (capabilities (
        (supports ())
        (limits (
          (max_context_window_tokens 0)
        ))
      ))
      (billing (
        (discountPercent 10)
      ))
      (quality_rank null)
      (quality_tier unranked)
    ))
    (ownedBy github-copilot)
  ))
  (providerMetadata (
    (id copilot/auto)
    (name Auto)
    (capabilities (
      (supports ())
      (limits (
        (max_context_window_tokens 0)
      ))
    ))
    (billing (
      (discountPercent 10)
    ))
    (quality_rank null)
    (quality_tier unranked)
    (object model)
    (display_name "GitHub Copilot · Auto")
    (description "Authenticated GitHub Copilot backing model 'auto'. Requesting this ID lazily starts or reuses one of 46 elastic workers (worker-copilot-5..50).")
    (context_length 0)
    (supported_parameters ([]
      messages
      temperature
      stream
    ))
    (owned_by github-copilot)
    (provider github-copilot)
    (backing_model auto)
    (connected true)
    (active_workers ([]
      worker-copilot-10
    ))
    (route_targets ([]))
    (routing_mode on_demand)
    (on_demand true)
    (on_demand_worker_prefix worker-copilot-)
    (on_demand_worker_start 5)
    (on_demand_worker_limit 46)
    (max_concurrent_calls 50)
    (simulated false)
    (policy ())
    (input_modalities (
      (attachment_transport (
        (supported true)
        (source "Copilot SDK blob attachments via EMULLM cloud-file transport")
        (media_types ([]
          */*
        ))
      ))
      (image (
        (status not_advertised)
        (media_types ([]))
        (enabled false)
      ))
      (audio (
        (status not_advertised)
        (source "Copilot SDK schema has no audio capability field")
        (media_types ([]))
        (transport_supported true)
        (enabled false)
      ))
      (general_file (
        (status transport_supported)
        (model_comprehension model-dependent)
        (enabled true)
      ))
    ))
    (task_capabilities (
      (code (
        (enabled false)
        (status not_advertised)
      ))
      (image_generation (
        (enabled false)
        (status not_advertised)
      ))
      (image_output (
        (enabled false)
        (status not_advertised)
      ))
      (summarization (
        (enabled true)
        (status general_chat_capability)
      ))
    ))
    (output_modalities (
      (image (
        (enabled false)
        (capability image_output)
        (status not_advertised)
        (media_types ([]))
      ))
    ))
    (backingModelMetadata (
      (id auto)
      (name Auto)
      (capabilities (
        (supports ())
        (limits (
          (max_context_window_tokens 0)
        ))
      ))
      (billing (
        (discountPercent 10)
      ))
      (quality_rank null)
      (quality_tier unranked)
    ))
  ))
  (discovery (
    (managed true)
    (backendId enullm-8801)
    (remoteModelId copilot/auto)
  ))
)
