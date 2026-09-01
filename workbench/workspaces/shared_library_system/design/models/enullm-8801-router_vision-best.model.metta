(
  (kind model)
  (id enullm-8801-router_vision-best)
  (label "Best · vision")
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
  (model router/vision-best)
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
    (contextWindow null)
    (maxOutputTokens null)
  ))
  (pricing ())
  (properties (
    (id router/vision-best)
    (object model)
    (display_name "Best · vision")
    (description "Routes to the best quality-ranked connected worker that explicitly advertises: vision_input.")
    (owned_by emullm-capability-router)
    (connected true)
    (active_workers ([]
      worker-copilot-1
      worker-copilot-12
      worker-copilot-13
      worker-copilot-14
      worker-copilot-15
      worker-copilot-16
      worker-copilot-17
      worker-copilot-18
      worker-copilot-2
      worker-copilot-3
      worker-copilot-4
      worker-copilot-5
      worker-copilot-6
      worker-copilot-7
      worker-copilot-8
      worker-copilot-9
    ))
    (selection best)
    (capability_alias vision)
    (required_capabilities ([]
      vision_input
    ))
    (assigned_worker_header X-EmuLLM-Worker-ID)
    (simulated false)
    (ownedBy emullm-capability-router)
  ))
  (providerMetadata (
    (id router/vision-best)
    (object model)
    (display_name "Best · vision")
    (description "Routes to the best quality-ranked connected worker that explicitly advertises: vision_input.")
    (owned_by emullm-capability-router)
    (connected true)
    (active_workers ([]
      worker-copilot-1
      worker-copilot-12
      worker-copilot-13
      worker-copilot-14
      worker-copilot-15
      worker-copilot-16
      worker-copilot-17
      worker-copilot-18
      worker-copilot-2
      worker-copilot-3
      worker-copilot-4
      worker-copilot-5
      worker-copilot-6
      worker-copilot-7
      worker-copilot-8
      worker-copilot-9
    ))
    (selection best)
    (capability_alias vision)
    (required_capabilities ([]
      vision_input
    ))
    (assigned_worker_header X-EmuLLM-Worker-ID)
    (simulated false)
  ))
  (discovery (
    (managed true)
    (backendId enullm-8801)
    (remoteModelId router/vision-best)
  ))
)
