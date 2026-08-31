(
  (kind model)
  (id enullm-8801-yourself_same)
  (label "yourself (unmodified)")
  (description "Discovered from EMULLM API at http://127.0.0.1:8801/v1.")
  (implements (
    (enullm-8801 ())
  ))
  (model yourself/same)
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
    (id yourself/same)
    (object model)
    (display_name "yourself (unmodified)")
    (context_length 200000)
    (supported_parameters ([]))
    (owned_by yourself)
    (connected false)
    (ownedBy yourself)
  ))
  (providerMetadata (
    (id yourself/same)
    (object model)
    (display_name "yourself (unmodified)")
    (context_length 200000)
    (supported_parameters ([]))
    (owned_by yourself)
    (connected false)
  ))
  (discovery (
    (managed true)
    (backendId enullm-8801)
    (remoteModelId yourself/same)
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
