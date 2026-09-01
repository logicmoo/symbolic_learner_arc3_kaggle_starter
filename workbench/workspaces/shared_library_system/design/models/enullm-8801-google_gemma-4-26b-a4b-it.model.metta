(
  (kind model)
  (id enullm-8801-google_gemma-4-26b-a4b-it)
  (label "google/gemma-4-26b-a4b-it · simulated by EMULLM")
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
  (model google/gemma-4-26b-a4b-it)
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
    (id google/gemma-4-26b-a4b-it)
    (object model)
    (display_name "google/gemma-4-26b-a4b-it · simulated by EMULLM")
    (description "Configured simulated model. Uses the default EMULLM worker-selection policy.")
    (context_length 200000)
    (supported_parameters ([]
      messages
      temperature
      stream
    ))
    (owned_by emullm)
    (connected false)
    (simulated true)
    (route_targets ([]))
    (active_workers ([]))
    (backing_models ())
    (ownedBy emullm)
  ))
  (providerMetadata (
    (id google/gemma-4-26b-a4b-it)
    (object model)
    (display_name "google/gemma-4-26b-a4b-it · simulated by EMULLM")
    (description "Configured simulated model. Uses the default EMULLM worker-selection policy.")
    (context_length 200000)
    (supported_parameters ([]
      messages
      temperature
      stream
    ))
    (owned_by emullm)
    (connected false)
    (simulated true)
    (route_targets ([]))
    (active_workers ([]))
    (backing_models ())
  ))
  (discovery (
    (managed true)
    (backendId enullm-8801)
    (remoteModelId google/gemma-4-26b-a4b-it)
  ))
)
