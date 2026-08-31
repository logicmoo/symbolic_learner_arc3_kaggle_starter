(
  (kind model)
  (id enullm-8801-copilot-headless-3_percent25)
  (label "copilot-headless-3 (~25% capable)")
  (description "Discovered from EMULLM API at http://127.0.0.1:8801/v1.")
  (implements (
    (enullm-8801 ())
  ))
  (model copilot-headless-3/percent25)
  (enabled true)
  (capabilities (
    (audio false)
    (code false)
    (functionCalling false)
    (json false)
    (jsonMode false)
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
    (id copilot-headless-3/percent25)
    (object model)
    (display_name "copilot-headless-3 (~25% capable)")
    (context_length 200000)
    (supported_parameters ([]))
    (owned_by copilot-headless-3)
    (connected true)
    (ownedBy copilot-headless-3)
  ))
  (providerMetadata (
    (id copilot-headless-3/percent25)
    (object model)
    (display_name "copilot-headless-3 (~25% capable)")
    (context_length 200000)
    (supported_parameters ([]))
    (owned_by copilot-headless-3)
    (connected true)
  ))
  (discovery (
    (managed true)
    (backendId enullm-8801)
    (remoteModelId copilot-headless-3/percent25)
  ))
  (dependsOn (
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
)
