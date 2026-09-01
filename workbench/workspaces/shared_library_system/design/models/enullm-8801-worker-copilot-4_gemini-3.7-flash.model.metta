(
  (kind model)
  (id enullm-8801-worker-copilot-4_gemini-3.7-flash)
  (label "worker-copilot-4/gemini-3.7-flash · simulated by EMULLM")
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
  (model worker-copilot-4/gemini-3.7-flash)
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
    (id worker-copilot-4/gemini-3.7-flash)
    (object model)
    (display_name "worker-copilot-4/gemini-3.7-flash · simulated by EMULLM")
    (description "Configured simulated model. Ordered route: worker-in-name.")
    (context_length 200000)
    (supported_parameters ([]
      messages
      temperature
      stream
    ))
    (owned_by emullm)
    (connected true)
    (simulated true)
    (route_targets ([]
      worker-in-name
    ))
    (active_workers ([]
      worker-copilot-4
    ))
    (backing_models (
      (worker-copilot-4 gpt-5.5)
    ))
    (on_demand false)
    (input_modalities (
      (image (
        (enabled true)
      ))
      (audio (
        (enabled false)
      ))
      (general_file (
        (enabled true)
      ))
    ))
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
    (id worker-copilot-4/gemini-3.7-flash)
    (object model)
    (display_name "worker-copilot-4/gemini-3.7-flash · simulated by EMULLM")
    (description "Configured simulated model. Ordered route: worker-in-name.")
    (context_length 200000)
    (supported_parameters ([]
      messages
      temperature
      stream
    ))
    (owned_by emullm)
    (connected true)
    (simulated true)
    (route_targets ([]
      worker-in-name
    ))
    (active_workers ([]
      worker-copilot-4
    ))
    (backing_models (
      (worker-copilot-4 gpt-5.5)
    ))
    (on_demand false)
    (input_modalities (
      (image (
        (enabled true)
      ))
      (audio (
        (enabled false)
      ))
      (general_file (
        (enabled true)
      ))
    ))
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
    (remoteModelId worker-copilot-4/gemini-3.7-flash)
  ))
)
