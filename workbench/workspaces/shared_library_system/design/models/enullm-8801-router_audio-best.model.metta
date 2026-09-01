(
  (kind model)
  (id enullm-8801-router_audio-best)
  (label "Best · audio")
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
  (model router/audio-best)
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
    (vision false)
  ))
  (limits (
    (contextWindow null)
    (maxOutputTokens null)
  ))
  (pricing ())
  (properties (
    (id router/audio-best)
    (object model)
    (display_name "Best · audio")
    (description "Routes to the best quality-ranked connected worker that explicitly advertises: audio_input.")
    (owned_by emullm-capability-router)
    (connected true)
    (active_workers ([]
      worker-copilot-3
      worker-copilot-5
    ))
    (selection best)
    (capability_alias audio)
    (required_capabilities ([]
      audio_input
    ))
    (assigned_worker_header X-EmuLLM-Worker-ID)
    (simulated false)
    (ownedBy emullm-capability-router)
  ))
  (providerMetadata (
    (id router/audio-best)
    (object model)
    (display_name "Best · audio")
    (description "Routes to the best quality-ranked connected worker that explicitly advertises: audio_input.")
    (owned_by emullm-capability-router)
    (connected true)
    (active_workers ([]
      worker-copilot-3
      worker-copilot-5
    ))
    (selection best)
    (capability_alias audio)
    (required_capabilities ([]
      audio_input
    ))
    (assigned_worker_header X-EmuLLM-Worker-ID)
    (simulated false)
  ))
  (discovery (
    (managed true)
    (backendId enullm-8801)
    (remoteModelId router/audio-best)
  ))
)
