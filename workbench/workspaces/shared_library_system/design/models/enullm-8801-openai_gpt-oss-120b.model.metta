(
  (kind model)
  (id enullm-8801-openai_gpt-oss-120b)
  (label "openai/gpt-oss-120b · simulated by EMULLM")
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
  (model openai/gpt-oss-120b)
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
    (id openai/gpt-oss-120b)
    (object model)
    (display_name "openai/gpt-oss-120b · simulated by EMULLM")
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
    (id openai/gpt-oss-120b)
    (object model)
    (display_name "openai/gpt-oss-120b · simulated by EMULLM")
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
    (remoteModelId openai/gpt-oss-120b)
  ))
)
