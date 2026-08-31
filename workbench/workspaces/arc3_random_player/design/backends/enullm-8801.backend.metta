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
    (defaultModel yourelf/same)
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
  (dependedOnBy (
    (enullm-8801-copilot-headless-2_percent75 ())
    (enullm-8801-copilot-headless-1_percent100 ())
    (enullm-8801-copilot-headless-1_same ())
    (enullm-8801-copilot-headless-1_percent10 ())
    (enullm-8801-copilot-headless-1_percent125 ())
    (enullm-8801-copilot-headless-1_percent25 ())
    (enullm-8801-copilot-headless-1_percent75 ())
    (enullm-8801-copilot-headless-2_percent100 ())
    (enullm-8801-copilot-headless-2_same ())
    (enullm-8801-copilot-headless-2_percent10 ())
    (enullm-8801-copilot-headless-2_percent125 ())
    (enullm-8801-copilot-headless-2_percent25 ())
    (enullm-8801-copilot-headless-3_percent100 ())
    (enullm-8801-copilot-headless-3_same ())
    (enullm-8801-copilot-headless-3_percent10 ())
    (enullm-8801-copilot-headless-3_percent125 ())
    (enullm-8801-copilot-headless-3_percent25 ())
    (enullm-8801-copilot-headless-3_percent75 ())
    (enullm-8801-copilot-headless-4_percent100 ())
    (enullm-8801-copilot-headless-4_same ())
    (enullm-8801-copilot-headless-4_percent10 ())
    (enullm-8801-copilot-headless-4_percent125 ())
    (enullm-8801-copilot-headless-4_percent25 ())
    (enullm-8801-copilot-headless-4_percent75 ())
    (enullm-8801-yourself_percent100 ())
    (enullm-8801-yourself_same ())
    (enullm-8801-yourself_percent10 ())
    (enullm-8801-yourself_percent125 ())
    (enullm-8801-yourself_percent25 ())
    (enullm-8801-yourself_percent75 ())
  ))
  (implementedBy (
    (enullm-8801-copilot-headless-2_percent75 ())
    (enullm-8801-copilot-headless-1_percent100 ())
    (enullm-8801-copilot-headless-1_same ())
    (enullm-8801-copilot-headless-1_percent10 ())
    (enullm-8801-copilot-headless-1_percent125 ())
    (enullm-8801-copilot-headless-1_percent25 ())
    (enullm-8801-copilot-headless-1_percent75 ())
    (enullm-8801-copilot-headless-2_percent100 ())
    (enullm-8801-copilot-headless-2_same ())
    (enullm-8801-copilot-headless-2_percent10 ())
    (enullm-8801-copilot-headless-2_percent125 ())
    (enullm-8801-copilot-headless-2_percent25 ())
    (enullm-8801-copilot-headless-3_percent100 ())
    (enullm-8801-copilot-headless-3_same ())
    (enullm-8801-copilot-headless-3_percent10 ())
    (enullm-8801-copilot-headless-3_percent125 ())
    (enullm-8801-copilot-headless-3_percent25 ())
    (enullm-8801-copilot-headless-3_percent75 ())
    (enullm-8801-copilot-headless-4_percent100 ())
    (enullm-8801-copilot-headless-4_same ())
    (enullm-8801-copilot-headless-4_percent10 ())
    (enullm-8801-copilot-headless-4_percent125 ())
    (enullm-8801-copilot-headless-4_percent25 ())
    (enullm-8801-copilot-headless-4_percent75 ())
    (enullm-8801-yourself_percent100 ())
    (enullm-8801-yourself_same ())
    (enullm-8801-yourself_percent10 ())
    (enullm-8801-yourself_percent125 ())
    (enullm-8801-yourself_percent25 ())
    (enullm-8801-yourself_percent75 ())
  ))
  (inheritedBy (
    (enullm-8801-copilot-headless-2_percent75 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        implementedBy
        preferredImplementation
      ))
    ))
    (enullm-8801-copilot-headless-1_percent100 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        implementedBy
        preferredImplementation
      ))
    ))
    (enullm-8801-copilot-headless-1_same (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        implementedBy
        preferredImplementation
      ))
    ))
    (enullm-8801-copilot-headless-1_percent10 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        implementedBy
        preferredImplementation
      ))
    ))
    (enullm-8801-copilot-headless-1_percent125 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        implementedBy
        preferredImplementation
      ))
    ))
    (enullm-8801-copilot-headless-1_percent25 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        implementedBy
        preferredImplementation
      ))
    ))
    (enullm-8801-copilot-headless-1_percent75 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        implementedBy
        preferredImplementation
      ))
    ))
    (enullm-8801-copilot-headless-2_percent100 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        implementedBy
        preferredImplementation
      ))
    ))
    (enullm-8801-copilot-headless-2_same (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        implementedBy
        preferredImplementation
      ))
    ))
    (enullm-8801-copilot-headless-2_percent10 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        implementedBy
        preferredImplementation
      ))
    ))
    (enullm-8801-copilot-headless-2_percent125 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        implementedBy
        preferredImplementation
      ))
    ))
    (enullm-8801-copilot-headless-2_percent25 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        implementedBy
        preferredImplementation
      ))
    ))
    (enullm-8801-copilot-headless-3_percent100 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        implementedBy
        preferredImplementation
      ))
    ))
    (enullm-8801-copilot-headless-3_same (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        implementedBy
        preferredImplementation
      ))
    ))
    (enullm-8801-copilot-headless-3_percent10 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        implementedBy
        preferredImplementation
      ))
    ))
    (enullm-8801-copilot-headless-3_percent125 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        implementedBy
        preferredImplementation
      ))
    ))
    (enullm-8801-copilot-headless-3_percent25 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        implementedBy
        preferredImplementation
      ))
    ))
    (enullm-8801-copilot-headless-3_percent75 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        implementedBy
        preferredImplementation
      ))
    ))
    (enullm-8801-copilot-headless-4_percent100 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        implementedBy
        preferredImplementation
      ))
    ))
    (enullm-8801-copilot-headless-4_same (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        implementedBy
        preferredImplementation
      ))
    ))
    (enullm-8801-copilot-headless-4_percent10 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        implementedBy
        preferredImplementation
      ))
    ))
    (enullm-8801-copilot-headless-4_percent125 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        implementedBy
        preferredImplementation
      ))
    ))
    (enullm-8801-copilot-headless-4_percent25 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        implementedBy
        preferredImplementation
      ))
    ))
    (enullm-8801-copilot-headless-4_percent75 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        implementedBy
        preferredImplementation
      ))
    ))
    (enullm-8801-yourself_percent100 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        implementedBy
        preferredImplementation
      ))
    ))
    (enullm-8801-yourself_same (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        implementedBy
        preferredImplementation
      ))
    ))
    (enullm-8801-yourself_percent10 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        implementedBy
        preferredImplementation
      ))
    ))
    (enullm-8801-yourself_percent125 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        implementedBy
        preferredImplementation
      ))
    ))
    (enullm-8801-yourself_percent25 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        implementedBy
        preferredImplementation
      ))
    ))
    (enullm-8801-yourself_percent75 (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        implementedBy
        preferredImplementation
      ))
    ))
  ))
)

(
  (provider openrouter)
  (official true)
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
    (defaultModel yourelf/same)
    (modelEnvironmentVariable null)
    (legacyModelEnvironmentVariable null)
    (defaultAnalysisLevel 4)
    (timeoutSeconds 900)
  ))
  (kind backend)
)
