(
  (kind model)
  (id enullm-8801-zira_for_sol)
  (label "zira/for_sol · simulated by EMULLM")
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
  (model zira/for_sol)
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
    (id zira/for_sol)
    (object model)
    (display_name "zira/for_sol · simulated by EMULLM")
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
      worker-copilot-11
      worker-copilot-12
      worker-copilot-13
      worker-copilot-14
      worker-copilot-15
      worker-copilot-16
      worker-copilot-17
      worker-copilot-18
      worker-copilot-19
      worker-copilot-2
      worker-copilot-20
      worker-copilot-21
      worker-copilot-3
      worker-copilot-4
      worker-copilot-5
      worker-copilot-6
      worker-copilot-7
      worker-copilot-8
      worker-copilot-9
    ))
    (backing_models (
      (worker-copilot-1 claude-sonnet-4.6)
      (worker-copilot-10 auto)
      (worker-copilot-11 auto)
      (worker-copilot-12 gpt-5.3-codex)
      (worker-copilot-13 gpt-5.3-codex)
      (worker-copilot-14 gpt-5.3-codex)
      (worker-copilot-15 gpt-5.3-codex)
      (worker-copilot-16 gpt-5.3-codex)
      (worker-copilot-17 gpt-5.3-codex)
      (worker-copilot-18 gpt-5.3-codex)
      (worker-copilot-19 auto)
      (worker-copilot-2 claude-sonnet-4.5)
      (worker-copilot-20 auto)
      (worker-copilot-21 auto)
      (worker-copilot-3 claude-opus-4.8-fast)
      (worker-copilot-4 gpt-5.6-sol)
      (worker-copilot-5 gemini-3.7-flash)
      (worker-copilot-6 gpt-5.3-codex)
      (worker-copilot-7 gpt-5.3-codex)
      (worker-copilot-8 gpt-5.3-codex)
      (worker-copilot-9 gpt-5.3-codex)
    ))
    (ownedBy emullm)
  ))
  (providerMetadata (
    (id zira/for_sol)
    (object model)
    (display_name "zira/for_sol · simulated by EMULLM")
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
      worker-copilot-11
      worker-copilot-12
      worker-copilot-13
      worker-copilot-14
      worker-copilot-15
      worker-copilot-16
      worker-copilot-17
      worker-copilot-18
      worker-copilot-19
      worker-copilot-2
      worker-copilot-20
      worker-copilot-21
      worker-copilot-3
      worker-copilot-4
      worker-copilot-5
      worker-copilot-6
      worker-copilot-7
      worker-copilot-8
      worker-copilot-9
    ))
    (backing_models (
      (worker-copilot-1 claude-sonnet-4.6)
      (worker-copilot-10 auto)
      (worker-copilot-11 auto)
      (worker-copilot-12 gpt-5.3-codex)
      (worker-copilot-13 gpt-5.3-codex)
      (worker-copilot-14 gpt-5.3-codex)
      (worker-copilot-15 gpt-5.3-codex)
      (worker-copilot-16 gpt-5.3-codex)
      (worker-copilot-17 gpt-5.3-codex)
      (worker-copilot-18 gpt-5.3-codex)
      (worker-copilot-19 auto)
      (worker-copilot-2 claude-sonnet-4.5)
      (worker-copilot-20 auto)
      (worker-copilot-21 auto)
      (worker-copilot-3 claude-opus-4.8-fast)
      (worker-copilot-4 gpt-5.6-sol)
      (worker-copilot-5 gemini-3.7-flash)
      (worker-copilot-6 gpt-5.3-codex)
      (worker-copilot-7 gpt-5.3-codex)
      (worker-copilot-8 gpt-5.3-codex)
      (worker-copilot-9 gpt-5.3-codex)
    ))
  ))
  (discovery (
    (managed true)
    (backendId enullm-8801)
    (remoteModelId zira/for_sol)
  ))
)
