(
  (kind backend)
  (id enullm-8801)
  (label "EMULLM API at http://127.0.0.1:8801/v1")
  (provider openrouter)
  (official true)
  (description "AIs on WebSockets pretending to be Backend LLM Servers")
  (enabled true)
  (capabilities ([]
    llm.complete
    llm.vision
  ))
  (configuration (
    (adapter openai)
    (baseUrl http://127.0.0.1:8801/v1)
    (apiKeyEnvironmentVariable null)
    (baseUrlEnvironmentVariable null)
    (legacyBaseUrlEnvironmentVariable null)
    (defaultModel yourelf.same)
    (modelEnvironmentVariable null)
    (legacyModelEnvironmentVariable null)
    (defaultAnalysisLevel 4)
    (timeoutSeconds 900)
  ))
  (aliases ([]))
  (categories ([]
    backends
    models
    systems/systems-llm
    todo-needs-categorization
    vision
  ))
)
