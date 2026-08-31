(
  (kind model)
  (id enullm-8801-yourself_percent25)
  (label "yourself (~25% capable)")
  (description "Discovered from EMULLM API at http://127.0.0.1:8801/v1.")
  (implements (
    (enullm-8801 ())
  ))
  (model yourself/percent25)
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
    (id yourself/percent25)
    (object model)
    (display_name "yourself (~25% capable)")
    (context_length 200000)
    (supported_parameters ([]))
    (owned_by yourself)
    (connected false)
    (ownedBy yourself)
  ))
  (providerMetadata (
    (id yourself/percent25)
    (object model)
    (display_name "yourself (~25% capable)")
    (context_length 200000)
    (supported_parameters ([]))
    (owned_by yourself)
    (connected false)
  ))
  (discovery (
    (managed true)
    (backendId enullm-8801)
    (remoteModelId yourself/percent25)
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
