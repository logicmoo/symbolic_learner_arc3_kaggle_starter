(
  (kind model)
  (id enullm-8801-worker-copilot-10_same)
  (label "worker-copilot-10 · headless-copilot (auto) · (unmodified)")
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
  (model worker-copilot-10/same)
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
    (contextWindow 200000)
    (maxOutputTokens null)
  ))
  (pricing ())
  (properties (
    (id worker-copilot-10/same)
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
    (display_name "worker-copilot-10 · headless-copilot (auto) · (unmodified)")
    (description "Resident GitHub Copilot servant backed by auto; session 4eacdbcf-e732-4088-84e0-fa872317fc8c. Stable worker ID: worker-copilot-10. Backing model: auto. Answer normally, at your full/actual capability.")
    (context_length 200000)
    (supported_parameters ([]))
    (owned_by worker-copilot-10)
    (connected true)
    (worker_id worker-copilot-10)
    (worker_kind headless-copilot)
    (backing_model auto)
    (simulated true)
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
    (id worker-copilot-10/same)
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
    (display_name "worker-copilot-10 · headless-copilot (auto) · (unmodified)")
    (description "Resident GitHub Copilot servant backed by auto; session 4eacdbcf-e732-4088-84e0-fa872317fc8c. Stable worker ID: worker-copilot-10. Backing model: auto. Answer normally, at your full/actual capability.")
    (context_length 200000)
    (supported_parameters ([]))
    (owned_by worker-copilot-10)
    (connected true)
    (worker_id worker-copilot-10)
    (worker_kind headless-copilot)
    (backing_model auto)
    (simulated true)
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
    (remoteModelId worker-copilot-10/same)
  ))
)
