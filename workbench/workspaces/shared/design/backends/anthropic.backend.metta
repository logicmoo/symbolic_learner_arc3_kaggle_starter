({}
  (kind backend)
  (id anthropic)
  (label "Anthropic API")
  (provider anthropic)
  (official true)
  (description "Shared Anthropic Messages API transport inherited by every workspace. Model files inherit this connection and add model-specific generation settings.")
  (enabled true)
  (capabilities (
    llm.complete
    llm.vision
  ))
  (configuration ({}
    (adapter anthropic_messages)
    (baseUrl https://api.anthropic.com/v1)
    (apiKeyEnvironmentVariable ANTHROPIC_API_KEY)
    (baseUrlEnvironmentVariable WORKBENCH_ANTHROPIC_BASE_URL)
    (legacyBaseUrlEnvironmentVariable ARC3_CLAUDE_BASE_URL)
    (defaultModel claude-sonnet-4-20250514)
    (modelEnvironmentVariable WORKBENCH_ANTHROPIC_MODEL)
    (legacyModelEnvironmentVariable ARC3_CLAUDE_MODEL)
    (defaultAnalysisLevel 4)
    (timeoutSeconds 900)
  ))
)
