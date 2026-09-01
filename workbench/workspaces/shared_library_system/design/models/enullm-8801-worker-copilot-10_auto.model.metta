(
  (kind model)
  (id enullm-8801-worker-copilot-10_auto)
  (label "worker-copilot-10 · headless-copilot backed by Auto (auto)")
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
  (model worker-copilot-10/auto)
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
    (id worker-copilot-10/auto)
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
    (display_name "worker-copilot-10 · headless-copilot backed by Auto (auto)")
    (description "Direct alias for stable worker 'worker-copilot-10' using its active backing model 'auto'.")
    (context_length 0)
    (supported_parameters ([]
      messages
      temperature
      stream
    ))
    (owned_by worker-copilot-10)
    (connected true)
    (worker_id worker-copilot-10)
    (worker_kind headless-copilot)
    (backing_model auto)
    (simulated true)
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
    (ownedBy worker-copilot-10)
  ))
  (providerMetadata (
    (id worker-copilot-10/auto)
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
    (display_name "worker-copilot-10 · headless-copilot backed by Auto (auto)")
    (description "Direct alias for stable worker 'worker-copilot-10' using its active backing model 'auto'.")
    (context_length 0)
    (supported_parameters ([]
      messages
      temperature
      stream
    ))
    (owned_by worker-copilot-10)
    (connected true)
    (worker_id worker-copilot-10)
    (worker_kind headless-copilot)
    (backing_model auto)
    (simulated true)
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
    (remoteModelId worker-copilot-10/auto)
  ))
)
