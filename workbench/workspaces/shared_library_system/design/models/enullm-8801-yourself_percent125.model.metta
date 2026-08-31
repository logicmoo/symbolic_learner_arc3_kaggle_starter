(
  (kind model)
  (id enullm-8801-yourself_percent125)
  (label "yourself (~125% -- extra thorough)")
  (description "Discovered from EMULLM API at http://127.0.0.1:8801/v1.")
  (implements (
    (enullm-8801 ())
  ))
  (model yourself/percent125)
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
    (id yourself/percent125)
    (object model)
    (display_name "yourself (~125% -- extra thorough)")
    (context_length 200000)
    (supported_parameters ([]))
    (owned_by yourself)
    (connected false)
    (ownedBy yourself)
  ))
  (providerMetadata (
    (id yourself/percent125)
    (object model)
    (display_name "yourself (~125% -- extra thorough)")
    (context_length 200000)
    (supported_parameters ([]))
    (owned_by yourself)
    (connected false)
  ))
  (discovery (
    (managed true)
    (backendId enullm-8801)
    (remoteModelId yourself/percent125)
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
