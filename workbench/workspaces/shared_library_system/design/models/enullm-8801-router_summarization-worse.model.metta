(
  (kind model)
  (id enullm-8801-router_summarization-worse)
  (label "Worse · summarization")
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
  (model router/summarization-worse)
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
    (contextWindow null)
    (maxOutputTokens null)
  ))
  (pricing ())
  (properties (
    (id router/summarization-worse)
    (object model)
    (display_name "Worse · summarization")
    (description "Routes to the worse quality-ranked connected worker that explicitly advertises: summarization.")
    (owned_by emullm-capability-router)
    (connected true)
    (active_workers ([]
      worker-copilot-10
      worker-copilot-11
      worker-copilot-12
      worker-copilot-13
      worker-copilot-14
      worker-copilot-15
      worker-copilot-16
      worker-copilot-17
      worker-copilot-18
      worker-copilot-19
      worker-copilot-20
      worker-copilot-21
      worker-copilot-5
      worker-copilot-6
      worker-copilot-7
      worker-copilot-8
      worker-copilot-9
    ))
    (selection worse)
    (capability_alias summarization)
    (required_capabilities ([]
      summarization
    ))
    (assigned_worker_header X-EmuLLM-Worker-ID)
    (simulated false)
    (ownedBy emullm-capability-router)
  ))
  (providerMetadata (
    (id router/summarization-worse)
    (object model)
    (display_name "Worse · summarization")
    (description "Routes to the worse quality-ranked connected worker that explicitly advertises: summarization.")
    (owned_by emullm-capability-router)
    (connected true)
    (active_workers ([]
      worker-copilot-10
      worker-copilot-11
      worker-copilot-12
      worker-copilot-13
      worker-copilot-14
      worker-copilot-15
      worker-copilot-16
      worker-copilot-17
      worker-copilot-18
      worker-copilot-19
      worker-copilot-20
      worker-copilot-21
      worker-copilot-5
      worker-copilot-6
      worker-copilot-7
      worker-copilot-8
      worker-copilot-9
    ))
    (selection worse)
    (capability_alias summarization)
    (required_capabilities ([]
      summarization
    ))
    (assigned_worker_header X-EmuLLM-Worker-ID)
    (simulated false)
  ))
  (discovery (
    (managed true)
    (backendId enullm-8801)
    (remoteModelId router/summarization-worse)
  ))
)
