(
  (kind model)
  (id enullm-8801-openai_gpt-oss-20b)
  (label "openai/gpt-oss-20b · simulated by EMULLM")
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
  (model openai/gpt-oss-20b)
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
    (id openai/gpt-oss-20b)
    (object model)
    (display_name "openai/gpt-oss-20b · simulated by EMULLM")
    (description "Configured simulated model. Ordered route: worker-copilot-* -> worker-codex-* -> https://llm.a.singularitycompute.com/v1.")
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
      worker-copilot-*
      worker-codex-*
      https://llm.a.singularitycompute.com/v1
    ))
    (active_workers ([]
      worker-copilot-1
      worker-copilot-10
      worker-copilot-2
      worker-copilot-3
      worker-copilot-4
      worker-copilot-5
    ))
    (backing_models (
      (worker-copilot-1 gpt-5.4-mini)
      (worker-copilot-10 auto)
      (worker-copilot-2 grok-4.5)
      (worker-copilot-3 claude-opus-4.8-fast)
      (worker-copilot-4 gpt-5.5)
      (worker-copilot-5 gemini-3.7-flash)
    ))
    (ownedBy emullm)
  ))
  (providerMetadata (
    (id openai/gpt-oss-20b)
    (object model)
    (display_name "openai/gpt-oss-20b · simulated by EMULLM")
    (description "Configured simulated model. Ordered route: worker-copilot-* -> worker-codex-* -> https://llm.a.singularitycompute.com/v1.")
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
      worker-copilot-*
      worker-codex-*
      https://llm.a.singularitycompute.com/v1
    ))
    (active_workers ([]
      worker-copilot-1
      worker-copilot-10
      worker-copilot-2
      worker-copilot-3
      worker-copilot-4
      worker-copilot-5
    ))
    (backing_models (
      (worker-copilot-1 gpt-5.4-mini)
      (worker-copilot-10 auto)
      (worker-copilot-2 grok-4.5)
      (worker-copilot-3 claude-opus-4.8-fast)
      (worker-copilot-4 gpt-5.5)
      (worker-copilot-5 gemini-3.7-flash)
    ))
  ))
  (discovery (
    (managed true)
    (backendId enullm-8801)
    (remoteModelId openai/gpt-oss-20b)
  ))
)
